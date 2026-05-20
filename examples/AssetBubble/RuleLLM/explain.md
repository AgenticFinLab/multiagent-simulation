# AssetBubble RuleLLM — Implementation Explanation

## §1 Overview

| Item                                   | Description                                                                                                                                                                                 |
|----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**                            | RuleLLM                                                                                                                                                                                     |
| **Implements**                         | `../simulation-bases.md`                                                                                                                                                                    |
| **Decision Logic**                     | Hybrid: LLM reasoning anchored to explicit quantitative rules (PERSONA + DECISION RULES dual-section prompts)                                                                               |
| **Key Difference from Other Variants** | Every system prompt embeds exact Rule-variant formulas (from `simulation-bases.md §4`) in plain text; LLM may adjust quantity ±20% but must follow rule sign and scale                      |
| **Primary Research Contribution**      | Isolates the effect of language reasoning: with identical quantitative constraints embedded in the prompt, does LLM reasoning alter phenomenon dynamics compared to the pure Rule baseline? |

---

## §2 Theory → Implementation Mapping

### Market: Theory → Implementation
*(Theory defined in `../simulation-bases.md §3`)*

| Theoretical Design Element                                 | Implementation                                                                             |
|------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| Price formation model → `simulation-bases.md §3.1`         | Identical to Rule variant; `Market` class copied from Rule `players.py`; formula unchanged |
| Bubble-prone parameter choice → `simulation-bases.md §3.1` | Same config values: `price_impact = 0.15`, `mean_reversion = 0.005`                        |
| Information broadcast design → `simulation-bases.md §3.3`  | Same `market_data` payload; adds `round` field for value investor frequency control        |
| All market mechanisms → `simulation-bases.md §3.2`         | Identical: price floor, short constraints, margin call all unchanged                       |

### Hybrid Investors: Theory → Implementation
*(Theory per investor defined in `../simulation-bases.md §4`)*

| Investor                 | Theory → `simulation-bases.md §4`                | PERSONA Source                         | DECISION RULES Source                                                          |
|--------------------------|--------------------------------------------------|----------------------------------------|--------------------------------------------------------------------------------|
| RuleLLMMomentumSpec (×5) | Greater Fool Theory → `§4 — MomentumSpeculator`  | `simulation-bases.md §4 — LLM Persona` | Exact momentum formula from `§4 — Rule-Based Behavior` + `§6` params           |
| RuleLLMRationalArb (×3)  | Limits to Arbitrage → `§4 — RationalArbitrageur` | `simulation-bases.md §4 — LLM Persona` | Deviation + cost_penalty formula from `§4` + max_short cap from `§6`           |
| RuleLLMNoiseTr (×2)      | Noise Trader Risk → `§4 — NoiseTrader`           | `simulation-bases.md §4 — LLM Persona` | Herding formula from `§4`; note: random_sentiment replaced by net_demand proxy |
| RuleLLMValueInv (×4)     | Value Investing → `§4 — FundamentalInvestor`     | `simulation-bases.md §4 — LLM Persona` | Frequency gate (every 5 rounds) + value deviation formula from `§4`            |
| RuleLLMLeveraged (×3)    | Leverage amplification → `§4 — LeveragedBuyer`   | `simulation-bases.md §4 — LLM Persona` | Margin call rule (highest priority) + leveraged buy formula from `§4`          |

**Core construction rule** (from Variant Construction Principles): The DECISION RULES section in every prompt reproduces the exact formulas from `simulation-bases.md §4 — Rule-Based Behavior`, expressed step-by-step in plain text. The LLM is instructed to follow the rule sign (buy/sell/hold) strictly, with at most ±20% quantity adjustment. If Rule parameters change in `simulation-bases.md §6`, the embedded prompt rules must be updated accordingly.

---

## §3 Table of Contents

