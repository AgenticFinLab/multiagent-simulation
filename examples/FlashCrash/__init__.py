"""FlashCrash - Market Microstructure Simulation

This module implements Flash Crash dynamics:
- Extreme rapid price decline (e.g., 2010 Flash Crash)
- Liquidity withdrawal during stress
- Algorithmic trading feedback loops
- Quick recovery after crash

Reference: Kirilenko et al. (2017), CFTC/SEC Flash Crash Report (2010)
"""

from examples.FlashCrash.players import (
    Market,
    HighFrequencyTrader,
    MarketMaker,
    AlgorithmicTrader,
    StopLossTrader,
    FundamentalTrader,
    RetailTrader,
)

__all__ = [
    "Market",
    "HighFrequencyTrader",
    "MarketMaker",
    "AlgorithmicTrader",
    "StopLossTrader",
    "FundamentalTrader",
    "RetailTrader",
]
