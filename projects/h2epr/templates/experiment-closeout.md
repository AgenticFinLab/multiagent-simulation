# Experiment closeout template

## Identity and scope

Record plan, admission receipt, code, package, binding, runtime, MASim, model,
analysis, and Git identities. Restate the comparison and claim boundary.

## Row and attempt ledger

List every planned row and seed. For every attempt, record custody, start and
terminal disposition, retry parent if any, run/release identity, and failure
class. Preserve failures in the denominator.

## Execution and evidence closure

Report package admission, trace/seal/replay/graph checks, unresolved transport,
repeatability or model variation, output checksums, and release status. Mark
missing evidence explicitly.

## Resource and scheduling record

Report actual concurrency, wall and stall outcomes, resource or quota
deviations, and any scheduling change. Explain why the change does or does not
alter comparison meaning.

## Analysis coverage

List each pinned analysis contract, available and unavailable measures,
aggregation units, denominators, and excluded attempts. Separate direct output
facts from interpretation.

## Findings and limitations

Give bounded within-event and cross-event findings. Record alternative
explanations, event-local semantics, and unsupported scientific conclusions.

## Disposition

Use one status for the whole plan and one terminal disposition per row. State
whether the result is releasable, requires rerun, returns to an owning layer,
or remains incomplete.
