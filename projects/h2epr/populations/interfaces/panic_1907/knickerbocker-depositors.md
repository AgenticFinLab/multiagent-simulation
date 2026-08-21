# Knickerbocker depositor population — interface preflight

## Representation and causal boundary

The R1 product is an event-bound depositor population model, not one
institutional Agent. Weighted choice units own withdrawal, retention, and
awaiting choices. The scenario owns unit composition, balances, signal
delivery, local visibility, service and queue state, request disposition,
payment, suspension, and institutional resource effects.

The population interacts with Knickerbocker's service process through
withdrawal requests and delivered results. It does not directly interact with
NBC or NYCH and receives their information only through an explicit public or
account channel.

## Semantic surface

### Observations and time limits

- remaining claim as last delivered account state;
- private withdrawal need as an explicit sensitivity assumption;
- dated, delivered institution signals with retained provenance and conflict;
- own or locally authorized access observation;
- optional coarse peer-activity projection, never exact global state;
- own request lifecycle and delivered result; and
- no future suspension, hidden Knickerbocker state, support deliberation, or
  other depositor private state.

### Private state

- remaining claim;
- withdrawal-need class;
- request state;
- last delivered information set; and
- pre-run response profile and qualitative mixed-signal tie rule.

### Outputs and routes

| Output | Counterparty or consumer | Route |
|---|---|---|
| `request_withdrawal` | Knickerbocker service process | population choice → request creation → service/adjudication → result |
| `retain_for_interval` | trace and later population state only | recorded decision with no new action intent |
| `await_request_result` | trace and request lifecycle only | recorded decision with no duplicate request |

The environment returns paid, partial, delayed, failed, rejected, expired,
cancelled, undelivered, or unavailable states through the appropriate
lifecycle and result records. The exact vocabulary is a consolidated-mapping
question; the distinctions may not be collapsed.

## Skeleton compatibility

- The model preserves the skeleton's population-versus-institution boundary.
- Institution communication affects the population only after delivery.
- Requested withdrawal is separate from realized resource effect.
- Population composition and operational access remain scenario-owned.
- The output does not add a new executable participant or event phase.
- Exogenous demand remains available as an explicit ablation, not as an
  endogenous-behavior claim.

No conflict with the accepted roster or semantic skeleton was found.

## Carrier preflight

| Interface family | Classification | Reason for later consolidated review |
|---|---|---|
| population participant class | `KNOWN_FIT` | Contracts V1 already recognizes `aggregate_population_agent` |
| weighted choice-unit identity and composition | `MAPPING_EXTENSION_EXPECTED` | later mapping must choose separate synthetic participants or an aggregate carrier with explicit unit/weight identity; R1 does not choose |
| delivered observation and forbidden-information boundary | `KNOWN_FIT` at contract level | V1 supports participant information boundaries and referenced observations; new depositor domains still need registry entries after release |
| response profile, tie rule, and private state | `MAPPING_EXTENSION_EXPECTED` | behaviorally material state can use existing profile/state carriers, but the released roster must choose one authoritative projection |
| withdrawal request | `KNOWN_FIT` at contract level | `ActionIntent` already carries target, parameters, resource request, observations, authority references, expiry, and idempotency; a new semantic intent definition is still required later |
| retention and awaiting decisions | `KNOWN_FIT` | `DecisionRecord` permits a decision with no action or message intent |
| request lifecycle and paid/partial/delayed/failed result | `MAPPING_EXTENSION_EXPECTED` | V1 has action dispositions and environment process state, but the depositor business lifecycle and exact reason mapping are not yet registered |
| requested-demand aggregation | `MAPPING_EXTENSION_EXPECTED` | aggregation must retain unit weights, original requests, admitted demand, and realized payment without double counting |
| trace and causal lineage | `KNOWN_FIT` at contract level | V1 traces observations, decisions, intents, dispositions, state transitions, and causal parents; cohort-level observability still depends on the chosen mapping |

## Preflight conclusion

`NO_CONCRETE_CARRIER_COUNTEREXAMPLE`

The current carrier has plausible paths for the released semantics. The first
population model adds real consolidated-mapping work—especially weighted unit
identity, aggregation, and the withdrawal lifecycle—but does not justify a
Contract change before the full Roster Definition release. No field, registry,
binding hash, implementation, or test is created in R1.
