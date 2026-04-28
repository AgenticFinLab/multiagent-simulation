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

### 1.1 Origin and Source Analysis

This subsection provides a deep account of where the simulation phenomenon originates —
its roots in academic literature, its grounding in real-world finance, and the chain of
intellectual development that connects historical events to the theoretical models to this
simulation's design.

#### 1.1.1 Intellectual Lineage

[3–5 paragraphs tracing the origin of this phenomenon:]

Paragraph 1 — Foundational observation: Who first described or documented this phenomenon?
In what context — an empirical observation, a laboratory experiment, a market crisis post-mortem?
What was the original evidence?

Paragraph 2 — Theoretical formalisation: Which academic works first built a mathematical or
conceptual model of this phenomenon? What simplifying assumptions were made? What has been
preserved vs. modified in this simulation?

Paragraph 3 — Empirical confirmation: Which large-scale empirical studies confirmed the
phenomenon across multiple markets, time periods, or asset classes? What are the key stylised
facts established in this literature?

Paragraph 4 — Connection to agent-based modelling: How has this phenomenon been previously
modelled in the ABM / computational finance literature? Which prior ABM studies are closest to
this simulation? What does this simulation add or change?

Paragraph 5 — Simulation design choices: Which specific decisions in this simulation's design
(agent types, thresholds, market mechanism) derive directly from the above literature? Cite
the specific source for each major design choice.

#### 1.1.2 Real-World Event Catalogue

A comprehensive search of all documented real-world events that correspond to this simulation's
phenomenon. This table is the primary RAG knowledge base seed for the Rag variant.

| Event Name | Date(s) | Market / Asset | Trigger             | Magnitude                      | Duration             | Correspondence to Simulation                  | Primary Source                 |
|------------|---------|----------------|---------------------|--------------------------------|----------------------|-----------------------------------------------|--------------------------------|
| [Event 1]  | [Date]  | [Market]       | [What initiated it] | [Peak deviation / loss / drop] | [Time to resolution] | [Which agents, which mechanism — be specific] | [Author/Report, Year, DOI/URL] |
| [Event 2]  | [Date]  | [Market]       | [Trigger]           | [Magnitude]                    | [Duration]           | [Correspondence]                              | [Source]                       |
| [Event 3]  | ...     | ...            | ...                 | ...                            | ...                  | ...                                           | ...                            |

**Minimum**: 3 events. **Recommended**: 5–7 events spanning different time periods and geographic markets.

**Catalogue quality criteria**:
- Every event must have a verifiable primary source (academic paper, regulatory report, or reputable journalism with date and URL)
- Magnitude must be a quantitative figure (%, $, basis points) — not "large" or "significant"
- Correspondence column must name specific simulation agents and mechanisms — not "similar dynamics"
- Events should span multiple decades and geographies to demonstrate the phenomenon's generality

#### 1.1.3 Book and Practitioner Literature

| Title        | Author(s) | Year   | Publisher   | Relevance to This Simulation                                               |
|--------------|-----------|--------|-------------|----------------------------------------------------------------------------|
| [Book Title] | [Author]  | [Year] | [Publisher] | [Specific chapter(s) or concept(s) that directly inform simulation design] |
| [Book Title] | [Author]  | [Year] | [Publisher] | [Relevance]                                                                |

Minimum 2 entries. Include both academic textbooks and practitioner accounts (e.g., memoirs,
regulatory post-mortems) where they document behavioural mechanisms that the simulation models.
```

**Quality criteria**:
- The Core Mechanism must be specific enough that a reader unfamiliar with the phenomenon can understand what drives it. Avoid generic phrases like "positive feedback." State what specific agent behavior creates the feedback.
- §1.1.2 Real-World Event Catalogue is **mandatory** — not optional. A simulation with no documented real-world correspondence is not deployable.
- Every entry in the event catalogue must have a quantitative magnitude column.
- The Intellectual Lineage must trace the path from historical observation → theory → this simulation. It must not simply list references — it must narrate the chain of influence.

---

### §2 Theoretical Foundation

This section establishes the complete academic basis for the entire simulation. Every theory here is later referenced by investor entries in §4 and parameters in §6. The goal is to make this section a self-contained theoretical survey — a reader should be able to understand the intellectual foundation of the simulation without consulting outside sources.

**Minimum**: 3 theories. **Recommended**: 4–6. Each theory must have a full entry as specified below.

**For EACH theory:**

```markdown
### Theory N: [Full Theory Name]

