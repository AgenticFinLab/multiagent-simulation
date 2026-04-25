# Root Document Specifications

## Purpose

This file defines the complete content specifications for the two root-level documents that every simulation must have:

1. **`simulation-bases.md`** — 9-section theoretical and design foundation
2. **`analysis-bases.md`** — 7-section analysis methodology foundation

These documents are the single source of truth for their respective domains. All four variant implementations (`explain.md`, `analysis.md`, `players.py`, `analysis.py`) trace back to these documents.

---

## Part I: `simulation-bases.md` — Theoretical and Design Foundation

**Location**: `examples/{SimulationName}/simulation-bases.md`

**Writing principle**: Write this document **before any code**. It drives all implementation decisions. Every investor type defined here must have a corresponding class in all four `players.py` files. Every parameter value must have a source citation.

---

### §1 Phenomenon Definition

```markdown
# {SimulationName} — Simulation Design Basis

## 1. Phenomenon Definition

| Item               | Description                                                                                          |
|--------------------|------------------------------------------------------------------------------------------------------|
| Phenomenon Name    | [Full name, common name, brief one-sentence description]                                             |
| Category           | [Type: herding / bubble / crash / leverage / behavioral bias / manipulation / etc.]                  |
| Core Mechanism     | [2-3 sentences: the key self-reinforcing or dynamic that produces the phenomenon]                    |
| Real-World Origin  | [Historical event(s), dates, markets, and scale of impact]                                           |
| Research Relevance | [Why this phenomenon matters to financial stability, behavioral finance, market efficiency research] |
```

**Quality criteria**: The Core Mechanism must be specific enough that a reader unfamiliar with the phenomenon can understand what drives it. Avoid generic phrases like "positive feedback." State what specific agent behavior creates the feedback.

---

### §2 Theoretical Foundation

This section establishes the academic basis for the entire simulation. Every theory here is later referenced by investor entries in §4 and parameters in §6.

**For EACH theory (minimum 2, maximum 6):**

```markdown
### Theory: [Full Theory Name]

- **Citation**: [Author, Year. "Title." *Journal Name*, Volume(Issue), Pages. https://doi.org/...]
- **Core Insight**: [2-3 sentences on the key mechanism this theory establishes. Use precise language — avoid paraphrasing away the rigor.]
- **Mathematical Formulation**:
  [The central equation(s) of this theory, as they apply to this simulation. Use LaTeX-style notation if helpful.]
  Example: `D_spec(t) ∝ (P(t) − MA(t)) / MA(t)` — momentum demand proportional to trend
- **Empirical Evidence**:
  [Key empirical studies and stylized facts that support this theory. Include parameter estimates where available.]
  Example: "Jegadeesh & Titman (1993) document momentum returns of 1–2% per month over 3–12 month horizons."
- **Relevance to This Simulation**: [Which investor(s) in §4 embody this theory; what aspect of the phenomenon this theory explains.]
- **Calibration Implication**: [What this theory implies about parameter choices — especially thresholds, sizes, and timing.]
```

**Quality criteria**:
- Every citation must include journal name, volume/issue, pages, and DOI where available.
- Mathematical Formulation must be present for every theory — do not omit because "no closed form exists"; write the verbal model precisely.
- Empirical Evidence must cite specific studies with quantitative findings, not just "has been documented."

---

### §3 Market Design Principles

#### §3.1 Price Formation Model

