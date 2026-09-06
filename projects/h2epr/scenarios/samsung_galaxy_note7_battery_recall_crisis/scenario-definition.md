# Samsung Galaxy Note7 Battery Recall Crisis Scenario Definition

## 1. Model overview

This dataset-conditioned Rule scenario represents the Note7 process as a sequence
of participant-authored reports, statements, regulatory and corporate decisions,
and investigation records. It uses H2EPR-0481's sealed three-file Source Profile,
eight reviewed runtime parents and one passive SDI context disposition. Twenty-nine
logical coordinates compress nine Draft episodes from launch to the final-report
boundary. The supported result is a replayable process account, not reconstructed
battery physics or recall effectiveness.

## 2. Event boundary and process coverage

The process covers product launch and sales, early aggregate incident reporting,
Samsung's early response, initial recall/guidance, a limited mainland recall,
domestic incident controversy, an aircraft-incident notification, production
exit, full mainland recall, litigation, and a represented investigation/report.

Physical fires, individual devices and injuries, aviation enforcement, inventory,
refund settlement, return rates, production quantities, judicial outcomes,
financial losses and public-opinion dynamics are outside the state reducer. Their
source mentions remain qualified context. Supplier relationship is opening
context; it does not manufacture an SDI decision interface.

## 3. Dataset basis, exposure, and temporal firewall

Only `event_spec.json`, `frozen_evidence.json` and `draft_epg.json` are admitted.
All four Draft stages are exposed before authoring. The 11 frozen pages include
competing contemporary accounts, later root-cause claims, scraped navigation and
truncated text; no external reconciliation is performed.

| Source defect or ambiguity | Executable treatment |
|---|---|
| Consumer reporting relation points from SDI | P_3 owns the early aggregate report; SDI remains context. |
| Initial recall transaction points to SDI | Samsung records notices to P_3; no supplier recall recipient. |
| Test-unit refund points to the regulator | P_5 may record a qualified request; no completed compensation. |
| Domestic dispute prose points to ATL / transaction endpoints mix cohorts and supplier | P_7 owns report/dispute/litigation; ATL owns only its statement. |
| Litigation and supplier-investigation relations use wrong IDs | Actor-local rows own records; corrupt links confer no authority. |
| 2017 root-cause descriptions coexist with 2016 decisions | Findings enter only after P_9 publication and transport; no backward leakage. |

The Source Profile records full-Draft exposure. This construction is neither a
blind event nor an unbiased forecast. Earlier work on another branch does not
provide input payload or research questions to this current release.

This is a declared-event-vocabulary-exposed baseline: all public field names and each actor's complete capability menu are visible from the first coordinate, including event-specific future terms. Generated result values and actual receipt remain distinct from that vocabulary. No historically prefix-clean information claim is made.

World feasibility is enforced by mechanism domains and state preconditions. Only explicit handler information_requirements are mandatory receipt admission. Other message guards, activation windows and priorities are selected Rule policy assumptions, not backend-neutral historical or institutional laws.

## 4. Temporal structure and exogenous inputs

- Coordinate 1: product launch record (2016-08-02; `S1/E1`).
- Coordinate 2: global sales-start record (2016-08-19; `S1/E1`).
- Coordinate 3: early aggregate incident report (2016-08-24 to 2016-08-31; `S1/E2`).
- Coordinate 4: initial cause statement (2016-08-24; source chronology overlaps reporting; `S1/E2`).
- Coordinate 5: additional quality-testing announcement (2016-08-31; `S1/E2`).
- Coordinate 6: shipment-delay record (2016-08-31; `S1/E2`).
- Coordinate 7: initial global recall (2016-09-02; `S2/E3`).
- Coordinate 8: safety guidance and regulator availability (2016-09-02 to 2016-09-14; `S2/E3`).
- Coordinate 9: regulatory requirement delivery / limited recall (2016-09-14; `S2/E4`).
- Coordinate 10: test-unit notice delivery and request window (2016-09-14 onward; `S2/E4`).
- Coordinate 11: mainland incident reporting (2016-09-18; `S2/E5`).
- Coordinate 12: Samsung and ATL represented accounts (2016-09-19; `S2/E5`).
- Coordinate 13: consumer dispute after statement delivery (2016-09-19 onward; `S2/E5`).
- Coordinate 14: recall-handling apology (2016-09-29; `S2/E5`).
- Coordinate 15: aircraft incident representation (2016-10-05; `S3/E6`).
- Coordinate 16: internal production-safety review (2016-10-05 to 2016-10-10; `S3/E6`).
- Coordinate 17: production-suspension announcement (2016-10-10; `S3/E6`).
- Coordinate 18: permanent product-stop announcement (2016-10-11; `S3/E7`).
- Coordinate 19: full mainland recall announcement (2016-10-11; `S3/E7`).
- Coordinate 20: consumer litigation availability (2016-11-04 onward; `S4/E8`).
- Coordinate 21: internal root-cause investigation (2016-11 to 2017-01; `S4/E8`).
- Coordinate 22: third-party commission (2016-11 to 2017-01; `S4/E8`).
- Coordinate 23: consortium investigation / litigation response (2016-11 to 2017-01; `S4/E8`).
- Coordinate 24: findings publication window (2017-01-23 boundary; `S4/E9`).
- Coordinate 25: finding delivery / final-report availability (2017-01-23 boundary; `S4/E9`).
- Coordinate 26: late-information grace (logical grace; no new source event; `S4/E9`).
- Coordinate 27: bounded final-report grace (logical grace; no new source event; `S4/E9`).
- Coordinate 28: last participant decision window (logical grace; no new source event; `S4/E9`).
- Coordinate 29: terminal transport barrier (delivery accounting only; `S4/E9`).

