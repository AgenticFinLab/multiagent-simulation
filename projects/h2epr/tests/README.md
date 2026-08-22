# H2EPR contract tests

The independent contract suite validates stable V1 schemas and synthetic
fixtures without starting MASim or reading evaluation references. Activate the
LMSim development environment, then run it from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider projects/h2epr/tests/contracts
```

The Agent suite retains the frozen two-role `0.1.0-dev` engineering baseline
and the current two-role conformance slice. It also validates the accepted
Roster release through a separate mapping profile: all twelve product hashes,
62 commitments, 115 observation placements, 107 intent placements,
capability-qualified identities, multi-capability actor composition,
host-scoped population state, authority/resource scope, a broker funding
lifecycle and deterministic replay. It does not select a full-Roster policy,
start Ray, or run the G3 simulation.

The fixture is documented under
[`fixtures/agents/panic_1907/minimal_binding_v0_1/`](fixtures/agents/panic_1907/minimal_binding_v0_1/).

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=projects/h2epr/src \
  python -B -m pytest -p no:cacheprovider projects/h2epr/tests/agents
```

The separate G1 construction suite validates the repository-local Source
Adapter and typed Construction IR:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=projects/h2epr/src \
  python -m pytest -p no:cacheprovider projects/h2epr/tests/construction
```

The G2 suite validates declarative registry/artifact/policy/world construction,
three canonical EventBundles, the nine-row profile/seed matrix, and bounded
serialized-input negatives without executing a simulator:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=projects/h2epr/src \
  python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/g2 \
  projects/h2epr/tests/construction \
  projects/h2epr/tests/contracts
```

The G3 suite validates the opt-in phased runtime, fixed Rule policy,
authoritative reducer, delayed-message transport, trace/seal/replay chain and
generated-only P007 annotations. Ordinary CI runs the offline owning suite; it
does not launch the formal Ray matrix:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=projects/h2epr/src \
  RAY_USAGE_STATS_ENABLED=0 \
  python -B -m pytest -p no:cacheprovider projects/h2epr/tests/g3
```

Fixtures below `fixtures/g3/` are synthetic closed-value examples, not run
outputs or historical targets. Formal canary outputs remain ignored local
evidence rather than tracked test fixtures.

The G4 owning suite validates Reference-blind sealed-trace inventory and
wrapper checks, deterministic event/episode/stage compilation, graph
relations, GraphSeal closure, and fail-closed dependency boundaries:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=projects/h2epr/src \
  python -B -m pytest -p no:cacheprovider projects/h2epr/tests/g4
```

G4 tests use only minimized synthetic fixtures below `fixtures/g4/` and
offline V1 contract assets. They do not read real A0 outputs or Reference
material, start Ray or a simulation, or establish historical fidelity. The
isolated post-seal evaluation surface remains future G5 work.

Fixtures below `fixtures/g2/` are minimized and explicitly synthetic. Real
target-derived bundles are generated only into the ignored local evidence
area; they are not tracked fixtures or expected scientific outcomes.

Construction fixtures under `fixtures/construction_ir/` are synthetic and
minimized. The cross-domain tests consume only an explicit hash-pinned
non-Reference manifest; they do not walk event directories or open a held-out
evaluation file. Architecture parsing is demo-only, and strict-policy tests do
not represent an actual clean strict build.

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

The contract, G1, G2, and Agent baseline suites do not run a full scenario. The
Agent baseline executes only its frozen three-tick semantic micro-situation. G3
exercises the bounded H2EPR Rule runtime and its deterministic interfaces; the
separately controlled canary matrix supplies execution evidence. G4 compiles eligible
sealed trace records into a deterministic V1 Generated EPG, but neither these
tests nor the canary establish historical calibration, Reference alignment or
scientific readiness. `examples/` and top-level `configs/` remain the standard
MASim scenario convention, while the reviewed H2EPR project/runtime/compiler
split remains evolvable. Required-surface checks deliberately allow unrelated
future files under `projects/h2epr/`.
