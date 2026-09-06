"""Current package runner with registered backends and ID-neutral inputs."""

from __future__ import annotations

import asyncio
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from h2epr.backends.registry import build_backend
from h2epr.benchmark.package import EventPackage, load_event_package
from h2epr.canonical import canonical_sha256, file_sha256, write_json, write_jsonl
from h2epr.masim_kernel import (
    AppendOnlyTransport,
    AuthoritativeReducer,
    TraceWriter,
    validate_trace,
    source_inventory as masim_source_inventory,
)

from ._runner_core import (
    _NAMED_BARRIERS,
    _OUTPUT_ROLES,
    _BenchmarkEngineBase,
    _BenchmarkRunArtifacts,
    _BenchmarkRunCoreError,
    _AnnotationDetector,
    _validate,
    _build_determinism_receipt,
)
from .environment import build_environment


PROJECT_ROOT = Path(__file__).resolve().parents[3]
NAMED_BARRIERS = _NAMED_BARRIERS
OUTPUT_ROLES = _OUTPUT_ROLES
BenchmarkRunArtifacts = _BenchmarkRunArtifacts
BenchmarkRunError = _BenchmarkRunCoreError


def h2epr_runtime_source_inventory() -> list[dict[str, str]]:
    relative_paths = (
        "src/h2epr/canonical.py",
        "src/h2epr/masim_kernel.py",
        "src/h2epr/semantic/_assets_core.py",
        "src/h2epr/semantic/assets.py",
        "src/h2epr/benchmark/_compiler_core.py",
        "src/h2epr/benchmark/compiler.py",
        "src/h2epr/backends/interface.py",
        "src/h2epr/backends/_rule_core.py",
        "src/h2epr/backends/rule.py",
        "src/h2epr/backends/registry.py",
        "src/h2epr/benchmark/package.py",
        "src/h2epr/runtime/_environment_core.py",
        "src/h2epr/runtime/environment.py",
        "src/h2epr/runtime/information.py",
        "src/h2epr/runtime/generated_epg.py",
        "src/h2epr/runtime/_runner_core.py",
        "src/h2epr/runtime/benchmark_runner.py",
    )
    return [
        {
            "relative_path": relative_path,
            "sha256": file_sha256(PROJECT_ROOT / relative_path),
        }
        for relative_path in relative_paths
    ]


def build_run_manifest(
    package: EventPackage,
    *,
    backend: str,
    run_seed: int,
    identity_variant: str = "canonical",
) -> dict[str, Any]:
    if backend != package.binding["backend"]:
        raise BenchmarkRunError("run_backend_binding_mismatch")
    h2epr_sources = h2epr_runtime_source_inventory()
    masim_sources = masim_source_inventory()
    settings = {
        "seed": run_seed,
        "tick_count": len(package.scenario["timeline"]),
        "timeline_sha256": canonical_sha256(package.scenario["timeline"]),
        "source_exposure": package.manifest["source_exposure"],
        "protocol_eligibility": package.manifest["protocol_eligibility"],
        "model_access": package.binding["model_access"],
        "network_access": package.binding["network_access"],
        "historical_calibration": False,
        "identity_variant": identity_variant,
    }
    identity = {
        "event_id": package.manifest["event_id"],
        "package_sha256": package.package_sha256,
        "binding_sha256": package.binding_sha256,
        "h2epr_runtime_sha256": canonical_sha256(h2epr_sources),
        "masim_kernel_sha256": canonical_sha256(masim_sources),
        "backend": backend,
        "run_settings": settings,
    }
    run_id = "run." + hashlib.sha256(
        canonical_sha256(identity).encode("ascii")
    ).hexdigest()[:24]
    manifest = {
        "schema_version": "h2epr.run-manifest.v3",
        "run_id": run_id,
        "event_id": package.manifest["event_id"],
        "package_id": package.manifest["package_id"],
        "package_sha256": package.package_sha256,
        "manifest_sha256": package.manifest["manifest_sha256"],
        "binding_id": package.binding["binding_id"],
        "binding_sha256": package.binding_sha256,
        "realization_id": package.realization["realization_id"],
        "realization_sha256": package.realization["realization_sha256"],
        "shared_configuration_id": package.shared_configuration[
            "configuration_id"
        ],
        "shared_configuration_sha256": package.shared_configuration[
            "configuration_sha256"
        ],
        "backend_configuration_id": package.backend_configuration[
            "configuration_id"
        ],
        "backend_configuration_sha256": package.backend_configuration[
            "configuration_sha256"
        ],
        "backend": backend,
        "run_settings": settings,
        "h2epr_runtime_sources": h2epr_sources,
        "masim_kernel_sources": masim_sources,
        "run_manifest_sha256": "0" * 64,
    }
    manifest["run_manifest_sha256"] = canonical_sha256(
        {
            key: item
            for key, item in manifest.items()
            if key != "run_manifest_sha256"
        }
    )
    _validate(manifest, "run-manifest.schema.json", "run_manifest")
    return manifest


