# H2EPR-0616 consolidated mapping substantive review

> Accepted substantive review · 25 August 2026 · fixed-input semantic review

## 1. Review conclusion

The reviewed candidate is accepted. It accounts for all nine
released products, 29 decision situations, 62 observation placements, 44
private-state placements, and 54 intent placements without adding a role,
behavior, information route, authority, or historical result.

No Blocking or Major semantic finding remains after candidate revision. The
review supports keeping Contracts V1, adding one event-qualified internal
mapping profile, and requiring the H2EPR-0616 Scenario semantic layer. It does
not authorize a loader, configuration, policy, runtime, or simulation.

## 2. Review scope and tests

| Reviewed candidate object | SHA-256 |
|---|---|
| semantic inventory | `35389ccd929650920b3a515ca7a128b3ae972bcb98baad8ef2a9bee9da12d0d8` |
| mapping specification | `9f4a948a3cde6b3e34cff0a3f1f0c4e6312992a7a1935427debe3e6ff3fca3eb` |
| V1 carrier review | `b5b5fd61a24e295a438441d9f99c6429fe9af3413c017df111399b6973931fe8` |

The mapping review must restart if any of these three objects changes
materially. Formal promotion changes status, owner-resolution, links, and
provenance wording only.

| Review item | Result |
|---|---|
| fixed semantic input is the exact release v0.1 | PASS |
| released product coverage | 9 / 9 |
| decision-situation coverage | 29 / 29 |
| observation placement coverage | 62 / 62; 50 reader labels |
| private-state placement coverage | 44 / 44 |
| intent placement coverage | 54 / 54; 53 reader labels |
| actor/unit/capability identity | PASS AS DESIGN |
| institution/office/unit ownership split | PASS AS DESIGN |
| observation and correction semantics | PASS |
| private-state ownership and lifecycle | PASS |
| intent/message/result separation | PASS |
| authority, capacity, relationship, and resource closure | PASS AS DESIGN |
| cross-hop causal lineage | PASS AS DESIGN |
| Contracts V1 carrier classification | PASS; no concrete counterexample |
| implementation or policy materialization | deliberately absent |

The review compared the candidate against the release products, semantic
skeleton, complete Scenario interface table, Contracts V1 surfaces, and the
accepted first-event mapping method. It did not import first-event historical
or behavioral meaning.

## 3. Requirement audit

| Objective requirement | Evidence in candidate | Verdict |
|---|---|---|
| preserve office and responsibility-unit boundaries | separate actor/unit identities, host relations, and capability-scoped state | `PASS` |
| prevent institutional duplication | one canonical institutional/system/resource/result state with scoped sub-entities | `PASS_AS_DESIGN` |
| preserve every released observation | exact 62-row closure and catalog rules | `PASS` |
| preserve every private-state placement | exact 44-row closure and reducer path | `PASS_WITH_IMPLEMENTATION_CONDITION` |
| preserve every released intent | exact 54-row closure and injective machine identity grammar | `PASS` |
| preserve recipient-specific delivery and correction | production, route, delivery, version, and frozen-decision rules | `PASS_AS_DESIGN` |
| separate proposal, authority, execution, and result | lifecycle/result ladder and reducer ownership | `PASS` |
| preserve concurrent-office capacity | explicit capacity identity and fail-closed ambiguity | `PASS_AS_DESIGN` |
| retain government and notification process boundary | Scenario/institutional process ownership; no new Agent | `PASS` |
| avoid a Contracts successor without proof | carrier table and concrete watchpoints | `PASS` |
| keep first implementation narrow | loader plus one lineage recommendation | `PASS` |

## 4. Adversarial findings and resolutions

### `SR-09` — institutional hosting could become shared knowledge

**Challenge.** Seven office actors and two responsibility-unit profiles are
hosted mainly by IHiS or SingHealth. A naive actor assembly could give them one
institutional observation envelope.

**Resolution.** Institutions retain canonical identity and process state,
while office/unit actors retain separate recipient deliveries, frozen
observations, private state, decisions, and intents. Host relations grant no
transitive knowledge.

