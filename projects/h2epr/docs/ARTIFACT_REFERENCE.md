# Artifact reference

## Dataset admission

| Artifact | Path | Authority | Principal consumer |
|---|---|---|---|
| event specification | `data/h2epr/.../event_spec.json` | public event identity and title | Source Profile loader |
| frozen evidence | `data/h2epr/.../frozen_evidence.json` | bounded dataset records | human semantic authoring |
| Draft EPG | `data/h2epr/.../draft_epg.json` | exposed stages, episodes, participants, actions, and time labels | roster, scenario, Rule baseline |
| Source Profile | `events/<event>/source-profile.json` | exact allow-list, byte identity, exposure, prohibitions, claims | every construction layer |

The Source Profile contains exactly three logical inputs in the order
`event_spec`, `frozen_evidence`, `draft_epg`. Direct paths are resolved without
listing sibling files.

## Participants

| Artifact | Required contribution | Falsifier |
|---|---|---|
| participant roster | every Draft occurrence, observed name/type/role, anchors, numeric gaps | one occurrence missing, duplicated, or silently normalized |
| actor map | one disposition and rationale per source participant; active runtime units | unmapped participant or unrecorded aggregation loss |
| Agent Definition | identity, represented interface, information, state, authority, choices, uncertainty, worked cases | exact backend policy or guaranteed outcome |
| Population Model | choice unit, inclusion, aggregation, heterogeneity boundary, promotion rule | invented microbehavior or group personality |
| semantic index | actor-to-parent path, hash, source IDs, all Draft anchors | hash drift or an anchor absent from the parent document |
| observation registry | producer, consumers, availability, visibility, missing behavior | observation with no owner or hidden future content |
| intent registry | meaning, eligible actors/targets, payload, authority, handler, lifecycle | action space wider than the semantic parents |
| lifecycle registry | initial, terminal, transitions, owner, trigger | terminal or pending state with no declared route |
| participant interface | exact per-actor observations, intents, lifecycles, state fields | actor or capability universe mismatch |

## Scenario and configuration

`scenario-interface.json` states the portable actor/state contract and exact
implementation identifiers. `scenario-mechanism.json` defines typed state
fields, intent handlers, parameter domains, preconditions, deterministic
effects, message kinds, annotations, conflict policy, safety invariants, and
descriptive outcome expectations.
The reader-facing Scenario Definition explains why those fields exist and
where the dataset stops supporting detail.

Shared configuration selects:

- active actors and ordered logical coordinates;
- opening state over the complete mechanism field universe;
- explicit directed routes and positive latency;
- observation timing and sealed-prestate rules;
- terminal transport policy and assumptions.

Backend configuration selects decision-production controls. Rule configuration
contains deterministic actor rows with activation windows or justified fixed
coordinates, guards, a typed action, optional
messages, and `no_op` as the default. Every top-level setting is covered by one
provenance pointer or one reviewed typed exemption. Admission receipts are
rederived from parents; they are not trusted merely because they self-hash.

## Releases, assembly, and package

Each semantic release contains a manifest and exact `SHA256SUMS`. Manifest
artifact paths normally remain within the release root. The backend-realization
release may reference only the three typed backend-configuration artifacts
under `configs/<event>/backends/<backend>/`.

The package assembly carries three identities:

| Identity | Includes | Excludes |
|---|---|---|
| `semantic_assembly_sha256` | source profile and four semantic releases | backend catalog and attachments |
| `backend_catalog_sha256` | semantic assembly identity plus backend statuses/releases | compiled package bytes |
| `assembly_sha256` | complete assembly declaration | only its own field |

The compiler first creates the backend-neutral package core. An implemented
backend is attached through a registered builder. Attachment changes the full
manifest identity and binding, but `package_sha256` must remain unchanged.

## Runtime evidence

| Artifact | Meaning |
|---|---|
| run manifest | package, binding, configuration, seed/model, H2EPR and MASim source identity |
| simulation trace | append-only, hash-chained record sequence |
| tick seals | coordinate-level state, transport, and record closure |
| run seal | terminal trace/state/transport closure |
| replay receipt | authoritative reduction from opening state to exact final state |
| Generated EPG | trace-derived graph with one first-class node per trace record |
| coordinate results | derived per-coordinate summaries |
| run receipt | output inventory, counts, closure claims, and local custody identity |
| outcome assessments in run receipt | each expectation's actual replayed value and match result; never an integrity-success flag |
| failed-attempt receipt | diagnostic partial custody, sealed ticks, typed failure and unresolved transport; no complete release or exact resume claim |
| determinism receipt | exact A/B comparison plus linked generated-ID invariance |

The compact tracked release contains identities and receipts, not the full
trace or graph. Publication reopens raw custody, validates the hash chain and
seals, replays state, rebuilds summaries and graph coverage, and rematerializes
deterministic Rule runs before accepting the release.

The observation contract retains each actor's own action dispositions and
actual received messages. Publication reconstructs this memory and the visible
state projection from prior trace evidence; it does not trust producer memory
or outcome flags. Graph links make delivery and cumulative memory provenance
traversable without treating available information as proven causal influence.

## Report and experiment artifacts

A simulation reading is descriptive analysis of one generated process. It
separates direct output facts, mechanism attribution, interpretation, and
limitations. A Draft-facing comparison is explicitly conditioned on full
Draft exposure and cannot be reported as held-out performance.

An experiment plan selects already valid package/backend rows, seeds, custody,
model controls, scheduling, failures, and analysis definitions. Admission is
read-only. It neither implements a backend nor launches a matrix.
