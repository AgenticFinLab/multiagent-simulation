"""MarketCrash - Rule-based Market Crash Simulation

Phenomenon: Market Crash / Flash Crash
    Rapid price decline with liquidity evaporation, often triggered by
    forced deleveraging and liquidity spiral dynamics.

Theoretical Foundation:
    - Minsky Moment: Sudden shift from stability to instability
    - Liquidity Spiral (Brunnermeier & Pedersen, 2009)
    - Fire Sales and Asset Prices (Shleifer & Vishny, 1992)

Investor Types:
    - RiskParityFund: Volatility targeting, forced deleveraging
    - LeveragedHedgeFund: Margin-constrained, forced liquidation
    - MarketMaker: Liquidity provider that withdraws in stress
    - PassiveInvestor: Buy-and-hold, minimal trading
    - PanicSeller: Retail that panic sells on losses
    - BottomFisher: Contrarian buyer in crashes
"""

from examples.MarketCrash.Rule.players import (
    Market,
    RiskParityFund,
    LeveragedHedgeFund,
    MarketMaker,
    PassiveInvestor,
    PanicSeller,
    BottomFisher,
)

__all__ = [
    "Market",
    "RiskParityFund",
    "LeveragedHedgeFund",
    "MarketMaker",
    "PassiveInvestor",
    "PanicSeller",
    "BottomFisher",
]