```markdown
### 3.1 Price Formation Model

**Formula**:
```
P(t+1) = P(t) + λ · D(t) + γ · [F(t) − P(t)] + ε(t)
```

**Variable Definitions**:

| Symbol | Name                 | Definition                                              | Role in Phenomenon            |
|--------|----------------------|---------------------------------------------------------|-------------------------------|
| P(t)   | Current price        | Market price at start of round t                        | State variable                |
| D(t)   | Net demand           | Σ buy_quantity − Σ sell_quantity across all investors   | Drives price change           |
| F(t)   | Fundamental value    | Intrinsic value; [constant / grows at rate g per round] | Mean reversion anchor         |
| λ      | Price impact         | Sensitivity of price to net demand                      | [Calibrated value and source] |
| γ      | Mean reversion speed | Speed of correction toward F                            | [Calibrated value and source] |
| ε(t)   | Noise                | ~ N(0, σ²)                                              | Background randomness         |

**Calibration Rationale**:
For EACH parameter (λ, γ, σ):
- Typical empirical range: [from literature]
- Chosen value: [specific value]
- Source: [full citation]
- Sensitivity: [High/Medium/Low — what changes if this parameter is varied ±50%]

**Economic Rationale**:
[Why each term is included. Why this combination of λ and γ is chosen to produce the target phenomenon.
For example: "High λ + low γ creates bubble-prone dynamics because demand shocks are amplified
and mean reversion is too slow to correct them within the simulation time horizon."]

**Dynamic Properties**:
- When D(t) > 0: [what happens to price; which agents drive this]
- When D(t) < 0: [what happens; cascade implications if applicable]
- When P >> F: [mean reversion magnitude; which agents activate]
- When P << F: [recovery mechanics; which agents activate]
- Noise effect: [what it represents economically; how it prevents determinism]
```

#### §3.2 Additional Market Mechanisms

For EACH mechanism beyond the price formula:

```markdown
**[Mechanism Name]**:
- Trigger: [Precise condition — e.g., "equity_ratio < 0.70" or "deviation < −0.15"]
- Action: [What the market does — prevent, force, cap, add cost]
- Economic Rationale: [Why this mechanism exists in real markets; which institution enforces it]
- Source: [Citation for the real-world institution/regulation that motivates this]
- Simulation Implementation: [How it is encoded in `_clear_market()` or other Market method]
```

#### §3.3 Information Broadcast Design

```markdown
### 3.3 Information Broadcast Design

Each round, the Market broadcasts to all investors:

| Field         | Type   | Definition                                | Rationale for Inclusion                 |
|---------------|--------|-------------------------------------------|-----------------------------------------|
| `price`       | float  | Current market price after order clearing | Primary signal for all agents           |
| `fundamental` | float  | Intrinsic fundamental value               | Required by value-sensitive agents      |
| `deviation`   | float  | (price − fundamental) / fundamental       | Pre-computed; used by most agents       |
| `round`       | int    | Current round number                      | Needed for frequency-controlled traders |
| [field]       | [type] | [definition]                              | [why included, which agents use it]     |

**Design Notes**:
[Explain any deliberate exclusions — e.g., "return_pct is NOT broadcast; all agents reference deviation only — this is consistent with relative value framing." Explain any unusual inclusions.]
```

---

### §4 Investor Taxonomy — The 7-Part Standard

**This is the most critical and detailed section of `simulation-bases.md`.** It defines every investor type at the economic archetype level — independent of any variant's implementation.

**Critical constraint**: Section §4 must NOT contain any of the following:
- `Rule-Based Behavior` (IF/THEN formulas, specific threshold values, code logic)
- `LLM Persona` (prompt personality text, signal interpretation guidelines)
- `RuleLLM Hybrid Notes` (embedded rule text for prompts)

These belong in each variant's `explain.md §2`. The §4 investor description defines **what the investor IS economically**, not **how any variant encodes it**.

---

#### 7-Part Investor Design Standard

For EACH investor type (minimum 4, maximum 7):

```markdown
### Investor: {ClassName}

#### 4.{N}.1 Summary

[One to two paragraphs. State: (1) who this investor represents in real financial markets,
(2) what economic role they play in this specific phenomenon (destabilizing / stabilizing /
amplifying / neutral), (3) what makes them behaviorally distinct from other investor types
in this simulation, (4) what the simulation would lose if this type were absent.]

Example:
"The ConcentratedFund represents a highly leveraged family office that holds large synthetic
equity exposure via Total Return Swaps (TRS), invisible to public disclosure requirements.
In the Archegos phenomenon, such funds represent the primary source of hidden systemic risk:
their forced liquidation triggers a cascade that none of the prime brokers individually
anticipated. Without this investor, the cascade mechanism does not initiate — this agent is
the single necessary precondition for the phenomenon."
```

