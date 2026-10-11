# Validation Plan — Priority Proofs of Concept

## Execution status

**All PoCs below: STATUS: NOT EXECUTED.** These are test specifications from the architecture proposal, not implementation evidence or claims that a working environment currently exists. Record environment, build/commit, test data, actual results, defects, and evidence links before changing a status.

| PoC | Architecture decisions |
| --- | --- |
| PoC 1 — Resource-based access control | AD-02 |
| PoC 2 — Document versioning and historical reconstruction | AD-03, AD-04 |
| PoC 3 — Proposal-to-project activation | AD-05, AD-07 |
| PoC 4 — Notification reliability | AD-06 |

## PoC 1 — Resource-Based Access Control

- **STATUS: NOT EXECUTED**
- **Objective:** Demonstrate that authorization denies access to unrelated restricted proposals.
- **Setup:** Create two authenticated PI identities and separate restricted proposals with no shared authorized relationship. Configure the candidate authorization policy.
- **Steps:** Authenticate as PI-A; request PI-B's proposal through its normal API and a direct identifier/URL; attempt a document download and a list/search path that could reveal it.
- **Expected assertions:**
  - Each protected request is denied server-side, regardless of identifier knowledge.
  - No protected proposal fields, document metadata, or file bytes are returned.
  - Denial does not mutate proposal state.
  - The response follows the approved anti-enumeration policy (candidate: HTTP 403 for authenticated denial); no conflicting response behavior across endpoints.
- **Evidence to capture:** Request/response logs with sensitive content redacted, authorization policy/configuration, test output.

## PoC 2 — Document Versioning and Historical Reconstruction

- **STATUS: NOT EXECUTED**
- **Objective:** Demonstrate that document revision does not destroy evidence used by an earlier submission.
- **Setup:** Create an authorized proposal and a known test file; record its expected hash.
- **Steps:** Upload version 1; record a submission referencing version 1; upload changed version 2; retrieve both versions and resolve the earlier submission reference.
- **Expected assertions:**
  - The two versions have distinct identifiers and content hashes.
  - Version 1 remains retrievable to an authorized user with its original hash.
  - The submission still resolves to version 1, not the latest version.
  - Version 2 is not exposed as available before object existence/integrity verification.
- **Evidence to capture:** Test output, version/submission metadata, hash comparison, and upload failure/recovery observations.

## PoC 3 — Proposal-to-Project Activation

- **STATUS: NOT EXECUTED**
- **Objective:** Demonstrate separate project creation with an auditable link to the accepted proposal version.
- **Setup:** Create a proposal with at least two versions and a favorable sponsor decision explicitly associated with one selected version.
- **Steps:** Attempt activation with missing prerequisites; then supply all approved activation fields and activate using the selected version.
- **Expected assertions:**
  - Missing prerequisites prevent activation and leave no active project.
  - A valid activation creates a distinct FundedProject.
  - The project references the originating proposal and exact accepted version; it does not select “latest” implicitly.
  - Actor, timestamp, activation event, and any associated outbox event are recorded consistently.
- **Evidence to capture:** Before/after state, request/result, database references, audit event, and automated test output.

## PoC 4 — Notification Reliability

- **STATUS: NOT EXECUTED**
- **Objective:** Demonstrate that temporary email failure does not require repeating the business operation or lose its notification event.
- **Setup:** Configure a test email adapter that can fail and later recover; select a notification-triggering operation.
- **Steps:** Commit the business operation while email delivery fails; inspect the outbox and attempt history; restore the adapter and retry worker processing.
- **Expected assertions:**
  - Business state and outbox event commit together.
  - Email outage does not roll back the business operation.
  - Failed attempts and retry/terminal delivery states are recorded.
  - Recovery processes the durable event without repeating the original business command.
  - Duplicate handling prevents or detects repeated delivery effects; exactly-once delivery is not assumed.
- **Evidence to capture:** Business and outbox records, worker logs, adapter responses, attempt count, deduplication behavior, and test output.

## Exit criteria and reporting

For each PoC, report **PASS**, **FAIL**, or **BLOCKED** only after execution, with the exact tested commit/build, environment, data setup, expected versus actual assertions, evidence, and linked defects. A failure or changed architectural assumption must trigger ADR/status review. Passing a narrow PoC does not by itself prove production readiness or resolve unrelated open policy questions.
