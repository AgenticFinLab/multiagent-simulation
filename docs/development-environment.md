# Development environments

MASim has two distinct development surfaces. Choose the smallest one that
matches the work being performed.

## Lightweight H2EPR contract validation

The portable baseline in `environments/lmsim.yml` provides Python 3.11 and the
exact Phase-0 validation tools. After creating and activating that environment,
run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider projects/h2epr/tests
```

This command validates only offline schemas, synthetic fixtures, and contract
semantics. It does not install the MASim runtime, start a simulation, call a
model or retrieval service, or evaluate a real event process.

The environment file is a reproducible current baseline. Later Phase-1 work
may add or revise dependencies through a reviewed change; Phase 0 does not
freeze the future runtime environment.

## Full MASim runtime development

Running standard MASim scenarios additionally requires the runtime dependencies
in `requirements.txt` and the separately sourced `lmbase` project described
there. Some scenario variants also require model-provider credentials. Follow
`docs/run-simulation.md` only when the task explicitly authorizes an actual
run.

H2EPR Phase 0 is repository-only and is not installed as a Python package by
`setup.py`. Its future runtime/package ownership requires a separate Phase-1
architecture decision based on implementation evidence.
