# AD-06 — Event-Driven Notifications

- **Status:** Proposed
- **Decision:** Persist notification events transactionally with business changes, deliver asynchronously, and use a separate scheduled process to create deadline reminders.

## Context

Users should not have to monitor the system continuously for review assignments, approvals, correction requests, funding decisions, or approaching/overdue dates. Some notifications follow an operation; reminders may be due even when no business record changes.

## Alternatives considered

1. **Manual communication:** leaves timeliness to individual behavior.
2. **Send email synchronously inside each business operation:** couples business success to email availability and duplicates notification logic.
3. **Transactional outbox plus worker:** decouples delivery and supports recovery; selected. Scheduled date evaluation generates reminder events into the same pipeline.

## Decision and rationale

Commit the business change and its outbox event in the same relational transaction. A background worker claims pending events, attempts delivery through an email adapter, records attempts/outcomes, and retries eligible failures. Delivery is not assumed to be exactly once; use idempotency/deduplication keys and handle ambiguous outcomes. A scheduled process finds approaching/overdue dates and creates reminder events without bypassing the common delivery pipeline.

Determine recipients from the affected entity and approved notification rules. Notifications do not grant access. Recipients must authenticate and pass authorization before opening linked content. Limit email content to what is necessary and do not attach confidential documents by default.

## Consequences and validation

Business operations can succeed despite a temporary email outage, but the system needs a worker, retry/duplicate policy, delivery state, recipient rules, and operational monitoring. PoC-04 simulates failure and recovery. Exact recipients, timing, escalation, and delivery targets remain open.