```markdown
#### 4.{N}.2 Theoretical and Empirical Foundation

[For EACH supporting theory or empirical study — minimum 2:]

**Theory/Study [k]: [Full Name]**

- Citation: [Author(s), Year. "Full Title." *Journal Name*, Volume(Issue), Pages–Pages. https://doi.org/...]
- Core Insight: [2-3 sentences on the specific mechanism this work establishes.]
- Mathematical Formulation:
  [The key equation(s) from this work, as relevant to this investor.]
  Notation: [Define every symbol used.]
- Empirical Evidence:
  [Specific quantitative findings from this work or associated studies.
   Examples: "Mean adjustment factor α ≈ 0.3–0.5 across 12 experimental studies (Tversky & Kahneman, 1974)."
   "Momentum returns average 1.0% per month at 12-month horizon (Jegadeesh & Titman, 1993)."]
- Relevance to This Investor:
  [Precisely how this investor's design operationalizes this theory.
   What specific parameter values or behavioral rules derive from this work.]
- Parameter Calibration:
  [Which parameters in §6 are set based on this work, and what the cited range is.]
```

```markdown
#### 4.{N}.3 Design Purpose and Activation Scenarios

**Purpose**: [One sentence: what market dynamic does this investor generate or counteract?]

**Activation Scenarios**:

| Market Condition                        | This Investor's Response | Economic Effect                    | Relevant Theory       |
|-----------------------------------------|--------------------------|------------------------------------|-----------------------|
| [Condition A — e.g., deviation < −0.15] | [What action, what size] | [Effect on price, on other agents] | [§2 theory reference] |
| [Condition B — e.g., price rising > 1%] | [What action]            | [Effect]                           | [Reference]           |
| [Condition C — e.g., normal market]     | Hold / no action         | [Stabilizing / neutral]            | —                     |

**Market Contribution**: [Stabilizing / Destabilizing / Neutral — quantitative rationale.
Example: "Strongly destabilizing: a single forced sell of 50% of position (≈1500 shares at
2× normal volume) causes deviation to drop ~5% in one round, which triggers PrimeBroker1."]

**Interaction Effects**:
[Which specific other agents does this investor amplify, counteract, or depend on?
What is the order-of-operations dependency? Example: "Must sell BEFORE PrimeBroker1
threshold is crossed, or cascade doesn't initiate."]
```

```markdown
#### 4.{N}.4 Behavioral Framework

This section defines the investor's decision logic at the archetype level — independent of
any specific variant implementation. It describes WHAT the investor does and WHY, in
economic/mathematical terms, leaving all variant-specific encoding to the variant's own
explain.md.

##### 4.{N}.4.1 Decision Information Set

[List every market signal this investor uses. For each signal, explain the information-theoretic
or behavioral rationale for including it (or excluding it).]

| Signal        | Used?  | Rationale                                                                             |
|---------------|--------|---------------------------------------------------------------------------------------|
| `price`       | Yes    | [Why — e.g., "trigger condition is price-level based"]                                |
| `fundamental` | Yes/No | [If No: why excluded — e.g., "behavioral bias means this agent ignores fundamentals"] |
| `deviation`   | Yes/No | [Rationale]                                                                           |
| `round`       | Yes/No | [Rationale — e.g., "frequency-control logic requires round number"]                   |
| [other]       | Yes/No | [Rationale]                                                                           |

**Information asymmetry note**: [Does this investor have unique information? Do they perceive
market signals differently from other agents (e.g., through a cognitive bias filter)? Be explicit.]

##### 4.{N}.4.2 Core Behavioral Mechanism

[Full narrative description of the decision process — minimum 4 paragraphs. This must be
precise enough that BOTH a deterministic formula AND an LLM persona can be independently
derived from it without further information.]

Paragraph 1 — Perception: What does this investor observe, and how do they interpret it?
Are there perceptual biases (anchoring, availability, confirmation)? What constitutes a
"normal" vs "alarming" signal for this investor?

Paragraph 2 — Trigger Logic: What specific condition(s) activate this investor? What is
the economic rationale for the threshold level? What does "crossing the threshold" mean
economically (e.g., "margin call occurs when equity falls below maintenance margin")?

Paragraph 3 — Action and Sizing: Once triggered, what does the investor do? How is the
trade size determined? What constraints bound the action (cash, position, leverage, caps)?
Express the sizing logic in economic terms (e.g., "sells proportional to depth of margin
breach, bounded by remaining position").

Paragraph 4 — State and Memory: Does this investor maintain persistent state across rounds?
What information do they remember? How does their state evolve? (e.g., "maintains a 60-round
rolling price history," "belief variable compounds confirming signals," "anchor is set once
at initialization and never updated").

##### 4.{N}.4.3 Mathematical Model

[Formal specification of the decision logic. This is the authoritative mathematical description
from which all variant implementations derive their formulas.]

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

**Model Limitations**:
[Any deliberate simplifications. Example: "The model assumes a discrete single threshold
for margin calls, whereas real margin agreements involve dynamic margin curves. This
simplification is consistent with the agent-based modeling literature (LeBaron, 2006)."]

##### 4.{N}.4.4 Behavioral Properties

| Property               | Value                                                                        | Rationale                                             |
|------------------------|------------------------------------------------------------------------------|-------------------------------------------------------|
| Time Horizon           | [High-frequency / Day trader / Position trader / Long-term]                  | [Why — grounded in §4.{N}.2 citations]                |
| Risk Tolerance         | [Low / Medium / High / Extreme]                                              | [Why — grounded in §4.{N}.2]                          |
| Decision Frequency     | [Every round / Every N rounds / Condition-triggered]                         | [Mechanism driving frequency]                         |
| Information Processing | [Rational / Biased / Noise-driven]                                           | [Which bias, if any — with literature source]         |
| Psychological Profile  | [Key traits — e.g., "overconfident, denial-resistant, emotionally reactive"] | [Source: §4.{N}.2 studies that document these traits] |
```

