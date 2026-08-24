# H2EPR Event Build Brief Template

Use this brief before participant production begins. It records the minimum
shared understanding needed to build an event consistently: the question,
boundary, evidence permission, causal responsibilities, initial roster
dispositions, shared semantics, and current authorization.

Keep the brief concise. Complete the minimum profile below and add a
conditional section only when the event actually triggers it. A small event
may keep its role map, roster, and semantic skeleton here. A larger event may
link separate versioned artifacts rather than duplicate them.

For a routine event, aim for a one- or two-page brief. Add only the causal,
role, and semantic rows needed for the current phase, and link existing
inventories instead of copying them. The prompts below do not require a
separate approval document or meeting. There is no minimum source, transition,
participant, batch, or review count.

This brief is not a full Scenario Definition, an implementation plan, or a
roadmap authorization. Do not retain empty tables merely to look complete.

## 1. Minimum event profile

| Field | Event record |
|---|---|
| Event | `<public ID, title, and stable event slug>` |
| Coordination entry | `<events/<event-slug>/README.md>` |
| Brief identity and status | `<semantic version or candidate identity; draft, review candidate, accepted, or superseded>` |
| Method baseline | `<repository commit plus the selected Skill and template paths>` |
| Primary question | `<one event-process question about decisions, information, interaction, or state change>` |
| Purpose and claim boundary | `<method, mechanism, reconstruction, or other bounded purpose; claims explicitly not made>` |
| Temporal boundary | `<analytic start, primary window, horizon, and deliberately excluded periods>` |
| Evidence and exposure | `<approved roots and source permissions; construction mode; draft, outcome, Reference, or evaluation exposure; protected paths>` |
| Current authorized phase and endpoint | `<one maintained phase name and the last result currently permitted>` |
| Excluded work | `<unapproved sources, later phases, implementations, runs, evaluations, claims, or external actions>` |
| Decision owner and review, if needed | `<scope owner and only the review needed for the current phase>` |
| Exact upstream inputs | `<fixture, source release, workflow, contract, or accepted artifact identities>` |

State the current authorization in one sentence:

> This cycle may `<produce or decide>` and stops before `<next unapproved
> activity>`.

Before any broad repository search, confirm that the working set excludes
`reference_epg.json`, held-out suffixes, and evaluation-only paths unless
post-seal evaluation is explicitly authorized. If protected target content is
seen, record the exposure here; the same builder or tool context cannot later
serve as a clean builder for that target.

## 2. Causal scope

Record only the transitions needed to answer the primary question. A
chronological milestone with no causal use need not appear.

| ID | Pre-state or opportunity | Transition to explain | Candidate decision or process owner | Authoritative result owner | Evidence status or open issue |
|---|---|---|---|---|---|
| `CT-<N>` | `<relevant condition>` | `<decision, delivery, interaction, or state change>` | `<participant or process>` | `<institution, scenario, or reducer>` | `<supported, bounded, disputed, unknown, or gated>` |

Distinguish initial context, endogenous decisions, exogenous inputs, and
excluded aftermath. Preserve uncertain dates and partial order. A data range,
publication date, or retrospective finding is not automatically an event
start or participant decision time.

## 3. Causal role map and roster dispositions

Use the disposition vocabulary in the
[participant workflow](agents/WORKFLOW.md): Agent; population or cohort;
representation gate; scenario or institutional process; initial or exogenous
context; or excluded.

| Entity or process | Disposition | Choice or causal responsibility | Representation boundary | Evidence maturity | Gate or reason for externalization |
|---|---|---|---|---|---|
| `<stable name>` | `<disposition>` | `<what must be explained or owned>` | `<individual, organization, unit, cohort, process, or boundary>` | `<current support>` | `<decision needed, or concise reason>` |

Historical prominence is not a reason to create an Agent. A scenario process
may not absorb a material autonomous choice merely to keep the roster small.
Open a representation gate only when reasonable alternatives would change the
causal model; obvious dispositions need no separate gate document.

## 4. Shared semantics and ownership

Record only concepts that two or more products must interpret consistently or
whose ownership could otherwise become ambiguous.

| Concept, route, or lifecycle | Event-bound meaning | Semantic or state owner | Participant-visible form | Required boundary or open question |
|---|---|---|---|---|
| `<time, institution, information, relationship, resource, request, message, result, or termination concept>` | `<meaning in this event>` | `<evidence, Definition, scenario, configuration, mapping, policy, or reducer>` | `<if and when observable>` | `<invariant, lineage need, or gate>` |

Do not define machine fields, exact schedules, policy code, or numerical
defaults here. A complex event may link a separate semantic skeleton; this
brief records its identity and acceptance status.

## 5. Current work package

| Field | Current decision |
|---|---|
| Work mode | `<event framing, reference pilot, or Roster production>` |
| Roles or processes in this package | `<bounded causal segment>` |
| Participant production profiles | `<disposition-only, standard, or deep, only when participant work is authorized>` |
| Required project Skills and templates | `<only those needed for this package>` |
| Expected outputs | `<phase-owned products>` |
| Review and verification | `<proportionate evidence, semantic, integrity, documentation, or test checks>` |
| Stop conditions | `<conditions that return work to an owner or require a scope decision>` |
| Next legal action | `<action and exact entry conditions, or explicit stop>` |

Later phases may be named as a non-authorizing roadmap when this helps
coordination. Do not pre-specify their actor counts, policies, variants, test
matrices, or implementation details.

## 6. Open decisions, only when needed

Omit this section when no material decision is open.

| ID | Decision or risk | Owning layer | Evidence or review needed | Dependent work | Owner disposition |
|---|---|---|---|---|---|
| `OD-<N>` or `RISK-<N>` | `<bounded issue>` | `<authority>` | `<minimum input needed>` | `<what cannot proceed>` | `<pending, accepted, rejected, or deferred>` |

At minimum, request owner direction when the primary question, temporal
boundary, evidence permission, causal owner, roster disposition, claim class,
or current endpoint would change. Ordinary defects return to their owning
layer without reopening the entire event.

## 7. Ready to start

The Frame the event phase closes when:

- [ ] the question, temporal boundary, evidence permission, exposure, current
  endpoint, and excluded work are explicit;
- [ ] the method baseline and protected-input search boundary are explicit;
- [ ] material causal transitions have owners, and relevant entities or
  processes have dispositions or bounded representation gates;
- [ ] shared ownership and information boundaries prevent scenario, mapping,
  implementation, or known outcomes from scripting participant behavior or
  results; and
- [ ] the next legal action and its entry conditions are named.

Apply the [phase closeout checklist](phase-closeout-checklist.md). Record the
result in this brief or an existing acceptance decision rather than creating a
parallel status document.

## Conditional extensions

Use these only when triggered:

| Trigger | Add or link |
|---|---|
| New external research, conflicting claims, or restricted evidence | Research brief, source strategy, evidence ledger, and exposure record from `historical-evidence-research`. |
| A representation would materially change the event model | A short representation-gate study and owner decision. |
| Several production batches need a stable shared authority | A versioned research roster and semantic skeleton. |
| Material structural interpretations compete | Named alternatives for later Scenario Definition; do not build a variant matrix here. |
| Privacy, security, legal, or sensitive operational material is present | Source-custody and publication restrictions appropriate to that material. |
| A strict calibration, held-out, evaluation, or validity claim is proposed | A separately authorized protocol; do not infer it from ordinary event construction. |

An accepted change to the question, interval, causal ownership, roster
disposition, or claim boundary uses a reviewed successor. Evidence refinement
inside the accepted boundary may update its own authority without rewriting
this brief.
