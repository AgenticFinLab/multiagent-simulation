# Bounded lineage conformance

Use this reference only when a separately authorized conformance task names
one exact, accepted mapping/binding release and one small multi-hop lineage.
It records the E6--E7 method learned from the H2EPR-0288 KT--NBC--NYCH case;
it does not authorize a broader runtime or replace scenario configuration,
policy, or scientific-evaluation methods.

## Entry declaration

Record before implementation:

- the externally supplied raw manifest hash and every frozen implementation
  surface it pins;
- the admitted Scenario Configuration identity and its execution boundary;
- exact actors, actions, routes, policy implementations, positive branches,
  and logical horizon in scope;
- the high-information cross-object risks that justify the slice;
- allowed new code, tests, closeout records, and verification commands; and
- explicit exclusions, including all other actors or policies, a simulator,
  calibration, evaluation, and validity claims.

Do not modify a frozen E6 surface during E7 unless an adversarial case proves
a real defect. If it does, return to E6 review and issue a new identity rather
than silently refreshing hashes from E7.

## Select the smallest causal lineage

A bounded lineage contains only enough hops to expose the target invariant.
Prefer one original sender, any indispensable carrier, one adjudicator, and
the return route. Name excluded actors and policy families explicitly.

Fix the positive branch in advance. Unsupported participant branches must
fail closed; E7 is not an invitation to implement every valid behavior in a
Definition. A fixture may be fully exposed and synthetic when labeled as
conformance-only and barred from historical or scientific claims.

## Validate two distinct layers

First validate each projected observation, action, message, authority scope,
route, and parameter against its accepted carrier contract. Then validate the
relationships that no single carrier object can prove:

- downstream decisions consume the exact message actually delivered on the
  preceding hop;
- an intermediary preserves original object identity, version, content hash,
  mandate, represented sender, and its own limited role;
- the adjudicator classifies the same request and does not borrow a later
  facility, broader authority, or unrelated route;
- the return disposition preserves case and request lineage and its declared
  scope; and
- action admission, business disposition, resource effect, and result
  delivery remain separate.

A well-formed carrier object with wrong cross-hop provenance is a required
negative. Per-object schema validation alone cannot close a multi-hop lineage.

## Record one deterministic conformance trace

Use the repository's existing domain-neutral trace, canonical hashing, tick
seal, run seal, and replay primitives. A fixed conformance runner may call the
accepted projections and policies directly; it need not start MASim, Ray, an
actor scheduler, or a full scenario runtime.

Keep trace state minimal. Persist only state that is required to establish
ordering, result separation, or replay. Do not copy every semantic field into
runtime state merely because it exists in an action or message. The trace
must still expose observations, decisions, intents, route adjudication,
deliveries, dispositions, state deltas, and the final result layers.

The conformance manifest should pin the E6 release, implementation identity,
actors, actions, tick count, exposure, simulation flag, execution boundary,
and validity-claim boundary. Repeated construction from identical inputs must
produce identical manifest, record chain, seals, final state, and replayed
state.

Do not call a project-local trace envelope a complete Contracts V1
`TraceRecord` unless it validates that contract. Validate V1 payloads at their
actual carrier boundaries and state the trace-envelope level precisely.

## Choose high-information negatives

Cover the accepted cross-object rules touched by the lineage, not a Cartesian
product of every field. Normally include:

1. external manifest or frozen-surface drift;
2. direct-route bypass or borrowed authority;
3. a validly shaped intermediary object with drifted provenance;
4. downstream activation before or against exact delivery;
5. wrong but well-formed delivered-message or business-object reference;
6. a dated institutional rule incorrectly back-projected into the focal time;
7. conflation of action acceptance, business result, resource effect, and
   delivery; and
8. trace mutation plus replay from an incorrect prestate.

Add another negative only when it protects a distinct accepted invariant or
routes a failure to a different owner. Do not implement unused policy branches
solely to create more tests.

## Close E7 and audit depth

Produce one concise implementation review and one machine-readable expected
vector or receipt. The receipt should make the exact binding hash, conformance
implementation hash, run-manifest hash, record count, tick/run seals, final
state hash, replay hash, deterministic-repeat result, and claim boundary
recoverable. A full trace file need not be tracked when the runner reproduces
it exactly and tests compare the receipt.

Before closing, verify and report:

- focused negative and trace/replay tests, relevant contract/import tests, and
  the owning regression suite;
- all E5 and E6 protected hashes remain unchanged;
- actor, action, route, policy, branch, and tick inventories did not widen;
- no simulator, full-event loop, calibration, evaluation, held-out protocol,
  or validity claim entered the implementation; and
- each code or document surface serves a named conformance invariant.

Use `PASS_BOUNDED_LINEAGE_CONFORMANCE` only when these checks pass. Otherwise
use `RETURN_TO_E6_BINDING`, `RETURN_TO_MAPPING_OR_SCENARIO`, or
`BLOCKED_BY_AUTHORIZATION_SCOPE` and name the owning layer.

After a pass, prefer forward-testing the method on a second event. Deepening
the first event requires a new question and authorization; it is not part of
method closeout.
