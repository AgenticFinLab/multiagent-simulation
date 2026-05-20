# TulipMania RuleLLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Mechanism | Persona reasoning anchored by mania, social-proof, valuation, and exit rules |
| Market | Same price/fundamental market as Rule |
| Agents | RuleLLM trend chaser, social-proof follower, intrinsic-value trader, early-exit trader, noise trader |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

| Agent | Root Section | Runtime Implementation |
|---|---|---|
| RuleLLMTrendChaser | `simulation-bases.md §4.1` | Prompt encodes positive-feedback demand |
| RuleLLMSocialProofFollower | `simulation-bases.md §4.2` | Prompt encodes crowd-following behavior |
| RuleLLMIntrinsicValueTrader | `simulation-bases.md §4.3` | Prompt encodes value anchor |
| RuleLLMEarlyExitTrader | `simulation-bases.md §4.4` | Prompt encodes early-exit behavior |
| RuleLLMNoiseTrader | `simulation-bases.md §4.5` | Prompt encodes random baseline behavior |

## §3 Market Mechanism Implementation

Market clearing remains unchanged. RuleLLM supplies persona and quantitative
rule instructions to the LLM before canonical order parsing.

## §4 Variant-Specific Features

This variant tests whether explicit rule text constrains LLM mania narratives
toward the Rule baseline.

## §5 Architecture Diagram

```text
Market state -> persona + rule prompt -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/TulipMania/RuleLLM/players.yml`.

## §7 Running Instructions

```bash
python examples/TulipMania/RuleLLM/run_tulipmania_rulellm.py \
  -c configs/TulipMania/RuleLLM/simulation.yml
```

## §8 Expected Behavior Patterns

RuleLLM should preserve mania amplification and correction pressure while
reducing unstructured prompt drift.

## §9 References

See `../simulation-bases.md §4`, `../simulation-bases.md §9`, and
`../analysis-bases.md §2`.

