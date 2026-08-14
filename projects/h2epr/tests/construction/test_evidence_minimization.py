from __future__ import annotations

import pytest

from h2epr.construction import (
    ApprovedExcerpt,
    Availability,
    ConstructionDiagnostic,
    EvidencePolicyError,
    ReviewState,
    bounded_diagnostic,
    canonical_snapshot_bytes,
    minimize_evidence,
)


def test_evidence_default_retains_only_pointer_hash_and_adjudication() -> None:
    raw = "synthetic confidential evidence paragraph"
    ref = minimize_evidence(
        source_id="synthetic",
        pointer="/sources/0/text",
        raw_value=raw,
        availability=Availability.CONSTRUCTION_ONLY,
        review_state=ReviewState.REVIEWED,
    )
    rendered = repr(ref)
    assert raw not in rendered
    assert ref.pointer == "/sources/0/text"
    assert len(ref.content_sha256) == 64
    assert ref.excerpt is None


def test_excerpt_requires_approval_and_purpose() -> None:
    with pytest.raises(EvidencePolicyError, match="approval_id_required"):
        ApprovedExcerpt.create("", "test", "synthetic")
    with pytest.raises(EvidencePolicyError, match="purpose_required"):
        ApprovedExcerpt.create("approval", "", "synthetic")


def test_excerpt_accepts_inclusive_280_utf8_bytes() -> None:
    excerpt = ApprovedExcerpt.create("approval", "synthetic boundary", "a" * 280)
    assert excerpt.utf8_bytes == 280


def test_excerpt_rejects_281_utf8_bytes() -> None:
    with pytest.raises(EvidencePolicyError, match="excerpt_too_large"):
        ApprovedExcerpt.create("approval", "synthetic boundary", "a" * 281)


def test_multibyte_excerpt_limit_counts_utf8_bytes() -> None:
    accepted = ApprovedExcerpt.create("approval", "synthetic boundary", "界" * 93)
    assert accepted.utf8_bytes == 279
    with pytest.raises(EvidencePolicyError, match="excerpt_too_large"):
        ApprovedExcerpt.create("approval", "synthetic boundary", "界" * 94)


def test_bounded_diagnostic_rejects_payload_sized_summary() -> None:
    diagnostic = bounded_diagnostic("synthetic_code", "bounded summary", "/pointer")
    assert diagnostic.summary == "bounded summary"
    with pytest.raises(EvidencePolicyError, match="diagnostic_summary_too_large"):
        bounded_diagnostic("synthetic_code", "x" * 161, "/pointer")


def test_bounded_diagnostic_rejects_multiline_summary() -> None:
    with pytest.raises(EvidencePolicyError, match="diagnostic_summary_multiline"):
        bounded_diagnostic("synthetic_code", "raw\npayload", "/pointer")


def test_direct_excerpt_constructor_enforces_declared_and_actual_size() -> None:
    with pytest.raises(EvidencePolicyError, match="excerpt_byte_count_mismatch"):
        ApprovedExcerpt("approval", "synthetic", "bounded", 0)
    with pytest.raises(EvidencePolicyError, match="excerpt_too_large"):
        ApprovedExcerpt("approval", "synthetic", "x" * 281, 281)


def test_direct_excerpt_constructor_enforces_approval_and_purpose() -> None:
    with pytest.raises(EvidencePolicyError, match="approval_id_required"):
        ApprovedExcerpt("", "synthetic", "bounded", 7)
    with pytest.raises(EvidencePolicyError, match="purpose_required"):
        ApprovedExcerpt("approval", "", "bounded", 7)


def test_forged_excerpt_is_revalidated_at_evidence_ingestion() -> None:
    forged = object.__new__(ApprovedExcerpt)
    object.__setattr__(forged, "approval_id", "approval")
    object.__setattr__(forged, "purpose", "synthetic")
    object.__setattr__(forged, "text", "x" * 281)
    object.__setattr__(forged, "utf8_bytes", 0)
    with pytest.raises(EvidencePolicyError, match="excerpt_too_large"):
        minimize_evidence(
            source_id="synthetic",
            pointer="/evidence",
            raw_value="synthetic",
            availability=Availability.CONSTRUCTION_ONLY,
            review_state=ReviewState.REVIEWED,
            excerpt=forged,
        )


