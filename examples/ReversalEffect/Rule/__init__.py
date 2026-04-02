"""ReversalEffect - Long-term Mean Reversion Simulation

This module implements the Reversal Effect (De Bondt & Thaler, 1985):
- Past losers tend to outperform past winners over 3-5 year horizons
- Market overreacts to both good and bad news
- Creates mean reversion in long-term returns
"""

from examples.ReversalEffect.Rule.players import (
    Market,
    ContrarianInvestor,
    MomentumInvestor,
    OverconfidentTrader,
    NoiseTrader,
    ValueInvestor,
    IndexTracker,
)

__all__ = [
    "Market",
    "ContrarianInvestor",
    "MomentumInvestor",
    "OverconfidentTrader",
    "NoiseTrader",
    "ValueInvestor",
    "IndexTracker",
]
