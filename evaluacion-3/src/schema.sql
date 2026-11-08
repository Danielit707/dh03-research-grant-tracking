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
    sponsor TEXT NOT NULL,
    deadline TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS proposals (
    id TEXT PRIMARY KEY,
    opportunity_id TEXT NOT NULL REFERENCES opportunities(id),
    title TEXT,
    sponsor TEXT,
    abstract TEXT,
    requested_amount REAL,
    deadline TEXT,
    status TEXT NOT NULL CHECK (status IN ('DRAFT', 'SUBMITTED')),
    version INTEGER NOT NULL DEFAULT 0 CHECK (version >= 0),
    submitted_version_id TEXT,
    created_by TEXT NOT NULL REFERENCES users(id),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CHECK (
        (status = 'DRAFT' AND submitted_version_id IS NULL)
        OR (status = 'SUBMITTED' AND submitted_version_id IS NOT NULL)
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

CREATE INDEX IF NOT EXISTS idx_proposals_created_by ON proposals(created_by);
CREATE INDEX IF NOT EXISTS idx_memberships_user ON proposal_memberships(user_id, proposal_id);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_events(entity_type, entity_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_outbox_pending ON notification_outbox(delivered_at, created_at);

CREATE TRIGGER IF NOT EXISTS proposal_versions_no_update
BEFORE UPDATE ON proposal_versions
BEGIN
    SELECT RAISE(ABORT, 'proposal versions are immutable');
END;

CREATE TRIGGER IF NOT EXISTS proposal_versions_no_delete
BEFORE DELETE ON proposal_versions
BEGIN
    SELECT RAISE(ABORT, 'proposal versions are immutable');
END;

CREATE TRIGGER IF NOT EXISTS audit_events_no_update
BEFORE UPDATE ON audit_events
BEGIN
    SELECT RAISE(ABORT, 'audit events are append-only');
END;

CREATE TRIGGER IF NOT EXISTS audit_events_no_delete
BEFORE DELETE ON audit_events
BEGIN
    SELECT RAISE(ABORT, 'audit events are append-only');
END;
