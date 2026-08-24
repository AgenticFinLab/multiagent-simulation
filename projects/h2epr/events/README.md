# H2EPR event coordination

This directory provides one lightweight entry point for each event under
active construction. It makes a multi-event project discoverable without
copying participant, scenario, configuration, or release assets into a second
event package.

## Layout

```text
events/
└── <event-slug>/
    └── README.md
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
accepted inventories under `releases/`. A larger event links those artifacts
from its coordination entry as they become authorized and accepted.

## Opening an event

1. Select a stable lowercase snake-case slug consistent with the other
   event-owned directories.
2. Copy only the useful prompts from the Event Build Brief template into the
   event `README.md`; remove unused optional sections.
3. Record the repository commit that supplies the method baseline and list
   only the Skills and templates selected for the current work package.
4. Declare construction mode, allowed source roots, protected paths, and any
   prior target exposure before broad file discovery or research.
5. Close only the Frame the event phase. Participant production begins through
   a later authorization recorded in the same entry.

The entry is updated in place when the event question, current phase, or linked
authorities change. Git history preserves earlier accepted states. It is not a
daily status log, build transcript, or substitute for release manifests and
phase-owned reviews.

## Protected inputs

Routine construction and repository audits exclude `reference_epg.json`,
held-out suffixes, and evaluation-only paths from searches, prompts, retrieval
indexes, and working sets. Seeing protected target content makes that human or
tool context full-draft-exposed for the target. Record the exposure rather
than attempting to restore clean-builder status.

Reference identities may appear in frozen fixture inventories, but Reference
content is read only by a separately authorized post-seal evaluation process.