**Status.** `RESOLVED_IN_CANDIDATE`.

### `SR-10` — office interface and historical officeholder could be conflated

**Challenge.** Several Definitions use named officeholders as historical
anchors but model an office-level decision interface. Mapping directly to an
unqualified natural-person identity would overstate stable personal behavior;
mapping directly to the institution would erase the office boundary.

**Resolution.** The actor entity is the bounded office/officeholder interface
for the modeled interval, hosted by the canonical institution and governed by
the released representation limits. It is neither a general personality nor
the institution as a whole.

**Status.** `RESOLVED_BY_IDENTITY_MODEL`.

### `SR-11` — population profiles could silently determine unit count

**Challenge.** The two Population Models establish role semantics but do not
fix the number, functional composition, assignment, access, or availability of
runtime units.

**Resolution.** Mapping releases capabilities only. Unit identity and
composition remain explicit configuration inputs; every unit receives
independent state and observation scope. No candidate runtime count is hidden
in the mapping.

**Status.** `RESOLVED_BY_CONFIGURATION_BOUNDARY`.

### `SR-12` — reused labels could collide across capabilities

**Challenge.** Seven observation labels and one intent label are reused. A
global reader-label dictionary would merge different sources, recipients, or
purposes.

**Resolution.** Observation, intent, action, and schema identities include
event and capability. Reader-facing names remain unchanged for traceability.

**Status.** `RESOLVED_IN_CANDIDATE`.

### `SR-13` — active work could be indistinguishable from never-issued work

**Challenge.** Missing, delayed, failed, expired, or superseded results matter
to later choices. If private state retained only the latest assessment, an
implementation could lose whether a request, direction, review, or report had
already been issued.

**Resolution.** The release now contains explicit active-intent/reference
state where behavior requires it. Mapping gives all 44 placements
capability-scoped reducer paths and requires lifecycle notices to distinguish
pending and unsuccessful work from never-issued work.

**Status.** `RESOLVED_IN_RELEASE_AND_CANDIDATE`.

### `SR-14` — flat V1 fields could hide a live compound-object lookup

**Challenge.** Technical accounts, meeting records, classification bases, and
outreach plans contain several behaviorally material properties. A single
opaque reference could allow a backend to read a later version.

**Resolution.** Each compound observation has a stable object/version plus
explicit atomic fields and a version-coherence validator. Decisions cite the
frozen projection; corrections create new deliveries.

**Status.** `RESOLVED_AS_DESIGN`; retained as a successor watchpoint.

### `SR-15` — admitted intent could be mistaken for containment or reporting

**Challenge.** The event contains multi-stage technical, institutional, and
notification processes. A single accepted flag would force causal success.

**Resolution.** Semantic admission, message materialization, route/transport,
delivery, institutional acceptance, execution, result, StateDelta, and later
observation are distinct records. Only the reducer changes truth.

**Status.** `RESOLVED_IN_CANDIDATE`.

### `SR-16` — external institutional inputs could hide a policy

**Challenge.** MOH/MCI/CSA responses and collective notification authorization
are not assigned to released Agents. Treating them as an unexplained
deterministic function would hide discretion and script the historical result.

**Resolution.** They are named exogenous institutional inputs with explicit
route, time, recipient visibility, result ownership, and sensitivity. The
Scenario cannot attribute them to an Agent or guarantee their occurrence.

**Status.** `RESOLVED_IN_SCENARIO_CANDIDATE`.

### `SR-17` — current loader is event-specific

**Challenge.** The existing release-wide loader validates a twelve-product
Panic 1907 release and fixture. Reusing it unchanged would reject or
mischaracterize the nine-product H2EPR-0616 release.

**Resolution.** The carrier review classifies an event-qualified internal
profile and exact fail-closed loader adaptation as later work. No current
candidate claims executable compatibility merely because Contracts V1 is
semantically sufficient.

**Status.** `IMPLEMENTATION_CONDITION`, not a semantic design gap.

