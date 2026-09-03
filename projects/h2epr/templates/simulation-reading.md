# Simulation reading template

## Run identity

Record event, package, backend, realization, configuration, seed/model,
runtime, trace, replay, Generated EPG, exposure, and claim boundary.

## Complete-output coverage

Record the exact trace, node, and edge counts actually traversed. Confirm every
graph endpoint and source-trace reference, trace-to-graph coverage, action and
message disposition, state delta, annotation, stage entry, seal, and terminal
transport lifecycle. Sampling only action nodes is not a complete reading.

## Generated trajectory

Describe opening state, early transitions, turning points, terminal state,
messages, rejected or partial intents, unresolved lifecycles, and generated
stages. Cite trace or graph record IDs for direct run facts.

Classify terminal values as closed lifecycles, persistent outcomes, or
deliberately open states. Do not invent a closing transition because a field
name sounds temporary.

## Mechanism reading

Explain which participant, backend, environment, transport, or reducer
mechanisms produced the trajectory. Separate direct run evidence from
interpretation.

## Limitations

State synthetic settings, exposed Draft use, omitted processes, model failures,
and conclusions the run cannot support. Any Draft-facing comparison receives a
separate label and is not an unbiased benchmark score when construction was
full-Draft-exposed.
