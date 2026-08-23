# Development environments

MASim has separate contract-validation and runtime profiles. Use the smallest
profile that covers the work being performed; passing a contract suite does
not establish runtime or experiment readiness.

## H2EPR contract and asset validation

The environment in `environments/lmsim.yml` provides Python 3.11 and the tools
needed for offline contract, construction, configuration, and research-asset
checks. H2EPR is packaged independently from MASim. Install it from the
repository root:

```bash
python -m pip install -e "projects/h2epr[test]"
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/contracts \
  projects/h2epr/tests/construction \
  projects/h2epr/tests/configuration \
  projects/h2epr/tests/agents
```

These suites resolve checked-in schemas without network access and do not
start a simulator, call a model provider, or evaluate an event.

## H2EPR runtime development

Runtime tests additionally use this MASim checkout and its dependencies.
Install MASim and the separately sourced `lmbase` package as described in
`requirements.txt`, then install H2EPR:

```bash
python -m pip install -e ".[tests]"
python -m pip install -e "projects/h2epr[test]"
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/g2 \
  projects/h2epr/tests/g3 \
  projects/h2epr/tests/g4
```

The deterministic runtime suites do not require model-provider credentials.
An actual distributed or model-backed run has additional resource, credential,
and output requirements and must pass the experiment preflight described in
`docs/experiment-preflight-skill/`.

## Standard MASim scenarios

Standard scenarios use the dependencies in `requirements.txt`; some variants
also require model-provider credentials and a retrieval corpus. Follow
`docs/run-simulation.md` and the scenario's own README for the exact command.

Generated run data belongs under `EXPERIMENT/`. Curated result packages under
`simulation-results/` are produced separately and are not runtime inputs.
