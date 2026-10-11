# Quality Attribute Scenarios

Each scenario uses the six required fields: **Source, Stimulus, Artifact, Environment, Response, Response Measure**. Measures below are candidate acceptance criteria for review, not institutional service-level commitments or test results. All scenarios remain unexecuted until evidence is recorded in the [validation findings](validation/findings.md).

## QA-01 — Security: reject access to another PI's proposal (AD-02)

- **Source:** A PI who is not associated with the target proposal.
- **Stimulus:** Sends a direct REST/application request to retrieve another PI's restricted proposal, including a known identifier or URL.
- **Artifact:** Proposal API and server-side authorization policy.
- **Environment:** Normal operation with two authenticated PIs and distinct restricted proposals.
- **Response:** The server denies the request without returning proposal or document data and records the denied attempt as required by the audit policy.
- **Response Measure:** 0 unauthorized disclosures; HTTP 403 for an authenticated but unauthorized request (or 404 only if a separately approved anti-enumeration policy requires it); no protected payload fields returned.

## QA-02 — Traceability: retrieve the exact submitted version (AD-03, AD-04)

- **Source:** An authorized Research Office reviewer or auditor.
- **Stimulus:** Requests the version associated with an earlier submission after a newer document version has been uploaded.
- **Artifact:** Document version records, object references, submission record, and audit history.
- **Environment:** Normal operation after at least two versions exist.
- **Response:** The system returns the exact version referenced by the submission and its associated actor/time/event metadata; later uploads do not replace it.
- **Response Measure:** 100% of test submissions resolve to the recorded immutable version and matching content hash; zero historical version overwrites.

## QA-03 — Integrity: reject activation without prerequisites (AD-05, AD-07)

- **Source:** An authorized coordinator attempts project activation.
- **Stimulus:** Requests activation with no favorable sponsor decision, missing required activation data, or a proposal version that is not explicitly accepted.
- **Artifact:** Activation business operation and relational records.
- **Environment:** Normal operation with an incomplete or ineligible proposal.
- **Response:** The operation rejects the transition, creates no active FundedProject, and leaves a traceable validation outcome.
- **Response Measure:** 100% of invalid activation attempts leave proposal/project state unchanged; no FundedProject is active without a favorable decision and explicit accepted-version reference.

## QA-04 — Maintainability: preserve module boundaries (AD-01)

- **Source:** A developer adding a change to one business capability.
- **Stimulus:** Implements or changes an operation within a module.
- **Artifact:** Modular-monolith application modules and their application interfaces.
- **Environment:** Normal development and automated integration-test run.
- **Response:** The change uses declared module interfaces and the module's rules can be tested without direct mutation of another module's internal structures.
- **Response Measure:** All module contract tests pass; no cross-module direct persistence access is found in the reviewed change. This candidate measure requires a repository-level boundary check to be defined.

## QA-05 — Resilience: email outage does not lose committed notification (AD-06)

- **Source:** A temporary email gateway failure.
- **Stimulus:** A business event is committed while notification delivery is unavailable.
- **Artifact:** Business transaction, outbox record, notification worker, and email adapter.
- **Environment:** Email gateway is unavailable during event processing, then recovers.
- **Response:** The business operation commits with its outbox event; the worker records failed attempts and retries delivery after recovery without requiring the user to repeat the operation.
- **Response Measure:** 100% of committed test events remain recoverable in the outbox; after recovery, each intended notification reaches a terminal delivery state; duplicate effects are prevented or detected using an idempotency/deduplication key. Delivery-time target remains TBD.

## QA-06 — Performance: structured lookup and document handling (AD-04)

- **Source:** An authorized user searches for a proposal and opens an associated document.
- **Stimulus:** Submits a representative filter/search request and retrieves a file using its metadata reference.
- **Artifact:** Proposal query path, relational database, document metadata, and object storage.
- **Environment:** Representative test data and concurrent load to be defined before execution.
- **Response:** Structured search returns authorized matching records; file retrieval is served from object storage without loading document bytes into relational query paths.
- **Response Measure:** Candidate target: p95 search response under 2 seconds and p95 file-download start under 3 seconds for the agreed benchmark dataset/load. Dataset, concurrency, file sizes, and targets require stakeholder confirmation before being acceptance criteria.

## QA-07 — Evolvability: substitute identity and sponsor adapters (AD-01, AD-02)

- **Source:** A developer integrating a different institutional identity provider or sponsor API.
- **Stimulus:** Replaces a configured adapter without changing proposal/project domain rules.
- **Artifact:** Identity and external-integration interfaces.
- **Environment:** Integration test using a simulated provider/API and then a different compatible test adapter.
- **Response:** Authentication/integration data is translated at the boundary; core authorization and lifecycle behavior remain unchanged.
- **Response Measure:** The same authorization and lifecycle contract tests pass for both adapters; no provider-specific fields leak into domain contracts. No actual integration has been tested.
