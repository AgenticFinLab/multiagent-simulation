"""Fail-closed publication of compact current Rule run releases."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Sequence

from h2epr.benchmark.package import EventPackage, load_event_package
from h2epr.canonical import write_json
from h2epr.conformance import (
    build_cross_event_contract_receipt,
    build_identity_invariance_receipt,
)
from h2epr._publication_core import (
    _PublicationCoreError,
    _derive_coordinate_results as _derive_coordinate_results,
    _derive_run_counts as _derive_run_counts,
    _require,
    _seal_inventory,
    _staged_release_root,
    _verify_rule_reproduction,
    _verify_run_custody,
    _write_text,
)
from h2epr.runtime.benchmark_runner import (
    OUTPUT_ROLES,
    build_determinism_receipt,
    build_run_manifest,
    h2epr_runtime_source_inventory,
    materialize_run,
)
from h2epr.runtime.environment import apply_delta


PublicationError = _PublicationCoreError


def _verify_custody(
    root: Path,
    package: EventPackage,
    *,
    expected_identity_variant: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    return _verify_run_custody(
        root,
        package,  # type: ignore[arg-type]
        expected_identity_variant=expected_identity_variant,
        runtime_source_inventory=h2epr_runtime_source_inventory,
        run_manifest_builder=build_run_manifest,
        delta_applier=apply_delta,
        output_roles=OUTPUT_ROLES,
    )


def _verify_reproduction(
    root: Path,
    package: EventPackage,
    data_root: Path,
    *,
    expected_identity_variant: str,
) -> None:
    _verify_rule_reproduction(
        root,
        package,  # type: ignore[arg-type]
        data_root,
        expected_identity_variant=expected_identity_variant,
        materializer=materialize_run,
        output_roles=OUTPUT_ROLES,
    )


def publish_rule_run_release(
    *,
    package_root: Path,
    data_root: Path,
    canonical_root: Path,
    repeat_root: Path,
    probe_root: Path,
    release_root: Path,
    event_title: str,
    simulation_reading_link: str,
) -> dict[str, Any]:
    """Independently verify three materializations and publish one release."""

    _require(not release_root.exists(), "release_root_must_be_absent")
    package = load_event_package(package_root, data_root, "rule")
    manifest, receipt = _verify_custody(
        canonical_root,
        package,
        expected_identity_variant="canonical",
    )
    _verify_reproduction(
        canonical_root,
        package,
        data_root,
        expected_identity_variant="canonical",
    )
    repeat_manifest, repeat_receipt = _verify_custody(
        repeat_root,
        package,
        expected_identity_variant="canonical",
    )
    _verify_reproduction(
        repeat_root,
        package,
        data_root,
        expected_identity_variant="canonical",
    )
    _verify_custody(
        probe_root,
        package,
        expected_identity_variant="generated-id-probe",
    )
    _verify_reproduction(
        probe_root,
        package,
        data_root,
        expected_identity_variant="generated-id-probe",
    )
    _require(
        manifest == repeat_manifest and receipt == repeat_receipt,
        "canonical_materializations_not_byte_equivalent",
    )
    identity = build_identity_invariance_receipt(canonical_root, probe_root)
    determinism = build_determinism_receipt(
        left_root=canonical_root,
        right_root=repeat_root,
        package=package,
        identity_conformance_receipt_sha256=identity["receipt_sha256"],
    )
    _require(determinism["all_byte_identical"], "determinism_not_closed")

    counts = receipt["counts"]
    reproduction_root = (
        receipt["custody"]["relative_locator"].rsplit("/", 1)[0]
        + "/reproduction"
    )
    readme = f"""# {event_title} Rule run release

This compact release records the dataset-conditioned Rule materialization of
`{manifest['event_id']}`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`{receipt['custody']['relative_locator']}`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `{receipt['run_id']}` |
| Package SHA-256 | `{receipt['package_sha256']}` |
| Rule binding SHA-256 | `{receipt['binding_sha256']}` |
| Run manifest SHA-256 | `{receipt['run_manifest_sha256']}` |
| Trace SHA-256 | `{receipt['trace_sha256']}` |
| Run seal SHA-256 | `{receipt['run_seal_sha256']}` |
| Final state SHA-256 | `{receipt['final_state_sha256']}` |
| Generated EPG seal | `{receipt['generated_epg_sha256']}` |

The run covers {counts['actors']} action-bearing representations over
{counts['ticks']} logical coordinates. Its sealed trace contains
{counts['trace_records']} records; the trace-derived graph contains
{counts['graph_nodes']} nodes and {counts['graph_edges']} edges. Terminal
transport custody contains no unresolved message.

## Independent verification

