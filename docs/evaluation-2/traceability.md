# Requirements-to-Architecture Traceability

Requirement identifiers refer to the existing [functional requirements](../functional-requirements.md). An ADR or contract indicates an architectural response, not proof of implementation. PoCs remain **NOT EXECUTED**; evidence status is in [validation findings](validation/findings.md).

| Requirement(s) | Capability | Architectural response / design location | Validation evidence |
| --- | --- | --- | --- |
| US-001–005 | Opportunity registration, proposal creation/maintenance, search | AD-01, AD-02; [domain/data](design/domain-and-data.md), [interfaces](design/interfaces.md) | Contract tests; authorization policy open |
| US-006–010 | Document upload, required-document completeness, versions, retrieval, decision/version association | AD-03, AD-04; [domain/data](design/domain-and-data.md), [lifecycle/runtime](design/lifecycle-and-runtime.md) | PoC-02; **NOT EXECUTED** |
| US-011–018 | Completeness, finance/academic/compliance review, outcome/comment, variable approvals, pending actions, revision requests | AD-02, AD-07; [interfaces](design/interfaces.md), [security](design/security.md) | Transition and assignment tests; workflow applicability open |
| US-019–023 | Submission authorization/record, sponsor feedback/outcome, visible status/actions | AD-03, AD-07; [lifecycle/runtime](design/lifecycle-and-runtime.md), [domain/data](design/domain-and-data.md) | Verify guards and exact submitted-version reference; unexecuted |
| US-024 | Funded project activation from awarded proposal | AD-05, AD-07; [lifecycle/runtime](design/lifecycle-and-runtime.md) | PoC-03; **NOT EXECUTED** |
| US-025–029 | Milestones, deliverables, important dates, project status, overdue items | AD-05, AD-06, AD-07; [domain/data](design/domain-and-data.md), [lifecycle/runtime](design/lifecycle-and-runtime.md) | Date/reminder tests; thresholds open |
| US-030–034 | Controlled project changes, review, preservation of original values, history, re-review | AD-03, AD-05, AD-07; [domain/data](design/domain-and-data.md), [interfaces](design/interfaces.md) | Before/after, approval and invalidation tests; rules open |
| US-035–038 | Status/review/deadline notifications and date views | AD-06; [lifecycle/runtime](design/lifecycle-and-runtime.md), [interfaces](design/interfaces.md) | PoC-04; **NOT EXECUTED** |
| US-039–041 | Resource-scoped access and authentication service | AD-02; [security](design/security.md) | PoC-01; **NOT EXECUTED** |
| US-042–043, US-046 | Operational/portfolio reports and search | AD-01, AD-02; [interfaces](design/interfaces.md), [security](design/security.md) | Query, authorization and metric definitions open |
| US-044–045 | Authorized history and recording significant lifecycle events | AD-03; [domain/data](design/domain-and-data.md), [security](design/security.md) | Verify event coverage, actor/time/version references; unexecuted |
| US-047–049 | Closure readiness, formal closure, retained closed history | AD-03, AD-07; [lifecycle/runtime](design/lifecycle-and-runtime.md), [domain/data](design/domain-and-data.md) | Closure guard/history tests; evidence policy open |

## Quality driver traceability

| Quality driver | Related requirements | ADR(s) | Scenario |
| --- | --- | --- | --- |
| Security | US-039–041 | AD-02 | [QA-01](quality-scenarios.md#qa-01--security-reject-access-to-another-pis-proposal-ad-02) |
| Traceability | US-008–010, US-020, US-032–033, US-044–045, US-049 | AD-03, AD-05 | [QA-02](quality-scenarios.md#qa-02--traceability-retrieve-the-exact-submitted-version-ad-03-ad-04) |
| Data integrity | US-016, US-019, US-024, US-031, US-047–048 | AD-04, AD-05, AD-07 | [QA-03](quality-scenarios.md#qa-03--integrity-reject-activation-without-prerequisites-ad-05-ad-07) |
| Maintainability | Cross-cutting | AD-01 | [QA-04](quality-scenarios.md#qa-04--maintainability-preserve-module-boundaries-ad-01) |
| Operational resilience | US-035–038 | AD-06 | [QA-05](quality-scenarios.md#qa-05--resilience-email-outage-does-not-lose-committed-notification-ad-06) |
| Performance | US-005, US-046; document requirements | AD-04 | [QA-06](quality-scenarios.md#qa-06--performance-structured-lookup-and-document-handling-ad-04) |
| Evolvability | US-041 and simulated integration scope | AD-01, AD-02 | [QA-07](quality-scenarios.md#qa-07--evolvability-substitute-identity-and-sponsor-adapters-ad-01-ad-02) |

Detailed role rules, retention policy, lifecycle conditions, provider choices, and measurable service targets have unresolved dependencies; see [project status](project-status.md).
