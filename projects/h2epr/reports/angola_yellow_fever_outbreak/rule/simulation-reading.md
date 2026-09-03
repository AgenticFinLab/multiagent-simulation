# Angola Yellow Fever Outbreak of 2016 Rule simulation reading

## Run identity

This reading covers the complete canonical seed-0 Rule output for H2EPR-0551.
Construction used the fully exposed Draft and exactly the three dataset inputs
sealed by the Source Profile. No Reference EPG, held-out material, external
research, or network retrieval entered the event package. The run is a
deterministic, dataset-conditioned construction baseline.

| Item | Identity |
|---|---|
| package | `h2epr.event-package.0551.v1`; `d6456af798b2593d264b18f7b1a4f0bf360682cfe36a26965ed3d29dbfe5c2b6` |
| Rule binding | `be5013c6677d8aae4de67f0ce37064966c590c4380cf16fb523d687b1f50a269` |
| Rule configuration | `h2epr.0551.rule.v1`; `a11794e113e3e71857552be6b66e9568ff4ae88a9964e45d31d2a2a7bb4e0a94` |
| canonical run | `run.2c5f37a8e456f99bdb1eff02`; seed `0`; model and network access denied |
| run manifest | `32527f4ebacc54e2762a392d28daf5d0c0b9b7297c44ae9f79e738b392c37dcb` |
| trace | `edec83529744119588cc50c14acb83c270f93699335121ecc791a858b404b1e0` |
| terminal state | `0a0b2245ca514c0ad69a212a0f0338cc836ad08065a301e1d024bd75aae700a4` |
| run seal | `2bdddf577ba041e109dbd804b6655bd250e7750fc72d5ca0a84ac6d2e75977ae` |
| Generated EPG | semantic seal `e76b4c4960a607af51ab274bb0634834562cc54ef8da4af1d05fb89ff7cd346f`; source trace as above |
| replay | pass; 826 records and 20 ticks replayed to the exact terminal-state hash |
| raw custody | `.local-runtime/h2epr-simulation/runs/benchmark/angola_yellow_fever_outbreak/rule/current/materialization-a` |

Canonical materializations A and B are byte-identical across all nine output
files. The determinism receipt is
`6a2698b9824bcae1a3f36cead2b0f5a8531a9601311bba3987e17e6d63024b03`.
A generated-ID probe changed run and record identities while preserving the
semantic trace, semantic graph, and terminal state. Its identity-conformance
receipt is
`12c75b14adff001c827ae28495a77607e5fc558f954253567c4a288a8e3a9ec5`.

## Complete-output coverage

The reading traversed all 826 JSONL records, all 866 graph nodes, and all
2,147 graph edges. It checked every edge endpoint and every node and edge
source-trace reference. The graph has 866 unique node IDs and 2,147 unique
edge IDs; all endpoints resolve, all 826 trace IDs are represented, no unknown
trace ID is cited, and no trace record is uncovered.

| Record family | Count | Reading result |
|---|---:|---|
| observations, participant decisions, action intents, action dispositions | 160 each | one complete path for each of 8 actors at each of 20 coordinates |
| non-`no_op` / `no_op` actions | 26 / 134 | all 160 dispositions accepted; 26 applied and 134 admitted with no effect |
| message intents | 30 | every intent has one queued and one delivered disposition |
| message dispositions | 60 | 30 queued and 30 delivered; none rejected, duplicated, or unresolved |
| state deltas | 26 | each links to an accepted source intent and declared state entity |
| stage entries | 4 | one entry for S1, S2, S3, and S4 |
| generated annotations | 5 | confirmation, two assessments, scaled response, and ongoing surveillance |
| tick opens, commits, and seals | 20 each | every coordinate closes against its poststate |
| run seals | 1 | zero unresolved intent IDs and recipient IDs |