- the run manifest and current H2EPR/read-only MASim source inventories are
  recomputed rather than trusted from the producer;
- action, decision, disposition, delta, transport, seal, replay, count, and
  graph semantics are rederived from the trace;
- the Generated EPG is independently recompiled and compared byte for byte;
- two fresh seed-0 materializations are byte identical across every output and
  the run receipt; and
- a generated-identity probe changes opaque identities while preserving the
  semantic trace, exact terminal state, and graph semantics.

## Reproduce

Run from the repository root with an absent output directory.

```bash
PYTHONPATH=projects/h2epr/src python -B -m h2epr.cli materialize \\
  --data-root {data_root.as_posix()} \\
  --package {package_root.as_posix()} \\
  --backend rule --seed 0 --identity-variant canonical \\
  --custody-locator {reproduction_root} \\
  --output {reproduction_root}
```

The accompanying [simulation reading]({simulation_reading_link}) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
"""
    with _staged_release_root(release_root) as staged:
        shutil.copyfile(
            canonical_root / "run_manifest.json",
            staged / "run-manifest.json",
        )
        shutil.copyfile(
            canonical_root / "run_receipt.json",
            staged / "run-receipt.json",
        )
        write_json(staged / "determinism-receipt.json", determinism)
        write_json(staged / "generated-id-conformance.json", identity)
        _write_text(staged / "README.md", readme)
        _seal_inventory(staged)
    return {
        "event_id": manifest["event_id"],
        "run_id": receipt["run_id"],
        "release_root": release_root.as_posix(),
        "determinism_receipt_sha256": determinism["receipt_sha256"],
        "identity_receipt_sha256": identity["receipt_sha256"],
        "counts": counts,
    }


def publish_cross_event_release(
    *,
    cases: Sequence[tuple[Path, Path]],
    data_root: Path,
    release_root: Path,
    event_release_links: Sequence[str],
) -> dict[str, Any]:
    """Verify canonical custody and publish one cross-event receipt."""

    _require(not release_root.exists(), "release_root_must_be_absent")
    _require(
        len(cases) == len(event_release_links),
        "cross_event_release_link_count_mismatch",
    )
    loaded: list[tuple[EventPackage, Path]] = []
    rows = []
    for package_root, canonical_root in cases:
        package = load_event_package(package_root, data_root, "rule")
        manifest, receipt = _verify_custody(
            canonical_root,
            package,
            expected_identity_variant="canonical",
        )
        _verify_reproduction(
            canonical_root,
            package,
            data_root,
            expected_identity_variant="canonical",
        )
        loaded.append((package, canonical_root))
        rows.append(
            {
                "event_id": manifest["event_id"],
                "package_sha256": package.package_sha256,
                "run_id": receipt["run_id"],
                "trace_records": receipt["counts"]["trace_records"],
                "graph_nodes": receipt["counts"]["graph_nodes"],
                "graph_edges": receipt["counts"]["graph_edges"],
            }
        )
    receipt = build_cross_event_contract_receipt(
        loaded,  # type: ignore[arg-type]
        expected_package_schema="h2epr.event-package.manifest.v4",
        expected_output_roles=OUTPUT_ROLES,
    )
    table = "\n".join(
        f"| [{row['event_id']}]({link}) | `{row['package_sha256']}` | "
        f"`{row['run_id']}` | {row['trace_records']} | {row['graph_nodes']} | "
        f"{row['graph_edges']} |"
        for row, link in zip(rows, event_release_links, strict=True)
    )
    readme = f"""# Cross-event Rule conformance

This release verifies {len(rows)} distinct H2EPR event packages on one Rule
contract, one runtime source inventory, and one read-only MASim kernel
inventory.

| Event release | Package SHA-256 | Run | Trace | Nodes | Edges |
|---|---|---|---:|---:|---:|
{table}

`conformance-receipt.json` records distinct event identities, the shared
package and backend-status contracts, equal H2EPR and MASim inventories, equal
output roles, replay/trace/transport closure, and common claim exclusions. It
establishes cross-event engineering closure for these {len(rows)} practices,
not historical fit, held-out performance, calibration, causality, scientific
validity, or universal generality.
"""
    with _staged_release_root(release_root) as staged:
        write_json(staged / "conformance-receipt.json", receipt)
        _write_text(staged / "README.md", readme)
        _seal_inventory(staged)
    return {
        "receipt_sha256": receipt["receipt_sha256"],
        "release_root": release_root.as_posix(),
        "event_ids": [row["event_id"] for row in rows],
        "passed": receipt["passed"],
    }


__all__ = [
    "PublicationError",
    "publish_cross_event_release",
    "publish_rule_run_release",
]
