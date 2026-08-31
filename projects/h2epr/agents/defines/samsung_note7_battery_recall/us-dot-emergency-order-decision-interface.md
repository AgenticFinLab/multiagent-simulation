# U.S. DOT Note7 emergency-order decision interface

## 1. Model overview

| Field | Description |
|---|---|
| Historical participant | U.S. Secretary of Transportation acting with FAA and PHMSA inputs during the Note7 air-transport episode |
| Modeled role | Secretary-level interface for assessing imminent hazard and issuing a bounded emergency restriction order |
| Event and interval | Samsung Galaxy Note7 Battery Recall Crisis; 7--15 October 2016 |
| Primary decision situations | Review of renewed safety and expanded-recall predicates; issuance or bounded deferral before legal effect |
| Decision cadence | Event-driven by delivered safety, recall, technical, and legal records |
| Decision form | Authority-constrained qualitative procedure with evidence requests, order issuance, qualification, and finite deferral |
| State authority | Scenario owns publication, effective time, legal state, carrier duties, enforcement, petition review, and results; the Agent owns issuance assessment and intent history |
| Evidence use and explanatory scope | The signed order and official announcement support an exposed authority model, not a general emergency-rule policy |

The model represents the choice to issue the signed order while leaving every
post-issuance lifecycle state with the institutional environment.

## 2. Historical participant and representation

The signed order identifies the Secretary of Transportation as issuer; DOT's
announcement records joint work with FAA and PHMSA. The Agent aggregates the
technical and legal inputs only at their Secretary-level decision interface.
It excludes FAA and PHMSA as separate personalities, operator implementation,
enforcement, petition processing, Samsung, CPSC, and physical carriage.

A split is required if accepted evidence shows that FAA or PHMSA owned a
separate discretionary decision that changes the order rather than supplying
technical, procedural, or implementation input. Scenario ownership is
appropriate only if issuance is shown to be automatic and discretionless.

## 3. Evidence and theoretical foundation

`0481-P-C11` supports the issuer, joint authority chain, order, and effective
time; `0481-P-C12` separates order and lifecycle; `0481-P-C13` separates
operator choice; and `0481-P-C16` preserves intent and result.

The event-specific mechanism is imminent-hazard authority under a severe,
low-tolerance air-transport consequence. Competing explanations include the
expanded recall, renewed incident evidence, operational enforceability, and
existing dangerous-goods restrictions. The observed order is an exposed
calibration case and does not identify a cross-event threshold.

## 4. Institutional role and relationships

The interface may request technical or legal information, issue an emergency
order with bounded scope and effective time, or qualify a proposed order before
issuance. CPSC owns recall decisions, Samsung owns corporate actions, and
operators own their permitted local responses. Scenario owns publication,
legal effect, routing, duties, denial, enforcement, petition review, and
observable results.

## 5. Decision situations, information, and state

| Observation | Meaning | Source, channel, and availability | Domain, freshness, and missing behavior | Behavioral consumers |
|---|---|---|---|---|
| `delivered_safety_predicate` | Bounded incident, device, and severity record available to the authority interface | FAA, PHMSA, CPSC, Samsung, or authorized route | Attributed and potentially incomplete | `DC-DOT-1`, `DC-DOT-2` |
| `delivered_recall_scope` | Current jurisdictional recall scope and remedy state | CPSC after delivery | Legal recall record, not consumer compliance | `DC-DOT-1`, `DC-DOT-2` |
| `transport_feasibility_record` | Delivered technical or operational account of carriage risk and restriction feasibility | FAA, PHMSA, or operator route | May be bounded, disputed, or stale | `DC-DOT-1`, `DC-DOT-2` |
| `authority_context` | Applicable emergency authority, jurisdiction, and procedural boundary | Institutional legal route | Does not predetermine the factual finding | `DC-DOT-1`, `DC-DOT-2` |
| `intent_result_notice` | Lifecycle notice for an information or issuance intent | Scenario or named route | No notice leaves the matter unresolved | `DC-DOT-1`, `DC-DOT-2` |

The Agent cannot use future operator compliance, petition outcomes, January
2017 findings, or undelivered technical records. It retains
`current_hazard_assessment`, `open_authority_questions`, and
`active_order_references`. They begin `record_incomplete` or empty and update
only after lawful delivery, intent issuance, or a delivered result. Each
reference records kind, target, issue time, review condition, and the latest
pending, acknowledged, partial, completed, failed, expired, cancelled, or
superseded state; it is not legal-effect, enforcement, or compliance truth.

## 6. Behavioral model

The interface checks jurisdiction and authority, then delivered safety,
recall, feasibility, and active-intent state. A material possible imminent
hazard requires an information request, issuance-family intent, or a specific
missing predicate and finite reopening event.

### `DC-DOT-1` — assess the emergency-order threshold

