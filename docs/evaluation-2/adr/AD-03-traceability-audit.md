# AD-03 — Document Versioning and Audit History

- **Status:** Proposed
- **Decision:** Preserve document versions and maintain an application-level append-only history of significant business operations.

## Context

Retaining only the latest document loses prior evidence. Versioning alone does not explain who submitted, approved, or changed a version. An audit event alone cannot reconstruct the historical document content.

## Alternatives considered

1. **Overwrite documents and omit audit history:** lowest storage cost, but destroys evidence and cannot reconstruct prior decisions.
2. **Version documents without audit events:** preserves file contents but not the actor, operation, outcome, or decision linking a version to an action.
3. **Version documents and audit significant events:** preserves both historical content and the events that explain its use; selected.

## Decision and rationale

Represent a logical document and its immutable versions separately. A version records its parent document, owning proposal/project, object-storage reference, uploader/time, state, format/size, content hash, and optional predecessor. A submission/approval event references the exact version used. Record significant submission, review, approval, rejection, document change, access change, activation, milestone, project change, and closure events.

Audit events are append-only through ordinary application functionality: no normal business operation edits or deletes a prior event. This is not a claim of tamper-proof storage against database or infrastructure administrators. Stronger tamper evidence requires separate requirements and controls. Preserve targeted business snapshots only where reconstructing a specific historical state requires them; do not snapshot the entire system after every change by default.

## Consequences and validation

History supports accountability and reconstruction but requires storage, retention/deletion policy, event classification, and access rules. Verify that a later upload cannot alter an earlier version and that a prior submission resolves to its exact stored content/hash. Retention and tamper-evidence requirements remain open.
