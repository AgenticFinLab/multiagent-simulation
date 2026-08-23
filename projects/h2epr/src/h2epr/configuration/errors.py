"""Stable failure classes for bounded Scenario Configuration admission."""

from __future__ import annotations

from enum import Enum


class ConfigurationFailureClass(str, Enum):
    """The authority layer to which a configuration admission failure routes."""

    SOURCE = "source"
    INTEGRITY = "integrity"
    STRUCTURE = "structure"
    SEMANTIC_REFERENCE = "semantic_reference"
    ASSEMBLY = "assembly"
    EXECUTION_BOUNDARY = "execution_boundary"
    PREFLIGHT_CONTEXT = "preflight_context"


class ConfigurationErrorCode(str, Enum):
    """Stable machine codes for the E5 configuration-admission surface."""

    SOURCE_NOT_FOUND = "CONFIG_SOURCE_NOT_FOUND"
    PROJECT_ROOT_NOT_FOUND = "CONFIG_PROJECT_ROOT_NOT_FOUND"
    PATH_UNSAFE = "CONFIG_PATH_UNSAFE"
    JSON_INVALID = "CONFIG_JSON_INVALID"
    JSON_DUPLICATE_KEY = "CONFIG_JSON_DUPLICATE_KEY"
    RELEASE_MANIFEST_INVALID = "CONFIG_RELEASE_MANIFEST_INVALID"
    CHECKSUM_INVENTORY_INVALID = "CONFIG_CHECKSUM_INVENTORY_INVALID"
    INTEGRITY_MISMATCH = "CONFIG_INTEGRITY_MISMATCH"
    SCHEMA_VERSION_UNSUPPORTED = "CONFIG_SCHEMA_VERSION_UNSUPPORTED"
    SCHEMA_INVALID = "CONFIG_SCHEMA_INVALID"
    SCHEMA_VALIDATION_FAILED = "CONFIG_SCHEMA_VALIDATION_FAILED"
    CANONICALIZATION_FAILED = "CONFIG_CANONICALIZATION_FAILED"
    SEMANTIC_INPUT_MISMATCH = "CONFIG_SEMANTIC_INPUT_MISMATCH"
    MAPPING_PROFILE_INVALID = "CONFIG_MAPPING_PROFILE_INVALID"
    REFERENCE_UNRESOLVED = "CONFIG_REFERENCE_UNRESOLVED"
    ASSEMBLY_INVALID = "CONFIG_ASSEMBLY_INVALID"
    OVERLAY_TARGET_INVALID = "CONFIG_OVERLAY_TARGET_INVALID"
    COVERAGE_MISMATCH = "CONFIG_COVERAGE_MISMATCH"
    EXECUTION_BOUNDARY_INVALID = "CONFIG_EXECUTION_BOUNDARY_INVALID"
    PREFLIGHT_CONTEXT_INVALID = "CONFIG_PREFLIGHT_CONTEXT_INVALID"


_FAILURE_CLASS_BY_CODE = {
    ConfigurationErrorCode.SOURCE_NOT_FOUND: ConfigurationFailureClass.SOURCE,
    ConfigurationErrorCode.PROJECT_ROOT_NOT_FOUND: ConfigurationFailureClass.SOURCE,
    ConfigurationErrorCode.PATH_UNSAFE: ConfigurationFailureClass.SOURCE,
    ConfigurationErrorCode.JSON_INVALID: ConfigurationFailureClass.STRUCTURE,
    ConfigurationErrorCode.JSON_DUPLICATE_KEY: ConfigurationFailureClass.STRUCTURE,
    ConfigurationErrorCode.RELEASE_MANIFEST_INVALID: ConfigurationFailureClass.INTEGRITY,
    ConfigurationErrorCode.CHECKSUM_INVENTORY_INVALID: ConfigurationFailureClass.INTEGRITY,
    ConfigurationErrorCode.INTEGRITY_MISMATCH: ConfigurationFailureClass.INTEGRITY,
    ConfigurationErrorCode.SCHEMA_VERSION_UNSUPPORTED: ConfigurationFailureClass.STRUCTURE,
    ConfigurationErrorCode.SCHEMA_INVALID: ConfigurationFailureClass.STRUCTURE,
    ConfigurationErrorCode.SCHEMA_VALIDATION_FAILED: ConfigurationFailureClass.STRUCTURE,
    ConfigurationErrorCode.CANONICALIZATION_FAILED: ConfigurationFailureClass.STRUCTURE,
    ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH: ConfigurationFailureClass.SEMANTIC_REFERENCE,
    ConfigurationErrorCode.MAPPING_PROFILE_INVALID: ConfigurationFailureClass.SEMANTIC_REFERENCE,
    ConfigurationErrorCode.REFERENCE_UNRESOLVED: ConfigurationFailureClass.SEMANTIC_REFERENCE,
    ConfigurationErrorCode.ASSEMBLY_INVALID: ConfigurationFailureClass.ASSEMBLY,
    ConfigurationErrorCode.OVERLAY_TARGET_INVALID: ConfigurationFailureClass.ASSEMBLY,
    ConfigurationErrorCode.COVERAGE_MISMATCH: ConfigurationFailureClass.ASSEMBLY,
    ConfigurationErrorCode.EXECUTION_BOUNDARY_INVALID: ConfigurationFailureClass.EXECUTION_BOUNDARY,
    ConfigurationErrorCode.PREFLIGHT_CONTEXT_INVALID: ConfigurationFailureClass.PREFLIGHT_CONTEXT,
}


class ConfigurationAdmissionError(ValueError):
    """One deterministic, routed rejection from the E5 admission surface."""

    def __init__(
        self,
        code: ConfigurationErrorCode,
        *,
        pointer: str = "",
        detail: str = "",
    ) -> None:
        self.code = code
        self.failure_class = _FAILURE_CLASS_BY_CODE[code]
        self.pointer = pointer
        self.detail = detail
        parts = [code.value]
        if pointer:
            parts.append(pointer)
        if detail:
            parts.append(detail)
        super().__init__(":".join(parts))


__all__ = [
    "ConfigurationAdmissionError",
    "ConfigurationErrorCode",
    "ConfigurationFailureClass",
]
