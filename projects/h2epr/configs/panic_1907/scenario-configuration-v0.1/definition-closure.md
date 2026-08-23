# H2EPR-0288 configuration-to-Definition closure

- Configuration: `h2epr.0288.scenario.mechanism-coverage.v0_1`
- Configuration version: `0.1.0`
- Definition authority: `H2EPR-0288-EVENT-SCENARIO-DEFINITION-v0.1`
- Closure status: `CLOSED_ACCEPTED_NON_EXECUTABLE`
- Historical calibration or validation: `NONE`

## 1. Closure rule

This check asks whether the configuration instantiates every configuration-owned
family in the accepted Event Scenario Definition without adding participant
behavior, institutional authority, world meaning, a machine contract, or the
known historical outcome. It does not ask whether a runtime can execute the
configuration. Unbound policy implementations, exact carrier projections, and a
fail-closed loader remain later implementation responsibilities.

## 2. Input identity

The configuration's seven recorded SHA-256 inputs match the current bytes of the
accepted Scenario Definition release, Scenario Definition, Roster Definition
release, consolidated mapping release, mapping profile, evidence ledger, and
source register. The accepted Scenario interface closure remains separately pinned by the
configuration release manifest.

The old `rule_canary_v1.json` and `compiler_canary_v1.json` are not semantic
inputs. No field, date, actor set, quantity, or policy is inherited from them.

## 3. Definition configuration-family closure

| Definition family | Configuration carrier | Closure | Boundary retained |
|---|---|---|---|
| temporal window and order | `clock`, dated `exogenous_inputs`, `POL-TIME-01` | closed | bounded dates remain windows; stable ID is only a residual tie-break |
| resource, claim, and exposure | depositor claims, qualitative opening projections, one call-loan object, `POL-AMOUNT-01` | closed | unknown is not zero or unlimited; no unsupported arithmetic or historical amount |
| population composition | six host-scoped depositor units, two bank units, one lender capability unit, one broker unit | closed | all weights, normalized claims, profiles, and postures are synthetic mechanism-coverage choices |
| authority and relationship | actor authority-graph identities plus opening authority and relationship records | closed | title, urgency, routing, or coordinator identity cannot create authority or resource ownership |
| information coverage and delay | dated information inputs, delivery language, `POL-INFO-01` | closed | issue is not receipt; recipient scope, freshness, correction, and version coherence remain required |
| service and queue | `POL-SERVICE-01` | closed | host-local FIFO and partial service are transparent construction choices, not historical claims |
| review and classification | `POL-REVIEW-01` | closed | no hidden score, solvency inference, or outcome-conditioned classification |
| proposal and commitment amount | qualitative participant postures plus `POL-AMOUNT-01` | closed | no automatic target allocation or use of another owner's envelope |
| facility and venue | dated facility and NYSE inputs, `POL-FACILITY-01`, `POL-VENUE-01` | closed | later rules are not back-projected; venue never supplies participant willingness or policy |
| horizon and revisit | analytic horizon, `POL-LIFECYCLE-01`, `completion_policy` | closed | unresolved objects carry owner, state, version, reason, and next event or fail closed |

## 4. Assembly and causal ownership

The configuration covers all 12 released semantic products through 16 unique
actors:

- 7 named institutional or personal decision interfaces;
- 6 depositor population actors, each scoped to one host;
- 2 independent bank actors; and
- 1 broker-borrower actor.

There are 10 population capability units. `member_bank_alpha` composes
`bank_resource_decision` and `call_money_lender` under one actor, entity,
ParticipantArtifact, authority graph, and resource owner. All actor IDs,
entity IDs, ParticipantArtifact IDs, authority-graph IDs, and unit IDs are
unique. Every unit references an actor that carries its declared capability.
Every opening relationship, resource record, and business object resolves to
a configured entity or actor.

## 5. Private inputs and decision activation

All six depositor units open with `opening_private_need = none`. Only these
three units are targets of `exo.synthetic_private_need_activations`:

- `unit.depositor.knickerbocker.need`;
- `unit.depositor.tca.need`; and
- `unit.depositor.lincoln.need`.

Their need changes to `immediate` only when the dated input is delivered in
the 22--23 October window. The three signal-response units receive no private
need activation in the baseline. This closes the prior ambiguity between a
configured response profile and an already-active opening decision.

## 6. Exogenous-input boundary

The nine input records have unique IDs and all set `outcome_forcing` to
`false`. They initialize or deliver only the accepted boundary information,
opportunity, private need, committee mandate, board authority, later facility,
Treasury omission, and venue availability. Referenced claim IDs are present
in the accepted evidence ledger.

None of these inputs supplies a participant request, disposition, commitment,
application, certificate, match, transfer, settlement, suspension, rescue, or
other known result. The Treasury input remains omitted in the baseline.

## 7. Policies, structural selections, and sensitivities

The configuration selects nine scenario policies. Every policy has
`implementation_status = unbound`, and the top-level execution boundary is
`execution_eligible = false`. Presenting this configuration to a runner therefore
must fail closed.

Eight conservative structural selections are pinned in the base identity.
Eight optional overlays are predeclared. Each overlay operation now records an
exact target kind, target ID, field, and value. Population changes address the
capability unit rather than the composed actor, preventing a sensitivity from
silently changing the wrong capability surface. An overlay remains unusable
until it is materialized with concrete values and a new exact configuration
identity.

## 8. Mapping and reproducibility coverage

The configuration copies the accepted full-Roster coverage expectations without
changing their meaning:

| Measure | Expected |
|---|---:|
| semantic products | 12 |
| observation placements | 115 |
| intent placements | 107 |
| named actors | 7 |
| population actors | 9 |
| population capability units | 10 |

These counts are interface expectations, not evidence that runtime
projection has occurred. Exact configuration hash, policy implementation
identity, carrier projection, backend identity, seed/random sources, and run
identity remain required before execution.

## 9. Residual routing

No configuration-to-Definition semantic gap blocks the accepted semantic
configuration. The following work remains deliberately outside this configuration:

1. bind exact, versioned implementations for all nine selected policies;
2. define and validate an exact carrier projection without inventing numeric
   defaults for qualitative envelopes;
3. implement a fail-closed configuration loader and cross-object checks;
4. materialize any selected sensitivity overlay before inspecting outcomes;
5. obtain separate authorization for a bounded implementation slice; and
6. defer simulation and historical-validity claims to their own reviewed
   stages.

If implementation exposes a reproducible mismatch, route it to configuration,
implementation, mapping, Scenario Definition, Roster/evidence, or Contracts
according to the actual semantic owner. Do not repair it by silently changing
an accepted input or backend default.
