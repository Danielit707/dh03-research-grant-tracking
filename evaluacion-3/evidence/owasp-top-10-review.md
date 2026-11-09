# OWASP Top 10:2025 targeted review

This is a code review plus local integration-test coverage for the Evaluation 3 prototype, mapped to OWASP Top 10:2025. It is not a penetration test, a complete control audit, or production certification. OWASP's Top 10 is an awareness standard; it does not replace threat modeling and application-specific review.

| Category | Review and current evidence | Remaining risk / boundary |
| --- | --- | --- |
| A01 Broken Access Control | Every proposal and document operation checks role and proposal membership server-side. PI upload requires owner relationship; coordinator verification requires assigned relationship; downloads are attachment responses. Tests cover cross-PI upload/download/read denial and coordinator scoping. | Demo tokens are intentionally shared evaluation credentials. No production session/SSO, CSRF model, or rate limiting. |
| A02 Security Misconfiguration | Uploaded bytes live outside the static web directory, use UUID storage keys, and are returned with `nosniff` and private/no-store headers. The run script binds localhost by default. | No production TLS, security-header policy, reverse-proxy configuration, host permissions audit, or deployment hardening. |
| A03 Software Supply Chain Failures | Direct dependencies in `requirements.txt` are pinned to exact versions. | No generated hash lockfile, dependency vulnerability scan, SBOM, provenance, or automated update policy. Pinned versions alone do not prove a dependency is secure. |
| A04 Cryptographic Failures | SHA-256 identifies uploaded bytes and submitted snapshots. | Hashes provide integrity identifiers, not confidentiality or authenticity. Local database and document bytes are not encrypted at rest; transport is only appropriate for loopback demo. |
| A05 Injection | SQL statements use bound parameters; dynamic update column names come only from a strict server-side allowlist. Browser output is escaped before interpolation. Filename input is reduced to a basename and never used as a storage path. | No separate static-analysis or penetration testing. Uploaded PDF content is not parsed or executed. |
| A06 Insecure Design | Sending to office is blocked until the required technical proposal, administrative documents, budget, and any call-specific ethics/compliance or academic review documents exist. Opportunity sponsor/deadline are authoritative server-side; expired/closed calls reject new drafts. Drafts are excluded from coordinator claiming; assignment is explicit and database constrained to one coordinator. | Demo call requirements and claim-to-self assignment are evaluation assumptions. Financial/academic review, institutional authorization, and sponsor submission are later stages not implemented yet. |
| A07 Authentication Failures | API requests require a Bearer token mapped to an active seeded user. Unknown/missing tokens fail closed. | Tokens are visible in the demo selector and have no expiry/rotation. This is deliberately not a real authentication design. |
| A08 Software or Data Integrity Failures | Proposal snapshots and uploaded document versions are immutable during the normal workflow; files receive UUID names and SHA-256 values. A PI-owned full proposal purge removes its versions and bytes after confirmation. | A crash between filesystem promotion and database commit can require manual orphan cleanup. No tamper-evident file store or object-store reconciliation job. Full proposal purge intentionally removes historical records for that proposal. |
| A09 Security Logging & Alerting Failures | Creation, assignment, upload, rejected owner uploads, verification and submission are audited during normal processing; denied upload attempts are recorded without logging file content. | No centralized log export, alerting, audit-retention policy, or complete logging of all unauthenticated/unauthorized requests. Explicit proposal purge also removes associated audit events and leaves no tombstone. |
| A10 Mishandling of Exceptional Conditions | Uploads have request and streamed file size limits; invalid lengths, oversized files, wrong extensions, empty content, invalid PDF markers, unknown requirement IDs, and unauthorized access fail with controlled errors. Staging files are removed on validation/transaction failure. | Disk exhaustion below the per-request limit, process termination during promotion, and filesystem/DB repair are not handled operationally. |

## Upload-specific controls

- Allow only `.pdf`; ignore client MIME type as proof of content.
- Normalize the submitted filename and reject empty, overlong, control-character, or non-PDF names; use a server-generated UUID for storage.
- Enforce a 10 MiB streaming limit (plus bounded multipart overhead), hash while writing to a staging file, and check `%PDF-` at the beginning plus `%%EOF` near the end.
- Store outside static assets and serve only after fresh proposal membership authorization, as an attachment with `application/octet-stream` and `X-Content-Type-Options: nosniff`.
- Keep previous versions and include the newest requirement/version/hash list in the submitted snapshot.

These basic markers are spoofable and do not establish that a PDF is well formed or free of malware. The app does not invoke a PDF parser, antivirus, sandbox, or content disarm/reconstruction service. Do not use real or sensitive documents in this local demo.

## Test evidence

The integration suite exercises role/resource denial, required-document gating, malformed PDF and extension rejection, path-like filenames, version preservation, private storage, safe download headers, and cross-PI download denial. The recorded run result is maintained in this section after executing `test.ps1`.
