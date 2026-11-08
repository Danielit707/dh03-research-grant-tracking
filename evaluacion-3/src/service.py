from datetime import date, datetime, timezone
import hashlib
import json
import sqlite3
import uuid
from typing import Any

from .database import Database
from .domain import DomainError, validate_submission
from .identity import Principal, require_membership, require_role


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _proposal(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "opportunity_id": row["opportunity_id"],
        "title": row["title"],
        "sponsor": row["sponsor"],
        "abstract": row["abstract"],
        "requested_amount": row["requested_amount"],
        "deadline": row["deadline"],
        "status": row["status"],
        "version": row["version"],
        "submitted_version_id": row["submitted_version_id"],
        "created_by": row["created_by"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


class ProposalService:
    def __init__(self, database: Database):
        self.database = database

    def create_proposal(self, principal: Principal, data: dict[str, Any]) -> dict[str, Any]:
        require_role(principal, "PI")
        now = _now()
        proposal_id = str(uuid.uuid4())
        with self.database.transaction() as connection:
            opportunity = connection.execute(
                "SELECT id FROM opportunities WHERE id = ?", (data["opportunity_id"],)
            ).fetchone()
            if opportunity is None:
                raise DomainError("opportunity_not_found", "Opportunity was not found", 404)

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
                    data.get("sponsor"),
                    data.get("abstract"),
                    data.get("requested_amount"),
                    data.get("deadline").isoformat() if data.get("deadline") else None,
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

    def get_proposal(self, principal: Principal, proposal_id: str) -> dict[str, Any]:
        require_role(principal, "PI", "RESEARCH_OFFICE_COORDINATOR")
        with self.database.read() as connection:
            row = connection.execute("SELECT * FROM proposals WHERE id = ?", (proposal_id,)).fetchone()
            if row is None:
                raise DomainError("proposal_not_found", "Proposal was not found", 404)
            require_membership(connection, proposal_id, principal)
            return _proposal(row)

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
        allowed_fields = {"title", "sponsor", "abstract", "requested_amount", "deadline"}
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

            if "deadline" in updates and updates["deadline"] is not None:
                updates["deadline"] = updates["deadline"].isoformat()
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
                {"fields": sorted(updates), "version": new_version},
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

            proposal = _proposal(row)
            validate_submission(proposal)
            snapshot = {
                "proposal_id": proposal["id"],
                "opportunity_id": proposal["opportunity_id"],
                "title": proposal["title"].strip(),
                "sponsor": proposal["sponsor"].strip(),
                "abstract": proposal["abstract"].strip(),
                "requested_amount": proposal["requested_amount"],
                "deadline": proposal["deadline"],
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
                {"version_id": version_id, "content_hash": content_hash},
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

    @staticmethod
    def _audit(
        connection: sqlite3.Connection,
        actor_id: str,
        event_type: str,
        proposal_id: str,
        details: dict[str, Any],
        occurred_at: str,
    ) -> str:
        audit_id = str(uuid.uuid4())
        connection.execute(
            """
            INSERT INTO audit_events (
                id, actor_id, event_type, entity_type, entity_id, outcome, details_json, occurred_at
            ) VALUES (?, ?, ?, 'Proposal', ?, 'SUCCESS', ?, ?)
            """,
            (audit_id, actor_id, event_type, proposal_id, _json(details), occurred_at),
        )
        return audit_id
