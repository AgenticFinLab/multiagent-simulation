"""Customized simulation builder.

Public surface used by the Streamlit interface to:

1. Parse the standardised ``## Parameters`` table out of an agent handbook
   under ``examples/AGENT_POOL/ExtractedExampleInvestors/unique/``.
2. Look up the marketplace catalog (discovered from :mod:`masim.agents` —
   each canonical class declares its own metadata and default prompts):
   supported engines, canonical class paths under ``masim.agents.*``, and
   default scenario-free prompts.
3. Look up the scenario feature manifest (``scenario_features.yml``) and check
   whether a roster is compatible with a given scenario.
4. Decide a fresh ``Customized-NNN`` folder name without collisions and write
   a self-contained simulation bundle under both
   ``configs/CUSTOMIZED_SIMULATION/Customized-NNN/`` and
   ``examples/CUSTOMIZED_SIMULATION/Customized-NNN/``.
"""

from .handbook_params import (
    ParamSpec,
    parse_parameters_file,
    parse_parameters_table,
)
from .agent_catalog import (
    AgentEntry,
    all_archetypes,
    get_agent_entry,
    get_canonical_class_path,
    get_default_prompts,
    is_archetype_supported,
    load_agent_catalog,
    required_features,
    supported_engines,
)
from .scenario_features import (
    is_scenario_compatible,
    load_scenario_features,
    scenario_market_features,
)
from .config_writer import (
    CustomizedAgentSelection,
    CustomizedBundleResult,
    apply_customized_modifications,
    apply_default_bundle_overrides,
    copy_default_scenario_bundle,
    extract_default_players,
    extract_market_extras,
    initialize_customized_folder,
    next_customized_id,
    write_customized_bundle,
    write_default_scenario_bundle,
)
from .selection_state import (
    delete_selection_state,
    load_selection_state,
    restore_state_to_session,
    save_selection_state,
    save_state_from_session,
)

__all__ = [
    # handbook params
    "ParamSpec",
    "parse_parameters_file",
    "parse_parameters_table",
    # agent catalog
    "AgentEntry",
    "load_agent_catalog",
    "get_agent_entry",
    "get_canonical_class_path",
    "get_default_prompts",
    "is_archetype_supported",
    "supported_engines",
    "required_features",
    "all_archetypes",
    # scenario features
    "load_scenario_features",
    "scenario_market_features",
    "is_scenario_compatible",
    # bundle writer
    "CustomizedAgentSelection",
    "CustomizedBundleResult",
    "apply_customized_modifications",
    "apply_default_bundle_overrides",
    "copy_default_scenario_bundle",
    "extract_default_players",
    "extract_market_extras",
    "initialize_customized_folder",
    "next_customized_id",
    "write_customized_bundle",
    "write_default_scenario_bundle",
    # selection state persistence
    "delete_selection_state",
    "load_selection_state",
    "restore_state_to_session",
    "save_selection_state",
    "save_state_from_session",
]
