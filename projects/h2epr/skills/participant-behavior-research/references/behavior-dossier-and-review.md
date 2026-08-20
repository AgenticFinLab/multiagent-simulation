# Behavior dossier and review

The participant behavior dossier is a publication-facing model specification.
It should be readable as serious historical and behavioral modeling work before
any runtime implementation is considered.

## Recommended content

Section titles and order may follow the participant and paper. Cover the
following content when it is behaviorally material.

### Research scope and historical setting

State the event interval, focal decisions, explanatory target, and the limits
of the dossier. Identify outcomes or sources already exposed during model
development.

### Participant identity and representation

Explain the historical entity, modeled decision interface, included and
excluded internal actors, aggregation rationale, and split triggers.

### Institutional role and governance

Describe mandate, membership or jurisdiction, duties, authority, decision
procedure, resource control, counterparties, and informal discretion. Mark
formal rules, observed practices, interpretations, and simplifications.

### Evidence and theoretical foundations

Summarize the claim families and original theoretical or empirical works used.
Explain what each source supports and where evidence remains disputed or
insufficient. Cite sources in a conventional scholarly form and link important
model statements to claim records.

### Behavioral mechanisms

Explain the candidate mechanisms, event applicability, causal process,
boundary conditions, competing explanations, and observable implications. Do
not present a theory citation as proof that the historical participant followed
the theory.

### Information environment

Describe observable information, prohibited information, channels, timing,
freshness, granularity, uncertainty, missing-information behavior, and the
difference between researcher knowledge and participant knowledge.

### Private state and belief

Define only the persistent state and assessments needed for behavior. Explain
initialization, update conditions, duration, decision effect, uncertainty, and
observable consequences.

### Goals, duties, authority, resources, and relationships

Show how institutional constraints and role-specific priorities shape the
choice set. Distinguish owning, controlling, coordinating, requesting, and
observing a resource.

### Decision situations and commitments

Present the high-information situations and the participant's alternatives,
precedence, fallbacks, abstention, intents, expected process patterns, and
falsifiers. Provide enough detail for an independent reader to challenge the
behavior without translating it into code.

### Action and communication repertoire

Describe the meanings and prerequisites of actions and messages at the domain
level. Separate attempted intent, delivery, institutional admissibility,
execution, and result.

### Parameters and uncertainty

Record meaning, units or ordering, evidence status, plausible bounds,
sensitivity role, and structural alternatives. Avoid decorative precision.

### Worked cases and behavioral predictions

Use observed, reconstructed, illustrative, and counterfactual cases to show
the model in operation. State what should change under role, authority,
information, resource, or mechanism perturbations.

### Assumptions, limitations, and unresolved questions

Name historical gaps, aggregation losses, unmodeled processes, analogy risks,
unidentified parameters, disputed mechanisms, and claims that would force a
revision.

### References

Provide stable, complete scholarly citations. A repository claim ID supports
auditability but does not replace the bibliography a paper reader needs.

## Keep implementation material separate

The publication-facing dossier should not contain:

- Python class or function names;
- repository-relative runtime binding paths;
- file hashes and seal identities;
- fixture, unit-test, or validator mechanics;
- JSON serialization details;
- backend prompts or Rule conditionals;
- temporary work-window status;
- claims that passing an engineering test proves historical validity.

Later conformance artifacts may cite the dossier and canonical Agent
Definition while recording those details separately.

## Substantive review

### Historical and evidential grounding

- Do the adopted sources support the claims and uses assigned to them?
- Are original theory and empirical sources cited directly?
- Are later outcomes and participant-time information distinguished?
- Are disputed claims and dependent source chains visible?
- Are assumptions labeled instead of written as facts?

### Representation and institutional fidelity

- Is the modeled actor a defensible decision interface?
- Are governance, authorization, membership, procedure, and resource control
  more informative than generic personality labels?
- Are aggregation losses and split triggers explicit?
- Are omitted intermediaries and institutional processes named?

### Behavioral sufficiency

- Do the mechanisms explain decisions beyond restating the known outcome?
- Are information, state, alternatives, precedence, fallback, and abstention
  sufficiently clear?
- Are persistent states behaviorally necessary and updateable from legitimate
  information?
- Are actions intents rather than self-realizing results?
- Are the selected decision situations informative and nonredundant?

### Uncertainty and alternatives

- Are parameter uncertainty, belief uncertainty, mechanism uncertainty, and
  historical dispute separated?
- Are precise values warranted?
- Do competing mechanisms remain visible when evidence cannot choose between
  them?
- Does the model state how it behaves under unknown or missing information?

### Scholarly quality

- Can the document stand as a clear methods or supplementary-material artifact?
- Does prose explain the causal argument rather than merely introduce tables?
- Are terms defined consistently and historically?
- Do citations support nearby claims?
- Are worked cases readable without code?
- Does the document avoid internal project-management and implementation
  language?

### Falsifiability and diagnostic value

- Does every important mechanism imply a process pattern or behavior that
  could fail?
- Are forbidden observations and actions explicit?
- Are role, authority, information, lifecycle, and mechanism perturbations
  meaningful?
- Can later reviewers distinguish a participant-model failure from a scenario
  or environment failure?
- Would withdrawing a key claim produce a known revision?

## Readiness verdicts

### `READY_FOR_DEFINITION_DRAFT`

The representation, evidence, mechanism, information, decisions, uncertainty,
and falsification account are coherent enough to standardize into a canonical
Agent Definition. Remaining limitations do not change the core representation
or legal intent envelope.

### `READY_WITH_EXPLICIT_ALTERNATIVES`

The dossier is sufficiently grounded, but two or more evidence-bounded
mechanisms or institutional interpretations must remain explicit. Definition
authoring may proceed only if it preserves the alternatives rather than
selecting one silently.

### `MORE_EVIDENCE_REQUIRED`

A material authority, information, mechanism, parameter, or historical claim
lacks adequate support. State the exact question, useful source classes, and
which part of the dossier cannot proceed.

### `REPRESENTATION_RECONSIDERATION_REQUIRED`

The proposed participant boundary suppresses an actor, governance process,
relationship, or heterogeneity needed to answer the research question. Revisit
the representation before enriching the narrative.

## Review record

A concise review should report:

```text
participant=
modeled_interval=
explanatory_target=
representation=
evidence_boundary=
mechanisms=
decision_situations=
material_uncertainties=
strongest_counterexample=
publication_readiness=
definition_readiness=
verdict=
required_revision=
```

The verdict is a readiness judgment for the next modeling stage. It is not a
claim that the participant, event, or simulation is historically validated.
