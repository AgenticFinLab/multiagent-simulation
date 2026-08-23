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
For the Panic of 1907, the first event-standardization cycle is complete
through a non-executable Scenario Configuration, fail-closed static admission,
a bounded KT--NBC--NYCH binding and focused E7 conformance/trace/replay. This is
a reusable engineering baseline, not a full-event simulation or a historical-
validity claim; the normal next method step is a separately selected second-
event forward test.

- [Project guide](H2EPR.md)
- [Source and tests](h2epr/)
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
