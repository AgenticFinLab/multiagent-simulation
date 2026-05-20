# LUNACollapse Analysis Guide

## §1 Metrics

| Metric | Description | Expected Range |
|--------|-------------|----------------|
| Price deviation | Deviation from fundamental | Varies by scenario |
| Max drawdown | Largest peak-to-trough decline | Varies by scenario |
| Volatility | Annualized return volatility | Varies by scenario |

## §2 Visualization Guide

1. **Price vs Fundamental**: Shows whether agents create mispricings
2. **Deviation Plot**: Magnitude and persistence of mispricings
3. **Return Distribution**: Should show fat tails for behavioral scenarios

## §3 Troubleshooting

- **No phenomenon observed**: Adjust agent parameters
- **Too extreme**: Add more stabilizing agents or increase mean reversion
- **Too stable**: Increase destabilizing agent parameters

## §4 References

- Algorithmic stablecoin mechanism design (Klages-Mundt et al., 2020)
- Death spiral dynamics (Levy, 2022)
- DeFi contagion (Werner et al., 2022)
