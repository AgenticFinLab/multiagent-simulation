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

- Compare RAG-driven trading intensity with the Rule, LLM, and RuleLLM variants.
- Check whether retrieved context reinforces, moderates, or merely rationalizes
  overconfident position changes.
- Confirm that retrieval context does not replace the configured market role of
  each agent.

## §6 Quality Checks

- Confirm the run completed the configured round count.
- Audit retrieval availability, parse failures, retry counts, and fallback holds
  before accepting the sample as clean.
- Review price deviation, volatility, and trading volume for implausible
  numerical spikes.

## §7 Reporting Notes

Report RAG outcomes together with retrieval and output-quality diagnostics.
Fallback-heavy runs should be marked explicitly even when simulator execution
completes successfully.
