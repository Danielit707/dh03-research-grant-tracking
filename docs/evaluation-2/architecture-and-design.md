# Architecture and Design

## Executive summary

DH-03 supports the research-proposal lifecycle from opportunity registration, proposal preparation, institutional review, and sponsor decision through funded-project activation, monitoring, change control, and closure. Its central architectural concern is preserving the integrity and history of that lifecycle while improving access control, visibility, and timely action.

The proposed baseline is a **modular monolith** with explicit application-module boundaries, a relational store for structured business data, and object storage for document contents. Authentication is delegated to an institutional identity provider when available; authorization combines role permissions with a user's relationship to the specific resource. Document versions and significant business events are both retained. Proposal and funded project are separate entities connected by an explicit activation operation. Lifecycle changes are performed through guarded business operations. Notifications are persisted with business changes using a transactional outbox and delivered asynchronously; deadline reminders are scheduled separately.

These are architectural recommendations, not claims about deployed technology or completed implementation. PostgreSQL and OIDC are candidates, not confirmed institutional choices. The architecture avoids asserting a cloud provider, availability target, retention period, exact authorization policy, or production identity integration without evidence.

## Architectural priorities and rationale

1. **Protect confidential information:** authenticate users independently from application authorization; check both operation permission and resource relationship on every protected server request.
2. **Preserve evidence:** keep immutable document versions and an application-level append-only history of significant actions, decisions, actors, and timestamps.
3. **Maintain lifecycle integrity:** prevent direct status mutation from bypassing completeness, review, approval, submission, funding, and activation conditions.
4. **Keep preparation distinct from execution:** create a project only through activation and retain an explicit link to its originating proposal and accepted version.
5. **Reduce manual monitoring:** derive notifications from committed business events, and evaluate future dates using a scheduled process.
6. **Stay proportionate to the academic scope:** separate responsibilities without requiring distributed deployment, service discovery, or independent operations for every module.
7. **Integrate rather than replace institutional systems:** use boundaries/adapters for identity, email, and simulated sponsor integrations.

The decisions use four tests: identify the problem, compare plausible alternatives, connect the selected option to a requirement or quality driver, and record its costs and conditions for reconsideration.

## Proposed system shape

The application is one deployable unit organized into identity and authorization, opportunities and proposals, funded projects, document management, audit, and notifications modules. Modules expose application operations rather than reaching into one another's internal data structures. A background worker handles outbox events and scheduled reminders. PostgreSQL is proposed for relational records and transactional coordination; object storage contains file bytes. External identity, email, and sponsor systems are outside the application boundary.

See the [context view](views/context-view.md), [container view](views/container-view.md), [domain model](views/domain-model-view.md), and the detailed [domain/data](design/domain-and-data.md), [runtime](design/lifecycle-and-runtime.md), [interface](design/interfaces.md), and [security](design/security.md) contracts.

## Decision summary

| ADR | Proposed decision | Main driver |
| --- | --- | --- |
| [AD-01](adr/AD-01-modular-monolith.md) | Deploy as a modular monolith initially | Clear responsibility boundaries at feasible operational cost |
| [AD-02](adr/AD-02-identity-authorization.md) | Separate authentication from combined role- and relationship-based authorization | Restrict access to relevant resources |
| [AD-03](adr/AD-03-traceability-audit.md) | Retain document versions and append-only application audit events | Reconstruct what changed, who acted, and what was decided |
| [AD-04](adr/AD-04-relational-object-storage.md) | Relational metadata and business data; object storage for file bytes | Integrity and queryability without coupling file lifecycle to database |
| [AD-05](adr/AD-05-proposal-project-separation.md) | Separate Proposal and FundedProject, joined through controlled activation | Preserve preparation history while operations evolve |
| [AD-06](adr/AD-06-event-notifications.md) | Transactional outbox, asynchronous event delivery, scheduled reminders | Avoid coupling committed work to email availability |
| [AD-07](adr/AD-07-controlled-transitions.md) | Enforce state transitions through explicit business operations | Prevent invalid lifecycle progression |

## Quality and validation

The [quality scenarios](quality-scenarios.md) turn the draft's security, traceability, integrity, maintainability, resilience, performance, and evolvability drivers into six-part scenarios. Quantitative targets are candidate acceptance criteria for review; they have not been measured or approved.

The [validation plan](validation/test-plan.md) specifies the four priority proofs of concept from the source proposal. Each is **STATUS: NOT EXECUTED**. Current known questions and risks are recorded in [project status](project-status.md), and the evidence register is in [validation findings](validation/findings.md).

## Implementation dependency order

1. Confirm domain entities, relationships, and lifecycle states.
2. Choose the identity integration/demonstration approach and define initial authorization policies.
3. Implement relational records and document metadata/version contracts.
4. Implement object storage, integrity verification, and recovery for partial uploads.
5. Implement audit records and guarded lifecycle transitions.
6. Implement proposal-to-project activation.
7. Implement outbox persistence and asynchronous notification processing.
8. Implement scheduled reminders.
9. Execute and record the four priority PoCs.
10. Review evidence, open risks, and resulting architectural adjustments.

This order addresses access control, data integrity, and history before broader automation. It is a proposed implementation sequence, not a report of work completed.
