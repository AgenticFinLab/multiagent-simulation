"""
Demo Package - Simple Price Averaging Simulation

Components:
- SimpleInvestor: Investor that submits prices to market
- SimpleMarket: Market that calculates and broadcasts average price
"""

from .players import SimpleInvestor
from .conductor import SimpleMarket

__all__ = [
    "SimpleInvestor",
    "SimpleMarket",
]
