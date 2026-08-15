# Development environments

MASim has distinct validation and runtime profiles. Choose the smallest one
that matches the work being performed; passing a smaller profile does not
establish readiness for a larger one.

## Lightweight H2EPR contract validation

The portable baseline in `environments/lmsim.yml` provides Python 3.11 and the
tools needed for the repository-only H2EPR contracts and the pure G1/G2
construction surface. After creating and activating that environment, run from
the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=projects/h2epr/src \
  python -m pytest -p no:cacheprovider \
  projects/h2epr/tests/contracts \
  projects/h2epr/tests/construction \
  projects/h2epr/tests/g2
```

This command validates offline schemas, synthetic fixtures, contract semantics,
Construction IR, and G2 artifact/EventBundle construction. It does not import
the G3 MASim/Ray runtime, start a simulation, call a model or retrieval service,
or evaluate a real event process.

The environment file is the portable validation baseline, not a lock for every
MASim or H2EPR runtime dependency. Later reviewed work may revise the runtime
profile without weakening the retained contract suite.

## Canonical H2EPR G3 runtime development

The project uses the local conda environment named `LMSim` for H2EPR runtime
development and validation. G3 additionally requires this MASim checkout, Ray
and its direct runtime libraries, and the separately sourced `lmbase` project.
The current clean-runner workflow pins the reviewed lmbase source revision
instead of silently relying on an unrelated editable checkout or installing
lmbase's full model-development dependency set.

From the repository root, with a reviewed lmbase checkout available, the G3
owning tests use:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=projects/h2epr/src:/path/to/lmbase \
  python -B -m pytest -p no:cacheprovider projects/h2epr/tests/g3
```

These tests exercise the deterministic Rule-only engineering surface. The
approved local canary additionally uses private/loopback Ray processes, but is
not part of routine contract validation and does not establish scientific
fidelity.

## Full MASim runtime development

Running standard MASim scenarios requires the runtime dependencies in
`requirements.txt` and the separately sourced `lmbase` project described there.
Some scenario variants also require model-provider credentials. Follow
`docs/run-simulation.md` only when the task explicitly authorizes an actual
run. The G3 CI profile is intentionally narrower and must not be treated as a
replacement for this full scenario environment.

H2EPR project source remains repository-local and is not installed as a Python
package by `setup.py`. G3 imports it explicitly through `PYTHONPATH`; future
packaging may evolve through a reviewed change without changing that present
boundary.
