# Step 1: Research and Theory Foundation

## Purpose

Build the academic and empirical foundation that makes the simulation scientifically credible. Everything in `simulation-bases.md §2` (Theoretical Foundation) and `§6` (Parameter Table) comes from this step.

---

## 1.1 Research Strategy

Conduct systematic research across five dimensions. Each dimension informs a different part of `simulation-bases.md`.

### Dimension 1: Core Economic Theory (→ simulation-bases.md §2)

Search for academic papers establishing the theoretical foundations of the phenomenon.

```
Search terms:
  "[phenomenon] financial theory"
  "[phenomenon] economic model"
  "agent-based model [phenomenon]"
  "[phenomenon] mechanism"

Target:
  2-4 foundational theories, each with a distinct mechanism and a distinct investor type
  At least 1 should have a formal mathematical model
  At least 1 should have direct empirical calibration
```

For each theory found:
- Record the full citation (Author, Year, Journal, Volume, Pages, DOI)
- Extract the core equation(s)
- Note which investor behavior this theory motivates
- Record any parameter estimates (e.g., "adjustment factor α ≈ 0.3")

### Dimension 2: Behavioral Finance (→ simulation-bases.md §4 investor design)

```
Search terms:
  "[phenomenon] behavioral finance"
  "[phenomenon] cognitive bias"
  "[phenomenon] investor psychology"
  "[phenomenon] herding behavior"

Target:
  Psychological profiles for each investor type
  Documented biases and heuristics
  Experimental evidence for behavioral parameters
```

### Dimension 3: Empirical Evidence (→ analysis-bases.md §6 calibration targets)

```
Search terms:
  "[phenomenon] empirical evidence"
  "[phenomenon] stylized facts"
  "[phenomenon] statistical properties"
  "[phenomenon] [asset class] data"

Target:
  Specific quantitative findings: "bubble ratio of 1.4-1.8x", "crash of 20-60%"
  Time series properties: duration, onset speed, recovery speed
  These become calibration targets in analysis-bases.md §6
```

### Dimension 4: Historical Case Studies (→ simulation-bases.md §8)

```
Search terms:
  "[phenomenon] case study"
  "[phenomenon] historical analysis"
  "famous [phenomenon] events"
  "[specific event name] analysis"

Target:
  2-3 events with: exact dates, trigger, price data, participant accounts
  These serve as: calibration anchors, §8 content, and RAG knowledge base content
```

### Dimension 5: Market Microstructure (→ simulation-bases.md §3)

```
Search terms:
  "[phenomenon] market microstructure"
  "price impact model financial markets"
  "market maker [phenomenon]"

Target:
  Price impact parameter λ: Hasbrouck (1991) estimates 0.01-0.05 per unit demand
  Mean reversion speed γ: French & Roll (1986) estimates 0.005-0.02
  These are the primary market parameters in §3.1
```

---

## 1.2 Theory Selection Criteria

Select 2-4 theories that satisfy ALL of the following:

1. **Mechanistic specificity**: The theory explains a specific causal mechanism (not just correlates with the phenomenon)
2. **Implementability**: Can be operationalized as an agent decision rule or LLM prompt
3. **Distinct investor mapping**: Each theory motivates a DIFFERENT investor type — no two investors should share the same primary theory
4. **Empirical support**: At least one empirical study documents the mechanism in real markets
5. **Mathematical grounding**: Has a closed-form or near-closed-form expression, even if approximate

**Anti-patterns to avoid**:
- "Investor sentiment" — too vague; which specific bias?
- Two theories that both reduce to "trend following" — pick the more precise one
- A theory with only anecdotal support — requires at least one published empirical study

---

## 1.3 Parameter Research Protocol

For each parameter in your simulation (λ, γ, σ, thresholds, position sizes):

1. Search the literature for empirical estimates: "price impact coefficient financial markets"
2. Record the range: "λ typically 0.01–0.05 in microstructure models (Hasbrouck, 1991)"
3. Choose a value within the range that: (a) produces the target phenomenon, (b) is closest to the mode of the empirical distribution
4. Document in §6 parameter table: value, range, full citation

**Non-negotiable**: Every numeric parameter in `simulation-bases.md §6` and `players.yml` must have at least one published source citation. "Based on intuition" is not acceptable.

---

## 1.4 Theory Documentation Template

For each theory selected (to be inserted into `simulation-bases.md §2`):

```
Theory: [Full Theory Name]

Citation: [Author(s), Year. "Full Title." *Journal Name*, Volume(Issue), Pages–Pages.
           https://doi.org/...]

Core Insight:
[2-3 precise sentences. Not a summary — the specific mechanism that makes this theory
relevant. What does the theory say CAUSES the phenomenon?]

Mathematical Formulation:
[The central equation. Use standard notation. Define every symbol.
If no formal model, write the verbal model as a constraint or comparison:
"D(t) ∝ [P(t) - MA(t)] / MA(t) — demand proportional to trend deviation from moving average"]

Empirical Evidence:
[Specific quantitative finding from the cited paper or associated empirical work.
Example: "In experiments, mean adjustment factor α ≈ 0.3 (Tversky & Kahneman, 1974, n=1200)."
Example: "Momentum returns average 1.0%/month at 12-month horizon (Jegadeesh & Titman, 1993)."]

Calibration Implication:
[What this theory implies about specific parameter choices.
Example: "α = 0.3 → adjustment_factor in players.yml = 0.3 for AnchoredTrader"]

Investor Mapping:
[Which investor class embodies this theory; what specific behavior it motivates]
```

---

## 1.5 Historical Case Study Documentation Template

For each event (to be inserted into `simulation-bases.md §8`):

```
Event: [Full Event Name]
Date:  [Specific dates or date range]
Market: [Asset class, exchange(s), geographic scope]
Trigger: [The precise catalyst — be specific, not generic]

Key Dynamics Timeline:
  [Date/Period]: [What happened] → [Market effect]
  [Date/Period]: [What happened] → [Market effect]
  [Date/Period]: [Resolution] → [Recovery dynamics]

Quantitative Data:
  Peak-to-trough: [% or absolute]
  Duration (onset to peak): [days/weeks]
  Recovery duration: [days/weeks/months]
  Key participants' losses or gains (if documented): [values with sources]

Agent Mappings:
  [Simulation Agent] → [Real-world participant]: [Justification for mapping]

Simulation Calibration Lessons:
  [Parameter]: should be calibrated to [value] to match [data point from event]
  [Timing]: onset should occur in [round range] based on [real timeline]

Sources:
  [Full citations for the historical data used above]
```

---

## 1.6 Quality Standard for `simulation-bases.md §2`

Before finalizing the Theoretical Foundation section, verify:

- [ ] Every theory has a DOI or full journal citation
- [ ] Every theory has an explicit mathematical formulation
- [ ] Every theory maps to exactly one investor type (no overlap)
- [ ] At least one empirical study is cited per theory with quantitative findings
- [ ] The Calibration Implication connects theory to specific `players.yml` parameter values
- [ ] No theory is described in vague terms — every "Core Insight" could be formalized

**If any of these are missing, the documentation is incomplete regardless of how many theories are cited.**
