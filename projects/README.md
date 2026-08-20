# Research projects

The `projects/` directory contains research systems that use MASim while
maintaining their own contracts, data boundaries and development lifecycle.
They are larger than a standard scenario under `examples/` and may include
multiple event configurations, compilers or evaluation protocols.

## Projects

### H2EPR

H2EPR studies auditable multi-agent reconstruction of real event processes.
Its current engineering path covers typed construction, participant artifacts,
deterministic Rule execution, sealed traces and Generated EPG compilation.
Current research focuses on event-specific Agent Definitions for the Panic of
1907.

- [Project guide](H2EPR.md)
- [Source and tests](h2epr/)
- [Architecture](h2epr/ARCHITECTURE.md)
- [Evolution policy](h2epr/EVOLUTION.md)

## Repository convention

Project-specific evidence, Agent behavior, scenarios and evaluation methods
stay inside the project that owns them. Reusable capabilities move into
`masim/` only after they have a clear domain-neutral interface and more than
one credible consumer.

Standard MASim scenarios continue to use the root `examples/` and `configs/`
directories.
