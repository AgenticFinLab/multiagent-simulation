# H2EPR contract tests

This suite validates the stable V1 schemas and synthetic fixtures without
starting MASim or reading evaluation references. Activate the LMSim
development environment, then run it from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider projects/h2epr/tests
```

The portable environment definition and the distinction between contract-only
validation and full MASim runtime development are documented in
[`docs/development-environment.md`](../../../docs/development-environment.md).

The support code is split by responsibility. Builders under `support/cases/`
own bounded communication, repository, and boundary-regression cases. The
test-only `case_specs/v1/` JSON files hold the 255 declarative schema,
construction, communication, and trace/identity conditions; small typed
adapters load them with a closed field, operation, and validator vocabulary.
They are not runtime fixtures, scenarios, experiments, contract schemas, or
audit history. `case_registry.py` combines the exact population;
`receipt.py` serializes it deterministically; `schema_registry.py` resolves the
catalog offline; and the validator modules separately own construction,
communication, identity, and trace/seal invariants. Every one of the 345
retained behavior cases is a separate pytest parameter with a stable
behavior-based ID and therefore appears independently in ordinary failures.
Each ID is exactly responsibility plus expected result plus one explicit
semantic condition. Legacy case provenance is retained only for local
migration evidence: it cannot select behavior or enter the public receipt.
Every case also exposes a canonical behavior-only mutation descriptor and its
SHA-256. Receipt grouping uses only responsibility, validation category, and
expected/observed outcome rather than historical cumulative suite slices.

This Phase-0 suite creates no runnable scenario. `examples/` and top-level
`configs/` remain the current standard MASim convention. Future H2EPR scenario,
configuration, runtime, and test locations remain adjustable through reviewed
Phase-1 architecture decisions. Passing this suite does not claim runtime or
scientific readiness, and the required-surface check deliberately allows
unrelated future files under `projects/h2epr/`.
