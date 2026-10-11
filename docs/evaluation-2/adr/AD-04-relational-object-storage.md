# AD-04 — Relational Data and Object Storage

- **Status:** Proposed
- **Decision:** Store structured business data and document metadata relationally; store document bytes in object storage.

## Context

Users need structured relationships among people, proposals, decisions, projects, milestones, and document versions, alongside potentially large files with independent access and retention characteristics.

## Alternatives considered

1. **Store files in the relational database:** simplifies some transactional workflows, but increases database/backup size and couples file lifecycle to database operations.
2. **Store all data as objects:** unsuitable for relational integrity and querying lifecycle relationships.
3. **Relational metadata plus object-store bytes:** matches the distinct data types and is selected.

## Decision and rationale

Use a relational database for entities, relationships, state, and metadata. PostgreSQL is the proposed initial candidate, not a confirmed institutional standard. Store file contents in object storage and reference them from immutable document-version records. Select a specific object-storage provider only after reviewing access controls, versioning, cost, retrieval, retention, and archival characteristics; do not assume a specific AWS tier.

Because the database and object store do not share an ordinary transaction, use an upload state machine: create a controlled pending upload; write the object; verify object availability and integrity (including content hash); finalize metadata; then expose the version as available. Failed/abandoned uploads must be detectable and recoverable or cleanable under an explicit policy.

## Consequences and validation

Separation supports appropriate query and storage management, but introduces partial failure, reconciliation, and archival retrieval concerns. PoC-02 validates immutable document history; upload integrity/recovery also needs a focused test before production use. Provider, file limits, lifecycle policy, and retention period remain open.
