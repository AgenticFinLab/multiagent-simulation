# Research projects

The `projects/` directory contains research systems that use MASim while
maintaining their own contracts, data boundaries and development lifecycle.
They are larger than a standard scenario under `examples/` and may include
multiple event configurations, compilers or evaluation protocols.

## Projects

### H2EPR

H2EPR builds auditable multi-agent simulations from bounded benchmark event
packages. It combines typed construction, participant and scenario semantics,
fail-closed configuration admission, deterministic runtime records, replay,
graph compilation, and independent release verification. Rule is the current
implemented backend. The current-event registry, rather than prose or a
directory's presence, identifies accepted event results.

- [Project guide](H2EPR.md)
- [Source and tests](h2epr/)
- [Event entries](h2epr/events/README.md)
- [Event modeling workflow](h2epr/WORKFLOW.md)
- [Architecture](h2epr/ARCHITECTURE.md)
- [Evolution policy](h2epr/EVOLUTION.md)
- [Current event registry](h2epr/events/current-events.json)

## Repository convention

Project-specific evidence, Agent behavior, scenarios and evaluation methods
stay inside the project that owns them. Shared H2EPR capabilities remain under
`projects/h2epr/`, even when more than one H2EPR event uses them. MASim changes
only through separately scoped base-framework work; H2EPR does not promote its
project code back into `masim/`.

Standard MASim scenarios continue to use the root `examples/` and `configs/`
directories.
