# mock-netsuite

Disposable stand-in for NetSuite. Emits records in true NetSuite shapes
(`internalId`, `tranDate`, `entity`; record types `job`, `vendorbill`,
`invoice`, `customerpayment`, `timebill`) and streams new postings over SSE.

Swapping to real NetSuite means implementing the same client interface in the
`intelligence` service against SuiteAnalytics/SuiteTalk — this service is thrown
away. See `../../docs/architecture.md`.

## Run

```bash
uv run mock-netsuite        # serves on :8000
```
