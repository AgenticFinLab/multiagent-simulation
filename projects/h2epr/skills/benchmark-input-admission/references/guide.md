# Benchmark input admission guide

## Contract

This task turns three named dataset files into one Source Profile. It does not
interpret the event, select participants, or search for better evidence. The
profile is the construction allow-list inherited by every downstream asset.

The caller supplies an exact event ID, data root, and endpoint. Resolve only:

| Logical name | Required filename | Permitted use |
|---|---|---|
| `event_spec` | `event_spec.json` | event identity and benchmark metadata |
| `frozen_evidence` | `frozen_evidence.json` | dataset-provided evidence records |
| `draft_epg` | `draft_epg.json` | exposed process, participant, and action structure |

Reference, held-out suffixes, evaluation-only data, network retrieval, and
external research remain prohibited even when their existence is already
known.

## Preflight record

Before opening an input, record the repository branch, HEAD, tree, worktree,
index, unmerged state, event ID, declared paths, authorized endpoint, and prior
exposure. Do not inventory the event directory to prove that no other files
were used. A direct `stat`, hash, or open of each declared path is sufficient.

Classify exposure as:

- `prefix_clean` when construction has not seen the later Draft suffix;
- `full_draft_exposed` when the complete Draft is an allowed construction
  input.

Exposure is a property of construction knowledge, not a quality verdict. It
must propagate into the package, run, report, and any comparison claim.

## Admission procedure

1. Reject absolute paths, `..`, symlinks, missing files, duplicate logical
   names, and names outside the exact three-name sequence.
2. Compute SHA-256 and byte size from the bytes actually opened.
3. Parse strict JSON and reject duplicate keys.
4. Match the public event ID across the event specification and every input
   location where the dataset declares it.
5. Inspect the Draft wrappers required by the current compiler: stages,
   episodes, participants, names, types, roles, actions, and timestamps. Each
   participant needs an explicit action list, which may be empty for a passive
   appearance. This does not remove the occurrence from later roster coverage
   or require a fabricated no-op source action. Validate every action wrapper
   when the list is nonempty; reject a missing field or non-list carrier.
6. Record dataset shape defects rather than silently repairing them.
7. State dataset limitations and the complete scientific claim exclusion set.
   Copy the machine tokens from the Source Profile template; do not substitute
   prose synonyms for required values.
8. Self-hash the profile with its hash field omitted, validate the schema, and
   hand off the exact profile identity.

## Worked failures

| Observation | Disposition | Reason |
|---|---|---|
| A named participant has `actions: []` in an early episode and acts later | admit the explicit empty list and retain both appearances | passive presence and a missing/malformed field are different cases |
| `actions` is absent, null, a mapping, or contains malformed action wrappers | reject | accepting passive appearances does not waive source-shape validation |
| A participant ID is absent in one episode | admit with a recorded source defect | the Draft remains unchanged; roster work must account for the gap |
| A filename differs only by capitalization | reject | logical input identity is exact, not best-effort |
| The caller asks to inspect a Reference file to improve the roster | stop | it crosses the construction boundary |
| The three files parse but disagree on event ID | reject | downstream identity cannot be made authoritative |
| The full Draft was already read in this construction lineage | use `full_draft_exposed` | exposure cannot be undone by reopening fewer files |

## Failure routing

Path, parse, identity, hash, or exposure failures remain with input admission.
Ambiguous participant meaning belongs to roster work after admission. A request
for historical verification or external supplementation requires a separately
authorized research protocol and cannot be repaired inside this workflow.

## Completion evidence

The handoff names the profile path, schema/profile versions, profile SHA-256,
the three file hashes and sizes, exposure mode, protocol eligibility, all
prohibited classes, dataset limitations, validation command and result, Git
state, and next legal action. No semantic asset may be started after a failed
or drifting admission.

The minimum exact `does_not_support` set is `held-out evaluation`, `historical
fit`, `parameter calibration`, `causal validity`, `scientific validity`, and
`universal generality`. Terms such as `held-out performance` or `causality`
may be useful additions, but they do not satisfy the corresponding machine
token.
