---
name: h2epr-agent-definition
description: Author a mature, publication-facing H2EPR Agent Definition from a reviewed participant behavior dossier and adjudicated evidence. Use to standardize one event-bound participant's representation, institutional role, theory, information, state, mechanisms, decision commitments, intents, parameters, worked cases, uncertainty, falsifiers, references, and version provenance while keeping runtime bindings and code in separate derived artifacts.
---

# Agent Definition authoring

Use this skill to turn reviewed participant research into the canonical
scholarly specification of an H2EPR Agent. The Definition must support both
Rule and future LLM implementations without becoming a prompt, code listing,
wire schema, or generic cross-event archetype.

MASim's Agent Design Handbook provides the minimum standard for theoretical
grounding, explicit information, mechanisms, parameters, worked cases,
verification, references, and cross-section consistency. H2EPR adds the
requirements of real-event modeling: historical time, claim-level evidence,
institutional governance, aggregation, participant-available information,
intent/result separation, structural uncertainty, and exposed-outcome control.

## Required inputs

Confirm that the following have been substantively reviewed:

- participant behavior dossier and readiness verdict;
- participant representation and aggregation rationale;
- evidence ledger, source register, use partition, and exposure status;
- candidate and competing behavioral mechanisms;
- observation, private-state, belief, governance, authority, resource, and
  relationship analysis;
- decision situations, worked cases, predictions, and falsifiers;
- applicable scenario concepts and machine-contract semantic types;
- Definition identity, event scope, version policy, and publication audience.

If the behavior dossier is absent or marked `MORE_EVIDENCE_REQUIRED` or
`REPRESENTATION_RECONSIDERATION_REQUIRED`, do not compensate by drafting a
more elaborate Definition. Return to
[`participant-behavior-research`](../participant-behavior-research/SKILL.md).

## Workflow

### 1. Fix identity, scope, and authority

Assign one stable identity to the participant Definition. State the event,
modeled interval, decision situations, represented interface, excluded actors,
and validity limits. Explain whether the document is a mutable candidate,
reviewed version, or released scholarly artifact.

Do not claim cross-event portability, historical calibration, prediction, or
validation unless a separate study has established it.

### 2. Build a complete content map

Before writing prose, map the reviewed research to the required content in
[`definition-content-and-style.md`](references/definition-content-and-style.md).
New candidates use the exact ten numbered top-level modules in the public
template. Role-specific subsections and the depth of optional material remain
flexible. Do not rewrite an accepted frozen release merely to normalize older
heading style.

The Definition should read as a coherent academic model, not a sequence of
compliance answers. Use tables to make dense mappings precise and prose to
explain historical context, causal reasoning, and limitations.

### 3. Establish evidence and theory foundations

Explain the original theoretical and empirical foundations, event-specific
evidence, competing historical interpretations, estimates, analogies, and
explicit modeling assumptions. Cite conventional scholarly references and link
material model statements to ledger claims.

The ledger remains authoritative for source status, event time,
participant-available time, use, exposure, conflict, and withdrawal. The
Definition explains how those claims shape behavior without copying the ledger
as a second evidence registry.

Read
[`evidence-theory-and-provenance.md`](references/evidence-theory-and-provenance.md).

### 4. Specify the represented institutional actor

Describe the historical entity and modeled decision interface; who is
aggregated and excluded; mandate, governance, authority, duties, resources,
relationships, communication channels, informal discretion, aggregation
losses, and split triggers.

Institutional constraints should explain behavior before generic personality
traits. Any psychological or preference construct must be defined, sourced,
behaviorally necessary, and connected to observable implications.

### 5. Specify the epistemic and state boundary

Define behaviorally material observations in semantic terms:

- meaning and historical source;
- participant visibility and channel;
- time, delay, freshness, and missing behavior;
- type, unit, domain, granularity, and uncertainty when meaningful;
- decisions or mechanisms that consume the information;
- information explicitly forbidden to the participant.

Use the compact observation inventory from the public template so each stable
semantic observation ID has a declared consumer. Add prose or subsections when
the source history, dispute, or institutional meaning cannot be represented
faithfully in one row. The inventory is not a copied runtime schema.

Separate world state, participant-available observation, modeled private state, belief or
assessment, and ephemeral reasoning. Define persistent state only when it
changes later behavior, and explain initialization, legitimate updates,
duration, and observable consequences.

### 6. Formalize mechanisms and Decision Commitments

Write the participant's general behavioral framework, including its decision
order and degree of determinacy, then express the focal decision situations as
falsifiable Decision Commitments. Keep model invariants separate from
provisional behavioral hypotheses.

For each commitment, make clear:

- activation and boundary conditions;
- claim and theory basis;
- participant-available information and relevant private state;
- authority and procedure;
- alternatives, duties, goals, precedence, and conflict handling;
- the minimum response required after activation;
- the selection basis when several intents remain permitted;
- fallback, information seeking, delay, escalation, and the bounded conditions
  for abstention;
