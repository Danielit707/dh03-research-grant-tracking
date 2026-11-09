# Evidence and known limitations

## Verification

- `python -m pytest -q`: **PASS** — 16 integration tests passed, covering opportunity pagination/descriptions, call-specific document rules, draft assignment denial, coordinator claiming, corrections/resubmission, full PI-authorized purge, upload limits/validation, document gate, private storage, access control, audit trail, and submission concurrency. One non-failing Starlette/httpx deprecation warning was emitted.
- `python -m compileall -q src tests`: **PASS**.
- `git diff --check`: **PASS** — only Git line-ending notices for newly written Markdown files.
- OWASP Top 10:2025 targeted mapping and upload-specific notes are recorded in [owasp-top-10-review.md](owasp-top-10-review.md).

## Known limitations

- This is a local academic demonstration; it has no production identity provider, secrets management, TLS configuration, rate limiting, or operational monitoring.
- The browser UI uses selectable synthetic bearer identities. This is not production authentication and must not be exposed to an untrusted network.
- SQLite and local filesystem storage provide persistence for this increment only. PostgreSQL/object storage deployment, file/database reconciliation, encryption at rest, backups, recovery, retention, and lifecycle controls are not implemented.
- Uploads are restricted to `.pdf` filenames and 10 MiB, with basic header/end-marker checks and SHA-256 hashing. The app does not parse PDFs, inspect embedded content, or detect malware. A file passing these checks must not be described as safe.
- Local documents are private in the sense that they are outside the static web root and served through an authorization-checked attachment endpoint; host filesystem users can still access them.
- Verification deadline notices are in-app only. The outbox has no delivery worker or email adapter.
- Opportunity catalog and requirements, users, coordinators, and deadlines are synthetic test data. Real organizational requirements and assignment/reassignment rules need stakeholder confirmation.
- A draft cannot be assigned; only a proposal sent to the office review queue is assignable. The implemented flow is `DRAFT` → office `SUBMITTED`, then coordinator `CHANGES_REQUIRED` returns the same proposal to `DRAFT` for resubmission. Financial review, academic-unit review, institutional authorization, sponsor submission/outcomes, funded-project activation, monitoring/change/closure, and reporting remain outside this increment.
- PI deletion is a full purge with no tombstone: it also removes the proposal's audit events. Keep this behavior only if complete deletion is the intended retention policy.
- Project duration should come from award terms; there is no universal duration rule.
