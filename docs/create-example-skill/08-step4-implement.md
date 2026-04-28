# Step 4: Implement Code

## Purpose

Implement all four simulation variants. Rule variant first (baseline), then LLM, RuleLLM, and Rag — in that order. Each variant builds on the previous.

**Reference implementations**: All four variants in `examples/AssetBubble/` are the primary reference. Study them before implementing.

---

## 4.1 Rule Variant Implementation

### 4.1.1 Directory Structure

```
examples/{SimulationName}/
├── __init__.py          (empty)
└── Rule/
    ├── __init__.py      (empty)
    ├── players.py
    ├── run_{name}.py
    └── analysis.py
```

### 4.1.2 `players.py` Structure (Rule Variant)

**Reference**: `examples/AssetBubble/Rule/players.py`

```python
"""
{SimulationName} — Rule-Based Simulation

Phenomenon: [1-2 sentence description]
    → simulation-bases.md §1

Theoretical Foundation:
    - [Theory 1 name] ([Author, Year])
      → simulation-bases.md §2.1
    - [Theory 2 name] ([Author, Year])
      → simulation-bases.md §2.2
    [...]

Key Dynamics:
    [Brief numbered list — full detail in simulation-bases.md §3]
    → simulation-bases.md §3

All parameters configured via players.yml.
    → simulation-bases.md §6
"""
```

**Market class docstring pattern**:
```python
class Market(GeneralPlayer):
    """
    Central market coordinator for {SimulationName}.

    Price formula (see simulation-bases.md §3.1 for full derivation and rationale):
        P(t+1) = P(t) + λ·D(t) + γ·[F−P(t)] + ε(t)

    Parameters (see simulation-bases.md §6 for source citations):
        price_impact (λ):   [brief description] — loaded from extras.price_impact
        mean_reversion (γ): [brief description] — loaded from extras.mean_reversion
        fundamental_value:  [brief description] — loaded from extras.fundamental_value
        noise_std (σ):      [brief description] — loaded from extras.noise_std
    """
```

**Investor class docstring pattern**:
```python
class {ClassName}(GeneralPlayer):
    """
    {1-2 sentence role description}.

    Theoretical basis: simulation-bases.md §4.{N} — {ClassName}
    Strategy specification: simulation-bases.md §4.{N}.4 — Behavioral Framework
    Parameters: simulation-bases.md §6
    See simulation-bases.md §4.{N} for full investor design specification.
    """
```

**Key implementation rules**:
1. `perceive()` initializes state on first call; extracts market data on all calls
2. `_initialize_investor_state()` loads ALL parameters from `self.state.config.extras`
3. `step()` calls `_make_decision()` and sends one order message
4. `_make_decision()` implements the logic from `simulation-bases.md §4.{N}.4.3 Mathematical Model`
5. No hardcoded numbers anywhere in the code — all come from config

### 4.1.3 `run_{name}.py` Pattern

```python
"""
{SimulationName} Rule Variant — Simulation Runner

Phenomenon: [brief]
Theory: [list]
Usage: python examples/{SimulationName}/Rule/run_{name}.py -c configs/{SimulationName}/Rule/simulation.yml
"""
import sys, os, argparse, logging

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

from masim.runner import SimulationRunner

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

def main():
    parser = argparse.ArgumentParser(description="{SimulationName} Rule simulation")
    parser.add_argument("-c", "--config", required=True, help="Path to simulation.yml")
    args = parser.parse_args()

    runner = SimulationRunner(config_path=args.config)
    runner.run()
    print(f"Simulation complete. Results in EXPERIMENT/{SimulationName}/Rule/")

if __name__ == "__main__":
    main()
```

### 4.1.4 `analysis.py` Structure (Rule Variant — Authoritative)

**Reference implementation**: `examples/AssetBubble/Rule/analysis.py`, `examples/AnchoringEffect/Rule/analysis.py`
**Record structure + API reference**: `docs/save-structure.md`

**Key rule**: Never parse EXPERIMENT files directly. Use `masim.utils.load_results()`.

#### Required top-level functions

