# Container View

```mermaid
flowchart LR
    ACTORS[PI / Reviewers / Admins / Team Members]
    IDP[Institutional Identity Provider<br/>or demo adapter]
    EMAIL[Email Gateway]
    SPONSOR[Sponsor APIs<br/>simulated]

    subgraph SYSTEM[DH-03 System Boundary]
        APP[Modular Monolith<br/>single deployable application]
        WORKER[Background Worker<br/>outbox delivery and scheduled reminders]
        DB[(Relational Database<br/>PostgreSQL proposed)]
        OBJ[(Object Storage<br/>document bytes)]

        subgraph MODULES[Logical application modules]
            IAM[Identity & Authorization]
            PROP[Opportunities & Proposals]
            PROJECT[Funded Projects]
            DOCS[Document Management]
            AUDIT[Audit]
            NOTIFY[Notifications]
        end
        APP --- IAM
        APP --- PROP
        APP --- PROJECT
        APP --- DOCS
        APP --- AUDIT
        APP --- NOTIFY
    end

    ACTORS -->|HTTPS application requests| APP
    APP <-->|Authentication protocol adapter| IDP
    APP -->|Relational transactions and outbox| DB
    APP -->|Store/retrieve verified file objects| OBJ
    WORKER -->|Claim event / record delivery state| DB
    WORKER -->|Send asynchronously| EMAIL
    WORKER -->|Read due dates and enqueue reminders| DB
    APP <-->|Adapter; simulated exchange| SPONSOR
```

## Notes

The logical modules are not separate deployable services. The worker is a separately scheduled/runtime process that shares application contracts and persistence; it does not bypass module rules. PostgreSQL and object storage are proposed technologies, not procurement decisions. See [AD-01](../adr/AD-01-modular-monolith.md), [AD-04](../adr/AD-04-relational-object-storage.md), and [AD-06](../adr/AD-06-event-notifications.md).
