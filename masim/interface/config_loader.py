"""Configuration loader for discovering and parsing simulation scenarios."""

import logging
from functools import lru_cache
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
import yaml

logger = logging.getLogger(__name__)


# Absolute project root — anchored to this source file's location so that
# scenario discovery, experiment data, and example assets are found regardless
# of the working directory from which Streamlit is launched.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]  # masim/interface → project root

# Base directory for docs
EXAMPLES_DIR = _PROJECT_ROOT / "examples"

CONFIGS_DIR = _PROJECT_ROOT / "configs"
EXPERIMENT_DIR = _PROJECT_ROOT / "EXPERIMENT"

# All implemented variants are available in the simulation workflow.
_HIDDEN_VARIANTS: set[str] = set()

# Directories excluded from scenario discovery
_EXCLUDED_DIRS = {"TEMPLATES", "__pycache__", "Demo", "CUSTOMIZED_SIMULATION"}


def _configs_path(scenario_key: str) -> Path:
    """Return the configs/ subdirectory for a scenario key.

    Args:
        scenario_key: Slash-separated key (e.g. 'AssetBubble/Rule') or flat name
    """
    return CONFIGS_DIR / scenario_key


def _experiment_path(scenario_key: str) -> Path:
    """Return the EXPERIMENT/ subdirectory for a scenario key."""
    return EXPERIMENT_DIR / scenario_key


def _examples_path(scenario_key: str) -> Path:
    """Return the examples/ subdirectory for a scenario key."""
    return EXAMPLES_DIR / scenario_key


def _flat_scenario_name(key: str) -> str:
    """Convert a slash-separated key to the legacy flat name for dict lookups.

    Examples:
        'AssetBubble/Rule'    -> 'AssetBubble'
        'AssetBubble/LLM'     -> 'AssetBubbleLLM'
        'AssetBubble/RuleLLM' -> 'AssetBubbleRuleLLM'
        'Demo'                -> 'Demo'
    """
    if "/" not in key:
        return key
    base, variant = key.split("/", 1)
    if variant == "Rule":
        return base
    return base + variant


def scenario_display_name(key: str) -> str:
    """Auto-generate a display name from a scenario key by splitting CamelCase.

    Examples:
        'AssetBubble/Rule'                -> 'Asset Bubble (Rule)'
        'FlashCrash2010/LLM'              -> 'Flash Crash 2010 (LLM)'
        'My_Study/AnchoringEffect/Rule'   -> 'Anchoring Effect (Rule)'
        'Demo'                            -> 'Demo'
    """
    # Strip project prefix for 3+-part keys (project/scenario/variant).
    parts = key.split("/")
    if len(parts) >= 3 and not key.startswith("CUSTOMIZED_SIMULATION/"):
        key = "/".join(parts[1:])  # drop project segment

    if "/" in key:
        base, variant = key.split("/", 1)
    else:
        base, variant = key, ""

    # Split CamelCase and letter-digit boundaries
    display = re.sub(
        r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|(?<=[A-Za-z])(?=[0-9])",
        " ",
        base,
    )

    if variant:
        return f"{display} ({variant})"
    return display


def _resolve_display_key(scenario_key: str) -> str:
    """Map special scenario keys to their source key for metadata display.

    Handles:
    - Project-prefixed keys: ``{project}/{scenario}/{variant}`` -> ``{scenario}/{variant}``
    - Rounds-adjusted bundles: ``CUSTOMIZED_SIMULATION/Default-{S}-{V}-rN`` -> ``{S}/{V}``

    Non-special keys are returned unchanged.
    """
    # Project-prefixed: 3+ parts where first is not a known special dir.
    parts = scenario_key.split("/")
    if (
        len(parts) >= 3
        and not scenario_key.startswith("CUSTOMIZED_SIMULATION/")
    ):
        # Strip project prefix for metadata lookup.
        return "/".join(parts[1:])

    if scenario_key.startswith("CUSTOMIZED_SIMULATION/"):
        tail = scenario_key.split("/", 1)[1]
        # New project-scoped format:
        # CUSTOMIZED_SIMULATION/{bundle_name}/Default/{variant}
        # bundle_name = "{slug}-{id}-{Scenario}" → extract scenario from last segment.
        tail_parts = tail.split("/")
        if len(tail_parts) >= 3 and tail_parts[1] == "Default":
            bundle_name = tail_parts[0]  # e.g. "MYTest-b6beb998-AnchoringEffect"
            variant = tail_parts[2]
            # Scenario is the last hyphen-separated segment of bundle_name
            scenario = bundle_name.rsplit("-", 1)[-1]
            return f"{scenario}/{variant}"
        # Customized-agents format:
        # CUSTOMIZED_SIMULATION/{bundle_name}/Customized-agents
        if len(tail_parts) >= 2 and tail_parts[1] == "Customized-agents":
            bundle_name = tail_parts[0]
            scenario = bundle_name.rsplit("-", 1)[-1]
            return f"{scenario}/Rule"
        # Legacy format: CUSTOMIZED_SIMULATION/[team-{team}-]Default-{S}-{V}-rN
        # Multi-team deployments prefix the deterministic Default bundle id
        # with ``team-{team_name}-``; peel that off first so the shape check
        # below matches both single-team and multi-team layouts.  The import
        # is deferred to avoid a circular import at module load.
        from .customized.team_namespace import strip_team_prefix
        stripped_tail = strip_team_prefix(tail)
        if stripped_tail.startswith("Default-"):
            body = re.sub(r"-r\d+$", "", stripped_tail[len("Default-"):])
            if "-" in body:
                scenario, variant = body.rsplit("-", 1)
                return f"{scenario}/{variant}"
    return scenario_key


def discover_scenarios() -> List[str]:
    """Discover all available simulation scenarios from configs directory.

    Scans configs/ at depth-2 for simulation.yml files.  Returns a sorted
    list of slash-separated keys like 'AssetBubble/Rule'.  Rag variants
    and TEMPLATES are excluded.
    """
    if not CONFIGS_DIR.exists():
        return []

    found: List[str] = []
    for item in sorted(CONFIGS_DIR.iterdir()):
        if (
            not item.is_dir()
            or item.name.startswith("_")
            or item.name in _EXCLUDED_DIRS
        ):
            continue
        # Depth-1: flat scenario (e.g. configs/Demo/simulation.yml)
        if (item / "simulation.yml").exists():
            found.append(item.name)
            continue
        # Depth-2: nested (e.g. configs/AssetBubble/Rule/simulation.yml)
        for sub in sorted(item.iterdir()):
            if not sub.is_dir() or sub.name in _HIDDEN_VARIANTS:
                continue
            if (sub / "simulation.yml").exists():
                found.append(f"{item.name}/{sub.name}")
    return found


def discover_scenario_groups() -> Dict[str, List[str]]:
    """Group discovered scenarios by their base scenario name.

    Returns:
        Ordered dict mapping base name (e.g. 'AssetBubble') to a list of
        full keys (e.g. ['AssetBubble/Rule', 'AssetBubble/LLM', ...]).
    """
    from collections import OrderedDict

    groups: Dict[str, List[str]] = OrderedDict()
    for key in discover_scenarios():
        if "/" in key:
            base = key.split("/", 1)[0]
        else:
            base = key
        groups.setdefault(base, []).append(key)
    return groups


