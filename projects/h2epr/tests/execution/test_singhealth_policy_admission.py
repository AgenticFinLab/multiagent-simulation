from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil

import pytest

from h2epr.scenarios.singhealth_data_breach.full_roster_v0_1 import (
    PolicyRealizationAdmissionError,
    PolicyRealizationErrorCode,
    build_singhealth_policy_realization_document,
    load_singhealth_policy_realization,
)
from h2epr.scenarios.singhealth_data_breach.full_roster_v0_1 import (
    admission as admission_module,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def project_copy(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("singhealth-policy-admission") / "h2epr"
    shutil.copytree(PROJECT_ROOT, root)
    return root


def _candidate(root: Path, *, status: str = "candidate") -> dict:
    return build_singhealth_policy_realization_document(
        project_root=root,
        status=status,
    )


def _write(root: Path, name: str, document: dict) -> tuple[Path, str]:
    directory = root / "execution/singhealth_data_breach/test-candidates"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.json"
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


def test_complete_candidate_is_closed_but_not_accepted(
    project_copy: Path,
) -> None:
    path, digest = _write(project_copy, "complete", _candidate(project_copy))

    admission = load_singhealth_policy_realization(
        path,
        project_root=project_copy,
        expected_source_sha256=digest,
    )

    assert admission.semantic_complete is True
    assert admission.implementation_complete is True
    assert admission.accepted is False
    assert admission.missing_implementation_ids == ()
    assert admission.coverage["actor_capability_bindings"] == 13
    with pytest.raises(TypeError):
        admission.document["status"] = "forged"


def test_accepted_status_rejects_a_missing_registered_implementation(
    project_copy: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    document = _candidate(
        project_copy,
        status="accepted_policy_realization",
    )
    missing_id = document["scenario_policy_realizations"][0][
        "implementation_id"
    ]
    available = dict(admission_module.implementation_versions())
    available.pop(missing_id)
    monkeypatch.setattr(
        admission_module,
        "implementation_versions",
        lambda: available,
    )
    path, digest = _write(project_copy, "missing-implementation", document)

    with pytest.raises(PolicyRealizationAdmissionError) as raised:
        load_singhealth_policy_realization(
            path,
            project_root=project_copy,
            expected_source_sha256=digest,
        )
    assert raised.value.code is PolicyRealizationErrorCode.IMPLEMENTATION_MISSING


def test_accepted_status_admits_the_closed_registry(project_copy: Path) -> None:
    document = _candidate(
        project_copy,
        status="accepted_policy_realization",
    )
    path, digest = _write(project_copy, "accepted", document)

    admission = load_singhealth_policy_realization(
        path,
        project_root=project_copy,
        expected_source_sha256=digest,
    )

    assert admission.accepted is True
    assert admission.implementation_complete is True
    assert len(document["participant_policy_realizations"]) == 13
    assert len(document["scenario_policy_realizations"]) == 9
    assert len(document["lifecycle_realizations"]) == 11


def test_missing_actor_placement_fails_exact_coverage(
    project_copy: Path,
) -> None:
    document = _candidate(project_copy)
    document["participant_policy_realizations"].pop()
    path, digest = _write(project_copy, "missing-placement", document)

    with pytest.raises(PolicyRealizationAdmissionError) as raised:
        load_singhealth_policy_realization(
            path,
            project_root=project_copy,
            expected_source_sha256=digest,
        )
    assert raised.value.code is (
        PolicyRealizationErrorCode.PLACEMENT_COVERAGE_MISMATCH
    )


def test_cross_capability_intent_reference_fails_closed(
    project_copy: Path,
) -> None:
    document = _candidate(project_copy)
    first, second = document["participant_policy_realizations"][:2]
    foreign_intent = second["decision_realizations"][0][
        "emittable_intent_ids"
    ][0]
    first["decision_realizations"][0]["emittable_intent_ids"] = [
        foreign_intent
    ]
    path, digest = _write(project_copy, "cross-capability-intent", document)

    with pytest.raises(PolicyRealizationAdmissionError) as raised:
        load_singhealth_policy_realization(
            path,
            project_root=project_copy,
            expected_source_sha256=digest,
        )
    assert raised.value.code is (
        PolicyRealizationErrorCode.SEMANTIC_REFERENCE_INVALID
    )


def test_policy_pointer_or_implementation_drift_is_rejected(
    project_copy: Path,
) -> None:
    document = _candidate(project_copy)
    document["scenario_policy_realizations"][0][
        "configuration_source_pointers"
    ] = ["/policy_selections/1"]
    path, digest = _write(project_copy, "wrong-policy-pointer", document)

    with pytest.raises(PolicyRealizationAdmissionError) as raised:
        load_singhealth_policy_realization(
            path,
            project_root=project_copy,
            expected_source_sha256=digest,
        )
    assert raised.value.code is PolicyRealizationErrorCode.POLICY_COVERAGE_MISMATCH

    document = _candidate(project_copy)
    document["lifecycle_realizations"][0]["state_ids"].pop()
    path, digest = _write(project_copy, "wrong-lifecycle", document)
    with pytest.raises(PolicyRealizationAdmissionError) as lifecycle_raised:
        load_singhealth_policy_realization(
            path,
            project_root=project_copy,
            expected_source_sha256=digest,
        )
    assert lifecycle_raised.value.code is (
        PolicyRealizationErrorCode.LIFECYCLE_COVERAGE_MISMATCH
    )


def test_parent_or_source_identity_drift_is_rejected(
    project_copy: Path,
) -> None:
    document = _candidate(project_copy)
    document["semantic_parent"]["configuration_canonical_sha256"] = "0" * 64
    path, digest = _write(project_copy, "wrong-parent", document)

    with pytest.raises(PolicyRealizationAdmissionError) as raised:
        load_singhealth_policy_realization(
            path,
            project_root=project_copy,
            expected_source_sha256=digest,
        )
    assert raised.value.code is PolicyRealizationErrorCode.PARENT_MISMATCH

    with pytest.raises(PolicyRealizationAdmissionError) as source_raised:
        load_singhealth_policy_realization(
            path,
            project_root=project_copy,
            expected_source_sha256="f" * 64,
        )
    assert source_raised.value.code is (
        PolicyRealizationErrorCode.INTEGRITY_MISMATCH
    )


def test_schema_and_returned_objects_are_fail_closed_and_detached(
    project_copy: Path,
) -> None:
    document = _candidate(project_copy)
    document["undeclared_extension"] = True
    path, digest = _write(project_copy, "schema-extension", document)
    with pytest.raises(PolicyRealizationAdmissionError) as raised:
        load_singhealth_policy_realization(
            path,
            project_root=project_copy,
            expected_source_sha256=digest,
        )
    assert raised.value.code is (
        PolicyRealizationErrorCode.SCHEMA_VALIDATION_FAILED
    )

    first = _candidate(project_copy)
    second = copy.deepcopy(first)
    second["version"] = "0.1.1"
    assert first["version"] == "0.1.0"
