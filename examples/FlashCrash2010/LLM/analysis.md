# FlashCrash2010 Analysis Guide

## Metrics Interpretation

### Price Metrics

| Metric | Description | Expected Range | Interpretation |
|--------|-------------|----------------|----------------|
| Max Drawdown | Largest peak-to-trough decline | -5% to -15% | Crash severity |
| Crash Magnitude | Price drop during crash phase | -5% to -10% | Speed of collapse |
| Recovery | Price rebound after trough | +3% to +8% | Market resilience |

### Market Structure Metrics

| Metric | Description | Expected Range | Interpretation |
|--------|-------------|----------------|----------------|
| Max Spread | Widest bid-ask spread | 0.5% - 2.0% | Liquidity stress |
| Min Depth | Lowest order book depth | 500 - 2000 | Liquidity evaporation |
| Depth Collapse | % reduction in depth | 50% - 90% | Severity of withdrawal |

### HFT Metrics

| Metric | Description | Expected Range | Interpretation |
|--------|-------------|----------------|----------------|
| Normal Participation | HFT % in calm periods | 60% - 70% | Normal liquidity provision |
| Stress Participation | HFT % during crash | 10% - 30% | Withdrawal severity |
| Participation Drop | Difference | 30% - 50% | Withdrawal magnitude |

## Visualization Guide

### Price vs Fundamental Plot
- **Normal**: Price tracks fundamental closely
- **Crash**: Sharp divergence with rapid decline
- **Recovery**: Price returns toward fundamental

### Spread Evolution Plot
- **Normal**: Tight spreads (~0.01%)
- **Crash**: Dramatic widening (10-50x normal)
- **Recovery**: Gradual tightening

### Order Book Depth Plot
- **Normal**: Deep book (5000-10000 shares)
- **Crash**: Shallow book (10-20% of normal)
- **Recovery**: Gradual restoration

### HFT Participation Plot
- **Normal**: High participation (60-70%)
- **Crash**: Sharp drop (withdrawal)
- **Recovery**: Partial return

## Comparative Analysis

### Rule vs LLM Variants

| Aspect | Rule | LLM |
|--------|------|-----|
| Withdrawal Timing | Fixed thresholds | Adaptive, context-dependent |
| Spread Setting | Deterministic | May vary based on interpretation |
| Recovery Speed | Fixed | May be faster/slower |

### Expected Differences

1. **Rule**: Predictable, repeatable patterns
2. **LLM**: More variation, potentially more realistic
3. **RuleLLM**: Balance of consistency and adaptability
4. **RAG**: Historical knowledge may improve response

## Troubleshooting

### No Crash Observed
- Check withdrawal_threshold (lower = earlier withdrawal)
- Increase momentum_chaser activity
- Add more stop_loss_traders

### Crash Too Severe
- Increase fundamental_trader capital
- Raise mean_reversion parameter
- Add more HFT market makers

### No Recovery
- Check mean_reversion strength
- Ensure fundamental_traders have sufficient capital
- Verify stop-loss traders don't all trigger simultaneously

## Statistical Validation

Compare simulation results to historical May 6, 2010 data:

| Metric | Historical | Simulation Target |
|--------|------------|-------------------|
| Max decline | ~9% (DJIA) | 5-10% |
| Duration | ~15 minutes | 20-50 rounds |
| Recovery | ~600 points | Partial to full |
| Volume spike | 3-5x normal | 2-4x normal |

## References

1. Kirilenko et al. (2017) - Benchmark for HFT behavior
2. CFTC-SEC Report (2010) - Official event analysis
3. Biais et al. (2015) - Order book dynamics theory
