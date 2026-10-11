# AD-01 — Modular Monolith

- **Status:** Proposed
- **Decision:** Use one deployable application organized into explicit modules.

## Context

Opportunities, proposals, reviews, approvals, projects, documents, audit, and notifications have distinct responsibilities but participate in a closely connected lifecycle. The team needs a demonstrable end-to-end solution within an academic scope. There is no evidence yet of independent scaling, separate service teams, strict deployment isolation, or an existing distributed platform requirement.

## Alternatives considered

1. **Conventional monolith without enforced module boundaries:** simplest deployment, but encourages mixed responsibilities, duplicated rules, and tight coupling.
2. **Modular monolith:** one deployment with defined module ownership and interfaces; separates concerns without introducing network/distributed-system failure modes.
3. **Microservices:** independent deployment and scaling, but adds service communication, partial failure, consistency, security, observability, and operational coordination.

## Decision and rationale

Adopt a modular monolith as the initial deployment model. Organize identity/authorization, opportunities/proposals, funded projects, document management, audit, and notifications as logical modules with explicit application interfaces. This balances separation of responsibilities with implementation and demonstration feasibility. “One deployment” does not permit arbitrary cross-module state mutation; ownership and contracts remain explicit.

## Consequences

- **Benefits:** understandable responsibilities, centralized testable business rules, collaborative implementation, simpler deployment, and a possible later extraction path.
- **Costs:** modules share deployment and may share persistence; a process failure may affect several modules; independent scaling is limited; boundaries need active enforcement.
- **Reconsider if:** evidence shows independent scaling, strict isolation, separately governed release cycles, or an institutional platform mandates distributed services.

## Validation

Review module ownership and dependencies; demonstrate that business operations call module interfaces rather than directly mutating another module's internals. This decision is not yet validated by implementation evidence.
