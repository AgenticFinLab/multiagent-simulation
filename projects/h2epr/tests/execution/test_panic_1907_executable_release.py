from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import pytest

from masim.integrations.event_process import canonical_sha256

from h2epr.scenarios.panic_1907.full_roster_v0_1 import (
    ExecutableAdmissionCode,
    ExecutableAdmissionError,
    build_panic_executable_package_document,
    build_panic_runtime_bundle_document,
    load_panic_executable_package,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RELEASE_ROOT = PROJECT_ROOT / "execution/panic_1907/full-roster-rule-v0.1"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: dict) -> str:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return _sha256(path)


@pytest.fixture(scope="module")
def project_copy(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("panic-executable-admission") / "h2epr"
    shutil.copytree(PROJECT_ROOT, root)
    return root


def test_panic_executable_release_is_strictly_admitted() -> None:
    manifest = json.loads(
        (RELEASE_ROOT / "manifest.json").read_text(encoding="utf-8")
    )
    package = manifest["package"]

    admission = load_panic_executable_package(
        RELEASE_ROOT / package["path"],
        project_root=PROJECT_ROOT,
        expected_source_sha256=package["source_sha256"],
    )

    assert admission.accepted is True
    assert admission.execution_eligible is True
    assert admission.deterministic_materialization is True
    assert admission.component_complete is True
    assert admission.package_canonical_sha256 == package["canonical_sha256"]
    assert admission.schema_sha256 == package["schema_sha256"]
    assert admission.runtime_bundle_source_sha256 == manifest[
        "runtime_bundle"
    ]["source_sha256"]
    assert dict(admission.coverage) == {
        "actor_instances": 16,
        "actor_carriers": 16,
        "actor_capability_bindings": 17,
        "action_bindings": 127,
        "decision_observation_rules": 88,
        "communication_routes": 35,
        "lifecycle_families": 13,
        "runtime_components": 9,
    }
    with pytest.raises(TypeError):
        admission.runtime_bundle_document["status"] = "forged"


def test_release_is_reproducible_from_static_objects() -> None:
    released_bundle = json.loads(
        (RELEASE_ROOT / "runtime-bundle.json").read_text(encoding="utf-8")
    )
    built_bundle = build_panic_runtime_bundle_document(project_root=PROJECT_ROOT)
    assert canonical_sha256(released_bundle) == canonical_sha256(built_bundle)

    source_sha = _sha256(RELEASE_ROOT / "runtime-bundle.json")
    built_package = build_panic_executable_package_document(
        project_root=PROJECT_ROOT,
        runtime_bundle_source_sha256=source_sha,
        runtime_bundle_canonical_sha256=canonical_sha256(built_bundle),
    )
    released_package = json.loads(
        (RELEASE_ROOT / "executable-package.json").read_text(encoding="utf-8")
    )
    assert released_package == built_package


def test_release_manifest_sources_artifacts_and_checksums_close() -> None:
    manifest = json.loads(
        (RELEASE_ROOT / "manifest.json").read_text(encoding="utf-8")
    )
    for source in manifest["implementation_sources"]:
        assert _sha256(PROJECT_ROOT / source["path"]) == source["sha256"]
    for schema in manifest["schemas"]:
        assert _sha256(PROJECT_ROOT / schema["path"]) == schema["sha256"]
    for artifact in manifest["artifacts"]:
        assert _sha256(RELEASE_ROOT / artifact["path"]) == artifact["sha256"]

    rows = {
        name: digest
        for digest, name in (
            line.split("  ", 1)
            for line in (RELEASE_ROOT / "SHA256SUMS")
            .read_text(encoding="utf-8")
            .splitlines()
        )
    }
    assert set(rows) == {
        "manifest.json",
        "README.md",
        "executable-package.json",
        "runtime-bundle.json",
        "substantive-review.md",
    }
    for name, digest in rows.items():
        assert _sha256(RELEASE_ROOT / name) == digest


def test_bundle_content_drift_fails_even_when_reference_hashes_are_updated(
    project_copy: Path,
) -> None:
    release = project_copy / "execution/panic_1907/full-roster-rule-v0.1"
    bundle_path = release / "runtime-bundle.json"
    package_path = release / "executable-package.json"
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    rule = bundle["observation_rules"][0]
    observation_id = rule["observation_ids"][0]
    rule["observation_values"][observation_id] = "forged_value"
    source_sha = _write_json(bundle_path, bundle)
    package = json.loads(package_path.read_text(encoding="utf-8"))
    package["runtime_bundle"]["source_sha256"] = source_sha
    package["runtime_bundle"]["canonical_sha256"] = canonical_sha256(bundle)
    _write_json(package_path, package)

    with pytest.raises(ExecutableAdmissionError) as raised:
        load_panic_executable_package(
            package_path,
            project_root=project_copy,
        )
    assert raised.value.code is (
        ExecutableAdmissionCode.BUNDLE_MATERIALIZATION_MISMATCH
    )


def test_duplicate_json_and_expected_source_drift_fail_closed(
    project_copy: Path,
) -> None:
    release = project_copy / "execution/panic_1907/full-roster-rule-v0.1"
    source = release / "executable-package.json"
    duplicate = release / "duplicate-package.json"
    duplicate.write_text(
        source.read_text(encoding="utf-8").replace(
            "{\n",
            '{\n  "format_identity": "duplicate",\n',
            1,
        ),
        encoding="utf-8",
    )
    with pytest.raises(ExecutableAdmissionError) as duplicate_raised:
        load_panic_executable_package(
            duplicate,
            project_root=project_copy,
        )
    assert duplicate_raised.value.code is ExecutableAdmissionCode.JSON_DUPLICATE_KEY

    with pytest.raises(ExecutableAdmissionError) as integrity_raised:
        load_panic_executable_package(
            source,
            project_root=project_copy,
            expected_source_sha256="f" * 64,
        )
    assert integrity_raised.value.code is ExecutableAdmissionCode.INTEGRITY_MISMATCH
