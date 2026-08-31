# Artifacts Log and Functional Requirements

## Executive Summary

This document contains the functional requirements and user story specifications for the research opportunity, proposal, and project management lifecycle. The requirements are organized across 10 distinct epics, categorized using MoSCoW prioritization (Must / Should).

### Requirements Summary Overview

- **Total Epics:** 10
- **Total User Stories:** 49
- **Must-Have Requirements:** 37 (75.5%)
- **Should-Have Requirements:** 12 (24.5%)

### Priority Breakdown by Epic

| Epic ID & Name | Total Stories | Must | Should |
| :--- | :---: | :---: | :---: |
| Epic 1 — Research Opportunity & Proposal Management | 5 | 4 | 1 |
| Epic 2 — Proposal Documents & Requirements | 5 | 5 | 0 |
| Epic 3 — Review & Approval Workflow | 8 | 6 | 2 |
| Epic 4 — Submission & Sponsor Decision | 5 | 4 | 1 |
| Epic 5 — Project Activation & Monitoring | 6 | 5 | 1 |
| Epic 6 — Project Changes & Traceability | 5 | 4 | 1 |
| Epic 7 — Notifications & Important Dates | 4 | 1 | 3 |
| Epic 8 — Security & Access Control | 3 | 3 | 0 |
| Epic 9 — Reporting & Audit History | 5 | 2 | 3 |
| Epic 10 — Project Closure | 3 | 3 | 0 |

---

## Functional Requirements by Epic

### Epic 1 — Research Opportunity & Proposal Management

| ID | User Story | Priority |
| :--- | :--- | :---: |
| **US-001** | As a Researcher, I want to register a research opportunity so that I can begin the proposal process. | `Must` |
| **US-002** | As a Researcher, I want to create a proposal record from a research opportunity so that proposal information can be tracked centrally. | `Must` |
| **US-003** | As a Researcher, I want to enter and update proposal information before submission so that the proposal reflects the current intended submission. | `Must` |
| **US-004** | As a Research Office Coordinator, I want to view and maintain proposal records so that institutional proposal activity can be tracked. | `Must` |
| **US-005** | As an authorized user, I want to search and filter proposals so that I can find relevant proposal records efficiently. | `Should` |

### Epic 2 — Proposal Documents & Requirements

| ID | User Story | Priority |
| :--- | :--- | :---: |
| **US-006** | As a Researcher, I want to upload proposal documents so that the required technical, administrative, financial, and other supporting information can be managed centrally. | `Must` |
| **US-007** | As a Research Office Coordinator, I want to identify missing required documents so that incomplete proposals can be returned for correction. | `Must` |
| **US-008** | As an authorized user, I want to create a new version of a proposal document so that changes can be tracked without losing previous versions. | `Must` |
| **US-009** | As an authorized user, I want to view previous document versions so that the history of proposal information remains traceable. | `Must` |
| **US-010** | As the system, I want to associate relevant document versions with review and approval decisions so that the information evaluated at each stage can be identified. | `Must` |

### Epic 3 — Review & Approval Workflow

| ID | User Story | Priority |
| :--- | :--- | :---: |
| **US-011** | As a Research Office Coordinator, I want to review proposal completeness so that incomplete submissions can be identified before institutional approval. | `Must` |
| **US-012** | As a Finance Representative, I want to review the financial information of applicable proposals so that budget requirements can be validated. | `Must` |
| **US-013** | As a Department Chair or Dean, I want to review proposals that require academic-unit approval so that institutional resource commitments can be validated. | `Should` |
| **US-014** | As a Compliance or Ethics Representative, I want to review proposals that require compliance or ethics validation so that applicable institutional requirements can be addressed. | `Should` |
| **US-015** | As an authorized approver, I want to approve or reject a review with comments so that the decision and its justification are recorded. | `Must` |
| **US-016** | As the system, I want to determine the required review and approval steps according to proposal characteristics so that different proposal types can follow appropriate workflows. | `Must` |
| **US-017** | As the system, I want to identify pending reviews and approvals so that users know what action is required before the proposal can progress. | `Must` |
| **US-018** | As an authorized reviewer, I want to request additional information or revisions so that incomplete or incorrect proposal information can be corrected. | `Must` |

### Epic 4 — Submission & Sponsor Decision

