from datetime import date, datetime, timezone
import hashlib
import json
import sqlite3
import uuid
from typing import Any

from .database import Database
from .document_store import LocalDocumentStore
from .domain import DomainError, validate_submission
from .identity import Principal, require_membership, require_role


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _proposal(row: sqlite3.Row) -> dict[str, Any]:
    verified = row["status"] == "VERIFIED" or (
        "verification_status" in row.keys() and row["verification_status"] == "COMPLETE"
    )
    proposal = {
        "id": row["id"],
        "opportunity_id": row["opportunity_id"],
        "title": row["title"],
        "sponsor": row["sponsor"],
        "abstract": row["abstract"],
        "requested_amount": row["requested_amount"],
        "deadline": row["deadline"],
        "status": "VERIFIED" if verified else row["status"],
        "version": row["version"],
        "submitted_version_id": row["submitted_version_id"],
        "created_by": row["created_by"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }
    if "opportunity_title" in row.keys():
        proposal["opportunity_title"] = row["opportunity_title"]
        proposal["opportunity_description"] = row["opportunity_description"]
    return proposal


class ProposalService:
    def __init__(self, database: Database, document_store: LocalDocumentStore):
        self.database = database
        self.document_store = document_store

    def create_proposal(self, principal: Principal, data: dict[str, Any]) -> dict[str, Any]:
        require_role(principal, "PI")
        now = _now()
        proposal_id = str(uuid.uuid4())
        with self.database.transaction() as connection:
            opportunity = connection.execute(
                "SELECT id, sponsor, deadline, status FROM opportunities WHERE id = ?", (data["opportunity_id"],)
            ).fetchone()
            if opportunity is None:
                raise DomainError("opportunity_not_found", "Opportunity was not found", 404)
            if opportunity["status"] != "OPEN" or opportunity["deadline"] < date.today().isoformat():
                raise DomainError("opportunity_closed", "This funding opportunity is no longer open", 409)
            connection.execute(
                """
                INSERT INTO proposals (
                    id, opportunity_id, title, sponsor, abstract, requested_amount,
                    deadline, status, version, created_by, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'DRAFT', 0, ?, ?, ?)
                """,
                (
                    proposal_id,
                    data["opportunity_id"],
                    data.get("title"),
                    opportunity["sponsor"],
                    data.get("abstract"),
                    data.get("requested_amount"),
                    opportunity["deadline"],
                    principal.id,
                    now,
                    now,
                ),
            )
            connection.execute(
                """
                INSERT INTO proposal_memberships (proposal_id, user_id, relationship)
                VALUES (?, ?, 'OWNER_PI')
                """,
                (proposal_id, principal.id),
            )
            connection.execute(
                """
                INSERT INTO document_verifications
                    (proposal_id, status, due_date, notes, updated_at)
                VALUES (?, 'PENDING', NULL, '', ?)
                """,
                (proposal_id, now),
            )
            self._audit(
                connection,
                principal.id,
                "proposal.created",
                proposal_id,
                {"status": "DRAFT"},
                now,
            )
            row = connection.execute("SELECT * FROM proposals WHERE id = ?", (proposal_id,)).fetchone()
            return _proposal(row)

    def list_proposals(self, principal: Principal) -> list[dict[str, Any]]:
        require_role(principal, "PI", "RESEARCH_OFFICE_COORDINATOR")
        with self.database.read() as connection:
            rows = connection.execute(
                """
                SELECT p.*, o.title AS opportunity_title,
                       o.description AS opportunity_description,
                       v.status AS verification_status
                FROM proposals p
                JOIN opportunities o ON o.id = p.opportunity_id
                JOIN proposal_memberships m ON m.proposal_id = p.id
                LEFT JOIN document_verifications v ON v.proposal_id = p.id
                WHERE m.user_id = ? ORDER BY p.updated_at DESC
                """,
                (principal.id,),
            ).fetchall()
            return [_proposal(row) for row in rows]

    def list_unassigned_proposals(self, principal: Principal) -> list[dict[str, Any]]:
        require_role(principal, "RESEARCH_OFFICE_COORDINATOR")
        with self.database.read() as connection:
            rows = connection.execute(
                """
                SELECT p.id, p.title, p.abstract, p.status, p.deadline,
                       o.title AS opportunity_title, o.description AS opportunity_description,
                       p.created_at
                FROM proposals p
                JOIN opportunities o ON o.id = p.opportunity_id
                WHERE p.status = 'SUBMITTED' AND NOT EXISTS (
                    SELECT 1 FROM proposal_memberships m
                    WHERE m.proposal_id = p.id AND m.relationship = 'ASSIGNED_COORDINATOR'
                )
                ORDER BY p.created_at
                """
            ).fetchall()
            return [dict(row) for row in rows]

    def assign_proposal_to_self(self, principal: Principal, proposal_id: str) -> dict[str, Any]:
        require_role(principal, "RESEARCH_OFFICE_COORDINATOR")
        now = _now()
        with self.database.transaction() as connection:
            proposal = connection.execute(
                "SELECT id, status FROM proposals WHERE id = ?", (proposal_id,)
            ).fetchone()
            if proposal is None:
                raise DomainError("proposal_not_found", "Proposal was not found", 404)
            if proposal["status"] != "SUBMITTED":
                raise DomainError(
                    "proposal_not_ready_for_assignment",
                    "A proposal must be sent to office review before coordinator assignment",
                    409,
                )
            assigned = connection.execute(
                """
                SELECT user_id FROM proposal_memberships
                WHERE proposal_id = ? AND relationship = 'ASSIGNED_COORDINATOR'
                """,
                (proposal_id,),
            ).fetchone()
            if assigned is not None:
                raise DomainError("coordinator_already_assigned", "Proposal already has an assigned coordinator", 409)
            connection.execute(
                """
                INSERT INTO proposal_memberships (proposal_id, user_id, relationship)
                VALUES (?, ?, 'ASSIGNED_COORDINATOR')
                """,
                (proposal_id, principal.id),
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO document_verifications
                    (proposal_id, status, due_date, notes, updated_at)
                VALUES (?, 'PENDING', NULL, '', ?)
                """,
                (proposal_id, now),
            )
            self._audit(
                connection, principal.id, "proposal.coordinator_assigned", proposal_id,
                {"coordinator_id": principal.id}, now,
            )
            return {"proposal_id": proposal_id, "coordinator_id": principal.id, "assigned_at": now}

    def list_proposal_documents(self, principal: Principal, proposal_id: str) -> list[dict[str, Any]]:
        require_role(principal, "PI", "RESEARCH_OFFICE_COORDINATOR")
        with self.database.read() as connection:
            proposal = connection.execute(
                "SELECT opportunity_id FROM proposals WHERE id = ?", (proposal_id,)
            ).fetchone()
            if proposal is None:
                raise DomainError("proposal_not_found", "Proposal was not found", 404)
            require_membership(connection, proposal_id, principal)
            requirements = connection.execute(
                """
                SELECT r.id, r.name, r.description, r.required, r.max_size_bytes,
                       d.id AS document_id, d.version, d.original_filename,
                       d.content_sha256, d.size_bytes, d.uploaded_at
                FROM opportunity_document_requirements r
                LEFT JOIN proposal_documents d ON d.proposal_id = ?
                    AND d.requirement_id = r.id
                    AND d.version = (
                        SELECT MAX(d2.version) FROM proposal_documents d2
                        WHERE d2.proposal_id = ? AND d2.requirement_id = r.id
                    )
                WHERE r.opportunity_id = ? AND r.active = 1 AND r.required = 1
                ORDER BY r.required DESC, r.name
                """,
                (proposal_id, proposal_id, proposal["opportunity_id"]),
            ).fetchall()
            return [
                {
                    "requirement_id": row["id"], "name": row["name"],
                    "description": row["description"], "required": bool(row["required"]),
                    "max_size_bytes": row["max_size_bytes"], "uploaded": row["document_id"] is not None,
                    "document_id": row["document_id"], "version": row["version"],
                    "filename": row["original_filename"], "content_sha256": row["content_sha256"],
                    "size_bytes": row["size_bytes"], "uploaded_at": row["uploaded_at"],
                }
                for row in requirements
            ]

    def upload_proposal_document(
        self, principal: Principal, proposal_id: str, requirement_id: str,
        file_stream, filename: str | None,
    ) -> dict[str, Any]:
        require_role(principal, "PI")
        with self.database.read() as connection:
            proposal = connection.execute(
                "SELECT opportunity_id, status FROM proposals WHERE id = ?", (proposal_id,)
            ).fetchone()
            if proposal is None:
                raise DomainError("proposal_not_found", "Proposal was not found", 404)
            require_membership(connection, proposal_id, principal, "OWNER_PI")
            if proposal["status"] != "DRAFT":
                raise DomainError("invalid_state_transition", "Documents can only be uploaded to a draft", 409)
            self._assert_not_verified(connection, proposal_id)
            requirement = connection.execute(
                """
                SELECT id, name, max_size_bytes FROM opportunity_document_requirements
                WHERE id = ? AND opportunity_id = ? AND active = 1 AND required = 1
                """,
                (requirement_id, proposal["opportunity_id"]),
            ).fetchone()
            if requirement is None:
                raise DomainError("document_requirement_not_found", "Document requirement was not found", 404)

        try:
            staged = self.document_store.stage_pdf(file_stream, filename, requirement["max_size_bytes"])
        except DomainError as error:
            with self.database.transaction() as connection:
                current = connection.execute(
                    "SELECT status FROM proposals WHERE id = ?", (proposal_id,)
                ).fetchone()
                if current is not None and current["status"] == "DRAFT":
                    try:
                        require_membership(connection, proposal_id, principal, "OWNER_PI")
                    except DomainError:
                        raise error
                    self._audit(
                        connection, principal.id, "proposal.document_upload_rejected", proposal_id,
                        {"requirement_id": requirement_id, "reason": error.code},
                        _now(), outcome="DENIED",
                    )
            raise
        final_path = None
        try:
            with self.database.transaction() as connection:
                proposal = connection.execute(
                    "SELECT opportunity_id, status FROM proposals WHERE id = ?", (proposal_id,)
                ).fetchone()
                if proposal is None:
                    raise DomainError("proposal_not_found", "Proposal was not found", 404)
                require_membership(connection, proposal_id, principal, "OWNER_PI")
                if proposal["status"] != "DRAFT":
                    raise DomainError("invalid_state_transition", "Documents can only be uploaded to a draft", 409)
                self._assert_not_verified(connection, proposal_id)
                current_requirement = connection.execute(
                    "SELECT id FROM opportunity_document_requirements WHERE id = ? AND opportunity_id = ? AND active = 1 AND required = 1",
                    (requirement_id, proposal["opportunity_id"]),
                ).fetchone()
                if current_requirement is None:
                    raise DomainError("document_requirement_not_found", "Document requirement was not found", 404)
                version = connection.execute(
                    "SELECT COALESCE(MAX(version), 0) + 1 FROM proposal_documents "
                    "WHERE proposal_id = ? AND requirement_id = ?",
                    (proposal_id, requirement_id),
                ).fetchone()[0]
                previous_document = connection.execute(
                    "SELECT version FROM proposal_documents WHERE proposal_id = ? AND requirement_id = ? ORDER BY version DESC LIMIT 1",
                    (proposal_id, requirement_id),
                ).fetchone()
                final_path = self.document_store.promote(staged)
                document_id = str(uuid.uuid4())
                now = _now()
                connection.execute(
                    """
                    INSERT INTO proposal_documents
                        (id, proposal_id, requirement_id, version, original_filename,
                         storage_key, content_sha256, content_type, size_bytes, uploaded_by, uploaded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'application/pdf', ?, ?, ?)
                    """,
                    (document_id, proposal_id, requirement_id, version, staged.original_filename,
                     staged.storage_key, staged.content_sha256, staged.size_bytes, principal.id, now),
                )
                self._audit(
                    connection, principal.id, "proposal.document_uploaded", proposal_id,
                    {"document_id": document_id, "requirement_id": requirement_id,
                     "requirement_name": requirement["name"],
                     "filename": staged.original_filename,
                     "previous_version": previous_document["version"] if previous_document else None,
                     "version": version, "sha256": staged.content_sha256,
                     "size_bytes": staged.size_bytes,
                     "reason": "Nueva versión de documento" if previous_document else "Primera carga del documento",
                     "documents": self._latest_documents(connection, proposal_id)}, now,
                )
                return {
                    "id": document_id, "proposal_id": proposal_id,
                    "requirement_id": requirement_id, "version": version,
                    "filename": staged.original_filename,
                    "content_sha256": staged.content_sha256,
                    "size_bytes": staged.size_bytes, "uploaded_at": now,
                }
        except Exception:
            if final_path is not None:
                final_path.unlink(missing_ok=True)
            self.document_store.discard(staged)
            raise

    def get_document_download(self, principal: Principal, proposal_id: str, document_id: str):
        require_role(principal, "PI", "RESEARCH_OFFICE_COORDINATOR")
        with self.database.read() as connection:
            proposal = connection.execute(
                "SELECT id FROM proposals WHERE id = ?", (proposal_id,)
            ).fetchone()
            if proposal is None:
                raise DomainError("proposal_not_found", "Proposal was not found", 404)
            require_membership(connection, proposal_id, principal)
            document = connection.execute(
                "SELECT * FROM proposal_documents WHERE id = ? AND proposal_id = ?",
                (document_id, proposal_id),
            ).fetchone()
            if document is None:
                raise DomainError("document_not_found", "Document was not found", 404)
            path = self.document_store.object_path(document["storage_key"])
            if not path.is_file():
                raise DomainError("document_unavailable", "Stored document is unavailable", 404)
            return path, document["original_filename"]

    def get_document_verification(self, principal: Principal, proposal_id: str) -> dict[str, Any]:
        require_role(principal, "PI", "RESEARCH_OFFICE_COORDINATOR")
        with self.database.read() as connection:
            proposal = connection.execute(
                "SELECT id FROM proposals WHERE id = ?", (proposal_id,)
            ).fetchone()
            if proposal is None:
                raise DomainError("proposal_not_found", "Proposal was not found", 404)
            require_membership(connection, proposal_id, principal)
            row = connection.execute(
                "SELECT * FROM document_verifications WHERE proposal_id = ?", (proposal_id,)
            ).fetchone()
            if row is None:
                return {"proposal_id": proposal_id, "status": "PENDING", "due_date": None,
                        "notes": "", "updated_by": None, "updated_at": None}
            return dict(row)

    def update_document_verification(
        self, principal: Principal, proposal_id: str, status: str, notes: str,
        due_date: date | None,
    ) -> dict[str, Any]:
        require_role(principal, "RESEARCH_OFFICE_COORDINATOR")
        allowed = {"PENDING", "COMPLETE", "CHANGES_REQUIRED"}
        if status not in allowed:
            raise DomainError("invalid_verification_status", "Invalid document verification status", 422)
        now = _now()
        with self.database.transaction() as connection:
            proposal = connection.execute(
                "SELECT id, deadline, status FROM proposals WHERE id = ?", (proposal_id,)
            ).fetchone()
            if proposal is None:
                raise DomainError("proposal_not_found", "Proposal was not found", 404)
            require_membership(connection, proposal_id, principal, "ASSIGNED_COORDINATOR")
            previous = connection.execute(
                "SELECT due_date, status, notes FROM document_verifications WHERE proposal_id = ?", (proposal_id,)
            ).fetchone()
            if previous and previous["status"] == "COMPLETE":
                raise DomainError("proposal_locked_after_verification", "Verified proposals are final in this workflow stage", 409)
            if proposal["status"] != "SUBMITTED":
                raise DomainError(
                    "proposal_not_under_office_review",
                    "The proposal must be sent to office review before coordinator verification",
                    409,
                )
            document_manifest = self._latest_documents(connection, proposal_id)
            missing_documents = [item["name"] for item in document_manifest if not item["document_id"]]
            if status == "COMPLETE" and missing_documents:
                raise DomainError("missing_required_documents", f"Required documents are missing: {', '.join(missing_documents)}", 422)
            effective_due_date = (
                due_date.isoformat() if due_date else
                (previous["due_date"] if previous else None)
            )
            if status in {"PENDING", "CHANGES_REQUIRED"} and effective_due_date is None:
                raise DomainError(
                    "verification_deadline_required",
                    "Set a document-verification deadline for pending work",
                    422,
                )
            if effective_due_date and proposal["deadline"] and effective_due_date > proposal["deadline"]:
                raise DomainError(
                    "verification_deadline_after_opportunity",
                    "The internal verification deadline cannot be after the opportunity deadline",
                    422,
                )
            connection.execute(
                """
                INSERT INTO document_verifications
                    (proposal_id, status, due_date, notes, updated_by, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(proposal_id) DO UPDATE SET
                    status = excluded.status, notes = excluded.notes,
                    due_date = COALESCE(excluded.due_date, document_verifications.due_date),
                    updated_by = excluded.updated_by, updated_at = excluded.updated_at
                """,
                (proposal_id, status, effective_due_date,
                 notes.strip(), principal.id, now),
            )
            self._audit(
                connection, principal.id, "documents.verification_updated", proposal_id,
                {
                    "status": status,
                    "previous_status": previous["status"] if previous else None,
                    "notes": notes.strip(),
                    "previous_notes": previous["notes"] if previous else "",
                    "due_date": effective_due_date,
                    "reason": notes.strip() or (
                        "Documentación verificada; la propuesta queda congelada"
                        if status == "COMPLETE" else
                        "Se solicita corrección documental"
                        if status == "CHANGES_REQUIRED" else
                        "Seguimiento de verificación documental"
                    ),
                    "documents": document_manifest,
                },
                now,
            )
            if status == "COMPLETE":
                changed = connection.execute(
                    "UPDATE proposals SET status = 'VERIFIED', updated_at = ? WHERE id = ? AND status = 'SUBMITTED'",
                    (now, proposal_id),
                ).rowcount
                if changed != 1:
                    raise DomainError(
                        "proposal_not_under_office_review",
                        "Only a proposal under office review can become verified",
                        409,
                    )
            if status == "CHANGES_REQUIRED":
                connection.execute(
                    """UPDATE proposals SET status = 'DRAFT', submitted_version_id = NULL,
                              updated_at = ? WHERE id = ? AND status = 'SUBMITTED'""",
                    (now, proposal_id),
                )
            row = connection.execute(
                "SELECT * FROM document_verifications WHERE proposal_id = ?", (proposal_id,)
            ).fetchone()
            return dict(row)

    def list_notifications(self, principal: Principal) -> list[dict[str, Any]]:
        require_role(principal, "PI", "RESEARCH_OFFICE_COORDINATOR")
        today = date.today()
        with self.database.read() as connection:
            rows = connection.execute(
                """
                SELECT p.id AS proposal_id, p.title, v.status, v.due_date
                FROM document_verifications v
                JOIN proposals p ON p.id = v.proposal_id
                JOIN proposal_memberships m ON m.proposal_id = p.id
                WHERE m.user_id = ? AND v.status IN ('PENDING', 'CHANGES_REQUIRED')
                  AND v.due_date IS NOT NULL
                ORDER BY v.due_date
                """,
                (principal.id,),
            ).fetchall()
            notices = []
            for row in rows:
                due = date.fromisoformat(row["due_date"])
                days = (due - today).days
                if days <= 7:
                    notices.append({
                        "proposal_id": row["proposal_id"], "title": row["title"],
                        "status": row["status"], "due_date": row["due_date"],
                        "days_remaining": days,
                        "message": "Plazo vencido" if days < 0 else
                                   "El plazo vence hoy" if days == 0 else
                                   f"Verificación documental pendiente: {days} días",
                    })
            return notices

    def get_proposal(self, principal: Principal, proposal_id: str) -> dict[str, Any]:
        require_role(principal, "PI", "RESEARCH_OFFICE_COORDINATOR")
        with self.database.read() as connection:
            row = connection.execute(
                """SELECT p.*, o.title AS opportunity_title,
                          o.description AS opportunity_description,
                          v.status AS verification_status
                   FROM proposals p JOIN opportunities o ON o.id = p.opportunity_id
                   LEFT JOIN document_verifications v ON v.proposal_id = p.id
                   WHERE p.id = ?""",
                (proposal_id,),
            ).fetchone()
            if row is None:
                raise DomainError("proposal_not_found", "Proposal was not found", 404)
            require_membership(connection, proposal_id, principal)
            return _proposal(row)

    def delete_proposal(self, principal: Principal, proposal_id: str) -> dict[str, Any]:
        require_role(principal, "PI")
        stored_files = []
        with self.database.transaction() as connection:
            proposal = connection.execute(
                """SELECT p.id, v.status AS verification_status FROM proposals p
                   LEFT JOIN document_verifications v ON v.proposal_id = p.id WHERE p.id = ?""", (proposal_id,)
            ).fetchone()
            if proposal is None:
                raise DomainError("proposal_not_found", "Proposal was not found", 404)
            require_membership(connection, proposal_id, principal, "OWNER_PI")
            self._assert_not_verified(connection, proposal_id)
            connection.execute("PRAGMA defer_foreign_keys = ON")
            keys = connection.execute(
                "SELECT storage_key FROM proposal_documents WHERE proposal_id = ?",
                (proposal_id,),
            ).fetchall()
            stored_files = [self.document_store.object_path(row["storage_key"]) for row in keys]
            connection.execute(
                "DELETE FROM notification_outbox WHERE aggregate_id = ?", (proposal_id,)
            )
            connection.execute(
                "DELETE FROM audit_events WHERE entity_type = 'Proposal' AND entity_id = ?",
                (proposal_id,),
            )
            connection.execute(
                "DELETE FROM proposal_documents WHERE proposal_id = ?", (proposal_id,)
            )
            connection.execute(
                "DELETE FROM proposal_versions WHERE proposal_id = ?", (proposal_id,)
            )
            connection.execute(
                "DELETE FROM document_verifications WHERE proposal_id = ?", (proposal_id,)
            )
            connection.execute(
                "DELETE FROM proposal_memberships WHERE proposal_id = ?", (proposal_id,)
            )
            connection.execute("DELETE FROM proposals WHERE id = ?", (proposal_id,))
        for path in stored_files:
            path.unlink(missing_ok=True)
        return {"proposal_id": proposal_id, "deleted": True}

    def update_draft(
        self,
        principal: Principal,
        proposal_id: str,
        updates: dict[str, Any],
        expected_version: int,
    ) -> dict[str, Any]:
        require_role(principal, "PI")
        if not updates:
            raise DomainError("empty_update", "At least one proposal field must be provided", 422)
        allowed_fields = {"title", "abstract", "requested_amount"}
        invalid_fields = set(updates) - allowed_fields
        if invalid_fields:
            raise DomainError(
                "invalid_update_fields",
                f"Fields cannot be updated: {', '.join(sorted(invalid_fields))}",
                422,
            )

        with self.database.transaction() as connection:
            row = connection.execute("SELECT * FROM proposals WHERE id = ?", (proposal_id,)).fetchone()
            if row is None:
                raise DomainError("proposal_not_found", "Proposal was not found", 404)
            require_membership(connection, proposal_id, principal, "OWNER_PI")
            if row["version"] != expected_version:
                raise DomainError(
                    "stale_proposal_version",
                    f"Expected version {expected_version}; current version is {row['version']}",
                    409,
                )
            if row["status"] != "DRAFT":
                raise DomainError(
                    "invalid_state_transition",
                    f"A proposal in {row['status']} state cannot be edited",
                    409,
                )
            self._assert_not_verified(connection, proposal_id)
            field_changes = {
                field: {"from": row[field], "to": updates[field]} for field in updates
            }

            assignments = ", ".join(f"{field} = ?" for field in updates)
            now = _now()
            new_version = expected_version + 1
            changed = connection.execute(
                f"""
                UPDATE proposals
                SET {assignments}, version = ?, updated_at = ?
                WHERE id = ? AND status = 'DRAFT' AND version = ?
                """,
                (*updates.values(), new_version, now, proposal_id, expected_version),
            ).rowcount
            if changed != 1:
                raise DomainError(
                    "stale_proposal_version",
                    "Proposal changed while the update was being processed",
                    409,
                )

            self._audit(
                connection,
                principal.id,
                "proposal.updated",
                proposal_id,
                {
                    "fields": sorted(updates),
                    "changes": field_changes,
                    "version": new_version,
                    "reason": "El investigador actualizó los datos de la propuesta",
                    "documents": self._latest_documents(connection, proposal_id),
                },
                now,
            )
            updated = connection.execute(
                "SELECT * FROM proposals WHERE id = ?", (proposal_id,)
            ).fetchone()
            return _proposal(updated)

    def submit_proposal(
        self,
        principal: Principal,
        proposal_id: str,
        expected_version: int,
    ) -> dict[str, Any]:
        require_role(principal, "PI")
        now = _now()
        with self.database.transaction() as connection:
            row = connection.execute("SELECT * FROM proposals WHERE id = ?", (proposal_id,)).fetchone()
            if row is None:
                raise DomainError("proposal_not_found", "Proposal was not found", 404)
            require_membership(connection, proposal_id, principal, "OWNER_PI")
            if row["version"] != expected_version:
                raise DomainError(
                    "stale_proposal_version",
                    f"Expected version {expected_version}; current version is {row['version']}",
                    409,
                )
            if row["status"] != "DRAFT":
                raise DomainError(
                    "invalid_state_transition",
                    f"A proposal in {row['status']} state cannot be submitted",
                    409,
                )
            self._assert_not_verified(connection, proposal_id)

            proposal = _proposal(row)
            validate_submission(proposal)
            requirements = connection.execute(
                """
                SELECT r.id, r.name FROM opportunity_document_requirements r
                WHERE r.opportunity_id = ? AND r.active = 1 AND r.required = 1
                ORDER BY r.name
                """,
                (proposal["opportunity_id"],),
            ).fetchall()
            missing_documents = []
            for requirement in requirements:
                latest = connection.execute(
                    """
                    SELECT id FROM proposal_documents
                    WHERE proposal_id = ? AND requirement_id = ?
                    ORDER BY version DESC LIMIT 1
                    """,
                    (proposal_id, requirement["id"]),
                ).fetchone()
                if latest is None:
                    missing_documents.append(requirement["name"])
            if missing_documents:
                raise DomainError(
                    "missing_required_documents",
                    f"Upload all required documents before submission: {', '.join(missing_documents)}",
                    422,
                )
            document_manifest = self._latest_documents(connection, proposal_id)
            snapshot = {
                "proposal_id": proposal["id"],
                "opportunity_id": proposal["opportunity_id"],
                "title": proposal["title"].strip(),
                "sponsor": proposal["sponsor"].strip(),
                "abstract": proposal["abstract"].strip(),
                "requested_amount": proposal["requested_amount"],
                "deadline": proposal["deadline"],
                "documents": document_manifest,
            }
            snapshot_json = _json(snapshot)
            content_hash = hashlib.sha256(snapshot_json.encode("utf-8")).hexdigest()
            version_id = str(uuid.uuid4())
            sequence = connection.execute(
                "SELECT COALESCE(MAX(sequence), 0) + 1 FROM proposal_versions WHERE proposal_id = ?",
                (proposal_id,),
            ).fetchone()[0]
            connection.execute(
                """
                INSERT INTO proposal_versions
                    (id, proposal_id, sequence, snapshot_json, content_hash, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (version_id, proposal_id, sequence, snapshot_json, content_hash, principal.id, now),
            )
            changed = connection.execute(
                """
                UPDATE proposals
                SET status = 'SUBMITTED', version = ?, submitted_version_id = ?, updated_at = ?
                WHERE id = ? AND status = 'DRAFT' AND version = ?
                """,
                (expected_version + 1, version_id, now, proposal_id, expected_version),
            ).rowcount
            if changed != 1:
                raise DomainError(
                    "stale_proposal_version",
                    "Proposal changed while submission was being processed",
                    409,
                )

            audit_id = self._audit(
                connection,
                principal.id,
                "proposal.submitted",
                proposal_id,
                {"version_id": version_id, "content_hash": content_hash,
                 "reason": "La propuesta se envió a revisión de la oficina con estos documentos",
                 "documents": document_manifest},
                now,
            )
            connection.execute(
                """
                INSERT INTO notification_outbox
                    (id, event_key, event_type, aggregate_id, payload_json, created_at)
                VALUES (?, ?, 'proposal.submitted', ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    audit_id,
                    proposal_id,
                    _json({"proposal_id": proposal_id, "version_id": version_id}),
                    now,
                ),
            )
            connection.execute(
                """UPDATE document_verifications
                   SET status = 'PENDING', notes = '', updated_by = ?, updated_at = ?
                   WHERE proposal_id = ?""",
                (principal.id, now, proposal_id),
            )
            submitted = connection.execute(
                "SELECT * FROM proposals WHERE id = ?", (proposal_id,)
            ).fetchone()
            return _proposal(submitted)

    def get_submitted_version(
        self,
        principal: Principal,
        proposal_id: str,
        version_id: str,
    ) -> dict[str, Any]:
        require_role(principal, "PI", "RESEARCH_OFFICE_COORDINATOR")
        with self.database.read() as connection:
            proposal = connection.execute(
                "SELECT id FROM proposals WHERE id = ?", (proposal_id,)
            ).fetchone()
            if proposal is None:
                raise DomainError("proposal_not_found", "Proposal was not found", 404)
            require_membership(connection, proposal_id, principal)
            row = connection.execute(
                "SELECT * FROM proposal_versions WHERE id = ? AND proposal_id = ?",
                (version_id, proposal_id),
            ).fetchone()
            if row is None:
                raise DomainError("proposal_version_not_found", "Proposal version was not found", 404)
            return {
                "id": row["id"],
                "proposal_id": row["proposal_id"],
                "sequence": row["sequence"],
                "snapshot": json.loads(row["snapshot_json"]),
                "content_hash": row["content_hash"],
                "created_by": row["created_by"],
                "created_at": row["created_at"],
            }

    def get_audit_events(self, principal: Principal, proposal_id: str) -> list[dict[str, Any]]:
        require_role(principal, "PI", "RESEARCH_OFFICE_COORDINATOR")
        with self.database.read() as connection:
            proposal = connection.execute(
                "SELECT id FROM proposals WHERE id = ?", (proposal_id,)
            ).fetchone()
            if proposal is None:
                raise DomainError("proposal_not_found", "Proposal was not found", 404)
            require_membership(connection, proposal_id, principal)
            rows = connection.execute(
                """
                SELECT id, actor_id, event_type, entity_type, entity_id, outcome,
                       details_json, occurred_at
                FROM audit_events
                WHERE entity_type = 'Proposal' AND entity_id = ?
                ORDER BY occurred_at, id
                """,
                (proposal_id,),
            ).fetchall()
            return [
                {
                    "id": row["id"],
                    "actor_id": row["actor_id"],
                    "event_type": row["event_type"],
                    "entity_type": row["entity_type"],
                    "entity_id": row["entity_id"],
                    "outcome": row["outcome"],
                    "details": json.loads(row["details_json"]),
                    "occurred_at": row["occurred_at"],
                }
                for row in rows
            ]

    def _latest_documents(self, connection: sqlite3.Connection, proposal_id: str) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in connection.execute(
                """
                SELECT r.id AS requirement_id, r.name, r.required, d.id AS document_id,
                       d.version, d.original_filename AS filename, d.content_sha256,
                       d.size_bytes, d.uploaded_at
                FROM opportunity_document_requirements r
                LEFT JOIN proposal_documents d ON d.proposal_id = ? AND d.requirement_id = r.id
                  AND d.version = (
                      SELECT MAX(d2.version) FROM proposal_documents d2
                      WHERE d2.proposal_id = ? AND d2.requirement_id = r.id
                  )
                WHERE r.opportunity_id = (SELECT opportunity_id FROM proposals WHERE id = ?)
                  AND r.active = 1 AND r.required = 1
                ORDER BY r.name
                """,
                (proposal_id, proposal_id, proposal_id),
            ).fetchall()
        ]

    @staticmethod
    def _assert_not_verified(connection: sqlite3.Connection, proposal_id: str) -> None:
        row = connection.execute(
            "SELECT status FROM document_verifications WHERE proposal_id = ?",
            (proposal_id,),
        ).fetchone()
        if row and row["status"] == "COMPLETE":
            raise DomainError(
                "proposal_locked_after_verification",
                "Verified proposals cannot be changed or deleted in this workflow stage",
                409,
            )

    @staticmethod
    def _audit(
        connection: sqlite3.Connection,
        actor_id: str,
        event_type: str,
        proposal_id: str,
        details: dict[str, Any],
        occurred_at: str,
        outcome: str = "SUCCESS",
    ) -> str:
        audit_id = str(uuid.uuid4())
        connection.execute(
            """
            INSERT INTO audit_events (
                id, actor_id, event_type, entity_type, entity_id, outcome, details_json, occurred_at
            ) VALUES (?, ?, ?, 'Proposal', ?, ?, ?, ?)
            """,
            (audit_id, actor_id, event_type, proposal_id, outcome, _json(details), occurred_at),
        )
        return audit_id
