# H2EPR Phase Closeout Checklist

Use this checklist only at a maintained phase boundary, not after every edit,
artifact, role, or production batch. The default closeout is a compact record
in the brief, manifest, release README, review, decision, or receipt that
already owns the result. Do not create a new closeout file when that would
duplicate an existing authority.

Apply the core checks to every phase. Apply a conditional check only
when the phase touched that surface. Artifact-specific reviews remain
authoritative; this checklist confirms scope, depth, and handoff. The checks
are review questions, not separate required reports, approvals, or sign-offs.
They impose no universal source, participant, test, or document count.

## 1. Compact closeout record

| Field | Closeout record |
|---|---|
| Event, phase, object, and inputs | `<stable event, one maintained phase, exact candidate or release, and upstream identities>` |
| Authorized purpose and endpoint | `<question tested and stopping boundary>` |
| Outputs and status | `<phase-owned results and artifact-specific verdict>` |
| Verification and limitations | `<checks and results; material omissions or findings with owner and consequence>` |
| Mainline and depth judgment | `<why the result is sufficient without entering later work>` |
| Next legal action | `<action and entry conditions, or explicit stop>` |

## 2. Core checks

- [ ] **Mainline:** the result still answers the accepted event or method
  question.
- [ ] **Minimality:** every material addition has a current consumer; optional
  roles, mechanisms, fields, variants, policies, cases, and runtime paths were
  deferred.
- [ ] **Inputs:** required inputs had the right status and identity; accepted
  upstream artifacts were not silently repaired downstream.
- [ ] **Authority:** evidence, participant semantics, scenario, configuration,
  mapping, policy, runtime state, and evaluation retain separate owners.
- [ ] **Evidence and information:** source permission, exposure, event time,
  participant-time availability, uncertainty, and prohibited inputs were
  preserved.
- [ ] **Review and verification:** the exact stable object received only the
  substantive, integrity, documentation, or test checks justified by its risk.
- [ ] **Repository discipline:** tracked assets are accepted and discoverable;
  mutable notes, duplicate trackers, hidden defaults, and event-specific
  content in shared layers were avoided.
- [ ] **Publication surface:** reader-facing research artifacts satisfy the
  [publication standard](PUBLICATION_STANDARD.md); project-only identity and
  integrity metadata remain in the records that own them; current event and
  directory guides point to the accepted endpoint rather than preserving a
  completed phase transcript.
- [ ] **Handoff:** limitations and owner decisions are visible, and completion
  does not automatically authorize the next phase; note a reusable method
  finding only when one actually emerged.

Record the depth judgment in one sentence:

> The phase stops at `<accepted boundary>` because additional `<work>` would
> test `<different or later question>`.

## 3. What blocks closure

Only a finding that invalidates the phase result or its safe handoff should
block closure. Examples are:

- a required input is missing, mutable, drifted, or outside its permission;
- the event question, interval, claim boundary, causal owner, roster
  disposition, or endpoint changed without approval;
- a participant receives future, hidden, Reference, or otherwise prohibited
  information;
- two layers claim the same behavior, authority, resource, result, or state;
- a downstream artifact adds missing semantics, relies on a hidden default, or
  changes an accepted upstream input;
- a required substantive review, release identity, integrity check, or focused
  test is absent or fails; or
- an implementation result is nondeterministic, untraceable, or not replayable
  when determinism, trace, or replay is part of the phase claim.

The following do not block by themselves: optional extra sources, additional
historical roles, broader variants, exhaustive field matrices, full test suites
for research-only edits, future policy coverage, full simulation, calibration,
or evaluation outside the current question. Record them only when they affect
a later entry condition.

## 4. Conditional checks

Apply only the rows touched by the phase.

