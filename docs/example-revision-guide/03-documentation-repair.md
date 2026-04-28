# Documentation Repair

## Purpose

This file specifies how to create or rewrite the four documentation file types for any simulation:
- `simulation-bases.md` (root)
- `analysis-bases.md` (root)
- `{Variant}/explain.md` (per variant × 4)
- `{Variant}/analysis.md` (per variant × 4)

The compliance standard for each file is defined in `02-remediation-standard.md`. This file explains **how** to produce a compliant file from scratch or from a non-compliant existing file.

---

## §1 Preparation: Source Extraction

Before writing any documentation, extract the ground truth from the existing code. This is the single most important step — documentation must describe what the code actually does.

### §1.1 Extract investor types from `Rule/players.py`

```bash
grep "^class " examples/<Scenario>/Rule/players.py
```

This gives you the canonical list of investor classes. Map each to a `§4.N` number (1-indexed, skipping Market).

### §1.2 Extract parameters from `Rule/players.py`

```bash
grep "config.extras\[" examples/<Scenario>/Rule/players.py | sort -u
```

This gives you all parameter names used in the code. These become the §6 parameter table.

### §1.3 Extract decision logic from `Rule/players.py`

Read the `decide()` method of each investor class. The if/then logic reveals:
- The decision thresholds (for §6 and variant explain.md §2)
- The formula structure (for simulation-bases.md §4 Behavioral Framework)
- The signal inputs (for §4 information set)

### §1.4 Extract LLM class names and prompt references

```bash
grep "^class LLM\|^class RuleLLM\|^class RagLLM" examples/<Scenario>/LLM/players.py
grep "^class " examples/<Scenario>/RuleLLM/players.py
grep "^class " examples/<Scenario>/Rag/players.py
```

### §1.5 Check for existing documentation content

Even if existing docs are non-compliant, they may contain useful content to preserve:
- Theory references and author/year citations
- Historical case descriptions
- Metric definitions

Always read existing files before rewriting — extract what is worth keeping.

---

## §2 Creating or Rewriting `simulation-bases.md`

### §2.1 When to create vs. rewrite

| Situation                                                       | Action                    |
|-----------------------------------------------------------------|---------------------------|
| File does not exist                                             | Create from scratch       |
| File exists but < 100 lines, lacks §4 7-part format             | Full rewrite              |
| File exists with ≥100 lines but missing sections                | Targeted section addition |
| File exists, has all 9 sections, only §4 entries need upgrading | Patch §4 entries only     |

### §2.2 Section writing order

Write sections in this order for maximum efficiency — later sections reference earlier ones:

1. **§1 Phenomenon + §1.1 Origin and Source Analysis** — start with the real-world grounding:
   - Write the §1 phenomenon table (name, category, mechanism, origin, relevance)
   - Write §1.1.1 Intellectual Lineage — research the academic history; trace observation → theory → ABM → this simulation (5 paragraphs)
   - Write §1.1.2 Real-World Event Catalogue — search for ≥5 documented real-world episodes; populate table with quantitative Magnitude and named agent Correspondence
   - Write §1.1.3 Book and Practitioner Literature — find ≥2 textbooks or practitioner accounts that directly inform design
   - **Why first**: §1.1.2 establishes the real-world phenomena that §4 agents map to, and §8 case studies expand on. §1.1.1 identifies the theoretical lineage that determines which theories to include in §2.
2. **§3 Market Design** — write the price equation; define all parameters
3. **§4 Investor Taxonomy** — one 7-part entry per investor (most work)
4. **§6 Parameter Table** — extract from §4 entries; add source citations
5. **§2 Theory** — consolidate all references cited in §4 with DOIs; write the 5-part theory entry (Citation, Mechanism, Math, Empirical Evidence, Relevance) for each theory
6. **§5 Agent Diversity** — describe how the investor mix produces the phenomenon
7. **§7 Round Structure** — describe execution sequence; can often reference §3
8. **§8 Historical Cases** — expand 3 episodes from §1.1.2 into full 7-part case entries (Event Profile, Chronological Dynamics, Quantitative Evidence, Agent Mappings, Calibration Lessons, Distinguishing Features, References)
9. **§9 Variant Comparison** — table of Rule/LLM/RuleLLM/Rag on decision mechanism

