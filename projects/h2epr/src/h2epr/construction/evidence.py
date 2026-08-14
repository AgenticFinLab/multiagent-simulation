"""Evidence minimization and bounded diagnostic policies."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .model import (
    ApprovedExcerpt,
    Availability,
    ConstructionDiagnostic,
    EvidenceRef,
    ReviewState,
)


class EvidencePolicyError(ValueError):
    """Evidence content exceeded its minimized representation boundary."""


def _validate_excerpt(excerpt: object) -> ApprovedExcerpt:
    if not isinstance(excerpt, ApprovedExcerpt):
        raise EvidencePolicyError("approved_excerpt_type_required")
    try:
        return ApprovedExcerpt(
            approval_id=excerpt.approval_id,
            purpose=excerpt.purpose,
            text=excerpt.text,
            utf8_bytes=excerpt.utf8_bytes,
        )
    except AttributeError as exc:
        raise EvidencePolicyError("approved_excerpt_fields_missing") from exc


def _content_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()


def minimize_evidence(
    *,
    source_id: str,
    pointer: str,
    raw_value: Any,
    availability: Availability,
    review_state: ReviewState,
    excerpt: ApprovedExcerpt | None = None,
) -> EvidenceRef:
    if excerpt is not None:
        excerpt = _validate_excerpt(excerpt)
    return EvidenceRef(
        source_id=source_id,
        pointer=pointer,
        content_sha256=hashlib.sha256(_content_bytes(raw_value)).hexdigest(),
        availability=availability,
        review_state=review_state,
        excerpt=excerpt,
    )


def bounded_diagnostic(code: str, summary: str, pointer: str) -> ConstructionDiagnostic:
    return ConstructionDiagnostic(code=code, summary=summary, pointer=pointer)
