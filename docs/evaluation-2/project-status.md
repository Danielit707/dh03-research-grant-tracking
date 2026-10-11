# Project Status: Open Items, Risks, and Backlog

## Current architecture status

The contents of this Evaluation 2 package describe a **proposed architectural baseline** derived from Nicolás's draft and existing project requirements. The package does not establish that a design has been implemented, an integration configured, or a PoC passed. All four priority PoCs are **NOT EXECUTED**.

## Open decisions and evidence

| ID | Open item | Risk if unresolved | Evidence / owner to confirm |
| --- | --- | --- | --- |
| OPEN-01 | Institutional identity provider, supported protocol, test access, and stable subject identifier | Demo authentication may be mistaken for production; access policy may not fit actual claims | IT Services: confirm provider and OIDC compatibility; define a labeled fallback |
| OPEN-02 | Final role catalog, resource relationships, and permissions | Unauthorized access or blocked legitimate work | Research Office, Research Director, IT: approve a role/resource/action matrix |
| OPEN-03 | External collaborator identity and permitted information/lifecycle stages | Confidential proposal data may be exposed or valid collaboration blocked | Research Director and IT: decide whether external access is in scope and define boundary |
| OPEN-04 | Storage provider, access controls, versioning, backup, file limits, and retrieval behavior | Upload integrity, availability, cost, or recovery failures | IT: evaluate providers and demonstrate upload, integrity verification, and recovery |
| OPEN-05 | Document/audit retention, archival tiers, deletion, legal holds, and retrieval time | Loss of evidence, unnecessary retention, or unplanned storage/retrieval cost | Research Office, IT, privacy owner: approve retention and archival policy; do not assume AWS tiers |
| OPEN-06 | Approval applicability, transition names, post-review change invalidation, and thresholds | Inconsistent workflow or invalid approvals | Research Office, Finance, academic/compliance approvers: validate representative cases |
| OPEN-07 | Award evidence, activation fields, copying/reference rules, and project baseline | Project may be activated from the wrong proposal version or incomplete evidence | Research Office and Research Director: approve activation checklist and version rule |
| OPEN-08 | Notification recipients, triggers, reminder intervals, timezone, escalation, retry ceiling | Missed or excessive/confidential notifications | Product owner/Research Office: approve event-recipient and reminder matrix |
| OPEN-09 | Scale, response-time, availability, backup, recovery, and disaster-recovery objectives | Performance/resilience claims cannot be designed or tested credibly | Product owner and IT: provide workload and service targets |
| OPEN-10 | Closure evidence and post-closure access/retention | Premature closure or incomplete institutional record | Research Office: approve closure checklist and history access policy |
| OPEN-11 | Sponsor API scope and simulated-versus-real integration boundary | Accidental commitment to unsupported real integration | Product owner and IT: document interface and confirm simulation-only scope |
| OPEN-12 | Candidate quality-scenario thresholds and benchmark conditions | Proposed metrics may not reflect course or stakeholder acceptance | QA lead and stakeholders: agree benchmark data/load and targets before testing |

## Risks

| Risk | Impact | Proposed response |
| --- | --- | --- |
| Missing policy detail is mistaken for a settled architecture | Rework and incorrect security/workflow behavior | Label assumptions and require sign-off for OPEN-02, OPEN-06, OPEN-07 |
| Partial failure between database and object storage | Missing objects, orphan objects, or false available-version metadata | Pending/finalized upload states, integrity check, reconciliation and recovery test |
| Email delivery is duplicated or delayed | Users may miss or receive repeated action messages | Durable outbox, attempt tracking, deduplication, operational visibility; do not claim exactly-once delivery |
| Modules erode into a tightly coupled monolith | Changes become difficult to isolate/test | Define module ownership, interfaces, and dependency review |
| Candidate metrics/provider choices treated as approved targets | Overcommitment or incorrect infrastructure choice | Keep candidate values marked provisional until stakeholder evidence is recorded |

## Near-term backlog

1. Resolve OPEN-01–OPEN-03 and draft an approved authorization matrix.
2. Confirm the lifecycle and activation conditions, including which version is accepted.
3. Define document, audit, and notification retention/recipient policies.
4. Select development/demo adapters and document the simulation boundary.
5. Execute PoC-01 through PoC-04 and attach reproducible evidence.
6. Confirm quality-scenario measures and benchmark environment.
7. Review module boundaries, data contracts, and quality-scenario results; update ADR status based on evidence.
