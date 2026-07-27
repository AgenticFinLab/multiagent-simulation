# Step 1: Research and Theory Foundation

## Purpose

Build the academic and empirical foundation that makes the simulation scientifically credible. Everything in `simulation-bases.md §2` (Theoretical Foundation) and `§6` (Parameter Table) comes from this step.

---

## Contract (Inputs / Outputs / Polish Hooks)

This block is the **stable I/O declaration** for Step 1. Both
`masim/skills/create-simulation-pipeline.md` and
`masim/skills/polish-simulation-pipeline.md` anchor to it. Downstream
skills MUST NOT redefine these fields.

**Inputs (consumed).** Target file
`examples/{ScenarioName}/{domain}-{scenario}.md`, specifically:

| Target section | Used to seed                                                     |
|----------------|------------------------------------------------------------------|
| §4 Theoretical Anchors | Dimension 1 & 2 expansion (theory equations, calibrations) |
| §5 Stylized Facts      | Dimension 3 expansion (empirical evidence, ranges)         |
| §6 Historical Anchors  | Dimension 4 expansion (case timelines, participant accounts) |
| §9 Parameter Seeds     | Dimension 3 & 5 expansion (parameter calibration papers)   |

**Outputs (produced or extended).**

| Artefact                                             | Extent of write                              |
|------------------------------------------------------|----------------------------------------------|
| `examples/{ScenarioName}/simulation-bases.md §1`     | Phenomenon Definition + §1.1.1 / §1.1.2 / §1.1.3 populated from target §2 + §6 + literature verification |
| `examples/{ScenarioName}/simulation-bases.md §2`     | Theoretical Foundation — one Theory block per target §4.{k}, each with Citation / Core Insight / Mathematical Formulation / Empirical Evidence / Relevance / Calibration Implication |
| `examples/{ScenarioName}/simulation-bases.md §6`     | Parameter Table — every target §9 row expanded with verified source |
| `examples/{ScenarioName}/analysis-bases.md §1`       | Analysis Objectives — hypothesis rows tied back to target §3 Research Goals |
| `examples/{ScenarioName}/simulation-build-log.md §B` | Research Notes B.1 — B.5 (theory / stylized fact / event / taxonomy / parameter expansions) |
| `simulation-build-log.md §C`                         | Any newly surfaced gap raised to the author |

**Polish Hooks (what a polish audit re-verifies against this step).**
When `polish-simulation-pipeline.md` audits Step 1, it MUST re-run
these three checks — no new research is added:

1. Every DOI / URL in `simulation-bases.md §1` and §2 still resolves.
2. Every Theory block under `simulation-bases.md §2` has all six sub-fields
   (Citation, Core Insight, Mathematical Formulation, Empirical Evidence,
   Relevance to This Simulation, Calibration Implication).
3. Every target §4.{k} anchor has a matching Theory block; every target §5
   fact traces to a row in `simulation-bases.md §1.1.2` or a literature footnote.

---

## 1.0 Prerequisite and Seed

Step 1 does **not** start from a blank page. It starts from the
scenario target file
`examples/{ScenarioName}/{domain}-{scenario}.md` (produced upstream by
invoking `masim/skills/define-simulation-scenario-skill.md`),
which by §11 validation already contains:

- **§4 Theoretical Anchors** — 3 — 6 theories with DOI citations.
- **§5 Stylized Facts** — 3 — 6 empirical regularities with
  quantitative ranges and acceptance metrics.
- **§6 Historical / Empirical Anchors** — 1 — 3 events with arcs.
- **§9 Parameter Seeds** — every numeric knob with empirical ranges.

Step 1 has three jobs **against** the target file:

1. **Verify.** Resolve every DOI / URL; confirm the quoted ranges
   appear in the cited works. Any failure → raise an
   `AskUserQuestion` defect; the target file is unlocked, corrected,
   re-locked, then research resumes.
2. **Expand.** For every verified anchor, add the deeper material
   that this step requires (key equations, parameter calibrations,
   mechanism diagrams, additional references) into
   `examples/{ScenarioName}/simulation-build-log.md §B`.
3. **Surface gaps.** If verification reveals a material gap (e.g.,
   a stylized fact whose source does not actually report a numeric
   range), record the gap in `simulation-build-log.md §C` and raise
   it to the author.

The five research dimensions below (§1.1 — §1.5) describe the
*depth* of the expansion under each target anchor; they are not a
fresh exploration from scratch.

---

## 1.1 Research Strategy

Conduct systematic research across five dimensions. Each dimension informs a different part of `simulation-bases.md`.

### Dimension 1: Core Domain Theory (→ simulation-bases.md §2)

Search for academic papers establishing the theoretical foundations of the phenomenon in the
scenario's domain (finance / opinion dynamics / epidemics / sociology / etc.).

```
Search terms (adapt to domain):
  "[phenomenon] theory"
  "[phenomenon] formal model"
  "agent-based model [phenomenon]"
  "[phenomenon] mechanism"
  finance instantiation: "[phenomenon] financial theory", "[phenomenon] economic model"
  opinion instantiation: "[phenomenon] social influence model", "opinion dynamics [phenomenon]"

Target:
  2-4 foundational theories, each with a distinct mechanism and a distinct agent type
  At least 1 should have a formal mathematical model
  At least 1 should have direct empirical calibration
```

