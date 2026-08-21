# H2EPR-0288 event semantic skeleton

- Version: `0.1`
- Status: accepted design boundary
- Event roster: [`agents/rosters/panic_1907.md`](../../agents/rosters/panic_1907.md)

This document fixes the shared event language that role batches use while the
full scenario remains under development. It is intentionally non-executable:
it does not set numerical world values, machine fields, policy thresholds, or
historical outcomes.

## Event frame

The modeled interval is the acute New York phase from approximately 18 through
26 October 1907. Its research question and participant dispositions are owned
by the event roster.

The working phase map is:

1. initial affiliated-bank distress and emerging Knickerbocker pressure;
2. National Bank of Commerce credit, request, and clearing-channel decisions;
3. the Knickerbocker run, operational boundary, and immediate information
   effects;
4. contagion to later trust companies and private coordination; and
5. collective trust-company, member-bank, and call-money response.

These phases organize evidence and interactions. They are not a deterministic
event script, and a known later outcome may not be injected into an earlier
Agent observation or policy.

## Sources of authority

| Question | Owner |
|---|---|
| who or what belongs in the event model | roster |
| what a participant represents, can know, remembers, chooses, and intends | Agent Definition or reviewed population model |
| source identity, locator, adopted passages, and custody hash | source register |
| what historical claim is supported, disputed, exposed, participant-available, or assigned an event time | evidence ledger |
| instantiated clock, world state, relationships, resources, delivery, feasibility, and realized results | scenario/environment and authoritative reducer |
| encoding, type, shape, serialization, and version | machine contracts |
| how released semantics are carried by an implementation | consolidated derived mapping |

An Agent emits an intent. The environment decides whether it is admissible and
feasible, and the authoritative reducer records its disposition, result, and
world-state effect. Message creation, delivery, receipt, business acceptance,
and realized effect are distinct events.

## Shared event concepts

Role products may rely on the following common concepts without redefining
them as private policy:

- institutional identity, membership, representation, and authority;
- credit exposure, liquidity resources, collateral, and resource control;
- clearing, correspondent, intermediary, committee, and market relationships;
- public, private, delivered, missing, stale, disputed, and unavailable
  information;
- request, case, review, authorization, proposal, disposition, notice, and
  result;
- operational access, withdrawal pressure, support capacity, and market
  liquidity; and
- event time, delivery time, effective interval, expiry, and causal lineage.

These are semantic families, not a frozen schema. A later mapping may reuse an
existing machine carrier or propose a narrow successor only after showing a
concrete loss.

## Interaction routes

The event model must preserve at least these distinctions:

| Route | Required boundary |
|---|---|
| Knickerbocker → NBC → NYCH support route | delivery to NBC is not delivery to NYCH; forwarding is an NBC choice when NBC is endogenous |
| NBC credit and clearing relation with Knickerbocker | credit, request intermediation, clearing service, and notice are separate lifecycles |
| NYCH review and disposition | membership, facility eligibility, alternative-route authority, resource ownership, and communicated disposition remain distinct |
| depositors ↔ trust companies | withdrawals and access affect resources; institutional communications become observations only when delivered |
| Morgan/private coordination ↔ trusts, banks, and market participants | examination, proposed support, contribution, and realized resource transfer are separate |
| trust-company committee and member institutions | a collective interface does not automatically own member resources or erase disagreement |
| call-money participants and NYSE process | participant lending and borrowing choices are separate from venue matching, collateral, and price mechanics |

## Event-owned state and lifecycles

The scenario owns the authoritative state of relationships, resources,
requests, delivery, procedures, and results. Role Definitions may declare how
an Agent reacts to these states, but may not create their business truth.

At minimum, later scenario design must distinguish:

- request formation, authorization, transmission, receipt, review,
  disposition, communication, expiry, and closure;
- credit availability, extension, adjustment, withdrawal, and notice;
- clearing-service availability, restriction, termination notice, and
  effective termination;
- review or committee initiation, information collection, authorization,
  proposal, and decision;
- resource proposal, reservation, commitment, execution, partial effect,
  failure, and release; and
- observation production, routing, delivery, freshness, and acknowledgement.

The exact state model remains mutable until consolidated mapping. A batch must
not invent a hidden lifecycle merely to make one Definition convenient.

## Fixed structural boundaries

- National Bank of Commerce is an accepted Agent for endogenous credit,
  intermediation, clearing, and notice choices, but is not in the current
  two-role executable baseline.
- The NYCH member-facility restriction is shared by both current structural
  interpretations. `NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE` is the baseline;
  `BOUNDED_ALTERNATIVE_ROUTE_DISCRETION` is a sensitivity variant. The chosen
  interpretation must enter scenario and run identity.
- Treasury public deposits are an explicit exogenous resource input in v0.1.
  The model may study their effects but may not claim to explain the Treasury
  decision.
- United Copper and affiliated-bank distress establish initial history rather
  than an endogenous trigger process.
- Population pressure may not be replaced by a single invented institutional
  personality.

## Lightweight interface preflight

Before a role or population product is accepted into the Roster Definition
release, its batch records one short interface note covering:

1. representation and causal choices;
2. observations and participant-time limits;
3. behaviorally material private state;
4. intents, counterparties, and interaction routes;
5. authority and resource dependencies;
6. lifecycle concepts and expected results;
7. scenario-owned facts or processes it requires; and
8. one of `KNOWN_FIT`, `MAPPING_EXTENSION_EXPECTED`, or
   `CONCRETE_CARRIER_COUNTEREXAMPLE` for each material interface family.

This preflight detects incompatible vocabulary, duplicate ownership, and an
obvious carrier problem. It does not assign wire fields, create registries,
pin executable hashes, implement policies, or run conformance tests.

## Consolidated mapping entry

Consolidated mapping begins only after Roster Definition release v0.1. It maps
the released Agent, population, scenario, interaction, and lifecycle semantics
as one system. Mapping may then revise internal profiles or present a narrow
contract-successor case, but it may not add behavior or historical knowledge
that was absent from the release.
