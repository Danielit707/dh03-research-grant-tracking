# Project Clarification Log

## Executive Summary

This document tracks key domain, technical, and operational questions requiring clarification for the Research Opportunity, Proposal, and Project Management System. Each item captures the stakeholder involved, the current client understanding, system impact, and resolution status.

### Clarification Status Overview

- **Total Clarification Items:** 12
- **Open Items:** 10 (83.3%)
- **Closed Items:** 2 (16.7%)

--- 

## Clarification Log

| ID | Question | Stakeholder | Client Response / Current Understanding | Impact Area | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **CL-001** | Who creates and maintains the official proposal record? | Research-office Coordinator | The responsible party for creating and maintaining the official proposal record has not yet been confirmed. | Proposal ownership and workflow | `Open` |
| **CL-002** | What information defines a research opportunity and what information must be registered? | Research-office Coordinator | A research opportunity represents a potential funding or research call. The minimum information required for registration remains under review. | Domain model and scope | `Open` |
| **CL-003** | Which documents are required for a proposal, and do requirements vary by proposal characteristics? | Research-office Coordinator | Required documents may vary depending on proposal type, sponsor, research activity, or other characteristics. The exact rules remain under review. | Completeness review and document management | `Open` |
| **CL-004** | Which document version is authoritative during a review or approval? | Research-office Coordinator | Document versions must be preserved and the version used for each relevant decision must remain identifiable. The exact authority rule remains under review. | Version control and auditability | `Open` |
| **CL-005** | Do approval requirements vary according to sponsor, project type, budget, or research activity? | Research Director | Yes. Approval requirements may vary according to relevant proposal or project characteristics. | Configurable approval workflow | `Closed` |
| **CL-006** | What happens to previous approvals when information changes after a review? | Research-office Coordinator | A significant change may require affected reviews or approvals to be repeated. The exact conditions remain under review. | Change workflow and lifecycle | `Open` |
| **CL-007** | Which changes require renewed approval? | Research Director | Significant changes to scope, schedule, team, or budget are candidates for renewed approval. Exact thresholds remain under review. | Business rules and authorization | `Open` |
| **CL-008** | What is the distinction between investigators and collaborators, and what responsibilities does each have? | Research Director | Both may participate in research activities, but their responsibilities and access rights have not yet been fully defined. | Roles, permissions, and domain model | `Open` |
| **CL-009** | Can external collaborators access proposal or project information? | Research Director / IT Services | External collaborators are part of the identified stakeholder context, but the information and lifecycle stages they may access remain under review. | Security and confidentiality | `Open` |
| **CL-010** | What information is considered sensitive, and who may access it? | IT Services | Proposal and project documents should be treated as controlled institutional information. Access should depend on the user's role and relationship to the proposal or project. Specific access rules for project-stage information remain under review. | Security and authorization | `Open` |
| **CL-011** | What information does Institutional / Senior Management require from institutional reports? | Institutional / Senior Management | Reports should support research portfolio monitoring and institutional decision-making. Exact indicators and aggregation level remain under review. | Reporting scope and access control | `Open` |
| **CL-012** | What evidence and approval are required before a funded project can be closed? | Research-office Coordinator | A project can be considered complete when all planned deliverables have been completed, all applicable delivery deadlines have been fulfilled, and the required technical, financial, administrative, and other applicable records have been provided. | Closure workflow and auditability | `Closed` |