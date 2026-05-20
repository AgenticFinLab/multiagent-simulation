# Market Crash LLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | LLM |
| Simulation | Market Crash |
| Decision Mechanism | LLM-generated trading orders with action, bid_price, quantity, and reasoning |
| Theory Reference | `examples/MarketCrash/simulation-bases.md` |
| Market Broadcast | `configs/MarketCrash/LLM/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

### §2.1 RiskParityFund (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `LLMRiskParityFund` in `examples/MarketCrash/LLM/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/MarketCrash/LLM/players.yml` through `extras`. |
| Variant-specific decision mechanism | LLM-generated trading orders with action, bid_price, quantity, and reasoning. |
### §2.2 LeveragedHedgeFund (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `configured player class family` in `examples/MarketCrash/LLM/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/MarketCrash/LLM/players.yml` through `extras`. |
| Variant-specific decision mechanism | LLM-generated trading orders with action, bid_price, quantity, and reasoning. |
### §2.3 MarketMaker (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `LLMMarketMaker` in `examples/MarketCrash/LLM/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/MarketCrash/LLM/players.yml` through `extras`. |
| Variant-specific decision mechanism | LLM-generated trading orders with action, bid_price, quantity, and reasoning. |
### §2.4 PassiveInvestor (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `LLMInvestor` in `examples/MarketCrash/LLM/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/MarketCrash/LLM/players.yml` through `extras`. |
| Variant-specific decision mechanism | LLM-generated trading orders with action, bid_price, quantity, and reasoning. |
### §2.5 PanicSeller (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `LLMPanicSeller` in `examples/MarketCrash/LLM/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/MarketCrash/LLM/players.yml` through `extras`. |
| Variant-specific decision mechanism | LLM-generated trading orders with action, bid_price, quantity, and reasoning. |
### §2.6 BottomFisher (simulation-bases.md §4.6)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.6 | `LLMBottomFisher` in `examples/MarketCrash/LLM/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/MarketCrash/LLM/players.yml` through `extras`. |
| Variant-specific decision mechanism | LLM-generated trading orders with action, bid_price, quantity, and reasoning. |

## §3 Market Mechanism

The coordinator mechanism is the final implementation in `examples/MarketCrash/LLM/players.py` and its configured counterpart in `configs/MarketCrash/LLM/players.yml`. It broadcasts scenario state each round, receives agent decisions, updates state variables, and records the series required by `analysis-bases.md`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/MarketCrash/LLM/players.py` |
| Prompt module | `examples/MarketCrash/LLM/prompts.py` |
| Inference | Uses the project ARK LLM policy; RAG variants also use the project Hunyuan/LiteLLM embedding policy. |
| Output parsing | Explicit parser contract in players.py and prompts.py |
| Error handling | Deterministic config/schema errors fail fast; stochastic API parse fallback is allowed only when explicit, conservative, logged, and quality-audited. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/MarketCrash/LLM/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/MarketCrash/LLM/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/MarketCrash/LLM/topology.yml` | Message routing between coordinator and agents. |
| `configs/MarketCrash/LLM/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/MarketCrash/LLM/run_crash_llm.py -c configs/MarketCrash/LLM/simulation.yml
```

## §7 Expected Behavior

- The run records the full scenario state path for the configured round count.
- Agent decisions should exercise the mechanism defined in `simulation-bases.md §4`.
- API variants may show greater behavioral dispersion than the deterministic Rule baseline while preserving the same scenario contract.
- A successful full experiment must pass Level-1 execution review and then Level-2 structural quality review.

## §8 References

See `examples/MarketCrash/simulation-bases.md §2` for full DOI citations and mechanism references.

## §9 Variant Comparison

See `examples/MarketCrash/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
