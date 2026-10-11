# Domain Model View

```mermaid
classDiagram
    class User {
        +UserId id
        +IdentitySubject externalSubject
        +ContactInfo contact
        +AccountStatus status
    }
    class Proposal {
        +ProposalId id
        +ProposalStatus status
        +OpportunityId opportunityId
    }
    class ProposalVersion {
        +VersionId id
        +int sequence
        +StorageReference objectRef
        +ContentHash hash
        +DateTime createdAt
    }
    class FundedProject {
        +ProjectId id
        +ProjectStatus status
        +DateTime activatedAt
        +VersionId acceptedProposalVersionId
    }
    class AuditLog {
        +AuditEventId id
        +String eventType
        +DateTime occurredAt
        +String outcome
        +String entityReference
    }
    class NotificationEvent {
        +EventId id
        +String eventType
        +DeliveryState state
        +int attemptCount
        +DateTime createdAt
    }

    Proposal "1" --> "1..*" ProposalVersion : has immutable versions
    Proposal "1" --> "0..1" FundedProject : origin of (activation)
    FundedProject "1" --> "1" ProposalVersion : accepted basis
    User "1" --> "0..*" Proposal : owns / participates
    User "1" --> "0..*" AuditLog : actor
    User "1" --> "0..*" NotificationEvent : recipient (policy-derived)
    ProposalVersion "1" --> "0..*" AuditLog : referenced by decisions
    Proposal "1" --> "0..*" AuditLog : lifecycle events
    FundedProject "1" --> "0..*" AuditLog : lifecycle events
    Proposal "1" --> "0..*" NotificationEvent : triggers
    FundedProject "1" --> "0..*" NotificationEvent : triggers
```

## Interpretation

The diagram is conceptual, not a complete schema. `User` relationships to proposals/projects must be modeled with explicit membership, role, or assignment records in persistence; the diagram summarizes those associations. `ProposalVersion` refers to document versions associated with proposal evidence; a complete document model may include a logical `Document` aggregate. Audit and notification events reference an affected entity and may reference a specific version. The accepted version is explicit and must not be inferred from recency. See [domain and data contracts](../design/domain-and-data.md).