def _decision_message_projection(message: Mapping[str, Any]) -> dict[str, Any]:
    """Remove opaque transport identities before participant decision production."""

    excluded = {
        "message_id",
        "message_intent_id",
        "intent_content_sha256",
    }
    return {
        key: copy.deepcopy(value)
        for key, value in message.items()
        if key not in excluded
    }


class BenchmarkEngine(_BenchmarkEngineBase):
    def __init__(
        self,
        package: EventPackage,
        *,
        backend_name: str,
        run_seed: int,
        identity_variant: str = "canonical",
    ) -> None:
        self.package = package
        self.backend_name = backend_name
        self.run_seed = run_seed
        self.manifest = build_run_manifest(
            package,
            backend=backend_name,
            run_seed=run_seed,
            identity_variant=identity_variant,
        )
        self.actor_ids = tuple(package.scenario["active_actor_ids"])
        self.timeline = tuple(copy.deepcopy(package.scenario["timeline"]))
        self.backend = build_backend(
            package,
            backend_name=backend_name,
            run_id=self.manifest["run_id"],
            run_seed=run_seed,
        )
        environment = build_environment(package.scenario)
        self.environment = environment
        self.reducer = AuthoritativeReducer(
            package.scenario["initial_state"],
            environment.apply_batch,
        )
        self.transport = AppendOnlyTransport(
            package.scenario["communication_routes"]
        )
        self.trace = TraceWriter(
            self.manifest["run_id"],
            self.manifest["run_manifest_sha256"],
        )
        self.detector = _AnnotationDetector(package.scenario)
        self.coordinate_results: dict[int, dict[str, Any]] = {}
        self._seen_stage_ids: set[str] = set()
        self.participant_memory: dict[str, dict[str, list[dict[str, Any]]]] = {
            actor_id: {"received_messages": [], "own_actions": []}
            for actor_id in self.actor_ids
        }

    def _pending_lifecycles(self, actor_id: str) -> list[dict[str, Any]]:
        latest: dict[str, Any] = {}
        for row in self.transport.history:
            if row.status != "duplicate":
                latest[row.message_intent_id] = row
        values = [
            {
                "lifecycle_id": "message_delivery",
                "status": row.status,
                "counterparty_id": (
                    row.recipient_id
                    if row.sender_id == actor_id
                    else row.sender_id
                ),
            }
            for row in latest.values()
            if row.status
            not in {"delivered", "expired", "rejected", "duplicate", "failed"}
            and actor_id == row.sender_id
        ]
        return sorted(values, key=canonical_sha256)

    def _observation_bundle(
        self,
        *,
        actor_id: str,
        coordinate: Mapping[str, Any],
        state: Mapping[str, Any],
        prestate_sha256: str,
        delivered_messages: tuple[Mapping[str, Any], ...],
    ) -> dict[str, Any]:
        projected = tuple(
            sorted(
                (
                    _decision_message_projection(message)
                    for message in delivered_messages
                ),
                key=canonical_sha256,
            )
        )
        bundle = super()._observation_bundle(
            actor_id=actor_id,
            coordinate=coordinate,
            state=state,
            prestate_sha256=prestate_sha256,
            delivered_messages=projected,
        )
        bundle["contract"]["memory"]["received_messages"].extend(copy.deepcopy(projected))
        return bundle

    async def run_coordinate(
        self, coordinate: Mapping[str, Any], barriers: tuple[str, ...] = NAMED_BARRIERS,
    ) -> dict[str, Any]:
        result = await super().run_coordinate(coordinate, barriers)
        rows = [row for row in self.trace.records
                if row["logical_tick"] == coordinate["logical_tick"]]
        actions = {row["payload"]["intent_id"]: row["payload"] for row in rows
                   if row["record_type"] == "action_intent"}
        for row in rows:
            if row["record_type"] == "observation":
                contract = row["payload"]["contract"]
                self.participant_memory[contract["actor_id"]]["received_messages"] = (
                    copy.deepcopy(contract["memory"]["received_messages"])
                )
        for row in rows:
            if row["record_type"] != "action_disposition":
                continue
            disposition = row["payload"]
            action = actions[disposition["intent_id"]]
            self.participant_memory[action["actor_id"]]["own_actions"].append({
                "logical_tick": coordinate["logical_tick"],
                "action_type": action["action_type"],
                "parameters": copy.deepcopy(action["parameters"]),
                "status": disposition["status"],
                "reason_code": disposition["reason_code"],
                "lifecycle_state": disposition["lifecycle_state"],
            })
        return result


