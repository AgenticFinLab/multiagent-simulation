# MarketCrash RuleLLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Mechanism | Explicit crash rules embedded in LLM prompts |
| Market | Same rule-based market as Rule |
| Agents | RuleLLM versions of panic, risk parity, leverage, liquidity, and bottom-fishing agents |
| Runtime Change | Documentation-only backfill in this commit |

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMRiskParityFund

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` | System prompt states volatility-targeting rule |
| Runtime path | `RuleLLMInvestor` builds market context and parses JSON decision |

### §2.2 RuleLLMLeveragedFund

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` | System prompt states margin/liquidation logic |
| Runtime path | Parsed action is constrained by cash/position before order |

### §2.3 RuleLLMMarketMaker

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` | Prompt describes volatility-sensitive liquidity provision |
| Runtime path | Order includes liquidity-relevant fields consumed by market logic |

### §2.4 RuleLLMPanicSeller

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` | Prompt states panic trigger and sell behavior |
| Runtime path | LLM may vary explanation but must return structured decision |

### §2.5 RuleLLMBottomFisher

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.6` | Prompt states discount/crash buying rule |
| Runtime path | Cash constraints cap buy quantity |

## §3 Market Mechanism Implementation

Market mechanics remain rule-based and comparable to Rule. Only investor
decision generation is LLM-mediated.

## §4 Variant-Specific Features

RuleLLM tests whether explicit numerical crash rules remain stable when the
final decision is emitted by an LLM.

## §5 Architecture Diagram

```text
Market update -> Rule prompt + market context -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/MarketCrash/RuleLLM/players.yml`. Each LLM agent uses
`extras.llm.sys_message`, `extras.llm.user_message`, `lm_name`, and
`generation_config`.

## §7 Running Instructions

```bash
python examples/MarketCrash/RuleLLM/run_marketcrash_rulellm.py \
  -c configs/MarketCrash/RuleLLM/simulation.yml
```

## §8 Expected Behavior Patterns

Expected market phases match Rule, but order timing and quantities may vary
because the LLM interprets rules and market state.

## §9 References

See `../simulation-bases.md §4` and `../analysis-bases.md §2`.
