from contextlib import asynccontextmanager
from datetime import date
import os
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .database import Database
from .domain import DomainError
from .identity import Principal, authenticate
from .service import ProposalService


DEMO_TOKEN_SUBJECTS = {
    "demo-pi-alice": "hu-demo-alice",
    "demo-pi-bob": "hu-demo-bob",
    "demo-coordinator": "hu-demo-coordinator",
}
bearer_scheme = HTTPBearer(auto_error=False)


class ProposalInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    opportunity_id: str = Field(min_length=1)
    title: str | None = None
    sponsor: str | None = None
    abstract: str | None = None
    requested_amount: float | None = None
    deadline: date | None = None


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
    deadline: date | None = None


def create_app(
    database_path: str | Path | None = None,
    token_subjects: dict[str, str] | None = None,
) -> FastAPI:
    resolved_path = database_path or os.environ.get(
        "DH03_DB_PATH",
        str(Path(__file__).resolve().parents[1] / "data" / "dh03.sqlite3"),
    )
    database = Database(resolved_path)
    service = ProposalService(database)
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
        return {"status": "ok"}

    @app.get("/opportunities")
    def list_opportunities() -> list[dict[str, str]]:
        with database.read() as connection:
            rows = connection.execute(
                "SELECT id, title, sponsor, deadline FROM opportunities ORDER BY deadline"
            ).fetchall()
            return [dict(row) for row in rows]

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