The Generated EPG adds one generated-event node, 20 coordinate nodes, 8
participant nodes, 11 state-entity nodes, and one node for every trace record.
Its edge families cover temporal placement, participant decisions, action and
message provenance, state changes, stage membership, annotation aggregation,
and seals. For example, `edge.b4424d59b287332b0564a4c110ef3555`
connects the IP-D confirmation delta to the laboratory state entity, and
`edge.ecc79486c2f86924ebb3a2a13c0603a2` connects the final Uganda
surveillance-message delivery to its queued predecessor.

## Generated trajectory

The opening state has no represented detection or confirmation; pending
laboratory results and committee assessments; inactive campaigns, scaled
response, and surveillance; no recorded cross-border signal; and an active
Uganda outbreak label. The common Rule backend produces the following process:

| Coordinate | Generated transition | Direct trace evidence |
|---|---|---|
| c01, S1/E1 | Angola detects the represented outbreak and routes a WHO notice plus two laboratory referrals. | decision `…00000011`; delta `…00000039`; stage entry `…00000041` |
| c02, S1/E2 | IP-D and NICD receive referrals, record separate confirmations, and notify WHO. | decisions `…00000061`, `…00000064`; deltas `…00000083`–`84` |
| c03, S1/E2 | WHO records initial confirmation only after both laboratory messages arrive. | deliveries `…00000088`–`89`; decision `…00000112`; delta `…00000122` |
| c04, S2/E3 | Angola records the case-surge report and sends it to WHO. | decision `…00000137`; delta `…00000161`; stage entry `…00000163` |
| c05, S2/E3 | Angola launches the represented local vaccination campaign and notifies the aggregate Population. | decision `…00000177`; delta `…00000201` |
| c06, S2/E3 | The Population records aggregate participation after notice delivery and reports to Angola and WHO. | decision `…00000214`; delta `…00000242` |
| c07–c08, S2/E4 | DRC reports imported cases; WHO then documents cross-border risk and notifies the emergency committee. | decisions `…00000260`, `…00000309`; deltas `…00000282`, `…00000321` |
| c09, S3/E5 | WHO convenes the first represented committee process and sends three invitations. | decision `…00000348`; delta `…00000364`; stage entry `…00000366` |
| c10–c11, S3/E5 | Angola and DRC submit distinct briefings; the committee receives both and issues the first assessment. | decisions `…00000382`, `…00000385`, `…00000435`; deltas `…00000408`–`09`, `…00000449` |
| c12, S3/E6 | WHO receives the assessment, records scaled coordination, and sends guidance to both countries and the Population. | decision `…00000477`; delta `…00000493` |
| c13, S3/E6 | Angola and DRC receive guidance and record separate implementation states. | deliveries `…00000497`–`98`; decisions `…00000509`, `…00000511`; deltas `…00000531`–`32` |
| c14, S3/E6 | The two-tick population route delivers guidance; the Population records regional participation and sends two reports. | delivery `…00000536`; decision `…00000545`; delta `…00000573` |
| c15–c17, S3/E7 | Both countries record progress reports, WHO convenes the second committee process, and the committee issues the second assessment. | decisions `…00000590`, `…00000593`, `…00000645`, `…00000682`; deltas `…00000616`–`17`, `…00000657`, `…00000696` |
| c18, S4/E8 | Uganda records an outbreak-end declaration and routes it to WHO. | decision `…00000720`; delta `…00000736`; stage entry `…00000738` |
| c19, S4/E9 | WHO, Angola, DRC, and Uganda separately activate ongoing surveillance; the three country actors send updates. | decisions `…00000752`, `…00000755`, `…00000762`, `…00000767`; deltas `…00000780`–`83` |
| c20, S4/E9 | The terminal barrier delivers all three surveillance updates without adding a state transition. | deliveries `…00000788`–`90`; terminal tick seal `f7019924…b0171` |

The ellipses abbreviate the common prefix
`trace.run.2c5f37a8e456f99bdb1eff02.`. Corresponding graph record nodes
use the same suffix under
`record.trace.run.2c5f37a8e456f99bdb1eff02.*`. Generated annotations occur
at records `…00000124`, `…00000451`, `…00000575`, `…00000698`, and
`…00000785`.

