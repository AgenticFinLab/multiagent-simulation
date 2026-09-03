# Shared contract feedback record

## Observation

Name the event phase, exact product/runtime identity, and direct evidence that
exposed a portability or usability problem. Describe the smallest behavior
that failed; do not generalize from domain vocabulary alone.

## Classification

| Question | Answer |
|---|---|
| Is the issue event-specific, shared H2EPR, MASim-owned, or future-phase? | |
| Which authority currently owns the behavior? | |
| Is the current schema valid but semantically insufficient? | |
| Can a new collaborator detect the issue before execution? | |
| Does the correction change accepted identity or require a successor? | |

Event-specific source or representation issues remain in the event. MASim
issues are recorded for separate base-framework work. Only a demonstrated
shared H2EPR gap proceeds below.

## Reduced synthetic case

State the event-neutral vocabulary, minimum inputs, expected result, observed
failure, and negative assertion. Add the case to the synthetic suite before
changing shared code. A real event must not become the hidden regression
oracle.

## Contract correction

List the minimal Skill, template, schema, validator, CLI, publication, or test
changes; affected consumers; failure code; compatibility decision; and
successor requirement. Explain why a narrower documentation-only or
event-local correction is insufficient.

## Verification and disposition

Record the initially failing synthetic test, passing focused test, complete
framework suite, real-event rerun, unchanged unrelated identities, and Git
state. Use `adopt`, `adopt with successor`, `event-local`, `MASim-owned`, or
`defer to future phase`. State the bounded effect and next legal action.