```markdown
#### 4.{N}.5 Decision Process Walkthrough

A step-by-step trace of one complete representative decision cycle, using concrete example
values. This serves as a "worked walkthrough" that clarifies the §4.{N}.4 narrative.

**Example Market State**:
- Round: [t]
- Price: [P(t)] — [significance, e.g., "5% below fundamental"]
- Fundamental: [F]
- Deviation: [δ = (P−F)/F = value]
- Cash: [C]
- Position: [pos] shares
- [Other relevant state: e.g., rolling average, belief variable]

**Decision Trace**:

Step 1 — Perception:
  Investor observes δ(t) = [value].
  [What this means to the investor — e.g., "This crosses the −0.15 leverage trigger,
  signaling that the maintenance margin has been breached."]

Step 2 — Trigger Check:
  Check: δ(t) = [value] < −θ = −[threshold]?  → [Yes/No]
  [Economic interpretation: e.g., "Yes — margin call condition is satisfied."]

Step 3 — Sizing:
  Q* = position × φ = [pos] × [fraction] = [result] shares
  Constraint check: Q* ≤ position ✓ (or: cash check for buyers)

Step 4 — Action:
  Decision: action = [buy/sell/hold], quantity = [Q*], bid_price = [P(t)]
  [Why this price — e.g., "market order; willing to take current price"]

Step 5 — Market Impact:
  This order contributes [+/−][Q*] to net demand D(t).
  Price effect (approximate): ΔP ≈ λ × (−Q*) = [value] × (−[Q*]) = −[result]
  [Interpretation: e.g., "Drives price down ~[X]%, bringing deviation to ~[Y]%."]
```

```markdown
#### 4.{N}.6 Worked Numerical Example

A fully calculated numerical example using the parameter values from §6.

**Inputs**:
| Variable | Value   | Source                     |
|----------|---------|----------------------------|
| P(t)     | [value] | Round t market price       |
| F        | [value] | Fundamental value (§6)     |
| δ(t)     | [value] | (P−F)/F                    |
| position | [value] | Agent holds [value] shares |
| cash     | [value] | Agent holds $[value]       |
| [param]  | [value] | From §6 parameter table    |

**Calculation**:
```
Step 1: Check trigger: δ(t) = [value] < −[threshold] = −[θ]  → [True/False]
Step 2: [If True] Compute Q*: Q* = [pos] × [φ] = [result] shares
Step 3: Constraint: Q* = [result] ≤ position = [pos] ✓
Step 4: Submit order: sell [result] shares at [price]
```

**Expected Market Impact**:
Net demand contribution: D += −[result]
Price update (before mean reversion and noise):
  ΔP_demand = λ × D = [λ] × (−[result]) = −[value]
  P(t+1) ≈ [P(t)] − [value] = [new_price]
  New deviation: ([new_price] − [F]) / [F] = [new_deviation]

[1-sentence economic interpretation of what this means for the phenomenon.]
```