| Triggered surface | Additional closeout question |
|---|---|
| New or changed evidence | Are adopted claims, conflicts, source custody, event time, participant availability, use, and exposure recorded? |
| Participant or population product | Did evidence, behavior, the participant product, publication-facing interface coverage, the proportionate working interface review, and roster/skeleton consistency close without implementation material? |
| Semantic release | Does every roster row have a disposition, and do the manifest and integrity records pin the accepted products? |
| Scenario or mapping | Does scenario own event-world meaning while mapping preserves released meaning without adding behavior or requesting a successor for convenience? |
| Scenario Configuration | Are purpose, assembly, selections, sensitivities, completion, and the non-executable boundary explicit and reviewed? |
| Admission or binding code | Do exact identities, fail-closed errors, the selected lineage, required policies, focused negatives, and affected regressions pass? |
| Trace or conformance | Are per-object and cross-lineage checks, deterministic trace/seals, replay, expected evidence, and depth review complete? |
| Policy Realization or executable successor | Does exact coverage close every configured actor capability, decision commitment, intent, selected policy, required lifecycle, and declared failure path without rewriting a semantic parent? |
| Full-roster Rule run | Is every configured actor instantiated, is authoritative state changed only by the environment/reducer, and are the canonical run and same-input repeat byte-identical in their scientific outputs? |
| Generated event graph | Does every graph item resolve to sealed trace provenance, do graph identity and closure checks pass, and is the claim limited to the declared uncalibrated mechanism-coverage run? |
| Evaluation or external claim | Is there a separate authorized protocol with the required evidence isolation and claim review? |
| Completed event baseline | Is the event entry concise and current, while hash-pinned phase records remain clearly readable as release-time boundaries? |

Verification is proportional. Run focused checks first. Full regression,
release checksums, or CI are required at the release or engineering boundary
that could affect them, not after every source note, role draft, or editorial
change.

## 5. Phase stopping boundaries

| Phase | Minimum result | Do not infer |
|---|---|---|
| Frame the event | Accepted question, boundary, evidence permission, causal ownership, dispositions, and shared semantics. | Participant production or code authorization. |
| Define participants | Reviewed Agent Definitions or Population Models, a lightweight semantic interface review, and shared publication-facing interface coverage. | Release membership, mapping, or implementation. |
| Release the semantic roster | Pinned accepted products and resolved dispositions. | Executability or validity. |
| Close scenario and mapping | Separate accepted event-world semantics and lossless carrier mapping. | Participant behavior from scenario or scenario meaning from mapping. |
| Configure a purpose | Reviewed declared-purpose configuration. | Executability, calibration, or outcome fit. |
| Admit the configuration | Fail-closed static identity, schema, reference, and receipt evidence. | Policy behavior or runtime readiness. |
| Bind a minimal lineage | Exact projection and only the policies required by the selected lineage. | Full-roster integration or broad simulation. |
| Review conformance | Focused negatives and deterministic trace/replay closeout for the bounded slice. | Scientific evaluation or historical validity. |
| Realize complete Rule behavior | Exact participant and Scenario-policy implementations with complete semantic and failure coverage. | A changed semantic configuration, hidden defaults, or run authority. |
| Assemble full-roster execution | Admitted executable successor, complete projection, explicit environment ownership, and reproducible run identity. | Calibration, outcome fitting, or an implicit run. |
| Close a generated event graph | Deterministic sealed runs, replay closure, trace-derived graph, and compact release evidence. | Historical reconstruction, policy effectiveness, or scientific validity. |

An event may intentionally stop after any authorized phase. Later rows are not
missing work unless the accepted research question requires them.

## 6. Disposition

Use one plain-language disposition:

- **Complete** — the applicable checks pass.
- **Complete with recorded limitations** — limitations remain inside the
  accepted claim and stopping boundary.
- **Return to owning layer** — a defect must be corrected by its semantic or
  engineering owner.
- **Owner decision required** — a material scope, representation, structural,
  or claim choice exceeds the current mandate.
- **Incomplete** — required output or verification is missing.

For repeated batches, one phase close record may reference batch and role
reviews; do not run this checklist separately for every role. For a release,
one manifest and review may close the phase. For a large event, aggregate
mechanically derived inventories rather than repeating the same checklist for
every item.
