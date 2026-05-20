# LTCMCollapse LLM — Implementation Explanation

## §1 Variant Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Implements | `../simulation-bases.md` |
| Decision Logic | persona-only LLM decisions using current market state |
| Key Difference | tests whether language agents reproduce LTCM-style stress behavior without executable rule formulas |
| Files | `players.py`, `prompts.py`, `run_ltcmcollapse_llm.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

| Investor | sim-bases Ref | Class | Prompt Constant | Implementation |
|---|---|---|---|---|
| ConvergenceArbitrageur | `§4.1` | `LLMConvergenceArbitrageur` | `LLM_CONVERGENCEARBITRAGEUR_PROMPT` | persona emphasizes spread convergence and leveraged sizing |
| LeverageTrader | `§4.2` | `LLMLeverageTrader` | `LLM_LEVERAGETRADER_PROMPT` | persona emphasizes margin calls and forced deleveraging |
| RiskManager | `§4.3` | `LLMRiskManager` | `LLM_RISKMANAGER_PROMPT` | persona emphasizes VaR/risk-limit cuts |
| LiquidityProvider | `§4.4` | `LLMLiquidityProvider` | `LLM_LIQUIDITYPROVIDER_PROMPT` | persona emphasizes market making and stress withdrawal |
| CentralBank | `§4.5` | `LLMCentralBank` | `LLM_CENTRALBANK_PROMPT` | persona emphasizes lender-of-last-resort support |

The LLM variant intentionally does not execute the Rule formulas. It supplies market state and personality instructions, then parses the returned decision JSON.

## §3 Market Mechanism Implementation

The market is imported from `examples.LTCMCollapse.Rule.players:Market`, so price formation is identical to Rule and follows `simulation-bases.md §3.1`.

Investor `decide()` builds a user message from:

- `round`
- `price`
- `fundamental`
- `deviation`
- `cash`
- `position`
- `portfolio_value`

## §4 Variant-Specific Features

LLM prompts define investor psychology without naming the historical event in the system prompt header. The output parser expects:

```xml
<analysis>...</analysis>
<decision>{"action": "buy|sell|hold", "bid_price": 100.0, "quantity": 1, "reasoning": "..."}</decision>
```

The actor retries parse failures up to three times and raises `RuntimeError` if no valid decision is produced. There is no silent fallback in this variant.

## §5 Architecture Diagram

```text
Market broadcast
  -> LLMInvestor.perceive()
  -> LLMInvestor.decide()
       -> LangChainAPIInference(system_prompt, user_message)
       -> parse_llm_response_with_thinking()
  -> LLMInvestor.act()
       -> emit standard order
```

## §6 Configuration Reference

| Config Area | File | Notes |
|---|---|---|
| model | `configs/LTCMCollapse/LLM/players.yml` | `ark/doubao-seed-2-0-mini-260428` |
| prompts | `examples/LTCMCollapse/LLM/prompts.py` | persona-only system prompts |
| rounds | `configs/LTCMCollapse/LLM/simulation.yml` | 200 configured rounds |

## §7 Expected Behavior Patterns

LLM agents may be more conservative or inconsistent than Rule agents, but valid samples should still show coherent stress responses: arbitrage opportunity recognition, margin caution, risk cuts, liquidity withdrawal, or intervention reasoning.

## §8 Validation Checklist

- Prompt references resolve from `players.yml`.
- Static API contract audit reports no missing fields.
- Level-2 LLM output quality audit reports low or zero parse failures/fallbacks.
- Existing `fix-scenarios` LLM full sample can be inherited if prompts and player code remain unchanged.

## §9 References

- `../simulation-bases.md`
- `../analysis-bases.md`
- `prompts.py`
- `players.py`
