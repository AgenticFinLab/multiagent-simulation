# SingHealth Data Breach

H2EPR-0616 uses the stable slug `singhealth_data_breach`. Its full-Draft, dataset-only Rule
baseline models a bounded response path from qualified breach records through
detection, disclosure, inquiry, enforcement, announced remediation and later
public attribution.

## Event assets

The [Source Profile](source-profile.json) seals exactly `event_spec.json`,
`frozen_evidence.json` and `draft_epg.json`. The
[roster and actor map](../../agents/rosters/singhealth_data_breach/) account for all nine source
IDs and 26 appearances. Eight
[Agent Definitions](../../agents/defines/singhealth_data_breach/) own the human semantics; the
affected-patient cohort remains explicit initial context because the Draft
exposes no patient-authored response. The
[participant interface](../../agents/interfaces/singhealth_data_breach/) projects five
observation classes, 17 event intents plus `no_op`, and two lifecycles.

The [Scenario](../../scenarios/singhealth_data_breach/) defines the public-record world,
authority and reducer. It distinguishes generated attribution results from already-visible
Whitefly-related vocabulary and rejects malformed Draft relation/penalty endpoints as
authority. The [shared configuration](../../configs/singhealth_data_breach/shared/) owns 20
coordinates, opening state and routes; the
[Rule configuration](../../configs/singhealth_data_breach/backends/rule/) owns selected choices.
The [Rule realization](../../execution/singhealth_data_breach/rule/) pins the common
implementation. [Assembly](package-assembly.json) compiles to the backend-neutral
[event package](package/).

Technical compromise, individual patient response/harm, fine payment, completed
control deployment and cybersecurity effectiveness remain outside the reducer.
The May 2015 date is retained as affected-record cohort context, not treated as
a verified intrusion start.

## Backend status

| Backend | Status | Current evidence or failure |
|---|---|---|
| Rule | implemented | admitted configuration/realization, exact package binding, independently verified run release |
| LLM | planned | no registered model-decision implementation or provenance; admission fails closed |
| RuleLLM | planned | no standardized proposal/admission implementation; admission fails closed |

Rule attaches without changing the backend-neutral package core. Planned catalog
entries provide no execution authority or fallback.

## Current result

The canonical seed-0 run is `run.26b57124e29d077af3150e02`: eight actors, 20 coordinates,
782 trace records,
820 graph nodes and
2,318 edges. Fresh A/B, generated-ID perturbation,
trace and tick/run seals, authoritative replay, complete graph reconstruction and
zero unresolved transport are independently verified in the
[run release](../../releases/singhealth_data_breach/rule/).

The [simulation reading](../../reports/singhealth_data_breach/rule/simulation-reading.md)
accounts for every output family, coordinate, non-default action and expectation.
Eight contract probes cover unresolved, withdrawn, withheld, delayed,
expired and policy-bypass paths, including withdrawn COI findings. They demonstrate
valid open endpoints, content-sensitive Rule choices and shared
receipt/world-state rejections while preserving execution integrity. Raw custody is
retained below ignored `.local-runtime/h2epr-simulation/`.

The [current registry](../current-events.json) and
[cross-event Rule conformance](../../releases/cross-event/rule/) cover the
accepted event set. Descriptive endpoint agreement is reported separately from
publication integrity.

## Claim boundary

This event establishes dataset-conditioned semantic construction,
state/information-aware deterministic Rule execution, independent verification,
replay, trace-derived graph provenance and bounded simulation-only description.
Full Draft exposure, representation gates and logical-time assumptions are part
of the result.

It does not establish intrusion timing, Whitefly attribution truth, individual
patient behavior, fine payment, implemented reform, historical fit, calibration,
held-out performance, security/policy effects, causal or scientific validity, or
universal generality. No external research, Reference or model decision was used.
