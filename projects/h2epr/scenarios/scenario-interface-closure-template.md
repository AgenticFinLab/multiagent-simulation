# H2EPR Scenario Interface Closure Template

> Status: working derived companion · release-wide · non-behavioral

This companion demonstrates that an Event Scenario Definition can supply and
adjudicate the complete interface of an accepted participant release. It is a
reconciliation record, not a second source of participant behavior, historical
evidence, scenario meaning, or machine-contract semantics.

Use released semantic identifiers unchanged. When several capabilities reuse a
reader-facing label, qualify the placement by capability rather than renaming
the released concept. Derive counts from the pinned release and mapping; do not
maintain a hand-copied total.

## 1. Closure identity and inputs

| Field | Value |
|---|---|
| Event and scenario identity | `<event ID; Scenario Definition ID/version>` |
| Participant semantic input | `<Roster Definition release or exact reviewed product set>` |
| Evidence/time boundary | `<ledger/use-partition identity>` |
| Consolidated mapping | `<accepted mapping identity/version, when available>` |
| Interface contract | `<applicable contract family/version>` |
| Structural baseline and variants | `<immutable system-only identities>` |
| Review state | `<mutable candidate / owner-reviewed / accepted>` |

Record the expected and derived counts for products, capabilities, actor or
population units, observations, private-state families, intents/messages,
business lifecycles, and cross-object rules. Any mismatch is a closure failure,
not a documentation rounding issue.

## 2. Participant and capability assembly

| Entity or unit | Capability/product | Decision interface | Host or institution | Authority owner | Resource owner | Closure status |
|---|---|---|---|---|---|---|
| `<stable entity/unit>` | `<released capability>` | `<actor or scoped population unit>` | `<host or none>` | `<authoritative record>` | `<one ledger owner>` | `<closed/gap>` |

Check that one historical or legal entity is not duplicated merely because it
composes several capabilities. Population units retain distinct host, weight,
private state, observations, authority, and resources.

## 3. Observation production and delivery

Include one row per released observation placement.

| Capability | Observation | Authoritative source/version | Production and projection | Route, scope, and delivery | Time/freshness/missing rule | Scenario concept | Closure status |
|---|---|---|---|---|---|---|---|
| `<capability>` | `<released ID>` | `<record owner>` | `<information product>` | `<eligible recipients>` | `<event/as-of and unavailable behavior>` | `<Scenario Definition reference>` | `<closed/gap>` |

An observation closes only when the Definition permits it, the scenario can
produce and deliver it, the evidence/time boundary permits it, and the accepted
carrier can freeze it without exposing hidden current state.

## 4. Intent, communication, adjudication, and result

Include one row per released intent placement.

| Capability | Intent | Authority and target | Required object/resource/relationship | Lifecycle and idempotency | Adjudication and result owner | Scenario concept | Closure status |
|---|---|---|---|---|---|---|---|
| `<capability>` | `<released ID>` | `<scope and competent authority>` | `<stable dependencies>` | `<business state/duplicate/expiry rule>` | `<environment process and typed result>` | `<Scenario Definition reference>` | `<closed/gap>` |

Keep action creation, message creation, transport, delivery, business
acceptance, execution, result, and later observation distinct. A valid
no-intent decision must not be converted into an invented action.

## 5. Private state and business lifecycles

| State or lifecycle family | Semantic owner | Initial state/basis | Valid transition causes | Version and replay path | Consumers | Closure status |
|---|---|---|---|---|---|---|
| `<family>` | `<participant or environment>` | `<source>` | `<decision/result/time/event>` | `<authoritative record>` | `<capabilities/processes>` | `<closed/gap>` |

Participant decision state and environment-owned business truth must never
become competing copies. Record pending, duplicate, expired, withdrawn,
reopened, partial, failed, and closed paths where the released semantics need
them.

## 6. Institutions, relationships, authority, and resources

| Requirement | Authoritative owner | Scope/effective interval | Invariant or conservation rule | Competing-claim handling | Closure status |
|---|---|---|---|---|---|
| `<membership/relationship/authority/resource>` | `<record/ledger>` | `<bounded scope>` | `<must always hold>` | `<adjudication rule>` | `<closed/gap>` |

Empty or unknown authority grants nothing. A coordinator, committee, venue, or
intermediary does not acquire another participant's resource merely by handling
its request or proposal.

## 7. Structural identity and representative cases

List every structural interpretation that can change admissibility,
information, ownership, routing, or results. Show where the selected value is
pinned outside participant observation.

Exercise a small set of high-information closure cases:

- one multi-capability institution with one actor and resource owner;
- one host-scoped population unit;
- one compound observation with version-coherence rejection;
- one multi-hop request or message;
- one authority or relationship failure;
- one resource proposal, commitment, transfer, and adverse result;
- one duplicate or expired business object; and
- one deterministic replay of the complete causal record.

## 8. Gaps, routing, and verdict

| Gap | Evidence | Owning layer | Required decision or revision | Blocks scenario acceptance? |
|---|---|---|---|---|
| `<gap>` | `<reproducible case>` | `<release/evidence/Definition/scenario/mapping/implementation/contracts>` | `<bounded action>` | `<yes/no>` |

Use one verdict:

- `CLOSED_FOR_OWNER_REVIEW`;
- `RETURN_TO_SCENARIO`;
- `RETURN_TO_MAPPING`;
- `RETURN_TO_RELEASE_OR_EVIDENCE`; or
- `BLOCKED_BY_CONCRETE_CARRIER_COUNTEREXAMPLE`.

Closure means the Scenario Definition and accepted mapping can support the
released participant interface without hidden semantics. It does not authorize
policy implementation or simulation and does not establish historical or
scientific validity.