```markdown
#### 4.{N}.7 Academic References

Complete bibliography for all sources cited in §4.{N}.2 through §4.{N}.4.4.
These may overlap with §2 (Theoretical Foundation) — that is acceptable and expected.

| #   | Full Citation                                                       | Contribution to This Investor Design                         |
|-----|---------------------------------------------------------------------|--------------------------------------------------------------|
| 1   | [Author(s), Year. "Full Title." *Journal*, Vol(Issue), Pages. DOI.] | [What aspect of this investor's design this source supports] |
| 2   | [Author(s), Year. "Full Title." *Journal*, Vol(Issue), Pages. DOI.] | [Contribution]                                               |
| ... | ...                                                                 | ...                                                          |
```

---

### §5 Agent Diversity Verification

```markdown
## 5. Agent Diversity Verification

| Diversity Criterion              | Met? | Evidence                                                                                                    |
|----------------------------------|------|-------------------------------------------------------------------------------------------------------------|
| Different time horizons          | Yes  | [List: e.g., "ConcentratedFund: medium-term; PrimeBroker1: high-frequency; BlockTradeBuyer: opportunistic"] |
| Different information processing | Yes  | [Which agents use which signals differently]                                                                |
| Conflicting incentives           | Yes  | [Which agents buy when others sell; example scenario]                                                       |
| Mix of stabilizing/destabilizing | Yes  | [Count and names; ratio should be ≥1 stabilizing per 2 destabilizing]                                       |
| Different risk tolerances        | Yes  | [Range: from Low to Extreme; examples]                                                                      |
| Different decision frequencies   | Yes  | [Examples of high-frequency vs. low-frequency actors]                                                       |

**Critical mass check**: [Explain why this investor set is sufficient to produce the target phenomenon.
What is the minimum subset of agents needed? What would break if one type were removed?]
```

---

### §6 Parameter Table

```markdown
## 6. Parameter Table

| Parameter         | Symbol | Value | Typical Range    | Source Citation | Description                      | Sensitivity      |
|-------------------|--------|-------|------------------|-----------------|----------------------------------|------------------|
| initial_price     | P(0)   | [val] | [range]          | [Full citation] | Starting asset price             | Low — scale only |
| fundamental_value | F      | [val] | [range]          | [Full citation] | Intrinsic value baseline         | Medium           |
| price_impact      | λ      | [val] | [range from lit] | [Full citation] | Price change per unit net demand | High             |
| mean_reversion    | γ      | [val] | [range from lit] | [Full citation] | Attraction speed toward F        | High             |
| noise_std         | σ      | [val] | [range]          | [Full citation] | Noise term standard deviation    | Low              |
| [agent param]     | [sym]  | [val] | [range]          | [Full citation] | [Meaning]                        | [High/Med/Low]   |
```

**Quality criteria**:
- Every numeric value must have a source citation that is a real, published work (not "normalization" except for scale-only parameters).
- The Typical Range column must come from the literature, not be invented.
- The Sensitivity column must describe what happens quantitatively, not just say "important."

---

### §7 Communication and Round Structure

```markdown
## 7. Communication and Round Structure

```
Round N (t = 1, 2, ..., T):

  Phase 1 — Market Broadcast:
    Market → all investors: {price, fundamental, deviation, round, [other fields]}
    This message triggers perceive() in all investors simultaneously.

  Phase 2 — Investor Decisions:
    For each investor i:
      perceive(): extract and store market data in custom_state
      decide():   apply strategy (deterministic rule / LLM call / RAG-augmented LLM call)
      act():      construct order message

  Phase 3 — Order Submission:
    Each investor → Market: {action: buy/sell/hold, quantity: Q, bid_price: P}

  Phase 4 — Market Clearing:
    Market.perceive(): collect all orders
    Market.decide():   compute D(t), apply price formula P(t+1) = ...
    Market.act():      broadcast updated state → triggers next round

  Phase 5 — Logging:
    Record market state, all investor states, and orders to EXPERIMENT/.../records/
