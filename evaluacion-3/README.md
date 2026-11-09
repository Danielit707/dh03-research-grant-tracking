# DH-03 — Evaluation 3, Increment 1

This runnable academic increment demonstrates a persisted proposal workflow with a small web interface: a PI browses open funding opportunities, prepares a proposal with the documents required for that specific call, and either saves a draft or sends it to the Research and Innovation Office. A coordinator claims proposals after they reach office review, sets an internal verification deadline, and records the document-completeness outcome.

## Scope and architecture

- **Modular monolith:** one FastAPI application with separate identity, domain validation, proposal service, and persistence modules.
- **Relational persistence:** SQLite schema with foreign keys, constraints, indexes, audited workflow events, immutable proposal snapshots, and transactionally coupled submission/outbox records. A user-confirmed full proposal purge also removes that proposal's audit history. SQLite is chosen for a no-service local setup; PostgreSQL remains the proposed deployment target in AD-04.
- **Identity and authorization:** seeded bearer-token demo adapter resolves stable subjects to database users. Protected proposal operations enforce server-side role and owner relationship checks. Demo credentials are not production authentication.
- **Implemented flow:** 20 synthetic open opportunities have descriptions and differing deadlines. The catalog shows six results per page. A PI prepares proposal information and its attachments together, then either saves a draft or sends a complete proposal to the Research and Innovation Office. Drafts cannot be assigned to a coordinator; only a proposal sent to office review can be claimed. The service rejects closed/expired opportunities, derives sponsor and deadline from the selected opportunity, and blocks sending until all documents required for that specific call are uploaded.
- **Document upload:** technical proposal, administrative documents, and budget are required for every call. Ethics/compliance and academic commitment review are required only for particular opportunities; each call displays its actual required list. The local prototype accepts PDF files up to 10 MB per requirement, checks a safe `.pdf` filename plus PDF header and end marker, calculates SHA-256, and stores generated-key files under a private local directory outside static web assets. Authorized proposal members download files through a permission-checked attachment endpoint. Upload versions are preserved.
- **Coordinator assignment:** coordinators see an unassigned-work queue with proposal summary and opportunity description. They can explicitly claim proposals sent to the office; draft assignment attempts return `409`. Only the assigned coordinator can record completeness verification; the assignment is audited.
- **Corrections and resubmission:** when the coordinator returns a submitted proposal as `CHANGES_REQUIRED`, the same proposal goes back to the PI as a draft. The PI can upload new document versions and send that same record again; prior snapshots and file versions stay available for traceability.
- **Proposal deletion:** a PI can delete their own proposal before document verification is complete, after a confirmation prompt. This is a full purge of that proposal's files, versions, assignment, review, outbox entries, and audit history. Once verified, deletion is blocked.
- **Document follow-up:** an assigned coordinator records `PENDING`, `COMPLETE`, or `CHANGES_REQUIRED` with notes. Completing verification requires every required document, changes the persisted proposal state to `VERIFIED`, and makes it read-only and non-deletable in this increment. Audit events retain the reason and document manifest for each review, plus uploaded document versions. In-app deadline notices appear when a pending verification is due within seven days or overdue.
- **Deadline handling:** the opportunity deadline is the sponsor's submission deadline and is copied to the proposal; a PI cannot set a different date. The coordinator sets a separate internal document-verification deadline for each proposal, no later than the opportunity deadline. Project duration is not given a universal default; it should come from the award terms when project activation is implemented.
- **Visual interface:** open `http://127.0.0.1:8000/` after starting the app. The low-glare research-themed interface uses a wide layout, spacious opportunity results, and a three-stage workflow indicator. Opportunities and proposals have separate views; the catalog shows six opportunities per page with previous/next navigation. Proposal history shows correction reasons and document versions available at each review. Coordinators see a neutral catalog subtitle and no application button.
- **Validation assumptions:** this slice requires a title and abstract; sponsor and submission deadline come from the opportunity. Budget review happens through the proposal's required budget document, not a separate requested-amount field. The synthetic opportunity document requirements are demonstration data, not approved institutional policy.

The implementation and architecture traceability are described in [docs/architecture-and-traceability.md](docs/architecture-and-traceability.md). The current limitations are listed in [evidence/known-limitations.md](evidence/known-limitations.md).

## Prerequisites

- Python 3.11 or newer
- PowerShell on Windows (commands below use the included scripts); equivalent commands work in other shells

If Windows reports that Python was not found, install Python 3.11 or newer and reopen PowerShell. The included scripts accept either `python.exe` or the Windows `py -3` launcher when it has a runtime installed.

No external database or object store is required. Uploaded demo PDFs are kept locally in a private directory beside the SQLite database. Dependencies and versions are listed in `requirements.txt`.

## Install and seed

From the repository root:

```powershell
Set-Location .\evaluacion-3
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.seed
```

