# ArchegosCollapse LLM — Implementation Explanation

## §1 Overview

| Item                                   | Description                                                                                                                                                        |
|----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**                            | LLM (persona-driven stochastic)                                                                                                                                    |
| **Implements**                         | `../simulation-bases.md`                                                                                                                                           |
| **Decision Logic**                     | LLM prompts with behavioral personas — no explicit rules; all decisions from LLM reasoning                                                                         |
| **Key Difference from Other Variants** | Investor decisions are stochastic LLM-generated; cascade timing varies run-to-run due to persona psychology (denial, panic, rationalization)                       |
| **Primary Research Contribution**      | Do LLM-simulated investor personas reproduce the psychological dynamics of the Archegos collapse: denial before capitulation, panic selling, opportunistic buying? |

---

## §2 Theory → Implementation Mapping

### ConcentratedFund: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.1 — ConcentratedFund)*

| Theory Component                                              | Implementation                                                                          |
|---------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| TRS leverage psychology → simulation-bases.md §4 LLM Persona  | `LLM_CONCENTRATED_FUND_SYS` in `prompts.py`; "denial is your first response"            |
| Denial response to margin pressure → sim-bases §4 LLM Persona | Prompt: "you are slow to react to margin pressure — denial is your first response"      |
| Large abrupt selling when unavoidable → sim-bases §4          | Prompt: "when margin calls become unavoidable, your forced selling is large and abrupt" |
| Position size range 40%–60% → sim-bases §4 LLM Persona        | No hardcoded rule; LLM must infer sell size from context and persona framing            |
| Prompt constant → `prompts.py`                                | `LLM_CONCENTRATED_FUND_SYS` loaded via `extras.llm.sys_message` in `players.yml`        |

### PrimeBroker1: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.2 — PrimeBroker1)*

| Theory Component                                              | Implementation                                                                         |
|---------------------------------------------------------------|----------------------------------------------------------------------------------------|
| First-mover competitive psychology → sim-bases §4 LLM Persona | `LLM_PRIME_BROKER1_SYS`: "speed is paramount"; "first to act preserves the most value" |
| Aggressive, decisive action → sim-bases §4 LLM Persona        | "you liquidate aggressively and quickly"; "act decisively when risk thresholds breach" |
| Sell 32%–48% of position → sim-bases §4 LLM Persona           | LLM infers quantity from persona; no formula in prompt                                 |
| Prompt constant                                               | `LLM_PRIME_BROKER1_SYS` in `prompts.py`                                                |

### PrimeBroker2: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.3 — PrimeBroker2)*

| Theory Component                                   | Implementation                                                          |
|----------------------------------------------------|-------------------------------------------------------------------------|
| Second-mover reluctance → sim-bases §4 LLM Persona | `LLM_PRIME_BROKER2_SYS`: "slower decision process, reluctant initially" |
| Accepts price penalty → sim-bases §4 LLM Persona   | "accepts price penalties to complete liquidation quickly"               |
| Amplifying role → sim-bases §4                     | "your selling extends liquidation pressure started by the first broker"    |

### BlockTradeBuyer: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.4 — BlockTradeBuyer)*

| Theory Component                                          | Implementation                                                                            |
|-----------------------------------------------------------|-------------------------------------------------------------------------------------------|
| Opportunistic discount-seeking → sim-bases §4 LLM Persona | `LLM_BLOCK_TRADE_BUYER_SYS`: "wait for dislocations — when forced sellers must unload"    |
| Deploy fixed capital ratio → sim-bases §4 LLM Persona     | "deploy capital aggressively"; LLM decides actual ratio based on perceived discount depth |
| Stabilizing force → sim-bases §4                          | "you are the stabilizing buyer that limits forced-selling pressure"                        |

### InformationTrader: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.5 — InformationTrader)*

