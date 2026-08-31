# H2EPR tests

The H2EPR suites validate serialized contracts, research-asset boundaries,
configuration admission, deterministic runtime behavior, and graph
compilation. Most suites are offline and do not start a simulator.

Install the project before running tests:

```bash
python -m pip install -e "projects/h2epr[test]"
```

## Suite ownership

| Directory | Responsibility |
|---|---|
| `contracts/` | JSON Schemas, cross-object invariants, repository boundaries, trace, and identity |
| `construction/` | Explicit source loading, lossless construction records, evidence isolation, import boundaries, and repository-level formal-asset integrity |
| `g2/` | Entity registry, participant artifacts, world inputs, and event-bundle construction |
| `configuration/` | Schema admission, canonical identity, references, assembly, failure classes, and portable receipts |
| `execution/` | Policy Realization, executable successors, shared run-closure kernel, repeated runs, replay, graph closure, custody, and fail-closed release boundaries |
| `agents/` | Definition profiles, mappings, bindings, participant slices, and lineage conformance |
| `g3/` | Phased runtime, policies, reducer, transport, trace, seals, replay, and detectors |
| `g4/` | Sealed-trace inventory, deterministic graph compilation, and graph seals |

The `g2`, `g3`, and `g4` directory names are retained identifiers for the
accepted artifact, runtime, and compiler suites. They do not imply that later
research phases run automatically.

## Commands

Run all H2EPR tests from the repository root:

```bash
python -B -m pytest -p no:cacheprovider projects/h2epr/tests
```

Run the offline contract and construction surface:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/contracts \
  projects/h2epr/tests/construction \
  projects/h2epr/tests/g2 \
  projects/h2epr/tests/execution
```

Run configuration and participant-asset checks:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/configuration \
  projects/h2epr/tests/agents
```

The bounded KT--NBC--NYCH binding and conformance modules can be checked
independently:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/agents/test_panic_1907_lineage_binding.py \
  projects/h2epr/tests/agents/test_panic_1907_lineage_conformance.py
```

The SingHealth semantic releases can be checked independently:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/agents/test_singhealth_roster_release.py \
  projects/h2epr/tests/agents/test_singhealth_scenario_mapping_release.py \
  projects/h2epr/tests/configuration/test_singhealth_scenario_configuration_release.py
```

The Note7 mapping, Scenario, configuration, and bounded admission releases can
be checked independently:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/agents/test_samsung_note7_mapping_scenario_release.py \
  projects/h2epr/tests/configuration/test_samsung_note7_scenario_configuration_release.py \
  projects/h2epr/tests/configuration/test_samsung_note7_scenario_configuration_admission.py
```

The bounded SingHealth carrier binding and lineage conformance can be checked
independently:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/agents/test_singhealth_data_breach_lineage_binding.py \
  projects/h2epr/tests/agents/test_singhealth_data_breach_lineage_conformance.py
```

The bounded Note7 carrier binding and lineage conformance can be checked
independently:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/agents/test_samsung_note7_lineage_binding.py \
  projects/h2epr/tests/agents/test_samsung_note7_lineage_conformance.py
```

The three configuration-admission profiles and their focused rejection cases can
be checked together:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/configuration/test_scenario_configuration_admission.py \
  projects/h2epr/tests/configuration/test_singhealth_scenario_configuration_admission.py \
  projects/h2epr/tests/configuration/test_samsung_note7_scenario_configuration_admission.py
```

The shared execution kernel and its exact Panic conformance can be checked
independently:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/execution/test_shared_execution_kernel.py
```

The accepted Panic and SingHealth run releases can be checked together at the
cross-event closure boundary:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/execution/test_cross_event_execution_conformance.py
```

Formal H2EPR JSON, release checksum inventories, and publication-surface local
links share one repository-level check:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/construction/test_repository_publication_surface.py
```

The main H2EPR workflow runs this check with the construction suite. A small
publication-only workflow runs the same check when one of the outer repository
guides changes without a project-tree change.

Runtime and compiler checks use the MASim dependencies described in the root
`requirements.txt`:

```bash
RAY_USAGE_STATS_ENABLED=0 python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/g3 \
  projects/h2epr/tests/g4
```

These tests exercise deterministic Rule paths. They do not run model-backed
experiments or establish historical fidelity.

## Fixture boundaries

- `fixtures/construction_ir/` contains minimized synthetic construction
  inputs. Cross-domain tests use only explicitly listed, hash-pinned files.
- `fixtures/g2/`, `fixtures/g3/`, and `fixtures/g4/` contain synthetic
  closed-value inputs rather than experiment output or historical targets.
- `fixtures/agents/panic_1907/minimal_binding_v0_1/` preserves the earlier
  three-tick engineering baseline as a regression fixture.
- Evaluation-only reference material is never read by construction, runtime,
  Agent, or compiler tests.

Real target-derived bundles and canary outputs remain generated evidence and
are not copied into the tracked fixture tree.

## Contract support code

Builders under `support/cases/` own schema, construction, communication,
repository, and trace/identity cases. Declarative cases in `case_specs/v1/`
use a closed operation and validator vocabulary. `schema_registry.py` resolves
the schema catalog offline, while the receipt and validator modules retain
separate serialization and semantic responsibilities.

Each contract condition is exposed as an independent pytest parameter with a
stable behavior-based ID. Historical suite grouping does not select behavior
or enter public receipts.

See [`docs/development-environment.md`](../../../docs/development-environment.md)
for the dependency profiles used by these suites.