- permissible domain-level action and message intents;
- expected and forbidden process patterns;
- competing mechanism and falsifier.

If a strong choice rule reproduces an already exposed event action, label it
as an event-specific calibration hypothesis. State the exact gate conditions,
the perturbations that change the response, and the claims it cannot support.
Do not present reproduction of that action as independent validation or a
cross-event behavioral law.

Read
[`behavioral-contract-and-interfaces.md`](references/behavioral-contract-and-interfaces.md).

### 7. Define intent semantics without owning results

Describe the action and communication repertoire at the domain level. State
the intended meaning, target, prerequisites, lifecycle, quantities or
categories, cancellation or expiry semantics, and prohibited self-realized
outcome.

Use the compact intent inventory from the public template so every stable
semantic intent ID is linked to at least one Decision Commitment. Keep wire
keys, carrier slots, validators, and result records in the derived mapping.

The participant may attempt, request, propose, authorize, refuse, communicate,
delay, or abstain. The environment owns delivery, institutional admissibility,
feasibility, execution, partial effect, failure, result, and authoritative
world-state transition.

### 8. Use mathematics and parameters when they add meaning

Include equations, decision rules, state transitions, probability models, or
quantitative parameters only when evidence and the behavioral mechanism
justify them. Define every symbol, unit, domain, assumption, and behavioral
interpretation.

Qualitative procedures, ordered categories, intervals, and alternative
mechanisms are valid formal specifications. Do not invent precise thresholds or
effect sizes to make the Definition look mature.

When preserving structural alternatives, separate their shared evidenced
boundary from the unresolved dimension. Name a conservative baseline and any
sensitivity variant, explain the evidence that would retire each, and do not
upgrade absence of an evidenced capacity into proof of categorical
prohibition.

### 9. Add worked cases and falsification

Use multiple worked situations to exercise normal, stressed, missing-
information, pending-state, authority-boundary, and adverse-result behavior as
applicable. Include observed, reconstructed, illustrative, and counterfactual
cases with explicit labels.

State expected process patterns, forbidden behavior, ablations, competing
explanations, and evidence or observations that would reject or narrow the
model. Read
[`worked-cases-and-falsification.md`](references/worked-cases-and-falsification.md).

### 10. Close assumptions, limitations, references, and provenance

List event-specific assumptions, unresolved claims, aggregation losses,
unmodeled actors or procedures, exposed outcomes, parameter limitations,
external-validity limits, and future evidence that would require revision.

Provide a complete bibliography and a concise design provenance/version
history. Record meaningful semantic changes and their rationale; keep Git
hashes, file hashes, runtime bindings, test output, and work-window status in
derived project records.

### 11. Perform cross-section consistency checks

Verify that:

- every observation is consumed or explicitly contextual;
- every persistent state has an initialization and legitimate update path;
- every mechanism uses declared information and produces declared intents;
- every activated commitment requires a meaningful response class or records
  a specific blocker and reopening event;
- no implementation can remain conforming through indefinite, generic
  abstention;
- every parameter appears consistently in theory, mechanism, cases, and
  uncertainty analysis;
- every intent belongs to at least one decision situation;
- every major claim has evidence or an explicit assumption label;
- worked cases obey the stated information and authority boundaries;
- limitations and falsifiers can force a concrete revision;
- no scenario value, wire schema, backend detail, or known result has become a
  hidden behavior authority.

For a new candidate, run the lightweight public-profile checker from the
repository root:

```bash
PYTHONPATH=projects/h2epr/src \
python -m h2epr.agents.definition_profile path/to/candidate.md
```

It checks the ten-module order, overview identity, observation and intent
inventories, and Decision Commitment cross-links. Treat a failure as an
authoring defect. Treat a pass only as structural readiness; it does not
replace substantive review.

## Outputs

A complete run produces:

1. one canonical event-bound Agent Definition candidate;
2. a content-coverage and cross-section consistency record;
3. a claim-to-mechanism and mechanism-to-decision traceability summary;
4. a list of unresolved alternatives and Definition withdrawal conditions;
5. an input package for independent scholarly and modeling review.

Do not produce the executable binding in the same document. A later derived
mapping may cite the frozen Definition and record runtime identifiers, types,
serialization, validators, and backend conformance.

## Stop conditions

Stop and return to research or request direction when:

- the participant representation is not defensible;
- material authority, information, mechanism, or evidence remains absent
  rather than explicitly bounded;
- the document can explain the known outcome only by importing that outcome;
- theory or parameters cannot be verified in original sources;
- the Definition and scenario both claim ownership of the same world fact or
  institutional rule;
- a requested behavior requires a new contract, backend, Rule, LLM, or
  simulation decision outside the task;
- a physical theory/Card split or cross-event abstraction is being proposed
  without repeated evidence from completed participant models.

Completeness means that the model and its limits are fully inspectable. It
does not mean filling every optional heading or eliminating every uncertainty.
