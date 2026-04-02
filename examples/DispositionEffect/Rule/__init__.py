"""DispositionEffect - Prospect Theory Trading Simulation

Demonstrates the disposition effect (Shefrin & Statman 1985):
- Tendency to sell winners too early (realize gains)
- Tendency to hold losers too long (reluctant to realize losses)

Theory: Prospect Theory (Kahneman & Tversky 1979)
- Loss aversion: Losses hurt more than equivalent gains feel good
- Reference point dependence: Evaluate gains/losses relative to purchase price
"""

from .players import (
    Market,
    DispositionInvestor,
    RationalInvestor,
    TaxAwareInvestor,
    IndexHolder,
    InstitutionalInvestor,
)

__all__ = [
    "Market",
    "DispositionInvestor",
    "RationalInvestor",
    "TaxAwareInvestor",
    "IndexHolder",
    "InstitutionalInvestor",
]
