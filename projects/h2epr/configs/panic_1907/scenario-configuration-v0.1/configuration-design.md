# H2EPR-0288 Scenario Configuration v0.1

- Version: `0.1.0`
- Purpose: mechanism coverage before bounded implementation
- Status: accepted non-executable configuration
- Historical calibration or validation: none

## 1. Configuration decision

The first configuration should not be called a historical baseline. The
available evidence supports event order, institutional identities, several
relationships and dated information products, but it does not identify exact
opening resources, population composition, private needs, named-bank
policies, service capacities or market allocation rules. Choosing those values
to reproduce the known panic would turn exposed outcomes into hidden policy.

This configuration therefore has a narrower purpose: assemble every released
semantic product once, exercise the important causal interfaces, and expose
the assumptions that a later bounded implementation must carry. The accepted
conservative structural interpretations are the baseline. Unidentified
participant profiles and quantities remain explicit construction
sensitivities.

The old `rule_canary_v1.json` and `compiler_canary_v1.json` remain frozen
engineering references. Their actor scope, 21 October start, 30 November end
and demo assumptions are not inherited here.

## 2. Clock and analytic horizon

The configuration begins on 18 October, uses 21–26 October as the primary causal
window, and closes at the end of 2 November New York local time. The last date
is a declared research construction assumption: it gives the later facility
and unresolved business objects one week of follow-through while staying
inside the accepted early-November boundary. It is not a historical claim
that the crisis, any institution or any market process ended then.

The clock is event-driven and partially ordered. Source-supported exact times
remain exact. Date-only or bounded evidence remains a window. Within a
decision barrier, all actors see projections from one frozen prestate; results
are delivered only in a later barrier. A stable event-ID order resolves only
otherwise unordered equal-time commits. It may not override a causal edge or
manufacture intraday sequence.

## 3. Structural baseline

| Identity | Baseline selection | Interpretation |
|---|---|---|
| `SV-NYCH-ROUTE` | `NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE` | no unproven focal alternative route is created; member-facility restriction remains fixed |
| `SV-NBC-DIRECTION` | `NO_NYCH_DIRECTION_DELIVERED` | NBC receives no invented NYCH instruction; its own and externally directed authority branches remain distinguishable |
| `SV-TPC-RECOMMENDATION` | `PROCEDURE_CONSERVATIVE` | the committee follows its bounded information and mandate gates without an inferred continuity-support preference |
| `SV-POOL-OWNERSHIP` | `INDEPENDENT_RESOURCE_OWNERS` | coordinators never become owners of contributor resources |
| `SV-MORGAN-ATTRIBUTION` | `NAMED_PERSONAL_COORDINATION` | Morgan acts only through the accepted personal coordination interface |
| `SV-MORGAN-RELATIONSHIP` | `RELATIONSHIP_HISTORY_DISABLED` | no prestige, closeness or inferred relationship score affects decisions |
| `SV-FACILITY` | `LATER_RULES_AVAILABLE_ONLY_AFTER_ACTIVATION` | certificate rules cannot appear before their dated activation |
| `SV-VENUE` | `CONSERVATIVE_RECORDED_ROUTE_AND_SETTLEMENT` | NYSE processes route and settle explicit objects but do not supply participant policy |

Changing one of these entries produces a different configuration identity. A
sensitivity run cannot replace the baseline after inspecting its output.

## 4. Actor and population assembly

### Named decision interfaces

The configuration instantiates the seven released named interfaces exactly
once: Knickerbocker Trust, NYCH, National Bank of Commerce, J. Pierpont
Morgan, Trust Company of America, Lincoln Trust Company and the trust-company
presidents' committee. Each has one entity, actor, ParticipantArtifact,
authority graph and canonical resource owner. NYCH, Morgan and the committee
have no direct transferable-resource capability in this release; retaining an
entity-level resource-owner identity prevents another actor from silently
claiming their resources.

### Population units

