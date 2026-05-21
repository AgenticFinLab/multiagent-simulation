# Volmageddon RuleLLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | RuleLLM |
| Simulation | Volmageddon |
| Decision Mechanism | Explicit rule prompts plus API reasoning over current-market volatility quantities |
| Theory Reference | `examples/Volmageddon/simulation-bases.md` |
| Market Broadcast | `configs/Volmageddon/RuleLLM/topology.yml` |

RuleLLM keeps the same special Volmageddon quantity schema as Rule and LLM:
`action`, non-negative `quantity`, `agent_type`, and API `reasoning`. It adds
prompt-level decision rules so stochastic outputs stay close to the deterministic
threshold logic.

## §2 Theory -> Implementation Mapping

### §2.1 ShortVolTrader (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Short-vol carry and stop-loss covering | `RuleLLMShortVolTrader` receives a persona section plus explicit stop-loss and short-carry decision rules. |
| Required config | Portfolio initialization and role metadata from `configs/Volmageddon/RuleLLM/players.yml`. |
| Output contract | Quantity-only `<decision>` JSON; conservative hold fallback is recorded if parsing fails after retries. |

### §2.2 VolETNManager (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Mechanical inverse-product rebalance | `RuleLLMVolETNManager` receives a rules section requiring buy pressure when positive deviation is large. |
| Required config | Portfolio initialization and `agent_type: vol_e_t_n_manager`. |
| Output contract | Uses `action`, `quantity`, and `reasoning`; no `bid_price`. |

### §2.3 LongVolHedger (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Hedge accumulation and spike profit-taking | `RuleLLMLongVolHedger` receives explicit rules for buying cheap volatility and trimming into spikes. |
| Required config | Portfolio initialization and `agent_type: long_vol_hedger`. |
| Output contract | Quantity is parsed and then constrained by cash/inventory. |

### §2.4 VolArbitrageur (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Large-dislocation arbitrage | `RuleLLMVolArbitrageur` receives explicit threshold and direction rules. |
| Required config | Portfolio initialization and `agent_type: vol_arbitrageur`. |
| Output contract | Quantity-only order sent to the shared market. |

### §2.5 EquityTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Volatility-linked risk control | `RuleLLMEquityTrader` receives explicit risk-reduction and mean-reversion rules. |
| Required config | Portfolio initialization and `agent_type: equity_trader`. |
| Output contract | Decisions are recorded with reasoning, analysis, and fallback metadata. |

## §3 Market Mechanism

The RuleLLM variant reuses the Rule market. Prompt rules constrain decisions,
but market clearing remains the same current-market quantity aggregation defined
in `simulation-bases.md §3`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/Volmageddon/RuleLLM/players.py` |
| Prompt module | `examples/Volmageddon/RuleLLM/prompts.py` |
| Inference | Project ARK model policy from `players.yml` |
| Output parsing | Required `action`, `quantity`, and `reasoning` validation |
| Error handling | Deterministic config/schema errors fail; stochastic parse fallback is explicit and auditable |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/Volmageddon/RuleLLM/simulation.yml` | 200-round simulation entry point and record path |
| `configs/Volmageddon/RuleLLM/players.yml` | Class paths, role metadata, portfolio initialization, and LLM config |
| `configs/Volmageddon/RuleLLM/topology.yml` | Market update and investor order routing |
| `configs/Volmageddon/RuleLLM/persona.yml` | Persona and recording metadata |

## §6 Running Instructions

```bash
python examples/Volmageddon/RuleLLM/run_volmageddon_rulellm.py -c configs/Volmageddon/RuleLLM/simulation.yml
```

## §7 Expected Behavior

- RuleLLM should be closer to Rule than unconstrained LLM on threshold timing
  and direction.
- API reasoning can vary, but the current-market quantity contract must remain
  valid.
- Any parser fallback must be rare, visible in payloads, and evaluated in
  Level-2 quality review.

## §8 References

See `examples/Volmageddon/simulation-bases.md §2` and `§8`.

## §9 Variant Comparison

RuleLLM is compared with Rule to test whether prompt-level rules preserve the
feedback mechanism, and with LLM to test whether explicit rules reduce
stochastic drift.
