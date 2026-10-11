# AD-02 — Identity and Authorization

- **Status:** Proposed
- **Decision:** Separate authentication from application authorization; combine role permissions with resource relationships and enforce access on the server.

## Context

Some opportunity information may be broadly discoverable while proposal documents, reviews, and project records are restricted. Users with the same role can have access to different resources. An email address alone does not prove identity or authority.

## Alternatives considered

1. **Email-based identity/authorization:** treats mutable contact data as proof of identity and resource access; rejected.
2. **RBAC only:** provides broad permissions but cannot ensure a reviewer is assigned to this proposal or a PI owns this particular record.
3. **Resource relationships only:** represents ownership/assignment but complicates broad operational permissions.
4. **Combined authorization:** role authorizes an operation class; resource relationship authorizes its use on the specific record.

## Decision and rationale

Use a combined role- and relationship-based policy. Authenticate through an institutional identity provider if available, with OIDC as a candidate integration standard. Link the application user to a stable provider subject identifier. If the academic environment lacks integration, use a clearly labeled demonstration identity adapter while retaining the same application authorization model. The provider, protocol compatibility, and final roles are not confirmed.

## Initial authorization rules

- Opportunity visibility is explicitly classified as community-visible or restricted.
- Opportunity access does not automatically grant proposal access.
- Proposal actions require both an allowed role and a valid relationship to that proposal.
- Reviewers access only assigned reviews.
- Project authorization is evaluated independently of proposal authorization.
- Administrative capabilities are distinct from ordinary research access.
- Every protected operation is authorized server-side; client-side hiding is not authorization.

## Consequences and validation

This makes access policies more precise and testable but requires explicit relationship data and careful handling of role/assignment changes. Validate by having one PI request another PI's restricted resource directly; the server must deny it without disclosing protected data. Exact permissions and external-collaborator access remain open.
