# Evaluation 3 implementation notes

## Implemented slice

The increment demonstrates the following persisted flow:

1. Users browse a vertically scrolling, paginated catalog of synthetic open opportunities with descriptions. Six results are returned per page; closed and expired opportunities are excluded.
2. The PI opens one postulation form that combines proposal information and documents. It offers two visible outcomes: save a draft (documents may be incomplete) or send the completed package to the Research and Innovation Office. The server still persists the draft before processing attachments, but the user does not need to perform a separate draft-creation step.
3. The sponsor and deadline are derived server-side from the selected opportunity. Technical proposal, administrative documents, and budget are required in every call. Ethics/compliance and academic commitment review are required only for calls whose terms include them. The catalog and postulation form show only the requirements for that call.
4. Uploaded files are size limited, checked for a safe PDF filename and basic PDF markers, hashed, staged, and stored under a generated key in a local private directory outside the static web root. Each replacement creates another immutable version.
5. The office-send command validates proposal fields and all required document links. If any required file is absent, it returns `422 missing_required_documents` without changing lifecycle state.
6. A single relational transaction creates an immutable submission snapshot including latest document versions and hashes, changes the proposal from `DRAFT` to `SUBMITTED` (meaning submitted to office review in this increment), appends the audit event, and adds a notification outbox event.
7. Drafts cannot be assigned. Only proposals sent to office review appear in the coordinator's unassigned queue; the API rejects attempts to claim drafts. The queue provides the opportunity description and proposal abstract. Coordinators explicitly claim an eligible proposal, then record document completeness and set an internal deadline no later than the sponsor deadline.
8. If the coordinator selects `CHANGES_REQUIRED`, the same proposal returns to the PI as a draft. The PI can replace document versions and resubmit the same proposal ID; older submission snapshots and file versions remain traceable.
9. When all required documents are accepted, one transaction changes the proposal's persisted status from `SUBMITTED` to `VERIFIED` and stores the `COMPLETE` verification event with its document manifest. This is a terminal state for this increment: proposal edits, document uploads, further review changes, and deletion are rejected.
10. Before verification is complete, the owning PI can explicitly hard-delete a proposal after confirmation. This removes its proposal process state, document bytes and metadata, versions, assignment, review, outbox entries, and audit events.

The browser UI exposes the open opportunity catalog, proposal creation from a selected call, a three-stage progress indicator, proposal state, required-document upload/download, verification history, assignment queue, and deadline notices. Notices are in-app only; no email is sent.

## Deadline and document assumptions

Opportunity submission deadlines come from the opportunity record. The coordinator fixes the internal verification deadline per proposal. The synthetic opportunities and dates are demonstration data only. Financial review, academic-unit review, conditional ethics/compliance handling, institutional authorization, and final sponsor submission remain later workflow stages to model; the existing `SUBMITTED` state represents a PI handoff to the office, not sponsor submission. Project duration will come from award terms when project activation is implemented; no universal duration is assumed.

Uploads accept `.pdf` filenames up to 10 MiB. The application checks filename controls/path components, file size, a `%PDF-` prefix, and `%%EOF` near the end; it calculates SHA-256 and returns files only as authorized downloads with attachment disposition and `nosniff`. These checks do not establish that a file is a valid or safe PDF. The prototype does not parse or execute PDF content and does not scan for malware. Local files are outside static assets but are not encrypted, backed up, or reconciled against database records.

## Architecture decision mapping

| Decision | Increment evidence |
| --- | --- |
| AD-01 Modular monolith | One FastAPI deployment with separated identity, proposal service, document storage adapter, domain validation, and SQLite persistence modules. |
| AD-02 Identity and authorization | Demo bearer-token adapter resolves a stable subject to a database user. Role and proposal relationship checks are enforced server-side for metadata, upload, and download. |
| AD-03 Traceability | Submission creates an append-only audit event and immutable proposal snapshot. Document uploads retain immutable versions, SHA-256 and uploader/time metadata; invalid file attempts by an authorized draft owner are audited. |
| AD-04 Relational/file storage | SQLite persists business state and metadata. A local private filesystem adapter stores bytes for this demo; cloud object storage remains a deployment decision. |
| AD-05 Proposal/project separation | Proposal lifecycle is modeled without a project table; funded-project activation remains deferred. |
| AD-06 Notifications | Submission outbox row commits atomically with state transition. A delivery worker, retries, and email adapter are deferred. |
| AD-07 Controlled transitions | Submission sends a complete `DRAFT` to office review; coordinator `CHANGES_REQUIRED` returns that same record to `DRAFT`; resubmission creates a newer immutable version; complete document verification moves it to terminal `VERIFIED`. Expected-version, state, and completeness checks reject invalid commands. |

## Evaluation boundaries and assumptions

- Demo bearer tokens and the identity selector are synthetic evaluation tools, not production authentication.
- Proposal deletion is an explicit owner-authorized purge exception to ordinary append-only history: it removes the proposal's audit history and does not retain a deletion tombstone.
- SQLite and local file storage make the increment reproducible without external services; PostgreSQL and object storage remain deployment targets to evaluate.
- Upload checks are defense in depth for a local demo, not malware detection or full PDF validation. Antivirus scanning, encryption, retention, backup, reconciliation, and production deployment controls remain future work.
- Opportunity names, deadlines, sponsors, document requirements, user identities, and assignment workflow are synthetic data for demonstration.
- Implemented proposal transitions are `DRAFT` → `SUBMITTED` (office review) and, when the assigned coordinator requests corrections, `SUBMITTED` → `DRAFT` → `SUBMITTED` on the same proposal; accepted documents transition `SUBMITTED` → terminal `VERIFIED`. Financial/academic approval, sponsor decisions, funded-project activation, project monitoring/change/closure, delivery of email notifications, and reporting are deferred.
- Submission does not assert that institutional reviews or approvals have completed.

## Traceability

| Requirement | Implemented behavior | Verification |
| --- | --- | --- |
| US-001–003 | Browse open opportunities and create a proposal from a selected opportunity; store PI ownership. | Opportunity catalog and create-flow integration tests. |
| US-006–009 | Upload opportunity-specific required PDF documents as versioned records with hashes. | Upload validation, versioning and storage tests. |
| US-007, US-011 | Assigned coordinator records document-verification status, notes and deadline. | Role/membership checks and audit history. |
| US-019–020 | Submit only a complete draft bound to its expected version. | Submission tests verify state, snapshot, audit and outbox; missing-file test verifies no transition. |
| US-023, US-038 | Display status, verification deadline and upcoming/overdue notices. | Notices derive from persisted verification dates and membership. |
| US-039–041 | Enforce role and relationship checks on proposal/document access. | Cross-PI access and coordinator assignment tests. |
| US-044–045 | Persist append-only audit events for creation, assignment, upload, rejection and submission. | Integration tests inspect event actor/type/outcome. |
| AD-04 / QA-03 | Reject incomplete submission without partial writes. | Required-document and field validation tests. |
| AD-07 | Serialize concurrent submissions and reject stale/invalid transitions. | Concurrency test asserts one committed event/version. |