async def _run(
    engine: BenchmarkEngine,
    checkpoint: Callable[[], None],
) -> BenchmarkRunArtifacts:
    try:
        await engine.setup()
        for coordinate in engine.timeline:
            await engine.run_coordinate(coordinate)
            checkpoint()
    except BaseException as error:
        try:
            await engine.shutdown()
        except BaseException as cleanup_error:
            error.add_note(f"backend shutdown also failed: {type(cleanup_error).__name__}")
        raise
    else:
        await engine.shutdown()
    return engine.finalize()


def _write_prefix(output_root: Path, engine: BenchmarkEngine) -> None:
    """Checkpoint observed evidence, without issuing a complete-run receipt."""
    write_jsonl(output_root / "simulation_trace.jsonl", engine.trace.records)
    write_json(output_root / "partial_state.json", engine.reducer.state)
    write_json(output_root / "coordinate_results.json", [
        engine.coordinate_results[tick] for tick in sorted(engine.coordinate_results)
    ])
    write_json(output_root / "tick_seals.json", [
        row["payload"] for row in engine.trace.records if row["record_type"] == "tick_seal"
    ])


def _write_failure(output_root: Path, engine: BenchmarkEngine, error: BaseException) -> None:
    _write_prefix(output_root, engine)
    unresolved, recipients = engine.transport.unresolved()
    failure = {
        "schema_version": "h2epr.failed-attempt.v1",
        "status": "failed",
        "run_id": engine.manifest["run_id"],
        "run_manifest_sha256": engine.manifest["run_manifest_sha256"],
        "exception_type": type(error).__name__,
        "failure_code": str(error),
        "sealed_logical_ticks": sorted(engine.coordinate_results),
        "trace_record_count": len(engine.trace.records),
        "trace_errors": validate_trace(engine.trace.records),
        "unresolved_message_intent_ids": list(unresolved),
        "unresolved_recipient_ids": list(recipients),
        "complete_run_release_eligible": False,
        "output_files": [{
            "relative_path": name, "sha256": file_sha256(output_root / name),
            "size_bytes": (output_root / name).stat().st_size,
        } for name in ("run_manifest.json", "simulation_trace.jsonl", "partial_state.json",
                       "coordinate_results.json", "tick_seals.json")],
    }
    failure["receipt_sha256"] = canonical_sha256(failure)
    _validate(failure, "failed-attempt.schema.json", "failed_attempt")
    write_json(output_root / "failure-receipt.json", failure)


