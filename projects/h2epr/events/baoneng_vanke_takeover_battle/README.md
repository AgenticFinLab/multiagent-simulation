# Baoneng–Vanke Takeover Battle

H2EPR-1031 uses the stable slug `baoneng_vanke_takeover_battle`. Its full-Draft,
dataset-only Rule baseline covers July 2015 through the June 2017 nomination and
scheduled-meeting boundary. It models participant disclosures, proposals,
opposition, corporate/regulatory responses and succession-related notices.

## Event assets

The [Source Profile](source-profile.json) seals exactly event_spec.json,
frozen_evidence.json and draft_epg.json. The
[roster and actor map](../../agents/rosters/baoneng_vanke_takeover_battle/) cover all
eight source IDs and 33 appearances. Eight
[Agent Definitions](../../agents/defines/baoneng_vanke_takeover_battle/) own the
human semantics; there is no source aggregate choice requiring a Population
Model. The [participant interface](../../agents/interfaces/baoneng_vanke_takeover_battle/)
projects four observation classes, 27 event intents plus no_op and two lifecycles.

The [Scenario](../../scenarios/baoneng_vanke_takeover_battle/) defines the record
world, authority and mechanism. Its interface closure accounts for all 31 source
action rows, including passive holdings, a passive nomination and a duplicated
nominee proposal. The [shared configuration](../../configs/baoneng_vanke_takeover_battle/shared/)
owns opening state, time and routes; the
[Rule configuration](../../configs/baoneng_vanke_takeover_battle/backends/rule/)
owns selected choices. The [Rule realization](../../execution/baoneng_vanke_takeover_battle/rule/)
pins the common implementation. [Assembly](package-assembly.json) compiles to
the backend-neutral [event package](package/).

The Source Profile records corrupt relation/transaction endpoints and conflicting
transaction/election claims. The 2016 proposed swap and later acquisition
disclosure remain separate; nomination and meeting notices do not produce an
elected board. P_2's composite issuer/board record is explicitly distinct from
Wang and Yu individual authority.

## Backend status

| Backend | Status | Current evidence or failure |
|---|---|---|
| Rule | implemented | admitted configuration/realization, exact package binding, independently verified run release |
| LLM | planned | no registered model-decision implementation or provenance; admission fails closed |
| RuleLLM | planned | no standardized proposal/admission implementation; admission fails closed |

Rule attaches without changing the backend-neutral package core. The backend
catalog does not authorize a planned implementation or fallback.

## Current result

The current canonical seed-0 run is `run.6f6408d11b70b472f33444ae`: eight actors,
20 coordinates, 823 trace records, 861 graph nodes and 2,465 edges. Fresh A/B,
generated-ID perturbation, trace and tick/run seals, authoritative replay,
complete graph reconstruction and zero unresolved transport are verified in the
[run release](../../releases/baoneng_vanke_takeover_battle/rule/).

The [simulation reading](../../reports/baoneng_vanke_takeover_battle/rule/simulation-reading.md)
records full-output coverage, every non-default action and terminal expectation,
and the limits of this disclosure/decision-record model. It also distinguishes
the canonical baseline from local missing/late-information construction probes.
Raw custody is retained under ignored
`.local-runtime/h2epr-simulation/runs/benchmark/baoneng_vanke_takeover_battle/rule/2026-09-05-passive-admission/`.

The [current registry](../current-events.json) and
[cross-event Rule conformance](../../releases/cross-event/rule/) cover the
current accepted event set. Desired record outcomes are descriptive; valid
open endpoints can still produce complete verified releases.

## Claim boundary

This event establishes dataset-conditioned semantic construction, deterministic
Rule execution, independent evidence verification, replay, graph provenance and
bounded simulation-only description. Full Draft exposure, logical-time
compression and the narrow statement choice set are part of the result.

It does not establish securities clearing, endogenous acquisition strategy,
verified legal control, an observed board election, historical fit, calibration,
held-out performance, policy effects, causal/scientific validity or universal
generality. No external research, Reference or model decision was used.
