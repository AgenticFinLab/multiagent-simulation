"""MomentumEffect - Momentum Trading Simulation

Demonstrates the momentum anomaly documented by Jegadeesh & Titman (1993):
Past winners continue to outperform, past losers continue to underperform.

Theory: Conservatism bias, gradual information diffusion, and behavioral
        underreaction lead to predictable price patterns.

Key Agents:
- MomentumTrader: Buys recent winners, sells recent losers
- ContrarianTrader: Mean reversion strategy (opposing force)
- IndexFund: Passive buy-and-hold baseline
- MarketMaker: Liquidity provision
"""

from .players import (
    Market,
    MomentumTrader,
    ContrarianTrader,
    IndexFund,
    MarketMaker,
    TechnicalTrader,
    FundamentalTrader,
)

__all__ = [
    "Market",
    "MomentumTrader",
    "ContrarianTrader",
    "IndexFund",
    "MarketMaker",
    "TechnicalTrader",
    "FundamentalTrader",
]
