# AD-05 — Separate Proposal and Funded Project

- **Status:** Proposed
- **Decision:** Model Proposal and FundedProject as distinct entities linked by an explicit, guarded activation process.

## Context

A proposal represents a funding request and contains preparation, reviews, approvals, submitted versions, and sponsor decisions. A funded project represents execution, milestones, deliverables, approved changes, and closure. Operational project changes must not rewrite what was approved or submitted.

## Alternatives considered

1. **One entity with a changing status:** mixes different lifecycles and risks overwriting approved proposal information.
2. **Create an unrelated project:** separates operations but loses proof of its proposal origin and accepted version.
3. **Separate entities with permanent origin/version references:** selected; preserves distinction and traceability.

## Decision and rationale

Activation is an explicit business operation. It confirms a favorable sponsor decision, identifies the exact proposal version that forms the basis, validates required activation information, creates the project, links it to the originating proposal/opportunity, records actor and time, and creates audit/notification events. Missing prerequisites leave the proposal/project unactivated.

Keep proposal reviews, decision, and document history in the proposal domain. The project references the originating proposal and accepted version; copy only data required for independent project operations. Preserve original approved values explicitly when operational values later change. Do not infer accepted version from “latest uploaded.”

## Consequences and validation

This preserves both lifecycle histories and permits independent operational change, at the cost of activation rules, cross-entity references, and explicit copy/reference policy. PoC-03 must prove the project is distinct and retains the exact proposal/version origin. Sponsor award evidence and complete activation conditions remain open.