| Units | Purpose | Assignment status |
|---|---|---|
| two Knickerbocker depositor units | compare ordinary immediate need with delivered-signal response | equal weight and normalized claim are synthetic mechanism-coverage choices |
| two TCA depositor units | compare ordinary need with host-signal response | synthetic; no claim about population shares |
| two Lincoln depositor units | compare ordinary need with contagion/access response | synthetic; no claim about population shares |
| `member_bank_alpha` | compose bank-resource and call-lender capabilities under one actor and one balance-sheet owner | synthetic institution-preserving unit |
| `correspondent_bank_beta` | retain a second independent resource owner and relationship-conditioned response | synthetic sensitivity unit, not a named historical bank |
| `broker_alpha` | exercise a complete call-loan funding lifecycle | synthetic institution-preserving unit |

The assembly has 16 actors and 10 population-unit capability instances. This
is deliberately smaller than a full posture factorial. It includes all 12
released semantic products, host scoping, heterogeneous depositor response,
two independent bank owners, one composed bank/lender actor and one broker.
Unused posture alternatives remain overlays instead of being multiplied into
an artificial historical population.

The population weights are all one and depositor claims are one normalized
claim share. These values make identity and aggregation visible; they do not
estimate account counts, balances, withdrawal totals or historical shares.
All six depositor units open with no active private need. The three
`*.need` units receive an `immediate` private need only when the dated
`exo.synthetic_private_need_activations` input is delivered during its
22--23 October window. The three signal-response units receive no private-need
activation in the baseline. This keeps a configured response profile distinct
from an already-active decision situation.

## 5. Opening records

The opening state uses only sourced categorical relations or visibly labeled
construction records:

- the KT–NBC clearing/correspondent relation is active before an authoritative
  notice/effective change, while its exact focal contract classification
  remains disputed;
- NBC is a NYCH member and Knickerbocker is not;
- `member_bank_alpha` is a synthetic NYCH member, while
  `correspondent_bank_beta` is a synthetic nonmember;
- each depositor claim is bound to exactly one host and unit;
- `member_bank_alpha` and `broker_alpha` share one explicitly synthetic active
  call-loan object so the funding lifecycle can be exercised; and
- the committee and Lincoln's communication authority remain inactive until
  their dated exogenous authority records are delivered.

Opening resources are qualitative envelopes: `constrained`,
`bounded_available`, `partial` or `unknown`. Unknown never means zero or
unlimited. No arithmetic across qualitative envelopes is permitted. Exact
numeric liquidity, collateral, capacity and service values are intentionally
not supplied by this configuration and may not be invented by a backend.

## 6. Exogenous inputs

The configuration admits only boundary events whose autonomous producer is outside
the released roster or whose content is already an accepted dated information
input:

1. pre-boundary affiliated-bank distress initializes dated information and
   relationships, but chooses no participant action;
2. the 21 October focal opportunity activates KT, NBC and NYCH decision
   situations without injecting a request, refusal or clearing decision;
3. the 22 October contradictory public signal set can be delivered to
   configured recipients without becoming world truth;
4. synthetic private-need events activate only the declared need-response
   units;
5. the wider presidents' forum constitutes the committee on 23 October but
   supplies no committee policy;
6. the Lincoln board authority record is delivered on 25 October, while issue,
   transport, truth and effect remain separate;
7. the member-only certificate facility becomes available on 26 October but
   creates no application or certificate; and
8. the NYSE calendar and loan stand expose routes and settlement opportunities
   without choosing lender or borrower behavior.

The Treasury public-deposit input is omitted in the baseline. Including it
requires a separately pinned dated overlay and creates a different exact
configuration identity.

## 7. Selected scenario policies

All policy names below are configuration semantics. Their implementations are
currently unbound, so the configuration must fail closed if presented to a runner.

### Time and information

`POL-TIME-01` preserves explicit predecessor edges and bounded event windows;
stable ID ordering is only a final deterministic tie-break. `POL-INFO-01`
separates production, issue, route, delivery, freshness, correction and
supersession. Public issue does not imply universal receipt. A compound
observation is unavailable when its component versions are incoherent.

### Service and queue

`POL-SERVICE-01` uses a host-local FIFO queue by admitted request event time,
with stable request ID only for a true tie. Partial service is permitted and
must return its realized form and amount. The policy is a transparent
construction choice, not a claim about the exact historical queue. A request
cannot reduce a claim; only a realized paid result can do so.

