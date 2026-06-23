"""Customized simulation builder.

Public surface used by the Streamlit interface to:

1. Parse the standardised ``## Parameters`` table out of an agent handbook
   under ``examples/AGENT_POOL/ExtractedExampleInvestors/unique/``.
2. Decide a fresh ``Customized-NNN`` folder name without collisions.
3. Write a self-contained simulation bundle under both
   ``configs/CUSTOMIZED_SIMULATION/Customized-NNN/`` and
   ``examples/CUSTOMIZED_SIMULATION/Customized-NNN/``.
4. Look up the curated archetype-to-class mapping that lets the bundle
   re-use existing scenario player classes via dotted import paths
   (no edits to ``examples/<Scenario>/``).
"""

from .handbook_params import (
    ParamSpec,
    parse_parameters_file,
    parse_parameters_table,
)
from .archetype_class_map import (
    ArchetypeBinding,
    is_archetype_mapped,
    load_archetype_class_map,
    load_default_prompts,
    resolve_archetype_binding,
)
from .config_writer import (
    CustomizedAgentSelection,
    CustomizedBundleResult,
    next_customized_id,
    write_customized_bundle,
)

__all__ = [
    "ParamSpec",
    "parse_parameters_file",
    "parse_parameters_table",
    "ArchetypeBinding",
    "is_archetype_mapped",
    "load_archetype_class_map",
    "load_default_prompts",
    "resolve_archetype_binding",
    "CustomizedAgentSelection",
    "CustomizedBundleResult",
    "next_customized_id",
    "write_customized_bundle",
]
