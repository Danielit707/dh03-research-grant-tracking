# Project Assumptions and Risk Analysis

## Executive Summary

This document outlines the operational, technical, and architectural assumptions identified for the Research Opportunity, Proposal, and Project Management System at Horizon University. Each assumption details its underlying rationale, risk impact if proven incorrect, validation methodology, designated owner, and tracking status.

### Key Metrics & Risk Profile

- **Total Assumptions Tracked:** 15
- **High Risk Assumptions:** 12 (80.0%)
- **Medium Risk Assumptions:** 3 (20.0%)
- **Status:** 100% Active

--- 

## Project Assumptions Log

| ID | Assumption | Rationale | Risk Level | Validation Method | Owner | Status |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| **ASM-001** | The Research Office will maintain the official proposal record after a researcher identifies a funding opportunity. | The Research Office coordinates institutional review and needs a consistent record of the proposal lifecycle. | `High` | Confirm proposal ownership and registration responsibility with the Research Office. | Business analyst | `Active` |
| **ASM-002** | A proposal may contain multiple technical, administrative, financial, and compliance documents. | Research proposals may require different categories of supporting information. | `High` | Review representative proposal cases with Research Office and relevant units. | Business analyst | `Active` |
| **ASM-003** | Proposal documents will be versioned and previous versions will remain traceable. | Different versions may currently circulate across documents, email, and spreadsheets. | `High` | Confirm document versioning and retention practices with Research Office. | Architect | `Active` |
| **ASM-004** | One document version will be identified as authoritative for the current proposal state. | Reviews and approvals need to reference the information that was actually evaluated. | `High` | Validate authoritative-version rules with Research Office. | Business analyst | `Active` |
| **ASM-005** | Approval requirements will vary according to proposal characteristics such as sponsor, project type, budget, or research activity. | The Discovery Analysis identifies variable approval requirements. | `High` | Validate approval scenarios with Research Office, Finance, academic units, and Compliance. | Business analyst | `Active` |
| **ASM-006** | A proposal may require multiple institutional reviews before it can be submitted to the sponsor. | The current process includes completeness, financial, academic, and potentially compliance reviews. | `High` | Map representative proposal workflows with stakeholders. | Product owner | `Active` |
| **ASM-007** | Changes to information after an approval may require the affected approval to be repeated. | Changes to approved information may invalidate decisions made during earlier review stages. | `High` | Validate change and reapproval rules with relevant review owners. | Business analyst | `Active` |
| **ASM-008** | Principal Investigators, research team members, and collaborators will have different responsibilities and access rights. | The Product Vision identifies these as distinct participant categories. | `High` | Validate responsibilities and access expectations with Research Office. | Business analyst | `Active` |
| **ASM-009** | Some research projects may involve collaborators or institutions external to Horizon University. | The Discovery Analysis identifies multi-institution projects as a relevant domain case. | `Medium` | Review representative multi-institution research scenarios. | Business analyst | `Active` |
| **ASM-010** | Funded proposals will transition into active research projects after sponsor approval and required institutional validation. | The current lifecycle distinguishes proposals from funded projects. | `High` | Validate the proposal-to-project transition with Research Office and Research Director. | Product owner | `Active` |
| **ASM-011** | Funded projects may contain multiple milestones, technical deliverables, financial deliverables, and reporting deadlines. | The Discovery Analysis explicitly identifies multiple deliverables and dates. | `Medium` | Review representative funded-project monitoring requirements. | Business analyst | `Active` |
| **ASM-012** | Approved project changes will preserve original values and record the history of the change. | The product requires traceability of changes to scope, schedule, team, and budget. | `High` | Validate change-record requirements with Research Office and project stakeholders. | Architect | `Active` |
| **ASM-013** | Approval and access rules will change over time as institutional and sponsor policies evolve. | The domain includes multiple sponsors and variable institutional requirements. | `High` | Validate expected policy-change frequency with Research Director and IT Services. | Architect | `Active` |
| **ASM-014** | Institutional and external integrations will be simulated rather than connected to production systems. | The Product Scope explicitly includes simulated integrations and excludes replacement of institutional systems. | `Medium` | Confirm integration constraints with IT Services. | Technical lead | `Active` |
| **ASM-015** | Real confidential research data will not be stored in the first implementation. | Real confidential research data is explicitly outside the product scope. | `High` | Confirm data-handling constraints with IT Services and privacy stakeholders. | QA and privacy owner | `Active` |
