"""Fail-closed admission for H2EPR experiment matrices."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Mapping

import jsonschema

from h2epr.benchmark.package import EventPackageError, load_event_package
from h2epr.canonical import canonical_sha256, file_sha256


class _ExperimentAdmissionCoreError(ValueError):
    """An experiment plan is unsafe, incomparable, or not executable."""


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_ROOT = PROJECT_ROOT / "schemas"
REQUIRED_CLAIM_EXCLUSIONS = {
    "held-out evaluation",
    "historical fit",
    "parameter calibration",
    "causal validity",
    "scientific validity",
    "universal generality",
}


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise _ExperimentAdmissionCoreError(code)


def _read_json(path: Path, label: str) -> dict[str, Any]:
    _require(path.is_file() and not path.is_symlink(), f"{label}_missing_or_unsafe")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _ExperimentAdmissionCoreError(f"{label}_unreadable") from exc
    _require(isinstance(value, dict), f"{label}_object_required")
    return value


def _validate(value: Mapping[str, Any], schema_name: str, label: str) -> None:
    schema = _read_json(SCHEMA_ROOT / schema_name, f"schema:{schema_name}")
    try:
        jsonschema.Draft202012Validator(schema).validate(value)
    except jsonschema.ValidationError as exc:
        raise _ExperimentAdmissionCoreError(
            f"{label}_schema_invalid:{exc.json_path}"
        ) from exc


def _safe_path(root: Path, relative_path: Any, label: str, *, directory: bool) -> Path:
    _require(
        isinstance(relative_path, str) and bool(relative_path),
        f"{label}_path_invalid",
    )
    relative = Path(relative_path)
    _require(
        not relative.is_absolute() and ".." not in relative.parts,
        f"{label}_path_unsafe",
    )
    path = root / relative
    predicate = path.is_dir if directory else path.is_file
    _require(predicate() and not path.is_symlink(), f"{label}_missing_or_unsafe")
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise _ExperimentAdmissionCoreError(f"{label}_escapes_project") from exc
    return path


def _safe_custody_locator(value: str, row_id: str) -> str:
    relative = Path(value)
    _require(
        not relative.is_absolute()
        and ".." not in relative.parts
        and len(relative.parts) > 3
        and relative.parts[:3]
        == (".local-runtime", "h2epr-simulation", "experiments"),
        f"experiment_custody_path_unsafe:{row_id}",
    )
    return relative.as_posix()


def _model_control_signature(
    model: Mapping[str, Any],
    *,
    prompt_contract: Mapping[str, str] | None = None,
    response_contract: Mapping[str, str] | None = None,
) -> str:
    """Identify every model-side control that can change a comparison row."""

    prompt = prompt_contract or model["prompt_contract"]
    response = response_contract or model["response_contract"]
    parameters = sorted(
        (
            {
                "name": item["name"],
                "value": item["value"],
                "basis": item["basis"],
            }
            for item in model["decoding_parameters"]
        ),
        key=lambda item: item["name"],
    )
    return canonical_sha256(
        {
            "provider": model["provider"],
            "model_id": model["model_id"],
            "model_version": model["model_version"],
            "service_mode": model["service_mode"],
            "prompt_contract": dict(prompt),
            "response_contract": dict(response),
            "decoding_parameters": parameters,
            "max_attempts": model["max_attempts"],
        }
    )


def _file_reference(
    project_root: Path,
    row: Mapping[str, Any],
    label: str,
) -> dict[str, str]:
    path = _safe_path(
        project_root,
        row["relative_path"],
        label,
        directory=False,
    )
    _require(file_sha256(path) == row["sha256"], f"{label}_hash_mismatch")
    return {
        "relative_path": row["relative_path"],
        "sha256": row["sha256"],
    }


def _check(check_id: str, evidence: Any) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "passed": True,
        "evidence_sha256": canonical_sha256(
            {"check_id": check_id, "evidence": evidence}
        ),
    }


def _admit_experiment_plan(
    *,
    project_root: Path,
    data_root: Path,
    plan: Mapping[str, Any],
    _package_loader: Callable[..., Any] | None = None,
    _package_error: type[Exception] = EventPackageError,
) -> dict[str, Any]:
    """Validate one immutable plan without launching or mutating a run."""

    project_root = project_root.resolve()
    data_root = data_root.resolve()
    package_loader = _package_loader or load_event_package
    _validate(plan, "experiment-plan.schema.json", "experiment_plan")
    _require(
        plan["plan_sha256"]
        == canonical_sha256(
            {key: value for key, value in plan.items() if key != "plan_sha256"}
        ),
        "experiment_plan_self_hash_mismatch",
    )

    row_ids: set[str] = set()
    custody_roots: set[str] = set()
    loaded_rows: dict[str, dict[str, Any]] = {}
    package_evidence: list[dict[str, Any]] = []
    model_evidence: list[dict[str, Any]] = []
    for row in plan["rows"]:
        row_id = row["row_id"]
        _require(row_id not in row_ids, f"experiment_row_id_duplicate:{row_id}")
        row_ids.add(row_id)
        custody_root = _safe_custody_locator(row["custody_root"], row_id)
        _require(
            custody_root not in custody_roots,
            f"experiment_custody_duplicate:{row_id}",
        )
        custody_roots.add(custody_root)

        package_root = _safe_path(
            project_root,
            row["package_relative_path"],
            f"experiment_package:{row_id}",
            directory=True,
        )
        try:
            package = package_loader(
                package_root,
                data_root,
                row["backend"],
            )
        except _package_error as exc:
            raise _ExperimentAdmissionCoreError(
                f"experiment_backend_unavailable:{row_id}:{exc}"
            ) from exc
        _require(
            package.manifest["event_id"] == row["event_id"],
            f"experiment_event_identity_mismatch:{row_id}",
        )
        _require(
            package.package_sha256 == row["package_sha256"],
            f"experiment_package_identity_mismatch:{row_id}",
        )
        _require(
            package.binding_sha256 == row["binding_sha256"],
            f"experiment_binding_identity_mismatch:{row_id}",
        )

        model = row.get("model_provenance")
        if model is not None:
            prompt = _file_reference(
                project_root,
                model["prompt_contract"],
                f"experiment_prompt_contract:{row_id}",
            )
            response = _file_reference(
                project_root,
                model["response_contract"],
                f"experiment_response_contract:{row_id}",
            )
            parameter_names = [
                item["name"] for item in model["decoding_parameters"]
            ]
            _require(
                len(parameter_names) == len(set(parameter_names)),
                f"experiment_decoding_parameter_duplicate:{row_id}",
            )
            decoding_parameters = sorted(
                (
                    {
                        "name": item["name"],
                        "value": item["value"],
                        "basis": item["basis"],
                    }
                    for item in model["decoding_parameters"]
                ),
                key=lambda item: item["name"],
            )
            model_signature = _model_control_signature(
                model,
                prompt_contract=prompt,
                response_contract=response,
            )
            model_evidence.append(
                {
                    "row_id": row_id,
                    "provider": model["provider"],
                    "model_id": model["model_id"],
                    "model_version": model["model_version"],
                    "service_mode": model["service_mode"],
                    "prompt_contract": prompt,
                    "response_contract": response,
                    "decoding_parameters": decoding_parameters,
                    "max_attempts": model["max_attempts"],
                    "model_control_signature": model_signature,
                }
            )
        else:
            model_signature = None
        loaded_rows[row_id] = {
            "event_id": row["event_id"],
            "backend": row["backend"],
            "package_sha256": row["package_sha256"],
            "binding_sha256": row["binding_sha256"],
            "seeds": tuple(row["seeds"]),
            "model_control_signature": model_signature,
        }
        package_evidence.append(
            {
                "row_id": row_id,
                "event_id": row["event_id"],
                "backend": row["backend"],
                "package_sha256": package.package_sha256,
                "binding_sha256": package.binding_sha256,
            }
        )

    group_ids: set[str] = set()
    comparison_evidence: list[dict[str, Any]] = []
    for group in plan["comparison_groups"]:
        group_id = group["group_id"]
        _require(
            group_id not in group_ids,
            f"experiment_comparison_group_duplicate:{group_id}",
        )
        group_ids.add(group_id)
        _require(
            set(group["row_ids"]) <= set(loaded_rows),
            f"experiment_comparison_row_unknown:{group_id}",
        )
        rows = [loaded_rows[row_id] for row_id in group["row_ids"]]
        seed_sets = {row["seeds"] for row in rows}
        _require(
            len(seed_sets) == 1,
            f"experiment_comparison_seed_mismatch:{group_id}",
        )
        if group["comparison_kind"] == "within_event_backend":
            _require(
                len({row["event_id"] for row in rows}) == 1
                and len({row["package_sha256"] for row in rows}) == 1,
                f"experiment_within_event_package_mismatch:{group_id}",
            )
            _require(
                len({row["backend"] for row in rows}) == len(rows),
                f"experiment_within_event_backend_duplicate:{group_id}",
            )
            model_rows = [
                row for row in rows if row["model_control_signature"] is not None
            ]
            if len(model_rows) > 1:
                _require(
                    len(
                        {
                            row["model_control_signature"]
                            for row in model_rows
                        }
                    )
                    == 1,
                    f"experiment_model_control_mismatch:{group_id}",
                )
        else:
            _require(
                len({row["event_id"] for row in rows}) == len(rows),
                f"experiment_cross_event_identity_duplicate:{group_id}",
            )
            _require(
                len({row["backend"] for row in rows}) == 1,
                f"experiment_cross_event_backend_mismatch:{group_id}",
            )
            if rows[0]["backend"] in {"llm", "rulellm"}:
                _require(
                    len(
                        {
                            row["model_control_signature"]
                            for row in rows
                        }
                    )
                    == 1,
                    f"experiment_model_control_mismatch:{group_id}",
                )
        comparison_evidence.append(
            {
                "group_id": group_id,
                "comparison_kind": group["comparison_kind"],
                "row_ids": group["row_ids"],
                "model_control_signatures": sorted(
                    {
                        row["model_control_signature"]
                        for row in rows
                        if row["model_control_signature"] is not None
                    }
                ),
            }
        )

    schedule = plan["scheduling"]
    _require(
        schedule["progress_poll_seconds"] < schedule["stall_timeout_seconds"]
        <= schedule["wall_timeout_seconds"],
        "experiment_timeout_order_invalid",
    )
    failure_policy = plan["failure_policy"]
    _require(
        (failure_policy["retry_limit"] == 0)
        == (failure_policy["retryable_classes"] == []),
        "experiment_retry_policy_incoherent",
    )

    analysis_ids: set[str] = set()
    analysis_evidence: list[dict[str, Any]] = []
    analysis_scopes: set[str] = set()
    for analysis in plan["analysis_contracts"]:
        analysis_id = analysis["analysis_id"]
        _require(
            analysis_id not in analysis_ids,
            f"experiment_analysis_id_duplicate:{analysis_id}",
        )
        analysis_ids.add(analysis_id)
        analysis_scopes.add(analysis["scope"])
        analysis_evidence.append(
            {
                "analysis_id": analysis_id,
                "scope": analysis["scope"],
                "definition": _file_reference(
                    project_root,
                    analysis["definition"],
                    f"experiment_analysis_contract:{analysis_id}",
                ),
            }
        )
    _require(
        "simulation_only" in analysis_scopes,
        "experiment_simulation_only_analysis_missing",
    )
    _require(
        {group["comparison_kind"] for group in plan["comparison_groups"]}
        <= analysis_scopes,
        "experiment_comparison_analysis_missing",
    )
    _require(
        REQUIRED_CLAIM_EXCLUSIONS
        <= set(plan["claim_boundary"]["does_not_support"]),
        "experiment_claim_boundary_incomplete",
    )

    backend_counts = Counter()
    for row in plan["rows"]:
        backend_counts[row["backend"]] += len(row["seeds"])
    normalized_backend_counts = {
        backend: backend_counts[backend]
        for backend in ("rule", "llm", "rulellm")
    }
    checks = [
        _check("plan_schema_and_identity", plan["plan_sha256"]),
        _check("package_and_binding_identity", package_evidence),
        _check(
            "row_and_custody_uniqueness",
            {"row_ids": sorted(row_ids), "custody_roots": sorted(custody_roots)},
        ),
        _check("model_provenance", model_evidence),
        _check("comparison_parity", comparison_evidence),
        _check(
            "schedule_and_failure_policy",
            {"scheduling": schedule, "failure_policy": failure_policy},
        ),
        _check("analysis_contract_identity", analysis_evidence),
        _check("claim_boundary", plan["claim_boundary"]),
    ]
    receipt = {
        "schema_version": "h2epr.experiment-admission-receipt.v3",
        "receipt_id": f"{plan['plan_id']}.admission",
        "plan_id": plan["plan_id"],
        "plan_sha256": plan["plan_sha256"],
        "row_count": len(plan["rows"]),
        "run_count": sum(normalized_backend_counts.values()),
        "backend_counts": normalized_backend_counts,
        "checks": checks,
        "admitted": True,
        "receipt_sha256": "0" * 64,
    }
    receipt["receipt_sha256"] = canonical_sha256(
        {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    )
    _validate(
        receipt,
        "experiment-admission-receipt.schema.json",
        "experiment_admission_receipt",
    )
    return receipt


def _load_and_admit_experiment_plan(
    *,
    project_root: Path,
    data_root: Path,
    plan_path: Path,
    _package_loader: Callable[..., Any] | None = None,
    _package_error: type[Exception] = EventPackageError,
) -> dict[str, Any]:
    """Read and admit one plan; no run is launched by this operation."""

    return _admit_experiment_plan(
        project_root=project_root,
        data_root=data_root,
        plan=_read_json(plan_path, "experiment_plan"),
        _package_loader=_package_loader,
        _package_error=_package_error,
    )


__all__ = [
    "_ExperimentAdmissionCoreError",
    "_admit_experiment_plan",
    "_load_and_admit_experiment_plan",
    "_model_control_signature",
]
