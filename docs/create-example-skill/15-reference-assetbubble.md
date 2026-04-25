# Reference: AssetBubble Implementation

## Purpose

AssetBubble is the primary reference implementation demonstrating all patterns, standards, and conventions used across this project. When in doubt about how to implement any part of a simulation, consult this reference first.

---

## Key Reference Files

| Component              | Reference File                                      | What It Demonstrates                                                                                                                                                            |
|------------------------|-----------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Root design document   | `examples/AssetBubble/simulation-bases.md`          | Full 9-section structure; expanded theoretical foundation; investor taxonomy with Rule-Based Behavior/LLM Persona (note: these will be migrated to explain.md per new standard) |
| Root analysis document | `examples/AssetBubble/analysis-bases.md`            | Full 7-section structure; 6+ metrics with formulas; calibration targets                                                                                                         |
| Market agent           | `examples/AssetBubble/Rule/players.py` lines 41–150 | Market class structure; `_clear_market()`; price formula implementation; state initialization pattern                                                                           |
| Rule investor agents   | `examples/AssetBubble/Rule/players.py` lines 150+   | Investor class docstring pattern; `_make_decision()`; config loading; `perceive()`/`step()` pattern                                                                             |
| Rule runner            | `examples/AssetBubble/Rule/run_bubble.py`           | `SimulationRunner` usage; argparse setup; logging                                                                                                                               |
| Rule analysis          | `examples/AssetBubble/Rule/analysis.py`             | `__all__` export; `load_simulation_data()`; `calculate_metrics()`; `create_visualizations()`                                                                                    |
| Rule explain.md        | `examples/AssetBubble/Rule/explain.md`              | 9-section structure; Theory→Implementation mapping table; architecture diagram                                                                                                  |
| Rule analysis.md       | `examples/AssetBubble/Rule/analysis.md`             | 7-section structure; metric mapping; variant comparison notes                                                                                                                   |
| LLM players            | `examples/AssetBubble/LLM/players.py`               | LLM investor class structure; prompt loading; response parsing; `_validate_decision()`                                                                                          |
| LLM prompts            | `examples/AssetBubble/LLM/prompts.py`               | Personality-only system prompt; canonical output format; user prompt template                                                                                                   |
| RuleLLM prompts        | `examples/AssetBubble/RuleLLM/prompts.py`           | `== PERSONA ==` + `== DECISION RULES ==` dual-section; rule text embedding                                                                                                      |
| Rag players            | `examples/AssetBubble/Rag/players.py`               | `_initialize_rag()`; `_formulate_knowledge_query()`; `_get_rag_context()`; KnowledgeStore integration                                                                           |
| Config — simulation    | `configs/AssetBubble/Rule/simulation.yml`           | Standard simulation.yml structure with all required fields                                                                                                                      |
| Config — players       | `configs/AssetBubble/Rule/players.yml`              | Agent definition with source citation comments; market parameters                                                                                                               |
| Config — topology      | `configs/AssetBubble/Rule/topology.yml`             | Star topology configuration                                                                                                                                                     |
| Config — persona       | `configs/AssetBubble/Rule/persona.yml`              | Persistence configuration per agent                                                                                                                                             |

---

## AssetBubble Key Patterns

### Pattern 1: Price Formula Implementation

```python
# In Market._clear_market():
net_demand = sum(buy_orders) - sum(sell_orders)
price_change = self._price_impact * net_demand           # λ·D(t)
mean_rev = self._mean_reversion * (self._fundamental - self._price)  # γ·[F−P(t)]
noise = random.gauss(0, self._noise_std)                # ε(t)
new_price = max(self._price + price_change + mean_rev + noise, 0.01)
```

### Pattern 2: Investor State Initialization

```python
def perceive(self, observation):
    if not self.state.custom_state.get("_initialized"):
        self._initialize_investor_state()
    # ... extract market data from observation

def _initialize_investor_state(self):
    extras = self.state.config.extras
    self.state.custom_state["_initialized"] = True
    self.state.custom_state["cash"] = extras.get("initial_cash", 100000.0)
    self.state.custom_state["position"] = extras.get("initial_position", 1000)
    self.state.custom_state["threshold"] = extras.get("threshold", 0.15)
    # Load ALL parameters from config here — no hardcoded values
```

### Pattern 3: LLM Decision Parsing

