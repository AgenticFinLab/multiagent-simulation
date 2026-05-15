# FlashCrash Analysis Bases

## §1 Objectives

1. Verify that the simulation reproduces the three phases of a flash crash: normal → cascade → recovery.
2. Quantify the role of liquidity withdrawal in amplifying the price decline.
3. Measure stop-loss cascade depth and timing relative to HFT withdrawal.
4. Compare crash severity and recovery speed across Rule / LLM / RuleLLM / Rag variants.
5. Assess fundamental-trader effectiveness as a stabilising and recovery mechanism.

## §2 Core Metrics

```python
def crash_depth(price_history: List[float], fundamental: float) -> float:
    """Max deviation below fundamental as fraction of fundamental.
    Returns positive number: 0.09 means price fell 9 % below fundamental."""
    deviations = [(p - fundamental) / fundamental for p in price_history]
    return abs(min(deviations))

def liquidity_vacuum_duration(liquidity_history: List[int],
                              low_threshold: int = 2) -> int:
    """Number of rounds in which total_liquidity <= low_threshold.
    Measures how long the market operates in amplified-impact mode."""
    return sum(1 for liq in liquidity_history if liq <= low_threshold)

def stop_loss_cascade_volume(orders_history: List[List[Dict]]) -> float:
    """Total sell volume from StopLossTrader agents across all rounds.
    Measures cumulative forced selling pressure."""
    return sum(
        abs(o["quantity"])
        for round_orders in orders_history
        for o in round_orders
        if o.get("strategy") == "StopLossTrader" and o["quantity"] < 0
    )

def recovery_speed(price_history: List[float], trough_round: int,
                   fundamental: float, recovery_threshold: float = 0.02) -> int:
    """Rounds from trough to price returning within recovery_threshold of fundamental.
    Returns -1 if price never recovers within the simulation."""
    for i in range(trough_round, len(price_history)):
        if abs(price_history[i] - fundamental) / fundamental <= recovery_threshold:
            return i - trough_round
    return -1

def hft_withdrawal_fraction(provides_liquidity_history: List[Dict[str, bool]],
                            crash_start: int, crash_end: int) -> float:
    """Fraction of HFT/MarketMaker agents with provides_liquidity=False during crash window.
    1.0 = complete withdrawal; 0.0 = full provision."""
    crash_rounds = provides_liquidity_history[crash_start:crash_end]
    if not crash_rounds:
        return 0.0
    total = sum(
        sum(1 for v in r.values() if not v)
        for r in crash_rounds
    )
    denominator = sum(len(r) for r in crash_rounds)
    return total / max(denominator, 1)

def price_amplification_ratio(observed_max_drop: float,
                              baseline_max_drop: float) -> float:
    """Ratio of actual crash depth to baseline (liquidity always = 1).
    Values > 1 indicate liquidity-driven amplification."""
    return observed_max_drop / max(baseline_max_drop, 1e-6)
```

## §3 Dimensions

| Dimension               | Key questions                                                             |
|-------------------------|---------------------------------------------------------------------------|
| **Crash severity**      | How deep does price fall? How fast?                                       |
| **Liquidity dynamics**  | When does `total_liquidity` collapse? For how long?                       |
| **Cascade mechanics**   | How many stop-loss agents trigger, and in which rounds?                   |
| **Recovery**            | Who drives recovery? How many rounds to return to fundamental ±2 %?       |
| **Variant differences** | Do LLM agents withdraw earlier/later? Do RAG agents anticipate the crash? |

## §4 Phase Analysis

| Phase    | Rounds (typical) | Key indicators                                     | Analysis focus                     |
|----------|------------------|----------------------------------------------------|------------------------------------|
| Normal   | 1–10             | `liquidity` ≥ 3; price ≈ fundamental               | Baseline market activity           |
| Trigger  | 11–15            | First HFT momentum signal; `liquidity` declining   | HFT contribution to initial drop   |
| Cascade  | 16–25            | `liquidity` ≤ 2; stop-loss triggers; spread rising | Liquidity vacuum + cascade volume  |
| Trough   | 26–30            | Min price; max `crash_depth`; FT buying            | Deepest fundamental deviation      |
| Recovery | 31–50            | `liquidity` recovering; price → fundamental        | `recovery_speed`, FT effectiveness |

## §5 Cross-Variant Analysis

| Metric                      | Rule                               | LLM                             | RuleLLM                          | Rag                                     |
|-----------------------------|------------------------------------|---------------------------------|----------------------------------|-----------------------------------------|
| `crash_depth`               | Deterministic for fixed params     | Stochastic; ~same magnitude     | Slightly reduced (LLM can hedge) | May be shallower (historical awareness) |
| `liquidity_vacuum_duration` | Fixed by `volatility_threshold`    | Variable by LLM judgment        | Mixed                            | Shorter if RAG recalls past recoveries  |
| `stop_loss_cascade_volume`  | Sum of all SL positions            | LLM may delay trigger           | Rule-determined stops            | RAG may inform earlier exit             |
| `recovery_speed`            | Determined by FT `value_threshold` | LLM "recognises" undervaluation | Hybrid                           | May recover faster                      |
| `hft_withdrawal_fraction`   | Binary at `volatility_threshold`   | Probabilistic                   | Mostly rule-driven               | Context-dependent                       |
| `price_amplification_ratio` | Highest (no discretion)            | Lower if LLM hesitates          | Intermediate                     | Lowest (anticipatory)                   |

## §6 Expected Results

| Metric                      | Typical range        | Historical benchmark   |
|-----------------------------|----------------------|------------------------|
| `crash_depth`               | 5–12 %               | ~9 % (May 6, 2010)     |
| `liquidity_vacuum_duration` | 5–20 rounds          | ~36 minutes            |
| `stop_loss_cascade_volume`  | 500–3000 shares      | Large but unquantified |
| `recovery_speed`            | 10–30 rounds         | ~20 minutes            |
| `hft_withdrawal_fraction`   | 0.6–1.0 during crash | ~80 % (Kirilenko 2017) |
| `price_amplification_ratio` | 1.5–4.0 ×            | —                      |

## §7 Visualization Catalogue

| Plot                               | x-axis             | y-axis                           | Purpose                                  |
|------------------------------------|--------------------|----------------------------------|------------------------------------------|
| Price path with phases             | Round              | Price + fundamental line         | Annotate trigger/cascade/trough/recovery |
| Liquidity time series              | Round              | `total_liquidity` count          | Show vacuum duration                     |
| Stop-loss cascade waterfall        | Round              | Cumulative stop-loss sell volume | Multi-wave structure                     |
| HFT provides_liquidity heatmap     | Agent × Round      | provides_liquidity (bool)        | Which MM withdraws first                 |
| Price amplification scatter        | `liquidity_factor` | `price_impact`                   | Amplification nonlinearity               |
| Recovery speed box plot (variants) | Variant            | `recovery_speed` (rounds)        | Cross-variant comparison                 |
