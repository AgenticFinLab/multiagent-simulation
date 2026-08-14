from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from h2epr.construction import (
    ArchitectureSourceManifest,
    Availability,
    ReviewState,
    SourceAdapter,
    SourceDescriptor,
    SourceKind,
    SourcePolicyError,
)


def _write(path: Path, data: bytes = b'{"synthetic":true}') -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def _descriptor(path: str, sha256: str, **changes: object) -> SourceDescriptor:
    values = {
        "logical_source_id": "synthetic-source",
        "source_kind": SourceKind.SYNTHETIC,
        "relative_path": path,
        "expected_sha256": sha256,
        "availability": Availability.CONSTRUCTION_ONLY,
        "review_state": ReviewState.REVIEWED,
    }
    values.update(changes)
    return SourceDescriptor(**values)


def _read(root: Path, *descriptors: SourceDescriptor):
    return SourceAdapter(root).read_architecture(ArchitectureSourceManifest(tuple(descriptors)))


def _forged_descriptor(**changes: object) -> SourceDescriptor:
    values = {
        "logical_source_id": "synthetic-source",
        "source_kind": SourceKind.SYNTHETIC,
        "relative_path": "source.json",
        "expected_sha256": "0" * 64,
        "availability": Availability.CONSTRUCTION_ONLY,
        "review_state": ReviewState.REVIEWED,
    }
    values.update(changes)
    descriptor = object.__new__(SourceDescriptor)
    for field_name, value in values.items():
        object.__setattr__(descriptor, field_name, value)
    return descriptor


def _forged_manifest(descriptors: object) -> ArchitectureSourceManifest:
    manifest = object.__new__(ArchitectureSourceManifest)
    object.__setattr__(manifest, "descriptors", descriptors)
    return manifest


@pytest.mark.parametrize(
    ("relative_path", "code"),
    [
        ("reference_" + "epg.json", "reference_forbidden"),
        ("nested/REFERENCE_" + "EPG.JSON", "reference_forbidden"),
        ("../escape.json", "path_traversal"),
        ("*.json", "glob_forbidden"),
        ("nested/?.json", "glob_forbidden"),
        ("/absolute.json", "absolute_path_forbidden"),
    ],
)
def test_lexical_path_rejection_occurs_before_open(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, relative_path: str, code: str
) -> None:
    opened = False

    def forbidden_open(*args: object, **kwargs: object):
        nonlocal opened
        opened = True
        raise AssertionError("open must not be attempted")

    monkeypatch.setattr(Path, "open", forbidden_open)
    with pytest.raises(SourcePolicyError, match=code):
        _read(tmp_path, _descriptor(relative_path, "0" * 64))
    assert not opened


def test_directory_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "directory.json").mkdir()
    with pytest.raises(SourcePolicyError, match="not_regular_file"):
        _read(tmp_path, _descriptor("directory.json", "0" * 64))