| Theory Component                                           | Implementation                                                                          |
|------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| Order-flow detection capability → sim-bases §4 LLM Persona | `LLM_INFORMATION_TRADER_SYS`: "you specialize in reading unusual order flow patterns"   |
| Front-run then rebuild pattern → sim-bases §4 LLM Persona  | "sell exposure ahead of the selling wave"; "buy back exposure when stabilized"          |
| Amplifies then aids price discovery → sim-bases §4         | "your front-running amplifies the initial decline but helps price discovery"            |

---

## §3 Market Mechanism Implementation

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) + λ × D(t) + γ × [F − P(t)] + ε(t)
```

Implemented in: `players.py → Market` class (re-used from `Rule.players` via import):
```python
from examples.ArchegosCollapse.Rule.players import Market
```

The Market class is **identical** to the Rule variant. Only the investor classes differ.

Code translation (same as Rule variant):

| sim-bases variable | Python variable                      | Config path                   | Value |
|--------------------|--------------------------------------|-------------------------------|-------|
| `λ`                | `price_impact`                       | `extras["price_impact"]`      | 0.03  |
| `γ`                | `mean_reversion`                     | `extras["mean_reversion"]`    | 0.01  |
| `F`                | `fundamental`                        | `extras["fundamental_value"]` | 100.0 |
| `D(t)`             | `net_demand = buy_qty − sell_qty`    | computed from orders          | —     |
| `ε(t)`             | `noise = random.gauss(0, noise_std)` | `extras["noise_std"]`         | 0.015 |

LLM variant JSON parsing: `parse_llm_response_with_thinking()` in `examples/llm_utils.py` parses `<decision>{...}</decision>` tag.

Deviations from simulation-bases.md design: None in market mechanics. Investor decisions stochastic.

---

## §4 Variant-Specific Features

*(Reference: simulation-bases.md §9 — LLM variant entry)*

**Persona-only prompts**: No explicit thresholds in any system prompt. The LLM must infer when to sell and how much based purely on the persona framing and the market state information in the user template. This tests whether LLM behavioral descriptions reproduce threshold-like behavior organically.

**User template variables**: `LLM_USER_TEMPLATE` provides `{round}`, `{price}`, `{prev_price}`, `{fundamental}`, `{deviation}`, `{cash}`, `{position}`, `{portfolio_value}` — computed in `players.py` before the LLM call.

**Stochastic cascade timing**: Each LLM call is independent; the ConcentratedFund persona may "hold" several rounds after margin pressure appears (denial phase) before finally selling. This makes cascade onset variable across runs.

**JSON parsing failure handling**: `LLMInvestor.decide()` retries malformed or
transient failures up to three times. If no valid canonical decision is
available after retries, the row fails loudly with `RuntimeError`; it does not
silently substitute a hold action.

**API key**: `ARK_API_KEY` (ByteDance Doubao) must be set as environment variable; loaded via `load_dotenv()` in `perceive()`.

---

## §5 Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║                              ROUND N                                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  Market.perceive() / decide() / act()                                 ║
║    [Rule-identical price formula — imported from Rule.players]        ║
║    → broadcasts {price, prev_price, fundamental, deviation, round}    ║
║                                                                       ║
║  Each LLMInvestor.perceive():                                         ║
║    → receives market data, updates state                              ║
║                                                                       ║
║  Each LLMInvestor.decide():                                           ║
║    → builds user_message from LLM_USER_TEMPLATE                      ║
║    → calls LangChainAPIInference(sys_prompt, user_message)  ──→ LLM  ║
║    → parses <decision>{"action","bid_price","quantity",...}</decision> ║
║    → returns order dict                                               ║
║                                                                       ║
║  ConcentratedFund:  denial? → hold / panic? → SELL large block       ║
║  PrimeBroker1:      speed urgency → SELL aggressively                ║
║  PrimeBroker2:      delayed but ultimately SELL at worse price       ║
║  BlockTradeBuyer:   discount-seeking → BUY on dislocation            ║
║  InformationTrader: signal detection → SELL / rebuild exposure → BUY ║
║         │                                                             ║
║         └──── send orders → Market [next round]                       ║
╚══════════════════════════════════════════════════════════════════════╝

LLM API Call Flow:
  LLMInvestor.decide()
    ├── sys_prompt = load_prompt(extras["llm"]["sys_message"])
    ├── user_msg  = LLM_USER_TEMPLATE.format(**state)
    └── InferInput(sys=sys_prompt, user=user_msg)
          → LangChainAPIInference → API → response
          → parse_llm_response_with_thinking(response)
          → {"action", "bid_price", "quantity", "reasoning"}
```

