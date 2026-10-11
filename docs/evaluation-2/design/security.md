# Security and Authorization Design

## Authentication is not authorization

Authentication establishes the caller's identity. The application maps the authenticated provider subject to an application `User`; it does not trust a client-supplied user ID, email, role, or resource relationship. OIDC is a proposed option only if the institutional provider and protocol are confirmed. A demo adapter must be isolated and labeled as non-production.

## Authorization policy

For every protected read or command, the server checks:

1. The authenticated user is active.
2. The user's role permits the operation class.
3. The user has an applicable relationship to the specific opportunity, proposal, review, document, or project.
4. The resource is in a state where the operation is permitted.

Initial policy direction:

- Opportunity visibility is explicit and does not confer access to linked proposals.
- PIs and team members see only records to which they are assigned or otherwise authorized.
- Reviewers can act only on reviews assigned to them.
- Project access is checked separately from proposal access.
- Administrative capabilities are explicit and are not implicit in ordinary researcher roles.
- External collaborators receive no access until their identity, sponsor, resource scope, and lifecycle access are explicitly approved.
- Every list, search, nested-resource, export, and file-download path applies the same authorization policy; filtering only in the client is insufficient.

The final role catalog, permissions, delegation rules, and external-collaborator policy are open; see [project status](../project-status.md).

## Document and notification protection

Document object keys are not public credentials. A user must pass application authorization before metadata or bytes are released. Notifications contain only the minimum useful information, do not attach confidential documents by default, and never grant access; links require authentication and a fresh authorization check.

## Audit and operational controls

Record significant access/decision/state-change events with actor, timestamp, action, outcome, entity reference, and relevant version reference. Audit events are append-only through application functions, not claimed to be immune to privileged infrastructure modification. Avoid logging credentials, tokens, or unnecessary confidential file contents. Storage encryption, key management, backup access, retention, incident response, and stronger tamper evidence require implementation decisions and review.

## Required security verification

Test horizontal access denial using direct identifiers and direct file-download paths, role restrictions, reviewer assignment boundaries, project/proposal separation, revoked membership, and list/search leakage. The unauthorized PI scenario must disclose zero protected data. The PoC is **NOT EXECUTED**; see [test plan](../validation/test-plan.md).