1. [Design Motivation and Core Idea](#1-design-motivation-and-core-idea)
2. [Three-Variant Comparison Framework](#2-three-variant-comparison-framework)
3. [Directory Structure](#3-directory-structure)
4. [System Architecture and Data Flow](#4-system-architecture-and-data-flow)
5. [Market Coordinator](#5-market-coordinator)
6. [Five Hybrid Investor Agents](#6-five-hybrid-investor-agents)
7. [Prompt Design: PERSONA + DECISION RULES Dual-Section Structure](#7-prompt-design-persona--decision-rules-dual-section-structure)
8. [RuleLLMInvestor Base Class — Implementation Details](#8-rulellminvestor-base-class--implementation-details)
9. [Configuration System (players.yml)](#9-configuration-system-playersyml)
10. [Running and Output](#10-running-and-output)

---

## §4 Design Motivation and Core Idea

### Background

Pure rule-based agents (AssetBubble) and pure LLM agents (AssetBubble LLM) each have fundamental limitations:

| Approach                      | Strengths                                                         | Weaknesses                                                                            |
|-------------------------------|-------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| Pure rule-based (AssetBubble) | Interpretable, reproducible, fully grounded in financial formulas | No language reasoning, no contextual adaptability, mechanically rigid behavior        |
| Pure LLM (AssetBubble LLM)    | Natural language reasoning, strong contextual understanding       | No quantitative constraints, decision drift, difficult to align with financial theory |

### Solution: Hybrid Design

AssetBubble RuleLLM combines both approaches:

> **Each LLM agent's system prompt simultaneously contains:**
> 1. **PERSONA** — who the agent is: investment style, risk attitude, emotional traits
> 2. **DECISION RULES** — the exact quantitative rules extracted from the rule-based counterpart, expressed as plain-text formulas and thresholds

This allows the LLM to engage in natural language reasoning while remaining anchored to well-defined quantitative principles, preventing unconstrained drift.

### Core Innovation

```
Pure rule:  financial formula → deterministic output
Pure LLM:   Persona → free reasoning → output
Hybrid:     Persona + quantitative rules → LLM reasoning → constrained output
                              ↑
                 ±20% deviation allowed to preserve reasoning space
```

---

## §5 Three-Variant Comparison Framework

The project defines four variants in a progressive series, enabling systematic comparative research:

```
AssetBubble          ─── pure rule-based (baseline)
    ↓ add natural language reasoning
AssetBubble LLM       ─── pure LLM (persona only, no explicit rules)
    ↓ add quantitative rule constraints
AssetBubble RuleLLM   ─── hybrid (persona + rules embedded in prompt)
    ↓ add external knowledge retrieval
AssetBubble Rag       ─── hybrid + personal RAG knowledge library
```

All three variants share identical:
- Market price dynamics formula
- Total agent count (18 players)
- Initial cash and position settings
- Simulation length (100 rounds)

This ensures fair cross-variant comparison.

---

## §6 Directory Structure

```
examples/AssetBubble/RuleLLM/
├── __init__.py              # Module init
├── players.py               # Market + RuleLLMInvestor base class + 5 subclasses
├── prompts.py               # 5 system prompts + 1 shared user template
├── run_bubble_rulellm.py    # Simulation runner script
├── analysis.py              # Analysis script (delegates to AssetBubble/analysis.py)
└── explain.md               # This document

configs/AssetBubble/RuleLLM/
├── simulation.yml           # Global simulation settings (rounds, Ray config, etc.)
├── players.yml              # All agent definitions (parameters + LLM pointers)
├── topology.yml             # Star topology network
└── persona.yml              # Persistence, monitoring, communication settings
```

---

## §7 System Architecture and Data Flow

### Per-Round Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     GeneralSimulator                         │
│                                                             │
│   Round N                                                   │
│   ─────────────────────────────────────────────────────     │
│                                                             │
│   ① 17 Investors perceive() in parallel                     │
│      Receive market_data broadcast from previous round      │
│      Append new price to price_history                      │
│                                                             │
│   ② Market perceive()                                       │
│      Collect all investor orders from inbound messages      │
│                                                             │
│   ③ 17 Investors decide() in parallel                       │
│      Build prompt → call LLM → parse JSON → execute trade   │
│      Send bid_price / quantity order to Market              │
│                                                             │
│   ④ Market decide()                                         │
│      Aggregate net demand → apply price formula → broadcast │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Message Types

| Sender   | Receiver      | Payload                                                                      |
|----------|---------------|------------------------------------------------------------------------------|
| Market   | All Investors | `market_data`: price, fundamental, bubble_ratio, return_pct, net_demand, ... |
| Investor | Market        | `order`: bid_price, quantity, strategy, reasoning                            |

---

## §8 Market Coordinator

The Market is a pure rule-based component, identical to AssetBubble. It does not use an LLM.

### Price Dynamics Formula

```
P(t+1) = P(t) + λ × NetDemand + γ × [F(t) - P(t)] + ε
```

| Parameter | Name             | Config Value                      | Meaning                                                                    |
|-----------|------------------|-----------------------------------|----------------------------------------------------------------------------|
| λ         | `price_impact`   | 0.15                              | Price sensitivity to net demand (amplifies order flow)                     |
| γ         | `mean_reversion` | 0.005                             | Speed of correction toward fundamental value (very slow → bubbles persist) |
| F(t)      | fundamental      | starts at 100, grows ×1.001/round | Company intrinsic value (slow steady growth)                               |
| ε         | noise            | N(0, 0.3)                         | Random exogenous shock                                                     |

### Key Design: Deliberately Bubble-Prone Parameters

- `mean_reversion = 0.005` (extremely low) → price can deviate from fundamentals for extended periods
- `price_impact = 0.15` (relatively high) → demand shocks are amplified into large price moves
- These two parameters together ensure that when speculative demand accumulates, a bubble forms and persists

### Bubble Ratio Metric

```python
bubble_ratio = new_price / new_fundamental
```

- `> 1.0`: price above fundamental value (bubble territory)
- `< 1.0`: price below fundamental value (undervaluation)
- This metric is broadcast to all investors and embedded in each round's user prompt

---

## §9 Five Hybrid Investor Agents

### 6.1 RuleLLM Momentum Speculator — ×5

**Theoretical foundation**: Greater Fool Theory (Keynes "Beauty Contest")

**Core logic**: Ignores fundamental value entirely, trades purely on price momentum. Believes that as long as prices are rising, there will always be a buyer willing to pay more.

**Rule formula (embedded in prompt)**:
```
momentum = (current_price - moving_average_5) / moving_average_5

IF momentum > 0.01:
    quantity = 2.0 × momentum × 20 × 2.0    (cap: +100)
ELIF momentum < -0.02:
    quantity = 2.0 × momentum × 20           (floor: -80)
ELSE: hold
```

**LLM freedom**: may adjust final quantity by up to ±20% based on qualitative context

---

### 6.2 RuleLLM Rational Arbitrageur — ×3

**Theoretical foundation**: Limits to Arbitrage (Shleifer & Vishny, 1997)

**Core logic**: Prices must eventually return to fundamental value. However, short-selling costs and capital constraints prevent unlimited arbitrage — the market can remain irrational longer than the arbitrageur's capital can sustain.

**Rule formula (embedded in prompt)**:
```
deviation = (current_price - fundamental_value) / fundamental_value

IF deviation > 0.05:    (overvalued by more than 5% — short)
    cost_penalty = max(0.2, 1.0 - 2.0 × short_cost_rate × 10)
    short_size   = deviation × 20 × cost_penalty
    quantity     = -min(short_size, 30 - current_short_position)
    [if short_position >= 30: hold — hit short limit]

ELIF deviation < -0.05:    (undervalued by more than 5% — buy)
    quantity = min(abs(deviation) × 20, 30)

ELSE: hold
```

**Key constraint**: Maximum short position is 30 shares — enforces the "limits to arbitrage" mechanism

---

### 6.3 RuleLLM Noise Trader — ×2

**Theoretical foundation**: Noise Trader Risk (De Long, Shleifer, Summers & Waldmann, 1990)

**Core logic**: Trades based on market sentiment and crowd behavior. Does not analyze fundamentals. Driven by a mix of random sentiment noise and herding tendency.

**Rule formula (embedded in prompt)**:
```
random_sentiment ~ N(0, 0.3)              # internal mood fluctuation
herding_sentiment = 0.7 × price_return × 10   # crowd-following signal

total_sentiment = random_sentiment + herding_sentiment

IF total_sentiment > 0.1:
    quantity = total_sentiment × 15    (cap: +40)
ELIF total_sentiment < -0.1:
    quantity = total_sentiment × 15    (floor: -40)
ELSE: hold
```

**LLM adaptation note**: The LLM cannot literally sample a random number, so the prompt instructs it to use `net_demand` and `price_return` as proxies for `total_sentiment`

---

### 6.4 RuleLLM Value Investor — ×4

**Theoretical foundation**: Traditional value investing (Graham & Dodd, 1934; Buffett)

**Core logic**: Only trades when price significantly deviates from fundamental value, and only once every 5 rounds — embodying patience and discipline as a competitive edge.

**Rule formula (embedded in prompt)**:
```
# Frequency control (key differentiating feature)
IF round_number mod 5 ≠ 0:  hold this round (patience is the edge)

# Value deviation calculation
deviation = (fundamental_value - current_price) / current_price

quantity = 1.5 × deviation × 10    →   clamped to [-15, +15]
```

**Override rule**: When `deviation > 15%`, the agent must trade regardless of the round number (forced trigger for extreme mispricings)

---

### 6.5 RuleLLM Leveraged Buyer — ×3

**Theoretical foundation**: Leverage amplification + procyclical deleveraging

**Core logic**: Uses 3× leverage to amplify returns in bull markets. Once portfolio equity drops below 70% of initial value (margin call threshold), the agent is forced to deleverage immediately — no discretion.

**Rule formula (embedded in prompt)**:
```
equity_ratio = portfolio_value / 10000

# Margin call check — HIGHEST PRIORITY, non-negotiable
IF equity_ratio < 0.7:
    quantity = -(long_position × 0.5)    # forced: sell half the long position

# Normal leveraged trading (only if no margin call)
ELIF price_return > 0.005:
    quantity = price_return × 20 × 3    (cap: +60)

ELIF price_return < -0.01:
    quantity = price_return × 20         (floor: -40)

ELSE: hold
```

**Bubble amplification mechanism**: Leveraged buyers amplify buying on the way up → pushes price higher → attracts more momentum chasers → positive feedback loop; forced deleveraging on the way down amplifies crashes

---

## §10 Prompt Design: PERSONA + DECISION RULES Dual-Section Structure

This is the core innovation of AssetBubble RuleLLM. Every agent's system prompt is structured in two mandatory sections.

### System Prompt Structure (Momentum Speculator example)

```
You are an AGGRESSIVE MOMENTUM SPECULATOR in the stock market.

== PERSONA ==
Identity: High-risk, high-reward trend chaser driven by the Greater Fool Theory.
Belief: "I don't care about fundamental value — I care about momentum. Someone will
always buy higher than me."
Style: Extremely aggressive. You fear missing big moves more than you fear losses.
Risk tolerance: Very high. You use leverage and large position sizes (up to 100 shares).
Emotional state: Excited by rising prices, panic-driven selling on sharp reversals.

== DECISION RULES (from Momentum Speculator, Greater Fool Theory) ==

Step 1 — Compute short-term momentum:
    momentum = (current_price - moving_average_5) / moving_average_5
    ...

Step 2 — Decide action:
    IF momentum > 0.01: quantity = 2.0 × momentum × 20 × 2.0  (cap: +100)
    ...

== YOUR TASK ==
You MAY adjust the exact quantity up/down by up to 20% based on qualitative
judgment, but the sign (buy/sell/hold) and approximate scale MUST follow the rule above.
```

### Role of the PERSONA Section

- Tells the LLM "who you are", establishing a stable and consistent decision-making style
- Provides emotional anchors (e.g., "panic-driven selling on sharp reversals") that guide LLM reasoning toward realistic investor behavior
- Ensures consistent behavior even in ambiguous or under-specified market situations

### Role of the DECISION RULES Section

- Translates the rule-based agent's mathematical formula into natural language, step by step
- The LLM is instructed to follow the steps sequentially, computing intermediate values explicitly
- Provides explicit numerical bounds (cap / floor) to prevent the LLM from generating unreasonable quantities

### The ±20% Freedom Design

```
== YOUR TASK ==
You MAY adjust the exact quantity up/down by up to 20% based on qualitative
judgment, but the sign (buy/sell/hold) and approximate scale MUST follow the rule.
```

This design ensures:
- The LLM is not merely a mechanical "translator" of the rule agent — language reasoning space is preserved
- The LLM cannot drift arbitrarily far from the rule-implied behavior — quantitative constraints remain binding
- The ±20% range creates a measurable research variable: do LLMs systematically amplify or dampen bubble dynamics compared to their pure rule-based counterparts?

---

### Shared User Prompt Template

All five agent types use the same user message template each round:

```
== MARKET STATE (Round {round}) ==
- Current Price:           $120.50
- Previous Price:          $118.20
- This Round Return:       +1.94%
- Fundamental Value:       $102.30
- Price/Fundamental Ratio: 1.18x  (>1.0 = overvalued, <1.0 = undervalued)
- Trading Volume:          245.00 shares
- Net Demand:              +32.50  (positive = more buying than selling)
- Short-Selling Cost:      2.0% per round
- Recent Prices (last 5):  [115.0, 116.3, 117.8, 118.2, 120.5]

== YOUR PORTFOLIO ==
- Cash Available:          $8420.50
- Long Position:           15.00 shares
- Short Position:          0.00 shares
- Portfolio Value:         $10231.00

Apply your DECISION RULES above to this data and output your trade decision.

Respond with ONLY valid JSON:
{"action": "buy"|"sell"|"hold", "bid_price": <price>, "quantity": <shares, +buy/-sell>, "reasoning": "<brief>"}
```

**Key fields explained**:
- `{round}` — unique to AssetBubble RuleLLM (absent in AssetBubble LLM): allows the LLM to track round number, which the Value Investor needs to apply the every-5-rounds frequency rule
- `bubble_ratio` — pre-computed price/fundamental ratio, directly helping the LLM assess bubble severity without requiring it to compute the ratio itself
- `recent_prices` — last 5 prices maintained by `HistoryBuffer`, required by the Momentum Speculator to compute the 5-period moving average

---

## §11 RuleLLMInvestor Base Class — Implementation Details

### perceive() — Initialization and State Update

```python
async def perceive(self, observation, prev_result=None):
    round_num = observation.round
    self.state.custom_state["round"] = round_num

    # Initialize only on round 1 (when "cash" is not yet in custom_state)
    if "cash" not in self.state.custom_state:
        # 1. Initialize portfolio
        self.state.custom_state["cash"] = extras["initial_cash"]       # 10000.0
        self.state.custom_state["position"] = extras["initial_position"]   # 0.0

        # 2. Initialize LLM client (loads ARK_API_KEY from .env)
        load_dotenv()
        llm_client = LangChainAPIInference(lm_name=..., generation_config=...)
        self.state.custom_state["llm_client"] = llm_client

        # 3. Initialize HistoryBuffer (maintains recent_prices for MA5)
        self.state.custom_state["price_history"] = HistoryBuffer(...)

    # Every round: receive and store latest market data
    if observation.inbounds:
        market_data = inb.payload
        self.state.custom_state["market_data"] = market_data
        self.state.custom_state["price_history"].append(market_data["price"])
```

### decide() — LLM Call and Retry Mechanism

```python
async def decide(self):
    user_prompt = self._build_prompt(market_data)
    system_prompt = load_prompt(llm_config["sys_message"])

    max_retries = 3
    for attempt in range(max_retries):
        infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
        infer_output = llm_client.run([infer_input])
        try:
            # Note: lmbase run() returns InferBatchOutput (updated API)
            # Must use outputs[0].response, not direct .response
            decision = self._parse_llm_response(infer_output.outputs[0].response)
            break
        except ValueError as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"LLM failed after 3 attempts: {e}")
            # Retry automatically when LLM returns null fields
```

### _parse_llm_response() — Robust JSON Parsing

LLM output format is not guaranteed. The parser attempts the following fallback chain:

```
1. Direct json.loads() on the full response string
2. Extract content from ```json ... ``` code block
3. Extract content from the first {...} braces found
4. All attempts fail → raise ValueError (triggers retry)

Validation: bid_price / quantity / reasoning must all be non-None
→ any null field → raise ValueError (triggers retry; using 0 as fallback is rejected
  because it silently distorts agent behavior)
```

### \_\_getstate\_\_ / \_\_setstate\_\_ — Ray Serialization Compatibility

Ray serializes player objects when transferring them across CPU cores. `LangChainAPIInference` contains an HTTP client that is not picklable:

```python
def __getstate__(self):
    # Strip llm_client before serialization
    state = copy(self.__dict__)
    del state["llm_client"]
    return state

def __setstate__(self, state):
    # Reconstruct llm_client after deserialization
    self.__dict__.update(state)
    self.state.custom_state["llm_client"] = LangChainAPIInference(
        lm_name=custom["lm_name"],
        generation_config=custom["generation_config"],
    )
```

The LLM model name and generation config are preserved in `custom_state` so the client can be rebuilt exactly as it was.

### _apply_constraints() — Hard Portfolio Constraint Enforcement

The LLM may suggest quantities that exceed available cash or position limits. This function applies hard constraints as the final step after LLM output is parsed:

```python
if quantity > 0:    # buying
    max_affordable = cash / bid_price
    quantity = min(quantity, max_affordable)    # cannot spend more than held cash

elif quantity < 0:  # selling
    max_sellable = position + 50               # allow up to 50 shares of short selling
    quantity = max(-max_sellable, quantity)    # cannot exceed short selling limit
```

---

## §12 Configuration System (players.yml)

### Configuration Structure Design

Each agent type's `extras` block simultaneously holds two categories of parameters:

```yaml
rulellm_momentum:
  extras:
    # ── Portfolio parameters
    initial_cash: 10000.0
    initial_position: 0.0
    custom_state_hot_limit: 3

    # ── Rule parameters (aligned with AssetBubble for documentation traceability)
    lookback_short: 5
    aggressiveness: 2.0
    base_position_size: 20.0
    leverage_multiplier: 2.0

    # ── LLM configuration (points to variable in prompts.py)
    llm:
      sys_message: "examples.AssetBubble RuleLLM.prompts:RULELLM_MOMENTUM_SYS"
      user_message: "examples.AssetBubble RuleLLM.prompts:RULELLM_USER_TEMPLATE"
      lm_name: "ark/doubao-seed-1-6-lite-251015"
      generation_config:
        temperature: 0.3      # low temperature → more deterministic, stricter rule following
        max_new_tokens: 500
```

### Dynamic Prompt Loading Mechanism

```python
# sys_message: "examples.AssetBubble RuleLLM.prompts:RULELLM_MOMENTUM_SYS"
#              └── Python module path              └── variable name

def load_prompt(prompt_path: str) -> str:
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)
```

This design allows prompts to be swapped by changing only the YAML config, without modifying any Python code — fully config-driven.

### Agent Instance Counts

| Agent Type           | Instances | Rationale                              |
|----------------------|-----------|----------------------------------------|
| Market               | 1         | Single coordinator                     |
| Momentum Speculator  | 5         | Most aggressive; primary bubble driver |
| Rational Arbitrageur | 3         | Corrective counterforce                |
| Noise Trader         | 2         | Adds stochastic crowd behavior         |
| Value Investor       | 4         | Long-term stabilizing anchor           |
| Leveraged Buyer      | 3         | Amplifies upswings; triggers crash     |
| **Total**            | **18**    | Identical to all other variants        |

### Temperature Settings and Their Meaning

- **Momentum / Arbitrageur / Value / Leveraged**: `temperature=0.3` — low stochasticity, promotes strict adherence to the embedded quantitative rules
- **Noise Trader**: `temperature=0.5` — higher stochasticity, consistent with the noise trader's theoretically random sentiment signal

---

## §13 Running and Output

### Running the Simulation

```bash
# Activate environment
conda activate LMSim

# Set API key in .env file
# ARK_API_KEY = your_key_here

# Run simulation (100 rounds)
python examples/AssetBubble/RuleLLM/run_bubble_rulellm.py \
    -c configs/AssetBubble/RuleLLM/simulation.yml

# Run analysis
python examples/AssetBubble/RuleLLM/analysis.py \
    -c configs/AssetBubble/RuleLLM/simulation.yml
```

### Output File Structure

```
EXPERIMENT/AssetBubble/RuleLLM/
├── records/
│   ├── market/
│   │   ├── price/            # Price time series (one entry per round)
│   │   ├── fundamental/      # Fundamental value time series
│   │   ├── volume/           # Trading volume time series
│   │   └── bubble_metric/    # Price/Fundamental ratio time series
│   ├── rulellm_momentum_1/ .. rulellm_momentum_5/
│   │   └── price/            # Price history observed by each investor agent
│   └── ...
└── communication/
    └── ...                   # Message logs (inter-agent communication records)
```

### Analysis Output Metrics

`analysis.py` delegates to the shared pipeline in `AssetBubble/analysis.py`, producing:

- Price vs. fundamental value time series (showing bubble formation and collapse)
- Bubble Ratio (P/F) evolution over 100 rounds
- Net demand contribution breakdown by agent type
- Bubble detection: peak P/F ratio, bubble onset round, duration, crash timing

### Cross-Variant Result Comparison

After running all three variants with identical market parameters, the following metrics can be compared:

| Metric                   | AssetBubble | AssetBubble LLM | AssetBubble RuleLLM    |
|--------------------------|-------------|-----------------|------------------------|
| Peak bubble P/F ratio    | —           | —               | —                      |
| Bubble duration (rounds) | —           | —               | —                      |
| Price volatility         | —           | —               | —                      |
| Rule adherence           | 100%        | N/A             | Partial (±20% freedom) |

> **Research questions**: Given identical rule constraints embedded in the prompt, does LLM reasoning change the pattern of bubble formation compared to the pure rule-based baseline? Does the LLM's ±20% discretion systematically amplify or dampen bubble dynamics? And how does access to explicit financial theory (RuleLLM) versus no theory (pure LLM) affect the emergence and severity of the bubble?

---

## §14 References

> Do NOT re-state full citations — all core theories are documented in `../simulation-bases.md §2`.

- Greater Fool Theory → `simulation-bases.md §2`, `§4 — MomentumSpeculator`; DECISION RULES in `RuleLLM/prompts.py:RULELLM_MOMENTUM_SYS`
- Limits to Arbitrage → `simulation-bases.md §2`, `§4 — RationalArbitrageur`; DECISION RULES in `RuleLLM/prompts.py:RULELLM_ARBITRAGEUR_SYS`
- Noise Trader Risk → `simulation-bases.md §2`, `§4 — NoiseTrader`; DECISION RULES in `RuleLLM/prompts.py:RULELLM_NOISE_SYS`
- Value Investing → `simulation-bases.md §4 — FundamentalInvestor`; frequency gate documented in `§4 — Rule-Based Behavior`
- Leverage amplification → `simulation-bases.md §2`, `§4 — LeveragedBuyer`; margin call rule in `§3.2`
- Parameter values for all embedded DECISION RULES → `simulation-bases.md §6`
- Historical calibration targets → `simulation-bases.md §8`
