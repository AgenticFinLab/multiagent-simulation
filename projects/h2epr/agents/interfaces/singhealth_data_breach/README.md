# SingHealth Data Breach participant interfaces

This guide organizes the two publication-facing interface accounts for the
seven office-level Agent Definitions and two responsibility-unit Population
Models in H2EPR-0616. It provides one cross-event reading structure while
leaving behavior with the participant models and event-world state, delivery,
adjudication, and results with the Event Scenario Definition.

## Reading map

| Interface | Participants | Main distinction |
|---|---|---|
| [Detection and escalation](r1-detection-and-escalation.md) | Technical administration and line-security units, the Security Incident Response Manager, and the Cluster Information Security Officer | Local findings, security interpretation, coordination, escalation, delivery, and technical effects remain separate. |
| [Classification and institutional escalation](r2-classification-and-institutional-escalation.md) | Operational and SCM management units, the GCIO, Sector Lead, IHiS CEO, SingHealth Deputy GCEO, and SingHealth GCEO | Operational accounts, classification, executive direction, institutional reporting, outreach planning, authorization, and patient delivery retain distinct owners. |

## Shared causal structure

The participant chain is source-preserving rather than a shared organizational
mind:

```text
technical unit forms a bounded finding or request
  -> security and management recipients observe only delivered content
  -> operational units assemble a qualified, source-linked account
  -> the GCIO routes that account to the appropriate senior office
  -> Sector Lead, IHiS CEO, Deputy GCEO, and GCEO decide within separate roles
  -> institutional processes adjudicate reporting, response, and outreach
```

The two interface accounts meet at the operational account delivered from the
technical and security layers. Later recipients do not inherit the source
unit's logs, assessment, or certainty. Corrections and verification results
must travel as new, causally linked information products.

## Information and state boundaries

- Technical, security, operational, and executive participants retain separate
  observations, assessments, open questions, and intent histories.
- Reporting relationships and concurrent appointments do not create shared
  knowledge or silently transfer authority between IHiS, SingHealth, MOH, or
  another institution.
- A delivered account preserves its sources, event time, uncertainty,
  freshness, known actions, open questions, and requested response.
- Incident concern, classification proposal, authoritative category, reporting
  direction, report issue, delivery, acknowledgement, and institutional
  response are different states.
- Outreach preparation, audience or channel proposal, consultation,
  authorization, execution, patient delivery, and response remain separate.
- Pending, acknowledged, completed, partial, failed, expired, cancelled, and
  superseded intents remain distinguishable from work that was never issued.

## Authority and result ownership

| Surface | Participant contribution | Owner outside participant policy |
|---|---|---|
| Technical investigation | Observe, assess, request verification, assign bounded work, or propose a local control | Access, execution, technical finding, containment effect, delay, and failure |
| Security coordination | Classify a local concern, request information, activate or coordinate response, and escalate a qualified account | Delivery, recipient action, institutional incident state, and realized control effect |
| Operational account | Gather and reconcile delivered material, preserve uncertainty, request clarification, and route a concern | Underlying logs, verification result, executive interpretation, and technical effect |
| IHiS classification and reporting | Assess, propose a category, direct reporting, assign investigation, or issue a bounded update | Authoritative category, report delivery, CSA receipt, external response, and investigation result |
| SingHealth governance | Request detail, direct or request MOH reporting, and prepare or review outreach options | MOH action, collective authorization, authoritative audience, execution, delivery, and patient response |

An intent cannot create its own acknowledgement, completion, or effect. Each
recipient applies its own information and authority boundary after delivery.

## Lifecycle expectations

Requests, assignments, coordination directions, reports, consultations, and
outreach plans retain stable identities and causal references. A later status
can acknowledge, complete, partially satisfy, reject, fail, expire, cancel, or
supersede an earlier intent. New evidence may reopen an assessment without
rewriting the information available at the earlier decision.

This lifecycle discipline is especially important for delayed verification,
cross-institution reporting, and patient communication: an issued message is
not a delivered one, and preparation or recommendation is not authorization.

## Informative perturbations

The interface account would be contradicted if these controlled changes did
not alter behavior as stated:

- an undelivered technical finding must create no observation in Security
  Management or a senior office;
- replacing a pending verification with a delivered adverse result must permit
  reassessment and escalation rather than indefinite waiting;
- replacing a complete operational account with a delivered, source-preserving
  correction must update later recipients without rewriting the earlier account;
- changing the acting capacity of a concurrent office holder must change which
  institutional intents are admissible;
- a failed report delivery must not create CSA acknowledgement or response; and
- outreach preparation without authorization or delivery must create no
  patient observation.

## Evidence and limits

The accounts rely principally on retrospective official inquiry material and
are qualitative, outcome-exposed, and uncalibrated. They explain role-specific
information, authority, and response alternatives; they do not recover private
thresholds, quantitative mechanism weights, complete technical exploit
mechanics, or a unique counterfactual effect for any missed escalation.

## Release relationship

The accepted [Roster Definition release](../../../releases/singhealth_data_breach/roster-definition-v0.1/)
pins the exact participant products and interface accounts. The
[consolidated mapping](../../bindings/singhealth_data_breach/consolidated/)
records their machine-facing placement. Mapping and bounded implementation do
not add participant behavior or change the scholarly interfaces described
here.
