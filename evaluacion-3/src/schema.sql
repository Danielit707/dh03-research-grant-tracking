PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    identity_subject TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('PI', 'RESEARCH_OFFICE_COORDINATOR')),
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS opportunities (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    sponsor TEXT NOT NULL,
    deadline TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'CLOSED'))
);

CREATE TABLE IF NOT EXISTS proposals (
    id TEXT PRIMARY KEY,
    opportunity_id TEXT NOT NULL REFERENCES opportunities(id),
    title TEXT,
    sponsor TEXT,
    abstract TEXT,
    requested_amount REAL,
    deadline TEXT,
    status TEXT NOT NULL CHECK (status IN ('DRAFT', 'SUBMITTED', 'VERIFIED')),
    version INTEGER NOT NULL DEFAULT 0 CHECK (version >= 0),
    submitted_version_id TEXT,
    created_by TEXT NOT NULL REFERENCES users(id),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CHECK (
        (status = 'DRAFT' AND submitted_version_id IS NULL)
        OR (status IN ('SUBMITTED', 'VERIFIED') AND submitted_version_id IS NOT NULL)
    ),
    FOREIGN KEY (id, submitted_version_id)
        REFERENCES proposal_versions(proposal_id, id)
);

CREATE TABLE IF NOT EXISTS proposal_memberships (
    proposal_id TEXT NOT NULL REFERENCES proposals(id),
    user_id TEXT NOT NULL REFERENCES users(id),
    relationship TEXT NOT NULL CHECK (relationship IN ('OWNER_PI', 'ASSIGNED_COORDINATOR')),
    PRIMARY KEY (proposal_id, user_id)
);

CREATE TABLE IF NOT EXISTS proposal_versions (
    id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL REFERENCES proposals(id),
    sequence INTEGER NOT NULL CHECK (sequence > 0),
    snapshot_json TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    created_by TEXT NOT NULL REFERENCES users(id),
    created_at TEXT NOT NULL,
    UNIQUE (proposal_id, sequence),
    UNIQUE (proposal_id, id)
);

CREATE TABLE IF NOT EXISTS audit_events (
    id TEXT PRIMARY KEY,
    actor_id TEXT NOT NULL REFERENCES users(id),
    event_type TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    outcome TEXT NOT NULL CHECK (outcome IN ('SUCCESS', 'DENIED')),
    details_json TEXT NOT NULL,
    occurred_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notification_outbox (
    id TEXT PRIMARY KEY,
    event_key TEXT NOT NULL UNIQUE REFERENCES audit_events(id),
    event_type TEXT NOT NULL,
    aggregate_id TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    delivered_at TEXT
);

CREATE TABLE IF NOT EXISTS document_verifications (
    proposal_id TEXT PRIMARY KEY REFERENCES proposals(id),
    status TEXT NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'COMPLETE', 'CHANGES_REQUIRED')),
    due_date TEXT,
    notes TEXT NOT NULL DEFAULT '',
    updated_by TEXT REFERENCES users(id),
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS opportunity_document_requirements (
    id TEXT PRIMARY KEY,
    opportunity_id TEXT NOT NULL REFERENCES opportunities(id),
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    required INTEGER NOT NULL DEFAULT 1 CHECK (required IN (0, 1)),
    allowed_extension TEXT NOT NULL DEFAULT '.pdf' CHECK (allowed_extension = '.pdf'),
    max_size_bytes INTEGER NOT NULL DEFAULT 10485760 CHECK (max_size_bytes > 0),
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    UNIQUE (opportunity_id, name)
);

CREATE TABLE IF NOT EXISTS proposal_documents (
    id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL REFERENCES proposals(id),
    requirement_id TEXT NOT NULL REFERENCES opportunity_document_requirements(id),
    version INTEGER NOT NULL CHECK (version > 0),
    original_filename TEXT NOT NULL,
    storage_key TEXT NOT NULL UNIQUE,
    content_sha256 TEXT NOT NULL,
    content_type TEXT NOT NULL CHECK (content_type = 'application/pdf'),
    size_bytes INTEGER NOT NULL CHECK (size_bytes > 0),
    uploaded_by TEXT NOT NULL REFERENCES users(id),
    uploaded_at TEXT NOT NULL,
    UNIQUE (proposal_id, requirement_id, version)
);

CREATE INDEX IF NOT EXISTS idx_proposals_created_by ON proposals(created_by);
CREATE INDEX IF NOT EXISTS idx_memberships_user ON proposal_memberships(user_id, proposal_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_one_assigned_coordinator_per_proposal
    ON proposal_memberships(proposal_id) WHERE relationship = 'ASSIGNED_COORDINATOR';
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_events(entity_type, entity_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_outbox_pending ON notification_outbox(delivered_at, created_at);
CREATE INDEX IF NOT EXISTS idx_document_requirement ON proposal_documents(proposal_id, requirement_id, version);

CREATE TRIGGER IF NOT EXISTS proposal_versions_no_update
BEFORE UPDATE ON proposal_versions
BEGIN
    SELECT RAISE(ABORT, 'proposal versions are immutable');
END;

DROP TRIGGER IF EXISTS proposal_versions_no_delete;

CREATE TRIGGER IF NOT EXISTS audit_events_no_update
BEFORE UPDATE ON audit_events
BEGIN
    SELECT RAISE(ABORT, 'audit events are append-only');
END;

DROP TRIGGER IF EXISTS audit_events_no_delete;

CREATE TRIGGER IF NOT EXISTS proposal_documents_no_update
BEFORE UPDATE ON proposal_documents
BEGIN
    SELECT RAISE(ABORT, 'proposal document versions are immutable');
END;

DROP TRIGGER IF EXISTS proposal_documents_no_delete;
