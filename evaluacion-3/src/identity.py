from dataclasses import dataclass
import sqlite3

from .domain import DomainError


@dataclass(frozen=True)
class Principal:
    id: str
    role: str


def authenticate(connection: sqlite3.Connection, token: str | None, token_subjects: dict[str, str]) -> Principal:
    if not token or token not in token_subjects:
        raise DomainError("unauthenticated", "A valid demo bearer token is required", 401)

    row = connection.execute(
        "SELECT id, role FROM users WHERE identity_subject = ? AND active = 1",
        (token_subjects[token],),
    ).fetchone()
    if row is None:
        raise DomainError("unauthenticated", "The authenticated user is not active", 401)
    return Principal(id=row["id"], role=row["role"])


def require_role(principal: Principal, *roles: str) -> None:
    if principal.role not in roles:
        raise DomainError("forbidden", "The user's role cannot perform this operation", 403)


def require_membership(
    connection: sqlite3.Connection,
    proposal_id: str,
    principal: Principal,
    relationship: str | None = None,
) -> None:
    query = "SELECT relationship FROM proposal_memberships WHERE proposal_id = ? AND user_id = ?"
    row = connection.execute(query, (proposal_id, principal.id)).fetchone()
    if row is None or (relationship is not None and row["relationship"] != relationship):
        raise DomainError("forbidden", "The user is not authorized for this proposal", 403)
