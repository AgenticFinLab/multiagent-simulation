# H2EPR-0616 generated-process reading

The accepted SingHealth run generates a four-wave escalation process spanning
technical investigation, operational coordination, executive reporting,
sector-level classification, and notification preparation. Compared with the
other current H2EPR runs, it carries a relatively rich private-state
progression: technical units move from routine possibility to suspicion,
operational units flag senior attention, and incident-governance actors open
reporting and coordination concerns.

This report is a reading of simulated output. The inventory, chronology,
routes, and state counts below are direct artifact facts. The section headed
“Analytical reading” states interpretations drawn from those facts. No Draft
EPG, Reference EPG, or historical comparison evidence is used.

## Reading scope

The primary object is the complete canonical Generated EPG identified by the
[accepted run release](../../../execution/singhealth_data_breach/run-and-graph-v0.1/).
The run manifest supplies the civil-date meaning of logical ticks. The sealed
trace and final state are used to check observation delivery and completion
state, because observations and seals are not projected as graph nodes.

| Coverage item | Complete reading result |
|---|---:|
| Generated EPG nodes | 752 of 752 |
| Generated EPG edges | 623 of 623 |
| Unique node-to-trace references | 752 |
| Sealed trace records traversed as context | 1,554 of 1,554 |
| Participants | 13 |
| Participant decisions / action intents | 41 / 41 |
| Canonical and repeat graph | byte-identical |

The graph declares `simulation_generated_mechanism_coverage` as its output
interpretation. Its own claim boundary sets historical calibration,
historical validation, and scientific validity to false.

## Graph form

The graph contains 41 participant decisions, 41 action intents, 41 action
dispositions, 222 policy applications, 141 state deltas, 73 message intents,
146 message dispositions, six exogenous releases, and 41 carry-forward nodes.
These are the same nine node types used by the other accepted H2EPR graphs.

Its 623 edges comprise 41 `adjudicates`, 141 `causes`, 73 `emits`, 222
`governs`, and 146 `routes` relations. They connect action intents to their
local results and messages, and messages to their queue and delivery
dispositions.

The graph has 129 weakly connected components: 41 action-centered components
and 88 isolated nodes made up of the six exogenous releases, 41 participant
decisions, and 41 carry-forward records. There is no explicit cross-action,
observation-to-decision, or lifecycle-to-carry-forward edge. Logical ticks and
source-trace identities retain the ordering needed for a process reading.

## Simulated process

Five civil-date anchors are each expanded into ten declared partial-order
slots. Those slots preserve execution precedence without claiming unobserved
intraday timestamps.

| Logical position | Simulated actions |
|---|---|
| 23 August 2017, modeled start | Attack opportunity, institutional appointments, and office-capacity context are admitted. No participant acts. |
| 18 January 2018, response wave | The sector lead requests classification verification; the security incident response manager requests an investigation; three technical units investigate local signals. |
| 11 June, acute-start wave | Cluster, executive, and SingHealth offices request incident or operational clarification; the response manager coordinates the incident; three operations units request technical accounts; the three technical units repeat investigation and move their local assessment from `routine_possible` to `suspicious`. |
| 20 July, core-horizon wave | The cluster security officer requests SIRT activation; the sector lead reports a CII incident to CSA; the response manager escalates; the GCIO notifies SingHealth management; executive offices request further detail; operations units escalate concerns; and technical units inspect partial results. |
| 23 July, notification-horizon wave | The cluster security officer escalates a potential CII incident; the IHiS CEO assigns an investigation lead; the sector lead requests report status; SingHealth executives request an outreach revision and receive a patient-impact update; the response manager delegates coverage; and operations units retry failed account requests. |

All six exogenous inputs carry `outcome_forcing: false`. They admit attack,
account, authority, government-response, and notification opportunities
without fixing the participant choices or their results.

## Participant levels and communication

The 13 actors span three levels:

- seven office-level interfaces for sector governance, IHiS and SingHealth
  leadership, cluster security, the GCIO, and incident response;
- three operational coordination units; and
- three technical responsibility units.

The three technical actors share one population capability and follow the
same three-step action sequence. The three operational actors likewise share
one capability and follow request, escalation, and retry steps. Their actor
identities and routes remain separate even where their state trajectories are
symmetric.

