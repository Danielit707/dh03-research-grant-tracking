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
├── adr/                              # Architecture Decision Records (MADR format)
├── src/                              # Application source code
├── tests/                            # Automated test suite
└── deployment/                       # Environment configuration and containerization scripts

Aquí tienes una versión de **`README.md`** actualizada, organizada y ajustada estrictamente a la estructura de tu repositorio y al contenido de tus artefactos para la **Evaluación 1**.

```markdown
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
├── adr/                              # Architecture Decision Records (MADR format)
├── src/                              # Application source code
├── tests/                            # Automated test suite
└── deployment/                       # Environment configuration and containerization scripts

```

---

## 🔑 Key Stakeholders & Main Users

* **Principal Investigators (PIs):** Submit proposals, manage team members, track review statuses, and monitor active grant execution.


* **Research-Office Coordinators:** Perform completeness checks, manage review workflows, and track deadlines.


* **Research Director:** Institutional portfolio oversight, risk tracking, and high-level reporting.


* **Finance Representatives:** Validate proposal budgets, verify permitted expenditures, and audit financial closure.


* **IT & Compliance:** SSO authentication, role-based access control (RBAC), data confidentiality, and auditability.



---

## 📄 Living Documentation & Quick Links

* 📑 [Team Agreement](https://www.google.com/search?q=docs/team-agreement.md)

* 📑 [Project Charter & Product Scope](https://www.google.com/search?q=docs/project-charter.md)

* 📑 [Stakeholder Register](https://www.google.com/search?q=docs/stakeholders.md)

* 📑 [Discovery Notes & AS-IS Analysis](https://www.google.com/search?q=docs/discovery-notes.md)

* 📑 [Clarification Log](https://www.google.com/search?q=docs/clarification-log.md)

* 📑 [Assumption Log](https://www.google.com/search?q=docs/assumption-log.md)

* 📑 [Product Backlog](https://www.google.com/search?q=docs/backlog.md)


---

## 🚦 Current Status & Project Milestones

* [x] **Phase 1: Project Engagement & Business Discovery**

* [x] Independent repository initialization and directory setup


* [x] Team Agreement definition (`docs/team-agreement.md`)


* [x] RFP analysis and Stakeholder mapping (`docs/stakeholders.md`)


* [x] Discovery notes & AS-IS process analysis (`docs/discovery-notes.md`)


* [x] Clarification Log & Assumption Log setup (`docs/clarification-log.md`, `docs/assumption-log.md`)


* [x] Product Vision and Scope specification (`docs/project-charter.md`)


* [ ] **Evaluation 1: Project Foundation and Business Discovery Defense**



* [ ] **Phase 2: Architecture & System Design**

* [ ] **Phase 3: Core Increment Implementation & Verification**

* [ ] **Phase 4: Final Release & System Defense**


---

## ⚠️ Known Scope Boundaries & Limitations

As defined in the project charter, the DH-03 system explicitly excludes:

* Replacing the complete university financial or ERP system.


* Processing actual monetary payments or calculating payroll.


* Direct automated submission to external sponsor portals.


* Automated scientific peer review or plagiarism detection.



---

## ⚙️ Execution Instructions

*(Technical execution details will be updated upon implementation in Phase 2 & 3)*.

### Prerequisites

* Git 2.x+


* Docker & Docker Compose



```bash
# Clone the repository
git clone [https://github.com/your-firm/DH-03-Research-Tracking-System.git](https://github.com/your-firm/DH-03-Research-Tracking-System.git)

# Navigate to project directory
cd DH-03-Research-Tracking-System

```

```

```