---

## §6 Configuration Reference

Key Configuration Parameters (`configs/ArchegosCollapse/LLM/players.yml`):

| Parameter | Config Path | Value | Design Justification |
|---|---|---|---|
| `price_impact` | `extras.price_impact` | 0.03 | Same as Rule — comparable cascade mechanics |
| `mean_reversion` | `extras.mean_reversion` | 0.01 | Same as Rule — enables cascade persistence |
| `sys_message` | `extras.llm.sys_message` | `examples.ArchegosCollapse.LLM.prompts:LLM_*_SYS` | Module path for LLM persona; loaded by `load_prompt()` |
| `user_message` | `extras.llm.user_message` | `examples.ArchegosCollapse.LLM.prompts:LLM_USER_TEMPLATE` | Module path for market-state user template |
| `lm_name` | `extras.llm.lm_name` | `ark/doubao-seed-2-0-mini-260428` | ByteDance Ark Doubao model |
| `temperature` | `extras.llm.generation_config.temperature` | 0.4-0.7 | Agent-specific stochasticity — reproduces persona variability |

---

## §7 Running Instructions

```bash
export ARK_API_KEY="your-bytedance-ark-api-key"
python examples/ArchegosCollapse/LLM/run_archegsoscollapse_llm.py \
    -c configs/ArchegosCollapse/LLM/simulation.yml
```

Required environment variables:
- `ARK_API_KEY`: ByteDance Doubao API key (required for all LLM calls)

Expected runtime: ~5–20 minutes for 200 rounds (depends on API latency, 5 LLM calls per round)

Output location: `EXPERIMENT/ArchegosCollapse/LLM/`

---

## §8 Expected Behavior Patterns

| Phase        | Rounds | Expected Agent Behavior                                                                    | Expected Price Dynamics                                         |
|--------------|--------|--------------------------------------------------------------------------------------------|-----------------------------------------------------------------|
| Pre-Cascade  | 1–15   | ConcentratedFund holds despite pressure (denial); PrimeBrokers monitor; InfoTrader watches | Price near 100 with noise; LLM may hold longer than Rule        |
| Denial Phase | 5–20   | ConcentratedFund resists selling; LLM persona produces "this is temporary" reasoning       | Slower cascade onset vs Rule; deviation builds gradually        |
| Panic Onset  | 15–30  | ConcentratedFund finally sells large block; PrimeBroker1 liquidates; InfoTrader shorts     | Sharp drop; cascade onset round later and more variable vs Rule |
| Peak Cascade | 25–45  | PrimeBroker2 forced to sell at worse prices; LLM may show "panic" reasoning patterns       | Deeper trough if denial delayed selling; deviation −20% to −40% |
| Recovery     | 40–100 | BlockTradeBuyer deploys aggressively; InfoTrader covers; LLM "recovery" reasoning          | Gradual mean reversion; LLM recovery timing more variable       |

---

## §9 References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- TRS leverage / ConcentratedFund denial psychology → `simulation-bases.md §2, §4 — ConcentratedFund LLM Persona`
- First-mover prime broker competitive psychology → `simulation-bases.md §2, §4 — PrimeBroker1 LLM Persona`
- Second-mover acceptance of price penalty → `simulation-bases.md §2, §4 — PrimeBroker2 LLM Persona`
- Opportunistic block buyer at discount → `simulation-bases.md §2, §4 — BlockTradeBuyer LLM Persona`
- Order-flow detection short-then-cover → `simulation-bases.md §2, §4 — InformationTrader LLM Persona`
- Price formula → `simulation-bases.md §3.1`
- LLM variant stochastic cascade timing → `simulation-bases.md §9 (LLM column)`