Every action produces one typed environment result. Thirty-two actions also
produce a declared participant communication. These routes connect technical
and operations units, the incident manager and cluster security officer,
cluster and sector governance, the GCIO and executive offices, and the sector
lead to CSA.

All 73 messages have latency one and receive both queued and delivered
dispositions. Seventy-one appear in exactly one Agent observation. The two
remaining messages are the sector lead’s report and later status request to
`institution.0616.csa`; CSA is an institutional endpoint rather than a
runtime Agent, so those terminal deliveries produce no private Agent
observation. No message intent or recipient is unresolved at the seal.

## Policy, state, and completion

All 222 policy applications pass:

| Policy family | Applications | Visible result |
|---|---:|---|
| authority | 41 | authority scope admitted |
| time | 41 | intent admitted at its declared coordinate |
| lifecycle | 41 | typed result completed |
| information and route | 32 each | information product created and route admitted |
| incident | 15 | suspected to under review |
| technical | 14 | canonical mechanism-coverage execution |
| coordination | 4 | requested to admitted |
| notification | 2 | preparation requested to drafting |

All 41 action dispositions are accepted. The 141 state deltas comprise 41
lifecycle additions, 41 idempotency records, and 59 participant-private
updates. The private updates produce several visible trajectories:

- technical local assessments move from `unexamined` to `routine_possible`
  and then `suspicious`; their final active references are `adverse` and their
  questions remain open;
- operational units finish with `senior_attention_needed`, an issued
  consolidated account, and adverse verification state;
- the incident manager moves from `routine_possible` to
  `reporting_trigger_met`, while its coverage assessment ends `uncovered`;
- the cluster security officer ends with `reporting_concern`; and
- several executive assessment fields remain `unassessed` even though their
  reporting, review, outreach, or notification references are pending.

All 41 lifecycle objects remain nonterminal and become carry-forward records.
Seventeen end `produced`, 16 `admitted`, four `authority_checked`, and one each
in `access_adjudication`, `drafted`, `drafting`, and `under_review`. The run
closes normally with all messages resolved. It reaches its observation
horizon while investigation, authority, reporting, and notification objects
remain open.

## Analytical reading

### The escalation chain is legible

The generated process has a clear progression from local technical review to
cross-team coordination, incident escalation, executive and sector reporting,
and notification preparation. Private-state updates reinforce this
progression instead of merely marking active intent references. Among the
three current runs, this is the strongest simulation-only account of a
multi-level organizational escalation.

### Repeated units provide coverage with limited differentiation

Separate technical and operations carriers prove that the framework can
project one population model across several responsibility units and preserve
their routes. In the canonical run, the three units within each group follow
nearly identical action and state sequences. That symmetry is useful for
carrier and mechanism coverage, while offering little evidence about
unit-specific timing, capacity, evidence quality, or divergent response.

### External institutional and affected-population feedback is bounded

CSA receives two messages but has no Agent state or response. MOH,
notification processes, and affected patients likewise remain outside the
autonomous actor set. The generated process therefore represents the issue
and route side of external reporting and patient-notification preparation,
not recipient interpretation, institutional feedback, or population-level
effect.

### Canonical execution remains a positive path

All 41 commitments emit actions, every applicable policy passes, and every
action is accepted. Labels such as `adverse`, `uncovered`, and
`reporting_trigger_met` describe participant state; they do not produce an
action rejection or failed transport in this run. The graph demonstrates
composition of escalation mechanisms rather than their behavioral
distribution under alternative conditions.

### Cross-action causality remains outside graph topology

The action-local provenance is exact, but decision and observation nodes do
not connect to earlier messages or state changes through graph edges. The
clock and trace show delivery before later waves; the Generated EPG alone does
not prove which delivered account caused a later classification, escalation,
or notification choice. That distinction should remain explicit in any
historical comparison.

## Questions reserved for later comparison

A later, separately scoped study can test:

- which escalation, reporting, and notification transitions are retained
  from the configured Draft EPG and which arise from runtime mechanisms;
- whether the four action waves preserve supportable historical order and
  organizational authority;
- whether the symmetric technical and operations trajectories need
  event-specific differentiation;
- whether CSA, MOH, or recipient feedback is necessary for the chosen
  historical question;
- which of the 41 open lifecycle objects have evidentiary outcomes and which
  should remain unresolved; and
- whether message-to-decision causal links can be supported without turning
  retrospective event knowledge into participant information.

Those questions are not answered by the present simulation-only reading.
