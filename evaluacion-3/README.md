# DH-03 — Evaluation 3, Increment 1

This runnable academic increment demonstrates a complete, persisted proposal-submission use case: a PI creates a draft, the server validates it, and one guarded state transition records an immutable submitted snapshot, audit event, and notification outbox event.

## Scope and architecture

- **Modular monolith:** one FastAPI application with separate identity, domain validation, proposal service, and persistence modules.
- **Relational persistence:** SQLite schema with foreign keys, constraints, indexes, append-only audit events, immutable proposal snapshots, and transactionally coupled submission/outbox records. SQLite is chosen for a no-service local setup; PostgreSQL remains the proposed deployment target in AD-04.
- **Identity and authorization:** seeded bearer-token demo adapter resolves stable subjects to database users. Protected proposal operations enforce server-side role and owner relationship checks. Demo credentials are not production authentication.
- **Implemented flow:** PI creates and edits a draft for an existing opportunity; PI submits the draft with its expected version; the service checks required fields and a future deadline; successful submission transitions `DRAFT` → `SUBMITTED`. A SHA-256 hash identifies the exact submitted snapshot.
- **Validation assumptions:** this slice requires title, sponsor, abstract, a finite positive requested amount, and a future deadline. Institutional requirements, review/approval gates, and document requirements are unresolved and are not represented as approved policy.

The implementation and architecture traceability are described in [docs/architecture-and-traceability.md](docs/architecture-and-traceability.md). The current limitations are listed in [evidence/known-limitations.md](evidence/known-limitations.md).

The timed narration, clean demo database setup, live PowerShell commands, recording checklist, and ZIP packaging steps are in [video-script.md](video-script.md).

## Prerequisites

- Python 3.11 or newer
- PowerShell on Windows (commands below use the included scripts); equivalent commands work in other shells

No external database or object store is required. Dependencies and tested versions are listed in `requirements.txt`.

## Install and seed

From the repository root:

```powershell
Set-Location .\evaluacion-3
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.seed
```

The seed command creates `data\dh03.sqlite3` and synthetic opportunity, PI, coordinator, and draft-proposal records. Re-running it is safe and does not reset or overwrite existing state. To use another database file, set `DH03_DB_PATH` before seeding and starting the app:

```powershell
$env:DH03_DB_PATH = ".\data\local.sqlite3"
python -m src.seed
```

## Run and verify the use case

Start the application:

```powershell
.\run.ps1
```

The script idempotently seeds the local database and starts Uvicorn at `http://127.0.0.1:8000`. Interactive API documentation is at `http://127.0.0.1:8000/docs`.

Synthetic identities (evaluation only):

| User | Bearer token | Scope |
| --- | --- | --- |
| Alice Rivera | `demo-pi-alice` | Own proposals |
| Bob Chen | `demo-pi-bob` | Own proposals |
| Research Office Coordinator | `demo-coordinator` | Coordinator role; no proposal membership is assigned by the demo seed |

Create a draft and submit it in PowerShell:

```powershell
$headers = @{ Authorization = "Bearer demo-pi-alice" }
$body = @{
    opportunity_id = "opp-horizon-2027"
    title = "Community solar storage pilot"
    sponsor = "Horizon Research Fund"
    abstract = "Evaluate a synthetic community-scale energy storage design."
    requested_amount = 42500
    deadline = (Get-Date).Date.AddDays(60).ToString("yyyy-MM-dd")
} | ConvertTo-Json

$proposal = Invoke-RestMethod -Method Post `
    -Uri "http://127.0.0.1:8000/proposals" -Headers $headers `
    -ContentType "application/json" -Body $body

$submission = Invoke-RestMethod -Method Post `
    -Uri "http://127.0.0.1:8000/proposals/$($proposal.id)/submit" `
    -Headers $headers -ContentType "application/json" `
    -Body (@{ expected_version = $proposal.version } | ConvertTo-Json)

$submission | Format-List id, status, version, submitted_version_id
Invoke-RestMethod -Uri "http://127.0.0.1:8000/proposals/$($proposal.id)/audit" `
    -Headers $headers
```

Verify that the response has `status = SUBMITTED`, a higher version, and a `submitted_version_id`. The audit endpoint returns the actor, event time, and exact snapshot reference. Fetch that immutable snapshot using:

```powershell
Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/proposals/$($proposal.id)/versions/$($submission.submitted_version_id)" `
    -Headers $headers
```

The seeded Alice draft (`proposal-seed-alice`) is also ready to submit using `expected_version = 0`. A second submission with the current version returns `409 invalid_state_transition`; Bob's proposal is not accessible using Alice's token and returns `403`.

## Run automated tests

```powershell
.\test.ps1
```

Or run directly with `python -m pytest -q`. Tests use isolated temporary SQLite databases and verify:

- successful submission, persisted snapshot/hash, audit actor/reference, and transactional outbox record;
- incomplete submission rejection with no partial state change;
- direct cross-PI read and submission denial;
- duplicate state transition rejection;
- concurrent submission behavior: one success, one stale-version conflict, and only one version/audit/outbox record.

Results and implementation boundaries are maintained in [evidence/](evidence/).

## Structure

```text
evaluacion-3/
├── README.md
├── video-script.md
├── docs/
├── src/
│   ├── database.py
│   ├── domain.py
│   ├── identity.py
│   ├── main.py
│   ├── schema.sql
│   ├── seed.py
│   └── service.py
├── tests/
├── evidence/
├── requirements.txt
├── run.ps1
├── test.ps1
└── video-link-or-video.txt
```

## Implemented vs. deferred

**Implemented:** proposal draft creation and editing, opportunity link, demo identity resolution, role/resource checks for proposal owner operations, submission completeness checks, optimistic concurrency, `DRAFT` → `SUBMITTED` transition, immutable submission snapshot/hash, append-only audit, atomic outbox persistence, synthetic seed data, and integration tests.

**Simulated or deferred to Evaluation 4:** institutional SSO/OIDC, PostgreSQL deployment, document bytes and object storage, configurable review/approval workflow, coordinator assignment operations, sponsor exchange, outbox delivery worker/email, funded-project activation and monitoring, project changes/closure, reporting, production deployment/security/operations, and stakeholder-approved lifecycle/completeness policies. The submission gate does not assert that institutional reviews or approvals have been completed.
