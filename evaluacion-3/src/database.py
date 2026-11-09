from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Iterator


class Database:
    def __init__(self, path: str | Path):
        self.path = str(path)

    def connect(self) -> sqlite3.Connection:
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        return connection

    def initialize(self) -> None:
        schema_path = Path(__file__).with_name("schema.sql")
        connection = self.connect()
        try:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.executescript(schema_path.read_text(encoding="utf-8"))
            requirement_columns = {
                row["name"] for row in connection.execute(
                    "PRAGMA table_info(opportunity_document_requirements)"
                )
            }
            if "active" not in requirement_columns:
                connection.execute(
                    "ALTER TABLE opportunity_document_requirements ADD COLUMN active "
                    "INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))"
                )
            opportunity_columns = {
                row["name"] for row in connection.execute("PRAGMA table_info(opportunities)")
            }
            if "description" not in opportunity_columns:
                connection.execute(
                    "ALTER TABLE opportunities ADD COLUMN description TEXT NOT NULL DEFAULT ''"
                )
            opportunity_columns = {
                row["name"] for row in connection.execute("PRAGMA table_info(opportunities)")
            }
            if "status" not in opportunity_columns:
                connection.execute(
                    "ALTER TABLE opportunities ADD COLUMN status TEXT NOT NULL DEFAULT 'OPEN' "
                    "CHECK (status IN ('OPEN', 'CLOSED'))"
                )
            verification_columns = {
                row["name"]: row for row in connection.execute(
                    "PRAGMA table_info(document_verifications)"
                )
            }
            due_date_column = verification_columns.get("due_date")
            if due_date_column is not None and due_date_column["notnull"]:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute("ALTER TABLE document_verifications RENAME TO document_verifications_old")
                connection.execute(
                    """
                    CREATE TABLE document_verifications (
                        proposal_id TEXT PRIMARY KEY REFERENCES proposals(id),
                        status TEXT NOT NULL DEFAULT 'PENDING'
                            CHECK (status IN ('PENDING', 'COMPLETE', 'CHANGES_REQUIRED')),
                        due_date TEXT,
                        notes TEXT NOT NULL DEFAULT '',
                        updated_by TEXT REFERENCES users(id),
                        updated_at TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    "INSERT INTO document_verifications SELECT * FROM document_verifications_old"
                )
                connection.execute("DROP TABLE document_verifications_old")
                connection.commit()
            proposal_table = connection.execute(
                "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'proposals'"
            ).fetchone()
            if proposal_table and "VERIFIED" not in proposal_table["sql"]:
                connection.execute("PRAGMA foreign_keys = OFF")
                connection.execute("BEGIN IMMEDIATE")
                try:
                    connection.execute(
                        """CREATE TABLE proposals_replacement (
                            id TEXT PRIMARY KEY,
                            opportunity_id TEXT NOT NULL REFERENCES opportunities(id),
                            title TEXT,
                            sponsor TEXT,
                            abstract TEXT,
                            requested_amount REAL,
                            deadline TEXT,
                            status TEXT NOT NULL CHECK (status IN ('DRAFT', 'SUBMITTED', 'VERIFIED')),
                            version INTEGER NOT NULL DEFAULT 0 CHECK (version >= 0),
                            submitted_version_id TEXT,
                            created_by TEXT NOT NULL REFERENCES users(id),
                            created_at TEXT NOT NULL,
                            updated_at TEXT NOT NULL,
                            CHECK (
                                (status = 'DRAFT' AND submitted_version_id IS NULL)
                                OR (status IN ('SUBMITTED', 'VERIFIED') AND submitted_version_id IS NOT NULL)
                            ),
                            FOREIGN KEY (id, submitted_version_id)
                                REFERENCES proposal_versions(proposal_id, id)
                        )"""
                    )
                    connection.execute(
                        """INSERT INTO proposals_replacement
                           (id, opportunity_id, title, sponsor, abstract, requested_amount, deadline,
                            status, version, submitted_version_id, created_by, created_at, updated_at)
                           SELECT id, opportunity_id, title, sponsor, abstract, requested_amount, deadline,
                                  status, version, submitted_version_id, created_by, created_at, updated_at
                           FROM proposals"""
                    )
                    connection.execute("DROP TABLE proposals")
                    connection.execute("ALTER TABLE proposals_replacement RENAME TO proposals")
                    connection.execute(
                        """UPDATE proposals SET status = 'VERIFIED'
                           WHERE id IN (SELECT proposal_id FROM document_verifications WHERE status = 'COMPLETE')"""
                    )
                    connection.execute(
                        "CREATE INDEX IF NOT EXISTS idx_proposals_created_by ON proposals(created_by)"
                    )
                    violations = connection.execute("PRAGMA foreign_key_check").fetchall()
                    if violations:
                        raise RuntimeError(f"Proposal status migration would break foreign keys: {violations}")
                    connection.commit()
                except Exception:
                    connection.rollback()
                    raise
                finally:
                    connection.execute("PRAGMA foreign_keys = ON")
        finally:
            connection.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @contextmanager
    def read(self) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            yield connection
        finally:
            connection.close()
