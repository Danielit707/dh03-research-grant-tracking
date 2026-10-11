# Context View

```mermaid
flowchart LR
    PI[Principal Investigator]
    REV[Reviewer / Approver]
    ADMIN[Research Office Administrator]
    TEAM[Research Team Member]
    IDP[Institutional Identity Provider]
    EMAIL[Email Gateway]
    SPONSOR[Sponsor APIs<br/>simulated in academic scope]
    DH03[DH-03 Research Proposal<br/>& Project Lifecycle System]

    PI -->|Register opportunities, prepare proposals,<br/>track status and projects| DH03
    REV -->|Review assigned items,<br/>approve or request changes| DH03
    ADMIN -->|Coordinate workflows, record decisions,<br/>activate and close projects| DH03
    TEAM -->|Access assigned proposal/project information| DH03
    DH03 <-->|Authenticate user / validate identity| IDP
    DH03 -->|Send notifications and reminders| EMAIL
    DH03 <-->|Exchange sponsor opportunity/decision data;<br/>simulation unless separately approved| SPONSOR
```

## Boundary notes

- Authentication delegation depends on provider availability; OIDC is only a candidate. A demonstration adapter must not be presented as production institutional SSO.
- Sponsor APIs are shown as external context but real portal submission is out of scope; integration is simulated in the initial academic scope.
- Email delivery is external and asynchronous; temporary failure must not roll back the business operation.
- Users and resource visibility are governed by server-side policies in [AD-02](../adr/AD-02-identity-authorization.md).
