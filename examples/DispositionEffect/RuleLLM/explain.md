# DispositionEffect RuleLLM — Implementation Explanation

## 1. Overview

RuleLLM combines the deterministic decision branches in `Rule/players.py` with an LLM explanation and a bounded sizing choice. The rule selects buy, sell, or hold; the model may vary a non-zero quantity by at most ±20%. `BaseLLMInvestor._rule_quantity()` and `_apply_constraints()` enforce that contract after parsing.

| Item | Value |
|---|---|
| Variant | RuleLLM |
| Environment | Rule-based `Market` |
| Agents | Disposition-biased, rational, tax-aware, index holder, institutional |
| Output contract | `<analysis>...</analysis><decision>{JSON}</decision>` |
| Configuration | `configs/DispositionEffect/RuleLLM/*.yml` |

## 2. Theory → Implementation Mapping

| Root design | Runtime class | Rule implementation | Prompt |
|---|---|---|---|
| §4.1 DispositionInvestor | `RuleLLMDispositionBiased` | `_rule_quantity()`: gain/loss thresholds, asymmetric sell fractions, reference-band buy | `RULELLM_DISPOSITION_BIASED_SYS` |
| §4.2 RationalInvestor | `RuleLLMRationalInvestor` | `_rule_quantity()`: target allocation, tolerance band, rebalance speed | `RULELLM_RATIONAL_SYS` |
| §4.3 TaxAwareInvestor | `RuleLLMTaxAwareInvestor` | `_rule_quantity()`: harvest losses and defer gains | `RULELLM_TAX_AWARE_SYS` |
| §4.4 IndexHolder | `RuleLLMIndexHolder` | `_rule_quantity()` always returns zero | `RULELLM_INDEX_HOLDER_SYS` |
| §4.5 InstitutionalInvestor | `RuleLLMInstitutionalInvestor` | `_rule_quantity()`: symmetric threshold sales | `RULELLM_INSTITUTIONAL_SYS` |

All prompts contain non-empty `PERSONA` and `DECISION RULES` sections. They expose exactly `action`, `bid_price`, `quantity`, and `reasoning`; the shared parser additionally returns the text inside `<analysis>`.

## 3. Environment Mechanism Implementation

`Market.perceive()` collects signed quantities. `Market.decide()` applies the §3 state law

```text
price(t+1) = max(1, price(t) + price_impact*net_demand
                 + mean_reversion*(fundamental-price(t)) + noise + news)
```

and broadcasts `price`, `prev_price`, `return`, `return_pct`, `volume`, `net_demand`, `news_shock`, and `round`. Every coefficient is loaded fail-fast from `players.yml`.

## 4. RuleLLM Variant-Specific Features

1. The system prompt supplies persona and explicit quantitative rules.
2. `LangChainAPIInference` receives one `InferInput` and returns the tagged response.
3. `parse_llm_response_with_thinking()` validates the canonical response structure.
4. `_rule_quantity()` fixes direction; the parsed magnitude is clamped to 80–120% of the deterministic quantity.
5. `_apply_constraints()` prevents overspending, overselling, and position-cap violations.
6. Trades execute at the broadcast market price, not an arbitrary model-proposed price.

## 5. Architecture

```text
Market broadcast
  -> BaseLLMInvestor.perceive (portfolio + market state)
  -> prompt.py persona + decision rules
  -> LangChainAPIInference
  -> tagged-response parser
  -> deterministic direction + ±20% sizing clamp
  -> solvency/inventory constraints
  -> investor order -> Market
```

The LLM client is removed during Ray serialization and reconstructed from the required `lm_name` and `generation_config` fields.

## 6. Configuration Reference

`players.yml` contains one entry for every §4 archetype. Market defaults trace to §6; agent thresholds and endowments trace to the corresponding §4 block or §6. Each LLM block requires `sys_message`, `user_message`, `lm_name`, `max_retries`, and `generation_config`.

`topology.yml` lists the expanded runtime identities. `simulation.yml` controls rounds, output paths, Ray resources, and communication storage.

## 7. Running Instructions

From the repository root:

```powershell
.\.venv\Scripts\python.exe examples\DispositionEffect\RuleLLM\run_disposition_rulellm.py `
  -c configs\DispositionEffect\RuleLLM\simulation.yml -r 5
```

Set `ARK_API_KEY` (or place it in `.env`) before a live run. Outputs are written under `EXPERIMENT/DispositionEffect/RuleLLM/`.

Run analysis after records exist:

```powershell
.\.venv\Scripts\python.exe examples\DispositionEffect\RuleLLM\analysis.py `
  -c configs\DispositionEffect\RuleLLM\simulation.yml
```

## 8. Expected Behavior Patterns

- Disposition-biased agents sell winners more aggressively than losers.
- Rational agents rebalance independently of purchase-price framing.
- Tax-aware agents raise loss realization through harvesting.
- Index holders produce zero turnover.
- Institutional agents use the same sale fraction on either threshold branch.
- Every non-zero RuleLLM order stays within ±20% of its Rule counterpart before portfolio constraints.

## 9. References

Theory and DOI references are centralized in `simulation-bases.md` §§2 and 4. Metric references are centralized in `analysis-bases.md` §2.
