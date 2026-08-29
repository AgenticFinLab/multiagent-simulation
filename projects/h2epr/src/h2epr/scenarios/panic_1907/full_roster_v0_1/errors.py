"""Stable failures for Panic full-roster Policy Realization admission."""

from __future__ import annotations

from enum import Enum


class PolicyRealizationErrorCode(str, Enum):
    """Machine-readable rejection codes for the event-local admission."""

    PREFLIGHT_INVALID = "PANIC_POLICY_PREFLIGHT_INVALID"
    SOURCE_NOT_FOUND = "PANIC_POLICY_SOURCE_NOT_FOUND"
    PATH_UNSAFE = "PANIC_POLICY_PATH_UNSAFE"
    INTEGRITY_MISMATCH = "PANIC_POLICY_INTEGRITY_MISMATCH"
    JSON_INVALID = "PANIC_POLICY_JSON_INVALID"
    JSON_DUPLICATE_KEY = "PANIC_POLICY_JSON_DUPLICATE_KEY"
    SCHEMA_INVALID = "PANIC_POLICY_SCHEMA_INVALID"
    SCHEMA_VALIDATION_FAILED = "PANIC_POLICY_SCHEMA_VALIDATION_FAILED"
    PARENT_MISMATCH = "PANIC_POLICY_PARENT_MISMATCH"
    CONFIGURATION_POINTER_INVALID = "PANIC_POLICY_CONFIGURATION_POINTER_INVALID"
    PLACEMENT_COVERAGE_MISMATCH = "PANIC_POLICY_PLACEMENT_COVERAGE_MISMATCH"
    SEMANTIC_REFERENCE_INVALID = "PANIC_POLICY_SEMANTIC_REFERENCE_INVALID"
    POLICY_COVERAGE_MISMATCH = "PANIC_POLICY_POLICY_COVERAGE_MISMATCH"
    LIFECYCLE_COVERAGE_MISMATCH = "PANIC_POLICY_LIFECYCLE_COVERAGE_MISMATCH"
    COVERAGE_MISMATCH = "PANIC_POLICY_COVERAGE_MISMATCH"
    IMPLEMENTATION_MISSING = "PANIC_POLICY_IMPLEMENTATION_MISSING"
    IMPLEMENTATION_VERSION_MISMATCH = "PANIC_POLICY_IMPLEMENTATION_VERSION_MISMATCH"


class PolicyRealizationAdmissionError(ValueError):
    """One fail-closed Policy Realization rejection."""

    def __init__(
        self,
        code: PolicyRealizationErrorCode,
        *,
        pointer: str = "",
        detail: str = "",
    ) -> None:
        self.code = code
        self.pointer = pointer
        self.detail = detail
        parts = [code.value]
        if pointer:
            parts.append(pointer)
        if detail:
            parts.append(detail)
        super().__init__(":".join(parts))


__all__ = [
    "PolicyRealizationAdmissionError",
    "PolicyRealizationErrorCode",
]
