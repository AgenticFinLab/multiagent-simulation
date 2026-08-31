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
compilation. The Panic of 1907, SingHealth Data Breach, and Samsung Galaxy
Note7 Battery Recall Crisis assets provide a three-event method baseline with
deterministic full-roster Rule execution, authoritative replay, and
trace-derived generated graphs. The result is uncalibrated engineering
mechanism coverage, not a scientific-validity claim.

- [Project guide](H2EPR.md)
- [Source and tests](h2epr/)
- [Event entries](h2epr/events/README.md)
- [Event modeling workflow](h2epr/WORKFLOW.md)
- [Architecture](h2epr/ARCHITECTURE.md)
- [Evolution policy](h2epr/EVOLUTION.md)
- [Three-event execution conformance](h2epr/execution/cross-event-conformance-v0.2/)

## Repository convention

Project-specific evidence, Agent behavior, scenarios and evaluation methods
stay inside the project that owns them. Shared H2EPR capabilities remain under
`projects/h2epr/`, even when more than one H2EPR event uses them. MASim changes
only through separately scoped base-framework work; H2EPR does not promote its
project code back into `masim/`.

Standard MASim scenarios continue to use the root `examples/` and `configs/`
directories.