Coordinates order information dependencies where source intervals overlap; they
do not estimate calendar duration. All baseline routes use one logical tick.
Coordinates 26–28 provide bounded late-information grace; coordinate 29 drains
transport and opens no new Rule row.

P_8 is a representation gate for the aircraft-incident record. The physical fire
is exogenous and has no participant-authored cause. There are no hidden commands
that force a recall, suspension, consumer response, finding or final report.

## 5. Participant assembly and authority

| Source | Runtime representation | Decision boundary |
|---|---|---|
| P_1 | Samsung Agent | manufacturer response, recall, production and report records |
| P_2 | initial context | supplier/status only; no invented decision |
| P_3 | global purchaser Population | aggregate early incident report |
| P_4 | regulator Agent | limited recall-plan requirement |
| P_5 | test-owner Population | qualified return/refund request after notice |
| P_6 | ATL Agent | qualified supplier statement |
| P_7 | regular-purchaser Population | domestic report, dispute and litigation filing |
| P_8 | airline representation-gate Agent | aircraft-incident record/message only |
| P_9 | composite investigation Agent | process and findings publication |

The three Populations preserve cohort-level choices without synthesizing people.
The P_9 composite is disclosed; a study of institutional disagreement requires
separate supported parents. Frozen-only aviation authorities, courts, media and
retailers are not silently made participants or environment decision makers.

## 6. World, institutions, relationships, and resources

The mechanism uses 28 public one-time record fields. `unrecorded` means no
admitted modeled record yet, not that the historical action did not occur. The
fields cover product, response, incident, recall, regulation, request, dispute,
product-exit and investigation families. Every field has one actor-authorized
handler and a reducer-owned value transition.

There is no device, money, inventory, return-rate, injury, production, court or
battery-state ledger. Unit counts and defect accounts are statement payloads or
record labels, not conserved resources or verified findings. Aviation restrictions
remain institutional context because no corresponding Draft participant exists.

## 7. Observation and communication routing

Every runtime actor receives sealed public prestate, current delivered messages,
its own outgoing pending lifecycle and runtime-derived received/own-action memory.
It never sees future episode labels, Reference content, another actor's pending
private message or generated opaque IDs as evidence.

Routes carry early and domestic incident reports, recall/guidance notices, the
regulator requirement, a test-owner request, disputed public accounts, aircraft
notification, litigation notice, investigation commission and findings. Receipt
guards depend on actual delivery. These channels and one-tick delays are explicit
construction assumptions, not recovered organizational communications.

## 8. Intent, adjudication, lifecycle, and result

Twenty-eight event intents plus `no_op` project from the eight current parents.
The backend emits an intent and optional statements. The environment validates
actor, target, parameters and prerequisites against one sealed prestate; the
reducer alone records accepted effects. Rejection produces no delta. Messages
have separate admitted/delivered lifecycle records.

An accepted recall notice does not complete a return; an accepted request does
not pay a refund. A statement does not establish physical cause. An aircraft
record does not force production action. An investigation process does not equal
published findings, and findings do not force Samsung's final report.

## 9. Configuration, variants, termination, and identity

Shared configuration owns actor set, opening state, timeline, routes, observation
and termination. Rule configuration owns inclusive windows, state/received-memory
guards, priorities, payloads and no-op fallback. Every top-level setting has
provenance; no value is described as calibrated.

Complete publication requires the full horizon, trace chain, tick/run seals,
authoritative replay, exact final state, graph reconstruction and zero unresolved
transport. Outcome expectations describe the canonical baseline and are not
release gates. Missing or delayed information may yield a different valid final
state. A semantic change requires successor parents and rebuilt descendants;
timing changes route through configuration.

## 10. Worked cases, falsification, and limitations

- Missing domestic report: both explanatory statements and their downstream
  dispute remain unavailable; independent recall/product-exit chains may continue.
- Delayed findings: Samsung waits for actual receipt and may finish with its final
  report open, without invalidating a complete replayable run.
- Foreign authority: Samsung cannot issue the regulator requirement, P_7 dispute,
  P_8 incident record or P_9 findings.
- Recall boundary: no notice or request handler creates a completed refund,
  population-wide return or effectiveness field.
- Temporal firewall: 2017 root-cause text in a 2016 observation falsifies the
  package even if the final state happens to match the Draft.

The model is a sparse statement/decision-record simulation informed by full Draft
exposure. It supports dataset-conditioned engineering and simulation-only reading,
not historical fit, parameter calibration, causal attribution, held-out
performance, scientific validity or universal generality.
