# SingHealth Data Breach full-roster Rule package v0.1

- Event: `H2EPR-0616`
- Package: `h2epr.0616.full-roster-rule.v0_1@0.1.0`
- Runtime bundle: `h2epr.0616.rule-runtime-bundle.v0_1@0.1.0`
- Status: `accepted_executable_package`
- Purpose: deterministic, uncalibrated mechanism coverage

This release is the executable successor to the accepted SingHealth Data
Breach Scenario Configuration and Policy Realization. It leaves those
semantic parents unchanged and supplies the actor carriers, initial state,
decision inputs, action bindings, routes, lifecycle graphs, runtime
components, clock, completion policy, and compiler input required for a
full-roster Rule run.

The [executable package](executable-package.json) records lineage, component
bindings, run requirements, and output custody. The
[runtime bundle](runtime-bundle.json) is the complete runtime input rebuilt
from the pinned parents. The [review](substantive-review.md) examines the
assembly, authority, timing, determinism, and claim boundaries.

## Closed assembly

| Surface | Accepted count |
|---|---:|
| actor instances and actor carriers | 13 |
| actor-capability projections | 13 |
| participant artifacts | 9 |
| decision observation rules | 41 |
| actor-qualified action bindings | 74 |
| communication routes | 46 |
| configured institutional route records | 8 |
| selected Scenario policies | 9 |
| lifecycle families | 11 |
| runtime components | 9 |

The package also pins the event-specific phased runner that connects these
components through MASim's public simulation lifecycle. Its fifty logical
coordinates can be materialized without adding runtime actors: deliveries to
MOH, CSA, or the notification process terminate at their declared bounded
route context rather than being promoted to autonomous participants.

One carrier belongs to each of the seven office actors and six responsibility
unit actors. The three technical units share one Population policy and the
three operational units share another, while every unit retains its own
assignment, capacity, access scope, private state, and action namespace.
Sharing an implementation therefore does not merge units or their knowledge.

Each configured commitment has one actor-qualified observation rule. Its
values remain inside the released domains and select one declared
mechanism-coverage path. All 41 rules emit a registered intent in this profile;
alternative branches and explicit no-intent behavior remain covered by the
participant-policy tests rather than being forced into the same run.

## Authority and communication

Participant policies consume only their declared observations and private
state. They may issue an intent, but they do not author route admission,
technical success, institutional classification, notification delivery, or
another participant's choice. The environment validates actor, capability,
commitment, branch, capacity, authority, access, resource owner, and prestate.
The reducer alone changes authoritative state and lifecycle records, and an
action result becomes visible only through later transport delivery.

The route registry contains thirteen environment-to-actor result channels and
thirty-three exact sender-recipient channels. Twenty-five participant channels
resolve directly to one of the eight configured institutional route records;
eight additional channels are canonical single-recipient projections from the
accepted participant products and consolidated mapping. Every route is
single-recipient. There is no set broadcast or all-to-all fallback, and
unsupported routes fail closed.

## Event-driven time

The clock uses five configuration anchors: modeled start, participant-response
start, acute-window start, core horizon, and notification-observation horizon.
At each anchor it exposes the ten declared same-time precedence barriers.
Decisions occur only at the `participant_decision_and_issue` barrier, yielding
50 deterministic logical coordinates in total. An anchor or barrier orders
work but does not claim an unobserved intraday timestamp.

The canonical profile releases all six exogenous opportunities at declared
anchors without selecting their historical outcome. Participant observations
are declared mechanism-coverage projections, not reconstructed measurements.
Pending lifecycle objects at the horizon retain owner, version, state, reason,
and causal references as typed carry-forward records.

## Determinism and output custody

Admission rebuilds the runtime bundle twice and requires identical canonical
bytes. The package requires two fresh runs with the same bundle and seed. The
runtime bundle, trace, tick seals, run seal, replay receipt, final state, and
generated EPG must agree, and every graph reference must resolve to the sealed
trace.

Large run materializations belong in an ignored event run directory. A
separate run-and-graph release may track compact manifests, receipts,
checksums, and reader documentation after repeated execution closes. This
package contains no canonical trace or generated EPG.

## Scope

The package was constructed with access to the full event record and uses
synthetic values where the accepted configuration is underdetermined. It
establishes an executable, replayable engineering boundary for mechanism
coverage. It does not establish historical calibration, historical
reconstruction, held-out performance, policy effectiveness, or scientific
validity.
