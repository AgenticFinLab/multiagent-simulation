"""Execution policies shipped with the platform.

- :class:`~masim.execution.self_fill.SelfFillModel` — the default, identical to
  the historical agent-side fill so existing runs are unchanged.
- :class:`~masim.execution.self_fill.MarketPriceFillModel` — an example policy
  that settles at the observable market price with optional slippage.

The contract they implement is :class:`masim.platform.execution.base.FillModel`.
"""

from masim.execution.self_fill import MarketPriceFillModel, SelfFillModel

__all__ = ["SelfFillModel", "MarketPriceFillModel"]
