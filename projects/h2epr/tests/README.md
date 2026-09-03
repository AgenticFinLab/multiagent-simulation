# Tests

The maintained suite uses standard-library `unittest` so the Rule baseline is
executable in the current offline environment.

| Package | Coverage |
|---|---|
| `benchmark` | Source admission, semantic compilation, package identities, planned-backend failure, tamper and path boundaries |
| `semantic` | Agent/Population, roster, interface, scenario, configuration, manifest, and checksum closure |
| `runtime` | Three timelines, decisions, environment effects, transport, trace, seals, replay, graph, determinism, identity invariance, and cross-event conformance |
| `publication` | Independent custody derivation, compact releases, readings, and resealed-forgery rejection |
| `experiments` | Plan identity, package/binding admission, custody uniqueness, model-control parity, scheduling, failures, analysis, and claim limits |
| `standards` | Schema catalog, Skill inventory, current-only repository shape, local links, and publication surface |

Run everything from the repository root:

```bash
PYTHONPATH=projects/h2epr/src python -B -m unittest discover \
  -s projects/h2epr/tests -t projects/h2epr/tests -p 'test_*.py' -v
```

Run one package by replacing the discovery root with, for example,
`projects/h2epr/tests/runtime` while keeping
`-t projects/h2epr/tests`.

LLM and RuleLLM have no skipped success tests or placeholder implementation.
Their admission paths fail closed while those backends remain planned.
