# TulipMania Rule — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether deterministic trend-chasing, social-proof, intrinsic-value,
early-exit, and noise rules generate mania inflation and collapse.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rule Notes |
|---|---|---|---|
| Bubble Premium | `compute_bubble_premium()` | `analysis-bases.md §2.1` | Peak price vs intrinsic value |
| Trend-Chasing Volume | `compute_trend_chasing_volume()` | `analysis-bases.md §2.2` | TrendChaser demand |
| Social-Proof Demand | `compute_social_proof_demand()` | `analysis-bases.md §2.3` | Crowd-driven demand |
| Fundamental Resistance | `compute_fundamental_resistance()` | `analysis-bases.md §2.4` | IntrinsicValueTrader selling |
| Early Exit Timing | `compute_early_exit_timing()` | `analysis-bases.md §2.5` | Timing relative to peak |
| Crash Magnitude | `compute_crash_magnitude()` | `analysis-bases.md §2.6` | Peak-to-trough decline |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Agent contribution |

## §3 Dimension-by-Dimension Analysis

Compare bubble growth, trend demand, social proof, fundamental resistance,
early exits, and crash magnitude.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Positive feedback | TrendChaser buys rising prices |
| Crowd amplification | SocialProofFollower follows demand |
| Fundamental anchor | IntrinsicValueTrader sells overvaluation |

## §5 References

Metrics derive from `../analysis-bases.md §2`; deterministic behavior derives
from `../simulation-bases.md §4` and `§9`.

