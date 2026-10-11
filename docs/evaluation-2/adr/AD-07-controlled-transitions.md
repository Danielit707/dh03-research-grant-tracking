# AD-07 — Controlled Business State Transitions

- **Status:** Proposed
- **Decision:** Enforce lifecycle changes through explicit business operations rather than unrestricted status updates.

## Context

Progression depends on prior conditions: reviews and approvals precede submission; a favorable award and required information precede project activation; closure depends on required evidence. Direct status edits could bypass those conditions or omit the version/event references that make a transition meaningful.

## Alternatives considered

1. **Allow direct status changes:** simple but cannot ensure prerequisites or side effects.
2. **Centralize transition rules in application operations:** validate permission and preconditions, perform the change, and record its outcome; selected.
3. **Adopt a separate workflow engine:** could suit complex, frequently reconfigured branching/timers, but current evidence does not justify its added component and operations.

## Decision and rationale

Provide explicit business operations for review decisions, submission authorization/recording, sponsor outcomes, activation, project changes, and closure. Each operation validates actor authority, current state, and required evidence; applies the transition atomically where possible; and records audit/outbox events. Reject invalid transitions without partial state changes. Keep configurable institutional rules behind policy boundaries where variability is established, without inventing unconfirmed conditions.

## Consequences and validation

Transition behavior is explicit and testable but requires a state/rule catalog and concurrency controls. PoC-03 checks activation prerequisites; dedicated transition tests must cover all approved lifecycle paths and invalid paths. Final state names, thresholds, and reapproval rules remain open.
