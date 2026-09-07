# Development environments

MASim has separate contract-validation and runtime profiles. Use the smallest
profile that covers the work being performed; passing a contract suite does
not establish runtime or experiment readiness.

## H2EPR contract and asset validation

The environment in `environments/lmsim.yml` provides Python 3.11 and the tools
needed for offline validation. H2EPR is packaged independently from MASim.
The maintained test groups below match `.github/workflows/h2epr-validation.yml`.
Install it from the
repository root:

```bash
python -m pip install -e "projects/h2epr[test]"
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/standards \
  projects/h2epr/tests/semantic \
  projects/h2epr/tests/benchmark \
  projects/h2epr/tests/experiments \
  projects/h2epr/tests/publication
```

These suites resolve checked-in schemas without network access. Publication
and experiment tests include temporary synthetic Rule materializations; this
is not a read-only validation command. They do not call a model provider or
perform held-out evaluation.

## H2EPR runtime development

The offline Rule tests use the unchanged MASim event-process kernel from this
checkout. H2EPR's isolated loader supports an environment without the complete
distributed/model stack. With the H2EPR validation dependencies installed:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/runtime
```

All current H2EPR tests also support standard-library discovery from the
repository root when the existing environment supplies H2EPR's dependencies:

```bash
PYTHONPATH=projects/h2epr/src:projects/h2epr/tests \
PYTHONDONTWRITEBYTECODE=1 RAY_USAGE_STATS_ENABLED=0 \
python -B -m unittest discover -s projects/h2epr/tests -v
```

These tests create temporary materializations and require writable temporary
storage, but no model-provider credentials. The CI runtime job separately
checks the full MASim import path with pinned `lmbase` and dependencies; use
that workflow for its exact installation profile. An isolated-kernel pass
does not establish distributed or model-backed readiness.
An actual distributed or model-backed run has additional resource, credential,
and output requirements and must pass the experiment preflight described in
`docs/experiment-preflight-skill/`.

## Standard MASim scenarios

Standard scenarios use the dependencies in `requirements.txt`; some variants
also require model-provider credentials and a retrieval corpus. Follow
`docs/run-simulation.md` and the scenario's own README for the exact command.

Generated run data belongs under `EXPERIMENT/`. Curated result packages under
`simulation-results/` are produced separately and are not runtime inputs.
