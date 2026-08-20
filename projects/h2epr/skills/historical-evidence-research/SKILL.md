---
name: h2epr-historical-evidence-research
description: Research historical, institutional, empirical, and scholarly evidence for an H2EPR participant or decision situation, producing claim-level records with explicit event-time, participant-availability, use, exposure, conflict, and uncertainty boundaries. Use before participant behavior modeling or Agent Definition authoring; external search and held-out access still require their own authorization.
---

# Historical evidence research

Use this skill to turn a bounded historical question into evidence that can
support an H2EPR participant, scenario, behavioral mechanism, parameter range,
or falsification claim. The result is an auditable research record, not a
biographical narrative or a collection of links.

## Required inputs

Establish these inputs before searching:

- event identity and modeled time window;
- participant, institution, relation, or decision situation under study;
- the exact modeling question;
- intended evidence uses;
- already exposed outcomes or sources;
- authorized local and external source boundaries;
- output location and source-archive policy.

Read [research-brief-and-source-strategy.md](references/research-brief-and-source-strategy.md)
when defining or reviewing these inputs.

If external research has not been authorized, complete the brief and local
source inventory, then stop before making network requests. Authorization for
one historical gap does not carry over to a new participant, mechanism, event,
or evidence use.

## Workflow

### 1. Frame the research question

Write questions that can change a model decision. Prefer:

> What authority and procedure governed this institution's response to this
> request at the modeled time?

over:

> What happened in the panic?

Split compound questions into claim families such as identity, membership,
authority, governance, information, resources, available actions, decision
process, timing, and observed response.

### 2. Build a claim-appropriate source strategy

Select sources according to the claim, not according to a universal venue
ranking. Institutional authority may require a constitution, amendment,
minutes, testimony, or official report. Contemporaneous knowledge may require
correspondence, newspapers, directories, balance sheets, or public statements.
Behavioral mechanisms may require scholarly theory and empirical studies.

Use both reactive search for known materials and proactive search for missing
source classes, terminology, cited records, and competing interpretations.

Read [research-brief-and-source-strategy.md](references/research-brief-and-source-strategy.md)
for source classes, query design, selection rules, and stopping criteria.

### 3. Read before adopting

Open the primary document or a stable faithful reproduction. Read enough
context to determine what the source actually establishes, who produced it,
when it was produced, and which participant could have known it.

Search results, snippets, catalogue metadata, third-party summaries, and links
that were never opened may help discovery; they are not adopted evidence.

For each adopted source, create a source record and atomic claim records. Use
[source-reading-and-claim-extraction.md](references/source-reading-and-claim-extraction.md).

Keep consulted but unused sources in the research log with a reason such as
redundant, locator only, target record absent, inaccessible, or insufficient
for the claim. Do not archive them as adopted evidence.

### 4. Separate time and use

For every behaviorally material claim, distinguish:

- when the underlying event or condition occurred;
- when the modeled participant could have known it;
- when the source became available to researchers;
- when the H2EPR research process accessed it;
- how the claim may be used in the current model version.

Read [temporal-and-use-boundaries.md](references/temporal-and-use-boundaries.md)
before classifying runtime-visible information, later outcomes, calibration
evidence, or held-out candidates.

### 5. Adjudicate, do not average away disagreement

Classify each atomic claim as directly supported, supported with bounded
inference, estimated, disputed, contradicted, unresolved, or unavailable. Name
the competing propositions when sources support materially different models.

Do not convert structural uncertainty into a confidence score or probability
unless the evidence and research question justify that representation. A hard
institutional prohibition and a discretionary member-priority policy are
different mechanisms, not two nearby parameter values.

### 6. Connect evidence to model use

Record exactly what the claim could support:

- participant identity or representation;
- institutional governance or authority;
- observation availability;
- resource or relationship state;
- behavioral mechanism selection;
- parameter or state bounding;
- scenario construction;
- worked case or falsifier;
- future evaluation only.

Do not write a decision rule merely because a historical outcome is known. A
claim can constrain a mechanism without determining a unique action.

Project decisions define research scope, ownership, and allowed uses; they are
not historical evidence about the participant. Advisory reviews and literature
maps can identify relevant theory, but publication-facing theoretical claims
must be checked against the cited original paper, book, dataset, or authoritative
edition before adoption.

### 7. Archive adopted sources

Archive only sources that actually enter claim adjudication when archival
permission and storage are available. Preserve the original bytes or a clearly
labeled faithful capture, record the locator and retrieval date, and compute a
content hash. Derived notes must remain distinguishable from raw source files.

### 8. Review and close the question

Use [evidence-review.md](references/evidence-review.md) to inspect source fit,
claim atomicity, temporal admissibility, conflict handling, model-use scope,
and exposure. Close each research question with one of:

- `RESOLVED_FOR_STATED_USE`;
- `BOUNDED_UNRESOLVED`;
- `INSUFFICIENT_EVIDENCE`;
- `EVIDENCE_UNAVAILABLE_WITHIN_AUTHORIZED_SCOPE`.

The verdict applies only to the stated question and use. It does not certify a
whole participant or event as historically valid.

## Outputs

A complete run normally produces:

1. a research brief and source strategy;
2. a source register;
3. claim-level evidence records;
4. an unresolved and conflicting evidence register;
5. explicit evidence-use and exposure classifications;
6. an adopted-source archive or stable locators, as permitted;
7. a concise research closure stating what is and is not supported.

Project-specific paths and serialization belong to the working context. This
skill defines the research semantics, not a required file tree or JSON schema.

## Stop conditions

Stop and report the boundary when:

- the next useful source lies outside the authorized network, archive, payment,
  privacy, secret, or held-out boundary;
- a source can only be located through an inaccessible or unverifiable copy;
- the research question has expanded to a new event, participant, mechanism,
  or use class;
- later outcome evidence would contaminate a claimed held-out partition;
- sources remain materially contradictory after the planned search strategy;
- the model would require an invented actor, authority, parameter, or decision
  process to proceed.

Unresolved evidence is a research result. Preserve it in the model as an
unknown, bounded alternative, sensitivity branch, or scope limitation.
