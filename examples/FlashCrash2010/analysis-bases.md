# FlashCrash2010 Analysis Bases

## §1 Objectives

1. Verify the simulation reproduces the full May 6, 2010 crash profile: depth collapse → price cascade → spread widening → recovery.
2. Quantify the order-book depth dynamics: how fast does `Depth` collapse, how low does it go?
3. Measure HFT withdrawal fraction and its correlation with crash depth.
4. Assess stop-loss cascade timing and cumulative volume relative to crash onset.
5. Compare crash severity, depth collapse, and recovery speed across Rule / LLM / RuleLLM / Rag variants.

## §2 Core Metrics

```python
def max_drawdown(price_history: List[float]) -> float:
    """Peak-to-trough price decline as fraction of peak price.
    Returns positive number: 0.09 = 9 % drawdown."""
    peak = price_history[0]
    max_dd = 0.0
    for p in price_history:
        if p > peak:
            peak = p
        dd = (peak - p) / peak
        if dd > max_dd:
            max_dd = dd
    return max_dd

def depth_collapse_ratio(depth_history: List[float], base_depth: float) -> float:
    """Minimum depth during simulation as fraction of base_depth.
    0.1 = depth fell to 10 % of baseline (90 % collapse)."""
    return min(depth_history) / base_depth

def spread_widening_factor(spread_history: List[float],
                           normal_spread: float = 0.0001) -> float:
    """Maximum spread reached divided by normal (baseline) spread.
    10.0 = spread was 10× normal at peak stress."""
    return max(spread_history) / max(normal_spread, 1e-8)

def hft_withdrawal_rounds(hft_orders_by_round: List[List[Dict]],
                          withdrawal_threshold: int = 0) -> int:
    """Number of rounds in which total HFT order quantity == 0 (complete withdrawal).
    withdrawal_threshold allows small residual HFT flow."""
    count = 0
    for round_orders in hft_orders_by_round:
        hft_qty = sum(abs(o["quantity"]) for o in round_orders
                      if o.get("agent_type") == "hft")
        if hft_qty <= withdrawal_threshold:
            count += 1
    return count

def cascade_trigger_rounds(stoploss_orders_by_round: List[List[Dict]]) -> List[int]:
    """List of rounds in which at least one StopLossTrader fires.
    Used to visualise multi-wave structure."""
    return [
        i for i, round_orders in enumerate(stoploss_orders_by_round)
        if any(o.get("agent_type") == "stoploss" and o["quantity"] < 0
               for o in round_orders)
    ]

def recovery_time(price_history: List[float], trough_round: int,
                  fundamental: float, threshold: float = 0.02) -> int:
    """Rounds from trough to price returning within threshold × fundamental of F.
    Returns -1 if not recovered."""
    for i in range(trough_round, len(price_history)):
        if abs(price_history[i] - fundamental) / fundamental <= threshold:
            return i - trough_round
    return -1
```

## §3 Dimensions

| Dimension             | Key questions                                                 |
|-----------------------|---------------------------------------------------------------|
| **Depth dynamics**    | How quickly does `Depth` collapse? What is the minimum ratio? |
| **Spread widening**   | How many rounds does spread stay above 10× normal?            |
| **HFT withdrawal**    | How many rounds is HFT participation below 30 %?              |
| **Stop-loss cascade** | In how many distinct waves do stop-losses fire?               |
| **Recovery**          | How many rounds to return within 2 % of fundamental?          |
| **Crash severity**    | What is the maximum drawdown?                                 |

## §4 Phase Analysis

| Phase    | Rounds (typical) | Key indicators                                               | Analysis focus                      |
|----------|------------------|--------------------------------------------------------------|-------------------------------------|
| Normal   | 1–10             | `depth` ≈ `base_depth`; `spread` ≈ `base_spread`; HFT active | Baseline calibration                |
| Trigger  | 11–15            | MomentumChaser detects trend; first HFT stress signal        | Who initiates the sell cascade      |
| Cascade  | 16–25            | `depth` < 20 % base; `spread` × 5–50; stop-losses fire       | Depth collapse speed; cascade waves |
| Trough   | 26–30            | Min price; max spread; FT buys aggressively                  | Crash depth; stabilisation onset    |
| Recovery | 31–50            | HFT returns; `depth` rebuilds; price → fundamental           | Recovery time; spread normalisation |

## §5 Cross-Variant Analysis

| Metric                   | Rule                                     | LLM                              | RuleLLM                       | Rag                               |
|--------------------------|------------------------------------------|----------------------------------|-------------------------------|-----------------------------------|
| `max_drawdown`           | Fixed by threshold params                | Stochastic around same magnitude | Slightly smaller (LLM hedges) | Smallest (historical awareness)   |
| `depth_collapse_ratio`   | Determined by stress_factor formula      | Modulated by LLM order volumes   | Mostly rule-driven depth      | Context-augmented                 |
| `spread_widening_factor` | Deterministic (volatility × hft formula) | Similar if LLM doesn't intervene | Hybrid                        | May be lower                      |
| `hft_withdrawal_rounds`  | Fixed by `withdrawal_threshold`          | Probabilistic; similar count     | Rule-dominant                 | May be fewer rounds               |
| Cascade waves            | Fixed by `stop_percentage` spread        | LLM may cut earlier              | Rule stops + LLM timing       | Historical guidance reduces waves |
| `recovery_time`          | Fixed by FT `value_trigger`              | Variable LLM recognition         | Hybrid                        | May be shorter                    |

## §6 Expected Results

| Metric                   | Typical range      | May 6, 2010 benchmark           |
|--------------------------|--------------------|---------------------------------|
| `max_drawdown`           | 5–12 %             | ~9 % (DJIA)                     |
| `depth_collapse_ratio`   | 0.05–0.20          | ~0.10 (90 % collapse estimated) |
| `spread_widening_factor` | 5–50 ×             | ~10–50 × (Biais 2015)           |
| `hft_withdrawal_rounds`  | 5–20               | ~36 minutes at ~1 round/min     |
| Cascade wave count       | 2–5 distinct waves | Multi-wave (CFTC-SEC 2010)      |
| `recovery_time`          | 10–25 rounds       | ~20 minutes                     |

## §7 Visualization Catalogue

| Plot                              | x-axis  | y-axis                              | Purpose                        |
|-----------------------------------|---------|-------------------------------------|--------------------------------|
| Price vs fundamental              | Round   | Price (line) + fundamental (dashed) | Full crash-recovery profile    |
| Order-book depth time series      | Round   | `Depth`                             | Show collapse and rebuild      |
| Spread evolution                  | Round   | `spread`                            | Stress widening pattern        |
| HFT participation fraction        | Round   | HFT order count / total orders      | Withdrawal timing              |
| Stop-loss cascade timeline        | Round   | Number of SL triggers per round     | Multi-wave cascade             |
| Depth vs spread scatter           | `depth` | `spread`                            | Non-linear stress relationship |
| Variant comparison: max drawdown  | Variant | `max_drawdown`                      | Cross-variant severity         |
| Variant comparison: recovery time | Variant | `recovery_time` (rounds)            | Cross-variant resilience       |
