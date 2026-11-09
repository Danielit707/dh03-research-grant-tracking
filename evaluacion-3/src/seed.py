from datetime import date, timedelta, datetime, timezone
import argparse
import os
from pathlib import Path

from .database import Database
from .service import ProposalService


SYNTHETIC_OPPORTUNITIES = [
    ("opp-horizon-2027", "Horizon University Seed Research Fund", "Horizon Research Fund", 365, "OPEN"),
    ("opp-gov-catalyst", "Government Research Catalyst", "National Research Council", 24, "OPEN"),
    ("opp-renewable-pilot", "Renewable Energy Pilot Grants", "Green Futures Foundation", 38, "OPEN"),
    ("opp-public-health", "Public Health Innovation Award", "Health Research Network", 52, "OPEN"),
    ("opp-marine-science", "Marine Science Partnership", "Blue Ocean Institute", 66, "OPEN"),
    ("opp-digital-learning", "Digital Learning Research Fund", "Horizon Education Trust", 79, "OPEN"),
    ("opp-water-resilience", "Urban Water Resilience Challenge", "Andes Water Alliance", 91, "OPEN"),
    ("opp-ai-social-good", "AI for Social Good Seed Grants", "Civic Technology Fund", 105, "OPEN"),
    ("opp-food-systems", "Sustainable Food Systems Grant", "AgroResearch Colombia", 118, "OPEN"),
    ("opp-indigenous-knowledge", "Community and Indigenous Knowledge Fund", "Cultural Heritage Foundation", 132, "OPEN"),
    ("opp-women-stem", "Women in STEM Research Program", "Equality in Science Fund", 146, "OPEN"),
    ("opp-climate-adaptation", "Climate Adaptation Research Challenge", "Climate Action Partnership", 160, "OPEN"),
    ("opp-biomedical", "Biomedical Discovery Award", "Horizon Health Foundation", 174, "OPEN"),
    ("opp-arts-heritage", "Community Arts and Heritage Fund", "Arts and Culture Council", 188, "OPEN"),
    ("opp-materials", "Advanced Materials Research Grant", "Materials Innovation Lab", 202, "OPEN"),
    ("opp-international-exchange", "International Research Exchange", "Global Academic Exchange", 216, "OPEN"),
    ("opp-smart-cities", "Smart Cities Innovation Fund", "Urban Futures Consortium", 230, "OPEN"),
    ("opp-rural-connectivity", "Rural Connectivity Research Award", "Digital Inclusion Foundation", 244, "OPEN"),
    ("opp-equipment", "Shared Research Equipment Microgrant", "Horizon Research Office", 258, "OPEN"),
    ("opp-early-career", "Early Career Investigator Award", "New Scholars Foundation", 272, "OPEN"),
    ("opp-closed-archive", "Archived Pilot Opportunity", "Demo Sponsor", -30, "CLOSED"),
    ("opp-closed-deadline", "Expired Demo Call", "Demo Sponsor", -2, "OPEN"),
]

STANDARD_DOCUMENTS = [
    ("technical", "Propuesta técnica", True, "Descripción técnica de la investigación propuesta."),
    ("administrative", "Documentos administrativos", True, "Documentación administrativa institucional de la propuesta."),
    ("financial", "Presupuesto", True, "Presupuesto detallado de la propuesta."),
    ("ethics", "Ética y compliance", False, "Adjuntar únicamente cuando la propuesta lo requiera."),
    ("academic", "Revisión de compromisos académicos", False, "Adjuntar únicamente cuando la unidad académica deba revisar compromisos de recursos."),
]

OPPORTUNITY_DESCRIPTIONS = {
    "opp-horizon-2027": "Financia estudios piloto interdisciplinarios que generen evidencia inicial para futuras convocatorias externas.",
    "opp-gov-catalyst": "Apoya investigación aplicada con impacto nacional y resultados útiles para políticas y servicios públicos.",
    "opp-renewable-pilot": "Busca proyectos piloto de energía renovable, almacenamiento y acceso energético comunitario.",
    "opp-public-health": "Financia soluciones de investigación que mejoren resultados de salud y reduzcan brechas de atención.",
    "opp-marine-science": "Promueve investigación colaborativa sobre ecosistemas marinos, conservación y uso sostenible de recursos.",
    "opp-digital-learning": "Apoya estudios que evalúen prácticas, herramientas y resultados de aprendizaje digital.",
    "opp-water-resilience": "Busca propuestas para fortalecer la gestión del agua y la resiliencia hídrica en zonas urbanas.",
    "opp-ai-social-good": "Financia usos responsables de inteligencia artificial para atender retos sociales verificables.",
    "opp-food-systems": "Apoya investigación para mejorar sostenibilidad, seguridad alimentaria y sistemas de producción.",
    "opp-indigenous-knowledge": "Promueve investigación colaborativa y respetuosa con comunidades y conocimientos indígenas.",
    "opp-women-stem": "Impulsa proyectos liderados por investigadoras y el desarrollo de equipos diversos en ciencia y tecnología.",
    "opp-climate-adaptation": "Busca evidencia y soluciones para adaptación climática en comunidades y sistemas vulnerables.",
    "opp-biomedical": "Financia investigación biomédica traslacional con beneficios potenciales para prevención o tratamiento.",
    "opp-arts-heritage": "Apoya investigación y prácticas comunitarias para preservar y compartir patrimonio cultural.",
    "opp-materials": "Promueve nuevos materiales y procesos con potencial de uso científico, industrial o ambiental.",
    "opp-international-exchange": "Financia colaboraciones internacionales, movilidad académica y desarrollo de investigación conjunta.",
    "opp-smart-cities": "Busca soluciones basadas en evidencia para movilidad, servicios y sostenibilidad urbana.",
    "opp-rural-connectivity": "Apoya investigación para ampliar conectividad digital y servicios en comunidades rurales.",
    "opp-equipment": "Apoya proyectos colaborativos que amplíen el acceso y uso compartido de infraestructura de investigación.",
    "opp-early-career": "Impulsa proyectos independientes de investigadores en etapas iniciales de su carrera académica.",
    "opp-closed-archive": "Convocatoria archivada para pruebas de visibilidad y estado.",
    "opp-closed-deadline": "Convocatoria de prueba con fecha de cierre vencida.",
}

