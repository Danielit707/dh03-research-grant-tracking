from datetime import date, timedelta, datetime, timezone
import argparse
import os
from pathlib import Path

from .database import Database
from .service import ProposalService


def seed(database: Database) -> None:
    database.initialize()
    now = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    deadline = (date.today() + timedelta(days=365)).isoformat()
    with database.transaction() as connection:
        connection.executemany(
            """
            INSERT OR IGNORE INTO users (id, identity_subject, display_name, role)
            VALUES (?, ?, ?, ?)
            """,
            [
                ("user-alice", "hu-demo-alice", "Alice Rivera (demo PI)", "PI"),
                ("user-bob", "hu-demo-bob", "Bob Chen (demo PI)", "PI"),
                (
                    "user-coordinator",
                    "hu-demo-coordinator",
                    "Research Office Coordinator (demo)",
                    "RESEARCH_OFFICE_COORDINATOR",
                ),
            ],
        )
        connection.execute(
            """
            INSERT OR IGNORE INTO opportunities (id, title, sponsor, deadline)
            VALUES (?, ?, ?, ?)
            """,
            ("opp-horizon-2027", "Horizon University Seed Research Fund", "Horizon Research Fund", deadline),
        )
        for proposal_id, user_id, title in (
            ("proposal-seed-alice", "user-alice", "Synthetic renewable energy pilot"),
            ("proposal-seed-bob", "user-bob", "Synthetic water quality study"),
        ):
            connection.execute(
                """
                INSERT OR IGNORE INTO proposals (
                    id, opportunity_id, title, sponsor, abstract, requested_amount,
                    deadline, status, version, created_by, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'DRAFT', 0, ?, ?, ?)
                """,
                (
                    proposal_id,
                    "opp-horizon-2027",
                    title,
                    "Horizon Research Fund",
                    f"Synthetic demonstration proposal owned by {user_id}.",
                    25000.0,
                    deadline,
                    user_id,
                    now,
                    now,
                ),
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO proposal_memberships (proposal_id, user_id, relationship)
                VALUES (?, ?, 'OWNER_PI')
                """,
                (proposal_id, user_id),
            )
            existing_audit = connection.execute(
                "SELECT 1 FROM audit_events WHERE entity_id = ? AND event_type = 'proposal.created'",
                (proposal_id,),
            ).fetchone()
            if existing_audit is None:
                ProposalService._audit(
                    connection,
                    user_id,
                    "proposal.created",
                    proposal_id,
                    {"status": "DRAFT", "seeded": True},
                    now,
                )


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the local database and synthetic demo records.")
    parser.add_argument(
        "--db",
        default=os.environ.get(
            "DH03_DB_PATH",
            str(Path(__file__).resolve().parents[1] / "data" / "dh03.sqlite3"),
        ),
    )
    args = parser.parse_args()
    database = Database(args.db)
    seed(database)
    with database.read() as connection:
        proposal_count = connection.execute("SELECT COUNT(*) FROM proposals").fetchone()[0]
    print(f"Seed complete: {proposal_count} synthetic proposals in {args.db}")


if __name__ == "__main__":
    main()
