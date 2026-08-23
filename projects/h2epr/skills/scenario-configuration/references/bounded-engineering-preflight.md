# Bounded engineering preflight

Use this reference for H2EPR E5: static admission of one exact, accepted
Scenario Configuration into a fail-closed configuration surface. It adapts
the repository experiment-preflight discipline without turning E5 into an
experiment launch.

Passing this preflight means only that the exact configuration can be
identified, parsed, validated, and rejected predictably when invalid. It does
not make the configuration executable and does not authorize E6 carrier
projection or policy/environment binding.

## Adaptation boundary

| Repository preflight practice | E5 adaptation |
|---|---|
| identify branch/commit and document worktree state | retain |
| select exact experiment rows | replace with one exact configuration identity and bounded validation scope |
| resolve config through the intended loader | retain as fail-closed structural admission |
| classify failures before fixing | retain with H2EPR authority routing |
| record exact commands and results | retain in a static receipt |
| API keys, prompts/parsers, and RAG assets | exclude |
| Ray/tmux scheduling, CPU budgets, timeouts, and output directories | exclude |
| full-round run and post-run sample intake | exclude |
| calibration and scientific-quality review | exclude |

Runtime-specific checks belong to a later runtime preflight if a run is ever
authorized.

## Required declaration

Before any implementation or check, record:

- repository root, branch, commit, and whether unrelated worktree changes are
  present;
- accepted configuration path, ID, version, status, file digest, and promoted
  manifest/checksum identities;
- pinned Definition, roster release, mapping, mapping-profile, evidence, and
  source identities required by the configuration;
- authorized validation surface, allowed files, focused test command, and
  explicit stopping point;
- expected schema identity and canonical-identity rule, when E5 supplies them;
- expected execution eligibility and policy-binding state; and
- prohibited work, including carrier projection, policy implementation,
  runtime, calibration, evaluation, and validity claims.

An undocumented dirty worktree is a preflight failure only when it prevents
exact attribution or overlaps the admitted surface. Preserve and report
unrelated user changes.

## Static gates

### Gate P0: authorization and repository identity

- The exact configuration and E5 surface are named.
- Repository identity and relevant worktree state are recorded.
- Every intended write and test stays inside the authorized surface.
- No accepted semantic artifact will be edited to make the loader pass.

### Gate P1: package identity and integrity

- Configuration ID, version, status, digest, manifest, and checksum inventory
  agree.
- Every pinned semantic input resolves exactly once from the declared root and
  matches its expected integrity value.
- Missing, unsafe, duplicate, unlisted, or drifted paths fail closed.

### Gate P2: parse, schema, and canonical identity

- The document parses without duplicate-key or unsupported-type ambiguity.
- The exact accepted schema version validates the complete document and
  rejects unknown fields according to its declared policy.
- Canonical serialization or equivalent identity normalization is deterministic
  and round-trips without semantic loss.
- Canonical digest mismatch and unsupported schema/version fail before any
  projection or policy lookup.

S1 does not define the schema, normalization algorithm, digest envelope, or
literal machine error codes. S2 must make those choices explicit and test
them.

### Gate P3: semantic references and assembly

- All referenced actors, entities, capabilities, units, hosts, authority
  graphs, resource owners, records, exogenous inputs, policies, and overlay
  targets resolve with the expected type.
- One-actor-per-entity, one-resource-owner-per-entity, host scope,
  capability membership, and declared coverage counts hold.
- Opening-state and dated-input combinations are consistent.
- No loader default, synonym, repair, or copied count changes accepted
  semantics.

### Gate P4: execution boundary and binding status

- The loader preserves the declared execution boundary.
- Every required selected policy reports its exact binding status.
- An unbound policy is valid for an accepted non-executable configuration but
  must block execution admission.
- Successful structural admission never flips `execution_eligible`, supplies
  a policy, selects a carrier, or authorizes a run.

### Gate P5: focused conformance and failure routing

- One accepted positive fixture loads to the expected canonical identity.
- Negative cases cover every implemented boundary named in the authorization,
  including integrity, schema/version, unknown field, reference, assembly,
  exact overlay target, and execution-policy checks as applicable.
- Each rejection is stable, deterministic, and routed to one owning layer.
- Focused tests run before relevant regression tests; exact commands and
  results are retained.

### Gate P6: static receipt

Record a machine-readable receipt containing at least:

- receipt-format identity and validation-surface version;
- repository identity and documented worktree state;
- exact configuration identity, source digest, canonical digest, and schema
  identity;
- exact pinned semantic-input identities and verification results;
- authorization and prohibited-scope summary;
- each gate result, focused command, exit status, and test summary;
- execution eligibility and policy-binding summary;
- stable failure class and diagnostic for a failed admission;
- final verdict and explicit next legal stage; and
- receipt identity or digest sufficient to compare repeated preflights.

The receipt may include observational metadata such as execution time, but
that metadata must not alter the canonical configuration identity.

## Failure ownership categories

S1 fixes these semantic categories, not their eventual literal machine codes:

| Category | Owner |
|---|---|
| repository attribution or unauthorized scope | engineering task boundary |
| configuration package identity or integrity | configuration promotion package |
| parse, schema, canonicalization, or loader default | E5 implementation |
| actor assembly, opening record, exogenous input, policy selection, overlay, or configured-purpose mismatch | Scenario Configuration |
| missing world/lifecycle meaning or causal owner | Event Scenario Definition |
| released participant meaning or evidence-time contradiction | participant product, release, or evidence authority |
| carrier identity or projection ambiguity | consolidated mapping or E6 projection |
| absent policy implementation | later policy-binding stage |

Do not edit an accepted Definition, mapping, or configuration merely to turn a
red engineering gate green.

## Verdicts

Use one of:

- `PASS_BOUNDED_CONFIGURATION_ADMISSION`;
- `FAIL_CONFIGURATION_SURFACE`;
- `RETURN_TO_CONFIGURATION`;
- `RETURN_TO_SCENARIO_MAPPING_OR_RELEASE`; or
- `BLOCKED_BY_AUTHORIZATION_SCOPE`.

The pass verdict authorizes only the already named E5 closeout. E6 requires a
new stage transition and exact projection scope.

## Stop conditions

Stop when:

- the accepted configuration or any pinned input drifts;
- a machine rule would need to invent or repair semantic content;
- the configured schema or canonical-identity rule is absent or ambiguous;
- a required reference cannot be resolved without broadening the event;
- a negative case exposes a Definition, mapping, or configuration defect;
- execution is requested while a required policy remains unbound; or
- the task would expand into API/RAG checks, runtime scheduling, full-event
  implementation, calibration, simulation, or scientific evaluation.
