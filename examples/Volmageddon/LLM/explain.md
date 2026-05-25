# Volmageddon LLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | LLM |
| Simulation | Volmageddon |
| Decision Mechanism | Persona-conditioned API decisions over current-market volatility quantities |
| Theory Reference | `examples/Volmageddon/simulation-bases.md` |
| Market Broadcast | `configs/Volmageddon/LLM/topology.yml` |

The LLM variant keeps Volmageddon's special current-market quantity schema:
API decisions emit `action`, `quantity`, and `reasoning`. They do not emit
`bid_price`, because the market clears directional quantities at the current
volatility proxy rather than matching limit orders.

## §2 Theory -> Implementation Mapping

### §2.1 ShortVolTrader (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Short-vol carry and stop-loss covering | `LLMShortVolTrader` uses `LLM_SHORT_VOL_TRADER_SYS` to reason as a carry seller exposed to volatility spikes. |
| Required config | Portfolio initialization and `agent_type: short_vol_trader` from `configs/Volmageddon/LLM/players.yml`. |
| Output contract | `<decision>` JSON contains `action`, `quantity`, and `reasoning`; parser fallback is explicit and auditable. |

### §2.2 VolETNManager (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Inverse-volatility product rebalancing | `LLMVolETNManager` reasons as a mechanical inverse-VIX product manager. |
| Required config | Portfolio initialization and `agent_type: vol_e_t_n_manager`. |
| Output contract | Quantity reflects rebalancing urgency; no `bid_price` is part of the runtime contract. |

### §2.3 LongVolHedger (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Long-volatility insurance and profit-taking | `LLMLongVolHedger` reasons about hedge accumulation and profit-taking. |
| Required config | Portfolio initialization and `agent_type: long_vol_hedger`. |
| Output contract | Quantity is constrained by cash and inventory after parsing. |

### §2.4 VolArbitrageur (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Dislocation arbitrage | `LLMVolArbitrageur` reasons about volatility proxy mispricing and mean reversion. |
| Required config | Portfolio initialization and `agent_type: vol_arbitrageur`. |
| Output contract | Decisions remain in the same current-market quantity schema. |

### §2.5 EquityTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Volatility-linked equity de-risking | `LLMEquityTrader` reasons about fundamental value and risk reduction. |
| Required config | Portfolio initialization and `agent_type: equity_trader`. |
| Output contract | Decisions are parsed, bounded, and recorded with reasoning and fallback metadata. |

## §3 Market Mechanism

The LLM variant reuses the Rule market. The only runtime difference is investor
decision generation: `LLMInvestor` builds a market-state prompt, calls the ARK
model configured in `players.yml`, parses a structured decision, constrains
quantity by cash/inventory, and emits an investor order.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/Volmageddon/LLM/players.py` |
| Prompt module | `examples/Volmageddon/LLM/prompts.py` |
| Inference | Project ARK model policy from `players.yml` |
| Output parsing | `parse_llm_quantity_response_with_thinking` plus required-field validation |
| Error handling | API call errors fail; stochastic parse failures can trigger explicit conservative hold fallback after retries |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/Volmageddon/LLM/simulation.yml` | 200-round simulation entry point and record path |
| `configs/Volmageddon/LLM/players.yml` | Class paths, role metadata, portfolio initialization, and LLM config |
| `configs/Volmageddon/LLM/topology.yml` | Market update and investor order routing |
| `configs/Volmageddon/LLM/persona.yml` | Persona and recording metadata |

## §6 Running Instructions

```bash
python examples/Volmageddon/LLM/run_volmageddon_llm.py -c configs/Volmageddon/LLM/simulation.yml
```

## §7 Expected Behavior

- The same five investor roles should remain identifiable in order payloads.
- LLM decisions may vary in urgency and quantity, but must preserve the
  `action`/`quantity`/`reasoning` schema.
- Parser fallback counts must be reviewed before accepting a full 200-round
  sample.

## §8 References

See `examples/Volmageddon/simulation-bases.md §2` and `§8`.

## §9 Variant Comparison

The LLM variant is compared against Rule to measure whether stochastic reasoning
changes spike timing, positive-feedback intensity, stabilizer activity, and
quality metrics without changing the market contract.
