---
name: h2epr-participant-behavior-research
description: Develop a historically grounded, institutionally explicit, publication-facing behavior model for an H2EPR participant from an adjudicated evidence set. Use after historical evidence research and before drafting an Agent Definition or population model; covers representation, information, private state, mechanisms, choices, uncertainty, cases, and falsifiers without writing runtime code.
---

# Participant behavior research

Use this skill to explain how a real-event participant is represented and why
that participant may act as modeled. The output is a scholarly behavior record
that can support an Agent Definition or population model and can be challenged
by evidence.

For a standard row, this may be a compact combined working record whose
applicable parts feed the accepted participant product. Use a separate, fuller
dossier for a deep row only when a material representation, causal, or evidence
judgment benefits from it.

This stage sits between evidence adjudication and participant-product
authoring. It does not turn historical outcomes into rules, design the whole
scenario, or translate the model into backend code.

## Required inputs

Establish:

- event identity, modeled interval, and focal decision time or times;
- participant, institutional decision interface, or population choice unit
  under study;
- research question and intended explanatory scope;
- adopted claim records, source register, use partition, and exposure record;
- material unresolved or conflicting claims;
- relevant original theory and empirical sources already verified;
- known scenario-owned institutions, relations, resources, and information
  channels;
- output location and review audience.

If material claims have not passed evidence review, return to
[`historical-evidence-research`](../historical-evidence-research/SKILL.md).
Do not hide missing evidence inside a personality score, precise threshold, or
plausible-sounding narrative.

## Workflow

### 1. Fix the explanatory target

State which decisions or process patterns the participant model is intended to
explain. Prefer a small number of high-information situations over an entire
biography or a generic profile.

Separate:

- participant behavior that this model aims to explain;
- world conditions supplied by the scenario;
- other participants' choices;
- results determined by institutional and environmental adjudication;
- later outcomes used only as exposed context or future evaluation.

### 2. Define the represented actor

Explain whether the participant is a person, office, management group,
committee, firm, association, public body, population choice unit, or another
decision interface. For an institution, identify who can speak or act for it,
which internal actors are aggregated, what disagreement is suppressed, and
what evidence would require a finer representation. For a population, define
the unit, retained heterogeneity, host boundaries, and split triggers without
inventing a collective voice.

Read
[`participant-scope-and-governance.md`](references/participant-scope-and-governance.md).

### 3. Reconstruct the institutional position

Describe mandate, duties, authority, prohibitions, governance procedures,
resource control, membership, counterparties, and communication channels.
Distinguish formal authority, observed practice, inferred discretion, and
modeling simplification.

Do not replace institutional procedure with generic risk tolerance,
willingness, confidence, fear, or benevolence unless those constructs have a
defined meaning, evidence base, observable implications, and update process.

### 4. Map evidence and theory to candidate mechanisms

For each behaviorally material mechanism, record:

- the general theoretical or empirical basis;
- event-specific claims that make the mechanism applicable;
- the translation from evidence to modeled behavior;
- competing mechanisms or interpretations;
- parameters or qualitative distinctions required;
- predictions and evidence that would weaken or reject it.

Theory proposes a mechanism; event evidence determines whether and how it may
apply to this participant. Read
[`theory-and-mechanism-mapping.md`](references/theory-and-mechanism-mapping.md).

### 5. Specify the participant's epistemic position

Describe what the participant can observe, through which channel, at what
time, in what form, with what delay or uncertainty, and what remains hidden.
Separate authoritative world state, legal observation, modeled private state,
belief or qualitative assessment, and later delivered results.

Only introduce persistent private state when it is necessary to explain later
behavior. State its meaning, initialization basis, update conditions, and
observable consequences. Do not assign precise subjective probabilities when
the evidence supports only an ordering, interval, qualitative judgment, or
unknown state.

### 6. Analyze decision situations

Begin with the smallest set of high-information situations needed to expose
the participant's material mechanisms and boundaries. Add another only when it
contributes a distinct mechanism, authority boundary, information problem, or
behavior.

