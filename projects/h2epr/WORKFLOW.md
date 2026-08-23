# H2EPR event modeling workflow

This document is the project-level stage spine for building an H2EPR event.
It coordinates the existing research, scenario, mapping, configuration, and
bounded engineering methods without replacing the authority of their accepted
artifacts or specialist Skills.

The [Agent development workflow](agents/WORKFLOW.md) is the participant-
production sub-process used in stages E0--E2. This document owns the handoff
from an event question through a reusable, reviewed conformance baseline.
Simulation and scientific evaluation remain separately authorized work.

## Operating rules

- A stage consumes exact accepted inputs and records their identities or hashes.
- Completing one stage does not authorize the next stage. Record the authorized
  endpoint before implementation or external research begins.
- Research semantics, machine projection, policy implementation, runtime
  execution, and scientific evaluation remain distinct authorities.
- Accepted artifacts are not silently repaired. A material change produces a
  reviewed successor identity and remaps every affected downstream consumer.
- Configuration is non-executable until a separately accepted admission and
  binding package proves the exact configuration identity, required bindings,
  carrier projection, and fail-closed behavior.
- Use the smallest high-information lineage needed to test a new boundary.
  A full roster is an integration target, not the default implementation unit.
- Route a failure to the layer that owns it; do not hide it with a backend
  default, outcome-conditioned patch, or broader scope.

## Event stage spine

| Stage | Entry condition | Required result | Normal stopping boundary |
|---|---|---|---|
| E0 -- frame the event | approved research question and evidence boundary | modeled interval, causal role map, research roster, semantic skeleton, exposure and permission record | no participant product or implementation is implied |
| E1 -- produce participant semantics | accepted E0 inputs and an authorized role batch | reviewed Agent Definitions and population/cohort products, adopted claims and sources, lightweight interface preflights | no release membership, mapping, or implementation is implied |
| E2 -- release the roster | every roster row has a reviewed disposition | hash-pinned Roster Definition release with one coherent semantic inventory | release is non-executable and makes no validity claim |
| E3 -- converge event semantics and carrier design | accepted E2 release | accepted consolidated mapping/carrier review plus accepted Event Scenario Definition and complete interface closure | neither artifact may add the other's semantics or authorize policy code |
| E4 -- configure one declared purpose | accepted E3 authorities and explicit owner choices | versioned Scenario Configuration, configuration-to-Definition closure, substantive review, manifest and integrity record | configuration remains non-executable; E5 may validate its surface but cannot make it runnable |
| E5 -- validate the configuration surface | explicit engineering authorization naming the exact E4 identity and validation scope | schema/canonical-identity rules, stable failure classes, fail-closed loader, static preflight receipt and focused positive/negative tests | structural admission does not supply a carrier projection, policy binding, or executable run |
| E6 -- project and bind the minimal lineage | accepted E5 validation and explicit projection/binding authorization | exact carrier projection plus versioned policy/environment implementations only for the selected lineage, with intent/result and authority/resource boundaries preserved | all untouched policies and the full roster remain unbound |
| E7 -- close conformance and method learning | accepted E6 binding | negative conformance, deterministic trace/replay evidence, implementation review, reusable method deltas, and a second-event entry decision | stop before broad simulation unless a new scientific question and authorization exist |

E3 mapping and Scenario Definition work may inform one another, but both must
retain their own authority and converge before E4. E5 validates the
configuration as a fail-closed semantic input; E6 is the first stage that may
project and bind the selected lineage. They may be reviewed in one small
engineering cycle only when the authorization names both outputs; their
acceptance questions and artifacts must remain distinguishable.

## Stage record and closeout gate

Each stage must leave one discoverable record, which may be an existing brief,
release README/manifest, review, ADR, or close record. Together the records must
make these facts recoverable without relying on chat history:

1. event and stage identity;
2. exact accepted inputs and their versions or hashes;
3. purpose, authorized endpoint, and excluded work;
4. outputs and their status;
5. verification performed and unresolved findings;
6. owner decisions and exposure classification; and
7. the next legal action and its entry conditions.

Before marking any stage complete, report its current state, artifacts,
verification, unresolved findings, mainline alignment, depth proportionality,
and next-stage entry condition. Do not advance when the work has drifted from
the event question, widened beyond authorization, or gone deeper than needed to
test the reusable boundary.

Do not create a parallel tracker when an existing manifest or close record can
carry this information. Candidate notes and rejected alternatives remain in the
working area; tracked history contains accepted artifacts and concise current
guides.

## Engineering preflight boundary

E5 adapts only the parts of the repository experiment-preflight discipline that
apply before a bounded H2EPR implementation:

- verify repository state and exact semantic/configuration identities;
- resolve one declared validation scope to one configuration and named carrier
  target without pretending the projection already exists;
- reject unknown fields, missing references, hash drift, unbound required
  policies, hidden defaults, unsupported arithmetic, and broader execution;
- classify failures before repairing them; and
- produce a deterministic readiness receipt for the admitted slice.

API/RAG credentials, Ray/tmux capacity, long-run timeouts, experiment output
directories, full-round scheduling, and post-run quality intake belong to a
later runtime preflight. They are not E5 requirements when no such run is
authorized.

## Failure routing

