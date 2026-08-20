---
name: h2epr-agent-definition-review
description: Conduct an independent substantive review of an H2EPR Agent Definition as a historical, institutional, behavioral, and publication-facing model. Use after authoring and before reference-candidate freeze or implementation mapping; checks evidence, representation, theory, information, state, mechanisms, intents, parameters, cases, uncertainty, falsifiability, scholarly quality, and cross-agent consistency without treating format or engineering tests as scientific validity.
---

# Agent Definition review

Use this skill to decide whether an H2EPR Agent Definition is ready to serve as
a reference research artifact. Review the model first on its own historical and
behavioral terms. Runtime conformance, code quality, and simulation outcomes
belong to later and separate reviews.

The reviewer should be able to reject a polished document when its evidence,
institutional representation, mechanism, or falsifiability is weak. The review
should also preserve well-founded uncertainty instead of demanding invented
precision.

## Required inputs

Obtain:

- the exact Agent Definition candidate and semantic version;
- participant behavior dossier and its readiness review;
- evidence ledger, adopted-source register, use/exposure partition, and
  unresolved claims;
- cited original theory and empirical sources;
- relevant scenario concepts or shared decision situations, without using
  runtime output to rationalize the Definition;
- authoring content-coverage and consistency record;
- comparison Definitions when cross-role consistency is in scope;
- review question, audience, and allowed evidence boundary.

If the review would require opening new sources or held-out material, pause and
obtain the necessary research authorization. A review mandate does not by
itself authorize new evidence acquisition.

## Review principles

- Judge claim-to-model fit, not source count.
- Judge institutional behavior, not historical-name realism.
- Judge causal and decision meaning, not document length.
- Judge parameter identifiability, not numerical density.
- Judge falsifiable predictions, not narrative plausibility.
- Judge public scholarly readability, not internal project fluency.
- Judge the canonical Definition without giving credit for behavior that
  exists only in code, prompts, tests, or private author explanations.
- Distinguish model failure, evidence gap, representation failure, and later
  implementation nonconformance.

## Workflow

### 1. Identify the review object and claims

Record the Definition identity, version, event scope, participant boundary,
candidate status, evidence exposure, and the scientific or modeling claims the
document makes. List claims it explicitly does not make.

Review a stable candidate. If the author changes it during review, close the
current findings against the reviewed version and start a new review pass.

### 2. Read the Definition without implementation material

First read the Definition, behavior dossier, ledger, and cited research without
runtime code or binding details. Determine whether an independent domain reader
can understand and challenge the participant model on its own terms.

Record ambiguities rather than resolving them from code. If code is necessary
to learn what the participant observes or does, the Definition is incomplete.

### 3. Review evidence, time, and theory

Check that material historical and institutional claims resolve to appropriate
sources; theory and empirical mechanisms use original works; source scope is
not broadened; participant-time information is admissible; exposed outcomes are
declared; and assumptions, analogies, estimates, disputes, and facts remain
distinct.

Read [`substantive-review-rubric.md`](references/substantive-review-rubric.md).

### 4. Review representation and institutional fidelity

Examine the historical entity, modeled decision interface, aggregation,
authorized voice, governance, membership, duties, procedure, resource control,
relationships, informal discretion, excluded actors, and split triggers.

Challenge generic personality constructs that may be standing in for an
institutional process. Ask whether a coarser or finer representation would
make different, testable predictions.

### 5. Review behavioral mechanisms and decision semantics

For every major mechanism and Decision Commitment, verify:

- evidence and theory basis;
- event applicability and boundary conditions;
- participant-available observations and private state;
- authority, alternatives, precedence, minimum response, fallback, and a
  bounded abstention rule;
- the selection basis and remaining freedom when more than one intent is
  permitted;
- domain intent and environment-owned result;
- competing explanation;
- observable implication and falsifier.

Reject mechanisms that only restate the known historical outcome or translate
an implementation branch into prose.

