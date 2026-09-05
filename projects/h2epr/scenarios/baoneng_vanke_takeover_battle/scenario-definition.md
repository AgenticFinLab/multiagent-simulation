# Baoneng–Vanke Takeover Battle Scenario Definition

## 1. Model overview

This dataset-conditioned Rule scenario represents the corporate-control dispute
through disclosures, proposals, objections and institutional response records.
It uses H2EPR-1031's sealed three-file Source Profile, eight reviewed Agent
Definitions and their participant interface. The interval is July 2015 to the
June 2017 nomination/meeting boundary; 20 logical coordinates compress ten Draft
episodes. There are eight Agents, no Population, and one authoritative record
environment. The supported result is an executable, replayable process account.

## 2. Event boundary and process coverage

Opening context contains Vanke as the contested listed company, Baoneng as the
acquiring shareholder interface, China Resources as an incumbent shareholder,
Wang/Yu as distinct management voices, and later-available Metro, Evergrande and
CSRC choice interfaces. Record fields start unrecorded; this means no simulated
disclosure has been made, not that the corresponding organization owns no shares.

The process covers the initial stake/management confrontation, conditional
restructuring and opposing positions, removal request/board response, another
shareholder's entry, negotiation and guidance, and the later Metro disclosure
and nominee process. It ends at a scheduled vote, with election unobserved.
Financing, securities clearing, market prices, undisclosed coalitions, internal
ballots and post-window ownership changes are outside the executable boundary.

## 3. Dataset basis, exposure, and time boundary

The Source Profile permits only event_spec, frozen_evidence and draft_epg.
All four Draft stages are exposed to the author; no unbiased forecast or held-out
performance follows. Frozen evidence remains dataset material, without external
retrieval. SRC006/007 repeat speculative reporting, SRC008 lacks substantive
abstract text, and retrospective material is not early participant knowledge.

| Source conflict | Executable treatment |
|---|---|
| E2/E4/E5/E7/E8/E9/E10 relation/transaction endpoints mismatch names/actions | Actor-local appearances and declared authority own actions; corrupt links remain source defects. |
| Proposed RMB45.6bn 2016 swap conflated with completed 2017 acquisition | Separate proposal records and later near-30% disclosure; no swap completion or seller inferred. |
| December LOI counterparty unnamed in SRC004 | Corporate conditional LOI without Metro identity; Metro terms become available in mid-2016. |
| E6/SRC002 disagree about the day/order of board rejection | Preserve request-before-response logical dependency and disclose unresolved calendar chronology. |
| Draft header claims board elected; SRC010 and E10 describe forthcoming June30 vote | Nomination/registration/scheduling only; election_result stays unobserved. |
| P_5 passive nomination and repeated late holding/nominee actions | Knowledge/status or merged repeated act, explicitly crosswalked in interface closure. |

Final slate, board outcome and future stage descriptions never appear in early
backend observations. Source dates stay trace navigation metadata, not a field
the Rule backend receives or a source of hidden future state updates.

## 4. Temporal structure and exogenous inputs

| Coordinates | Coverage | Timing qualification |
| --- | --- | --- |
| 1–4 | Initial stake reports, management choices, notice and LOI | Overlapping December intervals are serialized only for information flow. |
| 5–9 | Metro proposal, separate responses, removal request and board record | Mid-2016 availability and unresolved board-response date. |
| 10–13 | Evergrande entry, discussion, positions, operating statement | Negotiation interval overlaps the dated August22 business report. |
| 14–17 | Later acquisition disclosure, nominees, personal decline and meeting notice | Only the exposed June2017 announcements are represented. |
| 18–19 | Bounded waiting for late information | Structural grace coordinates, no additional source event. |
| 20 | Final transport accounting | No participant row opens or remains active here. |

Every actor sees one sealed prestate and due deliveries before selecting at most
one intent. Later own dispositions enter its memory at the next coordinate.
Messages use one logical tick in the baseline; selected windows admit waiting.
There are no hidden exogenous commands that force acquisition, opposition,
succession or dispute resolution. Later events become available as bounded
participant choices, with disclosed dataset-conditioned policy content.

## 5. Participant assembly and causal ownership

| Actor | Represented choice boundary |
| --- | --- |
| baoneng_group | affiliated acquirer disclosure and shareholder-proposal interface |
| vanke_corporate_governance | issuer disclosures and the separately attributed corporate board-response record |
| china_resources | incumbent shareholder position interface |
| wang_shi | named chairman personal statement and nomination choice |
| yu_liang | named president management-risk statement interface |
| shenzhen_metro | proposed investor, later acquisition-disclosure and nominee-proposal interface |
| evergrande_group | new shareholder disclosure and negotiation-participation interface |
| csrc | securities-regulator guidance issuance interface |

P_2 is an explicitly composite issuer/board-response interface. Its board record
is inaccessible to Wang or Yu individual actors; internal ballots and disagreement
would require separate supported parents. CSRC retains the guidance issuance
choice; transport only manages delivery after issuance. Metro can propose
nominees but cannot register them for Vanke or decide their election.

