# H2EPR event coordination

This directory provides one lightweight coordination entry for each event
admitted to H2EPR construction or retained as a project baseline. It makes a
multi-event project discoverable without copying participant, scenario,
configuration, or release assets into a second event package.

## Directory layout

```text
events/
└── <lowercase_snake_case_event_slug>/
    ├── README.md
    ├── frame-evidence-v<major>.<minor>.md
    ├── participant-evidence-v<major>.<minor>.md  # once participant production begins
    ├── source-register-v<major>.<minor>.md        # optional separate authority
    └── decision-situations-v<major>.<minor>.md    # optional shared portfolio
```

The event `README.md` instantiates the
[Event Build Brief](../event-build-brief-template.md). It owns the event's
primary question, boundary, construction exposure, current authorization,
method baseline, and links to responsibility-owned assets. For a small event,
it may also contain the causal role map, initial roster dispositions, and
semantic skeleton.

Do not create empty phase directories or duplicate accepted files here.
Definitions remain under `agents/`, population models under `populations/`,
scenario semantics under `scenarios/`, configurations under `configs/`, and
accepted inventories under `releases/`. The event directory owns shared source
identity, claim adjudication, participant-time evidence, and cross-participant
research situations. A larger event links all other artifacts from its
coordination entry as they become authorized and accepted.

An event may open with its `README.md` alone. Before its event frame is
accepted, it adds one versioned `frame-evidence` record that owns or integrates
the source register, claim ledger, unresolved questions, exposure boundary,
and evidence-use closure for that frame. Once participant production begins,
one versioned `participant-evidence` record becomes the event-level claim
authority shared by its Agent Definitions and population models.

A compact event may integrate adopted participant source identities and
decision situations in that record. A larger event may separate a versioned
source register or shared decision-situation portfolio when this improves
reading and custody without duplicating claims. These are alternate file
arrangements under one evidence responsibility, not different review paths.

Other supporting records are added only when a later phase needs an authority
that would make the entry difficult to read. Their names state their bounded
purpose and version. Do not create placeholder files, a separate evidence file
per role, or repeat the same record under several phase names.

## Event entries

| Event | Coordination entry | Current position |
|---|---|---|
| `H2EPR-0288`, Panic of 1907 | [panic_1907](panic_1907/README.md) | First event closed through deterministic full-roster Rule execution, replay, and a trace-derived generated EPG. |
| `H2EPR-0616`, SingHealth Data Breach | [singhealth_data_breach](singhealth_data_breach/README.md) | Retained second-event baseline through one bounded lineage-conformance case. |

Completed entries present accepted assets in two groups. The research-facing
group is the default scholarly path through evidence, participant models, and
event semantics. The reproducibility group retains exact release, mapping,
admission, binding, conformance, manifest, and checksum identities. Both groups
remain tracked; the distinction changes navigation, not custody or authority.

## README convention

Event entries use the same core order:

1. `Event profile` records identity, question, boundary, exposure, current
   authorization, exclusions, and exact upstream authorities.
2. Phase-specific sections follow the Event Build Brief order when needed:
   `Evidence readiness`, `Causal scope`, `Causal role map and roster
   dispositions`, and `Shared semantics and ownership`.
3. `Research-facing assets` links accepted evidence, participant models,
   interface accounts, Scenario semantics, and configuration design without
   copying their contents.
4. `Reproducibility and release records` links the exact accepted packages and
   validation records. An active event may keep candidate material under its
   `Current work package` rather than presenting it as an accepted asset.
5. `Current work package` states what is active and where it stops; a completed
   baseline uses `Current position` instead.
6. `Open decisions` appears only while a material owner decision remains.
7. `Phase status` gives the concise readiness or closeout disposition.

An active event may retain the phase-specific tables needed for its current
decision. A completed baseline replaces those details with links to accepted
authorities. This keeps the entries visually consistent without forcing every
event to carry the same amount of documentation.

## Opening an event

1. Select a stable lowercase snake-case slug consistent with the other
   event-owned directories.
2. Copy only the useful prompts from the Event Build Brief template into the
   event `README.md`; remove unused optional sections.
3. Identify the current method baseline and list only the Skills and templates
   selected for the work package. Keep its exact Git identity in the local work
   record during construction and include it in the first release manifest
   when the inputs are promoted.
4. Declare construction mode, allowed source roots, protected paths, and any
   prior target exposure before broad file discovery or research.
5. Close only the Frame the event phase. Participant production begins through
   a later authorization recorded in the same entry.

The entry is updated in place when the event question, current phase, or linked
authorities change. Git history preserves earlier accepted states. It is not a
daily status log, build transcript, or substitute for release manifests and
phase-owned reviews.

## Retaining a completed baseline

When an event stops at an accepted project boundary, keep a short coordination
entry that identifies the final question, accepted assets, claim boundary,
and next legal action. Preserve accepted research content and do not reconstruct
working notes; repository maintenance may normalize an authority's canonical
path while updating every pinned reference and checksum as one coherent
change. Deeper research begins only under a new question and authorization.

The event entry owns the current position. A hash-pinned phase package remains
an as-of-release record, so its description of the next eligible stage need not
be rewritten after that stage is completed. Current guides should make this
distinction clear and link the final accepted endpoint.

## Protected inputs

Routine construction and repository audits exclude `reference_epg.json`,
held-out suffixes, and evaluation-only paths from searches, prompts, retrieval
indexes, and working sets. Seeing protected target content makes that human or
tool context full-draft-exposed for the target. Record the exposure rather
than attempting to restore clean-builder status.

Reference identities may appear in frozen fixture inventories, but Reference
content is read only by a separately authorized post-seal evaluation process.
