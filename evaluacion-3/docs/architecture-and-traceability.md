# Evaluation 3 implementation notes

## Implemented slice

The increment implements a focused proposal submission workflow:

1. A PI creates a draft linked to a registered funding opportunity and can update it while it remains a draft.
2. The PI submits the draft using its current optimistic-lock version.
3. The application validates required proposal information and the future deadline.
4. A single relational transaction creates an immutable submission snapshot, changes the proposal to `SUBMITTED`, appends the audit event, and adds a notification outbox event.
5. Authorized proposal members can retrieve the exact submitted snapshot and its SHA-256 hash.

The demo validation policy requires a non-empty title, sponsor, and abstract, a finite positive requested amount, and a deadline after the current date. This is an explicit evaluation assumption, not a confirmed institutional completeness or document policy.

## Architecture decision mapping

| Decision | Increment evidence |
| --- | --- |
| AD-01 Modular monolith | One FastAPI deployment with separated identity, proposal service, domain validation, and SQLite persistence modules. |
| AD-02 Identity and authorization | Demo bearer-token adapter resolves a stable subject to an active database user. PI role and proposal owner relationship are checked server-side; direct access by a different PI is denied with 403. |
| AD-03 Traceability | Submission creates a database-enforced append-only audit event and an immutable proposal snapshot with actor, timestamp, and content hash. |
| AD-04 Relational storage | SQLite tables, foreign keys, checks, indexes, and transaction boundaries implement the evaluation schema. SQLite is the local adapter, not a change to the proposed PostgreSQL target. |
| AD-05 Proposal/project separation | Proposal lifecycle is modeled without a project table; funded-project activation remains deferred. |
| AD-06 Notifications | A submission outbox row commits atomically with the state transition. A delivery worker, retries, and email adapter are deferred. |
| AD-07 Controlled transitions | Only the submission operation can transition `DRAFT` to `SUBMITTED`; completeness and expected-version checks reject invalid or stale commands. |

## Evaluation boundaries and assumptions

- The demonstration identity tokens and seed records are synthetic and are not authentication for production use.
- SQLite is used to make the increment reproducible without a database service. PostgreSQL migration/provider validation remains future work.
- No document bytes are uploaded. Object storage, document-version upload/reconciliation, and required-document policies remain deferred.
- Approval/review workflows, sponsor integrations, funded project activation, project monitoring/change/closure, notifications delivery, reporting, and production deployment controls are deferred.
- The only implemented proposal transition is `DRAFT` → `SUBMITTED`. The submission gate does not claim that institutional reviews or approvals are complete.
- Role catalog, resource relationships, and completeness rules are evaluation-slice assumptions and require stakeholder confirmation before production use.

## Traceability

| Requirement | Implemented behavior | Verification |
| --- | --- | --- |
| US-002 | Create a proposal from an existing opportunity; record PI ownership. | Integration test creates and retrieves a draft. |
| US-003 | Update a draft using an expected version; reject edits after submission. | Incomplete-draft test repairs the record, and guarded update checks state/version. |
| US-019–020 | Record a submission through a guarded command bound to an exact version. | Happy-path integration test verifies version, audit, and outbox references. |
| US-023 | Return current lifecycle status and optimistic-lock version. | API response asserts `SUBMITTED` and incremented version. |
| US-039–041 | Authenticate a demo subject and enforce role plus resource relationship. | Cross-PI direct read and submission receive 403 with no proposal fields. |
| US-044–045 | Persist queryable, append-only audit events for creation and submission. | Integration test checks actor, event type, and version reference. |
| AD-04 / QA-03 | Reject incomplete submission without partial writes. | Validation test checks draft state and absence of version/outbox data. |
| AD-07 | Serialize concurrent submissions and reject stale/invalid transitions. | Concurrency and repeated-submission tests assert one committed event/version. |
