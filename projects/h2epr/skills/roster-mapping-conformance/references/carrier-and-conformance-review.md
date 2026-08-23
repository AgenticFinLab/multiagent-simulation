# Carrier and conformance review

Use this reference to review an H2EPR consolidated mapping or bounded
conformance implementation. The mapping is derived: it must preserve released
semantics without becoming a second Agent, scenario, or contract authority.

## Design review

### Release integrity

- Are manifest, local checksum inventory, paths, semantic product hashes, and
  owner decisions verified through their declared identities?
- Are all products included exactly once and all release counts derived rather
  than copied?
- Does every mapping artifact identify the release and contract versions it
  consumed?

### Identity and assembly

- Are entity, actor, population unit, host, capability, Definition,
  commitment, business object, observation, intent, message, and result
  identities distinct?
- Does one entity retain one actor, authority graph, relationship set, and
  resource owner across capabilities?
- Do repeated reader-facing labels receive unambiguous capability-qualified
  identities?
- Can a population unit be resolved without borrowing another unit's private
  state or resources?

### Information and state

- Does every observation pass Definition, scenario, evidence/time, and carrier
  admission?
- Are value, source object/version, event/as-of time, availability, freshness,
  visibility/scope, uncertainty, provenance, and consumers preserved where
  material?
- Are compound fields cross-version checked?
- Are participant decision state and business truth separate, versioned, and
  replayable?

### Intent, message, and lifecycle

- Does every released intent placement have one semantic mapping or an
  explicit no-runtime disposition?
- Are parameters defined without duplicating top-level carrier values?
- Are authority, target, relationship, resource, timing, expiry, and
  idempotency checked?
- Are action intent, message staging, transport, delivery, acceptance,
  execution, result, and later observation distinct?
- Do multi-hop and revised business objects preserve lineage and versions?
- Are no-intent, invalid, duplicate, expired, partial, failed, withdrawn, and
  reversed paths representable?

### Authority, resources, and results

- Is every grant scoped and tied to an authoritative record and interval?
- Is an empty scope treated as empty rather than universal?
- Does every resource have one owner and one authoritative ledger?
- Are proposal, reservation, commitment, transfer, effect, failure, and
  release distinct?
- Does only the reducer commit result and world-state change?
- Does trace retain invalid attempts and the complete causal chain?

### Carrier decision

- Under Contracts V1, is every requirement classified as `V1_DIRECT`,
  `V1_INTERNAL_MAPPING`, `SCENARIO_SEMANTIC_EXTENSION`, or
  `CONCRETE_SUCCESSOR_COUNTEREXAMPLE`?
- Is a proposed successor based on a reproducible loss rather than preferred
  design style?
- Were flat projections, namespacing, stable references plus atomic fields,
  validators, and event-owned state considered before a contract change?
- Does the review state migration and compatibility consequences?
- Are currently representable risks recorded separately as
  `NARROW_SUCCESSOR_WATCHPOINT` rather than promoted to a carrier failure?

### Candidate and promotion package

- Does the mutable candidate contain a fixed semantic inventory, mapping
  specification, carrier review, substantive review, and one authoritative set
  of cross-object rules?
- Are owner-decision items explicit before promotion?
- Does atomic promotion add a README, manifest, checksum inventory, and owner
  decision without changing semantic content?
- Do manifest counts derive from the pinned products rather than copied prose?
- Can every release-local checksum be verified from its owning directory after
  promotion?

## Conformance implementation review

- Does the loader reject drift in every referenced release and mapping asset?
- Are inventories derived from source products, including multi-digit IDs and
  repeated labels?
- Does the fixture identify the full entity/unit/capability composition it
  claims to test?
- Are positive and negative cases present for multi-capability ownership,
  population scope, compound observations, authority, resources, lifecycle,
  result separation, idempotency, and replay as applicable?
- Does any implementation-only default, synonym, threshold, action, memory, or
  repair change released meaning?
- Are error diagnostics precise enough to route a failure to its owning layer?
- Do focused, import/contract, and full regression tests pass from an isolated
  source checkout?
- Are policy, simulation, scientific validity, and contract-change claims
  withheld when outside scope?

## Verdict

Use one of:

- `PASS_DESIGN_FOR_OWNER_REVIEW`;
- `PASS_BOUNDED_CONFORMANCE_SCOPE`;
- `RETURN_TO_MAPPING`;
- `RETURN_TO_RELEASE_OR_SCENARIO`; or
- `BLOCKED_BY_CONCRETE_CARRIER_COUNTEREXAMPLE`.

List any remaining watchpoint separately. A watchpoint is not a successor
requirement until a reproducible implementation or scenario case demonstrates
the loss.