The seed command creates `data\dh03.sqlite3` and synthetic opportunity, PI, coordinator, and draft-proposal records. Re-running it preserves proposal and audit records while refreshing the synthetic opportunity catalog and its test document requirements. To use another database file, set `DH03_DB_PATH` before seeding and starting the app:

```powershell
$env:DH03_DB_PATH = ".\data\local.sqlite3"
python -m src.seed
```

## Run and verify the use case

Start the application:

```powershell
.\run.ps1
```

The launcher prints the exact Python module used for submission validation and stops if it detects the old required-amount rule. After startup, `Invoke-RestMethod http://127.0.0.1:8000/health` should return `submission_contract = requested_amount_optional-v2`.

The script idempotently seeds the local database and starts Uvicorn at `http://127.0.0.1:8000`. Interactive API documentation is at `http://127.0.0.1:8000/docs`.

The visual application is at `http://127.0.0.1:8000/`. Seeded proposals are drafts and have no coordinator assignment. To demonstrate the coordinator queue, create a proposal, attach its required files, and send it to office review while using a PI identity; then switch to a coordinator identity to claim it. The catalog includes 20 open opportunities with descriptions, varied deadlines, and opportunity-specific required-document sets.

Synthetic identities (evaluation only):

| User | Bearer token | Scope |
| --- | --- | --- |
| Alice Rivera | `demo-pi-alice` | Own proposals |
| Bob Chen | `demo-pi-bob` | Own proposals |
| Research Office Coordinator | `demo-coordinator` | Can claim proposals sent to office review |
| Mateo Rojas | `demo-coordinator-mateo` | Can claim proposals sent to office review |

New drafts are not assignable. Proposals sent to the Research Office remain unassigned until a coordinator claims them. Seeded PI proposals remain drafts and are excluded from the coordination queue.

Create a draft through the API (the visual application is the recommended end-to-end demonstration):

```powershell
$headers = @{ Authorization = "Bearer demo-pi-alice" }
$body = @{
    opportunity_id = "opp-horizon-2027"
    title = "Community solar storage pilot"
    abstract = "Evaluate a synthetic community-scale energy storage design."
} | ConvertTo-Json

$proposal = Invoke-RestMethod -Method Post `
    -Uri "http://127.0.0.1:8000/proposals" -Headers $headers `
    -ContentType "application/json" -Body $body

Invoke-RestMethod -Uri "http://127.0.0.1:8000/proposals/$($proposal.id)/documents" `
    -Headers $headers
```

Use the visual interface to upload each required PDF shown for the chosen opportunity and then submit. The server returns `422 missing_required_documents` while any required file is missing. In PowerShell, the documents endpoint above returns requirement IDs; upload each PDF as multipart form field `file` to `/proposals/{id}/documents/{requirement_id}`. The seeded Alice draft (`proposal-seed-alice`) can also be used after its required PDFs are uploaded. A second submission returns `409 invalid_state_transition`; another PI's proposal is denied with `403`.

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
- opportunity pagination and descriptions, opportunity-specific required documents, draft assignment denial, explicit coordinator claiming and role scoping;
- required-document submission gate, upload validation, versioning, private storage, safe download headers, and cross-PI access denial.
- coordinator return-to-PI flow, same-proposal resubmission with new document versions, and owner-authorized full proposal purge.

Results and implementation boundaries are maintained in [evidence/](evidence/), including a targeted review against OWASP Top 10:2025.

## Structure

```text
evaluacion-3/
├── README.md
├── docs/
├── src/
│   ├── database.py
│   ├── document_store.py
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

**Implemented:** open opportunity catalog with descriptions and pagination, opportunity-specific required documents, draft creation, draft-to-office submission, coordinator claiming only after submission, correction and same-proposal resubmission, PI-authorized full proposal purge, server-side role/resource checks, versioned local PDF upload/download with size limits and basic validation, required-document gate, optimistic concurrency, immutable submission snapshots/hashes, audited workflow operations, atomic outbox persistence, synthetic seed data, and integration tests.

The current increment also includes a browser interface to create proposals from existing opportunities, a role-filtered proposal list, demo coordinator assignment, document-verification status and notes, audit history display, and in-app deadline notices.

**Simulated or deferred:** institutional SSO/OIDC, PostgreSQL deployment, cloud object storage, configurable review/approval workflow, coordinator reassignment, sponsor exchange, outbox delivery worker/email, funded-project activation and monitoring, project changes/closure, reporting, production deployment/security/operations, and stakeholder-approved lifecycle/completeness policies. Local file checks do not detect malware or prove that a PDF is safe; this prototype does not parse PDFs or run antivirus. Production upload scanning, encryption, retention, backup, and recovery controls remain future work. Production rules for coordinator lead time and project duration are still to be confirmed. Submission does not assert that institutional reviews or approvals have been completed.
