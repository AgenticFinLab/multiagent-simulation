# FramingEffect Rule — Implementation Explanation

## §1 Variant Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Implements | `../simulation-bases.md` |
| Decision Logic | Deterministic threshold rules over price deviation |
| Key Difference from Other Variants | No LLM or retrieval calls; all investor actions are produced by `players.py` formulas. |
| Primary Research Contribution | Establishes the baseline framing-distortion dynamics against which LLM, RuleLLM, and RAG are compared. |
| Files | `players.py`, `run_framingeffect.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory → Implementation Mapping

### GainFrameFollower: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.1`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.1.2 | Class: `GainFrameFollower` in `players.py`; docstring cites `simulation-bases.md §4.1`. |
| Behavioral mechanism → sim-bases §4.1.4.2 | `decide()` reacts once `abs(deviation) > 0.02`. |
| Mathematical model → sim-bases §4.1.4.3 | Quantity is `min(800, int(abs(deviation) * 5000))`; positive deviation buys, negative deviation sells. |
| State variables → sim-bases §4.1.4.3 | `cash`, `position`, `price`, `fundamental`, and `deviation` are initialized in `perceive()`. |
| Parameters → sim-bases §6 | Baseline cash, position, price, and fundamental are loaded from `players.yml`. |
| Activation scenarios → sim-bases §4.1.3 | Activates when the market frame is salient enough to move beyond the 2% threshold. |

### LossFrameReactor: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.2`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.2.2 | Class: `LossFrameReactor`; docstring cites `simulation-bases.md §4.2`. |
| Behavioral mechanism → sim-bases §4.2.4.2 | `decide()` uses the same market deviation signal but represents the loss-frame-reactive biased population. |
| Mathematical model → sim-bases §4.2.4.3 | Threshold and size formula match the biased-trader baseline: 2% activation and 800-share cap. |
| State variables → sim-bases §4.2.4.3 | Portfolio state and current market fields are read from `custom_state`. |
| Parameters → sim-bases §6 | Portfolio calibration is loaded from `configs/FramingEffect/Rule/players.yml`. |
| Activation scenarios → sim-bases §4.2.3 | Activates in materially framed gain/loss states rather than quiet near-fundamental states. |

### FrameInvariantTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.3`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.3.2 | Class: `FrameInvariantTrader`; docstring cites `simulation-bases.md §4.3`. |
| Behavioral mechanism → sim-bases §4.3.4.2 | Ignores presentation frame and trades against fundamental mispricing. |
| Mathematical model → sim-bases §4.3.4.3 | Activates at `abs(deviation) > 0.05`; buys undervaluation and sells overvaluation. |
| State variables → sim-bases §4.3.4.3 | Uses current `price`, `fundamental`, `deviation`, `cash`, and `position`. |
| Parameters → sim-bases §6 | Baseline portfolio values are loaded from config. |
| Activation scenarios → sim-bases §4.3.3 | Waits for larger mispricing before supplying rational correction. |

### ArbitrageFramer: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.4`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.4.2 | Class: `ArbitrageFramer`; docstring cites `simulation-bases.md §4.4`. |
| Behavioral mechanism → sim-bases §4.4.4.2 | Trades against framing-induced price deviation. |
| Mathematical model → sim-bases §4.4.4.3 | Uses the same 5% contrarian threshold and 500-share cap as the rational correction force. |
| State variables → sim-bases §4.4.4.3 | Reads market deviation from the broadcast rather than recomputing an alternative signal. |
| Parameters → sim-bases §6 | Portfolio calibration is config supplied. |
| Activation scenarios → sim-bases §4.4.3 | Activates when framing mispricing is large enough to justify arbitrage risk. |

### NoiseTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.5`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.5.2 | Class: `NoiseTrader`; docstring cites `simulation-bases.md §4.5`. |
| Behavioral mechanism → sim-bases §4.5.4.2 | Randomly trades with fixed participation probability. |
| Mathematical model → sim-bases §4.5.4.3 | Random action and quantity provide background liquidity without directional framing logic. |
| State variables → sim-bases §4.5.4.3 | Uses portfolio constraints to cap random buy and sell orders. |
| Parameters → sim-bases §6 | Initial portfolio values are loaded from config. |
| Activation scenarios → sim-bases §4.5.3 | May trade in any round independent of framing state. |

## §3 Market Mechanism Implementation

Formula source: `simulation-bases.md §3.1`.

```text
P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
```

Implemented in `players.py → Market.decide()`.

| sim-bases symbol | Python variable | Config path |
|---|---|---|
| `lambda` | `price_impact` | `market.config.extras.price_impact` |
| `gamma` | `mean_reversion` | `market.config.extras.mean_reversion` |
| `F` | `fundamental` | `market.config.extras.fundamental_value` |
| `epsilon` | `noise` | `market.config.extras.noise_std` |
| `D(t)` | `net_demand` | computed from inbound orders |

The market broadcasts `price`, `fundamental`, `deviation`, and `round` to all investors.

## §4 Rule Variant-Specific Features

- Deterministic baseline: investors do not call external models.
- Biased traders activate earlier than rational traders, matching the phenomenon design in `simulation-bases.md §4`.
- The noise trader is the only stochastic investor and supplies non-informational liquidity.
- Runtime logic should remain stable unless a documented mechanism or contract defect is found.

## §5 Architecture Diagram

```text
Market broadcast(price, fundamental, deviation, round)
        |
        v
GainFrameFollower / LossFrameReactor / FrameInvariantTrader / ArbitrageFramer / NoiseTrader
        |
        v
order(action, quantity, agent_type)
        |
        v
Market.clear_market() -> next price
```

## §6 Configuration Reference

| Config File | Runtime Role |
|---|---|
| `configs/FramingEffect/Rule/simulation.yml` | 200-round run settings, Ray namespace, communication settings |
| `configs/FramingEffect/Rule/players.yml` | Market and investor class paths, portfolio parameters, price-impact parameters |
| `configs/FramingEffect/Rule/topology.yml` | Star topology: market broadcasts, investors return orders |
| `configs/FramingEffect/Rule/persona.yml` | Shared storage and proxy settings |

## §7 Expected Runtime Outputs

- Market records should include 200 price updates in full experiments.
- Investor orders should include `action`, `quantity`, `agent_type`, and sender identity.
- Analysis should read `price_history`, compute framing deviation metrics, and create the price-dynamics figure.

## §8 Validation Checklist

- `players.py` imports and compiles.
- `analysis.py` exposes `load_simulation_data`, `calculate_metrics`, and `create_visualizations`.
- Dry-run discovers `FramingEffect__Rule`.
- Preflight reports valid classes, runner, config load, and 200 rounds.
- Market logic and order semantics should remain stable across documentation-only updates.

## §9 Cross-Variant Comparison Notes

Rule is the baseline for comparing whether persona-only LLM reasoning, rule-embedded LLM reasoning, or retrieval-augmented reasoning changes framing-deviation intensity, persistence, and wealth redistribution.