### Review and classification

`POL-REVIEW-01` classifies delivered packages as complete,
conditionally complete, incomplete or disputed against the declared case
requirements. It has no numerical score and no hidden solvency classification.
Membership, authority, route and information sufficiency remain separate
tests. Missing or disputed material information yields a typed request,
condition, blocker or abstention rather than backend inference.

### Amount, facility and venue

`POL-AMOUNT-01` permits only a qualitative bounded band against the resource
owner's delivered envelope. It never auto-fills a known historical target or
allocates another owner's resources. `POL-FACILITY-01` enables member
applications only after dated activation; application, collateral review,
issue and resource effect remain different events.

`POL-VENUE-01` requires an explicit request, offer, compatibility result,
match, booking, transfer and settlement chain. A pool announcement is not an
offer, a match or funding. The venue never creates a participant's willingness,
call right, capacity or position-reduction policy.

### Lifecycle and result

`POL-LIFECYCLE-01` revisits an object only on a declared delivery, state change,
deadline or phase opportunity. At the horizon, an unresolved object is either
terminal or carried forward with owner, state, version, reason and next event.
`POL-RESULT-01` keeps admissibility, scheduling, execution, partial effect,
no-effect, failure and later result delivery distinct. An adapter may not
silently clamp or repair an invalid intent.

## 8. Predeclared sensitivity space

The machine configuration records bounded overlays for the alternative NYCH
route, NBC direction provenance, committee recommendation posture, depositor
conflict rule, bank participation, call-market support, Treasury input and
analytic horizon. Each overlay must be materialized before execution, assigned
its own exact hash and run identity, and reported as an unvalidated structural
or construction sensitivity.

Every overlay operation names its target kind, exact target ID, field and new
value. Population sensitivities point to capability-unit IDs rather than bare
actor names, so composition under one actor cannot redirect a change to the
wrong capability surface.

This list is not permission to perform a full factorial sweep. A run set must
state which scientific or carrier question each comparison answers.

## 9. Execution boundary and first implementation implication

This configuration is complete enough to review configuration ownership but not
to run. Exact numeric carrier values, policy implementations, loader identity
and runtime projection are deliberately absent. A backend may not supply them
as defaults.

If separately authorized, the smallest useful implementation slice is the
KT → NBC → NYCH request lineage:

1. load and hash the fixed release and configuration;
2. assemble the three named actors without adding behavior;
3. produce only legal actor-specific observations;
4. carry request authorization, forwarding, receipt, review, disposition and
   communicated result as separate objects/events; and
5. prove deterministic replay and fail-closed behavior.

Population service and the broker funding lifecycle should enter later bounded
slices. The full 16-actor configuration is the integration target, not the
first coding unit.

## 10. Accepted owner decisions

The project owner accepted `OD-CFG-01` through `OD-CFG-04` on 23 August
2026. [ADR-0006](../../../decisions/ADR-0006-panic-1907-scenario-configuration-boundary.md)
records the controlling boundary.

### `OD-CFG-01` — purpose and horizon

The mechanism-coverage purpose is accepted with an 18 October start, a 21–26
October primary window, and a 2 November analytic horizon. The horizon is a
construction choice, not a historical end date.

### `OD-CFG-02` — assembly

The accepted assembly contains 7 named actors, 6 host-scoped depositor units,
2 independent bank actors, and 1 broker actor. `member_bank_alpha` is the one
actor that composes bank-resource and call-lender capabilities under one
resource owner.

### `OD-CFG-03` — baseline and sensitivities

The eight conservative structural selections are accepted as the baseline.
Population profiles and qualitative opening envelopes remain
mechanism-coverage assumptions only; they are not historically representative
or calibrated. Every sensitivity overlay requires a new exact configuration
identity before use.

### `OD-CFG-04` — non-executable release boundary

Configuration semantics are accepted without hidden numeric defaults.
Execution remains ineligible until a separately reviewed implementation
binding supplies policy identities, exact carrier projections, and fail-closed
loader checks. If separately authorized, implementation begins with the
three-role KT–NBC–NYCH lineage rather than the full roster.
