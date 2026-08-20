# Definition content and style

An H2EPR Agent Definition is both a canonical behavioral specification and a
scholarly model description. Its form should make the participant intelligible
to domain readers while preserving enough precision for independent backend
implementation and review.

## Content coverage

The following content adapts the mature MASim Agent Definition pattern and adds
the historical and institutional requirements of H2EPR. Use the ten stable
top-level modules in the public Agent Definition template so readers can locate
the same kind of material across participants. Role-specific subsections,
mathematics, parameter tables, and structural alternatives remain conditional;
omissions within a module should be deliberate and explained.

### 1. Model overview

- clear participant and event title;
- stable Definition identity and semantic version;
- concise summary of what the participant represents and why it matters;
- modeled interval, focal decision situations, and explanatory scope;
- candidate/review/release and evidence-exposure status;
- claims explicitly outside the Definition.

### 2. Historical participant and representation

- historical identity and organizational setting;
- represented decision interface;
- included and excluded people, offices, committees, members, or processes;
- aggregation rationale, suppressed heterogeneity, and split triggers;
- distinction between legal entity, decision maker, and modeled Agent.

### 3. Evidence and theoretical foundation

- event-specific evidence and important disputes;
- original theory and empirical foundations;
- evidence-to-mechanism translation;
- analogies and their transfer limits;
- explicit modeling assumptions;
- exposed outcomes and use restrictions.

### 4. Institutional role and relationships

- mandate, duties, membership, jurisdiction, and obligations;
- formal and informal authority;
- governance, approval, delegation, examination, or review procedure;
- resources owned, controlled, coordinated, requested, or merely observed;
- counterparties and communication relationships;
- non-overridable constraints and role-specific priorities.

### 5. Decision situations, information, and state

- research questions the Agent helps answer;
- event phases or decision situations in which it is active;
- boundary conditions and non-applicable situations;
- what process differences the representation is expected to reveal.
- participant-available observations and explicitly forbidden information;
- semantic type, unit, domain, granularity, freshness, uncertainty, and missing
  behavior where meaningful;
- world state versus participant observation;
- persistent private decision state and its legitimate update conditions;
- qualitative or quantitative beliefs only when behaviorally necessary;
- information-to-decision consumption map.

### 6. Behavioral model

- candidate mechanisms and competing explanations;
- causal process and boundary conditions;
- Decision Commitments for focal situations;
- authority, alternatives, precedence, conflict handling, fallback, and
  abstention;
- minimum response, selection basis, and the conditions that make abstention
  legitimate;
- domain-level action and communication repertoire;
- separation of intent, delivery, admissibility, execution, and result;
- behavioral properties, invariants, and expected heterogeneity.

### 7. Intent and result boundary

- reader-facing action and communication meanings with stable semantic names;
- authority, targets, required content, and lifecycle;
- duplication, expiry, cancellation, and follow-up;
- environment-owned delivery, admissibility, execution, and result;
- invalid or unauthorized attempts retained for review.

### 8. Operationalization and uncertainty

- mathematical or procedural representation where informative;
- defined symbols, units, domains, and assumptions;
- parameter meaning, evidence status, range or ordering, and sensitivity;
- structural uncertainty kept separate from numerical uncertainty;
- no requirement to invent an equation for qualitative institutional
  procedure.

### 9. Worked cases and falsification

- multiple cases covering ordinary and boundary behavior;
- observed/reconstructed/illustrative/counterfactual labels;
- participant-available information, required response, intent, and environment-owned result;
- role, authority, information, lifecycle, mechanism, and parameter
  perturbations;
- expected and forbidden process patterns;
- calibration and validation use stated without circularity.

### 10. Limitations, references, and provenance

- historical gaps and disputed claims;
- aggregation, mechanism, parameter, and external-validity limits;
- unmodeled actors and processes;
- falsifying evidence and Definition withdrawal conditions;
- complete scholarly references;
- semantic version history and design rationale.

## Writing style

Write in the style of a clear methods paper or supplementary model
specification:

- open each major section with the substantive claim, not a process disclaimer;
- define technical and historically specific terms at first use;
- prefer active, precise sentences;
- use tables for repeated mappings and prose for causal explanation;
- keep citations close to the claims they support;
- distinguish evidence, inference, assumption, and design choice without
  prefixing every sentence with a status label;
- explain uncertainties directly rather than surrounding the document with
  repeated “not a validation” language;
- use domain vocabulary rather than internal project shorthand when a public
  term is available;
- keep enough detail that the model can be reconstructed and criticized.

Avoid generic AI-style headings such as “one-sentence positioning,” repetitive
negative disclaimers, promotional claims, and lists that substitute for an
argument.

## Tables and notation

Tables are useful for:

- claim-to-mechanism mappings;
- observation and information boundaries;
- governance and authority relations;
- parameters and uncertainty;
- Decision Commitments;
- worked-case comparisons;
- behavioral predictions and falsifiers.

Do not force narrative evidence or institutional history into a table when the
relationships require explanation. Define mathematical notation before use and
keep symbols consistent across equations, tables, and cases.

## Canonical semantics versus derived implementation

The Definition may specify:

- domain concepts and semantic names;
- types, units, domains, ordering, and missing behavior needed to understand
  behavior;
- domain-level intents and their lifecycle;
- state meaning and valid conceptual transitions;
- observable process predictions.

Keep these in a derived implementation mapping:

- Python, prompt, policy, adapter, and reducer identifiers;
- JSON keys and serialization mechanics;
- repository paths, content hashes, and binding catalogs;
- validation code and test matrices;
- fixture values chosen only for an engineering path;
- performance, deployment, and environment configuration.

The mapping must derive from the Definition, but the Definition should remain
readable and authoritative without it.
