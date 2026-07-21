"""Regression tests for EquityPremium price formation."""

import math
import unittest
from unittest.mock import patch

from examples.EquityPremium.market import calculate_stock_transition


class EquityPremiumMarketTest(unittest.TestCase):
    @patch("examples.EquityPremium.market.random.gauss", return_value=0.0)
    def test_extreme_order_sizes_cannot_overflow_price(self, _gauss):
        price = 100.0

        for _ in range(10_000):
            price, stock_return = calculate_stock_transition(
                price,
                [{"stock_qty": 1e308}, {"stock_qty": -5e307}],
                expected_return=0.000238,
                volatility=0.00945,
            )
            self.assertTrue(math.isfinite(price))
            self.assertLessEqual(abs(stock_return), 0.047488)

    def test_non_finite_order_fails_fast(self):
        with self.assertRaisesRegex(ValueError, "orders must be finite"):
            calculate_stock_transition(
                100.0,
                [{"stock_qty": float("inf")}],
                expected_return=0.000238,
                volatility=0.00945,
            )


if __name__ == "__main__":
    unittest.main()
