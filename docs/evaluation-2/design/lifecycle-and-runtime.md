# Lifecycle and Runtime

## Proposal lifecycle (conceptual)

The detailed status vocabulary and applicable approvals remain open. The following is a conceptual sequence; each step must be a guarded business operation, not a freely editable status field:

1. Register opportunity and proposal.
2. Prepare proposal metadata and immutable document versions.
3. Evaluate completeness; return for correction when required evidence is missing.
4. Assign and record applicable reviews/approvals. Applicability depends on sponsor, project type, budget, research activity, or other confirmed policy.
5. Authorize submission only after required steps are satisfied; record submission against the exact version submitted.
6. Record sponsor request/response and final funding outcome, preserving history and related versions.
7. If funded and activation prerequisites are met, invoke the project activation operation.

Changing information after review may invalidate affected decisions; exact invalidation/re-review conditions require confirmation. A new version must not silently change an earlier submission.

## Project lifecycle (conceptual)

Activation creates a distinct FundedProject only after a favorable funding decision, a selected accepted proposal version, and required funding/activation data are present. The operation links project to proposal/opportunity, records actor/time, preserves applicable baseline values, and writes audit and notification events.

During execution, authorized users maintain milestones, deliverables, important dates, status, and proposed changes. Changes requiring approval remain pending until the applicable decision is recorded. Closure is permitted only after required deliverables, dates, and technical/financial/administrative evidence are confirmed; the system retains the closed history. Exact closure evidence and thresholds remain to be confirmed.

## Transition operation contract

For every transition, the owning module operation must:

1. Authenticate the caller and authorize the operation against role and resource relationship.
2. Verify current state and required preconditions/evidence.
3. Apply state and associated record changes atomically within the relational transaction where possible.
4. Record actor/system identity, timestamp, outcome, reason/comment when required, and relevant version references.
5. Add outbox events in the same transaction for notifications that follow the committed change.
6. Return an explicit success or validation/conflict result; do not report success for a partial transition.

Concurrent requests must not both commit incompatible transitions. Use database constraints/optimistic concurrency or equivalent control and test the chosen mechanism.

## Runtime notification flow

Business transaction + outbox event → worker claims pending event → resolve recipients from approved relationship rules → send minimal notification through email adapter → record attempt/result and retry eligible failures. Delivery is not exactly once; use deduplication/idempotency and surface exhausted failures for operations.

A scheduled process independently finds approaching/overdue dates and enqueues reminder events using the same outbox/delivery path. Interval, timezone, escalation, retries, and operational alert thresholds are not yet specified.