For each theory found:
- Record the full citation (Author, Year, Journal, Volume, Pages, DOI)
- Extract the core equation(s)
- Note which agent behavior this theory motivates (finance appendix: investor behavior)
- Record any parameter estimates (e.g., "adjustment factor α ≈ 0.3")

### Dimension 2: Behavioral Foundations (→ simulation-bases.md §4 agent design)

Depending on the scenario domain, "Behavioral Foundations" spans behavioral finance, social
psychology, epidemiological behavior, adoption theory, or the analogous body of work.

```
Search terms (adapt to domain):
  "[phenomenon] behavioral finance" (finance)
  "[phenomenon] social psychology" / "cognitive bias" (opinion)
  "[phenomenon] health behavior" (epidemics)
  "[phenomenon] diffusion of innovations" (sociology)
  "[phenomenon] herding behavior" (any)

Target:
  Psychological / behavioral profiles for each agent type
  Documented biases and heuristics
  Experimental evidence for behavioral parameters
```

### Dimension 3: Empirical Evidence (→ analysis-bases.md §6 calibration targets)

```
Search terms:
  "[phenomenon] empirical evidence"
  "[phenomenon] stylized facts"
  "[phenomenon] statistical properties"
  "[phenomenon] [asset class / population / cohort] data"

Target:
  Specific quantitative findings — finance example: "bubble ratio of 1.4-1.8x, crash of 20-60%";
  opinion example: "consensus fraction 0.6-0.8 within 500 iterations for N=100";
  epidemics example: "R₀ 2.3-2.6 for SARS-CoV-2, doubling time 3-5 days".
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
  2-3 events with: exact dates, trigger, primary observable data (finance: price data;
  opinion: opinion-shift data; epidemics: incidence data), participant accounts
  These serve as: calibration anchors, §8 content, and RAG knowledge base content
```

### Dimension 5: Environment Microstructure / Interaction Mechanics (→ simulation-bases.md §3)

```
Search terms (adapt to domain):
  "[phenomenon] microstructure" / "interaction rules" / "coupling mechanism"
  finance instantiation: "price impact model financial markets", "market maker [phenomenon]"
  opinion instantiation: "bounded confidence [phenomenon]", "communication topology"
  epidemics instantiation: "contact network [phenomenon]", "transmission model"

Target (finance instantiation shown; substitute analogous parameters for other domains):
  Price impact parameter λ: Hasbrouck (1991) estimates 0.01-0.05 per unit demand
  Mean reversion speed γ: French & Roll (1986) estimates 0.005-0.02
  These are the primary environment parameters in §3.1
```

---

## 1.2 Theory Selection Criteria

Select 2-4 theories that satisfy ALL of the following:

1. **Mechanistic specificity**: The theory explains a specific causal mechanism (not just correlates with the phenomenon)
2. **Implementability**: Can be operationalized as an agent decision rule or LLM prompt
3. **Distinct agent mapping**: Each theory motivates a DIFFERENT agent type — no two agents should share the same primary theory (finance appendix: "investor type")
4. **Empirical support**: At least one empirical study documents the mechanism in the target-domain literature (finance: real markets; opinion: field surveys / lab experiments; epidemics: contact-tracing datasets; sociology: adoption panels)
5. **Mathematical grounding**: Has a closed-form or near-closed-form expression, even if approximate

**Anti-patterns to avoid**:
- "Agent sentiment" — too vague; which specific bias?
- Two theories that both reduce to "trend following" (finance) / "conformity" (opinion) / "peer contagion" (epidemics) — pick the more precise one
- A theory with only anecdotal support — requires at least one published empirical study

---

## 1.3 Parameter Research Protocol

For each parameter in your simulation (state-dynamics coefficients, thresholds, action-scale limits — finance instantiation: λ, γ, σ, position sizes):

1. Search the literature for empirical estimates: "primary state-dynamics coefficient in [domain] literature" (finance instantiation: "price impact coefficient financial markets")
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

Agent Mapping (finance appendix: Investor Mapping):
[Which agent class embodies this theory; what specific behavior it motivates]
```

---

## 1.5 Historical Case Study Documentation Template

For each event (to be inserted into `simulation-bases.md §8`):

```
Event: [Full Event Name]
Date:  [Specific dates or date range]
Setting / Domain Context: [Finance: asset class, exchange(s), geographic scope. Opinion: platform / community / population, geographic scope. Epidemics: population, time window, geography. Sociology: cohort, community, jurisdiction.]
Trigger: [The precise catalyst — be specific, not generic]

Key Dynamics Timeline:
  [Date/Period]: [What happened] → [Environment effect]
  [Date/Period]: [What happened] → [Environment effect]
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
- [ ] Every theory maps to exactly one agent type (no overlap; finance appendix: investor type)
- [ ] At least one empirical study is cited per theory with quantitative findings
- [ ] The Calibration Implication connects theory to specific `players.yml` parameter values
- [ ] No theory is described in vague terms — every "Core Insight" could be formalized

**If any of these are missing, the documentation is incomplete regardless of how many theories are cited.**
