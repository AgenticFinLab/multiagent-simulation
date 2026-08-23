# KT--NBC--NYCH bounded binding v0.1

This release binds one selected Panic of 1907 request lineage to Contracts V1.
It pins the accepted Scenario Configuration and admission receipt, the
consolidated roster mapping profile, the machine binding, and the implementation
surfaces used by the lineage.

## Bound surface

The binding contains three named actors and four semantic actions:

1. Knickerbocker Trust submits one bounded request to the National Bank of
   Commerce;
2. the National Bank of Commerce forwards it once as a pure courier,
   preserving the original request, content hash, mandate, and represented
   sender;
3. the New York Clearing House records and classifies only the request
   delivered on the second hop; and
4. the New York Clearing House issues one scoped disposition to Knickerbocker
   without implying universal prohibition, delivery, resource commitment, or
   a rescue outcome.

The lineage implements the time, information, review, facility, lifecycle, and
result policies needed by these actions. Amount, service, and venue policies
remain unbound.

## Authority and claim boundary

This is a full-draft-exposed conformance binding. It does not alter the
accepted Scenario Configuration: all nine configuration-level policy
selections remain `unbound`, and `execution_eligible` remains false.

The release starts no simulator and supplies no full-roster runtime,
calibration, evaluation, or historical-validity claim. The older two-role
mapping and runner remain frozen reference assets; this release supersedes
their direct KT-to-NYCH abstraction only for the bounded three-role lineage.

## Integrity

`manifest.json` records the binding, implementation files, and exact upstream
identities. Its `manifest_sha256` field is the canonical self-hash; consumers
also verify the raw manifest bytes against an independently supplied anchor.
`SHA256SUMS` covers files owned by this release directory.

## Files

- `binding.json` declares the actors, relationships, observations, actions,
  routes, policies, and excluded scope.
- `manifest.json` records implementation and upstream identities.
- `SHA256SUMS` records local package-file hashes.
- `src/h2epr/scenarios/panic_1907/lineage_v0_1/` contains the fail-closed
  loader, V1 projector, participant policies, and bounded environment
  policies.
- `tests/agents/test_panic_1907_lineage_binding.py` exercises positive loading,
  projection, and policy boundaries without running a simulation.

After installing H2EPR, validate the binding from the repository root:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/agents/test_panic_1907_lineage_binding.py

cd projects/h2epr/agents/bindings/panic_1907/kt-nbc-nych-v0.1
sha256sum --check SHA256SUMS
```
