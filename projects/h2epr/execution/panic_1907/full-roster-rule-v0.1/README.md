# Panic of 1907 full-roster Rule package v0.1

- Event: `H2EPR-0288`
- Package: `h2epr.0288.full-roster-rule.v0_1@0.1.0`
- Runtime bundle: `h2epr.0288.rule-runtime-bundle.v0_1@0.1.0`
- Status: `accepted_executable_package`
- Purpose: deterministic, uncalibrated mechanism coverage

This release is the executable successor to the accepted Panic of 1907
Scenario Configuration and Policy Realization. It preserves those releases as
semantic parents and supplies the closed actor carriers, initial state,
decision inputs, action bindings, routes, lifecycle graphs, runtime components,
clock, completion policy, and compiler input needed for a full-roster Rule run.

The [executable package](executable-package.json) records lineage, component
bindings, run requirements, and output custody. The
[runtime bundle](runtime-bundle.json) is the self-contained runtime input
materialized from the hash-pinned parents. The [review](substantive-review.md)
assesses the assembly, authority, determinism, and claim boundaries.

## Closed assembly

| Surface | Accepted count |
|---|---:|
| actor instances and actor carriers | 16 |
| actor-capability projections | 17 |
| participant artifacts | 12 |
| decision observation rules | 88 |
| actor-qualified action bindings | 127 |
| communication routes | 35 |
| selected Scenario policies | 9 |
| lifecycle families | 13 |
| runtime components | 9 |

One carrier belongs to each configured actor. The composed member-bank actor
contains separate bank-resource and call-money-lender capability projections,
with distinct policy state and configuration inputs under one actor and one
resource owner. Shared population policies remain shared implementations, but
their configured profiles, hosts, state, and action scopes remain
actor-qualified.

Each commitment receives one explicit observation rule and logical execution
coordinate. The values stay inside its released domains and form a declared
mechanism-coverage path; they are not inferred historical measurements. The
canonical path selects at most one branch per commitment and retains an
explicit no-intent result where no branch activates. Alternative branches are
closed by policy tests rather than forced into one run.

## Runtime authority

Participant policies consume only their declared observations, private state,
and configuration parameters. They may emit a registered intent, but they do
not author admission, business disposition, execution result, message
delivery, or another participant's choice. The environment creates typed
results, the reducer alone changes authoritative state and lifecycle records,
and results become visible through a later transport delivery.

Routes are derived from the declared interaction topology and the actions that
actually require a recipient. Environment-to-actor result routes and bounded
participant routes are explicit; there is no all-to-all fallback. Unknown
actors, actions, routes, configuration values, components, or lifecycle
references are rejected rather than repaired.

The clock uses two deterministic partial-order slots per civil date from 18
October through 2 November 1907. A slot orders barrier work but does not assert
an unobserved intraday time. The run uses the public MASim phased lifecycle,
event-process values, append-only transport, authoritative reducer, trace,
seal, and replay interfaces without changing MASim.

## Determinism and output boundary

The bundle is reconstructed twice during admission and both canonical byte
streams must agree. The package requires two fresh runs with the same bundle
and seed. Their runtime bundle, trace, tick seals, run seal, replay receipt,
final state, and generated EPG must match, and every graph reference must
resolve to the sealed trace.

Large run materializations belong in an ignored event run directory. A later
run-and-graph release may track compact manifests, receipts, checksums, and
reader documentation after the repeated execution closes. This package itself
contains no canonical trace or generated EPG.

## Scope

The package is exposed to the full event record and uses synthetic
mechanism-coverage projections where the accepted configuration is
underdetermined. It establishes an executable and replayable engineering
boundary. It does not establish historical calibration, historical
reconstruction, held-out performance, policy effectiveness, or scientific
validity.
