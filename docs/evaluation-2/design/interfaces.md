# Application and Integration Interfaces

These are conceptual contracts, not an implemented API specification. Concrete transport, payload schemas, authentication claims, error envelopes, and versioning rules remain to be selected.

## Application operations

| Operation | Owning capability | Required checks/effects |
| --- | --- | --- |
| Create/update opportunity or proposal | Opportunities & Proposals | Authenticate; authorize role and resource relationship; record actor/time for significant changes |
| Upload document version | Document Management | Authorize; create pending version; verify object integrity; expose only after finalization |
| Record review/approval outcome | Opportunities & Proposals | Verify reviewer assignment, current state and evidence; retain outcome/comment and decision-time version references |
| Authorize/record submission | Opportunities & Proposals | Verify required reviews; bind submission to exact version; append audit/outbox event |
| Record sponsor outcome | Opportunities & Proposals | Authorized actor; retain outcome/evidence and relevant version relationship |
| Activate funded project | Funded Projects | Verify favorable decision, explicit accepted version, required activation data; create distinct project and origin links |
| Propose/approve project change | Funded Projects | Capture before/after, reason, required reviewers; apply approved state only through controlled operation |
| Close project | Funded Projects | Verify required evidence/deliverables; preserve closure event and readable history |
| Search or retrieve resource | Owning module | Apply authorization to every result and nested document; do not rely on UI filtering |

## External adapters

- **Identity adapter:** maps an authenticated external subject to a stable application User; authentication success does not grant resource access. OIDC is a candidate only.
- **Email adapter:** receives notification requests from the worker, reports success/failure/ambiguous outcome, and does not run inside the business transaction.
- **Sponsor adapter:** simulated in the academic scope; should not submit to real portals absent explicit scope and approval.
- **Object-storage adapter:** stores/retrieves opaque objects and exposes integrity/availability results; application authorization remains authoritative.

## Error and idempotency behavior

Operations distinguish authentication failure, authorization denial, validation failure, stale/concurrent state, and dependency failure. A retryable external failure must not be converted into a success-shaped response. Commands likely to be retried (upload finalization, transition, notification delivery) need idempotency or duplicate detection. Exact status codes and transport representations are implementation decisions; protected resource access must not disclose content on denial.