CONDITIONAL_REQUIRED = {
    "opp-gov-catalyst": {"ethics"},
    "opp-public-health": {"ethics"},
    "opp-indigenous-knowledge": {"ethics"},
    "opp-biomedical": {"ethics"},
    "opp-water-resilience": {"academic"},
    "opp-equipment": {"academic"},
}


def seed(database: Database) -> None:
    database.initialize()
    now = datetime.now(timezone.utc).isoformat(timespec="microseconds")
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
                    "Camila Torres (demo coordinator)",
                    "RESEARCH_OFFICE_COORDINATOR",
                ),
                (
                    "user-coordinator-2",
                    "hu-demo-coordinator-2",
                    "Mateo Rojas (demo coordinator)",
                    "RESEARCH_OFFICE_COORDINATOR",
                ),
            ],
        )
        for opportunity_id, title, sponsor, days_open, status in SYNTHETIC_OPPORTUNITIES:
            opportunity_deadline = (date.today() + timedelta(days=days_open)).isoformat()
            connection.execute(
                """
                INSERT INTO opportunities (id, title, description, sponsor, deadline, status)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    description = excluded.description,
                    sponsor = excluded.sponsor,
                    status = excluded.status
                """,
                (opportunity_id, title, OPPORTUNITY_DESCRIPTIONS[opportunity_id],
                 sponsor, opportunity_deadline, status),
            )
            connection.execute(
                "UPDATE opportunity_document_requirements SET active = 0 WHERE opportunity_id = ?",
                (opportunity_id,),
            )
            required_conditional = CONDITIONAL_REQUIRED.get(opportunity_id, set())
            for key, name, required, description in STANDARD_DOCUMENTS:
                required_for_call = required or key in required_conditional
                existing = connection.execute(
                    "SELECT id FROM opportunity_document_requirements WHERE opportunity_id = ? AND name = ?",
                    (opportunity_id, name),
                ).fetchone()
                if existing:
                    connection.execute(
                        """UPDATE opportunity_document_requirements
                           SET description = ?, required = ?, allowed_extension = '.pdf',
                               max_size_bytes = ?, active = 1 WHERE id = ?""",
                        (description, int(required_for_call), 10 * 1024 * 1024, existing["id"]),
                    )
                else:
                    connection.execute(
                        """
                        INSERT INTO opportunity_document_requirements
                            (id, opportunity_id, name, description, required, allowed_extension,
                             max_size_bytes, active)
                        VALUES (?, ?, ?, ?, ?, '.pdf', ?, 1)
                        """,
                        (f"{opportunity_id}-doc-{key}", opportunity_id, name,
                         description, int(required_for_call), 10 * 1024 * 1024),
                    )
        seed_deadline = connection.execute(
            "SELECT deadline FROM opportunities WHERE id = 'opp-horizon-2027'"
        ).fetchone()["deadline"]
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
                    seed_deadline,
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
        draft_assignments = connection.execute(
            """SELECT m.proposal_id, m.user_id FROM proposal_memberships m
               JOIN proposals p ON p.id = m.proposal_id
               WHERE m.relationship = 'ASSIGNED_COORDINATOR' AND p.status = 'DRAFT'"""
        ).fetchall()
        for assignment in draft_assignments:
            connection.execute(
                "DELETE FROM proposal_memberships WHERE proposal_id = ? AND user_id = ?",
                (assignment["proposal_id"], assignment["user_id"]),
            )
            connection.execute(
                "DELETE FROM document_verifications WHERE proposal_id = ?",
                (assignment["proposal_id"],),
            )
            unassignment_logged = connection.execute(
                """SELECT 1 FROM audit_events WHERE entity_id = ?
                   AND event_type = 'proposal.coordinator_unassigned'""",
                (assignment["proposal_id"],),
            ).fetchone()
            if unassignment_logged is None:
                ProposalService._audit(
                    connection,
                    assignment["user_id"],
                    "proposal.coordinator_unassigned",
                    assignment["proposal_id"],
                    {"reason": "drafts_cannot_be_assigned"},
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
