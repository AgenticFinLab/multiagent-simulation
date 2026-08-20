# Temporal and evidence-use boundaries

Historical event modeling requires more than a publication date. A claim can
be true, well sourced, and still be illegal input for a participant at the
modeled decision time.

## Time dimensions

Track the dimensions that affect the claim.

| Time | Question |
|---|---|
| Event time | When did the condition, communication, decision, or result exist in the historical world? |
| Participant-available time | When could the modeled participant have learned it through an allowed channel? |
| Source-production time | When was the source created, amended, published, or recorded? |
| Research-available time | When did the current model-building process obtain the source or claim? |

Use intervals and uncertainty markers when exact timestamps are unavailable.
Do not collapse “occurred,” “was recorded,” “became public,” and “was known to
this participant.”

## Participant availability

For any candidate observation, identify:

- information content;
- sender, observer, publication, or institutional channel;
- intended audience and access rights;
- delivery or publication time;
- expected lag, freshness, and possible staleness;
- whether the participant receives exact values, ranges, qualitative reports,
  rumors, or no signal;
- provenance that the runtime observation should preserve.

Simulator world state is not Agent knowledge. A researcher having a balance
sheet, committee record, or later reconstruction does not imply the historical
participant saw it.

## Evidence-use classes

Use one or more explicit classes when they are compatible.

| Use class | Meaning |
|---|---|
| Identity and representation | Defines the entity, organizational level, or modeled decision interface. |
| Construction | Supports event-specific state, relation, institution, or allowed observation. |
| Mechanism selection | Supports a candidate behavioral or organizational process. |
| Parameter bounding | Constrains a quantity, interval, ordering, sensitivity, or qualitative level. |
| Scenario semantics | Supports environment rules, exogenous events, adjudication, timing, or termination. |
| Worked case | Supplies a transparent illustrative situation without acting as independent validation. |
| Falsification claim | Defines an observation that would contradict or narrow the model. |
| Evaluation only | Reserved for post-freeze or post-seal assessment and prohibited from model construction. |
| Context only | Improves explanation but does not determine model behavior. |

A claim's use must be narrower than or equal to what its source and temporal
status support. General theory may motivate a mechanism; it cannot establish
that a named institution used it. A known historical outcome may illustrate a
case; it cannot be hidden and then presented as held-out validation.

## Exposure classes

Record what the model authors and backends have already seen. Project-specific
labels may differ, but they should distinguish at least:

- not accessed in the current model-building process;
- accessed for source discovery only;
- adopted for construction or mechanism design;
- full-draft or outcome exposed;
- reserved for later evaluation;
- evaluation-exposed and no longer held out.

Once evidence has shaped a Definition, prompt, Rule, state, parameter, or
scenario, it cannot validate that same version as unseen evidence.

## Outcome and suffix leakage

Later event outcomes can enter research in several legitimate ways:

- as explicitly exposed background;
- as construction evidence for an exploratory model;
- as a worked historical case;
- as evaluation evidence for a successor model after a predeclared freeze.

Label the use. Never let later outcomes appear in a participant observation,
behavioral rationale, retrieval corpus, or hidden backend context when they
were unavailable at the decision time.

If full-event materials have already been read, do not manufacture a held-out
set by relabeling remembered claims. A future event, a different time segment,
a genuinely unexamined source class, or pre-registered process patterns may be
needed for stronger evaluation.

## Conflicting temporal accounts

When sources disagree on timing:

1. retain each sourced interval;
2. record clock, timezone, edition, reporting lag, and retrospective status;
3. identify which decision situations change under each interval;
4. use an interval or explicit scenario branch if the difference is material;
5. avoid selecting the timestamp that makes the desired causal order work.

## Use-partition review

Before participant behavior research begins, verify:

- every adopted claim has an allowed use;
- every runtime-visible information claim has participant availability;
- evaluation-only claims have not influenced the current model;
- exposed outcomes are labeled in worked cases and interpretation;
- competing mechanisms remain separate when evidence has not resolved them;
- a future reviewer can reconstruct which evidence shaped each behavioral
  mechanism.
