# Experiment standard

## Purpose and current status

An H2EPR run materializes one event package, backend binding, seed, and runtime
identity. An experiment is an identity-sealed set of those runs assembled for
a declared comparison. The experiment layer owns selection and scheduling; it
does not change participant semantics, scenario state, backend behavior, or
runtime output.

The current `h2epr.experiment` adapter reloads selected packages and verifies
package and binding identities, seed sets, custody separation, model
provenance, comparison parity, analysis contracts, timeout order, retry policy,
and claim exclusions. Admission is read-only and launches no run.
Rule is currently the only implemented backend, so any plan row naming `llm`
or `rulellm` fails during package admission.

## Units and authority

```text
experiment plan
  ├── row: event package × backend binding × seed set
  │     └── run: one package × one binding × one seed
  ├── comparison group: compatible rows and comparison kind
  ├── scheduling and failure policy
  └── pinned analysis contracts and claim boundary
```

The event package owns actors, observations, action spaces, environment,
timeline, and opening state. The backend binding owns decision production.
The run manifest owns the realized seed and source inventories. The
experiment plan owns which valid runs belong together, their fresh custody
roots, and the conditions under which a comparison may be attempted. Custody
locators are normalized before uniqueness is checked, so textual aliases such
as a trailing slash cannot designate the same directory twice.

An experiment plan may select an accepted asset; it may not repair or
override it. Changing an event package or binding creates a different row.
Changing only the seed creates another run inside the same row.

## Plan identity and row contract

Machine plans validate against
[`experiment-plan.schema.json`](schemas/experiment-plan.schema.json) and
carry a canonical `plan_sha256`. Every row pins:

- one event ID and project-relative package path;
- the backend-neutral package hash and selected binding hash;
- one or more explicit, unique integer seeds;
- canonical generated-identity mode; and
- a unique ignored custody root below
  `.local-runtime/h2epr-simulation/experiments/`.

The admission code reloads the package with the named backend. A planned,
missing, mismatched, unsafe, or hash-drifted binding is rejected before any
execution. Custody roots are declarations, not output-directory discovery;
the plan cannot reuse a path or escape the experiment custody boundary.

## Backend and model provenance

Rule rows must not carry model settings. LLM and RuleLLM rows require the
provider, stable model and version identifiers, local or remote service mode,
prompt and response contract paths and hashes, every decoding parameter with
its basis, and a finite attempt limit. Credentials and endpoint secrets never
belong in the plan.

The admission receipt preserves the complete model-control record, including
decoding values and bases, and derives a canonical control signature. Every
LLM or RuleLLM row in a cross-event group must have the same signature. When a
within-event group contains both LLM and RuleLLM, those model-side controls
must also match; their controlled difference is the RuleLLM constraint layer,
not an unrecorded model or decoding change. A Rule row has no model signature.

Model service availability is not evidence of backend implementation. The
binding must already exist and pass ordinary package admission. An eventual
model runner must record request, parse, retry, refusal, timeout, and fallback
dispositions without silently substituting Rule behavior.

## Comparison parity

Two comparison kinds are admitted.

| Kind | Required parity | Allowed difference |
|---|---|---|
| `within_event_backend` | Event, package hash, seed set, runtime/environment/trace contracts, analysis definition, and equal model controls across LLM/RuleLLM rows | Backend binding and decision production |
| `cross_event_contract` | Backend, seed set, model controls for model backends, package schema family, output roles, runtime/MASim inventories, closure checks, and claim exclusions | Event package and event-local vocabulary |

Within-event groups require distinct backends. Cross-event groups require
distinct event IDs. Every group must have a pinned analysis contract of the
same scope. A missing value remains missing; event-local fields are not forced
into a false common metric.

## Scheduling, progress, and resource control

The plan sets a maximum parallel-run count, wall timeout, stall timeout, and
progress-poll interval. Their order is strict:

```text
progress poll < stall timeout <= wall timeout
```

Wall time bounds a run even when it remains active. Stall time detects a lack
of new durable progress. A future executor must define progress from sealed
runtime milestones or committed output, not log volume. Parallelism is a
resource ceiling, not a target; memory, model quota, or process limits may
reduce it without changing the scientific row.

Resume is not assumed safe. A run may resume only if participant, transport,
reducer, trace, and generated-ID state can be restored exactly and the result
retains one coherent run identity. Otherwise the failed custody is preserved
and the row restarts in a new directory.

## Failure routing and retries

Failures retain their original layer.

| Class | Examples | Default disposition |
|---|---|---|
| admission | schema, path, hash, package, binding, parity | stop; correct the owning plan or asset |
| model contract | prompt/response mismatch, malformed output, refusal | record; no hidden backend substitution |
| provider transient | temporary service or transport failure | retry only when declared |
| resource exhaustion | memory, worker, thread, or quota exhaustion | preserve custody; reduce scheduling pressure |
| stall | no durable progress within the declared window | preserve evidence; retry only when declared |
| runtime contract | invalid action, authority, reducer, route, or lifecycle | stop; route to backend or environment owner |
| evidence integrity | trace, seal, replay, graph, checksum | reject the run and release |
| analysis | missing input, undefined metric, non-comparable output | record as unavailable; do not invent a value |

Automatic retries are restricted to `provider_transient`,
`resource_exhaustion`, and `stall`. A zero retry limit requires an empty
retryable-class list. Every failed attempt keeps separate custody and a typed
record; retries never overwrite the first failure.

## Analysis and publication

Every experiment pins at least one simulation-only analysis definition.
Comparison groups additionally pin a definition matching their scope. The
analysis contract states required inputs, unavailable-value behavior,
aggregation unit, and interpretation boundary before results are seen.

Reusable metrics belong in a domain or method family with one authoritative
implementation. Event-local analysis may assemble those metrics and add a
clearly named event-specific measure. This adopts MASim's registry principle
without importing its finance-only measures into unrelated H2EPR events.

An experiment closeout records all planned rows, successful and failed
attempts, excluded outputs, source and model identities, resource deviations,
analysis availability, and the exact denominator behind every aggregate.
Only independently verified run releases may enter a published comparison.

## Claim boundary

Experiment admission establishes plan integrity and executable-row
availability. Successful runs may add engineering repeatability or
cross-backend process evidence. Neither plan admission nor run count alone
establishes historical fit, parameter calibration, held-out performance,
causality, policy effectiveness, scientific validity, or universal
generality. Those claims require a separately accepted evaluation protocol.

## Commands

Admission is read-only unless an output receipt is explicitly requested:

```bash
PYTHONPATH=projects/h2epr/src python -B -m h2epr.cli admit-experiment \
  --data-root data/h2epr \
  --plan projects/h2epr/experiments/<experiment>/plan.json
```

The resulting receipt validates against
[`experiment-admission-receipt.schema.json`](schemas/experiment-admission-receipt.schema.json).
No matrix executor or experiment release is claimed at the current boundary.
