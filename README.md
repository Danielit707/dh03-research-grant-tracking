# DH-03: Research Project and Grant Tracking System

> **Client:** Research and Innovation Office, Horizon University  
> **Initiative:** Digital Horizon Initiative  
> **Course:** Software Design II (Universidad del Norte) — 2026-30  
> **Project Type:** Standalone Software Initiative  
> **Current Phase:** Phase 1 — Engagement & Business Discovery  

---

## 📌 Project Overview

**Horizon University** manages 150–250 research proposals annually funded by internal university programs, government agencies, private companies, international organizations, and nonprofit institutions.

Currently, proposal registration, document management, financial validation, and project tracking are fragmented across spreadsheets, unstructured email chains, shared folders, and disconnected university financial systems. This fragmentation creates critical operational issues:
* **Lack of Visibility:** Principal Investigators (PIs) and coordinators cannot track pending approvals or review stages in real time.
* **Version Control Conflicts:** Multiple document versions circulate concurrently via email, leading to budget errors and outdated approvals.
* **Audit & Security Risks:** Sensitive proposal data is vulnerable to unauthorized access, and completed projects often lack verifiable technical/administrative closure records.

**The DH-03 Research Project and Grant Tracking System** is an independent software solution designed to provide end-to-end visibility, traceable versioning, role-based access control, and complete lifecycle management for research proposals and active funded projects.

---

## 👥 Team Structure & Roles

Following the Studio Handbook guidelines for 3-member consulting teams, responsibilities are combined to ensure full coverage while maintaining collective ownership of design, requirements, and codebase:

| Member | Primary Role | Core Responsibilities |
| :--- | :--- | :--- |
| **Daniel Eduardo Cera Moran** | **Team Coordinator & Process Lead** | Internal organization, commitment tracking, business process modeling (BPMN), stakeholder discovery management, and client alignment. |
| **Member 2** | **Architecture & Design Lead** | Structural system definition, UML/C4 modeling, Architecture Decision Records (ADRs), and technical justification of design trade-offs. |
| **Member 3** | **Quality & Configuration Lead (QA/DevOps)** | Repository hygiene, test strategy execution, quality attribute verification, and continuous integration/delivery setup. |

> *Principle:* Roles divide execution focus, **not knowledge**. All team members participate in programming, design decisions, requirement mapping, and project defense.

---

## 📂 Repository Structure

```text
.
├── README.md                         # Project overview, team roles, status, and navigation
├── docs/                             # Core project artifacts and living documentation
│   ├── team-agreement.md             # Governance, communication rules, and conflict protocols
│   ├── project-charter.md            # Vision, business objectives, problem statement, and scope
│   ├── stakeholders.md               # Stakeholder Register and interest matrix
│   ├── discovery-notes.md            # Key findings and analysis from client consultation
│   ├── clarification-log.md          # Log of questions, client answers, and resolution status
│   ├── assumption-log.md             # Working business and technical assumptions
│   ├── quality-attributes.md         # Non-functional requirements, security, and quality scenarios
│   ├── backlog.md                    # Prioritized User Stories and functional requirements
│   └── processes/                    # Business process models (BPMN)
│       ├── current-state-bpmn.png    # AS-IS process flow (Fragmented email/spreadsheet flow)
│       └── proposed-state-bpmn.png   # TO-BE process flow (Centralized system flow)
├── requirements/                     # Extended functional/non-functional requirements specifications
├── architecture/                     # System architecture views (C4 Model, UML diagrams)
├── adr/                              # Architecture Decision Records (MADR format)
├── src/                              # Source code implementation
├── tests/                            # Test suite (unit, integration, and end-to-end)
└── deployment/                       # Containerization (Docker) and environment setup scripts

🔑 Key StakeholdersStakeholder GroupPrimary Interest & ResponsibilityPrincipal Investigators (PIs)Lead proposals, submit documentation, track review deadlines, and monitor active grant execution.Research-Office CoordinatorsReview submissions, verify document completeness, coordinate institutional reviews, and track deadlines.Research DirectorPortfolio-level oversight, strategic metrics, milestone monitoring, and high-level risk management.Finance RepresentativeValidates proposal budget summaries, verifies permitted expenditure categories, and audits project closure.IT Services & ComplianceEnforces institutional authentication (SSO/OAuth), role-based access control (RBAC), data privacy, and auditability.🚀 Current Project Status & Milestones[x] Phase 1: Project Engagement & Discovery[x] Autonomous repository initialization & structure setup[x] Team Agreement definition (docs/team-agreement.md)[x] RFP analysis & Stakeholder mapping (docs/stakeholders.md)[x] Discovery notes & preliminary process analysis (docs/discovery-notes.md)[x] Initial Clarification Log & Assumption Log creation[x] Product Vision & Scope Charter definition (docs/project-charter.md)[ ] Evaluation 1: Project Foundation and Business Discovery Defense[ ] Phase 2: Architecture & System Design[ ] Phase 3: Core Increment Implementation & Verification[ ] Phase 4: Final Release & System Governance📄 Key Documentation Quick Links📑 Team Agreement📑 Project Charter & Product Scope📑 Stakeholder Register📑 Discovery Notes & Analysis📑 Clarification Log📑 Assumption Log📑 Product Backlog & User Stories⚙️ Execution & Setup Instructions(Instructions will be updated as implementation artifacts are introduced in future phases.)PrerequisitesGit 2.x+Docker & Docker Compose (for local environment setup)Local SetupBash# Clone the repository
git clone [https://github.com/your-firm-name/DH-03-Research-Tracking-System.git](https://github.com/your-firm-name/DH-03-Research-Tracking-System.git)

# Navigate to repository root
cd DH-03-Research-Tracking-System
🛡️ License & Academic ContextThis project is developed as part of the Software Design II (2026-30) studio course at Universidad del Norte, contributing to the Digital Horizon Initiative at Horizon University. All research and financial data used within this system are synthetic.
---

### ¿Qué destaca este README frente al profesor en la Evaluación 1?
1. **Cumplimiento estricto del Handbook:** Incluye las carpetas oficiales recomendadas (`docs/`, `requirements/`, `architecture/`, `adr/`, `src/`, `tests/`).
2. **Definición de Roles de 3 Integrantes:** Detalla cómo combinaron los roles estándar sin fragmentar el conocimiento.
3. **Hipervínculos a la carpeta `docs/`:** Permite al jurado navegar directamente a tus documentos convert
