# Research projects

The `projects/` directory contains research systems that use MASim while
maintaining their own contracts, data boundaries and development lifecycle.
They are larger than a standard scenario under `examples/` and may include
multiple event configurations, compilers or evaluation protocols.

## Projects

### H2EPR

H2EPR studies auditable multi-agent reconstruction of real event processes.
It combines typed construction, participant and scenario semantics,
fail-closed configuration admission, deterministic runtime records, and graph
compilation. The Panic of 1907 and SingHealth Data Breach assets provide a
bounded cross-event method baseline; they do not constitute full-event
simulations or scientific-validity claims.

- [Project guide](H2EPR.md)
- [Source and tests](h2epr/)
- [Event entries](h2epr/events/README.md)
- [Event modeling workflow](h2epr/WORKFLOW.md)
- [Architecture](h2epr/ARCHITECTURE.md)
- [Evolution policy](h2epr/EVOLUTION.md)

## Repository convention

Project-specific evidence, Agent behavior, scenarios and evaluation methods
stay inside the project that owns them. Reusable capabilities move into
`masim/` only after they have a clear domain-neutral interface and more than
one credible consumer.

Standard MASim scenarios continue to use the root `examples/` and `configs/`
directories.