def get_scenario_info(scenario_name: str) -> Dict[str, Any]:
    """Get basic information about a scenario.

    Args:
        scenario_name: Slash-separated key (e.g. 'AssetBubble/Rule')

    Returns:
        Dict with name, display_name, description, is_llm, config_path
    """
    config_path = _configs_path(scenario_name) / "simulation.yml"
    variant = scenario_name.split("/")[-1] if "/" in scenario_name else ""

    info = {
        "name": scenario_name,
        "display_name": scenario_display_name(scenario_name),
        "description": "",
        "is_llm": variant in ("LLM", "RuleLLM", "Rag"),
        "config_path": str(config_path),
        "exists": config_path.exists(),
    }

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Strip !include directives so yaml.safe_load doesn't choke
            lines = []
            for line in content.split("\n"):
                if "!include" in line:
                    key = line.split(":")[0]
                    lines.append(f"{key}: {{}}")
                else:
                    lines.append(line)
            config = yaml.safe_load("\n".join(lines))
            if config and "setting" in config:
                info["description"] = config["setting"].get("description", "")
                info["total_rounds"] = config["setting"].get("total_rounds", 0)
                info["record_path"] = config["setting"].get("record_path", "")
        except Exception as e:
            logger.warning("Failed to parse scenario config %s: %s", config_path, e)

    return info


def load_players_config(scenario_name: str) -> Dict[str, Any]:
    """Load players configuration for a scenario.

    Args:
        scenario_name: Name of the scenario directory

    Returns:
        Dict mapping player type to configuration
    """
    players_path = _configs_path(scenario_name) / "players.yml"

    if not players_path.exists():
        return {}

    try:
        with open(players_path, "r", encoding="utf-8") as f:
            # Simple YAML load - doesn't handle !include tags
            content = f.read()
            # Remove !include directives for basic parsing
            lines = []
            for line in content.split("\n"):
                if "!include" in line:
                    # Keep the key, remove the include
                    line = line.split("!include")[0].rstrip() + ": {}"
                lines.append(line)
            return yaml.safe_load("\n".join(lines)) or {}
    except Exception as e:
        print(f"Error loading players config: {e}")
        return {}


# ---------------------------------------------------------------------------
# Agent theory tags — the core academic concept each agent embodies
# ---------------------------------------------------------------------------
_AGENT_THEORIES: Dict[str, str] = {
    # Coordinator
    "Market": "Order-clearing mechanism",
    # AssetBubble
    "MomentumSpeculator": "Greater Fool Theory",
    "RationalArbitrageur": "Limits to Arbitrage",
    "NoiseTrader": "Noise Trader Risk",
    "FundamentalInvestor": "Fundamental Valuation",
    "LeveragedBuyer": "Margin Amplification",
    "ConservativeHolder": "Passive Buy-and-Hold",
    "LLMGreaterFoolSpeculator": "Greater Fool Theory",
    "LLMRationalArbitrageur": "Limits to Arbitrage",
    "LLMSentimentTrader": "Noise Trader Risk",
    "LLMValueInvestor": "Fundamental Valuation",
    "LLMLeveragedSpeculator": "Margin Amplification",
    # AssetBubbleRuleLLM (Hybrid Rule + LLM)
    "RuleLLMMomentumSpeculator": "Greater Fool Theory",
    "RuleLLMRationalArbitrageur": "Limits to Arbitrage",
    "RuleLLMNoiseTrader": "Noise Trader Risk",
    "RuleLLMValueInvestor": "Fundamental Valuation",
    "RuleLLMLeveragedBuyer": "Margin Amplification",
    # AssetBubbleRag (RAG + LLM)
    "RagLLMMomentumSpeculator": "Greater Fool Theory",
    "RagLLMRationalArbitrageur": "Limits to Arbitrage",
    "RagLLMNoiseTrader": "Noise Trader Risk",
    "RagLLMValueInvestor": "Fundamental Valuation",
    "RagLLMLeveragedBuyer": "Margin Amplification",
    # MarketCrash
    "RiskParityFund": "Risk Parity / Deleveraging",
    "LeveragedHedgeFund": "Leverage Cycle Theory",
    "MarketMaker": "Inventory Risk Model",
    "PassiveInvestor": "Passive Index Investing",
    "PanicSeller": "Loss Aversion / Threshold Selling",
    "BottomFisher": "Contrarian Value Investing",
    "LLMPanicSeller": "Loss Aversion / Threshold Selling",
    "LLMRiskParityFund": "Risk Parity / Deleveraging",
    "LLMLeveragedFund": "Leverage Cycle Theory",
    "LLMMarketMaker": "Inventory Risk Model",
    "LLMBottomFisher": "Contrarian Value Investing",
    # HerdEffect
    "MomentumInvestor": "Social Learning / Herding",
    "ContrarianInvestor": "Anti-Herding / Contrarianism",
    "RiskAverseInvestor": "Mean-Variance Optimisation",
    "AggressiveInvestor": "Overconfidence Bias",
    # MomentumEffect
    "MomentumTrader": "Momentum Premium (Jegadeesh & Titman)",
    "ContrarianTrader": "Mean Reversion / DeBondt-Thaler",
    "IndexFund": "Passive Benchmark",
    "TechnicalTrader": "Technical Analysis",
    "FundamentalTrader": "Fundamental Valuation",
    # ReversalEffect
    "OverconfidentTrader": "Overconfidence Bias",
    "ValueInvestor": "Fundamental Valuation",
    "LLMContrarianInvestor": "Mean Reversion / DeBondt-Thaler",
    "LLMOverconfidentTrader": "Overconfidence Bias",
    "LLMMomentumChaser": "Momentum Premium",
    "LLMNoiseTrader": "Noise Trader Risk",
    # FlashCrash
    "HighFrequencyTrader": "High-Frequency Trading",
    "AlgorithmicTrader": "Algorithmic Execution",
    "StopLossTrader": "Stop-Loss Cascade",
    "RetailTrader": "Retail Investor Behaviour",
    "LLMHighFrequencyTrader": "High-Frequency Trading",
    "LLMFlashMarketMaker": "Inventory Risk Model",
    "LLMStopLossTrader": "Stop-Loss Cascade",
    "LLMFundamentalTrader": "Fundamental Valuation",
    "LLMAlgorithmicTrader": "Algorithmic Execution",
    # VolatilityClustering
    "Fundamentalist": "Fundamental Valuation",
    "TrendFollower": "Chartist / Trend Extrapolation",
    "SlowAdapter": "Adaptive Expectations",
    "VolatilityTrader": "GARCH Volatility Trading",
    "LLMFundamentalist": "Fundamental Valuation",
    "LLMTrendFollower": "Chartist / Trend Extrapolation",
    "LLMSlowAdapter": "Adaptive Expectations",
    "LLMVolatilityTrader": "GARCH Volatility Trading",
    # DispositionEffect
    "DispositionInvestor": "Prospect Theory (Kahneman-Tversky)",
    "RationalInvestor": "Expected Utility Theory",
    "TaxAwareInvestor": "Tax-Loss Harvesting",
    "IndexHolder": "Passive Buy-and-Hold",
    "InstitutionalInvestor": "Professional Discipline",
    "LLMDispositionBiased": "Prospect Theory (Kahneman-Tversky)",
    "LLMRationalInvestor": "Expected Utility Theory",
    "LLMTaxAwareInvestor": "Tax-Loss Harvesting",
    "LLMInstitutionalInvestor": "Professional Discipline",
    "LLMLossAverse": "Loss Aversion (Kahneman-Tversky)",
    # DispositionEffectRuleLLM
    "RuleLLMDispositionBiased": "Prospect Theory (Kahneman-Tversky)",
    "RuleLLMRationalInvestor": "Expected Utility Theory",
    "RuleLLMTaxAwareInvestor": "Tax-Loss Harvesting",
    "RuleLLMInstitutionalInvestor": "Professional Discipline",
    "RuleLLMLossAverse": "Loss Aversion (Kahneman-Tversky)",
    # HerdEffectRuleLLM
    "RuleLLMMomentumInvestor": "Momentum Premium (Jegadeesh & Titman)",
    "RuleLLMContrarianInvestor": "Mean Reversion / DeBondt-Thaler",
    "RuleLLMRiskAverseInvestor": "Mean-Variance Optimisation",
    "RuleLLMAggressiveInvestor": "Overconfidence Bias",
    "RuleLLMNoiseTrader": "Noise Trader Risk",
    # EquityPremium
    "MyopicLossAverseInvestor": "Myopic Loss Aversion (Benartzi-Thaler)",
    "LongHorizonInvestor": "Long-Horizon Risk Diversification",
    "RiskNeutralInvestor": "Expected Value Maximisation",
    "ConservativeInvestor": "Mean-Variance Optimisation",
    # LiquidityDryup
    "LiquiditySeeker": "Liquidity Demand Shock",
    "ValueTrader": "Liquidity Supply / Arbitrage",
    # ShortSqueeze
    "ShortSeller": "Short Selling / Negative Outlook",
    "MomentumBuyer": "Momentum Premium",
    "InstitutionalHolder": "Float Reduction Mechanism",
}


