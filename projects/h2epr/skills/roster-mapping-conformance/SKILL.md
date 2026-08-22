---
name: h2epr-roster-mapping-conformance
description: Derive and review an H2EPR release-wide semantic mapping, carrier decision, and bounded conformance profile from a fixed Roster Definition release. Use after participant production closes to map identities, capabilities, observations, private state, intents, messages, lifecycles, authority, resources, results, and replay without adding behavior; implementation and simulation require separate authorization.
---

# Roster mapping and conformance

> Method status: working candidate extracted from the accepted H2EPR-0288
> consolidated mapping and bounded loader/conformance use case.

Use this Skill after a Roster Definition release has fixed the event's Agent,
population, evidence, skeleton, and interface identities. It maps that semantic
system onto the current carrier and, when separately authorized, verifies the
mapping with a bounded loader/conformance implementation.

This Skill has two modes:

- **Design mode** produces the semantic inventory, mapping specification,
  carrier review, cross-object rules, and substantive review.
- **Conformance mode** implements or extends only the accepted mapping loader,
  derived profile, fixtures, and tests named in the authorization.

Do not enter conformance mode merely because design mode passes. Read
[carrier and conformance review](references/carrier-and-conformance-review.md)
before closing either mode.

Keep the artifact transition explicit:

```text
mutable design candidate
  -> owner decision
  -> separately authorized atomic promotion
  -> separately authorized conformance implementation
```

Design review, formal promotion, and conformance may occur in nearby tasks, but
one does not silently authorize the next. Promotion changes identity and
integrity records only; any semantic revision returns to design review.

## Required inputs

Confirm:

- release manifest, checksum inventory, release identity, and accepted owner
  decisions;
- roster, semantic skeleton or Scenario Definition, evidence authorities,
  Definitions, population products, and interface preflights pinned by the
  release;
- current machine contracts and any accepted reference mapping;
- implementation and scenario surfaces that may be inspected;
- requested mode, authorized mutations, verification scope, and stopping
  point; and
- prohibited work, including policy, simulation, contract change, held-out
  access, or Definition revision unless explicitly included.

If the release is mutable, internally inconsistent, or not byte-identifiable,
stop before mapping. A mapping cannot stabilize an unstable semantic input.

## Design mode

### 1. Verify the release

Recompute the release checksum inventory and every referenced product hash.
Resolve each path relative to one declared project root. Reject missing,
unlisted, duplicate, unsafe, or drifted assets.

Record the exact release and contract versions. Do not silently substitute the
current working file for a pinned release member.

### 2. Build the semantic inventory

Inventory the release before choosing carriers:

- entity, participant, unit, host, capability, and Definition identities;
- commitments and their observation, private-state, and intent dependencies;
- observation meanings, domains, time, visibility, freshness, missing
  behavior, and provenance;
- replayable participant decision state versus environment-owned business
  truth;
- action and message intents, semantic parameters, targets, authority,
  resources, expiry, and prohibited results;
- business-object and communication lifecycles;
- structural variants, exogenous inputs, and scenario-owned mechanics; and
- required trace and run-identity links.

Count placements as well as distinct reader-facing names. Reused labels do not
imply shared identity or meaning.

### 3. Define identity and actor assembly

Map four layers explicitly:

```text
historical/legal entity
  -> runtime actor or population unit
    -> one or more released capabilities
      -> capability-scoped semantic placements
```

One entity has one canonical actor interface, authority graph, relationship
set, and resource owner. Several capabilities may compose into that actor;
they may not create duplicate institutions or balance sheets. Population units
retain host, institution, weight, observations, private state, and resources.

Define stable identities for business objects, observations, commitments,
intents, messages, results, and scenario components. Names that collide across
capabilities must remain unambiguous without changing their reader-facing
labels.

### 4. Map observations and private state

Admit an observation only when:

```text
the released product permits it
AND the scenario can produce it
AND evidence/time policy permits it
AND the carrier preserves its typed frozen projection
```

Map source record, value/domain, as-of and event time, effective interval,
freshness, availability, visibility/scope, uncertainty/dispute, provenance,
and consuming commitments as required. Compound observations need one stable
object/version reference plus separately checked behaviorally material fields;
the reference may not reveal hidden current state.

Every persistent participant state needs one replayable owner, initialization,
legal update event, version, visibility, and consumer. Business lifecycle
truth remains environment-owned.

### 5. Map intents, messages, and lifecycles

Give each placement an unambiguous machine identity while preserving the
released semantic ID. Define its semantic parameters, canonical carrier
precedence, authority, target, relationship, resource, timing, expiry,
idempotency, and result boundary.

Keep action creation, message creation, staging, transport, delivery, receipt,
business acceptance, execution, and result separate. Multi-hop processes must
retain the identities and versions of each business object and hop.

Map lifecycle states and transitions without inventing an action for a valid
no-intent decision. Define duplicate, invalid, delayed, partial, failed,
expired, withdrawn, reversed, and closed paths where released semantics need
them.

### 6. Map authority, resources, results, and trace

Authority is scoped to actor, capability, action, target, resource or
relationship, effective interval, and source record as applicable. Empty
target scope is not a wildcard.

Resources retain owner, controller, category, unit, valuation/as-of,
conditions, reservations, commitments, transfers, releases, and competing
claims. A proposal or accepted intent does not move a resource.

Only the reducer creates authoritative result/state effects. Trace must link
the frozen observation, commitment basis, decision, intent/message,
disposition, result, state delta, and later observation without erasing
invalid attempts.