| Function                                       | Purpose                                                                                                                                                 |
|------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| `_batch_to_rounds(values)`                     | Convert batch store list to `{round_num: value}` (1-based)                                                                                              |
| `_load_data(results)`                          | Load all coordinator batch stores + investor turn payloads from `SimulationResults`                                                                     |
| `_validate_{scenario}(...)`                    | Validate results against `analysis-bases.md §6` calibration targets; returns a result object with `.score`, `.is_valid`, `.criteria`, `.interpretation` |
| `analyze_{scenario}(data, config, output_dir)` | Orchestrates metrics → validation → plots → `summary.json`; prints structured report                                                                    |
| `main()`                                       | `load_config` → `load_results` → `_load_data` → `analyze_{scenario}`                                                                                    |

#### Output standard: structured validation report

Every `Rule/analysis.py` **must** produce a console report in this exact format:

```
==================================================
{SCENARIO NAME} ANALYSIS
==================================================
{Metric 1}: {value}  (target: {range from analysis-bases.md §6})
{Metric 2}: {value}  (target: {range})
...

VALIDATION: === {SCENARIO} SIMULATION VALIDATION: VALID|INVALID ===
Overall Fit Score: XX.X% (threshold: 50%)

[1] {CRITERION NAME}
    Observed: {observed value with units}
    Expected: {calibration range} ({citation from analysis-bases.md §2})
    Score: XX.X%
    Assessment: {LABEL} — {1-2 sentences of qualitative discussion}
    {Diagnostic advice if not optimal}

[2] {CRITERION NAME}
    ...

[SUMMARY]
{2-3 sentences on whether the phenomenon was reproduced.}
{Academic references that calibrate the expected behavior.}
Fit Score: XX.X%
```

Rules:
- **Criterion labels** must match metric names from `analysis-bases.md §2`
- **Expected ranges** must be the exact values from `analysis-bases.md §6` calibration table
- **Citations** in Assessment text must name the calibration source (e.g., `Campbell & Sharpe 2009`, `Kindleberger 2000`)
- **Threshold**: 50% overall Fit Score for VALID verdict (configurable per scenario)
- **Per-criterion scores** are weighted; weights must sum to 1.0 (document in code comment)

#### Validation logic pattern

```python
from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class {Scenario}ValidationResult:
    is_valid: bool
    score: float              # 0–1 overall Fit Score
    criteria: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    interpretation: str = ""

    def to_dict(self):
        return {"is_valid": self.is_valid, "score": round(self.score, 4),
                "criteria": self.criteria, "interpretation": self.interpretation}


def _validate_{scenario}(
    metric_a: float,   # from _compute_* functions
    metric_b: float,
    total_rounds: int,
) -> {Scenario}ValidationResult:
    """
    Validate against analysis-bases.md §6 calibration targets.

    Criteria (weights must sum to 1.0):
        1. {Criterion A}  target: {range}  weight: 0.40  source: {citation}
        2. {Criterion B}  target: {range}  weight: 0.40  source: {citation}
        3. {Criterion C}  target: {range}  weight: 0.20  source: {citation}
    """
    criteria = {}

    # --- Criterion 1: {Name} ---
    score_a = 0.0
    if {optimal_condition}:
        score_a = 1.0
    elif {marginal_condition}:
        score_a = 0.5 + ...  # linear interpolation toward 1.0
    else:
        score_a = ...        # penalized score
    criteria["{name}"] = {
        "value": round(metric_a, 3),
        "target": "{range}",
        "score": round(score_a, 3),
        "passed": {boolean_test},
    }

    # ... repeat for criteria 2, 3

    overall = score_a * 0.40 + score_b * 0.40 + score_c * 0.20
    is_valid = overall > 0.50 and {primary_condition}
    interpretation = _build_interpretation(...)
    return {Scenario}ValidationResult(is_valid=is_valid, score=overall,
                                      criteria=criteria, interpretation=interpretation)
```

#### Interpretation builder pattern

