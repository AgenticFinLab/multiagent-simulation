"""FlashCrash2010 Rule-Based Variant

Deterministic rule-based implementation of the 2010 Flash Crash simulation.

Agents:
    Market:             Order book with dynamic depth
    HFTMarketMaker:     Liquidity provider with withdrawal behavior
    MomentumChaser:     Trend-following HFT
    FundamentalTrader:  Value-based stabilizer
    StopLossTrader:     Stop-loss order trigger
    NoiseTrader:        Random uninformed trader
"""

from examples.FlashCrash2010.Rule.players import (
    FundamentalTrader,
    HFTMarketMaker,
    Market,
    MomentumChaser,
    NoiseTrader,
    StopLossTrader,
)

__all__ = [
    "Market",
    "HFTMarketMaker",
    "MomentumChaser",
    "FundamentalTrader",
    "StopLossTrader",
    "NoiseTrader",
]
