# Evidence and known limitations

## Verification

- `.\test.ps1`: **PASS** — 7 integration tests passed. Coverage includes successful submission and persisted snapshot/audit/outbox, incomplete and expired-deadline rejection, draft repair, role/resource denial, duplicate transition rejection, and concurrent submission conflict.
- `python -m compileall -q src tests`: **PASS**.
- `git diff --check`: **PASS**.
- `python -m src.seed` against a temporary database, run twice: **PASS** — both runs succeeded and retained the two synthetic proposals.
- The test run emitted two non-failing dependency deprecation warnings from the installed Starlette TestClient/httpx and AnyIO combination.

These results apply to the local evaluation setup and do not establish production readiness or validate the deferred integrations and policies below.

## Known limitations

- This is a local academic demonstration; it has no production identity provider, secrets management, TLS configuration, or operational monitoring.
- SQLite provides relational persistence for this isolated increment but does not validate the proposed PostgreSQL production deployment.
- The transactional outbox is persisted but no background delivery worker or email adapter is included.
- Proposal evidence is structured metadata only; document bytes, object storage, immutable document uploads, and recovery are not implemented.
- Review/approval policy, sponsor outcomes, project activation and lifecycle, closure, and portfolio reporting are outside this increment.
- The demo completeness requirements and current lifecycle vocabulary are implementation assumptions pending stakeholder confirmation.
