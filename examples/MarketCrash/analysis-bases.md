# MarketCrash Analysis Bases

## §1 Analysis Objectives

The analysis checks whether a run exhibits a coherent crash process rather than
just a valid execution. The core questions are:

1. How deep and how fast was the drawdown?
2. How much selling came from mechanical deleveraging versus panic behavior?
3. Did liquidity provision weaken during stress?
4. Did BottomFisher demand absorb any portion of the sell cascade?

## §2 Metrics

### §2.1 Maximum Drawdown

Measure peak-to-trough loss in the market price path.

### §2.2 Largest One-Round Drop

Measure crash velocity as the most negative round return.

### §2.3 Volatility Spike

Measure whether realized volatility rises materially during the crash window.

### §2.4 Forced-Selling Pressure

Measure sell volume attributable to `RiskParityFund` and
`LeveragedHedgeFund`/`LeveragedFund` archetypes.

### §2.5 Liquidity Withdrawal

Measure reduced market-making activity using quote flow and, for RuleLLM/Rag,
`provides_liquidity` participation.

### §2.6 Panic Contribution

Measure sell volume from `PanicSeller` agents during negative-return rounds.

### §2.7 Bottom-Fisher Absorption

Measure whether `BottomFisher` buy volume offsets a meaningful share of crash
selling after deep discounts emerge.

## §3 Analysis Dimensions

The scenario should be analyzed along four axes:

- round-level price and return dynamics,
- investor-type order-flow contributions,
- liquidity versus volatility interaction,
- stabilizing versus amplifying demand.

## §4 Phase Analysis

Interpret the trajectory in five phases:

1. pre-crash positioning,
2. volatility onset,
3. deleveraging cascade,
4. liquidity stress,
5. stabilization or failed recovery.

## §5 Cross-Variant Comparison

The Rule baseline is the reference for mechanism shape. LLM, RuleLLM, and Rag
should be compared on:

- crash depth and speed,
- liquidity withdrawal timing,
- share of forced or panic selling,
- whether Rag retrieval changes stabilization timing,
- whether API variants remain structurally coherent despite stochastic output.

## §6 Expected Results

A valid MarketCrash run should show:

- a clear drawdown episode,
- elevated volatility around the crash window,
- non-trivial selling from deleveraging or panic archetypes,
- reduced liquidity support during stress,
- limited but visible contrarian support from BottomFisher.

## §7 Visualization And Output Contract

All variants must produce:

- `summary.json`
- `00_investor_bids.png`
- `01_marketcrash_dynamics.png`
- `02_marketcrash_analysis.png`
- `03_summary.png`

The Rag variant must additionally produce:

- `rag_stats.json`

Variant-level `analysis.md` files should map these outputs to the scenario’s
actual metrics rather than using placeholder function contracts.