```python
def _build_interpretation(
    is_valid, overall_score,
    metric_a, metric_b, ...,
    score_a, score_b, ...,
) -> str:
    lines = []
    verdict = "VALID" if is_valid else "INVALID"
    lines.append(f"=== {SCENARIO} SIMULATION VALIDATION: {verdict} ===")
    lines.append(f"Overall Fit Score: {overall_score:.1%} (threshold: 50%)")
    lines.append("")

    # One block per criterion:
    lines.append("[1] {CRITERION NAME}")
    lines.append(f"    Observed: {metric_a:.2f} {units}")
    lines.append(f"    Expected: {range} ({citation})")
    lines.append(f"    Score: {score_a:.1%}")
    if {optimal}:   lines.append("    Assessment: OPTIMAL — ...")
    elif {marginal}: lines.append("    Assessment: MARGINAL — ...")
    else:           lines.append("    Assessment: INSUFFICIENT — ...")
    lines.append("")

    # [SUMMARY] block:
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append("The simulation successfully reproduces {phenomenon}: ...")
        lines.append("Results are consistent with {primary references}.")
    else:
        lines.append("The simulation does not fully reproduce {phenomenon}.")
        lines.append(f"Key issues: {', '.join(missing)}.")
    lines.append(f"Fit Score: {overall_score:.1%}")
    return "\n".join(lines)
```

#### Three mandatory plots

Every `Rule/analysis.py` must produce exactly three PNG files in `{base_dir}/analysis/`:

| Filename                     | Contents                                        | Primary metrics shown        |
|------------------------------|-------------------------------------------------|------------------------------|
| `01_{scenario}_dynamics.png` | Price vs. Fundamental time-series + Deviation % | Main phenomenon trajectory   |
| `02_{scenario}_analysis.png` | Phenomenon-specific deep-dive                   | Scenario-specific metric(s)  |
| `03_summary.png`             | Agent volume bar + Persistence/Residual chart   | Agent behavior + convergence |

All three correspond directly to dimensions in `analysis-bases.md §3`.

#### `main()` skeleton

```python
from masim.utils import load_config, load_results

def main():
    import argparse, os
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)
    results = load_results(config)
    data = _load_data(results)
    summary = analyze_{scenario}(data, config, output_dir)
    return summary
```

---

## 4.2 LLM Variant Implementation

### 4.2.1 Key Differences from Rule

- Market class: **identical copy** from Rule variant
- Investor classes: Replace `_make_decision()` with LLM call
- Add: `prompts.py` with system and user prompt constants
- `run_*.py`: Same pattern, different import path and config

### 4.2.2 `prompts.py` Structure

```python
"""
{SimulationName} LLM Variant — Prompt Definitions

System prompts define investor personalities ONLY.
They must NOT name the phenomenon, mention the price formula, or hint at the event type.

Reference: simulation-bases.md §4.{N}.4.4 for each investor's Behavioral Properties.
"""

# ─────────────────────────────────────────────
# {ClassName} — System Prompt
# Persona basis: simulation-bases.md §4.{N}.4.4 Behavioral Properties
# ─────────────────────────────────────────────

{CLASS_NAME}_SYSTEM = """You are a [role description] in financial markets.

CORE BELIEF: [One sentence guiding all decisions — derived from sim-bases §4.{N}.4.2]

YOUR PSYCHOLOGY:
[2-3 sentences on mindset, biases, tendencies — grounded in sim-bases §4.{N}.2 theories]

YOUR STRATEGY:
1. [Decision step 1]
2. [Decision step 2]
3. [Decision step 3]

HOW YOU INTERPRET MARKET DATA:
- Price above fundamental: [interpretation]
- Price below fundamental: [interpretation]
- Large positive deviation: [interpretation]
- Large negative deviation: [interpretation]

POSITION SIZING:
- Aggressive trades: [range] shares
- Moderate trades: [range] shares
- Conservative trades: [range] shares

CONSTRAINTS:
- Cannot spend more than available cash
- Cannot sell more shares than currently held
- [Any other hard constraints]

OUTPUT FORMAT:
First output your reasoning inside <analysis>...</analysis> tags,
then output your decision inside <decision>...</decision> tags.
The decision must be valid JSON:
{"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
IMPORTANT: bid_price and quantity MUST be numeric values (e.g., 10.5), NOT expressions or formulas.
"""

{CLASS_NAME}_USER = """Current Market State:
- Price: ${price:.2f}
- Fundamental Value: ${fundamental:.2f}
- Deviation from Fundamental: {deviation:.2%}
- Round: {round}

Your Portfolio:
- Cash: ${cash:.2f}
- Shares Held: {position}
- Portfolio Value: ${portfolio_value:.2f}

What is your trading decision for this round?"""
```

