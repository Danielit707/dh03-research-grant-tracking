# Validation Findings and Evidence Register

## Current result

No PoC execution evidence is included in the source proposal or this repository. Therefore, the status of PoC 1 through PoC 4 is **NOT EXECUTED**. No architectural behavior is reported as passed or production-verified.

## Findings register

| ID | Item | Status | Finding / evidence |
| --- | --- | --- | --- |
| VAL-01 | PoC 1 — Resource-based access control (AD-02) | NOT EXECUTED | No authorization implementation or test evidence attached. See [test specification](test-plan.md#poc-1--resource-based-access-control). |
| VAL-02 | PoC 2 — Document versioning and historical reconstruction (AD-03, AD-04) | NOT EXECUTED | No version-store/upload-integrity test evidence attached. See [test specification](test-plan.md#poc-2--document-versioning-and-historical-reconstruction). |
| VAL-03 | PoC 3 — Proposal-to-project activation (AD-05, AD-07) | NOT EXECUTED | No activation workflow test evidence attached. See [test specification](test-plan.md#poc-3--proposal-to-project-activation). |
| VAL-04 | PoC 4 — Notification reliability (AD-06) | NOT EXECUTED | No outbox/worker failure-recovery test evidence attached. See [test specification](test-plan.md#poc-4--notification-reliability). |
| VAL-05 | Candidate quality-scenario measures | NOT MEASURED | Thresholds in [quality scenarios](../quality-scenarios.md) are proposed for review, not measured targets or results. |

## Evidence update protocol

When a PoC is run, replace its `NOT EXECUTED` status only with a recorded result and include:

- execution date and responsible tester;
- tested commit/build and environment/configuration;
- test data/setup and exact steps;
- expected and actual assertion results;
- evidence location (logs, test output, hashes, screenshots where useful);
- defects, deviations, and follow-up owner;
- whether any ADR or open risk changed as a result.

Do not remove a failed or blocked result; preserve it and document remediation/retest evidence. “Not executed” is an honest status, not a passing result.