All eight source IDs and 33 appearances are retained. No source aggregate choice
needs a Population Model. Frozen-only Anbang, affiliates, analysts, unidentified
investors, exchanges and election voters are outside the modeled decision
roster. Their unmodeled choices are not silently assigned to the environment.

## 6. World, institutions, relationships, and resources

| Record family | Meaning and decision owner | Excluded effect |
| --- | --- | --- |
| stake_disclosures | Baoneng two reports, Evergrande report, later Metro report | No order book, seller, cash, share conservation or verified ownership ledger |
| management | Wang opposition/publication and Yu risk statement | No company-wide board decision or proved financial-risk finding |
| corporate | Vanke issuer notices, conditional LOI and business report | No exchange permission, completed issuance or causal profit model |
| proposal / positions | Metro terms/participation, Vanke proposal, each shareholder's opposition | No automatic dilution, consent coalition or veto calculation |
| governance / regulation | Baoneng request, board-owned corporate response, CSRC guidance | No manager self-removal power or regulator-selected winner |
| negotiation | Corporate invitation and three separately authored positions | No inferred agreement or endogenous acquisition clearing |
| nomination | Metro proposal, corporate registration/meeting, Wang decline; election unobserved | No nominee self-appointment or forced shareholder ballot result |

The mechanism declares 28 public string fields: 27 one-time record transitions
and one immutable unobserved election field. Each handler names one actor and
one record target; its own field must still be unrecorded and any declared prior
record must be present. There is no numerical financial resource ledger. Record
truth is only that an admitted modeled statement/action occurred, not that its
reported market quantity or legal conclusion has been independently verified.

## 7. Observation and communication routing

The four maintained observations are public prestate, current deliveries, own
outgoing pending lifecycle and persistent received/own-action memory. Information
flows include initial stake reports to management, Yu's statement to Wang, Metro
terms to Vanke, corporate proposal to distinct investors, removal request and
response, guidance, discussion invitations, and later acquisition/nominee notices.
Message kinds and routes are explicit in mechanism and shared configuration.

Public record visibility does not replace a message-known guard selected by the
Rule. Those receipt dependencies are authored communication assumptions, not
verified internal corporate protocols or general legal requirements. No calibrated
memory expiry is selected for these one-off bounded statements. Pending incoming
private messages remain inaccessible until transport admits delivery.

## 8. Intent, adjudication, lifecycle, and result

27 event intents plus `no_op` are projected from the Agent parents. Intent
authority, target, parameter and state precondition checks precede reducer
effects. Accepted actions change their own record only; rejected attempts leave
it unchanged. Messages are separate typed statements and may not be treated as
proof that the sender's coupled action was accepted. A changed visible prestate
can reopen a rejected Rule row; unchanged repeated rejection alone cannot.

Concurrent distinct writes to one field are rejected; identical writes follow
the common idempotent rule. The event's current handlers separate shareholder
position fields, so simultaneous opposition is not artificial write contention.
Four one-shot annotations summarize record combinations and are trace-derived,
not independent historical labels or proof of causation.

## 9. Configuration, variants, termination, and identity

Shared configuration owns opening records, actor set, timeline, routes and
observation/termination contract. Rule configuration owns selected availability
windows, unique priorities, guards, emitted statements and `no_op` fallback.
Every top-level setting has provenance; behavioral settings are structural
choices anchored to sources, not dataset-fitted parameters.

The horizon, exact replay and terminal transport are integrity requirements.
28 outcome expectations describe records for the canonical baseline, including
the deliberately unobserved election; unmet expectations do not invalidate an
otherwise complete run. Delay or missing communication can leave nominee or
meeting records open. No complete release may discard unresolved transport.
Failed attempts retain sealed-prefix custody and cannot masquerade as full runs.

Changed authority or field meaning requires a semantic successor and dependent
registry/configuration/package rebuild. Changed timing within those bounds is
a configuration successor. Current formal paths contain one accepted version;
Git and ignored custody retain history and construction attempts.

## 10. Worked cases, falsification, and limitations

- Concurrent shareholder positions: Baoneng and China Resources can record
  opposition in the same coordinate without either acquiring the other's power.
- Missing proposal: no delivered Metro terms means no selected Vanke proposal;
  the environment does not create the transaction to match the Draft.
- Board authority: Wang or Yu submitting `record_board_rejection` is invalid,
  even though each holds a management role in the source.
- Late nominees: acquisition disclosure can be recorded while absent/delayed
  nominee information leaves registration, personal response or meeting notice
  open. A valid complete graph must still account for all executed records.
- Outcome boundary: a scheduled June30 meeting never changes election_result;
  a graph that labels elected directors would exceed this scenario.

This is a sparse disclosure/decision-record model, not a takeover strategy or
market microstructure simulation. Its choices and dependencies remain strongly
informed by full Draft exposure. Internal negotiation, voting, funding and
external market response are unmodeled. A broader decision set requires better
supported semantic parents before any LLM implementation or scientific study.