def get_agent_theory(class_name: str) -> str:
    """Return the core academic theory tag for an agent class.

    Args:
        class_name: Class name extracted after ':' from players.yml

    Returns:
        Short theory label string, or empty string if unknown
    """
    return _AGENT_THEORIES.get(
        class_name,
        _AGENT_THEORIES.get(class_name.replace("LLM", "", 1), ""),
    )


def get_docs_content(scenario_name: str) -> Optional[str]:
    """Read the explain.md file for a scenario.

    Args:
        scenario_name: Name of the scenario directory

    Returns:
        Full markdown string, or None if file not found
    """
    docs_path = _examples_path(scenario_name) / "explain.md"
    if not docs_path.exists():
        return None
    try:
        return docs_path.read_text(encoding="utf-8")
    except Exception:
        return None


def _scenario_base(scenario_key: str) -> str:
    """Return the base scenario name for a scenario key.

    Examples:
        'AssetBubble/Rule' -> 'AssetBubble'
        'AssetBubble'      -> 'AssetBubble'
        'myproj/AssetBubble/Rule' -> 'AssetBubble' (project-prefixed key)
        'CUSTOMIZED_SIMULATION/{slug}-{id}-AssetBubble/Customized-agents'
            -> 'AssetBubble'
        'CUSTOMIZED_SIMULATION/Default-AssetBubble-LLM-r5' -> 'AssetBubble'

    Customized bundle keys are resolved through ``_resolve_display_key``
    first so the caller lands on the shipped scenario directory (e.g.
    ``examples/AssetBubble/``) instead of on a nonexistent
    ``examples/Customized-agents/`` path.
    """
    if not scenario_key:
        return scenario_key
    key = _resolve_display_key(scenario_key)
    parts = key.split("/")
    # Strip trailing variant if present (Rule/LLM/RuleLLM/Rag)
    if parts[-1] in ("Rule", "LLM", "RuleLLM", "Rag"):
        parts = parts[:-1]
    return parts[-1] if parts else key


def _customized_bundle_bases_path(
    scenario_key: str, filename: str
) -> Optional[Path]:
    """Return the bundle-local bases file for a customized scenario, if any.

    Customized bundles ship their own copies of ``simulation-bases.md`` /
    ``analysis-bases.md`` under
    ``examples/CUSTOMIZED_SIMULATION/{bundle}/{sub}/{filename}`` where
    ``{sub}`` is ``Default`` or ``Customized-agents``. The bundle-local
    copy is preferred because it survives even if the shipped scenario
    is later archived, and it reflects any bundle-time snapshots.
    """
    if not scenario_key.startswith("CUSTOMIZED_SIMULATION/"):
        return None
    tail = scenario_key.split("/", 1)[1]
    tail_parts = tail.split("/")
    if len(tail_parts) < 2:
        return None
    bundle_name, sub = tail_parts[0], tail_parts[1]
    if sub not in ("Default", "Customized-agents"):
        return None
    candidate = (
        EXAMPLES_DIR / "CUSTOMIZED_SIMULATION" / bundle_name / sub / filename
    )
    return candidate if candidate.exists() else None


def get_simulation_bases_path(scenario_key: str) -> Optional[Path]:
    """Return the path to a scenario's simulation-bases.md, or None.

    Resolution order:
      1. Customized bundles: check the bundle-local copy under
         ``examples/CUSTOMIZED_SIMULATION/{bundle}/{sub}/`` first.
      2. Shipped scenarios: fall back to the canonical
         ``examples/{ScenarioBase}/simulation-bases.md``.

    The lookup is variant-agnostic and project-agnostic: only the base
    scenario name (extracted via :func:`_scenario_base`) is used.
    """
    bundle_local = _customized_bundle_bases_path(
        scenario_key, "simulation-bases.md"
    )
    if bundle_local is not None:
        return bundle_local
    base = _scenario_base(scenario_key)
    candidate = EXAMPLES_DIR / base / "simulation-bases.md"
    return candidate if candidate.exists() else None


def get_simulation_bases_content(scenario_key: str) -> Optional[str]:
    """Return the full markdown text of ``simulation-bases.md`` or None."""
    path = get_simulation_bases_path(scenario_key)
    if path is None:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def get_analysis_bases_path(scenario_key: str) -> Optional[Path]:
    """Return the path to a scenario's analysis-bases.md, or None.

    Resolution order:
      1. Customized bundles: check the bundle-local copy under
         ``examples/CUSTOMIZED_SIMULATION/{bundle}/{sub}/`` first.
      2. Shipped scenarios: fall back to the canonical
         ``examples/{ScenarioBase}/analysis-bases.md``.

    The lookup is variant-agnostic and project-agnostic: only the base
    scenario name (extracted via :func:`_scenario_base`) is used.
    """
    bundle_local = _customized_bundle_bases_path(
        scenario_key, "analysis-bases.md"
    )
    if bundle_local is not None:
        return bundle_local
    base = _scenario_base(scenario_key)
    candidate = EXAMPLES_DIR / base / "analysis-bases.md"
    return candidate if candidate.exists() else None