### 6. Review information, state, parameters, and cases

Check world/observation/state/belief separation, participant-available time,
missing and stale behavior, persistent-state updates, parameter meaning and
evidence status, mathematical correctness, worked-case arithmetic, and
coverage of boundary situations. Test whether an always-wait or always-abstain
implementation could satisfy every commitment; if so, the behavioral model is
underdetermined even if its intent catalogue is rich.

For a strong rule fitted to an exposed action, verify that the Definition calls
it an event-specific calibration hypothesis and withholds prediction,
validation, and cross-event claims. For structural alternatives, verify that a
shared fixed boundary is outside the fork, the baseline and sensitivity roles
are explicit, and absence of evidence has not been rewritten as proof of
prohibition.

Apply the adversarial checks in
[`adversarial-and-minimality-review.md`](references/adversarial-and-minimality-review.md).

### 7. Review scholarly quality

Assess whether the Definition can function as a paper or supplementary-method
artifact:

- coherent narrative and explicit research question;
- precise historical and domain terminology;
- complete, nearby, and accurate citations;
- sufficient depth without repetitive compliance prose;
- readable tables and defined notation;
- transparent limitations and competing interpretations;
- absence of internal code, test, Git, binding, and work-window detail;
- claims calibrated to the evidence and pilot scope.

### 8. Review cross-section consistency

Trace observations to mechanisms, mechanisms to decisions, parameters to
cases, intents to decision situations, evidence to claims, and falsifiers to
concrete revision consequences. Identify orphan content and hidden
dependencies.

Content that has no explanatory, behavioral, evidentiary, or review consumer
should be removed or identified as contextual narrative rather than mandatory
model semantics.

### 9. Review cross-agent consistency when applicable

Compare participants using
[`cross-agent-and-publication-review.md`](references/cross-agent-and-publication-review.md).
Require the same methodological standard, evidence discipline, semantic
distinctions, and scholarly quality, but do not force institutions with
different roles into identical sections, variables, or decision algorithms.

### 10. Write findings and verdict

Report the strongest supported aspects, then findings ordered by consequence.
For each finding give the evidence, why it matters, required revision, and
where the work must return: Definition editing, behavior research, evidence
research, or participant representation.

Use [`review-report-and-verdict.md`](references/review-report-and-verdict.md).

## Finding severity

- **Blocking** — the Definition makes a material unsupported claim, violates
  the evidence/time boundary, uses an indefensible participant
  representation, lacks a central behavioral mechanism, confuses intent with
  result, or cannot be falsified.
- **Major** — a behaviorally important section is ambiguous, internally
  inconsistent, weakly sourced, underdeveloped, or not independently
  reviewable.
- **Minor** — a localized clarity, terminology, citation, example, or
  organization problem that does not change the core model.
- **Observation** — a nonmandatory improvement or future research opportunity.

Do not convert these categories into a numerical score unless a later research
protocol defines what the score means and how reliability is established.

## Outputs

A complete review produces:

1. review identity and evidence boundary;
2. concise model and claim summary;
3. strongest contributions and strongest counterargument;
4. severity-ranked findings with exact evidence and revision paths;
5. cross-section and, when applicable, cross-agent consistency results;
6. unresolved evidence and alternative-mechanism register;
7. publication-readiness and Definition-readiness verdict;
8. a rereview checklist tied to the findings.

## Stop conditions

Stop and report when:

- the candidate changes materially during review;
- required sources, ledger records, or the behavior dossier are missing;
- the reviewer would need unauthorized network, archive, private, Reference,
  or held-out access;
- implementation or simulation output is being used to fill a missing
  Definition mechanism;
- the review question expands to scenario validity, runtime conformance,
  Rule/LLM quality, or event-level evaluation without a separate mandate;
- a material owner decision is needed to change the participant scope or
  scientific claim.

A rigorous review may return the work to an earlier stage. That is a useful
result, not a failure of the workflow.
