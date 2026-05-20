# TulipMania LLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Mechanism | Persona-driven mania, social proof, valuation, early exit, and noise decisions |
| Market | Same price/fundamental market as Rule |
| Agents | LLM trend chaser, social-proof follower, intrinsic-value trader, early-exit trader, noise trader |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

| Agent | Root Section | Runtime Implementation |
|---|---|---|
| LLMTrendChaser | `simulation-bases.md §4.1` | Persona prompt follows rising prices |
| LLMSocialProofFollower | `simulation-bases.md §4.2` | Persona prompt follows crowd participation |
| LLMIntrinsicValueTrader | `simulation-bases.md §4.3` | Persona prompt anchors on intrinsic value |
| LLMEarlyExitTrader | `simulation-bases.md §4.4` | Persona prompt exits before crash |
| LLMNoiseTrader | `simulation-bases.md §4.5` | Persona prompt supplies random baseline liquidity |

## §3 Market Mechanism Implementation

Market mechanics match Rule. LLM changes the decision generator from explicit
rules to persona reasoning and canonical order JSON.

## §4 Variant-Specific Features

LLM tests whether mania narratives, social proof, and early-exit reasoning
emerge from investor personas without changing market clearing.

## §5 Architecture Diagram

```text
Market state -> persona prompt -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/TulipMania/LLM/players.yml`.

## §7 Running Instructions

```bash
python examples/TulipMania/LLM/run_tulipmania_llm.py \
  -c configs/TulipMania/LLM/simulation.yml
```

## §8 Expected Behavior Patterns

Trend and social-proof personas should amplify mania; intrinsic-value and
early-exit personas should provide correction pressure.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.

