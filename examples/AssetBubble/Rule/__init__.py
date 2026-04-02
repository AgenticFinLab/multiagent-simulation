"""AssetBubble - Rule-based Asset Bubble Simulation

This module implements a market simulation demonstrating asset bubble formation
and potential collapse through interactions between heterogeneous agents.

Phenomenon: Asset Bubbles
    Asset prices severely and persistently deviate from fundamental value,
    often driven by speculative momentum and limited arbitrage.

Theoretical Foundation:
    - Greater Fool Theory: Speculation based on selling to someone willing to pay more
    - Limits to Arbitrage: Rational traders cannot fully correct mispricings
    - De Long et al. (1990): Noise Trader Risk model
    - Abreu & Brunnermeier (2003): Bubbles and crashes model

Investor Types:
    - MomentumSpeculator: Chases price trends, ignores fundamentals, high risk
    - RationalArbitrageur: Value investor, attempts to short overvalued assets
    - NoiseTrader: Random/emotional trading, tends to follow crowds
    - FundamentalInvestor: Anchors to intrinsic value (weak)
    - LeveragedBuyer: Amplified momentum with margin constraints
    - ConservativeHolder: Long-term holder, provides stability
"""

from examples.AssetBubble.Rule.players import (
    Market,
    MomentumSpeculator,
    RationalArbitrageur,
    NoiseTrader,
    FundamentalInvestor,
    LeveragedBuyer,
    ConservativeHolder,
)

__all__ = [
    "Market",
    "MomentumSpeculator",
    "RationalArbitrageur",
    "NoiseTrader",
    "FundamentalInvestor",
    "LeveragedBuyer",
    "ConservativeHolder",
]
