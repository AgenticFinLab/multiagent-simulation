"""Bounded, non-executable Scenario Configuration admission."""

from .errors import (
    ConfigurationAdmissionError,
    ConfigurationErrorCode,
    ConfigurationFailureClass,
)
from .loader import (
    CONFIGURATION_ADMISSION_VERSION,
    CONFIGURATION_CANONICALIZATION,
    CONFIGURATION_FORMAT_ID,
    CONFIGURATION_RECEIPT_FORMAT,
    CONFIGURATION_SCHEMA_RELATIVE_PATH,
    DOMAIN_NEUTRAL_SEMANTIC_CONFIGURATION_FORMAT_ID,
    DOMAIN_NEUTRAL_SEMANTIC_CONFIGURATION_SCHEMA_RELATIVE_PATH,
    SEMANTIC_CONFIGURATION_ADMISSION_VERSION,
    SEMANTIC_CONFIGURATION_FORMAT_ID,
    SEMANTIC_CONFIGURATION_SCHEMA_RELATIVE_PATH,
    ScenarioConfigurationAdmission,
    build_configuration_preflight_receipt,
    load_scenario_configuration,
)

__all__ = [
    "CONFIGURATION_ADMISSION_VERSION",
    "CONFIGURATION_CANONICALIZATION",
    "CONFIGURATION_FORMAT_ID",
    "CONFIGURATION_RECEIPT_FORMAT",
    "CONFIGURATION_SCHEMA_RELATIVE_PATH",
    "DOMAIN_NEUTRAL_SEMANTIC_CONFIGURATION_FORMAT_ID",
    "DOMAIN_NEUTRAL_SEMANTIC_CONFIGURATION_SCHEMA_RELATIVE_PATH",
    "SEMANTIC_CONFIGURATION_ADMISSION_VERSION",
    "SEMANTIC_CONFIGURATION_FORMAT_ID",
    "SEMANTIC_CONFIGURATION_SCHEMA_RELATIVE_PATH",
    "ConfigurationAdmissionError",
    "ConfigurationErrorCode",
    "ConfigurationFailureClass",
    "ScenarioConfigurationAdmission",
    "build_configuration_preflight_receipt",
    "load_scenario_configuration",
]