```

**Round duration interpretation**: [What real-world time period does one round represent?
E.g., "Each round represents one trading day." Justify this choice.]

**Synchronous vs. asynchronous**: [Are agents processing simultaneously? Any ordering dependencies?]
```

---

### §8 Historical Case Studies

For EACH real-world event (minimum 1, recommended 2):

```markdown
## 8. Historical Case Studies

### Event: [Full Event Name]

| Item      | Detail                                                     |
|-----------|------------------------------------------------------------|
| Date      | [Specific dates or period, e.g., "March 24–29, 2021"]      |
| Market    | [Asset class, exchange, geographic scope]                  |
| Trigger   | [The specific catalyst — be precise, not generic]          |
| Duration  | [From onset to resolution; in days, weeks, or months]      |
| Magnitude | [Key quantitative data: peak decline %, losses in $, etc.] |

**Key Dynamics Timeline**:

| Date / Period | Event           | Market Effect         |
|---------------|-----------------|-----------------------|
| [Date]        | [What happened] | [Price/volume effect] |
| [Date]        | [What happened] | [Effect]              |
| ...           | ...             | ...                   |

**Quantitative Evidence**:
[Specific data points with sources — e.g., "ViacomCBS fell 60% from $100 to $40 (SEC, 2022, Archegos Report p.47)"]

**Agent Mappings**:

| Simulation Agent | Real-World Counterpart | Evidence for Mapping                  |
|------------------|------------------------|---------------------------------------|
| [ClassName]      | [Real participant]     | [What makes this mapping appropriate] |

**Lessons for Simulation Calibration**:
[What specific parameter values, timing, or behavioral patterns from this event should be
preserved in the simulation. This section is a key source for RAG variant knowledge base content.]

**Primary Sources**:
[Full citations for the data and analysis in this section.]
```

---

### §9 Variant Comparison Preview

```markdown
## 9. Variant Comparison Preview

| Aspect                        | Rule                                         | LLM                                 | RuleLLM                          | Rag                                           |
|-------------------------------|----------------------------------------------|-------------------------------------|----------------------------------|-----------------------------------------------|
| Decision Logic                | Fixed formulas                               | Persona + LLM reasoning             | Formula-anchored LLM             | RAG-augmented LLM                             |
| Determinism                   | Fully deterministic                          | Stochastic                          | Semi-deterministic               | Stochastic                                    |
| Expected Phenomenon Intensity | [Calibration target]                         | [Expected range; direction vs Rule] | [Near-Rule; deviation from Rule] | [Modified by knowledge; direction vs RuleLLM] |
| Key Behavioral Difference     | Baseline reference                           | [Specific behavioral difference]    | [Specific difference]            | [Specific difference]                         |
| Research Question             | Does the phenomenon emerge from rules alone? | [LLM-specific question]             | [RuleLLM-specific question]      | [RAG-specific question]                       |

**Predicted Ordering**: [E.g., "Expected phenomenon intensity: Rule ≥ RuleLLM > LLM > Rag because ..."]
```

---

## Part II: `analysis-bases.md` — Analysis Methodology Foundation

**Location**: `examples/{SimulationName}/analysis-bases.md`

**Writing principle**: Write this document alongside `simulation-bases.md`, before implementing `analysis.py`. Every metric in §2 must be implemented in every variant's `analysis.py`. §6 calibration targets must cite specific literature values.

---

### §1 Analysis Objectives

```markdown
# {SimulationName} — Analysis Methodology Basis

## 1. Analysis Objectives

| Objective | Research Question                                         | Primary Metric(s)           | Expected Finding (from literature)       | Failure Indicator                           |
|-----------|-----------------------------------------------------------|-----------------------------|------------------------------------------|---------------------------------------------|
| O1        | [Specific question answerable by running this simulation] | [Which metric(s) answer it] | [What the literature predicts; citation] | [What would indicate a calibration failure] |
| O2        | ...                                                       | ...                         | ...                                      | ...                                         |
| O3        | ...                                                       | ...                         | ...                                      | ...                                         |
```

