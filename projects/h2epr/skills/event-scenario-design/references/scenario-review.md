# Event Scenario review

Use this review after the Scenario Definition candidate is stable. Review the
scenario without giving it credit for behavior or safeguards that exist only
in code, configuration, tests, or a private explanation.

## Review object

Record:

- Scenario Definition identity and version;
- Scenario interface-closure identity and derived inventory counts;
- roster/release, skeleton, evidence, mapping, and contract inputs;
- research question, interval, baseline variant, and exposure status;
- claims the candidate makes and withholds; and
- review permissions and excluded evidence.

Restart the review if the candidate changes materially.

Perform the review as a separate pass. Do not give the candidate credit for
unrecorded reasoning from its authoring session.

## Substantive checks

### Boundary and causality

- Does the scenario answer a bounded event-process question?
- Are endogenous, initial, exogenous, and excluded processes distinct?
- Do phases organize opportunities without forcing the known chronology?
- Can the scenario fail to reproduce the exposed outcome?
- Are engineering, reconstruction, calibration, and validation claims kept
  separate?

### Authority and ownership

- Does every decision belong to one Agent, population, or environment process?
- Does every world fact, relationship, resource, lifecycle, and result have
  one authoritative owner?
- Are participant decision state and business truth separate?
- Do coordinators, intermediaries, committees, venues, and resource owners
  retain distinct causal roles?
- Would removing a scenario mechanism expose a real gap rather than merely
  shorten the document?

### Time and information

- Is every material input assigned an event/as-of time and production source?
- Can a participant receive it only through an allowed route and scope?
- Are issue, transport, delivery, receipt, acknowledgement, and business
  acceptance distinct where behavior depends on them?
- Are missing, stale, disputed, corrected, and unavailable states meaningful?
- Can a backend dereference hidden current state through an identifier?
- Is future, outcome, Reference, or evaluation information excluded?

### Institutions, relationships, and resources

- Are membership, mandate, jurisdiction, authorization, and procedure
  represented as institutional state rather than personality?
- Are relationships versioned and changed only through valid events?
- Does one entity retain one resource owner across multiple capabilities?
- Are reservation, commitment, transfer, partial execution, failure, and
  release distinct?
- Do conservation, exclusivity, and scope checks survive competing intents?

### Lifecycles, adjudication, and results

- Does every material business object have stable identity and valid states?
- Are duplicate, expiry, cancellation, concurrency, and reopening defined?
- Do multi-hop requests and messages preserve sender, carrier, recipient, and
  causal lineage?
- Are intent acceptance, scheduling, execution, partial effect, no effect,
  failure, and delivered result distinct?
- Are invalid attempts recorded rather than silently normalized?
- Does only the reducer commit authoritative state?

### Operationalization and variants

- Are qualitative and numerical representations proportional to the evidence?
- Are source class, identification status, and sensitivity purpose explicit?
- Does each structural variant change one unresolved mechanism while retaining
  shared fixed boundaries?
- Is the chosen variant part of scenario/run identity?
- Are normal completion, incomplete termination, invariant failure, and
  evaluation eligibility separate?

### Falsification and usability

- Do worked cases exercise normal, missing-information, authority, duplicate,
  resource-conflict, and adverse-result paths?
- Do perturbations predict inspectable differences in state or trace?
- Can a reviewer route each failure to evidence, Definition, scenario,
  mapping, implementation, or contracts?
- Is every major state, rule, parameter, and case consumed by the research
  question or a falsifier?
- Can an implementer reconstruct the semantic world without inventing policy
  or reading the historical outcome?
- Can a domain reader understand the event model without knowing repository
  class names, carrier slots, hashes, or build procedures?

### Release-interface closure

- Do the derived product, capability, observation, intent, lifecycle, and rule
  counts reconcile with the pinned release and mapping?
- Does every released observation placement have one scenario source,
  projection, delivery path, time rule, and semantic reference?
- Does every released intent placement have one authority/target account,
  business lifecycle, adjudication owner, result boundary, and semantic
  reference?
- Are participant assembly, private/business state, relationships, resources,
  structural variants, and replay closed without duplicating an authority?
- Are all gaps explicit and routed to the layer that owns the missing meaning?

## Findings and verdict

Classify findings as:

- **Blocking**: invalid evidence/time boundary, missing causal owner, duplicate
  authority, outcome forcing, intent/result collapse, release-interface
  non-closure, or non-falsifiable scenario;
- **Major**: behaviorally material ambiguity, missing lifecycle, weak
  adjudication, hidden state, unsupported parameter, or incomplete variant;
- **Minor**: localized clarity, terminology, reference, or organization issue;
  or
- **Observation**: non-required improvement or later research opportunity.

End with one verdict:

- `ACCEPT_FOR_OWNER_REVIEW`;
- `RETURN_FOR_SCENARIO_REVISION`;
- `RETURN_TO_EVIDENCE_OR_ROSTER`; or
- `BLOCKED_BY_OWNER_OR_CARRIER_DECISION`.

Acceptance means the scenario semantics are ready for owner consideration. It
does not authorize implementation, simulation, or a scientific-validity
claim.
