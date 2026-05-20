# LTCMCollapse RuleLLM — Implementation Explanation

## §1 Variant Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Implements | `../simulation-bases.md` |
| Decision Logic | LLM decisions guided by explicit persona and decision-rule prompts |
| Key Difference | preserves the Rule mechanism as text while allowing language-model judgement |
| Files | `players.py`, `prompts.py`, `run_ltcmcollapse_rulellm.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

| Investor | sim-bases Ref | Class | Prompt Constant | Rule Encoding |
|---|---|---|---|---|
| ConvergenceArbitrageur | `§4.1` | `RuleLLMConvergenceArbitrageur` | `RULELLM_CONVERGENCEARBITRAGEUR_PROMPT` | `== DECISION RULES ==` states ±3% spread trigger and capped leveraged sizing |
| LeverageTrader | `§4.2` | `RuleLLMLeverageTrader` | `RULELLM_LEVERAGETRADER_PROMPT` | margin-call deleveraging and undervaluation buying rules |
| RiskManager | `§4.3` | `RuleLLMRiskManager` | `RULELLM_RISKMANAGER_PROMPT` | three-times-VaR breach and 50% risk-cut rule |
| LiquidityProvider | `§4.4` | `RuleLLMLiquidityProvider` | `RULELLM_LIQUIDITYPROVIDER_PROMPT` | 5% stress withdrawal and normal liquidity provision |
| CentralBank | `§4.5` | `RuleLLMCentralBank` | `RULELLM_CENTRALBANK_PROMPT` | -10% systemic stress threshold and buy-only intervention |

## §3 Market Mechanism Implementation

The market is imported from the Rule variant, so `Market.perceive()` and price formation are identical to `simulation-bases.md §3.1`.

## §4 Variant-Specific Features

Every system prompt has two required sections:

- `== PERSONA ==`: investor role, belief, and risk style from `simulation-bases.md §4.N`.
- `== DECISION RULES ==`: plain-language version of the Rule decision mechanism.

The rules are guidance for LLM reasoning, not executable code. The parser still requires `<analysis>` and `<decision>` JSON with `action`, `bid_price`, `quantity`, and `reasoning`.

## §5 Architecture Diagram

```text
Rule market broadcast
  -> RuleLLMInvestor.perceive()
  -> RuleLLMInvestor.decide()
       -> system prompt = PERSONA + DECISION RULES
       -> user message = current market state
       -> parse decision JSON
  -> emit standard order
```

## §6 Configuration Reference

| Config Area | File | Notes |
|---|---|---|
| prompts | `examples/LTCMCollapse/RuleLLM/prompts.py` | standardized dual-section prompts |
| model | `configs/LTCMCollapse/RuleLLM/players.yml` | `ark/doubao-seed-2-0-mini-260428` |
| rounds | `configs/LTCMCollapse/RuleLLM/simulation.yml` | 200 configured rounds |

## §7 Expected Behavior Patterns

RuleLLM should be closer to Rule than the persona-only LLM variant. Deviations are expected from natural-language interpretation and stochastic model output, but the sign and rough scale of decisions should align with the embedded rule descriptions.

## §8 Validation Checklist

- System prompts contain `== PERSONA ==` and `== DECISION RULES ==`.
- Static API contract audit reports zero issues.
- Full 200-round rerun is required after prompt standardization.
- Level-2 quality audit must pass before accepting the new sample.

## §9 References

- `../simulation-bases.md`
- `../analysis-bases.md`
- `prompts.py`
- `players.py`
