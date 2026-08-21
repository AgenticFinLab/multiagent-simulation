# National Bank of Commerce interface preflight

| Item | Value |
|---|---|
| Status | accepted preflight for Roster Definition release |
| Event | `H2EPR-0288` |
| Roster | `v0.4` |
| Semantic skeleton | `v0.1` |
| Product | NBC Agent Definition `0.1.0` |

## Purpose

This note preserves the accepted read-only Definition-to-binding impact review
as a release-level interface preflight. It inventories NBC's semantic surface
without extending the two-role binding, choosing machine fields, implementing
policy or modifying Contracts V1.

## Semantic surface

NBC contributes four Decision Commitments, twelve observation concepts, three
private decision-state families and fifteen semantic intents covering:

- institution, authority and clearing/correspondent relationships;
- dated credit and clearing exposure records;
- counterparty condition and a delivered support request;
- NBC-legible review notices and legal/authority assessments;
- credit continuation, conditioning or limitation;
- request forwarding, sponsorship, representation or decline;
- clearing continuation, condition, termination notice and communication; and
- adaptation to delivered request, notice, credit and relationship results.

NBC does not own Knickerbocker policy, NYCH procedure, notice transport,
relationship effect, booked credit, repayment or realized loss.

## Required consolidated-mapping work

| Interface family | Classification | Required treatment |
|---|---|---|
| NBC participant identity and Definition hash | `KNOWN_FIT` | bind NBC as endogenous only in the consolidated profile; retain the two-role reference profile unchanged |
| dated compound observations | `MAPPING_EXTENSION_EXPECTED` | project every behaviorally consumed attribute with source, time, scope and provenance; stable IDs may not hide world dereference |
| private review/intermediation/communication postures | `KNOWN_FIT_WITH_INTERNAL_MAPPING` | reducer-committed actor-private state linked to authoritative records, never backend-private memory |
| fifteen action/message intents | `KNOWN_FIT_WITH_INTERNAL_MAPPING` | define parameter, target, authority, lifecycle, idempotency and forbidden-result rules before implementation |
| KT → NBC → NYCH request lineage | `MAPPING_EXTENSION_EXPECTED` | delivery to NBC must not create final-recipient delivery or an NYCH case; preserve hop and sponsorship provenance |
| credit lifecycle | `MAPPING_EXTENSION_EXPECTED` | separate proposal, authorization, booking, partial result, repayment and loss |
| clearing relation and notice lifecycle | `MAPPING_EXTENSION_EXPECTED` | separate decision, issue, fanout, delivery, remaining obligations and effective relationship change |
| structural alternatives | `KNOWN_FIT_WITH_INTERNAL_MAPPING` | pin NBC termination provenance and NYCH route interpretation in scenario/run identity; never expose research labels to policy |
| trace and replay | `KNOWN_FIT` | retain observation, request-hop, notice, relationship, result and state-version causal references |

## Required cross-object checks

1. NBC sees only dated records and delivered directions available to it.
2. Forwarding, sponsorship and representation cite the original request and
   preserve sender, recipient and mandate lineage.
3. Delivery to an intermediary is not delivery to the final recipient.
4. NBC cannot create NYCH authority, Knickerbocker authorization or a booked
   credit/result effect.
5. Notice issue, transport, delivery and effective relationship change remain
   separate.
6. Bank-initiated, committee-directed and disputed termination provenance are
   run-pinned alternatives, not historically validated participant traits.

## Preflight conclusion

`NO_CONCRETE_V1_CARRIER_COUNTEREXAMPLE`

NBC requires a consolidated mapping-profile extension for compound
observations, route hops and credit/clearing lifecycles. The reviewed semantics
do not justify a Contracts V1 successor before implementation demonstrates an
irreducible carrier failure.