**Critical constraints for LLM prompts**:
- System prompt must NOT name the phenomenon (no "carry trade", "flash crash", "anchoring bias")
- System prompt must NOT mention the price formula or its parameters
- The output format block is mandatory — copy it exactly as shown above
- Always `<analysis>` not `<think>`

### 4.2.3 `analysis.py` Structure (LLM Variant)

```python
"""
{SimulationName} LLM Variant — Analysis Script

Extends Rule/analysis.py with LLM-specific analysis.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

from examples.{SimulationName}.Rule.analysis import (
    _batch_to_rounds,
    _load_data,
    calculate_metrics,
    create_visualizations,
)

def analyze_action_distribution(agent_records):
    """Analyze distribution of buy/sell/hold decisions by agent type."""
    ...

def main():
    # Reuses _load_data, calculate_metrics, create_visualizations from Rule
    # Adds action_distribution analysis
    ...
```

---

## 4.3 RuleLLM Variant Implementation

### 4.3.1 Key Differences from LLM

- Only difference is `prompts.py`: every system prompt has TWO mandatory sections: `== PERSONA ==` and `== DECISION RULES ==`
- Players.py is identical to LLM variant structure
- `analysis.py` adds `analyze_rule_adherence()`

### 4.3.2 RuleLLM Prompt Structure

```python
{CLASS_NAME}_SYSTEM = """
== PERSONA ==

You are a [role description] in financial markets.

CORE BELIEF: [Identical to LLM variant persona]

YOUR PSYCHOLOGY:
[Identical to LLM variant psychology description]

== DECISION RULES ==

You follow these quantitative rules based on market conditions:

RULE 1 — [Trigger Name]:
  When: [Condition in plain text — e.g., "deviation = (price − fundamental) / fundamental < −0.15"]
  Action: [Exact action — e.g., "SELL 50% of your current shares"]
  Quantity formula: [E.g., "quantity = position × 0.50"]

RULE 2 — [Next Trigger]:
  When: [Condition]
  Action: [Action]

DEFAULT: Hold — take no action when no rule triggers.

RULE COMPLIANCE: You MUST follow the sign (buy/sell/hold) of the triggered rule.
You may adjust the quantity by up to ±20% based on context, but the direction is non-negotiable.
Explain your adherence or adjustment in the <analysis> section.

OUTPUT FORMAT:
First output your reasoning inside <analysis>...</analysis> tags,
then output your decision inside <decision>...</decision> tags.
The decision must be valid JSON:
{"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
IMPORTANT: bid_price and quantity MUST be numeric values (e.g., 10.5), NOT expressions or formulas.
"""
```

**Critical**: The `== DECISION RULES ==` section must reproduce the EXACT formulas from `Rule/players.py → _make_decision()`. If Rule parameters change, update this section immediately.

### 4.3.3 `analyze_rule_adherence()` in `analysis.py`

```python
def analyze_rule_adherence(agent_records):
    """
    Measure how often LLM decisions match Rule-variant decisions.

    Args:
        agent_records: Dict[agent_id, List[Dict]] — each record has 'rule_action' and 'action'

    Returns:
        Dict[agent_id, Dict]:
            adherence_rate: float (target ≥ 0.80)
            matching_rounds: int
            total_rounds: int
            meets_target: bool
    """
```

---

## 4.4 Rag Variant Implementation

### 4.4.1 Key Differences from RuleLLM

- `players.py`: Each investor class adds `_initialize_rag()` and uses retrieval in `step()`
- `prompts.py`: User prompt template adds `{rag_context}` placeholder
- `analysis.py`: Adds `analyze_rag_knowledge_effect()`
- `players.yml`: Each agent has `rag:` configuration block

### 4.4.2 Rag Player Additional Methods

