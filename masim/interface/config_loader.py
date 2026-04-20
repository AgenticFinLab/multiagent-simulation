"""Configuration loader for discovering and parsing simulation scenarios."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml


# Base directory for docs
EXAMPLES_DIR = Path("examples")

CONFIGS_DIR = Path("configs")
EXPERIMENT_DIR = Path("EXPERIMENT")

# Maps flat config-dir name → (parent_dir, sub_dir) in examples/ and EXPERIMENT/
# Scenarios not in this map (e.g. "Demo") remain flat.
SCENARIO_PATH_MAP: Dict[str, Tuple[str, str]] = {
    "AssetBubble": ("AssetBubble", "Rule"),
    "AssetBubbleLLM": ("AssetBubble", "LLM"),
    "AssetBubbleRuleLLM": ("AssetBubble", "RuleLLM"),
    "AssetBubbleRag": ("AssetBubble", "Rag"),
    "DispositionEffect": ("DispositionEffect", "Rule"),
    "DispositionEffectLLM": ("DispositionEffect", "LLM"),
    "DispositionEffectRuleLLM": ("DispositionEffect", "RuleLLM"),
    "DispositionEffectRag": ("DispositionEffect", "Rag"),
    "HerdEffect": ("HerdEffect", "Rule"),
    "HerdEffectLLM": ("HerdEffect", "LLM"),
    "HerdEffectRuleLLM": ("HerdEffect", "RuleLLM"),
    "EquityPremium": ("EquityPremium", "Rule"),
    "EquityPremiumLLM": ("EquityPremium", "LLM"),
    "FlashCrash": ("FlashCrash", "Rule"),
    "FlashCrashLLM": ("FlashCrash", "LLM"),
    "LiquidityDryup": ("LiquidityDryup", "Rule"),
    "LiquidityDryupLLM": ("LiquidityDryup", "LLM"),
    "MarketCrash": ("MarketCrash", "Rule"),
    "MarketCrashLLM": ("MarketCrash", "LLM"),
    "MomentumEffect": ("MomentumEffect", "Rule"),
    "MomentumEffectLLM": ("MomentumEffect", "LLM"),
    "ReversalEffect": ("ReversalEffect", "Rule"),
    "ReversalEffectLLM": ("ReversalEffect", "LLM"),
    "ShortSqueeze": ("ShortSqueeze", "Rule"),
    "ShortSqueezeLLM": ("ShortSqueeze", "LLM"),
    "VolatilityClustering": ("VolatilityClustering", "Rule"),
    "VolatilityClusteringLLM": ("VolatilityClustering", "LLM"),
}


def _examples_path(scenario_name: str) -> Path:
    """Return the examples/ subdirectory for a scenario (nested or flat)."""
    mapping = SCENARIO_PATH_MAP.get(scenario_name)
    if mapping:
        parent, sub = mapping
        return EXAMPLES_DIR / parent / sub
    return EXAMPLES_DIR / scenario_name


def _experiment_path(scenario_name: str) -> Path:
    """Return the EXPERIMENT/ subdirectory for a scenario (nested or flat)."""
    mapping = SCENARIO_PATH_MAP.get(scenario_name)
    if mapping:
        parent, sub = mapping
        return EXPERIMENT_DIR / parent / sub
    return EXPERIMENT_DIR / scenario_name


def _configs_path(scenario_name: str) -> Path:
    """Return the configs/ subdirectory for a scenario (nested or flat)."""
    mapping = SCENARIO_PATH_MAP.get(scenario_name)
    if mapping:
        parent, sub = mapping
        return CONFIGS_DIR / parent / sub
    return CONFIGS_DIR / scenario_name


# Scenario name mapping for display
SCENARIO_DISPLAY_NAMES = {
    "AssetBubble": "Asset Bubble",
    "AssetBubbleLLM": "Asset Bubble (LLM)",
    "AssetBubbleRuleLLM": "Asset Bubble (RuleLLM)",
    "AssetBubbleRag": "Asset Bubble (RAG)",
    "MarketCrash": "Market Crash",
    "MarketCrashLLM": "Market Crash (LLM)",
    "HerdEffect": "Herd Effect",
    "HerdEffectLLM": "Herd Effect (LLM)",
    "HerdEffectRuleLLM": "Herd Effect (RuleLLM)",
    "MomentumEffect": "Momentum Effect",
    "MomentumEffectLLM": "Momentum Effect (LLM)",
    "ReversalEffect": "Reversal Effect",
    "ReversalEffectLLM": "Reversal Effect (LLM)",
    "FlashCrash": "Flash Crash",
    "FlashCrashLLM": "Flash Crash (LLM)",
    "VolatilityClustering": "Volatility Clustering",
    "VolatilityClusteringLLM": "Volatility Clustering (LLM)",
    "EquityPremium": "Equity Premium",
    "EquityPremiumLLM": "Equity Premium (LLM)",
    "DispositionEffect": "Disposition Effect",
    "DispositionEffectLLM": "Disposition Effect (LLM)",
    "DispositionEffectRuleLLM": "Disposition Effect (RuleLLM)",
    "DispositionEffectRag": "Disposition Effect (RAG)",
    "LiquidityDryup": "Liquidity Dry-up",
    "LiquidityDryupLLM": "Liquidity Dry-up (LLM)",
    "ShortSqueeze": "Short Squeeze",
    "ShortSqueezeLLM": "Short Squeeze (LLM)",
    "Demo": "Demo",
}


def discover_scenarios() -> List[str]:
    """Discover all available simulation scenarios from configs directory.

    Supports both flat layout (configs/Demo/) and nested layout
    (configs/AssetBubble/Rule/, configs/AssetBubble/LLM/, ...).

    Returns:
        List of logical scenario names keyed by SCENARIO_PATH_MAP
        (e.g., ["AssetBubble", "AssetBubbleLLM", "Demo", ...])
    """
    if not CONFIGS_DIR.exists():
        return []

    found = set()

    # Walk up to depth-2 looking for simulation.yml
    for item in sorted(CONFIGS_DIR.iterdir()):
        if not item.is_dir() or item.name.startswith("_") or item.name == "TEMPLATES":
            continue
        # Depth-1: flat scenario (e.g. configs/Demo/simulation.yml)
        if (item / "simulation.yml").exists():
            found.add(item.name)
        else:
            # Depth-2: nested scenario (e.g. configs/AssetBubble/Rule/simulation.yml)
            for sub in sorted(item.iterdir()):
                if sub.is_dir() and (sub / "simulation.yml").exists():
                    # Reverse-lookup logical name from (parent, subdir)
                    key = (item.name, sub.name)
                    logical = next(
                        (k for k, v in SCENARIO_PATH_MAP.items() if v == key), None
                    )
                    if logical:
                        found.add(logical)

    # Return in a stable display order matching SCENARIO_DISPLAY_NAMES
    order = list(SCENARIO_DISPLAY_NAMES.keys())
    return [s for s in order if s in found] + sorted(found - set(order))


def get_scenario_info(scenario_name: str) -> Dict[str, Any]:
    """Get basic information about a scenario.

    Args:
        scenario_name: Name of the scenario directory

    Returns:
        Dict with name, display_name, description, is_llm, config_path
    """
    config_path = _configs_path(scenario_name) / "simulation.yml"

    info = {
        "name": scenario_name,
        "display_name": SCENARIO_DISPLAY_NAMES.get(scenario_name, scenario_name),
        "description": "",
        "is_llm": scenario_name.endswith("LLM") or scenario_name.endswith("Rag"),
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
        except Exception:
            pass

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


def get_scenario_pairs() -> List[Tuple[str, str]]:
    """Get pairs of (rule_based, llm) scenario names.

    Returns:
        List of tuples (base_name, llm_name) for scenarios that have both variants
        Special variants (RuleLLM, Rag) are paired with their base scenario.
    """
    scenarios = discover_scenarios()
    pairs = []
    seen = set()

    for name in scenarios:
        if name in seen:
            continue

        # Handle RuleLLM variants - pair with their base scenario
        if name.endswith("RuleLLM"):
            base = name[:-8]  # Remove "RuleLLM"
            if base in scenarios and base not in seen:
                pairs.append((base, name))
                seen.add(base)
            else:
                pairs.append((None, name))
            seen.add(name)
        # Handle Rag variants
        elif name.endswith("Rag"):
            base = name[:-3]  # Remove "Rag"
            if base in scenarios and base not in seen:
                pairs.append((base, name))
                seen.add(base)
            else:
                pairs.append((None, name))
            seen.add(name)
        # Standard LLM variant (not RuleLLM)
        elif name.endswith("LLM"):
            base = name[:-3]
            if base in scenarios:
                pairs.append((base, name))
                seen.add(base)
                seen.add(name)
            else:
                pairs.append((None, name))
                seen.add(name)
        # Base scenario (not LLM variant)
        else:
            llm_variant = name + "LLM"
            if llm_variant in scenarios and llm_variant not in seen:
                pairs.append((name, llm_variant))
                seen.add(name)
                seen.add(llm_variant)
            elif name not in seen:
                pairs.append((name, None))
                seen.add(name)

    return pairs


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

    record_path = Path(info["record_path"])
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
        scenario_name: Name of the scenario directory

    Returns:
        Human-readable market description string
    """
    # Strip LLM suffix for fallback lookup
    base = scenario_name[:-3] if scenario_name.endswith("LLM") else scenario_name
    return _SCENARIO_MARKET_DESCRIPTIONS.get(
        scenario_name,
        _SCENARIO_MARKET_DESCRIPTIONS.get(base, ""),
    )


def get_market_type(scenario_name: str) -> str:
    """Infer the market type from the scenario name and config.

    Args:
        scenario_name: Name of the scenario

    Returns:
        Human-readable market type string (e.g. 'Stock Market')
    """
    # All current scenarios are equity/stock market simulations
    name_lower = scenario_name.lower()
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

    record_path = Path(info["record_path"])
    analysis_path = record_path.parent / "analysis"

    return analysis_path if analysis_path.exists() else None