| ID | User Story | Priority |
| :--- | :--- | :---: |
| **US-019** | As an authorized institutional representative, I want to authorize a proposal for submission so that only proposals that have completed required institutional reviews can proceed. | `Must` |
| **US-020** | As a Research Office Coordinator, I want to record the submission of a proposal to a sponsor so that the proposal lifecycle remains traceable. | `Must` |
| **US-021** | As a Research Office Coordinator, I want to record sponsor requests for clarification or revision so that external feedback can be tracked. | `Should` |
| **US-022** | As a Research Office Coordinator, I want to record the sponsor's final decision so that the proposal outcome is preserved. | `Must` |
| **US-023** | As an authorized user, I want to view the current proposal status and pending actions so that I can understand its position in the lifecycle. | `Must` |

### Epic 5 — Project Activation & Monitoring

| ID | User Story | Priority |
| :--- | :--- | :---: |
| **US-024** | As a Research Office Coordinator, I want to activate a funded research project from an approved proposal so that project execution can begin with the relevant proposal information. | `Must` |
| **US-025** | As a Project Stakeholder, I want to record project milestones so that project progress can be monitored. | `Must` |
| **US-026** | As a Project Stakeholder, I want to record technical and financial deliverables so that required project outputs can be tracked. | `Must` |
| **US-027** | As a Project Stakeholder, I want to track reporting deadlines and other important project dates so that overdue activities can be identified. | `Must` |
| **US-028** | As an authorized user, I want to view the current project status and pending actions so that I can monitor project progress. | `Must` |
| **US-029** | As the system, I want to identify overdue milestones, deliverables, and deadlines so that projects requiring attention can be detected. | `Should` |

### Epic 6 — Project Changes & Traceability

| ID | User Story | Priority |
| :--- | :--- | :---: |
| **US-030** | As an authorized project user, I want to propose changes to project scope, schedule, team, or budget so that approved project information can be updated through a controlled process. | `Must` |
| **US-031** | As an authorized reviewer, I want to review changes that require approval so that significant modifications are properly controlled. | `Must` |
| **US-032** | As the system, I want to preserve the original approved values when a project change is recorded so that the previous project state remains traceable. | `Must` |
| **US-033** | As the system, I want to record the history of approved project changes so that decisions and modifications can be reconstructed. | `Must` |
| **US-034** | As the system, I want to identify when a change may require renewed review or approval so that affected decisions are not silently invalidated. | `Should` |

### Epic 7 — Notifications & Important Dates

| ID | User Story | Priority |
| :--- | :--- | :---: |
| **US-035** | As a Researcher, I want to receive notifications about relevant proposal status changes so that I know when action is required. | `Should` |
| **US-036** | As an Approver, I want to receive notifications about pending reviews and approvals so that required actions are not overlooked. | `Should` |
| **US-037** | As a Project Stakeholder, I want to receive notifications about approaching deadlines and overdue activities so that project commitments can be monitored. | `Should` |
| **US-038** | As an authorized user, I want to view upcoming and overdue important dates so that I can prioritize pending work. | `Must` |

### Epic 8 — Security & Access Control

| ID | User Story | Priority |
| :--- | :--- | :---: |
| **US-039** | As an authorized user, I want to access proposals and projects according to my role and relationship to them so that confidential information is protected. | `Must` |
| **US-040** | As the system, I want to restrict sensitive proposal and project information to authorized users so that confidential institutional information is not unnecessarily exposed. | `Must` |
| **US-041** | As an IT Services representative, I want users to authenticate through an institutional or simulated identity service so that access can be associated with an authenticated user. | `Must` |

### Epic 9 — Reporting & Audit History

| ID | User Story | Priority |
| :--- | :--- | :---: |
| **US-042** | As a Research Office Coordinator, I want to view operational reports about proposals and projects so that I can monitor ongoing institutional activities. | `Should` |
| **US-043** | As Senior Management, I want to view institutional research portfolio information so that I can support strategic decision-making. | `Should` |
| **US-044** | As an authorized user, I want to view the history of important proposal and project activities so that decisions and changes can be traced. | `Must` |
| **US-045** | As the system, I want to record important submissions, reviews, approvals, decisions, changes, and closure activities so that the lifecycle is auditable. | `Must` |
| **US-046** | As an authorized user, I want to search and filter proposals and projects so that relevant operational information can be retrieved efficiently. | `Should` |

### Epic 10 — Project Closure

| ID | User Story | Priority |
| :--- | :--- | :---: |
| **US-047** | As a Research Office Coordinator, I want to verify that required project deliverables and closure records have been provided so that the project can proceed to closure. | `Must` |
| **US-048** | As an authorized user, I want to record the administrative closure of a project so that its lifecycle can be formally completed. | `Must` |
| **US-049** | As the system, I want to preserve the project history after closure so that completed projects remain traceable for institutional purposes. | `Must` |