```python
# In LLM investor step():
response = self._llm_client.chat(messages=[
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
])
# Parse <decision>{...}</decision> from response
import re, json
match = re.search(r"<decision>(.*?)</decision>", response, re.DOTALL)
if match:
    decision = json.loads(match.group(1))
    action = decision.get("action", "hold")
    quantity = float(decision.get("quantity", 0))
    bid_price = float(decision.get("bid_price", market_price))
```

### Pattern 4: Module Docstring Citation

```python
"""
{SimulationName} — Rule-Based Simulation

Phenomenon: [1-2 sentences]
    → simulation-bases.md §1

Theoretical Foundation:
    - Theory Name (Author, Year)
      → simulation-bases.md §2.N
    ...
    → simulation-bases.md §3 for market design
    → simulation-bases.md §6 for parameters
"""
```

### Pattern 5: Player Class Docstring Citation

```python
class {ClassName}(GeneralPlayer):
    """
    [Role description — 1 sentence].

    Theoretical basis: simulation-bases.md §4.{N} — {ClassName}
    Strategy specification: simulation-bases.md §4.{N}.4 — Behavioral Framework
    Parameters: simulation-bases.md §6
    See simulation-bases.md §4.{N} for full investor design specification.
    """
```

### Pattern 6: RuleLLM Prompt Structure

```python
AGENT_SYSTEM = """
== PERSONA ==

You are [role description].

CORE BELIEF: [One sentence]

YOUR PSYCHOLOGY:
[2-3 sentences on mindset and biases]

== DECISION RULES ==

You follow these rules:

RULE 1 — [Trigger Name]:
  When: [Condition in plain English using market data field names]
  Action: [Exact buy/sell/hold instruction]
  Quantity: [Formula in words]

DEFAULT: Hold when no rule triggers.

RULE COMPLIANCE: Follow the sign strictly; adjust quantity by up to ±20%.

OUTPUT FORMAT:
[canonical output format block]
"""
```

### Pattern 7: Analysis DRY Imports

```python
# In LLM/analysis.py (and RuleLLM, Rag):
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from examples.AssetBubble.Rule.analysis import (
    load_simulation_data,
    calculate_metrics,
    create_visualizations,
)
# Then define only variant-specific additions
```

---

## AssetBubble Simulation Parameters (Reference Values)

| Parameter             | Value | Typical Range | Source                                  |
|-----------------------|-------|---------------|-----------------------------------------|
| price_impact (λ)      | 0.15  | 0.05–0.25     | Calibrated for bubble dynamics          |
| mean_reversion (γ)    | 0.005 | 0.005–0.05    | Deliberately low for extended deviation |
| noise_std (σ)         | 0.3   | 0.01–0.5      | Background trading noise                |
| fundamental_growth    | 0.001 | 0.0–0.005     | Slow growing fundamental                |
| short_cost_rate       | 0.001 | 0.0–0.01      | Borrowing cost per round                |
| margin_call_threshold | 0.70  | 0.6–0.8       | Equity floor for forced selling         |

---

## AssetBubble Investor Types (Reference)

| Class               | Theory                                            | Market Role            | Primary Signal             |
|---------------------|---------------------------------------------------|------------------------|----------------------------|
| MomentumSpeculator  | Greater Fool Theory (Keynes, 1936)                | Strongly Destabilizing | price_history (MA5)        |
| RationalArbitrageur | Limits to Arbitrage (Shleifer & Vishny, 1997)     | Weakly Stabilizing     | deviation, short_cost_rate |
| NoiseTrader         | Noise Trader Risk (De Long et al., 1990)          | Amplifying             | return (sentiment proxy)   |
| FundamentalInvestor | Value Investing (Graham & Dodd, 1934)             | Weakly Stabilizing     | deviation (every 5 rounds) |
| LeveragedBuyer      | Synchronization Risk (Abreu & Brunnermeier, 2003) | Strongly Destabilizing | return, equity_ratio       |

---

## How to Use This Reference

1. When implementing a new **Market class**: copy `AssetBubble/Rule/players.py Market` class and adapt `_clear_market()` for the new simulation's price dynamics.

2. When implementing a new **investor class**: copy the pattern from the closest AssetBubble investor type (e.g., MomentumSpeculator for trend-following, RationalArbitrageur for value-based, NoiseTrader for random activity).

3. When writing **explain.md**: use `AssetBubble/Rule/explain.md` as the structural template. Every section has an equivalent in the AssetBubble reference.

4. When writing **prompts.py**: copy the output format block verbatim from `AssetBubble/LLM/prompts.py` — it must not be modified.

5. When writing **analysis.py**: copy the `__all__` export pattern from `AssetBubble/Rule/analysis.py` exactly.