For each situation, examine:

- entry conditions and relevant history;
- legal observations and missing or stale information;
- relevant private state;
- authority and procedural preconditions;
- available alternatives and prohibited actions;
- goals, duties, precedence, and conflict handling;
- fallback, information seeking, delay, escalation, or abstention;
- typed action or message intents the participant may issue;
- results that remain outside the participant's control;
- expected and forbidden process patterns;
- a counterexample or perturbation that challenges the mechanism.

Read
[`decision-situations-and-behavior.md`](references/decision-situations-and-behavior.md).

### 7. Treat parameters and uncertainty honestly

Classify each behaviorally material quantity as observed, reconstructed,
estimated, bounded, ordinal, sensitivity-only, disputed, or unidentified.
Give the unit and applicable range when meaningful. Explain why the quantity
changes behavior and which evidence constrains it.

Keep parameter uncertainty, uncertain world state, uncertain participant
belief, competing mechanisms, and conflicting historical evidence separate.
Do not average structural alternatives into a single confidence score.

### 8. Write the scholarly behavior record

Present a coherent account that a historian, domain scholar, modeler, and
implementation reviewer can read without consulting source code. Use concise
tables where they clarify evidence, information, authority, mechanisms, or
decision situations, but retain enough prose to explain causal reasoning and
historical context.

The record should include the applicable citations and claim references,
assumptions and limitations, cases, alternative explanations, and explicit
falsification conditions. Use
[`behavior-dossier-and-review.md`](references/behavior-dossier-and-review.md).

### 9. Review before Definition authoring

Review the dossier for:

- evidence and temporal admissibility;
- defensible participant aggregation;
- institutional and governance fidelity;
- mechanism clarity and competing explanations;
- complete information and decision boundaries;
- separation of intent from result;
- parameter honesty;
- scholarly readability and citation quality;
- predictions, falsifiers, and representation split triggers;
- absence of code, backend, file-hash, test, and serialization detail from the
  publication-facing account.

Resolve the review as `READY_FOR_DEFINITION_DRAFT`,
`READY_FOR_POPULATION_MODEL_DRAFT`, `READY_WITH_EXPLICIT_ALTERNATIVES`,
`MORE_EVIDENCE_REQUIRED`, or `REPRESENTATION_RECONSIDERATION_REQUIRED`, and
explain the consequence. Use the first two only for their matching
representation routes.

## Outputs

A complete run closes the applicable behavior responsibilities:

1. an explanatory-scope statement;
2. a participant representation and aggregation rationale;
3. an institutional governance, authority, resource, and relationship model;
4. a theory-to-evidence-to-mechanism map;
5. an observation, private-state, and belief analysis;
6. a portfolio of high-information decision situations;
7. parameter and structural-uncertainty records;
8. worked cases, behavioral predictions, counterexamples, and falsifiers;
9. a publication-facing participant behavior record;
10. a substantive review and readiness verdict.

These are coverage responsibilities, not ten required documents or a fixed
case count. A standard row may combine them in one working record and refer to
shared evidence records rather than copying them. The accepted Agent
Definition or population model selects the canonical behavioral content;
later conformance work maps that product to executable backends.

## Stop conditions

Stop and state the boundary when:

- the participant or institutional decision interface cannot be identified;
- the proposed behavior depends on authority, information, or resources that
  have not been researched;
- decisive claims are unavailable, contradicted, or restricted to a different
  evidence use;
- an aggregate institutional Agent suppresses internal differences that are
  necessary to explain the focal decisions;
- a candidate mechanism has no event-specific applicability evidence and
  cannot be retained honestly as an explicit assumption or alternative;
- the behavior can only be produced by importing a known later outcome;
- the next step would require scenario, contract, backend, Rule, LLM, or
  simulation design outside the authorized task.

An unresolved mechanism can remain as a named alternative. A missing
institutional foundation cannot be repaired by adding narrative detail.
