# Step 4: Implement Code

## Purpose

Implement every simulation variant marked `Yes` in target §10.1, in the sequence declared there (each successive variant builds on the previous, so a purely-computational baseline should typically be listed first).

<!-- Finance-appendix (§4.1.F) instantiation:
     The finance-default variant sequence is Rule → LLM → RuleLLM → Rag —
     Rule as the deterministic baseline, LLM adds language-model deliberation,
     RuleLLM overlays quantitative decision rules on the LLM persona,
     and Rag finally enriches the LLM with retrieved historical context. -->

**Reference implementations**: The primary reference is `examples/AssetBubble/` (study any built variants you need). This is a finance-appendix (§4.1.F) reference — non-finance scenarios should treat its `Market` class, price formula, and `bid_price`/`quantity` fields as domain-instantiation examples, and map them to their own coordinator, state-update law, and action fields via the finance-appendix pattern.

---

## Implementer Contract Reminder (READ FIRST, RE-READ EVERY PASS)

Before writing or modifying any code in this step, **open the agent's design specification and re-read its §3.6.0 I/O Contract** (defined by `masim/skills/agent-design-skill.md` v2.3.1). The I/O Contract is the single source of truth for:

1. **Inputs** the agent consumes per call — every row in the Inputs table MUST have a real read against the environment / state / round header. If the engine cannot supply an input listed there, the implementation is incomplete.
2. **Outputs** the agent emits — every `Required? = yes` field MUST be populated on every call. Extra fields MUST NOT be emitted. Numeric fields MUST be clamped to their declared valid range before emission.
3. **Content constraints** — required fields, forbidden fields, value ranges, unit conventions, sign conventions, determinism markers.
4. **Serialization format** — the canonical tag pattern `<analysis>...</analysis><decision>{JSON}</decision>` (see this file's `OUTPUT FORMAT` blocks below) is mandated by the contract, NOT invented here. The JSON keys MUST match the contract's Outputs table verbatim.
5. **Variant parity** — each of the four canonical variants `Rule`, `LLM`, `RuleLLM`, `Rag` that is declared `Yes` in target §10.1 MUST emit the same output field set. Every variant is implemented independently and MUST pass a smoke run before Step 5. If a target scenario needs a fifth variant, the `implement-simulation-skill` docs MUST be upgraded first (see `01-mandatory-structure.md § Canonical Variant Set — Introducing a new variant`); no variant may be added silently. If any canonical variant needs a new output field, extend the design's §3.6.0 FIRST, then propagate to every one of `Rule`, `LLM`, `RuleLLM`, `Rag`.

**Conflict resolution rule:** on any conflict between the agent's §3.6.0 I/O Contract and prose elsewhere (§3.6.2 mechanism, §3.6.3 action space, or target §4.1.X appendix), the §3.6.0 contract wins. Reconcile the other section in the same editing pass.

**Canonical variant set:** the four variants named across this file — `Rule`, `LLM`, `RuleLLM`, `Rag` — are the *only* variants supported by the current version of `implement-simulation-skill`. Each MUST be implemented completely and independently for every scenario that declares it `Yes` in target §10.1. If a scenario needs a variant outside this set, follow the upgrade procedure in `01-mandatory-structure.md § Canonical Variant Set — Introducing a new variant` BEFORE writing code (add named coverage in every implement-* doc, then implement).

Every checklist item in this step (parser tests, prompt drafting, decision-emission wiring) is a mechanical projection of the contract. If the contract is missing or ambiguous, STOP and file a design revision before writing code.

---

## Contract (Inputs / Outputs / Polish Hooks)

This block is the **stable I/O declaration** for Step 4. Both
`masim/skills/create-simulation-pipeline.md` and
`masim/skills/polish-simulation-pipeline.md` anchor to it.

**Inputs (consumed).**

| Source                                                                        | Used for                                                              |
|-------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| Target §10.1 (variants marked `Yes`)                                          | which `{V}/` folders to implement, and in what order                  |
| `simulation-bases.md §3` Environment Design (finance appendix: Market Design) | Coordinator class implementation                                      |
| `simulation-bases.md §4.{N}` Agent blocks (finance appendix: Investor blocks) | one Player class per agent, one prompt per agent (LLM-based variants) |
| `configs/{ScenarioName}/{V}/*.yml`                                            | runtime `extras` values (fail-fast access — no defaults)              |
| `masim/skills/implement-simulation-skill/03-variant-documents-spec.md`        | `explain.md` and `analysis.md` layout                                 |

**Outputs (produced).**

| Artefact per built `V`                                             | Extent of write                                                                                                                                                                             |
|--------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `examples/{ScenarioName}/{V}/players.py`                           | Coordinator class + one Player class per §4.{N} block (finance appendix: `Market` + investor players); **fail-fast** — no `extras.get(key, default)`, no `decision.get("action", fallback)` |
| `examples/{ScenarioName}/{V}/analysis.py`                          | metric functions per `analysis-bases.md §2` (LLM-based: also decision-field extractors per §4.2.3)                                                                                          |
| `examples/{ScenarioName}/{V}/run_{name}.py`                        | orchestration entry point                                                                                                                                                                   |
| `examples/{ScenarioName}/{V}/prompts.py` (LLM-based variants only) | system prompt + user prompt template + parser                                                                                                                                               |
| `examples/{ScenarioName}/{V}/explain.md`                           | 9-section implementation guide per `03-variant-documents-spec.md` — traces every §4.{N} back to the class/method that implements it                                                         |
| `examples/{ScenarioName}/{V}/analysis.md`                          | 7-section analysis guide per `03-variant-documents-spec.md` — traces every `analysis-bases.md §2` metric to a function                                                                      |

**Polish Hooks (what a polish audit re-verifies against this step).**
When `polish-simulation-pipeline.md` audits Step 4, it MUST re-run
these six checks — no new features are added:

1. **No-defaults rule.** No `extras.get(key, default)`, no `decision.get("action", "hold")`, no `if X else fallback` for required data. Legitimate exceptions listed in `00-overview.md §Key Design Principles` are permitted.
2. **`py_compile` clean** on every `players.py`, `analysis.py`, `run_*.py`, `prompts.py` in every built variant.
3. **LLM decision-field access rule** (§4.2.3) followed in each of `LLM`, `RuleLLM`, and `Rag` `players.py` (all three model-consulting variants in the canonical set; `Rule` is exempt).
4. **`explain.md` §2 completeness** — every §4.{N} block in `simulation-bases.md` has a matching Theory → Implementation Mapping row.
5. **`analysis.md` §2 completeness** — every metric declared in `analysis-bases.md §2` has an implementation trace.
6. **`Rag`-only checks** (when `Rag` is declared `Yes` in target §10.1) — `_RAG_FALLBACK` constant present in `Rag/analysis.py` and matches the shape declared in the agent design's §3.6.0 I/O Contract and in `analysis-bases.md §4.4.3` (or the equivalent retrieval-metric section).

---

## 4.1 Rule Variant Implementation

> **Domain-neutrality note.** §§4.1–4.4 walk through the four finance-default variants — Rule (deterministic baseline), LLM (persona-driven deliberation), RuleLLM (persona + explicit decision rules), Rag (persona + retrieved historical context). Non-finance scenarios that declare a different variant scheme in target §10.1 (e.g., only `Rule` and `LLM`, or a domain-specific `Compartment` / `Threshold` variant) map their variants onto whichever of these four templates is closest and skip the rest.

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

**Coordinator class docstring pattern**:
```python
class {CoordinatorClass}(GeneralPlayer):
    """
    Central environment coordinator for {SimulationName}.

    State-update law (see simulation-bases.md §3.1 for full derivation and rationale):
        S(t+1) = f( S(t), aggregate_action(t), noise(t) )

    Parameters (see simulation-bases.md §6 for source citations):
        {coeff_1}: [brief description] — loaded from extras.{coeff_1}
        {coeff_2}: [brief description] — loaded from extras.{coeff_2}
        ...
    """
```

<details>
<summary>Finance-appendix (§4.1.F) instantiation — <code>Market</code> class docstring pattern</summary>

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

</details>

<!-- Non-finance domain instantiations of the coordinator docstring:
     - Opinion:    consensus/dispersion coordinator; law is bounded-confidence update
                   x_i(t+1) = x_i(t) + μ·Σ w_ij·[x_j(t)−x_i(t)]; params μ (trust rate),
                   ε (confidence bound), σ (noise).
     - Epidemics:  compartment coordinator; SIR/SEIR update on {S,E,I,R} fractions;
                   params β (infection rate), γ (recovery rate), σ (E→I rate).
     - Sociology:  diffusion coordinator; threshold update over adoption fraction;
                   params θ (adoption threshold), α (imitation weight). -->

**Agent class docstring pattern**:
```python
class {ClassName}(GeneralPlayer):
    """
    {1-2 sentence role description}.

    Theoretical basis: simulation-bases.md §4.{N} — {ClassName}
    Strategy specification: simulation-bases.md §4.{N}.5 — Behavioral Framework
    Parameters: simulation-bases.md §6
    See simulation-bases.md §4.{N} for full agent design specification (finance appendix: full investor design specification).
    """
```

**Key implementation rules**:
1. `perceive()` initializes state on first call; extracts environment state broadcast on all calls (finance appendix: extracts market data)
2. `_initialize_agent_state()` (finance appendix: `_initialize_investor_state()`) loads ALL parameters from `self.state.config.extras`
3. `step()` calls `_make_decision()` and sends one action message (finance appendix: one order message)
4. `_make_decision()` implements the logic from `simulation-bases.md §4.{N}.5.4 Mathematical Model`
5. No hardcoded numbers anywhere in the code — all come from config
6. No `.get(key, default)`, no `if X else fallback`, no silent error recovery — all missing project data must `raise` immediately; stochastic API fallback is allowed only under `00-overview.md` Principle #6

### 4.1.3 `run_{name}.py` Pattern

```python
#!/usr/bin/env python
"""{SimulationName} Rule-Based Simulation Runner.

Usage::

    python examples/{SimulationName}/Rule/run_{name}.py \
        -c configs/{SimulationName}/Rule/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="{SimulationName}",
        variant="Rule-Based",
        default_config="configs/{SimulationName}/Rule/simulation.yml",
        phenomenon="{One-line phenomenon description}",
        load_env=False,
    )
```

### 4.1.4 `analysis.py` Structure (Rule Variant — Authoritative)

**Reference implementation**: `examples/AssetBubble/Rule/analysis.py`, `examples/AnchoringEffect/Rule/analysis.py`
**Record structure + API reference**: `docs/save-structure.md`

**Key rule**: Never parse EXPERIMENT files directly. Use `masim.utils.load_results()`.

#### Evaluation-First Import Rule (MANDATORY)

> **Full specification**: See `masim/skills/implement-simulation-skill/10-evaluation-architecture.md`.

All reusable metric, visualization, validation, and data-loading functions live in `masim/evaluation/`. Scenario analysis scripts import from there. The decision flowchart is:

1. **Need a function?** → Check `masim/evaluation/` first (timeseries, behavioral, volatility, microstructure, visualization, validation, registry, data_loader, pipeline).
2. **Found it?** → Import it. Done.
3. **Not found but reusable?** → Implement it in the correct `masim/evaluation/` submodule FIRST, then import it.
4. **Truly scenario-specific?** → Implement locally with a comment explaining why it cannot be generalized.

**Correct imports**:
```python
from masim.evaluation.finance.timeseries import calculate_returns, calculate_max_drawdown
from masim.evaluation.finance.behavioral import calculate_bid_convergence_cv
from masim.evaluation.finance.volatility import calculate_garch_signature
from masim.evaluation.finance.visualization import plot_price_dynamics, save_figure
from masim.evaluation.finance.validation import validate_asset_bubble
from masim.evaluation.registry import Metric, MetricsRegistry, MetricUnavailable
from masim.evaluation.data_loader import load_data, batch_to_rounds, market_players, series
```

The within-scenario DRY hierarchy (`LLM/analysis.py` imports scenario-specific orchestration from `Rule/analysis.py`) remains valid for scenario-specific functions like `analyze_{scenario}()` and `_validate_{scenario}()`. Generic metric/viz/validation utilities always come from `masim/evaluation/`.

#### Required top-level functions

| Function                                                              | Purpose                                                                                                                                                 |
|-----------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| `_load_data(results)` (from `masim.evaluation.data_loader.load_data`) | Load all coordinator batch stores + agent turn payloads from `SimulationResults`                                                                        |
| `_validate_{scenario}(...)`                                           | Validate results against `analysis-bases.md §6` calibration targets; returns a result object with `.score`, `.is_valid`, `.criteria`, `.interpretation` |
| `analyze_{scenario}(data, config, output_dir)`                        | Orchestrates metrics → validation → plots → `summary.json`; prints structured report                                                                    |
| `main()`                                                              | `load_config` → `load_results` → `_load_data` → `analyze_{scenario}`                                                                                    |

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

#### Mandatory plots

Every `Rule/analysis.py` must produce the following PNG files in `{base_dir}/analysis/`:

| Filename                     | Contents                                                                                                   | Primary metrics shown                                                                                   |
|------------------------------|------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| `00_agent_actions.png`       | Environment state trajectory + each agent's action-price/level curves                                      | Headline overview — agent behaviour vs environment state (finance appendix: agent bids vs market price) |
| `01_{scenario}_dynamics.png` | Environment state vs. Anchor/Reference time-series + Deviation % (finance appendix: Price vs. Fundamental) | Main phenomenon trajectory                                                                              |
| `02_{scenario}_analysis.png` | Phenomenon-specific deep-dive                                                                              | Scenario-specific metric(s)                                                                             |
| `03_summary.png`             | Agent volume/participation bar + Persistence/Residual chart                                                | Agent behavior + convergence                                                                            |

**Plot 0 specification** (`00_agent_actions.png`):
- Layout: single-panel, `figsize=(16, 8)` — the "headline" chart.
- **Environment state**: thick coordinator line (finance appendix: gold `#f0a500`, linewidth 2.5, zorder=10 — market price).
- **Anchor / Reference**: dashed horizontal reference line (finance appendix: green fundamental value).
- **Agent action curves**: one coloured line per `player_id` from an `agent_actions = {pid: {round_num: action_scalar}}` dict, with small markers.
- X-axis = Round, Y-axis = domain-appropriate action/state scalar (finance appendix: Price).
- Legend at bottom-center, multi-column.
- Data source: `player.turns.field("{action_scalar_field}")` for each non-coordinator player (finance appendix: `player.turns.field("bid_price")`).

Plots 01–03 correspond directly to dimensions in `analysis-bases.md §3`.

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

- Coordinator class (finance appendix: `Market`): **identical copy** from Rule variant
- Agent classes (finance appendix: Investor classes): Replace `_make_decision()` with LLM call
- Add: `prompts.py` with system and user prompt constants
- `run_*.py`: Same pattern, different import path and config

### 4.2.2 `prompts.py` Structure

The domain-neutral shell is:

```python
"""
{SimulationName} LLM Variant — Prompt Definitions

System prompts define agent personalities ONLY.
They must NOT name the phenomenon, mention the state-update law, or hint at the event type.

Reference: simulation-bases.md §4.{N}.5.5 for each agent's Behavioral Properties.
"""

# ─────────────────────────────────────────────
# {ClassName} — System Prompt
# Persona basis: simulation-bases.md §4.{N}.5.5 Behavioral Properties
# ─────────────────────────────────────────────

{CLASS_NAME}_SYSTEM = """You are a [role description] operating in the target domain.

CORE BELIEF: [One sentence guiding all decisions — derived from sim-bases §4.{N}.5.2]

YOUR PSYCHOLOGY:
[2-3 sentences on mindset, biases, tendencies — grounded in sim-bases §4.{N}.3 theories]

YOUR STRATEGY:
1. [Decision step 1]
2. [Decision step 2]
3. [Decision step 3]

HOW YOU INTERPRET THE ENVIRONMENT STATE BROADCAST:
- {state_signal_high}: [interpretation]
- {state_signal_low}:  [interpretation]
- {deviation_high}:    [interpretation]
- {deviation_low}:     [interpretation]

ACTION SIZING:
- Aggressive: [range of the action-magnitude field]
- Moderate:   [range]
- Conservative: [range]

CONSTRAINTS:
- [Domain-specific hard constraints — e.g., resource caps, exposure limits, once-per-round]

OUTPUT FORMAT:
First output your reasoning inside <analysis>...</analysis> tags,
then output your decision inside <decision>...</decision> tags.
The decision must be valid JSON with exactly the fields declared in target §4.1.{X} appendix.
IMPORTANT: numeric fields MUST be numeric values (e.g., 10.5), NOT expressions or formulas.
"""

{CLASS_NAME}_USER = """Current Environment State:
{state_broadcast_lines}   # e.g., "- {field_1}: {value_fmt_1}", one per broadcast field
- Round: {round}

Your Local State:
{agent_local_state_lines} # e.g., resources, position, exposure — from §4.{N}.5

What is your decision for this round?"""
```

<details>
<summary>Finance-appendix (§4.1.F) instantiation — full <code>prompts.py</code> template</summary>

```python
"""
{SimulationName} LLM Variant — Prompt Definitions

System prompts define investor personalities ONLY.
They must NOT name the phenomenon, mention the price formula, or hint at the event type.

Reference: simulation-bases.md §4.{N}.5.5 for each investor's Behavioral Properties.
"""

# ─────────────────────────────────────────────
# {ClassName} — System Prompt
# Persona basis: simulation-bases.md §4.{N}.5.5 Behavioral Properties
# ─────────────────────────────────────────────

{CLASS_NAME}_SYSTEM = """You are a [role description] in financial markets.

CORE BELIEF: [One sentence guiding all decisions — derived from sim-bases §4.{N}.5.2]

YOUR PSYCHOLOGY:
[2-3 sentences on mindset, biases, tendencies — grounded in sim-bases §4.{N}.3 theories]

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

</details>

<!-- Non-finance domain instantiations of the LLM prompt output-format JSON:
     - Opinion:    {"speech_act": "assert"|"defer"|"silent", "opinion": float in [-1,1], "confidence": float, "reasoning": string}
     - Epidemics:  {"contact_action": "meet"|"avoid", "contact_count": int, "test": bool, "reasoning": string}
     - Sociology:  {"decision": "adopt"|"reject"|"defer", "confidence": float, "reasoning": string} -->

**Critical constraints for LLM prompts** (domain-neutral):
- System prompt must NOT name the phenomenon (finance-appendix examples of forbidden phrase types: "carry trade", "flash crash", "anchoring bias"; opinion equivalents: "polarization cascade", "echo chamber"; epidemics: "super-spreader", "herd immunity")
- System prompt must NOT mention the state-update law or its coefficients (finance appendix: the price formula and its λ, γ, σ parameters)
- The output format block is mandatory — copy it exactly as shown above
- Always `<analysis>` not `<think>`


### 4.2.3 LLM Decision Field Access Rule

The `decide()` method in every LLM-based variant (finance appendix: LLM / RuleLLM / Rag) MUST read **every decision field declared in target §4.1.{X} appendix** directly from the LLM response via `decision["key"]`. NEVER derive or infer a missing field from another field (finance-appendix example: deriving `action` from the sign of `quantity`). If any field is missing because the prompt/parser contract is wrong, it must fail-fast via `KeyError`; if the contract is already correct and stochastic malformed API output remains, use only the explicit counted fallback policy in `00-overview.md` Principle #6.

<!-- Finance-appendix (§4.1.F) instantiation — the four required decision fields
     are: action, bid_price, quantity, reasoning. -->

Constraint and execution logic MUST branch on the categorical decision field, not on the sign of a numeric magnitude field:
- Finance appendix: `if action == "buy"` / `elif action == "sell"` instead of `if quantity > 0` / `elif quantity < 0`; `quantity` is always positive per format specification.
- Opinion appendix: `if speech_act == "assert"` / `elif speech_act == "defer"`, not on the sign of `opinion`.
- Epidemics appendix: `if contact_action == "meet"` / `elif contact_action == "avoid"`, not on `contact_count > 0`.

**Why**: Deriving fields silently masks missing fields and introduces incorrect values. The principle is that `decide()` should be a pure function that derives outputs from inputs without inferring missing data.

### 4.2.4 `analysis.py` Structure (LLM Variant)

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
    """Analyze distribution of the categorical decision field per agent type
    (finance appendix: buy / sell / hold)."""
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
- `analysis.py` reuses core metrics from Rule/analysis.py — no additional variant-specific analysis function

**Design principle**: The embedded rules are **deeper agent characterization**, not executable mandates. They define what the agent knows, how they habitually think, and what quantitative frameworks they follow. The LLM uses these rules as guidance alongside its persona to make intelligent, context-aware decisions. This is a simulation of an informed decision-maker, not a rule executor (finance appendix: an informed investor).

### 4.3.2 RuleLLM Prompt Structure

Domain-neutral shell:

```python
{CLASS_NAME}_SYSTEM = """
== PERSONA ==

You are a [role description] operating in the target domain.

CORE BELIEF: [Identical to LLM variant persona]

YOUR PSYCHOLOGY:
[Identical to LLM variant psychology description]

== DECISION RULES ==

You follow these quantitative rules based on the environment state broadcast:

RULE 1 — [Trigger Name]:
  When: [Condition on broadcast fields, e.g., "{state_deviation} < −0.15"]
  Action: [Exact categorical action + magnitude formula in the target §4.1.{X} action space]

RULE 2 — [Next Trigger]:
  When: [Condition]
  Action: [Action]

DEFAULT: [Neutral action — e.g., hold / defer / no-op] when no rule triggers.

RULE COMPLIANCE: You MUST follow the categorical direction of the triggered rule.
You may adjust the magnitude by up to ±20% based on context, but the direction is non-negotiable.
Explain your adherence or adjustment in the <analysis> section.

OUTPUT FORMAT:
First output your reasoning inside <analysis>...</analysis> tags,
then output your decision inside <decision>...</decision> tags.
The decision must be valid JSON with exactly the fields declared in target §4.1.{X} appendix.
IMPORTANT: numeric fields MUST be numeric values (e.g., 10.5), NOT expressions or formulas.
"""
```

<details>
<summary>Finance-appendix (§4.1.F) instantiation — full RuleLLM prompt template</summary>

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

</details>

**Critical**: The `== DECISION RULES ==` section must reproduce the EXACT formulas from `Rule/players.py → _make_decision()` for the same agent class. If Rule parameters change, update this section immediately.

---

## 4.4 Rag Variant Implementation

### 4.4.1 Key Differences from RuleLLM

- `players.py`: Each agent class (finance appendix: investor class) adds `_initialize_rag()` and uses retrieval in `step()`
- `prompts.py`: User prompt template adds `{rag_context}` placeholder
- `analysis.py`: Adds `analyze_rag_knowledge_effect()`
- `players.yml`: Each agent has `rag:` configuration block

### 4.4.2 Rag Player Additional Methods

Domain-neutral shell:

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

def _formulate_knowledge_query(self, state_broadcast: dict) -> str:
    """Build retrieval query from the current environment state broadcast.

    Query strategy: choose regime-appropriate language for whichever state signal
    the target §4.1.{X} appendix identifies as the primary deviation-from-anchor signal,
    then concatenate scenario-relevant vocabulary.
    """
    deviation = state_broadcast["{deviation_field}"]  # from target §4.1.{X} appendix
    if deviation < -0.10:
        return f"[low-regime historical context] deviation {deviation:.2f}"
    elif deviation > 0.10:
        return f"[high-regime historical context] deviation {deviation:.2f}"
    else:
        return f"[normal-regime historical context] deviation {deviation:.2f}"

def _get_rag_context(self, state_broadcast: dict) -> str:
    """Retrieve relevant documents and format as context string."""
    query = self._formulate_knowledge_query(state_broadcast)
    docs = self._knowledge_store.query(query)
    if not docs:
        return "(No relevant knowledge retrieved this round.)"
    return "\n\n".join(f"[Context {i+1}]: {doc}" for i, doc in enumerate(docs))
```

<details>
<summary>Finance-appendix (§4.1.F) instantiation — <code>_formulate_knowledge_query</code></summary>

```python
def _formulate_knowledge_query(self, market_data: dict) -> str:
    """Build retrieval query from current market state."""
    deviation = market_data["deviation"]
    # Query strategy: use current market state language to retrieve relevant historical context
    if deviation < -0.10:
        return f"forced liquidation crisis deviation {deviation:.2f} market crash"
    elif deviation > 0.10:
        return f"overvalued market bubble deviation {deviation:.2f}"
    else:
        return f"normal market conditions deviation {deviation:.2f}"
```

</details>

<!-- Non-finance domain instantiations of the RAG query strategy:
     - Opinion:    low-regime → "polarization backlash minority-view suppression"
                   high-regime → "consensus cascade majority reinforcement"
                   normal    → "steady-state discussion balanced opinion"
     - Epidemics:  low-regime → "outbreak tail decline recovery phase"
                   high-regime → "acceleration wave super-spreader event"
                   normal    → "endemic baseline low incidence"
     - Sociology:  low-regime → "adoption stall abandonment reversal"
                   high-regime → "diffusion cascade tipping point"
                   normal    → "steady adoption S-curve middle" -->


### 4.4.3 `_RAG_FALLBACK` Constant

Every Rag `analysis.py` must define:

```python
_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"
```

This exact string is checked by `analyze_rag_knowledge_effect()` to distinguish successful from failed retrievals.

### 4.4.4 User Prompt Template for Rag

Domain-neutral shell:

```python
{CLASS_NAME}_USER = """Current Environment State:
{state_broadcast_lines}   # one line per broadcast field from target §4.1.{X}
- Round: {round}

Your Local State:
{agent_local_state_lines} # from §4.{N}.5

Relevant Historical Knowledge:
{rag_context}

What is your decision for this round?"""
```

<details>
<summary>Finance-appendix (§4.1.F) instantiation — Rag user prompt template</summary>

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

</details>

The `{rag_context}` placeholder is filled at runtime with either retrieved documents or the fallback string.

---

## 4.5 Implementation Quality Checklist

After implementing each variant:

- [ ] All agent classes have docstrings citing `simulation-bases.md §4.{N}`
- [ ] All numeric values in `_make_decision()` are loaded from config, not hardcoded
- [ ] `perceive()` initializes state correctly on first call
- [ ] `step()` always sends exactly one action message (finance appendix: one order message)
- [ ] LLM prompts do NOT name the phenomenon or mention the state-update law (finance appendix: the price formula and its λ, γ, σ parameters)
- [ ] LLM prompts end with canonical `OUTPUT FORMAT` block using `<analysis>` tags
- [ ] RuleLLM prompts have both `== PERSONA ==` and `== DECISION RULES ==` sections
- [ ] `Rule/analysis.py` uses `load_results()` + `_load_data()` — no raw `os.listdir()` + `json.load()` on record files
- [ ] `Rule/analysis.py` exports `_load_data` and metric/validation functions for import by other variants
- [ ] Every LLM-based variant's `analysis.py` imports `_load_data` from `Rule/analysis.py` (finance appendix: LLM/RuleLLM/Rag)
- [ ] Rag `analysis.py` defines `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"`
- [ ] All `__init__.py` files present

- [ ] Every LLM-based `decide()` reads every decision field declared in target §4.1.{X} directly — no derivation from another field (finance-appendix example: no derivation of `action` from the sign of `quantity`)
- [ ] Constraint/execution logic branches on the categorical decision field, not on the sign of a numeric magnitude field
- [ ] `validate_order()` (or the domain-appropriate `validate_action()` equivalent) called before returning the action dict

#### Strict no-default compliance checklist

- [ ] No `.get(key, default)` on simulation data dicts (config extras, message payloads, LLM responses, coordinator data) — use `dict["key"]`
- [ ] No `if X else fallback` for required data fields (finance-appendix example of a forbidden pattern: `if fundamentals else 1.0`)
- [ ] No silent neutral-action substitution when LLM parse fails (finance-appendix example: silent `hold` substitution) — must `raise RuntimeError` or use explicit counted stochastic API fallback under `00-overview.md` Principle #6
- [ ] No `if rates else 0.0` for computed metrics — must `raise ValueError` if no data collected
- [ ] No `payload.get("field", None)` in analysis scripts — use `payload["field"]`
- [ ] Only legitimate `.get()` exceptions remain: RAG config resolution, `__getstate__`/`__setstate__`, truly optional config sections, matplotlib defaults

#### `analysis.py` output standard checklist

- [ ] Console output header: `=== {SCENARIO} SIMULATION VALIDATION: VALID|INVALID ===`
- [ ] Overall Fit Score printed with `(threshold: 50%)` label
- [ ] Each criterion block has: `[N]` label, `Observed:`, `Expected:` with calibration range, `Score:`, `Assessment:` with qualitative discussion
- [ ] Assessment text cites the calibration source from `analysis-bases.md §6` (author + year)
- [ ] Criterion weights documented in `_validate_*` docstring and sum to 1.0
- [ ] `[SUMMARY]` block present at end of interpretation
- [ ] Produces exactly 4 PNG files: `00_agent_actions.png`, `01_*.png`, `02_*.png`, `03_*.png` in `{base_dir}/analysis/`
- [ ] Saves `summary.json` containing `metrics`, `validation` (with `.score`, `.is_valid`, `.criteria`, `.interpretation`)
- [ ] `py_compile` passes on each built variant's `analysis.py` file (variants marked `Yes` in target §10.1)