def test_symlink_escaping_approved_root_is_rejected(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-g1-source.json"
    sha = _write(outside)
    (tmp_path / "escape.json").symlink_to(outside)
    with pytest.raises(SourcePolicyError, match="approved_root_escape"):
        _read(tmp_path, _descriptor("escape.json", sha))


def test_hash_mismatch_is_rejected(tmp_path: Path) -> None:
    _write(tmp_path / "source.json")
    with pytest.raises(SourcePolicyError, match="content_hash_mismatch"):
        _read(tmp_path, _descriptor("source.json", "0" * 64))


def test_duplicate_logical_source_is_rejected(tmp_path: Path) -> None:
    sha_a = _write(tmp_path / "a.json")
    sha_b = _write(tmp_path / "b.json")
    with pytest.raises(SourcePolicyError, match="duplicate_logical_source"):
        _read(tmp_path, _descriptor("a.json", sha_a), _descriptor("b.json", sha_b))


def test_duplicate_resolved_path_is_rejected(tmp_path: Path) -> None:
    sha = _write(tmp_path / "a.json")
    first = _descriptor("a.json", sha)
    second = _descriptor("a.json", sha, logical_source_id="synthetic-source-2")
    with pytest.raises(SourcePolicyError, match="duplicate_resolved_path"):
        _read(tmp_path, first, second)


def test_unknown_source_kind_is_rejected(tmp_path: Path) -> None:
    sha = _write(tmp_path / "a.json")
    descriptor = _descriptor("a.json", sha, source_kind="unknown")
    with pytest.raises(SourcePolicyError, match="unknown_source_kind"):
        _read(tmp_path, descriptor)


def test_source_kind_basename_must_match(tmp_path: Path) -> None:
    sha = _write(tmp_path / "wrong.json")
    descriptor = _descriptor("wrong.json", sha, source_kind=SourceKind.DRAFT_EPG)
    with pytest.raises(SourcePolicyError, match="source_kind_path_mismatch"):
        _read(tmp_path, descriptor)


def test_explicit_manifest_does_not_read_implicit_sibling(tmp_path: Path) -> None:
    selected_sha = _write(tmp_path / "selected.json")
    _write(tmp_path / "unlisted.json", b"not-json-and-must-not-be-read")
    loaded = _read(tmp_path, _descriptor("selected.json", selected_sha))
    assert [item.descriptor.relative_path for item in loaded] == ["selected.json"]


def test_descriptor_has_no_catch_all_metadata_or_reference_locator() -> None:
    fields = set(SourceDescriptor.__dataclass_fields__)
    assert "metadata" not in fields
    assert "reference" not in fields
    assert "evaluation_input" not in fields


def test_source_descriptor_constructor_rejects_logical_id_string_subclass() -> None:
    class LogicalIdImpostor(str):
        def __hash__(self) -> int:
            raise AssertionError("hash must not run")

    with pytest.raises(ValueError, match="source_descriptor_id_invalid"):
        _descriptor("source.json", "0" * 64, logical_source_id=LogicalIdImpostor("synthetic-source"))


def test_source_descriptor_constructor_rejects_source_kind_string_subclass() -> None:
    class KindImpostor(str):
        def __eq__(self, other: object) -> bool:
            raise AssertionError("equality must not run")

        __hash__ = str.__hash__

    with pytest.raises(ValueError, match="source_descriptor_kind_invalid"):
        _descriptor("source.json", "0" * 64, source_kind=KindImpostor("synthetic"))


def test_source_descriptor_constructor_rejects_expected_hash_string_subclass() -> None:
    class HashImpostor(str):
        def __eq__(self, other: object) -> bool:
            raise AssertionError("comparison must not run")

    with pytest.raises(ValueError, match="source_descriptor_hash_invalid"):
        _descriptor("source.json", HashImpostor("0" * 64))


def test_source_adapter_rejects_architecture_manifest_subclass(tmp_path: Path) -> None:
    class ManifestImpostor(ArchitectureSourceManifest):
        def __getattribute__(self, name: str):
            if name == "descriptors":
                raise AssertionError("descriptor access must not run")
            return super().__getattribute__(name)

    manifest = object.__new__(ManifestImpostor)
    with pytest.raises(SourcePolicyError, match="source_manifest_type_invalid"):
        SourceAdapter(tmp_path).read_architecture(manifest)


def test_source_adapter_rejects_descriptor_tuple_subclass_without_iteration(tmp_path: Path) -> None:
    class DescriptorTupleImpostor(tuple):
        def __iter__(self):
            raise AssertionError("iteration must not run")

    manifest = _forged_manifest(DescriptorTupleImpostor(()))
    with pytest.raises(SourcePolicyError, match="source_manifest_descriptors_invalid"):
        SourceAdapter(tmp_path).read_architecture(manifest)


def test_source_adapter_rejects_source_descriptor_subclass(tmp_path: Path) -> None:
    class DescriptorImpostor(SourceDescriptor):
        def __getattribute__(self, name: str):
            raise AssertionError("field access must not run")

    descriptor = object.__new__(DescriptorImpostor)
    with pytest.raises(SourcePolicyError, match="source_descriptor_type_invalid"):
        SourceAdapter(tmp_path).read_architecture(_forged_manifest((descriptor,)))


def test_source_adapter_rejects_forged_descriptor_missing_fields_stably(tmp_path: Path) -> None:
    expected = {
        "logical_source_id": "source_descriptor_id_invalid",
        "source_kind": "source_descriptor_kind_invalid",
        "relative_path": "source_descriptor_path_invalid",
        "expected_sha256": "source_descriptor_hash_invalid",
        "availability": "source_descriptor_availability_invalid",
        "review_state": "source_descriptor_review_state_invalid",
    }
    for missing_field, code in expected.items():
        descriptor = _forged_descriptor()
        object.__delattr__(descriptor, missing_field)
        with pytest.raises(SourcePolicyError, match=code):
            SourceAdapter(tmp_path).read_architecture(_forged_manifest((descriptor,)))


def test_source_adapter_rejects_logical_id_behavior_before_hash_or_equality(tmp_path: Path) -> None:
    class LogicalIdImpostor(str):
        def __hash__(self) -> int:
            raise AssertionError("hash must not run")

        def __eq__(self, other: object) -> bool:
            raise AssertionError("equality must not run")

    descriptor = _forged_descriptor(logical_source_id=LogicalIdImpostor("synthetic-source"))
    with pytest.raises(SourcePolicyError, match="source_descriptor_id_invalid"):
        SourceAdapter(tmp_path).read_architecture(_forged_manifest((descriptor,)))


def test_source_adapter_rejects_expected_hash_behavior_before_comparison(tmp_path: Path) -> None:
    class HashImpostor(str):
        def __eq__(self, other: object) -> bool:
            raise AssertionError("comparison must not run")

    descriptor = _forged_descriptor(expected_sha256=HashImpostor("0" * 64))
    with pytest.raises(SourcePolicyError, match="source_descriptor_hash_invalid"):
        SourceAdapter(tmp_path).read_architecture(_forged_manifest((descriptor,)))