Terminal values are process labels. Detection, dual laboratory confirmation,
two committee meetings, and all message lifecycles have closed within the
configured process. Recorded assessments, country implementation labels, and
the Uganda declaration persist as generated outcomes. The local campaign and
both population-participation fields remain active or participating;
surveillance remains deliberately `ongoing`; and `surge_reported` and
`no_recent_confirmed_cases_reported` remain reports rather than an inferred
epidemic closure.

## Mechanism reading

Direct run facts show a message- and state-gated process. The shared
configuration fixes the 20 logical coordinates and routes. The declarative
Rule backend selects rows by actor, coordinate, delivered messages, and
prestate. The authoritative environment alone admits effects and changes
state. Laboratory referral gates the two c02 decisions; dual confirmation
messages gate c03; country briefings gate the first assessment; the first
assessment gates scaled coordination; the two country progress messages gate
the second review; and the final barrier closes three outstanding surveillance
deliveries.

All eight actors submit one decision per coordinate against one sealed
prestate. Twenty-six event rows produce 26 non-conflicting deltas, while 134
unmatched actor-coordinate pairs take the explicit accepted `no_op` path. The
two c02 confirmations, two c10 briefings, two c13 implementations, two c15
progress reports, and four c19 surveillance transitions touch distinct fields
within their respective batches. MASim transport owns queued/delivered
lifecycle changes; the reducer, trace writer, and H2EPR runtime own committed
state, the hash chain, tick/run seals, replay, and graph projection.

The actorization is intentionally mixed. Seven named organizational or
committee interfaces are Agents, while the changing P_3 Luanda/Angola/DRC
scope becomes one explicitly lossy aggregate Population. P_7 and P_10 remain
world-state dispositions because the Draft does not expose autonomous choices
for them. This prevents population labels from becoming artificial decision
makers merely to obtain full-roster execution.

### Interpretation

Within this configuration, coordination is concentrated at four inspectable
handoffs: referrals into laboratory confirmation, country information into
committee assessment, assessment into scaled response, and national progress
into the second review. Separating WHO from its emergency committee, and WHO
coordination from national implementation and population participation,
preserves visible authority boundaries. The generated process also keeps the
Uganda declaration separate from the deliberately open regional-surveillance
state.

This interpretation is conditional on exposed-Draft sequencing and selected
Rule guards. It does not show that these messages caused the historical
actions or that the represented public-health measures were effective. It
does show that the event-neutral framework can express a public-health event
with mixed actorization, changing source scope, parallel national actions,
open terminal states, and a transport barrier without an event branch in
common Python.

## Limitations

- Construction saw the full Draft, so Draft-facing resemblance is expected
  and is not held-out predictive evidence.
- The frozen evidence is heterogeneous and was not externally reconciled.
  Draft relation-direction, participant-name, and endpoint inconsistencies are
  preserved as source defects but do not define executable authority.
- P_3 retains one source ID while changing geographic scope. Its aggregate
  Population records this loss; no individual vaccination, dose receipt,
  coverage, or heterogeneous health trajectory is simulated.
- Logical ticks preserve a selected order but do not calibrate elapsed time,
  epidemiological dynamics, incubation, transmission, vaccine supply, or
  route delay.
- `confirmed`, `implemented`, `implemented_fractional`,
  `no_recent_confirmed_cases_reported`, and `declared_ended` are modeled
  report or process states. They do not independently prove case counts,
  transmission interruption, response success, or public-health effect.
- The event end is open. Ongoing surveillance is retained rather than replaced
  with an invented terminal resolution, and the Uganda milestone does not
  establish an Angola-specific causal relationship.
- This Rule run supports package, execution, integrity, replay,
  graph-provenance, and bounded descriptive claims. It does not support
  historical fit, parameter calibration, held-out evaluation, causal or
  scientific validity, policy effectiveness, or universal generality.

The next eligible work after release acceptance is a separately authorized
third event, perturbation, or backend comparison. This reading does not
authorize LLM/RuleLLM implementation or scientific evaluation.
