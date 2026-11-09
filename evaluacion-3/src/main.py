from contextlib import asynccontextmanager
from datetime import date
import os
from pathlib import Path

from fastapi import Depends, FastAPI, File, Query, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .database import Database
from .document_store import LocalDocumentStore, MAX_DOCUMENT_BYTES
from .domain import DomainError
from .identity import Principal, authenticate
from .service import ProposalService


DEMO_TOKEN_SUBJECTS = {
    "demo-pi-alice": "hu-demo-alice",
    "demo-pi-bob": "hu-demo-bob",
    "demo-coordinator": "hu-demo-coordinator",
    "demo-coordinator-mateo": "hu-demo-coordinator-2",
}
bearer_scheme = HTTPBearer(auto_error=False)

MAX_UPLOAD_REQUEST_BYTES = MAX_DOCUMENT_BYTES + 256 * 1024


class _RequestBodyTooLarge(Exception):
    pass


class UploadSizeLimitMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        is_document_upload = (
            scope["type"] == "http"
            and scope.get("method") == "POST"
            and "/documents/" in scope.get("path", "")
        )
        if not is_document_upload:
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        content_length = headers.get(b"content-length")
        if content_length is not None:
            try:
                declared_length = int(content_length)
            except ValueError:
                await self._reject(send, 400, "invalid_content_length")
                return
            if declared_length > MAX_UPLOAD_REQUEST_BYTES:
                await self._reject(send, 413, "upload_request_too_large")
                return

        received = 0

        async def limited_receive():
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > MAX_UPLOAD_REQUEST_BYTES:
                    raise _RequestBodyTooLarge
            return message

        try:
            await self.app(scope, limited_receive, send)
        except _RequestBodyTooLarge:
            await self._reject(send, 413, "upload_request_too_large")

    @staticmethod
    async def _reject(send, status_code: int, code: str):
        body = (f'{{"error":{{"code":"{code}","message":"Upload request is too large"}}}}').encode()
        await send({
            "type": "http.response.start", "status": status_code,
            "headers": [(b"content-type", b"application/json"),
                        (b"content-length", str(len(body)).encode())],
        })
        await send({"type": "http.response.body", "body": body})


class ProposalInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    opportunity_id: str = Field(min_length=1)
    title: str | None = None
    abstract: str | None = None
    requested_amount: float | None = None


class SubmitProposalInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_version: int = Field(ge=0)


class ProposalUpdateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_version: int = Field(ge=0)
    title: str | None = None
    sponsor: str | None = None
    abstract: str | None = None
    requested_amount: float | None = None


class VerificationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str
    notes: str = Field(default="", max_length=2000)
    due_date: date | None = None