Minimum 3 objectives. Each must be answerable from simulation output — no vague objectives like "understand the phenomenon."

---

### §2 Core Metrics Catalogue

For EACH metric (minimum 6, including all mandatory types):

```markdown
### Metric: [Metric Name]

- **Category**: [Price Dynamics / Volatility / Behavioral / Portfolio / Phenomenon-Specific / Agent Activity]
- **Definition**: [Complete, unambiguous plain-language definition. No ambiguity allowed.]
- **Formula**:
  ```
  [Equation in precise notation]
  where [define every symbol]
  ```
- **Interpretation**:
  - Value = 0: [What this means economically]
  - Value > [threshold]: [What it indicates about the phenomenon]
  - Value < [threshold]: [What it indicates]
  - Typical "healthy" range: [X to Y — from literature or calibration]
- **Academic Basis**:
  [Full citation: Author(s), Year. "Title." *Journal*, Vol(Issue), Pages. DOI.]
  [Brief note on what this citation establishes about this metric's validity or interpretation.]
- **Normal Range**: [Typical values from literature for this type of phenomenon; be specific]
- **Red Flag Threshold**: [Value that indicates a calibration problem; what to adjust]
- **Implementation Notes**: [Which function in `Rule/analysis.py` computes this; data source file]
```

**Mandatory metrics** (must appear in every simulation's `analysis-bases.md`):

| # | Metric Type                      | Rationale                                                             |
|---|----------------------------------|-----------------------------------------------------------------------|
| 1 | Price deviation from fundamental | Primary phenomenon detection metric                                   |
| 2 | Phenomenon intensity measure     | Phenomenon-specific (e.g., bubble ratio, crash depth, bias magnitude) |
| 3 | Volatility metric                | Rolling std of returns or similar; required for risk assessment       |
| 4 | Portfolio / wealth metric        | Tracks agent performance; enables cross-variant comparison            |
| 5 | Volume or activity metric        | Trading intensity proxy; detects silent periods                       |
| 6 | ≥1 phenomenon-specific metric    | Unique to this simulation — not present in generic bubble/crash sims  |

---

### §3 Analysis Dimensions

Minimum 3 dimensions. Typical simulations cover all four listed below:

```markdown
### Dimension [N]: [Descriptive Name — e.g., "Price Cascade Dynamics"]

**Purpose**: [One sentence: what specific question does this dimension answer?]

**Metrics Used**: [List from §2 — e.g., "Price deviation, max drawdown, cascade volatility"]

**Visualization**:
- Plot type: [Line / Bar / Scatter / Histogram / Heatmap]
- X-axis: [What is plotted on X]
- Y-axis: [What is plotted on Y]
- Overlays: [Threshold lines, reference curves, phase annotations]
- File name: [e.g., `price_dynamics.png`]

**Expected Pattern**:
[What the chart should look like if the simulation works correctly.
Be specific: "Price should cross the −15% deviation threshold by round 15–25 and remain
below it for 10–20 rounds before recovering."]

**Comparison Baseline**: [What to compare against — Rule variant as deterministic reference;
historical data from §8 of simulation-bases.md; theoretical prediction from §2 theory]

**Variant-Specific Interpretation Notes**:
- Rule: [What to expect specifically for Rule variant]
- LLM: [What LLM adds or changes in this dimension]
- RuleLLM: [Expected difference from Rule]
- Rag: [Expected difference from RuleLLM]
```

---

### §4 Phase Analysis Framework

```markdown
## 4. Phase Analysis Framework

**Overview**: [Describe the lifecycle of the phenomenon in terms of distinct phases.]

| Phase | Name                    | Entry Condition    | Exit Condition       | Key Indicators       | Expected Duration |
|-------|-------------------------|--------------------|----------------------|----------------------|-------------------|
| 1     | [Onset / Pre-phase]     | [Metric threshold] | [Next threshold]     | [Observable signals] | [Round range]     |
| 2     | [Escalation / Active]   | ...                | ...                  | ...                  | ...               |
| 3     | [Peak / Maximum]        | ...                | ...                  | ...                  | ...               |
| 4     | [Resolution / Recovery] | ...                | Exit condition = end | ...                  | ...               |

**Phase Detection Algorithm**:
[Precise rule for automatically classifying each round into a phase from simulation output.
Example: "Phase 2 (Cascade Onset): first round t where deviation(t) < −0.10 and remains
below −0.10 for at least 3 consecutive rounds."]

**Phase Transition Sensitivity**:
[Which parameters most affect phase transition timing. This is critical for calibration.]
```

---

### §5 Cross-Variant Comparison Framework

```markdown
## 5. Cross-Variant Comparison Framework

**Normalization Protocol**:
[How to make metrics comparable across variants with potentially different run configurations.
Example: "All metrics normalized using the same fundamental_value = 100.0 and initial_price = 100.0.
Use percentages not absolute values."]

**Statistical Test**:
[Which statistical test to use for cross-variant comparison; significance level.
Example: "Two-sample t-test on max_drawdown across 10 simulation runs; α = 0.05."]

**Primary Comparison Axes**:

| Axis                   | Measurement                       | Expected Ordering                                     | Research Implication                      |
|------------------------|-----------------------------------|-------------------------------------------------------|-------------------------------------------|
| Phenomenon onset speed | Round of first threshold crossing | [Which variant is faster/slower; why]                 | [What this tells us about LLM/RAG effect] |
| Phenomenon intensity   | Peak metric value                 | [Expected ordering]                                   | [Implication]                             |
| Behavioral realism     | Qualitative trace analysis        | [Criteria for assessment]                             | [What "more realistic" means]             |
| Decision quality       | Portfolio outcome distribution    | [Which variant performs better; for which agent type] | [Implication]                             |

**Reporting Table Format**:
[Define the exact table structure that cross-variant comparison reports must use.]
```

---

### §6 Expected Results and Validation

```markdown
## 6. Expected Results and Validation

### Expected Stylized Facts

| Fact     | Quantitative Target           | Literature Source (full citation) | How to Verify in Simulation |
|----------|-------------------------------|-----------------------------------|-----------------------------|
| [Fact 1] | [Specific range or threshold] | [Author, Year, Journal, DOI]      | [Which metric, which plot]  |
| [Fact 2] | ...                           | ...                               | ...                         |

### Calibration Targets

| Metric     | Target Range | Source          | Adjustment if Out of Range             |
|------------|--------------|-----------------|----------------------------------------|
| [Metric A] | [Min, Max]   | [Full citation] | [Which parameter to adjust; direction] |
| [Metric B] | ...          | ...             | ...                                    |

### Validation Failure Signs

| Symptom              | Diagnosis                                                    | Corrective Action                                 |
|----------------------|--------------------------------------------------------------|---------------------------------------------------|
| [Observable problem] | [Root cause — which parameter or mechanism is miscalibrated] | [Specific adjustment: parameter name + direction] |
| [Problem]            | [Diagnosis]                                                  | [Action]                                          |
```

---

### §7 Visualization Catalogue

```markdown
## 7. Visualization Catalogue

| Plot Name | Type                         | X-axis  | Y-axis  | Overlays             | Generated By      | Purpose           |
|-----------|------------------------------|---------|---------|----------------------|-------------------|-------------------|
| [name]    | [Line/Bar/Scatter/Histogram] | [Field] | [Field] | [Lines, annotations] | [function_name()] | [What it reveals] |
```

**Minimum required plots** (every simulation must produce all of these):

1. Price vs. Fundamental over time — shows phenomenon emergence
2. Phenomenon intensity metric over time — shows severity and lifecycle
3. Investor/portfolio performance comparison — agent-level analysis
4. Phase detection overlay on price chart — shows phase transitions
5. Cross-variant comparison summary — enables research conclusions

---

## Authorship and Update Policy

- Both `simulation-bases.md` and `analysis-bases.md` are written **before any code** and updated after all variants are complete (especially §9 of simulation-bases.md).
- When agent parameters change (e.g., threshold updated in `players.yml`), the corresponding entry in `simulation-bases.md §6` and any derived `explain.md` files must be updated immediately.
- When a new empirical finding contradicts a calibration value, update the citation AND the parameter value together — never update one without the other.
