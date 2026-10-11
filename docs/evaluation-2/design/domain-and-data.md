# Domain and Data Contracts

## Core records and invariants

| Concept | Responsibility | Invariant / relationship |
| --- | --- | --- |
| User | Application identity linked to an authentication subject | Stable application ID; provider subject is an identity link, not an authorization grant |
| Opportunity | Funding/research call and its dates/requirements | Visibility and ownership are explicit; opportunity access does not imply proposal access |
| Proposal | Request being prepared, reviewed, submitted, and decided | Remains distinct from a funded project; retains lifecycle and decision history |
| ProposalVersion | Immutable file/evidence revision | Unique version ID, storage reference, uploader/time, size/type, hash, predecessor where applicable |
| Review / Approval | Assigned institutional evaluation and outcome | Actor, assignment, outcome, comments and decision-time evidence are attributable |
| FundedProject | Execution record created through activation | References originating proposal and exact accepted version; operational values may evolve without overwriting origin evidence |
| ProjectChange | Proposed and decided change to scope/schedule/team/budget | Preserve before/after values, reason, actor/time and applicable approval history |
| AuditEvent | Historical fact about a significant business operation | Append-only through application operations; actor/system, time, type, entity, outcome, version/object reference, reason/comment when required |
| NotificationEvent | Durable request for user communication | Created with the triggering business transaction; delivery state and attempts are recorded |

The entity inventory is a design baseline, not an approved schema. Exact fields, cardinalities, retention rules, and required evidence remain subject to stakeholder confirmation.

## Document upload protocol

The relational database and object store do not share a normal atomic transaction. An upload therefore follows a recoverable protocol:

1. Authorize the uploader and create a pending upload/version record with a unique identifier.
2. Store bytes at a non-public object key; never expose a pending object as an available document.
3. Verify object existence and expected integrity (including a content hash); record size/type and storage reference.
4. Finalize the version record as available only after verification.
5. If an operation fails, retain enough state to retry or identify an orphan for controlled cleanup. Cleanup must not delete a version referenced by a submission, decision, project, or audit event.

Access to bytes is mediated by the application or a short-lived, policy-checked storage access mechanism. Object keys alone are not authorization.

## Historical integrity

- A replacement creates a new version; it never overwrites an existing version's content.
- A submission and any review/approval that depends on a file reference the exact version used.
- `FundedProject` references its originating proposal and the accepted proposal version.
- Where a project value changes from an approved baseline, retain the baseline separately from the current operational value.
- Audit events are append-only through normal application functionality. Administrative/infrastructure tamper resistance is not asserted.
- Data retention, legal hold, permitted deletion, and archival tier require explicit policies before they are implemented.

## Persistence recommendation

PostgreSQL is the proposed relational store for structured entities, constraints, and transactionally coupled audit/outbox records. Object storage is proposed for document contents. Neither provider choice is confirmed. Keep storage-specific behavior behind adapters; database transactions cannot by themselves guarantee object-store consistency.
