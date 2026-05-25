# GamblerFallacy Rule — Implementation Explanation

## §1 Variant Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Implements | `../simulation-bases.md` |
| Decision Logic | Deterministic threshold rules over deviation from fundamental value |
| Key Difference from Other Variants | No LLM or retrieval calls; all orders come from fixed formulas in `players.py`. |
| Primary Research Contribution | Establishes the baseline for streak-based bias, hot-hand momentum, and rational correction. |
| Files | `players.py`, `run_gamblerfallacy.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory → Implementation Mapping

### StreakReversalTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.1`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.1.2 | Class: `StreakReversalTrader`; docstring cites `simulation-bases.md §4.1`. |
| Behavioral mechanism → sim-bases §4.1.4.2 | `decide()` activates when `abs(deviation) > 0.02`. |
| Mathematical model → sim-bases §4.1.4.3 | Quantity is `min(800, int(abs(deviation) * 5000))`; trades are bounded by cash and position. |
| State variables → sim-bases §4.1.4.3 | `cash`, `position`, `price`, `fundamental`, and `deviation` are initialized in `perceive()`. |
| Parameters → sim-bases §6 | Portfolio and market baselines are loaded from `players.yml`. |
| Activation scenarios → sim-bases §4.1.3 | Activates when a streak-like deviation becomes salient. |

### HotHandTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.2`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.2.2 | Class: `HotHandTrader`; docstring cites `simulation-bases.md §4.2`. |
| Behavioral mechanism → sim-bases §4.2.4.2 | Uses the same deviation-triggered structure to represent continuation belief. |
| Mathematical model → sim-bases §4.2.4.3 | Uses 2% activation, deviation-proportional sizing, and 800-share cap. |
| State variables → sim-bases §4.2.4.3 | Reads current market and portfolio fields from `custom_state`. |
| Parameters → sim-bases §6 | Initial portfolio and market reference values are config supplied. |
| Activation scenarios → sim-bases §4.2.3 | Activates in streak-active states rather than near-fundamental quiet states. |

### IndependentAssessor: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.3`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.3.2 | Class: `IndependentAssessor`; docstring cites `simulation-bases.md §4.3`. |
| Behavioral mechanism → sim-bases §4.3.4.2 | Treats sequential outcomes as independent and trades against mispricing. |
| Mathematical model → sim-bases §4.3.4.3 | Activates at `abs(deviation) > 0.05` with a 500-share cap. |
| State variables → sim-bases §4.3.4.3 | Uses current price, fundamental, deviation, cash, and position. |
| Parameters → sim-bases §6 | Runtime values come from `players.yml`. |
| Activation scenarios → sim-bases §4.3.3 | Waits for larger deviations before rational correction. |

### Arbitrageur: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.4`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.4.2 | Class: `Arbitrageur`; docstring cites `simulation-bases.md §4.4`. |
| Behavioral mechanism → sim-bases §4.4.4.2 | Exploits streak-driven mispricing through contrarian trades. |
| Mathematical model → sim-bases §4.4.4.3 | Uses the same 5% threshold and 500-share cap as the rational correction force. |
| State variables → sim-bases §4.4.4.3 | Reads broadcast market deviation directly. |
| Parameters → sim-bases §6 | Portfolio calibration is config supplied. |
| Activation scenarios → sim-bases §4.4.3 | Activates when arbitrage opportunity exceeds noise-trader risk. |

### NoiseTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.5`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.5.2 | Class: `NoiseTrader`; docstring cites `simulation-bases.md §4.5`. |
| Behavioral mechanism → sim-bases §4.5.4.2 | Randomly supplies background liquidity. |
| Mathematical model → sim-bases §4.5.4.3 | Random direction and size are bounded by cash and holdings. |
| State variables → sim-bases §4.5.4.3 | Uses portfolio constraints in `custom_state`. |
| Parameters → sim-bases §6 | Initial values are config supplied. |
| Activation scenarios → sim-bases §4.5.3 | Can trade in any round independently of streak signal. |

## §3 Market Mechanism Implementation

Formula source: `simulation-bases.md §3.1`.

```text
P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
```

Implemented in `players.py → Market.decide()`. The market broadcasts `price`, `fundamental`, `deviation`, and `round`; investors return `order` payloads with `action`, `bid_price`, `quantity`, `reasoning`, `agent_type`, `strategy`, and sender identity.

## §4 Rule Variant-Specific Features

- Streak-biased agents activate at smaller deviations than rational correction agents.
- Legacy inline thresholds are documented as current runtime truth rather than silently redesigned.

## §5 Architecture Diagram

```text
Market broadcast -> Rule investors -> order payloads -> Market.clear_market() -> next broadcast
```

## §6 Configuration Reference

| Config File | Runtime Role |
|---|---|
| `configs/GamblerFallacy/Rule/simulation.yml` | 200-round run and Ray settings |
| `configs/GamblerFallacy/Rule/players.yml` | Market and investor class paths plus portfolio settings |
| `configs/GamblerFallacy/Rule/topology.yml` | Star topology |
| `configs/GamblerFallacy/Rule/persona.yml` | Shared storage/proxy settings |

## §7 Expected Runtime Outputs

Full runs should produce 200 rounds, market price history, and canonical order records for all configured investors.

## §8 Validation Checklist

- `players.py` and `analysis.py` compile.
- Dry-run discovers `GamblerFallacy__Rule`.
- Preflight validates class paths, runner, total rounds, and topology.
- Runtime logic should remain stable unless a documented mechanism or contract defect is found.

## §9 Cross-Variant Comparison Notes

Rule provides the baseline for comparing whether LLM reasoning, rule-embedded prompts, or RAG context changes streak asymmetry, momentum demand, correction efficiency, and wealth distribution.
