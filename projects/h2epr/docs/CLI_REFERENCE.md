# CLI reference

## Boundary

The CLI exposes maintained admission, compilation, execution, conformance, and
publication entry points. Commands use the same Python functions as tests and
do not bypass schemas, parent identity checks, replay, or publication
verification. They do not authorize a phase, choose an event, discover
protected inputs, install dependencies, or contact a remote service.

Run from the repository root:

```bash
export PYTHONPATH=projects/h2epr/src
python -B -m h2epr.cli --help
```

Every success is one canonicalizable JSON object on stdout. An expected
contract failure is one JSON object on stderr with `status`, `command`,
`error_type`, and stable `error_code`, and exits with status 2. Unexpected
programming errors retain a traceback so they cannot be mistaken for an
ordinary admission rejection.

## Commands

| Command | Reads | Writes | Refuses |
|---|---|---|---|
| `validate-registry` | current registry and declared paths | nothing | schema, hash, duplicate identity, unsafe/missing path |
| `build-package` | assembly, released parents, schemas, implementation sources, dataset | absent package root | parent, provenance, registry, path, source, or attachment drift |
| `validate-package` | package, selected binding, dataset | nothing | integrity, source exposure, implementation, actor/action, or backend mismatch |
| `materialize` | admitted package and dataset | absent raw-custody root | unavailable backend, invalid decision/effect, replay, graph, seal, or transport failure |
| `identity-conformance` | canonical and opaque-ID custody roots | optional receipt | semantic trajectory or graph drift |
| `admit-experiment` | plan, packages, bindings, analysis contracts | optional receipt | parity, custody, model-control, scheduling, retry, or claim-boundary failure |
| `publish-run-release` | package and three sealed Rule custody roots | absent compact release root | any independent reproduction or evidence failure |
| `publish-cross-event-release` | at least two package/custody pairs | absent compact release root | identity alias, contract/source/output mismatch, or failed constituent evidence |

Use `python -B -m h2epr.cli <command> --help` for the exact argument surface.

## Standard sequence for Rule

```bash
python -B -m h2epr.cli validate-registry

python -B -m h2epr.cli build-package \
  --data-root data/h2epr \
  --assembly projects/h2epr/events/<event>/package-assembly.json \
  --output projects/h2epr/events/<event>/package

python -B -m h2epr.cli validate-package \
  --data-root data/h2epr \
  --package projects/h2epr/events/<event>/package \
  --backend rule

python -B -m h2epr.cli materialize \
  --data-root data/h2epr \
  --package projects/h2epr/events/<event>/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/<event>/rule/current/materialization-a \
  --output .local-runtime/h2epr-simulation/runs/<event>/rule/current/materialization-a
```

Materialize B into a distinct physical root with the same logical locator,
then materialize an identity probe with a distinct locator and
`--identity-variant opaque-generated-ids`. Use the two conformance/publication
commands only after all roots pass direct validation. The release guide owns
the evidence interpretation.

## Failure handling

Example shape:

```json
{"command":"validate-registry","error_code":"current_event_registry_self_hash_mismatch","error_type":"CurrentEventRegistryError","status":"fail"}
```

Do not retry by changing data, seed, or output until the error has been routed
to its owning layer. Preserve a failed materialization root. A partially staged
compact release is removed by the publisher; an existing release root is never
overwritten.

## Path and environment rules

Use repository-relative, non-symlinked formal asset paths. Raw custody belongs
beneath ignored `.local-runtime/h2epr-simulation/runs/`. Do not point output at
a tracked semantic parent or package. `PYTHONPATH` selects the local H2EPR
implementation; it does not pin run identity—the run manifest independently
records exact H2EPR and MASim source hashes.