```python
def _initialize_rag(self) -> None:
    """Initialize KnowledgeStore from config. Build index on first run, load from disk on subsequent."""
    from masim.rag import KnowledgeStore
    rag_config = self.state.config.extras.get("rag", {})
    self._knowledge_store = KnowledgeStore(
        docs_dir=rag_config.get("docs_dir"),
        persist_dir=rag_config.get("rag_persist_dir"),
        embed_model=rag_config.get("embed_model", "text-embedding-3-small"),
        top_k=rag_config.get("top_k", 3),
    )

def _formulate_knowledge_query(self, market_data: dict) -> str:
    """Build retrieval query from current market state."""
    deviation = market_data.get("deviation", 0)
    # Query strategy: use current market state language to retrieve relevant historical context
    if deviation < -0.10:
        return f"forced liquidation crisis deviation {deviation:.2f} market crash"
    elif deviation > 0.10:
        return f"overvalued market bubble deviation {deviation:.2f}"
    else:
        return f"normal market conditions deviation {deviation:.2f}"

def _get_rag_context(self, market_data: dict) -> str:
    """Retrieve relevant documents and format as context string."""
    query = self._formulate_knowledge_query(market_data)
    docs = self._knowledge_store.query(query)
    if not docs:
        return "(No relevant knowledge retrieved this round.)"
    return "\n\n".join(f"[Context {i+1}]: {doc}" for i, doc in enumerate(docs))
```

### 4.4.3 `_RAG_FALLBACK` Constant

Every Rag `analysis.py` must define:

```python
_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"
```

This exact string is checked by `analyze_rag_knowledge_effect()` to distinguish successful from failed retrievals.

### 4.4.4 User Prompt Template for Rag

```python
{CLASS_NAME}_USER = """Current Market State:
- Price: ${price:.2f}
- Fundamental Value: ${fundamental:.2f}
- Deviation from Fundamental: {deviation:.2%}
- Round: {round}

Your Portfolio:
- Cash: ${cash:.2f}
- Shares Held: {position}
- Portfolio Value: ${portfolio_value:.2f}

Relevant Historical Knowledge:
{rag_context}

What is your trading decision for this round?"""
```

The `{rag_context}` placeholder is filled at runtime with either retrieved documents or the fallback string.

---

## 4.5 Implementation Quality Checklist

After implementing each variant:

- [ ] All agent classes have docstrings citing `simulation-bases.md §4.{N}`
- [ ] All numeric values in `_make_decision()` are loaded from config, not hardcoded
- [ ] `perceive()` initializes state correctly on first call
- [ ] `step()` always sends exactly one order message
- [ ] LLM prompts do NOT name the phenomenon or mention the price formula
- [ ] LLM prompts end with canonical `OUTPUT FORMAT` block using `<analysis>` tags
- [ ] RuleLLM prompts have both `== PERSONA ==` and `== DECISION RULES ==` sections
- [ ] `Rule/analysis.py` uses `load_results()` + `_load_data()` — no raw `os.listdir()` + `json.load()` on record files
- [ ] `Rule/analysis.py` exports `_load_data` and metric/validation functions for import by other variants
- [ ] LLM/RuleLLM/Rag `analysis.py` imports `_load_data` from `Rule/analysis.py`
- [ ] Rag `analysis.py` defines `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"`
- [ ] All `__init__.py` files present

#### `analysis.py` output standard checklist

- [ ] Console output header: `=== {SCENARIO} SIMULATION VALIDATION: VALID|INVALID ===`
- [ ] Overall Fit Score printed with `(threshold: 50%)` label
- [ ] Each criterion block has: `[N]` label, `Observed:`, `Expected:` with calibration range, `Score:`, `Assessment:` with qualitative discussion
- [ ] Assessment text cites the calibration source from `analysis-bases.md §6` (author + year)
- [ ] Criterion weights documented in `_validate_*` docstring and sum to 1.0
- [ ] `[SUMMARY]` block present at end of interpretation
- [ ] Produces exactly 3 PNG files: `01_*.png`, `02_*.png`, `03_*.png` in `{base_dir}/analysis/`
- [ ] Saves `summary.json` containing `metrics`, `validation` (with `.score`, `.is_valid`, `.criteria`, `.interpretation`)
- [ ] `py_compile` passes on all four variant `analysis.py` files