def materialize_run(
    *,
    package_root: Path,
    data_root: Path,
    output_root: Path,
    backend: str = "rule",
    run_seed: int = 0,
    identity_variant: str = "canonical",
    custody_locator: str | None = None,
) -> dict[str, Any]:
    if output_root.exists():
        raise FileExistsError("run_output_root_must_be_absent")
    package = load_event_package(package_root, data_root, backend)
    engine = BenchmarkEngine(
        package, backend_name=backend, run_seed=run_seed,
        identity_variant=identity_variant,
    )
    output_root.mkdir(parents=True)
    write_json(output_root / "run_manifest.json", engine.manifest)
    try:
        artifacts = asyncio.run(_run(engine, lambda: _write_prefix(output_root, engine)))
        return _write_complete(output_root, artifacts, custody_locator)
    except BaseException as error:
        try:
            _write_failure(output_root, engine, error)
        except Exception as custody_error:
            error.add_note(f"failure custody write failed: {custody_error}")
        raise


def _write_complete(
    output_root: Path, artifacts: BenchmarkRunArtifacts, custody_locator: str | None,
) -> dict[str, Any]:
    write_json(output_root / "coordinate_results.json", artifacts.coordinate_results)
    write_json(output_root / "final_state.json", artifacts.final_state)
    write_json(output_root / "generated_epg.json", artifacts.generated_epg)
    write_json(output_root / "replay_receipt.json", artifacts.replay_receipt)
    write_json(output_root / "run_manifest.json", artifacts.run_manifest)
    write_json(output_root / "run_seal.json", artifacts.run_seal)
    write_jsonl(output_root / "simulation_trace.jsonl", artifacts.simulation_trace)
    write_json(output_root / "tick_seals.json", artifacts.tick_seals)
    output_files = [
        {
            "relative_path": filename,
            "sha256": file_sha256(output_root / filename),
            "size_bytes": (output_root / filename).stat().st_size,
        }
        for filename in OUTPUT_ROLES
    ]
    receipt = copy.deepcopy(artifacts.run_receipt)
    receipt["output_files"] = output_files
    receipt["custody"] = {
        "relative_locator": custody_locator
        or f".local-runtime/h2epr-simulation/runs/unpublished/{receipt['run_id']}",
        "inventory_sha256": canonical_sha256(output_files),
    }
    receipt["receipt_sha256"] = canonical_sha256(
        {
            key: item
            for key, item in receipt.items()
            if key != "receipt_sha256"
        }
    )
    _validate(receipt, "run-receipt.schema.json", "run_receipt")
    # This checkpoint belongs to the just-completed attempt. The exact final
    # state and its sealed trace now replace it; failed attempts keep theirs.
    (output_root / "partial_state.json").unlink()
    write_json(output_root / "run_receipt.json", receipt)
    return receipt


def build_determinism_receipt(
    *,
    left_root: Path,
    right_root: Path,
    package: EventPackage,
    identity_conformance_receipt_sha256: str,
) -> dict[str, Any]:
    return _build_determinism_receipt(
        left_root=left_root,
        right_root=right_root,
        package=package,  # type: ignore[arg-type]
        identity_conformance_receipt_sha256=(
            identity_conformance_receipt_sha256
        ),
    )


__all__ = [
    "BenchmarkEngine",
    "BenchmarkRunArtifacts",
    "BenchmarkRunError",
    "NAMED_BARRIERS",
    "OUTPUT_ROLES",
    "build_determinism_receipt",
    "build_run_manifest",
    "h2epr_runtime_source_inventory",
    "materialize_run",
]
