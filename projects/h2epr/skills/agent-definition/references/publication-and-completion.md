# Publication and completion

## Publication goal

The published Agent Definition should read like a methods appendix: precise
enough to reproduce the participant boundary, clear enough to audit without
code, and modest about what the benchmark inputs establish.

Publication is not a formatting exercise. It records an accepted semantic
parent that machine assets can project without widening.

## Ten-module quality contract

### 1. Model overview

Give a compact identity and scope table, then state the represented choice in
plain language. A reader should know why this is an Agent before reaching the
behavior sections.

### 2. Benchmark participant and representation

Record included and excluded units, aggregation loss, rejected dispositions,
and a concrete split or narrowing trigger. Avoid organizational biography.

### 3. Dataset basis and provenance

Provide resolvable anchors, claim classes, assumptions, conflicts, and
withdrawal consequences. Do not inflate benchmark statements into verified
history.

### 4. Event role, relationships, and authority

Separate decide, authorize, communicate, allocate, execute, verify, and observe
authority. Name directional relationships and resource boundaries.

### 5. Decision situations, observations, and state

Close activation, delivery, freshness, missing behavior, visibility,
persistence, forbidden information, and reopening. Do not expose the entire
world state.

### 6. Admissible decision semantics

Use stable document-local `decision.*` labels. State alternatives, duties,
prohibitions, delay, concurrency, backend freedom, and falsifiers. Avoid
decision trees and preferred trajectories.

### 7. Intent and environment-result boundary

Use exact event-wide `intent_id` values and typed lifecycle semantics. Name
every result that remains environment-owned.

### 8. Configurable dimensions and uncertainty

Declare only meaningful constructs and domains. Leave exact values and
selection logic downstream. State whether a construct is dataset-derived,
synthetic, or underdetermined.

### 9. Worked cases and contract falsification

Exercise normal, missing, pending, rejected, adverse, and perturbed paths.
Cases should test invariants and authority, not reproduce the Draft ending.

### 10. Limitations and source anchors

Name representation losses, omitted roles, assumption dependence, structural
alternatives, parameter limits, and successor conditions. End with a compact
source and semantic-parent index.

## Natural technical writing

Prefer concrete subjects and owned verbs:

- “The environment admits the request”;
- “`obs.authority_notice` becomes stale after a superseding notice”; and
- “`decision.response_request` permits either request class.”

Avoid:

- defensive repetition of what the project does not claim;
- generic claims that the design is robust, realistic, comprehensive, or
  flexible;
- one-sentence paragraphs that restate table headings;
- copied boilerplate unchanged across unrelated Agents;
- vague nouns such as “stakeholders,” “context,” or “relevant information”;
- future tense used to hide missing semantics; and
- long theory discussions that do not change an executable contract.

Limitations should identify an actual omitted distinction and its consequence,
not recite a universal disclaimer.

## Cross-product consistency

Before acceptance, compare the Definition with:

- roster Agent ID, source IDs, and disposition;
- actor map and capability ownership;
- observation, intent, lifecycle, and state registries;
- scenario routes, resources, authority, and effects;
- configuration construct names and domains;
- backend binding actor semantic parents and intent IDs; and
- tests that exercise shared handlers and failure paths.

The prose is authoritative for participant semantics, while machine registries
are authoritative for executable identifiers and validation. A mismatch is a
release failure; neither side silently overrides the other.

## Identity and current-version policy

Publish one current Definition at the event's canonical path. The maintained
participant semantic index pins its actor, representation kind, semantic ID,
path, checksum, source participant IDs, and Draft anchors. It is a closed
machine contract: do not add template, reviewer, or successor fields to it or
to a run/configuration receipt.

Use a separate review record for the exact candidate path/hash, template
path/hash or repository revision, accepted parent paths/content identities,
reviewer/date, checks, findings, accepted limitations, successor condition,
verdict, and next legal action. Supervisor working reviews belong in ignored
project memory. If a semantic release publishes a review as a formal artifact,
its manifest must seal that artifact like the other release files; the
manifest alone does not validate the review's meaning. An unpublished review
must not become a required runtime or clean-checkout input.

The Definition names semantic parents and the review-record location; the
external record pins the completed candidate and projection set. This avoids
self-embedded Definition hashes and reciprocal content-hash dependencies. The
review is not a competing authority for the event's current release status.

Git history preserves replaced text. Do not publish parallel `v0.1`, `v0.2`,
“final,” “revised,” or dated copies as competing current authorities unless a
repository-level release standard explicitly requires an immutable successor.

## Validation layers

### Structural

- UTF-8 and final newline;
- exact ten-module order;
- no unfilled template markers;
- local links resolve;
- stable IDs are unique; and
- tables have consistent columns.

### Semantic

- representation passes the disposition test;
- claims have a provenance class;
- observations have producers and routes;
- persistent state has an updater;
- every commitment maps to observations and intents;
- every intent names an environment-owned result;
- more than one backend can implement the contract;
- worked cases cover adverse paths; and
- limitations include successor conditions.

### Event-wide

- no duplicate decision authority;
- registries neither omit nor widen Definition semantics;
- scenario mechanisms can admit and reject relevant intents;
- configuration values remain outside the Definition; and
- backend bindings reference the accepted Definition identity.

Automated structure checks support review. They do not decide whether a claimed
authority is justified or whether the representation is scientifically useful.

## Review disposition

Separate product state from the independent review verdict:

| Product state | Review verdict and meaning |
|---|---|
| `REVIEW_CANDIDATE` | no verdict yet; independent review pending |
| `REVISE` | `return to owning layer`; findings prevent acceptance |
| `ACCEPTED` | `accept` or `accept with recorded limitations`, with the distinction preserved in the review record |
| `SUPERSEDED` | historical accepted product replaced by the sole current successor; not a new reviewer verdict |

Use the three verdicts from the Agent Definition review Skill. A product-state
label alone never stands in for reviewer identity, findings, or acceptance.

Acceptance records the reviewer, parent identities, checks performed, accepted
limitations, and exact content identity. It does not accept a backend, run, or
scientific conclusion.

## Failure routing

| Finding | Owner |
|---|---|
| incomplete source occurrence or wrong disposition | roster |
| unsupported identity or authority | Agent Definition revision |
| missing shared semantic ID | participant registry |
| missing world route, resource, or effect | scenario/mechanism |
| exact value or comparison arm | configuration/experiment plan |
| selection algorithm or prompt | backend realization |
| trace or state update defect | runtime/publication |
| historical or causal validity question | later scientific evaluation |

Do not broaden the Agent Definition to absorb downstream incompleteness.

## Completion handoff

The handoff must name:

- files created or changed;
- accepted parent identities;
- Definition content identity;
- source and assumption counts;
- commitment, observation, state, intent, and case counts;
- structural and semantic validation results;
- unresolved limitations;
- reviewer disposition; and
- next legal action.

A completion handoff is evidence about the product. It is not a substitute for
independent review of the Definition itself.
