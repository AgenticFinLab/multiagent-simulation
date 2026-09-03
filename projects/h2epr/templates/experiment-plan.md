# Experiment plan template

## 1. Purpose and comparison claim

State the bounded question answered by assembling these runs. Name the
comparison kind and the engineering or descriptive claim it can support.

## 2. Accepted parents

List each event package, backend binding, shared configuration, analysis
contract, and content identity. Record input exposure and excluded claim
classes.

## 3. Matrix rows and seeds

Give every row a stable ID, event, package, backend, explicit seed set, and
fresh ignored custody root. For model rows, pin model, prompt, response,
decoding values and bases, and attempt provenance. Show the canonicalized
custody locator and the model-control signature used for parity review.

## 4. Parity and controlled differences

For each comparison group, state what must be byte- or identity-equal and what
may differ. Explain any field that cannot be compared across events.
For model-backed groups, require identical provider/model/version, service
mode, prompt and response identities, decoding values and bases, and attempt
limit wherever those controls are not the declared treatment.

## 5. Scheduling and resources

Declare concurrency ceiling, wall timeout, stall timeout, progress signal,
poll interval, model quota assumptions, and capacity constraints.

## 6. Failure and retry policy

Classify admission, model, provider, resource, stall, runtime, evidence, and
analysis failures. Name the retryable classes, finite retry limit, and custody
rule for every attempt.

## 7. Analysis contract

Pin simulation-only and comparison definitions before execution. Define
required inputs, missing-value behavior, aggregation unit, denominator, and
event-local exceptions.

## 8. Completion and publication

Define terminal row dispositions, minimum evidence for release, treatment of
failed attempts, checksum inventory, and exact reproduction commands.

## 9. Claim boundary and threats

Separate plan integrity, execution evidence, process interpretation, and any
future scientific evaluation. List confounds and unsupported conclusions.

## 10. Admission record

Record plan and receipt identities, validation commands, Git state, reviewer,
disposition, and next legal action. Admission does not authorize execution
unless that action is separately in scope.