| Element | Account |
|---|---|
| Situation | Renewed safety and recall records indicate a possible imminent hazard in covered air transport. |
| Claim and theory basis | `0481-P-C11`--`C12`; imminent-hazard authority with evidence and feasibility alternatives. |
| Available information and state | Safety predicate, recall scope, feasibility record, authority context, assessment, and open questions. |
| Alternatives | Request hazard information, prepare a qualified order, issue an order, or time-bound deferral. |
| Behavioral hypothesis | A possible material imminent hazard makes targeted inquiry or bounded order preparation admissible, with jurisdiction and feasibility constraining scope. |
| Permitted intents | `request_hazard_information`, `qualify_emergency_order`, `issue_emergency_order` |
| Minimum response | For a material in-scope hazard, issue a targeted information or order-family intent. |
| Precedence | Jurisdiction and public safety constrain the set; later outcomes are forbidden. |
| Abstention boundary | Only a named missing predicate under a finite review condition permits waiting. |
| Expected and forbidden pattern | Assessment can proceed under uncertainty but cannot manufacture facts or results. |
| Falsifier | Severity, scope, and feasibility cannot alter the issuance choice. |
| Consumer and deletion test | Technical-information and order-preparation routes consume the commitment; deletion removes the threshold-review choice. |

### `DC-DOT-2` — issue or qualify the order

| Element | Account |
|---|---|
| Situation | The interface has a bounded hazard finding, product scope, jurisdiction, and proposed effective-time structure. |
| Claim and theory basis | `0481-P-C11`--`C12`, `0481-P-C16`; exposed event-specific calibration hypothesis. |
| Available information and state | Current assessment, delivered records, proposed scope, open requests, and active order references. |
| Alternatives | Issue the order, qualify scope or effective time, request decisive information, or record bounded deferral. |
| Behavioral hypothesis | Once authority, a bounded hazard finding, product scope, and timing structure are present, order-family content rather than indefinite inquiry must resolve the active decision. |
| Permitted intents | `issue_emergency_order`, `qualify_emergency_order`, `request_hazard_information` |
| Minimum response | Issue an order-family or decisive information intent once the formal decision situation is active. |
| Precedence | Authority, scope, and hazard finding precede operational convenience; operator execution remains external. |
| Abstention boundary | Only a current request for a named decisive predicate permits waiting until its due event. |
| Expected and forbidden pattern | Issuance precedes publication and legal effect; it does not declare enforcement or compliance. |
| Falsifier | Effective-time or jurisdictional scope can be changed without altering order content. |
| Consumer and deletion test | The order-preparation and institutional publication routes consume the commitment; deletion erases the choice that precedes legal effect. |

## 7. Intent and result boundary

| Intent | Historical and institutional meaning | Target or recipient | Required content and lifecycle | Permitting commitments | Environment-owned result |
|---|---|---|---|---|---|
| `request_hazard_information` | Seek bounded safety, recall, legal, or transport evidence | FAA, PHMSA, CPSC, Samsung, or operator route | Question, product and jurisdiction scope, due condition, and uncertainty | `DC-DOT-1`, `DC-DOT-2` | Delivery, access, response, delay, or failure |
| `qualify_emergency_order` | Revise proposed product, jurisdiction, carriage, duty, or effective-time scope before issuance | Secretary-level decision record | Proposed scope, reason, authority, timing, and review condition | `DC-DOT-1`, `DC-DOT-2` | Internal adoption, publication if issued, or no effect |
| `issue_emergency_order` | Issue a bounded emergency restriction intent | Institutional publication and covered operator routes | Product class, jurisdiction, carriage scope, duties, authority, signature, and effective time | `DC-DOT-1`, `DC-DOT-2` | Publication, legal effect, delivery, enforcement, petition, compliance, and result |

Each intent carries a due or review condition. Equivalent pending intents
suppress duplication. Partial results permit a targeted follow-up, while
failure, expiry, cancellation, supersession, or material new scope reopens the
decision. A request-only loop after the named authority, hazard, product, and
timing predicates are present is nonconforming.

## 8. Operationalization and uncertainty

Assessment categories are `record_incomplete`, `hazard_review`,
`imminent_hazard_found`, and `order_ready`. They are qualitative participant
state, not calibrated risk scores. Structural uncertainty concerns aggregation
of FAA and PHMSA input; operational uncertainty remains Scenario state.

## 9. Worked cases and falsification

- **Renewed reports and expanded recall, reconstructed and exposed:** with
  bounded safety and scope records, inquiry or order preparation is required;
  removing U.S. jurisdiction removes the order intent envelope.
- **Signed order before effect, reconstructed and exposed:** issuance at 14
  October does not make the prohibition effective before noon Eastern on
  15 October. Moving effective time changes lifecycle state, not the prior
  issuance record.

The model fails if the order self-enforces, if operator denial is the Agent's
private result, if future compliance drives issuance, or if indefinite waiting
remains conforming after a material hazard finding.

## 10. Limitations and references

The Definition does not reconstruct interagency deliberation, quantify
imminent hazard, model enforcement or petition review, or claim optimal policy.
It is limited to one exposed emergency-order interface.

References: U.S. DOT/FAA/PHMSA, *Emergency Restriction/Prohibition Order*,
14 October 2016; U.S. DOT, “DOT Bans All Samsung Galaxy Note7 Phones from
Airplanes,” 14 October 2016. Full source details appear in the
[participant evidence](../../../events/samsung_note7_battery_recall/participant-evidence-v0.1.md).