| Finding | Owning layer |
|---|---|
| source, event-time, participant-availability, exposure, or historical claim error | evidence research |
| representation, mechanism, decision, parameter, or falsifier error | participant research or Definition |
| institution, world state, routing, delivery, lifecycle, resource, adjudication, or termination gap | Event Scenario Definition |
| actor assembly, structural selection, opening record, sensitivity, or configured-purpose error | Scenario Configuration |
| released semantic loss, ambiguous identity, or carrier mismatch | consolidated mapping |
| schema, canonicalization, hash, reference, or admission error | configuration admission/loader |
| hidden branch, default, policy mismatch, or implementation-only state | policy/environment implementation |
| nondeterministic transition, trace, or replay failure | runtime/reducer/trace implementation |
| empirical or historical comparison problem | separately authorized post-seal evaluation |

## Current H2EPR-0288 position

| Stage | Status | Accepted authority or next result |
|---|---|---|
| E0 | complete | Roster v0.4 and event semantic skeleton |
| E1 | complete | seven Agent Definitions and five population models with reviews and interface preflights |
| E2 | complete | Roster Definition release v0.1 |
| E3 | complete | consolidated mapping/carrier review and Event Scenario Definition v0.1/interface closure |
| E4 | complete | accepted non-executable Scenario Configuration v0.1 |
| E5 | complete | [bounded configuration admission v0.1](configs/panic_1907/configuration-admission-v0.1/) with exact schema/canonical identity, stable failure classes, fail-closed loader, cross-object checks, focused negatives, and static receipt |
| E6 | complete | [KT--NBC--NYCH bounded binding v0.1](agents/bindings/panic_1907/kt-nbc-nych-v0.1/) with exact upstream identities, four V1-projected actions, three routes, and six lineage-only policy implementations |
| E7 | complete | [KT--NBC--NYCH lineage conformance closeout v0.1](scenarios/panic_1907/lineage-conformance-v0.1/) with adversarial negatives, deterministic trace/replay receipt, implementation review, and method delta |

The current standardization cycle follows S0--S4:

| Cycle step | Status | Bounded result |
|---|---|---|
| S0 | complete | event workflow, authority, status, scope, and closeout-gate alignment |
| S1 | complete | reusable Scenario Configuration and narrow engineering-preflight method assets |
| S2 | complete | E5 schema/canonical identity, failure classes, loader, receipt, and focused tests |
| S3 | complete | E6 KT--NBC--NYCH carrier projection and minimal binding |
| S4 | complete | E7 negative conformance, trace/replay, review, and method closeout |

### Completed-cycle closeout

| Step | State and artifacts | Verification and findings | Mainline/depth audit | Next entry condition |
|---|---|---|---|---|
| S0 | project-level E0--E7 workflow plus aligned mutable guides | static workflow audit and `git diff --check` passed; no accepted semantic artifact changed | aligned; documentation-only scope stopped before Skill, schema, loader, policy, or runtime work | extract the configuration and bounded-preflight method from the accepted first-event case |
| S1 | `scenario-configuration` Skill, three progressive-disclosure references, public semantic template, and configuration index | Skill validator, link/boundary checks, accepted-release checksum verification, and retrospective 16-actor/10-unit configuration conformance passed; no unresolved blocker | aligned; method assets only, with machine schema, canonicalization, error codes, loader, carrier projection, policy, runtime, and evaluation left to their later stages | explicit S2 scope pinned to the accepted H2EPR-0288 configuration and E5 validation surface |
| S2 | project-local v0.1 schema, `h2epr.configuration` fail-closed loader/error/receipt surface, 17 focused tests, and bounded-admission receipt | configuration plus Agent regression 114 passed; Contracts V1 regression 349 passed; import/event-identity boundary 2 passed; receipt self/surface hashes passed; path and receipt defects found during review were corrected | aligned; accepted semantic bytes and Contracts V1 untouched, all nine policies remain unbound, no carrier/policy/runtime code added; implementation size remains below the existing roster loader and serves only E5 gates | exact E5 pass receipt plus separate E6 authorization naming the KT--NBC--NYCH lineage and minimum bindings |
| S3 | hash-anchored bounded release, exact loader/projector, three positive participant policies, six environment-policy implementations, four actions, three routes, and four focused tests | focused E6 tests 4 passed; configuration plus Agent regression 118 passed; Contracts V1 regression 349 passed; import boundary 2 passed; local release checksums and protected S2/configuration hashes passed | aligned; only KT, NBC and NYCH are present, 13 actors and three unrelated policies remain excluded, accepted configuration stays non-executable with all nine selections unchanged, and no trace/replay, simulator, calibration or evaluation was added | exact E6 manifest anchor plus S4 authorization already present; add adversarial negatives and one deterministic conformance trace without widening the lineage |
| S4 | fixed five-tick conformance runner, cross-hop validator, 12 focused negative/trace tests, reproducible receipt, implementation review, and bounded-lineage Skill reference | focused tests 12 passed; configuration plus Agent regression 130 passed; Contracts V1 349 passed; import boundary 2 passed; Skill validator, closeout checksums, protected E5/E6 hashes, and `git diff --check` passed | aligned; actor/action/route/policy inventories did not widen, only eight replay deltas were added, the trace envelope is described precisely, and no simulator, full event, calibration, held-out protocol, evaluation, or validity claim entered | stop H2EPR-0288 at E7; forward-test the method on a second event, or obtain a new question and authorization before deepening this event |

This cycle explicitly excludes full 16-actor runtime integration, all nine
policy implementations, full-event simulation, calibration or historical fit,
held-out/clean-builder experiments, post-seal scientific evaluation, and any
historical-validity or scientific-validity claim.

After the completed E7, prefer applying the method to a second event over deepening H2EPR-0288
without a newly approved research question. Cross-event reuse is demonstrated
by another event, not asserted from the first one.
