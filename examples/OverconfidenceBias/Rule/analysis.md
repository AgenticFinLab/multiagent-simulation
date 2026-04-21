# OverconfidenceBias Analysis Guide

## Metrics

| Metric | Description | Expected Range |
|--------|-------------|----------------|
| Price deviation | Deviation from fundamental | Varies by scenario |
| Max drawdown | Largest peak-to-trough decline | Varies by scenario |
| Volatility | Annualized return volatility | Varies by scenario |

## Visualization Guide

1. **Price vs Fundamental**: Shows whether agents create mispricings
2. **Deviation Plot**: Magnitude and persistence of mispricings
3. **Return Distribution**: Should show fat tails for behavioral scenarios

## Troubleshooting

- **No phenomenon observed**: Adjust agent parameters
- **Too extreme**: Add more stabilizing agents or increase mean reversion
- **Too stable**: Increase destabilizing agent parameters

## References

- Daniel, Hirshleifer & Subrahmanyam (1998): Investor psychology and security market under/overreactions
- Odean (1998): Volume, volatility, price, and profit when all traders are above average
- Barber & Odean (2001): Boys will be boys: Gender, overconfidence, and common stock investment