def test_forged_excerpt_is_revalidated_at_deterministic_export() -> None:
    forged = object.__new__(ApprovedExcerpt)
    object.__setattr__(forged, "approval_id", "approval")
    object.__setattr__(forged, "purpose", "synthetic")
    object.__setattr__(forged, "text", "bounded")
    object.__setattr__(forged, "utf8_bytes", 0)
    with pytest.raises(EvidencePolicyError, match="excerpt_byte_count_mismatch"):
        canonical_snapshot_bytes(forged)


def test_direct_diagnostic_constructor_enforces_single_line_byte_bound() -> None:
    with pytest.raises(EvidencePolicyError, match="diagnostic_summary_multiline"):
        ConstructionDiagnostic("synthetic", "line one\nline two", "/pointer")
    with pytest.raises(EvidencePolicyError, match="diagnostic_summary_too_large"):
        ConstructionDiagnostic("synthetic", "界" * 54, "/pointer")
    diagnostic = ConstructionDiagnostic("synthetic", "界" * 53, "/pointer")
    assert len(diagnostic.summary.encode("utf-8")) == 159


def test_diagnostic_rejects_non_string_code() -> None:
    with pytest.raises(EvidencePolicyError, match="diagnostic_code_invalid"):
        ConstructionDiagnostic(7, "bounded", "/pointer")  # type: ignore[arg-type]


def test_diagnostic_rejects_non_string_pointer() -> None:
    with pytest.raises(EvidencePolicyError, match="diagnostic_pointer_invalid"):
        ConstructionDiagnostic("synthetic", "bounded", 7)  # type: ignore[arg-type]


def test_diagnostic_rejects_invalid_or_oversize_code() -> None:
    class CodeSubclass(str):
        pass

    for code in ("", "Uppercase", "not-valid", "a" * 65, CodeSubclass("synthetic")):
        with pytest.raises(EvidencePolicyError, match="diagnostic_code_invalid"):
            ConstructionDiagnostic(code, "bounded", "/pointer")


def test_diagnostic_rejects_noncanonical_pointer() -> None:
    class PointerSubclass(str):
        pass

    for pointer in ("not-a-pointer", "/bad~2escape", "//ambiguous", PointerSubclass("/pointer")):
        with pytest.raises(EvidencePolicyError, match="diagnostic_pointer_invalid"):
            ConstructionDiagnostic("synthetic", "bounded", pointer)


def test_diagnostic_export_rejects_noncanonical_type_and_missing_fields_stably() -> None:
    class DiagnosticSubclass(ConstructionDiagnostic):
        pass

    subclass = object.__new__(DiagnosticSubclass)
    object.__setattr__(subclass, "code", "synthetic")
    object.__setattr__(subclass, "summary", "bounded")
    object.__setattr__(subclass, "pointer", "/pointer")
    with pytest.raises(EvidencePolicyError, match="diagnostic_type_invalid"):
        canonical_snapshot_bytes(subclass)

    missing_pointer = object.__new__(ConstructionDiagnostic)
    object.__setattr__(missing_pointer, "code", "synthetic")
    object.__setattr__(missing_pointer, "summary", "bounded")
    with pytest.raises(EvidencePolicyError, match="diagnostic_pointer_invalid"):
        canonical_snapshot_bytes(missing_pointer)


def test_valid_root_and_nested_diagnostic_pointers_remain_accepted() -> None:
    root = ConstructionDiagnostic("synthetic", "bounded", "")
    nested = ConstructionDiagnostic("synthetic_nested", "bounded", "/stages/0")
    assert canonical_snapshot_bytes(root) == (
        b'{"code":"synthetic","pointer":"","summary":"bounded"}\n'
    )
    assert canonical_snapshot_bytes(nested) == (
        b'{"code":"synthetic_nested","pointer":"/stages/0","summary":"bounded"}\n'
    )
