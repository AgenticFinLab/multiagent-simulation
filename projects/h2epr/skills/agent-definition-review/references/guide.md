# Participant semantic review guide

## Independence and record

Review the candidate against its accepted parents, not against the author's
intent or a successful run. Record candidate path/hash, Source Profile,
roster/actor map, interface registries, Scenario candidate, template revision,
reviewer, date, and exposure boundary. A changed candidate invalidates the
review record.

## Severity model

| Severity | Meaning | Disposition |
|---|---|---|
| blocker | protected exposure, source fabrication, impossible identity, or scripted outcome | stop; candidate cannot progress |
| high | missing authority, active actor, observation owner, intent result, or backend-neutrality boundary | return to owning layer |
| medium | incomplete worked case, limitation, successor trigger, or cross-participant explanation | revise before release |
| low | local clarity or navigation issue with no semantic widening | may close with recorded correction |

Never average findings into a score. One unresolved blocker or high finding
prevents acceptance.

## Review passes

1. Reconstruct the represented decision interface from the dataset anchors.
2. Erase names and ask whether authority still follows roles and state.
3. Swap two actor IDs and check that no hidden name branch changes semantics.
4. Remove or stale each material observation and inspect the declared response.
5. Inject later Draft information and verify it is forbidden at the earlier
   decision point.
6. Submit invalid target, payload, authority, and lifecycle combinations.
7. Make the environment deny or partially realize an admissible intent.
8. Perturb one material observation and one aggregation choice.
9. Compare the prose with registry projections for widening or missing rows.
10. Search for thresholds, prompts, decoding, selected parameters, or assumed
    successful results that belong to another layer.

## Finding format

Every finding contains severity, stable finding ID, direct evidence, violated
contract, impact, owning layer, required correction, and retest. Distinguish a
file fact from reviewer inference. Close a finding only against new candidate
bytes and record how the evidence changed.

## Verdicts

- `accept`: all passes close and no material limitation is omitted.
- `accept with recorded limitations`: the interface is executable and honest,
  while explicitly bounded dataset or aggregation limits remain.
- `return to owning layer`: a semantic or evidence defect prevents release.

The review never promotes a backend or validates history. It certifies that
the human semantic parent is dataset-bounded, internally coherent,
backend-neutral, and falsifiable.

## Failure routing

Route each open finding to the layer named in its record. Source and roster
defects return to admission/mapping; representation defects return to the
semantic parent; world ownership returns to Scenario work; selected values and
decision procedures return to configuration or backend realization. A review
must not repair another layer inside its verdict.

## Handoff

Publish the finding ledger, candidate identity, closed/admitted limitations,
registry parity result, adversarial cases exercised, final verdict, and next
legal action. Event-wide batch review remains required after individual
acceptance.