def get_analysis_bases_content(scenario_key: str) -> Optional[str]:
    """Return the full markdown text of ``analysis-bases.md`` or None."""
    path = get_analysis_bases_path(scenario_key)
    if path is None:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def get_phenomenon_description(scenario_key: str) -> str:
    """Extract the ``Phenomenon Name`` cell from ``simulation-bases.md``.

    The canonical simulation-bases.md opens with a table whose first row
    is ``| Phenomenon Name | <bold-name> \u2014 <clear description> |``.
    This function returns just the value cell, stripped of markdown
    formatting, so callers can render a brief, human-readable scenario
    description. Returns an empty string when the field is not found.
    """
    content = get_simulation_bases_content(scenario_key)
    if not content:
        return ""
    # Match the row: |  Phenomenon Name  |  <value>  |
    match = re.search(
        r"^\|\s*Phenomenon\s+Name\s*\|\s*(.+?)\s*\|\s*$",
        content,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    if not match:
        return ""
    text = match.group(1).strip()
    # Strip bold markdown (**text**) and stray backticks.
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = text.replace("`", "")
    return text.strip()


def get_finance_scenario_path(scenario_key: str) -> Optional[Path]:
    """Return the path to a scenario's ``finance-{name}.md``, or None.

    The finance file lives at
    ``examples/{ScenarioBase}/finance-{name}.md`` and is the target-spec
    / reverse-reconstructed scenario definition (produced by
    ``polish-simulation-pipeline`` / ``define-simulation-scenario-skill``).
    Filename casing is inconsistent across scenarios, so this helper tries
    a few variants in order:

    1. Kebab-case from CamelCase (e.g. ``AnchoringEffect`` \u2192
       ``finance-anchoring-effect.md``).
    2. All-lowercase with no hyphens (e.g. ``ShortSqueeze`` \u2192
       ``finance-shortsqueeze.md``).
    3. Any ``finance-*.md`` file found in the scenario directory
       (first match, alphabetically) as a defensive fallback.
    """
    base = _scenario_base(scenario_key)
    scenario_dir = EXAMPLES_DIR / base
    if not scenario_dir.exists():
        return None
    # Kebab-case: split CamelCase and letter-digit boundaries with '-'.
    kebab = re.sub(
        r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|(?<=[A-Za-z])(?=[0-9])",
        "-",
        base,
    ).lower()
    candidate = scenario_dir / f"finance-{kebab}.md"
    if candidate.exists():
        return candidate
    # All-lowercase fallback (e.g. finance-shortsqueeze.md).
    lower_candidate = scenario_dir / f"finance-{base.lower()}.md"
    if lower_candidate.exists():
        return lower_candidate
    # Last-resort glob (picks up any unforeseen naming variant).
    matches = sorted(scenario_dir.glob("finance-*.md"))
    return matches[0] if matches else None


def get_finance_scenario_content(scenario_key: str) -> Optional[str]:
    """Return the full markdown text of ``finance-{scenario}.md`` or None."""
    path = get_finance_scenario_path(scenario_key)
    if path is None:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Agent principle descriptions (keyed by class name suffix after ':')
# Covers all rule-based and LLM variants across every scenario
# ---------------------------------------------------------------------------
_AGENT_PRINCIPLES: Dict[str, str] = {
    # Coordinator
    "Market": "Rule-based price-clearing coordinator that sets market price each round",
    # AssetBubble / AssetBubbleLLM
    "MomentumSpeculator": "Chases price trends aggressively; primary bubble driver (destabilising)",
    "RationalArbitrageur": "Sells short on overvaluation; limited by capital constraints (weak stabilising)",
    "NoiseTrader": "Follows sentiment and recent returns; amplifies herd behaviour (destabilising)",
    "FundamentalInvestor": "Buys/sells based on intrinsic value; slow to act (weak stabilising)",
    "LeveragedBuyer": "Uses margin to amplify long positions; margin-call risk (strongly destabilising)",
    "ConservativeHolder": "Holds long-term target positions; rebalances slowly (very weak stabilising)",
    "LLMGreaterFoolSpeculator": "LLM-driven greater-fool speculator riding price momentum into the bubble",
    "LLMRationalArbitrageur": "LLM-driven arbitrageur exploiting fundamental mispricings with limited capital",
    "LLMSentimentTrader": "LLM-driven trader reacting to market sentiment and narrative signals",
    "LLMValueInvestor": "LLM-driven value investor anchoring on fundamental worth",
    "LLMLeveragedSpeculator": "LLM-driven speculator using leverage to amplify returns (and losses)",
    # AssetBubbleRuleLLM (Hybrid Rule + LLM)
    "RuleLLMMomentumSpeculator": "Hybrid rule+LLM speculator following momentum formulas with qualitative adjustments",
    "RuleLLMRationalArbitrageur": "Hybrid rule+LLM arbitrageur exploiting mispricings with cost-aware reasoning",
    "RuleLLMNoiseTrader": "Hybrid rule+LLM trader following sentiment signals with herding adjustments",
    "RuleLLMValueInvestor": "Hybrid rule+LLM value investor trading infrequently on fundamental deviation",
    "RuleLLMLeveragedBuyer": "Hybrid rule+LLM leveraged buyer with margin-call awareness in reasoning",
    # AssetBubbleRag (RAG + LLM)
    "RagLLMMomentumSpeculator": "RAG-augmented momentum speculator retrieving relevant trading knowledge",
    "RagLLMRationalArbitrageur": "RAG-augmented arbitrageur with knowledge-grounded mispricing analysis",
    "RagLLMNoiseTrader": "RAG-augmented noise trader informed by retrieved sentiment research",
    "RagLLMValueInvestor": "RAG-augmented value investor using fundamental analysis literature",
    "RagLLMLeveragedBuyer": "RAG-augmented leveraged buyer with risk management knowledge retrieval",
    # MarketCrash / MarketCrashLLM
    "RiskParityFund": "Balances risk across asset classes; forced deleveraging triggers cascade",
    "LeveragedHedgeFund": "High-leverage positions; margin calls accelerate crash dynamics",
    "MarketMaker": "Provides two-sided quotes; inventory risk forces price concessions",
    "PassiveInvestor": "Index-tracking; systematic outflows amplify crash momentum",
    "PanicSeller": "Liquidates on loss thresholds; positive feedback into crash",
    "BottomFisher": "Buys on deep dips; acts as a partial stabiliser at extremes",
    "LLMPanicSeller": "LLM-driven panic seller with loss-aversion bias",
    "LLMRiskParityFund": "LLM-driven risk-parity fund managing cross-asset volatility exposure",
    "LLMLeveragedFund": "LLM-driven leveraged fund amplifying market swings",
    "LLMMarketMaker": "LLM-driven market maker managing bid-ask spread and inventory",
    "LLMBottomFisher": "LLM-driven contrarian buyer at market lows",
    # HerdEffect
    "MomentumInvestor": "Follows recent price trends; amplifies herding cascades",
    "ContrarianInvestor": "Bets against consensus; provides weak mean-reversion pressure",
    "RiskAverseInvestor": "Reduces exposure during volatility spikes; adds stability",
    "AggressiveInvestor": "Large position sizes with high conviction; amplifies moves",
    # MomentumEffect / MomentumEffectLLM
    "MomentumTrader": "Buys winners and sells losers based on recent returns",
    "ContrarianTrader": "Fades momentum; profits from mean-reversion episodes",
    "IndexFund": "Passive buy-and-hold benchmark; no active signal",
    "TechnicalTrader": "Uses moving averages and chart patterns to time entries",
    "FundamentalTrader": "Trades on earnings/valuation signals; long-horizon view",
    # ReversalEffect / ReversalEffectLLM
    "OverconfidentTrader": "Over-extrapolates recent returns; creates reversal opportunities",
    "ValueInvestor": "Patient buyer of undervalued assets; anchors long-run prices",
    "LLMContrarianInvestor": "LLM-driven contrarian fading recent overreactions",
    "LLMOverconfidentTrader": "LLM-driven overconfident trader prone to excessive extrapolation",
    "LLMMomentumChaser": "LLM-driven momentum chaser riding short-term price trends",
    "LLMNoiseTrader": "LLM-driven noise trader injecting random price pressure",
    # FlashCrash / FlashCrashLLM
    "HighFrequencyTrader": "Sub-millisecond quote updates; can trigger liquidity withdrawal",
    "AlgorithmicTrader": "Rule-based algo triggered by price/volume signals",
    "StopLossTrader": "Automatic exit on loss threshold; cascades price drops",
    "RetailTrader": "Individual investor with delayed reaction; amplifies aftermath",
    "LLMHighFrequencyTrader": "LLM-driven HFT responding to order-book imbalances",
    "LLMFlashMarketMaker": "LLM-driven market maker pulling quotes under stress",
    "LLMStopLossTrader": "LLM-driven stop-loss trader with configurable exit thresholds",
    "LLMFundamentalTrader": "LLM-driven fundamental trader stabilising after crash",
    "LLMAlgorithmicTrader": "LLM-driven algorithmic trader using quantitative signals",
    # VolatilityClustering / VolatilityClusteringLLM
    "Fundamentalist": "Reverts to fundamental value; dampens excess volatility",
    "TrendFollower": "Extrapolates trends; amplifies volatility clustering",
    "SlowAdapter": "Gradual belief update; lagged response creates persistence",
    "VolatilityTrader": "Explicitly trades on realised vs. implied volatility spreads",
    "LLMFundamentalist": "LLM-driven fundamentalist with value-anchoring reasoning",
    "LLMTrendFollower": "LLM-driven trend follower interpreting price narratives",
    "LLMSlowAdapter": "LLM-driven slow adapter updating beliefs gradually",
    "LLMVolatilityTrader": "LLM-driven volatility trader calibrating exposure to vol regime",
    # DispositionEffect / DispositionEffectLLM
    "DispositionInvestor": "Sells winners too early and holds losers too long (prospect theory)",
    "RationalInvestor": "Maximises expected utility; no disposition bias",
    "TaxAwareInvestor": "Harvests tax losses; rational selling of losers",
    "IndexHolder": "Passive index holder; no active trading bias",
    "InstitutionalInvestor": "Large-scale disciplined trader with risk limits",
    "LLMDispositionBiased": "LLM investor exhibiting prospect-theory disposition bias in reasoning",
    "LLMRationalInvestor": "LLM investor applying expected-utility maximisation",
    "LLMTaxAwareInvestor": "LLM investor optimising after-tax portfolio returns",
    "LLMInstitutionalInvestor": "LLM-driven institutional investor with mandate constraints",
    "LLMLossAverse": "LLM investor with strong loss aversion; holds losers, books gains",
    # DispositionEffectRuleLLM
    "RuleLLMDispositionBiased": "Hybrid rule+LLM investor following embedded disposition effect formulas",
    "RuleLLMRationalInvestor": "Hybrid rule+LLM investor with systematic rebalancing rules",
    "RuleLLMTaxAwareInvestor": "Hybrid rule+LLM investor applying tax-loss harvesting formulas",
    "RuleLLMInstitutionalInvestor": "Hybrid rule+LLM institutional investor with symmetric thresholds",
    "RuleLLMLossAverse": "Hybrid rule+LLM investor with extreme loss aversion embedded rules",
    # HerdEffectRuleLLM
    "RuleLLMMomentumInvestor": "Hybrid rule+LLM momentum investor following trend formulas",
    "RuleLLMContrarianInvestor": "Hybrid rule+LLM contrarian applying mean-reversion rules",
    "RuleLLMRiskAverseInvestor": "Hybrid rule+LLM investor with variance-adjusted position sizing",
    "RuleLLMAggressiveInvestor": "Hybrid rule+LLM aggressive investor with acceleration bonus",
    "RuleLLMNoiseTrader": "Hybrid rule+LLM noise trader with random trading rules",
    # EquityPremium / EquityPremiumLLM
    "MyopicLossAverseInvestor": "Evaluates P&L at short horizons; demands high equity premium",
    "LongHorizonInvestor": "Patient investor; sees lower loss probability over long run",
    "RiskNeutralInvestor": "Evaluates expected return only; no risk premium required",
    "ConservativeInvestor": "Prefers low-volatility assets; shifts to bonds under uncertainty",
    # LiquidityDryup / LiquidityDryupLLM
    "LiquiditySeeker": "Demands immediate execution; exacerbates dryups under stress",
    "ValueTrader": "Provides liquidity at dislocated prices; partial stabiliser",
    # ShortSqueeze / ShortSqueezeLLM
    "ShortSeller": "Borrows and sells shares expecting decline; forced to cover on squeeze",
    "MomentumBuyer": "Buys rising assets; accelerates squeeze as shorts cover",
    "RetailTrader": "Individual trader; coordinated retail buying triggers squeezes",
    "InstitutionalHolder": "Long-term holder; reduces float and amplifies squeeze dynamics",
}


def get_agents_info(scenario_name: str) -> List[Dict[str, Any]]:
    """Get information about all agents in a scenario.

    Args:
        scenario_name: Name of the scenario directory

    Returns:
        List of agent info dicts with name, class, instances, role, params, principle
    """
    players = load_players_config(scenario_name)
    agents = []

    for player_id, config in players.items():
        if not isinstance(config, dict):
            continue

        class_str = config.get("class", "")
        # Extract the class name after the last ':'
        class_name = class_str.split(":")[-1] if ":" in class_str else class_str
        # Strip LLM prefix for principle lookup (LLMFoo -> Foo also checked)
        principle = _AGENT_PRINCIPLES.get(
            class_name,
            _AGENT_PRINCIPLES.get(class_name.replace("LLM", "", 1), ""),
        )
        theory = get_agent_theory(class_name)

        agent_info = {
            "id": player_id,
            "name": config.get("name", player_id),
            "class": class_str,
            "instances": config.get("num_instances", 1),
            "role": "coordinator" if player_id == "market" else "player",
            "principle": principle,
            "theory": theory,
            "params": {},
        }

        # Extract key parameters from extras
        if "config" in config and isinstance(config["config"], dict):
            extras = config["config"].get("extras", {})
            if isinstance(extras, dict):
                # Filter to interesting params
                interesting_keys = [
                    "aggressiveness",
                    "leverage_multiplier",
                    "leverage_ratio",
                    "sentiment_volatility",
                    "herding_weight",
                    "deviation_threshold",
                    "trade_frequency",
                    "value_sensitivity",
                    "lookback_short",
                    "base_position_size",
                    "target_position",
                    "rebalance_frequency",
                ]
                agent_info["params"] = {
                    k: v
                    for k, v in extras.items()
                    if k in interesting_keys and not k.endswith("_path")
                }

        agents.append(agent_info)

    return agents


def get_agent_roster(scenario_name: str) -> List[Dict[str, Any]]:
    """Return the full list of concrete agent instances for a scenario.

    Mirrors ``expand_player_instances`` in ``masim/utils/config.py`` so the
    instance ids match the simulator's ``sender_id`` values:
      * ``num_instances == 1`` -> instance id = base key (unchanged)
      * ``num_instances  > 1`` -> instance ids = ``base_1`` ... ``base_N``

    The market coordinator is excluded. Used by the simulation page to render
    every configured investor each round (non-trading ones shown as HOLD),
    so the activity panel matches the sidebar roster.

    Returns:
        List of dicts with keys ``id``, ``name``, ``base``.
    """
    players = load_players_config(scenario_name)
    roster: List[Dict[str, Any]] = []

    for base_key, config in players.items():
        if not isinstance(config, dict):
            continue
        if base_key == "market":
            continue
        role = ""
        if "config" in config and isinstance(config["config"], dict):
            role = config["config"].get("role", "")
        if role == "coordinator":
            continue

        name = config.get("name", base_key)
        try:
            n = int(config.get("num_instances", 1) or 1)
        except (TypeError, ValueError):
            n = 1

        if n <= 1:
            roster.append({"id": base_key, "name": name, "base": base_key})
        else:
            for i in range(1, n + 1):
                roster.append(
                    {"id": f"{base_key}_{i}", "name": f"{name} {i}", "base": base_key}
                )

    return roster


def check_simulation_results(scenario_name: str) -> bool:
    """Check if simulation results exist for a scenario.

    Args:
        scenario_name: Name of the scenario directory

    Returns:
        True if results exist and can be analyzed
    """
    info = get_scenario_info(scenario_name)
    if not info.get("record_path"):
        return False

    record_path = _PROJECT_ROOT / info["record_path"]
    return record_path.exists() and any(record_path.iterdir())


def get_diagram_path(scenario_name: str) -> Optional[Path]:
    """Find the topology diagram PNG saved by the simulator.

    The simulator saves diagrams to:
      EXPERIMENT/{scenario}/records/diagrams/topology_r*.png

    Args:
        scenario_name: Name of the scenario directory

    Returns:
        Path to the latest topology PNG, or None if not found
    """
    scenario_name = _resolve_display_key(scenario_name)
    diagram_dir = _experiment_path(scenario_name) / "records" / "diagrams"
    if not diagram_dir.exists():
        return None
    # Take the first available topology PNG (typically only one)
    pngs = sorted(diagram_dir.glob("topology_*.png"))
    return pngs[0] if pngs else None


def get_topology_info(scenario_name: str) -> Dict[str, Any]:
    """Parse topology.yml to get connection graph for diagram rendering.

    Args:
        scenario_name: Name of the scenario directory

    Returns:
        Dict with topology_type, sources, connections (node -> [targets])
    """
    scenario_name = _resolve_display_key(scenario_name)
    topology_path = _configs_path(scenario_name) / "topology.yml"

    result: Dict[str, Any] = {
        "topology_type": "star",
        "sources": [],
        "connections": {},
        "nodes": [],
    }

    if not topology_path.exists():
        return result

    try:
        with open(topology_path, "r", encoding="utf-8") as f:
            topo = yaml.safe_load(f)

        if not topo:
            return result

        result["topology_type"] = topo.get("type", "star")
        result["sources"] = topo.get("sources", [])
        connections = topo.get("connections", {})
        result["connections"] = connections

        # Collect all unique node names
        nodes = set(result["sources"])
        for src, targets in connections.items():
            nodes.add(src)
            if isinstance(targets, list):
                nodes.update(targets)
        result["nodes"] = sorted(nodes)

    except Exception as e:
        print(f"Error loading topology: {e}")

    return result


# Short market description for each scenario — what investors are doing
_SCENARIO_MARKET_DESCRIPTIONS: Dict[str, str] = {
    "AssetBubble": (
        "Investors trade a single risky equity. Speculators and leveraged buyers "
        "chase price momentum, gradually inflating a bubble, while rational "
        "arbitrageurs attempt limited short-selling to correct the overvaluation."
    ),
    "AssetBubbleLLM": (
        "LLM-driven investors trade a single risky equity. Greater-fool speculators "
        "ride the bubble narrative, leveraged players amplify it, and value-anchored "
        "agents try to resist — testing whether LLM reasoning reproduces bubble dynamics."
    ),
    "AssetBubbleRuleLLM": (
        "Hybrid rule+LLM investors trade with embedded quantitative rules. Each agent "
        "follows explicit financial formulas (momentum, deviation, sentiment) while "
        "using LLM reasoning for qualitative context — combining rule precision with "
        "language understanding."
    ),
    "AssetBubbleRag": (
        "RAG-augmented LLM investors retrieve relevant financial knowledge before "
        "deciding. Each agent queries a knowledge base of trading literature, grounding "
        "decisions in retrieved context — testing whether external knowledge improves "
        "trading behavior and bubble dynamics."
    ),
    "MarketCrash": (
        "Investors hold a diversified portfolio. Risk-parity funds and leveraged hedge "
        "funds delever simultaneously under stress, panic sellers exit at thresholds, "
        "and bottom fishers attempt to stabilise prices at extremes."
    ),
    "MarketCrashLLM": (
        "LLM investors manage portfolios under market stress. Panic sellers and leveraged "
        "funds react to losses in natural language, while bottom fishers assess value — "
        "probing whether LLM agents exhibit contagion and recovery patterns."
    ),
    "HerdEffect": (
        "Investors observe peers' trading decisions and market price. Momentum investors "
        "copy recent winners, contrarians fade the crowd, and noise traders add random "
        "pressure — creating waves of synchronised herd behaviour."
    ),
    "HerdEffectLLM": (
        "LLM investors read market narratives and peer signals. The simulation tests "
        "whether language-model reasoning leads to emergent herding or independent "
        "judgment under social influence."
    ),
    "MomentumEffect": (
        "Investors trade based on past return signals. Momentum traders buy recent "
        "winners and sell losers, contrarian traders fade them, and index funds provide "
        "a passive benchmark — measuring return autocorrelation and momentum persistence."
    ),
    "MomentumEffectLLM": (
        "LLM investors interpret price history narratives. The simulation tests whether "
        "LLM-driven momentum chasers generate the same return persistence and eventual "
        "reversal as rule-based counterparts."
    ),
    "ReversalEffect": (
        "Investors trade on mean-reversion signals after extreme moves. Contrarians buy "
        "oversold stocks and sell overbought ones, while overconfident traders "
        "over-extrapolate trends — creating the conditions for price reversals."
    ),
    "ReversalEffectLLM": (
        "LLM investors reason about overreaction and fair value. The simulation tests "
        "whether LLM contrarians correctly identify and exploit mean-reversion "
        "opportunities generated by overconfident LLM traders."
    ),
    "FlashCrash": (
        "High-frequency traders and algorithmic market makers interact in a fast "
        "order-book environment. Stop-loss cascades and HFT liquidity withdrawal "
        "combine to trigger a sudden, deep price crash followed by rapid recovery."
    ),
    "FlashCrashLLM": (
        "LLM-driven HFTs and market makers respond to rapid order-flow signals in "
        "natural language. The simulation tests whether LLM speed-of-reasoning and "
        "risk thresholds reproduce the flash crash and recovery pattern."
    ),
    "VolatilityClustering": (
        "Investors with heterogeneous belief-update speeds trade a single asset. "
        "Trend followers amplify volatility, fundamentalists dampen it, and slow "
        "adapters create persistence — producing GARCH-like volatility clustering."
    ),
    "VolatilityClusteringLLM": (
        "LLM investors update beliefs about market regime at different speeds. "
        "The simulation tests whether language-model reasoning reproduces the "
        "volatility clustering and regime persistence observed in real markets."
    ),
    "EquityPremium": (
        "Investors choose between a risky stock and a risk-free bond each round. "
        "Myopic loss-averse investors demand a high equity premium due to short "
        "evaluation horizons, while long-horizon patients require far less."
    ),
    "EquityPremiumLLM": (
        "LLM investors decide between stocks and bonds using loss-aversion reasoning. "
        "The simulation tests whether LLM myopic framing generates an equity premium "
        "as large as that observed in rule-based models and real markets."
    ),
    "DispositionEffect": (
        "Investors manage a portfolio of stocks with varying purchase prices. "
        "Disposition-biased traders sell winners too early and hold losers too long, "
        "while rational and tax-aware agents trade to maximise after-tax returns."
    ),
    "DispositionEffectLLM": (
        "LLM investors track personal cost bases and make sell decisions in natural "
        "language. The simulation tests whether LLM reasoning reproduces the "
        "prospect-theory disposition effect seen in real retail investors."
    ),
    "DispositionEffectRuleLLM": (
        "Hybrid rule+LLM investors follow embedded quantitative disposition rules "
        "while using LLM reasoning for qualitative adjustments. Each agent computes "
        "gain/loss relative to reference point and applies prospect-theory formulas "
        "with natural language context — combining rule precision with LLM flexibility."
    ),
    "HerdEffectRuleLLM": (
        "Hybrid rule+LLM investors follow embedded momentum, contrarian, and volatility "
        "formulas while using LLM reasoning for market context. The simulation tests "
        "whether herding behavior emerges from agents following explicit trend-following "
        "and mean-reversion rules enhanced by qualitative judgment."
    ),
    "LiquidityDryup": (
        "Market makers provide bid-ask liquidity while informed traders and liquidity "
        "seekers consume it. Under stress, market makers widen spreads or withdraw, "
        "causing a sudden collapse in available liquidity."
    ),
    "LiquidityDryupLLM": (
        "LLM market makers and traders negotiate liquidity in natural language. "
        "The simulation tests whether LLM-driven market makers reduce quotes under "
        "stress, reproducing the liquidity dry-up pattern."
    ),
    "ShortSqueeze": (
        "Short sellers have borrowed and sold shares expecting a decline. When "
        "momentum buyers and coordinated retail traders push prices up, short "
        "sellers are forced to buy back — amplifying the price spike."
    ),
    "ShortSqueezeLLM": (
        "LLM short sellers and momentum buyers reason about price pressure in natural "
        "language. The simulation tests whether LLM agents reproduce the forced-covering "
        "feedback loop characteristic of real short squeezes."
    ),
}


def get_market_description(scenario_name: str) -> str:
    """Return a short description of the market dynamics for a scenario.

    Args:
        scenario_name: Slash-separated key or legacy flat name

    Returns:
        Human-readable market description string
    """
    scenario_name = _resolve_display_key(scenario_name)
    flat = _flat_scenario_name(scenario_name)
    # Fallback: strip LLM/RuleLLM suffix
    base = flat[:-3] if flat.endswith("LLM") else flat
    return _SCENARIO_MARKET_DESCRIPTIONS.get(
        flat,
        _SCENARIO_MARKET_DESCRIPTIONS.get(base, ""),
    )


def _load_players_yml_lenient(scenario_key: str) -> Dict[str, Any]:
    """Load configs/{scenario}/{variant}/players.yml with !include tolerance.

    The players.yml files use `!include persona.yml` tags that PyYAML's
    SafeLoader rejects. This helper installs a null constructor so we can
    still read scalar keys like `archetype:` from within the market block.
    Returns an empty dict on any error.
    """
    p = _configs_path(scenario_key) / "players.yml"
    if not p.exists():
        return {}

    class _Loader(yaml.SafeLoader):
        pass

    _Loader.add_constructor("!include", lambda loader, node: None)
    _Loader.add_multi_constructor("", lambda loader, tag_suffix, node: None)
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = yaml.load(f, Loader=_Loader)
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001 - defensive: bad YAML shouldn't crash UI
        return {}


def _find_coordinator_block(players_cfg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Return the coordinator's config block from a parsed players.yml.

    Standard finance scenarios use the top-level key ``market:``. Opinion /
    information scenarios use ``{variant}_opinion_environment:`` or
    ``{variant}_information_environment:``. This helper returns the value
    dict for whichever coordinator-role block is present.
    """
    if not players_cfg:
        return None
    if isinstance(players_cfg.get("market"), dict):
        return players_cfg["market"]
    for key, val in players_cfg.items():
        if isinstance(val, dict) and (
            key.endswith("_opinion_environment")
            or key.endswith("_information_environment")
        ):
            return val
    return None


# Fallback map used when a scenario's players.yml has no `archetype:` field
# (e.g. the file predates the archetype convention). Prefer reading the YAML
# field; this table only guards against config regressions.
_ARCHETYPE_FALLBACK: Dict[str, str] = {
    "EchoChamber": "opinion-echo-chamber-clustering",
    "RumorSpread": "information-sis-contagion",
    "LUNACollapse": "crypto-algostable-depeg",
    "SVBBankRun": "deposit-bank-run-diamond-dybvig",
    "Volmageddon": "derivatives-vol-feedback",
    "CreditCycle": "credit-minsky-cycle",
    "GFC2008": "credit-minsky-cycle",
    "EuropeanDebtCrisis": "bond-yield-spread-inverse",
    "LTCMCollapse": "bond-yield-spread-inverse",
    "SorosPound": "fx-currency-peg-and-attack",
    "AsianFinancialCrisis": "fx-currency-peg-and-attack",
    "CurrencyCrisis": "fx-currency-peg-and-attack",
    "CarryTradeUnwind": "fx-currency-peg-and-attack",
}


@lru_cache(maxsize=64)
def get_market_archetype(scenario_name: str) -> Optional[str]:
    """Return the archetype stem bound to this scenario, if any.

    Resolution order:
      1. Read `archetype:` field from the coordinator block in
         configs/{scenario}/{variant}/players.yml.
      2. Fall back to the built-in ``_ARCHETYPE_FALLBACK`` table for
         scenarios whose YAML has not yet been updated.
      3. Fall back to ``stock-standard-price-impact`` (the workhorse
         archetype used by most behavioural-bias scenarios).

    Args:
        scenario_name: Scenario key (accepts flat "AssetBubble" or
            slash-separated "AssetBubble/Rule").

    Returns:
        A kebab-case archetype stem (matching a file under
        ``examples/AGENT_POOL/market/{stem}.md``) or ``None`` if the
        scenario name is unknown and no players.yml can be parsed.
    """
    resolved = _resolve_display_key(scenario_name)
    # Try each variant in turn — variants share the archetype in practice.
    for variant in ("Rule", "LLM", "RuleLLM", "Rag"):
        cfg = _load_players_yml_lenient(f"{resolved}/{variant}")
        block = _find_coordinator_block(cfg)
        if block:
            arch = block.get("archetype")
            if isinstance(arch, str) and arch:
                return arch
    # Also try the raw key in case it's already a full "Name/Variant" path.
    cfg = _load_players_yml_lenient(scenario_name)
    block = _find_coordinator_block(cfg)
    if block:
        arch = block.get("archetype")
        if isinstance(arch, str) and arch:
            return arch
    if resolved in _ARCHETYPE_FALLBACK:
        return _ARCHETYPE_FALLBACK[resolved]
    return "stock-standard-price-impact"


def get_market_icon_path(scenario_name: str) -> Optional[Path]:
    """Return the coordinator icon PNG for this scenario, if present on disk.

    The path is ``examples/AGENT_POOL/agent_images/icons/market/{stem}.png``
    where ``{stem}`` is the archetype returned by :func:`get_market_archetype`.

    Returns ``None`` if either the archetype cannot be resolved or the PNG
    file does not exist.
    """
    stem = get_market_archetype(scenario_name)
    if not stem:
        return None
    p = EXAMPLES_DIR / "AGENT_POOL" / "agent_images" / "icons" / "market" / f"{stem}.png"
    return p if p.exists() else None


# Human-readable Market-Type label per archetype stem. Used by
# ``get_market_type`` so the sidebar shows a semantic label that matches
# the icon rather than a keyword-guessed generic string.
_ARCHETYPE_MARKET_TYPE: Dict[str, str] = {
    "stock-standard-price-impact": "Stock Market",
    "opinion-echo-chamber-clustering": "Opinion Field",
    "information-sis-contagion": "Information Field",
    "fx-currency-peg-and-attack": "FX Market",
    "bond-yield-spread-inverse": "Bond Market",
    "crypto-algostable-depeg": "Crypto Market",
    "derivatives-vol-feedback": "Derivatives Market",
    "deposit-bank-run-diamond-dybvig": "Deposit Market",
    "credit-minsky-cycle": "Credit Market",
}


def get_market_type(scenario_name: str) -> str:
    """Infer the market type from the scenario's bound archetype.

    Prefers the ``players.yml → market.archetype:`` field (via
    :func:`get_market_archetype`) and maps it through
    ``_ARCHETYPE_MARKET_TYPE`` to a human-readable label. Falls back to the
    legacy keyword-based guess only when no archetype can be resolved.

    Args:
        scenario_name: Name of the scenario

    Returns:
        Human-readable market type string (e.g. 'Stock Market').
    """
    stem = get_market_archetype(scenario_name)
    if stem and stem in _ARCHETYPE_MARKET_TYPE:
        return _ARCHETYPE_MARKET_TYPE[stem]

    # Fallback: legacy keyword heuristic (kept for safety when the archetype
    # cannot be resolved — should be unreachable once all scenarios carry
    # the `archetype:` field).
    name_lower = _resolve_display_key(scenario_name).lower()
    if "crypto" in name_lower:
        return "Crypto Market"
    elif "bond" in name_lower or "fixed" in name_lower:
        return "Bond Market"
    elif "fx" in name_lower or "currency" in name_lower:
        return "FX Market"
    else:
        return "Stock Market"


def get_analysis_path(scenario_name: str) -> Optional[Path]:
    """Get the path to analysis output directory.

    Args:
        scenario_name: Name of the scenario directory

    Returns:
        Path to analysis directory or None
    """
    info = get_scenario_info(scenario_name)
    if not info.get("record_path"):
        return None

    record_path = _PROJECT_ROOT / info["record_path"]
    analysis_path = record_path.parent / "analysis"

    return analysis_path if analysis_path.exists() else None


def _dir_latest_mtime(
    root: Optional[Path], exclude: Optional[Path] = None
) -> Optional[float]:
    """Return the newest file mtime under *root* (recursive).

    Args:
        root: Directory to scan; None/absent yields None.
        exclude: Optional subtree to skip (e.g. the analysis output dir).

    Returns:
        The maximum st_mtime among files, or None when no files are found.
    """
    if not root or not root.exists():
        return None
    latest: Optional[float] = None
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if exclude is not None:
            try:
                p.relative_to(exclude)
                continue  # inside the excluded subtree
            except ValueError:
                pass
        try:
            m = p.stat().st_mtime
        except OSError:
            continue
        if latest is None or m > latest:
            latest = m
    return latest


def get_analysis_freshness(scenario_name: str) -> str:
    """Classify analysis output relative to the underlying experiment data.

    Compares the newest analysis artefact mtime against the newest data-file
    mtime, so a stale analysis (produced before the latest run) can be flagged
    for re-running rather than silently shown.

    Args:
        scenario_name: Scenario directory name.

    Returns:
        One of:
          - "no_data": no experiment data exists.
          - "missing": data exists but no analysis charts are on disk.
          - "stale":   analysis charts exist but predate the newest data file.
          - "fresh":   analysis charts exist and post-date all data files.
    """
    info = get_scenario_info(scenario_name)
    if not info.get("record_path"):
        return "no_data"

    record_path = _PROJECT_ROOT / info["record_path"]
    variant_dir = record_path.parent
    analysis_path = variant_dir / "analysis"

    pngs = list(analysis_path.glob("*.png")) if analysis_path.exists() else []
    data_mtime = _dir_latest_mtime(variant_dir, exclude=analysis_path)

    if not pngs:
        return "missing" if data_mtime is not None else "no_data"

    analysis_mtime = max(p.stat().st_mtime for p in pngs)
    summary = analysis_path / "summary.json"
    if summary.exists():
        analysis_mtime = max(analysis_mtime, summary.stat().st_mtime)

    if data_mtime is None:
        return "fresh"
    return "fresh" if analysis_mtime >= data_mtime else "stale"