#### N.1 Citation and Status

- **Primary Citation**: [Author(s), Year. "Full Title." *Journal Name*, Volume(Issue), Pages. https://doi.org/...]
- **Theory Status**: [Foundational / Contested / Widely-applied / Emerging — with 1-sentence justification]
- **Original Context**: [The phenomenon/market this theory was originally developed to explain; year of original formulation if different from first citation]

#### N.2 Core Theoretical Mechanism

[3–5 paragraphs. This is the heart of the theory entry:]

Paragraph 1 — Central claim: What does this theory assert about agent behaviour or market dynamics?
State it as a precise, falsifiable claim. Avoid hedged language like "suggests" — be direct.

Paragraph 2 — Mechanism: What is the causal chain the theory proposes? What specific decision
process or incentive structure produces the asserted outcome? Walk through the mechanism step
by step (e.g., "A rises → B responds → C adjusts → D results, which feeds back to A").

Paragraph 3 — Boundary conditions: Under what conditions does the theory hold? What assumptions
are required? Which real-world frictions does it abstract away? Are those abstractions appropriate
for this simulation?

Paragraph 4 — Theoretical debates: What are the main critiques of this theory in the literature?
Are there competing theories that predict different outcomes? How does this simulation resolve
that ambiguity in its design?

#### N.3 Mathematical Formulation

**Core Model**:
```
[Central equation(s) — write the full formal model, not just a sketch]
[Define every symbol inline or in the notation table below]
```

**Notation**:

| Symbol | Meaning                  | Units / Type    | Typical Range               | Source     |
|--------|--------------------------|-----------------|-----------------------------|------------|
| [sym]  | [Plain-language meaning] | [Units or type] | [From empirical literature] | [Citation] |

**Derivation sketch** (if non-trivial):
[The key steps that lead from primitives to the central equation, if the equation is not self-evident.
For well-known models, a 2-3 step sketch is sufficient. For novel combinations, be thorough.]

**Model variants or extensions**:
[Any important extensions of the base model that are relevant to this simulation. For example,
if the base model assumes rational agents but this simulation uses a bounded-rational version,
explain the modification and its source.]

#### N.4 Empirical Evidence

**Supporting Studies**:

| Study                                     | Finding                         | Market / Period      | Sample Size | Relevance                                   |
|-------------------------------------------|---------------------------------|----------------------|-------------|---------------------------------------------|
| [Author(s), Year — "Title," Journal, DOI] | [Specific quantitative finding] | [Where/when studied] | [N]         | [How this supports the theory as used here] |
| [Study 2]                                 | [Finding with numbers]          | [Market]             | [N]         | [Relevance]                                 |

**Key Stylised Facts** (as established by this literature):

1. [Fact 1 — quantitative, e.g., "Mean momentum return = 1.01% per month at 12-month horizon"]
2. [Fact 2]
3. [Fact 3]

**Contradicting Evidence** (if any):
[Studies that find weak or null effects; markets where the phenomenon does not hold; periods of
breakdown. Acknowledging contradicting evidence strengthens the theoretical grounding, not
weakens it.]

#### N.5 Relevance to This Simulation

**Agent mapping**: [Which investor type(s) in §4 embody this theory, and how specifically.]

**Mechanism mapping**: [Which part of the simulation's price formation or decision logic this
theory directly explains — cite §3.1 or §4.N references explicitly.]

**Parameter calibration implication**: [What this theory implies about specific parameter values,
thresholds, or ranges — be quantitative where possible. E.g., "Tversky & Kahneman (1992) estimate
loss aversion coefficient λ ≈ 2.25; this directly calibrates the loss_aversion parameter in §6."]

**Limitations in this context**: [What aspects of the full theory are not captured by this simulation,
and why the simplification is acceptable for the research question being addressed.]
```

**Quality criteria**:
- Every citation must include journal name, volume/issue, pages, and DOI where available.
- Mathematical Formulation §N.3 must be present for every theory — do not omit because "no closed form exists"; write the verbal model precisely and include the notation table.
- Empirical Evidence §N.4 must include a supporting studies table with quantitative findings, not just "has been documented."
- The Relevance §N.5 must name specific §4 investor numbers — "This theory is embodied by §4.2 MarketMaker" not "some agents."
- Theories must be ordered from most foundational to most specific to this simulation.

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

**Purpose**: Section §8 is the empirical grounding of the simulation. It connects the abstract agent-based model to documented real-world episodes, establishes calibration targets derived from historical data, and populates the RAG variant's knowledge base. A simulation without this section cannot be externally validated.

**Minimum**: 2 events. **Recommended**: 3–5, spanning different time periods, markets, and geographic regions to demonstrate the phenomenon's generality.

For EACH real-world event:

```markdown
## 8. Historical Case Studies

### Case N: [Full Event Name]

#### N.1 Event Profile

| Item       | Detail                                                                              |
|------------|-------------------------------------------------------------------------------------|
| Date Range | [Specific dates or period, e.g., "March 24–29, 2021"; "August–October 1987"]        |
| Market     | [Asset class, exchange, geographic scope, e.g., "US equity markets, NYSE + NASDAQ"] |
| Trigger    | [The specific catalyst — precise and verifiable, not generic]                       |
| Duration   | [From onset to resolution; in hours, days, weeks, or months]                        |
| Magnitude  | [Key quantitative data: peak decline %, total loss in $, volatility spike in bps]   |
| Resolution | [How the episode ended: policy intervention, natural correction, bankruptcy, etc.]  |
| Sources    | [Primary sources for this section: regulatory reports, academic papers, articles]   |

#### N.2 Chronological Dynamics

| Date / Period | Event                                             | Market Effect                | Quantitative Measure           |
|---------------|---------------------------------------------------|------------------------------|--------------------------------|
| [Date]        | [What happened — specific action or announcement] | [Price/volume/spread effect] | [Number with units and source] |
| [Date]        | [Event]                                           | [Effect]                     | [Measure]                      |
| [Date]        | ...                                               | ...                          | ...                            |

**Narrative**: [3–5 sentences describing the episode's progression in plain language, tying together the timeline entries above. What made this event escalate? What eventually halted it?]

#### N.3 Quantitative Evidence

[Specific data points with sources. Each bullet must include a number, a unit, and a full source citation.]

- [Metric]: [Value] ([Source: Author/Org, Year, report title or URL, page if applicable])
- [Metric]: [Value] ([Source])
- [Metric]: [Value] ([Source])

Minimum 4 quantitative data points per event.

#### N.4 Agent Mappings

| Simulation Agent | Real-World Counterpart              | Evidence for Mapping                                                       | Behavioural Correspondence                                                     |
|------------------|-------------------------------------|----------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| [ClassName §4.N] | [Real institution/participant type] | [Quote, regulatory filing, or academic analysis establishing this mapping] | [Specific behaviour in the real event that matches the agent's decision logic] |
| [ClassName §4.N] | [Real counterpart]                  | [Evidence]                                                                 | [Correspondence]                                                               |

#### N.5 Simulation Calibration Lessons

[What specific parameter values, timing, or behavioural patterns from this event should inform simulation calibration. Be precise: cite the quantitative evidence from §N.3 and connect it to specific parameters in §6.]

| Parameter (§6) | Historical Value from This Event | Source     | Calibration Implication              |
|----------------|----------------------------------|------------|--------------------------------------|
| [param_name]   | [Value from historical data]     | [Citation] | [How to set or bound this parameter] |

#### N.6 Distinguishing Features

[What makes this specific episode unique compared to other events in this catalogue? What aspect of the simulation does this event best validate? What is the most important lesson this event provides that is NOT captured by other events in the list?]

#### N.7 References for This Case

| # | Full Citation                                               | Content Referenced                          |
|---|-------------------------------------------------------------|---------------------------------------------|
| 1 | [Author(s)/Org, Year. "Title." Journal/Report. DOI or URL.] | [Which part of this case entry it supports] |
| 2 | ...                                                         | ...                                         |
```

**§8 Quality criteria**:
- §N.3 Quantitative Evidence: every data point must have a number, unit, and source. "Prices fell significantly" is not acceptable.
- §N.4 Agent Mappings: every simulation agent must appear in at least one case's mapping table across the full §8. If an agent has no historical counterpart in any documented event, its design must be re-examined.
- §N.5 Calibration Lessons: must close the loop between historical data and §6 parameter values. This section makes §8 actionable, not merely illustrative.
- Events in the catalogue should collectively cover all investor types from §4 — i.e., each investor type should be mapped to at least one real-world counterpart across the full set of cases.

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
### Metric: [Metric Name] ([Abbreviation])

#### Category
[Price Dynamics / Volatility / Behavioral / Portfolio / Phenomenon-Specific / Agent Activity / Microstructure]

#### Definition
[Complete, unambiguous plain-language definition. No ambiguity allowed. State what is being
measured, over what time window, and with respect to what baseline or reference value.]

#### Formula
```
[Equation in precise, unambiguous notation — define every symbol]
where:
  [symbol] = [complete definition including units and computation method]
  [symbol] = [definition]
```

**Computation notes**: [How to compute this from raw simulation output. Which data files / fields
are inputs. Any edge cases — e.g., "If fundamental = 0, return NaN."]

#### Interpretation

| Range                           | Economic Meaning                                      | Simulation Interpretation                       |
|---------------------------------|-------------------------------------------------------|-------------------------------------------------|
| = 0                             | [What zero means theoretically]                       | [What it means in this simulation specifically] |
| (0, threshold_low)              | [Low value meaning]                                   | [Simulation meaning]                            |
| [threshold_low, threshold_high] | [Normal range meaning]                                | [Expected during normal phase]                  |
| > threshold_high                | [High value meaning — what phenomenon this indicates] | [Which phase; which agents active]              |

#### Academic Basis

**Primary source**:
[Full citation: Author(s), Year. "Title." *Journal*, Vol(Issue), Pages. DOI.]

[2–3 sentences: How does this source establish this metric? Was it proposed here, validated here,
or applied in the same phenomenal context? Does the cited paper define the formula exactly as
written above, or is there an adaptation?]

**Supporting studies**:

| Study                                     | Context          | Finding               | Relevance to This Metric                            |
|-------------------------------------------|------------------|-----------------------|-----------------------------------------------------|
| [Author(s), Year. "Title." Journal. DOI.] | [Market, period] | [Quantitative result] | [Why this validates the metric for this simulation] |
| [Study 2]                                 | ...              | ...                   | ...                                                 |

#### Normal Range (from literature)
[Typical values for this metric type in the relevant phenomenon literature. Be specific:
e.g., "Bubble duration in stock markets: 12–24 months (Hong & Stein, 2003); in housing markets:
3–7 years (Glaeser et al., 2008)." Provide the range that would indicate the simulation is
producing realistic-scale output.]

#### Red Flag Threshold
- **Too high** (> [value]): [Diagnosis — which parameter is miscalibrated; direction to adjust]
- **Too low** (< [value]): [Diagnosis — adjustment direction]
- **Zero for all rounds**: [What this symptom indicates; immediate corrective action]

#### Relationship to Other Metrics
[How this metric relates to the others in §2. Does it correlate, diverge, or act as a leading
indicator of another metric? Example: "BAI typically peaks 3–5 rounds before BD crosses threshold;
if both peak simultaneously, the cascade is unusually fast and price_impact may be too high."]

#### Implementation Notes
[Which function in `Rule/analysis.py` computes this; input data source (price_history, agent_states,
trade_history); return type and units.]
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

### 6.1 Expected Stylised Facts

For each stylised fact that this simulation is designed to reproduce, provide the quantitative
target, the literature source, and the verification method.

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