**Key dependency**: §8 Historical Cases must be written AFTER §4 Investor Taxonomy, because the Agent Mappings table (§N.4) requires knowing all §4.N class names and section numbers. §8 also references §6 parameter names in the Calibration Lessons table (§N.5).

### §2.3 §4 Investor Entry Template

The template below implements the **7-part investor standard** (see `02-root-documents-spec.md §4` and `02-remediation-standard.md §1.2`). Every §4 entry must contain all 7 parts; any abbreviated entry is non-compliant.

```markdown
### §4.N InvestorClassName

#### 4.N.1 Summary

[Two paragraphs:]
[Paragraph 1 — Real-world identity: who this investor represents in actual markets (institution type, strategy style, typical AUM or activity scale).]
[Paragraph 2 — Simulation role: what economic role this investor plays in this specific phenomenon (destabilizing/stabilizing/amplifying/neutral); what the simulation would lose if this type were absent; how it is behaviorally distinct from other investor types.]

#### 4.N.2 Theoretical and Empirical Foundation

[For each supporting theory or empirical study — minimum 2 entries, written in this sub-format:]

**Theory/Study 1: [Full Theory Name]**

- **Citation**: [Author(s), Year. "Full Title." *Journal Name*, Volume(Issue), Pages–Pages. https://doi.org/...]
- **Core Insight**: [2-3 sentences on the specific mechanism this work establishes — not just "X theory says Y"; state the causal chain.]
- **Mathematical Formulation**:
  ```
  [Key equation(s) from this work, as directly relevant to this investor's logic.]
  [Define every symbol used inline.]
  ```
- **Empirical Evidence**: [Specific quantitative findings from this work or associated studies.
  Examples: "Mean adjustment factor α ≈ 0.3–0.5 across 12 experimental studies (Tversky & Kahneman, 1974)."
  "Momentum returns average 1.0% per month at 12-month horizon (Jegadeesh & Titman, 1993)."]
- **Relevance to This Investor**: [Precisely how this investor's design operationalizes this theory. What specific parameter values or behavioral rules derive from this work.]
- **Parameter Calibration**: [Which parameters in §6 are set based on this work, and what the cited range is.]

**Theory/Study 2: [Full Theory Name]**
[Same sub-format as above]

#### 4.N.3 Design Purpose and Activation Scenarios

**Purpose**: [One sentence: what market dynamic does this investor generate or counteract?]

**Activation Scenarios**:

| Market Condition                        | This Investor's Response | Economic Effect                    | Relevant Theory       |
|-----------------------------------------|--------------------------|------------------------------------|-----------------------|
| [Condition A — e.g., deviation < −0.15] | [What action, what size] | [Effect on price, on other agents] | [§2 theory reference] |
| [Condition B — e.g., price rising > 1%] | [What action]            | [Effect]                           | [Reference]           |
| [Condition C — normal market]           | Hold / no action         | [Stabilizing / neutral]            | —                     |

**Market Contribution**: [Stabilizing / Destabilizing / Neutral — quantitative rationale. E.g., "Strongly destabilizing: a single forced sell of 50% of position (≈1500 shares at 2× normal volume) causes deviation to drop ~5% in one round, which triggers PrimeBroker1."]

**Interaction Effects**: [Which specific other agents does this investor amplify, counteract, or depend on? What is the order-of-operations dependency?]

#### 4.N.4 Behavioral Framework

##### 4.N.4.1 Decision Information Set

| Signal                   | Used?  | Rationale                                                                             |
|--------------------------|--------|---------------------------------------------------------------------------------------|
| `price`                  | Yes/No | [Why — e.g., "trigger condition is price-level based"]                                |
| `fundamental`            | Yes/No | [If No: why excluded — e.g., "behavioral bias means this agent ignores fundamentals"] |
| `deviation`              | Yes/No | [Rationale]                                                                           |
| `round`                  | Yes/No | [Rationale — e.g., "frequency-control logic requires round number"]                   |
| [other broadcast fields] | Yes/No | [Rationale]                                                                           |

**Information asymmetry note**: [Does this investor have unique information? Do they perceive market signals differently from other agents through a cognitive bias filter?]

##### 4.N.4.2 Core Behavioral Mechanism

[4 paragraphs:]

Paragraph 1 — Perception: what does this investor observe, and how do they interpret it? Are there perceptual biases? What constitutes a "normal" vs. "alarming" signal?

Paragraph 2 — Trigger Logic: what specific condition(s) activate this investor? What is the economic rationale for the threshold level? What does "crossing the threshold" mean economically?

Paragraph 3 — Action and Sizing: once triggered, what does the investor do? How is trade size determined? What constraints bound the action (cash, position, leverage, caps)? Express sizing logic in economic terms.

Paragraph 4 — State and Memory: does this investor maintain persistent state across rounds? What information do they remember? How does their state evolve?

##### 4.N.4.3 Mathematical Model

**Decision Variable**: [What quantity is being computed — e.g., Q*(t) = optimal trade quantity]

**Trigger Function**:
```
[Condition in closed form]
Example: δ(t) < −θ   where δ(t) = (P(t) − F) / F,  θ = leverage_trigger
```

**Sizing Function**:
```
[Formula for Q*(t) — units: shares]
Example: Q*(t) = position(t) × φ    where φ = liquidation_fraction
Bounds: 0 ≤ Q*(t) ≤ position(t)
```

**State Variables** (if any):
| Variable | Type             | Initial Value | Update Rule              | Economic Meaning     |
|----------|------------------|---------------|--------------------------|----------------------|
| [var]    | [float/int/list] | [value]       | [how updated each round] | [what it represents] |

**Parameter Definitions**:
| Symbol | Plain-Language Meaning | Config Path   | Value   | Source Citation |
|--------|------------------------|---------------|---------|-----------------|
| θ      | [meaning]              | extras.[name] | [value] | [citation]      |
| φ      | [meaning]              | extras.[name] | [value] | [citation]      |

**Model Limitations**: [Deliberate simplifications and why they are acceptable for the research question.]

##### 4.N.4.4 Behavioral Properties

| Property               | Value                                                       | Rationale                            |
|------------------------|-------------------------------------------------------------|--------------------------------------|
| Time Horizon           | [High-frequency / Day trader / Position trader / Long-term] | [Why — grounded in §4.N.2 citations] |
| Risk Tolerance         | [Low / Medium / High / Extreme]                             | [Why — grounded in §4.N.2]           |
| Decision Frequency     | [Every round / Every N rounds / Condition-triggered]        | [Mechanism]                          |
| Information Processing | [Rational / Biased / Noise-driven]                          | [Which bias, if any — with source]   |
| Psychological Profile  | [Key traits — e.g., "overconfident, denial-resistant"]      | [Source: §4.N.2 studies]             |

#### 4.N.5 Decision Process Walkthrough

A step-by-step trace of one representative decision cycle using concrete example values:

**Example Market State**:
- Round: [t], Price: [P(t)], Fundamental: [F], Deviation: [δ], Cash: [C], Position: [pos] shares

**Decision Trace**:

Step 1 — Perception: investor observes δ(t) = [value]. [What this means to the investor.]
Step 2 — Trigger Check: check δ(t) = [value] < −θ = −[threshold]? → [Yes/No]. [Economic interpretation.]
Step 3 — Sizing: Q* = position × φ = [pos] × [fraction] = [result] shares. Constraint check: Q* ≤ position ✓
Step 4 — Action: decision = {action: [buy/sell/hold], quantity: [Q*], bid_price: [P(t)]}. [Why this price.]
Step 5 — Market Impact: contributes [±Q*] to net demand D(t). ΔP ≈ λ × (±Q*) ≈ [value]. [Interpretation.]

#### 4.N.6 Worked Numerical Example

**Inputs**:
| Variable | Value   | Source                     |
|----------|---------|----------------------------|
| P(t)     | [value] | Round t market price       |
| F        | [value] | Fundamental value (§6)     |
| δ(t)     | [value] | (P−F)/F                    |
| position | [value] | Agent holds [value] shares |
| [param]  | [value] | From §6 parameter table    |

**Calculation**:
```
Step 1: Check trigger: δ(t) = [value] < −[threshold] → [True/False]
Step 2: [If True] Q* = [pos] × [φ] = [result] shares
Step 3: Constraint: Q* = [result] ≤ position = [pos] ✓
Step 4: Submit order: [buy/sell] [result] shares at [price]
```

**Expected Market Impact**:
D += [±result]; ΔP_demand = λ × D = [λ] × ([±result]) = [value]; P(t+1) ≈ [new_price]
[1-sentence economic interpretation.]

#### 4.N.7 Academic References

| # | Full Citation                                                       | Contribution to This Investor Design                         |
|---|---------------------------------------------------------------------|--------------------------------------------------------------|
| 1 | [Author(s), Year. "Full Title." *Journal*, Vol(Issue), Pages. DOI.] | [What aspect of this investor's design this source supports] |
| 2 | [Author(s), Year. "Full Title." *Journal*, Vol(Issue), Pages. DOI.] | [Contribution]                                               |
```

**How this differs from the old minimal template**:

| Old Template Field                 | New 7-Part Equivalent                                                 | What Was Added                                                                                       |
|------------------------------------|-----------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| Summary (2 lines)                  | §4.N.1 Summary (2 paragraphs)                                         | Real-world identity paragraph added                                                                  |
| Theoretical Foundation (2 bullets) | §4.N.2 (≥2 full theory entries)                                       | Math formulation, empirical evidence, parameter calibration per theory                               |
| Design Purpose (3 bullets)         | §4.N.3 (Activation table + Market Contribution + Interaction Effects) | Quantitative market contribution; named interaction effects                                          |
| Behavioral Framework (4 fields)    | §4.N.4 (4 sub-sections with tables)                                   | Information set table, 4-paragraph mechanism narrative, full math model, behavioral properties table |
| Decision Walkthrough (4 steps)     | §4.N.5 (5 steps with market impact)                                   | Added Step 5 market impact calculation                                                               |
| Worked Example (3 bullets)         | §4.N.6 (Input table + calculation block + expected impact)            | Structured table input; D(t) impact calculation                                                      |
| Academic References (1 bullet)     | §4.N.7 (indexed table with contributions)                             | Explicit statement of what each source contributes                                                   |

### §2.4 Common mistakes to avoid

**§4 content violations** (these belong in variant docs, not in simulation-bases.md §4):
- Do not put `if deviation > threshold: buy` in §4 — this is Rule-specific code, belongs in `Rule/explain.md §2`
- Do not reference any LLM or prompt in §4
- Do not use the same parameter values as another simulation without citing them
- §4.N numbering must match the order used in variant explain.md files

**§1.1 Origin and Source Analysis violations** (newly required — most commonly wrong):
- Do not write §1.1.1 Intellectual Lineage as a bullet list of references — it must be a narrative with paragraphs tracing the chain of influence
- Do not populate §1.1.2 with events that lack quantitative Magnitude — "significant decline" fails; must be "−22.6% in one session"
- Do not populate §1.1.2 Correspondence column with "similar dynamics" — must name specific §4.N class names (e.g., "StopLossTrader §4.4 triggers, MomentumChaser §4.2 amplifies")
- Do not limit §1.1.2 to US markets — must include at least one non-US event
- Do not limit §1.1.2 to recent events — must span multiple decades (pre-2000 events are especially important for intellectual lineage)
- Do not skip §1.1.3 when there are practitioner accounts — regulatory post-mortems (SEC, BIS, BdF reports) count as practitioner literature

**§2 Theory depth violations** (newly required — most commonly underdeveloped):
- Do not write §N.2 Core Mechanism as a single sentence — requires ≥3 paragraphs covering central claim, mechanism chain, boundary conditions, and theoretical debates
- Do not skip §N.3 Mathematical Formulation because "no closed form exists" — write the verbal model as a system of equations with a notation table; approximation is acceptable
- Do not write §N.4 Empirical Evidence as "has been empirically confirmed" — must include a supporting studies table with specific quantitative findings (numbers, units, markets, periods)
- Do not write §N.5 Relevance as "this theory is relevant" — must name specific §4.N investor numbers and specific §3.1 price model terms; must state what parameter values the theory implies
- Do not write §N.3 without a notation table — every symbol in every equation must be defined in the notation table; undefined symbols fail compliance

**§8 Historical Cases depth violations** (newly required — most commonly shallow):
- Do not write §N.3 Quantitative Evidence as prose — must be bullet points with number + unit + full source citation per point; minimum 4 points
- Do not write §N.4 Agent Mappings with only 1–2 agents — all simulation agents must collectively appear in the mappings table across §8; each agent must have at least one historical counterpart
- Do not write §N.5 Calibration Lessons without linking to §6 parameter names — the "Parameter (§6)" column must use the exact parameter name from the §6 table
- Do not use the same real-world event as both §1.1.2 and §8 without expanding it — §8 case entries must be substantially more detailed than §1.1.2 catalogue rows

---

## §3 Creating or Rewriting `analysis-bases.md`

### §3.1 Metric selection

Choose 5–7 metrics that directly measure the simulation's core phenomenon. Every metric must be:
1. Computable from the simulation output data (price_history, agent_states, trade_history)
2. Theoretically motivated (cite a paper that defines or uses this metric)
3. Differentiating across variants (useful for Rule vs. LLM comparison)

### §3.2 Metric naming convention

Use abbreviations that are mnemonic for the phenomenon:
- AssetBubble: BAI, BD, CS, MAF, SSR, RT, WDI
- DispositionEffect: PGR, PLR, DC, HPA, PDI, TRI
- CurrencyCrisis: AII, PSD, DER, SFAF, FAS, RS, WTI

### §3.3 §2 Metric Entry Template

The template below implements the **full structured metric standard** (see `02-root-documents-spec.md §2 Core Metrics Catalogue`). A minimal definition + Python function is no longer compliant; every metric must include interpretation table, academic basis with supporting studies, normal range, red flag threshold, and metric relationships.

```markdown
### Metric: [Metric Name] ([Abbreviation])

#### Category
[Price Dynamics / Volatility / Behavioral / Portfolio / Phenomenon-Specific / Agent Activity / Microstructure]

#### Definition
[Complete, unambiguous plain-language definition. State what is being measured, over what time
window, and with respect to what baseline or reference value. No ambiguity allowed.]

#### Formula
```
[Equation in precise, unambiguous notation — define every symbol]
where:
  [symbol] = [complete definition including units and computation method]
  [symbol] = [definition]
```

**Computation notes**: [How to compute from raw simulation output. Which data files/fields are inputs.
Any edge cases — e.g., "If fundamental = 0, return NaN." "If no stop-loss trades occur, return 0."]

**Python function**:
```python
def metric_name(arg1: List[float], arg2: float, threshold: float = 0.10) -> float:
    """[One-line description of what this function computes].

    Args:
        arg1: [description with units]
        arg2: [description with units]
        threshold: [description, default value and justification from literature]
    Returns:
        [description of return value, units, and what range to expect]
    """
```

#### Interpretation

| Range                           | Economic Meaning                                                  | Simulation Interpretation                                                                                 |
|---------------------------------|-------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| = 0                             | [What zero means theoretically — e.g., "No price crash occurred"] | [What it means in this simulation specifically — e.g., "All agents held positions; no cascade triggered"] |
| (0, threshold_low)              | [Low value meaning]                                               | [Simulation meaning — which phase, which agents active]                                                   |
| [threshold_low, threshold_high] | [Normal range meaning]                                            | [Expected during which phase of the phenomenon]                                                           |
| > threshold_high                | [High value meaning — which phenomenon this indicates]            | [Which agents are dominant; which feedback loop is active]                                                |

#### Academic Basis

**Primary source**:
[Full citation: Author(s), Year. "Title." *Journal*, Vol(Issue), Pages. DOI.]

[2–3 sentences: How does this source establish this metric? Was it proposed here, validated here,
or applied in the same phenomenal context? Does the cited paper define the formula exactly as
written above, or is there an adaptation? If adapted, explain what changed and why.]

**Supporting studies**:

| Study                                     | Context                       | Finding                                     | Relevance to This Metric                            |
|-------------------------------------------|-------------------------------|---------------------------------------------|-----------------------------------------------------|
| [Author(s), Year. "Title." Journal. DOI.] | [Market, period, sample size] | [Specific quantitative result with numbers] | [Why this validates the metric for this simulation] |
| [Study 2]                                 | ...                           | [Quantitative result]                       | ...                                                 |

#### Normal Range (from literature)
[Typical values for this metric in the relevant phenomenon literature. Be specific:
e.g., "Bubble duration in stock markets: 12–24 months (Hong & Stein, 2003); in housing markets:
3–7 years (Glaeser et al., 2008)." This is the range that indicates the simulation is producing
realistic-scale output. If the simulation output falls outside this range, the simulation is
miscalibrated, not the metric.]

#### Red Flag Threshold
- **Too high** (> [value]): [Diagnosis — which parameter is miscalibrated; direction and magnitude to adjust]
- **Too low** (< [value]): [Diagnosis — adjustment direction]
- **Zero for all rounds**: [What this symptom indicates; immediate corrective action — which parameter to check first]

#### Relationship to Other Metrics
[How this metric relates to the others in §2. Does it correlate, diverge, or act as a leading
indicator of another metric? E.g., "BAI typically peaks 3–5 rounds before BD crosses threshold;
if both peak simultaneously, the cascade is unusually fast and price_impact may be too high."
State direction of correlation, timing relationship, and what anomaly means diagnostically.]

#### Implementation Notes
[Which function in `Rule/analysis.py` computes this; input data source (price_history, agent_states,
trade_history); return type and units; any variant-specific adaptation notes.]
```

**How this differs from the old minimal template**:

| Old Template Field                         | New Structured Equivalent                                               | What Was Added                                |
|--------------------------------------------|-------------------------------------------------------------------------|-----------------------------------------------|
| `**Definition**` (1 line)                  | Definition block + computation notes                                    | Edge cases; explicit data source              |
| `**Python function**` (signature only)     | Full Python function with typed Args and Returns docstring              | Arg descriptions, units, return range         |
| `**Interpretation**` (2 bullets)           | Interpretation table (4 rows)                                           | Range-to-simulation-phase mapping             |
| `**Theoretical grounding**` (1 line + DOI) | Academic Basis: primary source (3 sentences) + supporting studies table | Supporting studies with quantitative findings |
| _(absent)_                                 | Normal Range from literature                                            | Calibration anchor from published values      |
| _(absent)_                                 | Red Flag Threshold (3 scenarios)                                        | Diagnostic guidance for miscalibration        |
| _(absent)_                                 | Relationship to Other Metrics                                           | Cross-metric diagnostic logic                 |
| _(absent)_                                 | Implementation Notes                                                    | Code → metric traceability                    |

### §3.4 §6 Expected Results Template

The §6 Expected Results section must be split into **four sub-sections** (see `02-root-documents-spec.md §6`). The old single-table format is non-compliant.

```markdown
## 6. Expected Results and Validation

### 6.1 Expected Stylised Facts

For each stylised fact this simulation is designed to reproduce, provide the quantitative target,
the literature source, and the verification method.

| Fact                                                                           | Quantitative Target                                                         | Literature Source (full citation + DOI) | How to Verify in Simulation             | Failure Indicator                                 |
|--------------------------------------------------------------------------------|-----------------------------------------------------------------------------|-----------------------------------------|-----------------------------------------|---------------------------------------------------|
| [Fact 1 — a specific, measurable stylised fact from the phenomenon literature] | [Specific range or threshold — e.g., "bubble peak ≥ 20% above fundamental"] | [Author, Year, Journal, DOI]            | [Which metric, which phase, which plot] | [What would indicate this fact is NOT reproduced] |
| [Fact 2]                                                                       | ...                                                                         | ...                                     | ...                                     | ...                                               |
| [Fact 3]                                                                       | ...                                                                         | ...                                     | ...                                     | ...                                               |

Minimum 4 stylised facts. Each must be verifiable from simulation output within a single run.

### 6.2 Calibration Targets

| Metric     | Target Range | Lower Bound Source | Upper Bound Source | Adjustment if Below Range     | Adjustment if Above Range     |
|------------|--------------|--------------------|--------------------|-------------------------------|-------------------------------|
| [Metric A] | [Min, Max]   | [Full citation]    | [Full citation]    | [Which parameter + direction] | [Which parameter + direction] |
| [Metric B] | ...          | ...                | ...                | ...                           | ...                           |

**Calibration protocol**:
1. Run the Rule variant for 10 seeds with default parameters.
2. Compute the mean of each metric across runs.
3. Compare against target ranges above.
4. Adjust parameters using the guidance above.
5. Re-run and verify before proceeding to LLM/RuleLLM/Rag variants.

### 6.3 Cross-Variant Predictions

Based on the theoretical expectations from `simulation-bases.md §9`, state the expected direction
of metric change for each variant relative to the Rule baseline.

| Metric     | Rule (Baseline)           | LLM Expected                                    | RuleLLM Expected     | Rag Expected         | Theoretical Basis                       |
|------------|---------------------------|-------------------------------------------------|----------------------|----------------------|-----------------------------------------|
| [Metric A] | [Baseline value or range] | [Higher / Lower / Similar — with justification] | [Expected direction] | [Expected direction] | [§2 theory that predicts this ordering] |

### 6.4 Validation Failure Signs

| Symptom                                                                    | Diagnosis                    | Root Cause                                       | Corrective Action                                           |
|----------------------------------------------------------------------------|------------------------------|--------------------------------------------------|-------------------------------------------------------------|
| [Observable problem — e.g., "Price never deviates > 10% from fundamental"] | [What this symptom tells us] | [Which parameter or mechanism is the root cause] | [Specific adjustment: parameter name, direction, magnitude] |
| [Symptom 2]                                                                | [Diagnosis]                  | [Root cause]                                     | [Action]                                                    |
| [Symptom 3]                                                                | ...                          | ...                                              | ...                                                         |
```

**How this differs from the old §6 template**:

| Old §6 Structure            | New §6 Structure                    | Purpose of Change                                                    |
|-----------------------------|-------------------------------------|----------------------------------------------------------------------|
| Single agent × metric table | §6.1 Stylised Facts table           | Connects to phenomenon literature (quantitative targets with DOI)    |
| Cross-Variant Predictions   | §6.2 Calibration Targets + protocol | Makes §6 actionable: specifies how to calibrate and in what sequence |
| _(combined)_                | §6.3 Cross-Variant Predictions      | Separates calibration targets from variant comparison predictions    |
| _(absent)_                  | §6.4 Validation Failure Signs       | Diagnostic guide: what to check when the simulation misbehaves       |

---

## §4 Rewriting `{Variant}/explain.md`

### §4.1 When a rewrite is required

A `✓(lean)` explain.md typically looks like one of these patterns — all require full rewrite:

| Pattern                   | Symptoms                                                               | Action       |
|---------------------------|------------------------------------------------------------------------|--------------|
| **Agent description doc** | Has "Agent Descriptions" section with parameter lists                  | Full rewrite |
| **Usage guide**           | Has "Usage" section with bash commands for all 4 variants              | Full rewrite |
| **Theory summary**        | Repeats theory from simulation-bases.md without implementation mapping | Full rewrite |
| **Stub**                  | Fewer than 50 lines                                                    | Full rewrite |

### §4.2 Writing each variant's explain.md

#### Rule variant

The `§2` Theory→Implementation mapping tables translate the 7-part investor designs in `simulation-bases.md §4.N` into concrete if/then rules from `Rule/players.py`.

For each investor `§2.N`:
1. Read `simulation-bases.md §4.N` — identify the key behavioral mechanism
2. Read `Rule/players.py` class — identify the exact threshold, formula, and order_size
3. Write 2–3 rows in the mapping table: one row per distinct behavioral rule

Example:
```markdown
### §2.1 NewEconomyEvangelist (simulation-bases.md §4.1)

| Theory Component                    | Implementation                               |
|-------------------------------------|----------------------------------------------|
| Narrative economics (Shiller, 2000) | `if deviation > -0.20: buy order_size (600)` |
| Crash capitulation                  | `if deviation < -0.30: sell order_size // 2` |
```

#### LLM variant

The `§2` tables map from theory to **system prompt instructions**.

```markdown
### §2.1 LLMNewEconomyEvangelist (simulation-bases.md §4.1)

| Theory Component                    | Implementation                                                            |
|-------------------------------------|---------------------------------------------------------------------------|
| Narrative economics (Shiller, 2000) | System prompt: "You believe in the new internet economy paradigm..."      |
| Crash capitulation                  | Persona encodes reluctance to sell; only exits on deep negative deviation |
```

#### RuleLLM variant

The `§2` tables map from theory to **embedded rules in system prompts**.

```markdown
### §2.1 RuleLLMNewEconomyEvangelist (simulation-bases.md §4.1)

| Theory Component                    | Implementation                                                                     |
|-------------------------------------|------------------------------------------------------------------------------------|
| Narrative economics (Shiller, 2000) | System prompt embeds: "Buy when deviation > −0.20; sell only if deviation < −0.30" |
| LLM contextualisation               | LLM reasons about narrative strength but cannot override embedded thresholds       |
```

#### Rag variant

The `§2` tables map from theory to **RAG query and knowledge retrieval**.

```markdown
### §2.1 RagLLMNewEconomyEvangelist (simulation-bases.md §4.1)

| Theory Component                    | Implementation                                                                       |
|-------------------------------------|--------------------------------------------------------------------------------------|
| Narrative economics (Shiller, 2000) | System prompt: narrative-driven buyer persona; RAG retrieves Shiller (2000) passages |
| Historical anchoring                | Retrieved documents moderate or reinforce buying based on retrieved crash evidence   |
```

### §4.3 §1 Overview Table Template

```markdown
## §1 Overview

[1-paragraph description of this variant's approach to the simulation]

| Aspect             | Detail                                                                  |
|--------------------|-------------------------------------------------------------------------|
| Variant            | [Rule / LLM / RuleLLM / Rag]                                            |
| Simulation         | [SimulationName]                                                        |
| Decision Mechanism | [Threshold rules / LLM persona / Rule-embedded LLM / RAG-augmented LLM] |
| Theory Reference   | `simulation-bases.md §4.1–§4.N`                                         |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round` [+ others]                 |
```

---

## §5 Rewriting `{Variant}/analysis.md`

### §5.1 The §2 Metric→Function Table

This is the core of the analysis.md. Copy the 7 metrics from `analysis-bases.md §2` and map each to:
- Its Python function name and arguments (exact match to analysis-bases.md)
- Its `analysis-bases.md §2.X` reference

```markdown
## §2 Metric → Function Mapping

| Metric                       | Function                                                             | analysis-bases.md ref |
|------------------------------|----------------------------------------------------------------------|-----------------------|
| BAI (Bubble Amplitude Index) | `bubble_amplitude_index(price_history, fundamental)`                 | §2.1                  |
| BD (Bubble Duration)         | `bubble_duration(price_history, fundamental, bubble_threshold=0.10)` | §2.2                  |
...
```

### §5.2 The §3 Variant-Specific Notes

Write one bullet point per investor that explains how this variant's mechanism affects the metric measurement:

```markdown
## §3 [Variant]-Specific Notes

- **InvestorName (§4.N)**: [How this variant's mechanism (rule/LLM/RAG) affects this investor's contribution to the metrics]
- **Metric X**: [Specific expected behavior unique to this variant]
```

### §5.3 The §4 Expected Ranges Table

Provide concrete numeric ranges, not "Varies by scenario":

```markdown
## §4 Expected Ranges

| Metric | [Variant] Expected Range | Interpretation                    |
|--------|--------------------------|-----------------------------------|
| BAI    | 0.5 – 1.5                | 50–150% above fundamental at peak |
| BD     | 20 – 50 rounds           | Multi-phase bubble                |
```

For LLM/RuleLLM/Rag variants, add a "vs. Rule Baseline" column to enable direct comparison.

---

## §6 Writing Order for a Full-Create Simulation

When all files are missing, follow this order:

1. **Extract ground truth** from `Rule/players.py` (§1)
2. **Write `simulation-bases.md`** (§2)
3. **Write `analysis-bases.md`** (§3)
4. **Write `Rule/explain.md`** — first explain.md, using sim-bases as reference
5. **Write `Rule/analysis.md`** — first analysis.md
6. **Write `LLM/explain.md`** — maps LLM class names to §4.N
7. **Write `LLM/analysis.md``
8. **Write `RuleLLM/explain.md`**
9. **Write `RuleLLM/analysis.md`**
10. **Write `Rag/explain.md`**
11. **Write `Rag/analysis.md`**

After all docs are written, proceed to `04-code-repair.md` to patch `players.py` docstrings.

---

## §7 Partial Repair Strategy

When only some files need repair (Mixed or Partial-fill task type):

| File Status | Action                                                                |
|-------------|-----------------------------------------------------------------------|
| ✓           | No action needed                                                      |
| ✓(lean)     | Read the file first; extract any useful content; then rewrite to spec |
| -           | Create from scratch using §2–§5 templates above                       |
| ✗           | Create root document from scratch (highest priority)                  |

**Always write root documents first** (`simulation-bases.md`, `analysis-bases.md`) before any variant documents — variant explain.md files depend on the `§4.N` numbering established in `simulation-bases.md`.
