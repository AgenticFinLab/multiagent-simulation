# OverconfidenceBias Analysis Guide

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

- Daniel, Hirshleifer & Subrahmanyam (1998): Investor psychology and security market under/overreactions
- Odean (1998): Volume, volatility, price, and profit when all traders are above average
- Barber & Odean (2001): Boys will be boys: Gender, overconfidence, and common stock investment

## §5 Interpretation Checklist

- Compare overconfident and calibrated agents' average order size and trading
  frequency.
- Check whether large overconfident trades coincide with wider price deviations
  from fundamental value.
- Confirm that stabilizing agents reduce, rather than amplify, deviations.

## §6 Quality Checks

- Confirm the run completed the configured round count.
- Confirm trade records include valid action, price, and quantity fields.
- Review volatility and drawdown metrics for implausible numerical spikes.

## §7 Reporting Notes

Report the Rule variant as the deterministic baseline. When comparing with API
variants, separate overconfidence-driven trading intensity from model-output
quality issues such as parse failures or fallback actions.