def create_app(
    database_path: str | Path | None = None,
    token_subjects: dict[str, str] | None = None,
) -> FastAPI:
    resolved_path = database_path or os.environ.get(
        "DH03_DB_PATH",
        str(Path(__file__).resolve().parents[1] / "data" / "dh03.sqlite3"),
    )
    database = Database(resolved_path)
    upload_root = os.environ.get(
        "DH03_UPLOAD_DIR",
        str(Path(resolved_path).resolve().parent / "private-documents"),
    )
    document_store = LocalDocumentStore(upload_root)
    service = ProposalService(database, document_store)
    identity_tokens = token_subjects if token_subjects is not None else DEMO_TOKEN_SUBJECTS

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        database.initialize()
        yield

    app = FastAPI(
        title="DH-03 Research Grant Tracking — Evaluation 3",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.state.database = database
    app.add_middleware(UploadSizeLimitMiddleware)

    @app.get("/", include_in_schema=False)
    def home() -> FileResponse:
        return FileResponse(Path(__file__).with_name("static") / "index.html")

    @app.exception_handler(DomainError)
    async def domain_error_handler(_, error: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=error.status_code,
            content={"error": {"code": error.code, "message": error.message}},
        )

    def current_principal(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    ) -> Principal:
        token = credentials.credentials if credentials is not None else ""
        with database.read() as connection:
            return authenticate(connection, token, identity_tokens)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "submission_contract": "requested_amount_optional-v2",
        }

    @app.get("/opportunities")
    def list_opportunities(
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=6, ge=1, le=50),
    ) -> dict:
        with database.read() as connection:
            total = connection.execute(
                "SELECT COUNT(*) FROM opportunities WHERE status = 'OPEN' AND deadline >= ?",
                (date.today().isoformat(),),
            ).fetchone()[0]
            rows = connection.execute(
                """
                SELECT id, title, description, sponsor, deadline, status FROM opportunities
                WHERE status = 'OPEN' AND deadline >= ? ORDER BY deadline, id
                LIMIT ? OFFSET ?
                """,
                (date.today().isoformat(), page_size, (page - 1) * page_size),
            ).fetchall()
            results = []
            for row in rows:
                item = dict(row)
                requirements = connection.execute(
                    """
                    SELECT id, name, description, required, max_size_bytes
                    FROM opportunity_document_requirements
                    WHERE opportunity_id = ? AND active = 1 AND required = 1 ORDER BY name
                    """,
                    (row["id"],),
                ).fetchall()
                item["documents"] = [
                    {**dict(requirement), "required": bool(requirement["required"])}
                    for requirement in requirements
                ]
                item["required_documents"] = [
                    requirement["name"] for requirement in requirements if requirement["required"]
                ]
                item["required_document_count"] = len(item["required_documents"])
                results.append(item)
            return {
                "items": results,
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size,
            }

    @app.get("/coordinator-assignments")
    def list_coordinator_assignments(
        principal: Principal = Depends(current_principal),
    ) -> list[dict]:
        return service.list_unassigned_proposals(principal)

    @app.post("/proposals/{proposal_id}/coordinator-assignment", status_code=201)
    def assign_coordinator_to_self(
        proposal_id: str, principal: Principal = Depends(current_principal)
    ) -> dict:
        return service.assign_proposal_to_self(principal, proposal_id)

    @app.get("/proposals")
    def list_proposals(principal: Principal = Depends(current_principal)) -> list[dict]:
        return service.list_proposals(principal)

    @app.get("/notifications")
    def list_notifications(principal: Principal = Depends(current_principal)) -> list[dict]:
        return service.list_notifications(principal)

    @app.get("/proposals/{proposal_id}/document-verification")
    def get_document_verification(
        proposal_id: str, principal: Principal = Depends(current_principal)
    ) -> dict:
        return service.get_document_verification(principal, proposal_id)

    @app.put("/proposals/{proposal_id}/document-verification")
    def update_document_verification(
        proposal_id: str, request: VerificationInput,
        principal: Principal = Depends(current_principal),
    ) -> dict:
        return service.update_document_verification(
            principal, proposal_id, request.status, request.notes, request.due_date
        )

    @app.get("/proposals/{proposal_id}/documents")
    def list_proposal_documents(
        proposal_id: str, principal: Principal = Depends(current_principal)
    ) -> list[dict]:
        return service.list_proposal_documents(principal, proposal_id)

    @app.post("/proposals/{proposal_id}/documents/{requirement_id}", status_code=201)
    def upload_proposal_document(
        proposal_id: str,
        requirement_id: str,
        file: UploadFile = File(...),
        principal: Principal = Depends(current_principal),
    ) -> dict:
        return service.upload_proposal_document(
            principal, proposal_id, requirement_id, file.file, file.filename
        )

    @app.get("/proposals/{proposal_id}/documents/{document_id}/download")
    def download_proposal_document(
        proposal_id: str, document_id: str,
        principal: Principal = Depends(current_principal),
    ) -> FileResponse:
        path, original_filename = service.get_document_download(
            principal, proposal_id, document_id
        )
        return FileResponse(
            path,
            media_type="application/octet-stream",
            filename=original_filename,
            headers={
                "X-Content-Type-Options": "nosniff",
                "Cache-Control": "private, no-store",
            },
        )

    @app.post("/proposals", status_code=201)
    def create_proposal(
        request: ProposalInput,
        principal: Principal = Depends(current_principal),
    ) -> dict:
        data = request.model_dump()
        return service.create_proposal(principal, data)

    @app.get("/proposals/{proposal_id}")
    def get_proposal(
        proposal_id: str,
        principal: Principal = Depends(current_principal),
    ) -> dict:
        return service.get_proposal(principal, proposal_id)

    @app.delete("/proposals/{proposal_id}")
    def delete_proposal(
        proposal_id: str,
        principal: Principal = Depends(current_principal),
    ) -> dict:
        return service.delete_proposal(principal, proposal_id)

    @app.patch("/proposals/{proposal_id}")
    def update_proposal(
        proposal_id: str,
        request: ProposalUpdateInput,
        principal: Principal = Depends(current_principal),
    ) -> dict:
        updates = request.model_dump(exclude_unset=True)
        expected_version = updates.pop("expected_version")
        return service.update_draft(principal, proposal_id, updates, expected_version)

    @app.post("/proposals/{proposal_id}/submit")
    def submit_proposal(
        proposal_id: str,
        request: SubmitProposalInput,
        principal: Principal = Depends(current_principal),
    ) -> dict:
        return service.submit_proposal(principal, proposal_id, request.expected_version)

    @app.get("/proposals/{proposal_id}/versions/{version_id}")
    def get_version(
        proposal_id: str,
        version_id: str,
        principal: Principal = Depends(current_principal),
    ) -> dict:
        return service.get_submitted_version(principal, proposal_id, version_id)

    @app.get("/proposals/{proposal_id}/audit")
    def get_audit(
        proposal_id: str,
        principal: Principal = Depends(current_principal),
    ) -> list[dict]:
        return service.get_audit_events(principal, proposal_id)

    return app


app = create_app()
