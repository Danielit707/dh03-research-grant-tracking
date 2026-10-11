# Requirements and Architectural Drivers

## Scope and source

This review uses the existing [functional requirements](../functional-requirements.md), [project charter](../project-charter.md), [clarification log](../clarification-log.md), and the architecture proposal [`../Propuesta Entregable 2.pdf`](../Propuesta%20Entregable%202.pdf). The existing user-story identifiers (US-001–US-049) remain the requirement identifiers; this document groups them by capability rather than duplicating the full story text.

The product manages research opportunities, proposals and supporting documents, reviews and institutional approvals, submission and sponsor outcomes, funded-project execution, changes, notifications, reporting, and closure. The system is intended to support simulated integrations in the academic scope. It does not replace university finance, identity, document-management, ethics, or sponsor systems; submit proposals to real sponsor portals; process payments; or store real confidential research data.

## Functional requirements

| ID range | Capability / required behavior | Architectural implication |
| --- | --- | --- |
| US-001–005 | Register opportunities; create and maintain proposal records; search/filter | Opportunity and Proposal modules; ownership and visibility rules |
| US-006–010 | Upload, version, retrieve, and associate documents with the decisions that used them | Document metadata/version model; object storage; immutable references |
| US-011–018 | Check completeness; conduct applicable reviews; approve, reject, request revisions; identify pending actions | Guarded review workflow; configurable applicability rules; role and assignment checks |
| US-019–023 | Authorize and record submission; record sponsor feedback/outcome; show status and next actions | Submission event references an exact proposal version; controlled transitions |
| US-024–029 | Activate funded work; maintain milestones, deliverables, dates, status, and overdue indicators | Separate FundedProject; activation operation; date-based reminders |
| US-030–034 | Propose/review changes; preserve original values and decisions; identify changes that may need reapproval | Change request and approval history; explicit old/new values; configurable impact rules |
| US-035–038 | Notify relevant researchers/approvers/project stakeholders; show upcoming and overdue dates | Outbox-backed asynchronous notification module and scheduled reminder process |
| US-039–041 | Restrict records by role and resource relationship; authenticate through institutional or simulated identity service | Authentication adapter; server-side authorization policy |
| US-042–046 | Provide operational/portfolio reporting and searchable audit history | Authorized read models/queries; audit records; reporting access policy |
| US-047–049 | Verify closure evidence; record formal closure; preserve history after closure | Guarded closure operation; retained records and evidence references |

The exact details of user permissions, approval rules, document requirements, transition labels, and closure evidence are not fully specified. See [project status](project-status.md) and the originating [clarification log](../clarification-log.md).

## Quality drivers

| Attribute | Required outcome | Proposed architectural response | Cost or unresolved measure |
| --- | --- | --- | --- |
| Security | Only users authorized for a particular opportunity, proposal, document, or project can access it | Authentication separated from authorization; role plus resource relationship checks on server | Exact permissions, external collaborator policy, and security controls need confirmation |
| Traceability | Reconstruct submissions, approvals, changes, and project origin | Immutable document versions, references to decision-time versions, append-only application audit events | Retention, deletion, and any stronger tamper-evidence requirements are open |
| Data integrity | Keep relationships consistent and prevent invalid lifecycle progression | Relational constraints, transactions, explicit state-transition operations | Business rule catalog and concurrency behavior need verification |
| Maintainability | Keep domain responsibilities understandable and testable | Modular monolith with explicit module interfaces and ownership | Boundaries require team discipline; coupling is not yet measured |
| Operational resilience | A temporary email outage must not undo a successful business operation or lose its notification event | Transactional outbox, asynchronous worker, retry and duplicate handling | Delivery latency, retry policy, and operational monitoring are undecided |
| Performance | Efficiently query structured records and store/retrieve large files | Relational database for structured data; object storage for bytes; metadata references | Workload, file limits, latency, throughput, and archive retrieval targets are unknown |
| Evolvability | Integrate with institutional services and adapt as rules change | Adapter boundaries; modular responsibilities; avoid provider-specific commitments | Identity provider, sponsor integration scope, and workflow configurability remain open |

## Constraints and assumptions

- Academic delivery and end-to-end demonstration favor a low-operational-complexity initial deployment.
- Institutional identity is preferred if available. OIDC is a candidate protocol; neither its availability nor a provider is confirmed.
- PostgreSQL is a proposed relational implementation, not an approved institutional standard.
- Object storage is proposed for file contents. Provider, retention, archival tier, and retrieval service level remain undecided.
- Sponsor and institutional integrations are simulated unless scope changes through explicit approval.
- Real confidential research data is outside the first implementation scope.
- The current source does not establish deployment scale, uptime, disaster recovery, or regulatory retention targets.

## Architecture evidence still required

Stakeholder approval of authorization policy and workflow conditions, identity and storage-provider selection, data retention/deletion rules, operating-scale evidence, and results from all four PoCs are required before treating the proposals as validated. See the [traceability matrix](traceability.md) for requirement-to-architecture links.