### `SR-18` — long semantic IDs approach the StableId bound

**Challenge.** The longest proposed action schema identity is 124 characters
under a 128-character StableId limit.

**Resolution.** The exact released catalog fits without aliasing. A later
loader must assert every generated ID and may not append undeclared suffixes.
Any future product that exceeds the bound reopens the watchpoint rather than
silently truncating meaning.

**Status.** `PASS_FOR_RELEASE_V0.1_WITH_LOADER_ASSERTION`.

## 5. Cross-object consistency review

### Identity and information

```text
canonical institution
  -> office/unit host and capacity relation
    -> runtime actor and released capability
      -> recipient-specific frozen observation
        -> capability-scoped decision/private state
```

This preserves separate decision interfaces without multiplying institutional
truth. No route permits an office to read a host institution's full state,
another office's private assessment, or an undelivered/corrected future
record.

### Intent and result

```text
released decision situation
  -> capability-qualified DecisionRecord
    -> capability-qualified ActionIntent
      -> authority/route/object/resource adjudication
        -> optional recipient-specific MessageIntent
          -> delivery or institutional/technical result
            -> reducer StateDelta
              -> separately delivered later observation
```

Every negative or partial state remains trace-visible. Participant private
state may retain a reference or assessment but cannot create the result.

### Replay

Release, Scenario, mapping, configuration, assembly, variant, policy,
exogenous input, time, Contract, code, and RNG identities are pinned before an
admitted run. Ordered decisions, intents, messages, dispositions, deliveries,
results, deltas, and versions reconstruct each later observation and all 44
private-state paths without backend-local persistent memory.

## 6. Minimality and mainline review

The candidate adds only:

1. one event-qualified consolidated semantic mapping;
2. one H2EPR-0616 Scenario semantic layer; and
3. later, if authorized, an exact release loader and one bounded lineage
   conformance fixture.

It does not add a participant, general Agent archetype, Contracts version,
Rule-policy set, full-roster runtime, simulation, calibration, evaluation, or
historical-validity claim. This is proportionate to the project mainline: it
closes the semantic interfaces needed for scalable event construction and
defers event-specific breadth.

## 7. Conditions before implementation

Design acceptance would not satisfy these later implementation conditions:

1. materialize exact event-qualified entries for all 62 observations, 44
   private-state placements, and 54 intents from the fixed release;
2. assert all generated StableIds and every source/product hash;
3. declare a bounded office/unit assembly without duplicated institutional
   truth or private-state sharing;
4. implement only the selected lineage's necessary lifecycles and negative
   cases;
5. prove source/version, recipient delivery, capacity, idempotency, result,
   delta, and replay closure; and
6. rerun successor watchpoints before proposing any Contracts change.

These are deliberate later materialization tasks, not unresolved semantic
architecture.

## 8. Owner decision resolution

### `OD-CM-05` — institution and sub-entity identity

Accept one canonical institution record with distinct office and
responsibility-unit actor sub-entities, separate information/private state,
and no duplicated institutional/system/resource/result truth.

**Resolution:** `ACCEPTED`.

### `OD-CM-06` — consolidated semantic mapping

Accept event/capability-qualified observation, private-state, intent, message,
lifecycle, authority, result, and trace mapping for the exact nine-product
release.

**Resolution:** `ACCEPTED`.

### `OD-CM-07` — carrier decision

Accept Contracts V1, require an H2EPR-0616 event-qualified internal mapping
profile and Scenario semantics, and reject a Contracts successor absent a
concrete counterexample.

**Resolution:** `ACCEPTED`.

### `OD-CM-08` — later first implementation slice

After separate design promotion and implementation authorization, begin with
an exact fail-closed loader and one bounded technical-to-institutional lineage,
not all participant policies or a full simulation.

**Resolution:** `ACCEPTED_AS_FUTURE_SCOPE_ONLY`.

## 9. Review verdict

`ACCEPTED_BY_OWNER`

The remaining work is deliberate future configuration and bounded
materialization, not further semantic expansion. This verdict authorizes no
implementation.
