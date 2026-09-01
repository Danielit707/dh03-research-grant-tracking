# DH-03: Research Project and Grant Tracking System

> **Client:** Research and Innovation Office, Horizon University  
> **Course:** Software Design II (Universidad del Norte) — 2026-30  
> **Project Type:** Independent Consulting Initiative (Digital Horizon)  
> **Current Phase:** Phase 1 — Engagement & Business Discovery  

---

## 📌 Project Purpose & System Overview

**Horizon University** processes 150–250 research proposals annually funded by internal programs, government grants, private industry, and international sponsors.

Currently, the proposal and grant lifecycle suffers from severe operational fragmentation:
* **Information Scatter:** Proposals, budgets, and documentation are managed across disconnected spreadsheets, email chains, and shared folders.
* **Review Ambiguity:** Review workflows lack real-time visibility, preventing researchers and coordinators from identifying pending approvals or bottlenecks.
* **Traceability & Confidentiality Risks:** Changes to budgets, scope, or team members are not consistently audited, and sensitive pre-award data lacks explicit role-based protection.

**The DH-03 System** provides a centralized, secure, and traceable software solution to manage the end-to-end lifecycle of research proposals and active funded projects—from initial opportunity registration to final administrative closure.

---

## 👥 Team Structure & Roles (3-Member Model)

In alignment with the Studio Handbook guidelines for 3-member teams, roles and responsibilities are combined to ensure complete coverage:

| Team Member | Role | Core Responsibilities |
| :--- | :--- | :--- |
| **Daniel Eduardo Cera Moran** | **Team Coordinator & Process Lead** | Internal team organization, meeting coordination, business process modeling (BPMN), stakeholder engagement, and discovery management. |
| **Member 2** | **Architecture & Design Lead** | System structural definition, UML/C4 modeling, component boundaries, and Architecture Decision Records (ADRs). |
| **Member 3** | **Quality & Configuration Lead (QA/DevOps)** | Repository governance, artifact consistency, testing strategies, Definition of Done, and CI/CD pipelines. |

> *Note:* Responsibilities divide execution focus, **not knowledge**. All team members program, participate in design, understand requirements, and defend the solution.

---

## 📂 Repository Structure

The repository is structured according to the standard course guidelines:

```text
.
├── README.md                         # Project overview, team roles, status, and navigation
├── docs/                             # Core project artifacts and living documentation
│   ├── team-agreement.md             # Governance, communication rules, and conflict protocols
│   ├── project-charter.md            # Vision, business objectives, problem statement, and scope
│   ├── stakeholders.md               # Stakeholder Register and interest/impact matrix
│   ├── discovery-notes.md            # Key findings and AS-IS process analysis
│   ├── clarification-log.md          # Log of questions, client answers, and status
│   ├── assumption-log.md             # Working business and technical assumptions
│   ├── quality-attributes.md         # Non-functional requirements and quality scenarios
│   ├── backlog.md                    # Prioritized User Stories and functional requirements
│   └── processes/                    # Business process models (BPMN)
│       ├── current-state-bpmn.png    # AS-IS process flow
│       └── proposed-state-bpmn.png   # TO-BE process flow
├── requirements/                     # Detailed requirements specifications
├── architecture/                     # Architecture views (C4 Model, UML)
├── adr/                              # Architecture Decision Records (MADR format)[cite: 3, 4]
├── src/                              # Application source code[cite: 3]
├── tests/                            # Automated test suite[cite: 3]
└── deployment/                       # Environment configuration and containerization scripts[cite: 3]