### 7. Decide carrier fit

Assign every material requirement exactly one disposition:

- `V1_DIRECT` — Contracts V1 represents it directly;
- `V1_INTERNAL_MAPPING` — a profile, registry, validator, or
  namespaced projection is sufficient;
- `SCENARIO_SEMANTIC_EXTENSION` — the carrier fits but the event world/process
  has not yet supplied the meaning; or
- `CONCRETE_SUCCESSOR_COUNTEREXAMPLE` — an irreducible semantic loss remains
  after reasonable mapping alternatives.

When the active carrier is not V1, define the equivalent version-qualified
`<CONTRACT>_DIRECT` and `<CONTRACT>_INTERNAL_MAPPING` labels once in the carrier
review. Record unresolved but currently representable risks separately as
`NARROW_SUCCESSOR_WATCHPOINT`; a watchpoint is not a fifth requirement
disposition and does not justify a contract change.

Do not propose a contract successor for convenience, preferred nesting, or a
missing implementation. State the exact counterexample, failed alternatives,
affected consumer, migration consequence, and smallest possible seam.

### 8. Write cross-object rules and review

Write fail-closed rules covering release integrity, identity/assembly,
information, private state, lifecycle, intent/message, authority, resource,
result, trace, replay, and run identity.

Perform an adversarial substantive review. Test label collisions,
multi-capability entities, host-scoped populations, compound observation
versions, no-intent decisions, multi-hop lineage, conflicting authority,
shared resources, accepted-with-no-effect results, structural variants, and
replay.

Design mode stops with a reviewed mutable candidate and explicit owner-decision
items. After the owner resolves them, a short, separately authorized promotion
revalidates the candidate, records the decision, creates the integrity package,
and makes no semantic edits.

## Conformance mode

Enter only with explicit implementation authorization and an accepted design.

### 1. Implement the smallest derived surface

Build only the release loader, mapping profile, registries, validators,
fixtures, and tests required by the authorized risks. Derive inventories from
the pinned release; do not maintain hand-copied semantic counts or behavior.

Require exact release and mapping identities. Keep policy references
unassigned when policy implementation is not authorized.

### 2. Exercise representative high-risk cases

At minimum, select cases that cover the risks actually present in the release.
Common high-information cases include:

- one entity composing several capabilities while retaining one actor,
  authority graph, and resource owner;
- one host-scoped or institution-preserving population unit;
- a compound observation with cross-version rejection;
- a multi-hop request/message route;
- a scoped authority failure;
- a resource proposal, commitment, and realized transfer kept separate;
- one complete business lifecycle with invalid transitions;
- idempotent duplicate handling; and
- deterministic result separation and replay.

Add negative cases for every accepted cross-object rule touched by the slice.

### 3. Run focused and full verification

Run the smallest focused tests first, then the relevant import/contract suites,
then the full project regression. Record exact commands and results. A green
fixture does not establish policy behavior, scenario validity, or historical
accuracy.

### 4. Route real failures

Return failures to their authority:

| Failure | Owner |
|---|---|
| release/hash/path or semantic inventory mismatch | release process |
| missing or contradictory participant meaning | Definition/population product |
| world, route, delivery, lifecycle, resource, or adjudication gap | scenario |
| carrier projection loss or ambiguous identity | mapping |
| hidden default, copied semantics, nondeterminism, or silent repair | implementation |
| irreducible representation loss | narrow contract-successor review |

Do not edit a frozen Definition or contract simply to make a test pass.

## Outputs

Design mode uses this minimum candidate package unless an established project
convention supplies equivalent names:

1. `semantic-inventory.md` — fixed release inventory and derived counts;
2. `mapping-specification.md` — identity, assembly, observation, state, intent,
   lifecycle, authority, resource, result, trace, and replay mapping;
3. `v1-carrier-review.md` — requirement-level dispositions, watchpoints, and
   smallest demonstrated successor counterexample, if any;
4. `substantive-review.md` — adversarial findings, implementation conditions,
   and owner-decision items; and
5. referenced cross-object conformance rules, kept in the candidate package or
   in one declared authoritative project location.

Atomic promotion additionally produces or finalizes:

1. `README.md` — release identity, scope, files, verification, and next legal
   stage;
2. `manifest.json` — source release, coverage, artifact hashes, accepted owner
   decision, carrier verdict, authorization boundary, and next stage; and
3. `SHA256SUMS` — the manifest, release files, and owner-decision record.

Do not describe a mutable candidate as a mapping release. Do not change
semantic content while calculating promotion hashes.

Authorized conformance mode may additionally produce:

1. exact-hash loader and derived mapping profile;
2. minimal registries/validators and synthetic fixtures;
3. focused and regression test evidence;
4. implementation review and failure-routing record; and
5. a bounded admission verdict.

Neither mode selects a Rule/LLM policy, runs a simulation, or proves scientific
validity unless those actions receive separate scope.

## Stop conditions

Stop and request direction when:

- a release asset fails integrity or the semantic input changes;
- mapping would add behavior, evidence, authority, observation, intent, or
  result meaning;
- actor assembly would duplicate an entity, authority, relationship, private
  state, or resource owner;
- scenario ownership is missing for a required world or lifecycle meaning;
- a concrete carrier counterexample remains after internal alternatives;
- a failure requires Definition, scenario, contract, policy, or simulation
  work outside the authorization; or
- conformance results are being presented as behavioral or historical
  validity.
