---
name: agent-design-skill
purpose: Format-locked, scenario-domain-agnostic handbook for designing a single simulation participant agent at the theory and behaviour layer. Suitable for inclusion in any *bases.md agent taxonomy.
status: canonical
audience: Authors and reviewers of participant-agent specifications, independent of the scenario domain and independent of how the agent will later be realised.
domain_companions: Scenario-domain row labels, value palettes, and worked substitution examples live in sibling `agent-design-<domain>.md` files (e.g. `agent-design-finance.md`). The core handbook stays domain-neutral.
rfc2119: This document uses MUST / MUST NOT / SHOULD / MAY in the RFC-2119 sense.
---

# Simulation Agent Design Handbook

This handbook is the **single source of truth** for designing any
simulation participant agent at the *design layer*. It governs the
intrinsic specification of an agent — its theory, role, information
set, decision mechanism, action space, parameters, and validation
expectations — and is intended to produce a self-contained section
that can be embedded directly into any `*bases.md` agent taxonomy.

The handbook is **scenario-domain agnostic**. Domain-specific row
labels, value palettes, real-world counterpart enumerations, and
worked substitution examples are NOT in this file; they live in
sibling **domain companion files** (`agent-design-<domain>.md`,
e.g. `agent-design-finance.md`). A conformant specification cites
the core handbook AND the relevant companion. Sections, headers,
field schemas, and the validation checklist defined here apply
uniformly to every domain.

The handbook governs **one agent at a time** and covers only what is
*intrinsic to the agent*: theory, role, information set, decision
logic, action choices, self-imposed discipline, parameters, and
validation expectations. A conformant specification MUST NOT include
implementation details (engine code, configuration form, parser
tokens, file paths, class structure, UI), environment rules
(matching engine, tick grid, fee schedule, latency, message-routing
policy, content-moderation rules, regulator-imposed limits), or
peer-network / social topology. The same design MUST be reusable
across any matching mechanism, any message-routing scheme, and any
peer-graph the scenario layer provides.

A specification that conforms to this handbook MUST be:

1. **Theoretically grounded** — every behavioural claim traces back to
   a named theory or empirical study with a citation.
2. **Behaviourally complete** — information set, decision mechanism,
   action space, state evolution, and edge cases are all explicit.
3. **Parameterised** — every tunable knob is named, typed, ranged,
   ranked by sensitivity, tied to a calibration source, and labelled
   with the direction of its effect.
4. **Validation-ready** — expected emergent behaviours and sanity
   bounds are declared so any implementation can be tested against them.
5. **Reproducible by design** — the specification declares its
   determinism semantics so any implementation can honour them.
6. **Auditable** — design provenance, version, and ablation hooks are
   declared, not implicit.

---

## 1. When to Use This Handbook

Apply this handbook whenever you:

- Author a brand-new agent specification.
- Refactor a legacy agent specification into the unified format.
- Extend an existing specification with new theory, signals,
  parameters, or validation expectations.
- Validate that a specification is *theory-complete*,
  *behaviourally-complete*, and *validation-ready*.

If you are only editing prose inside an already-conformant section, you
do not need to re-run the full validation checklist, but section names,
header levels, and table headers MUST remain identical.

---

## 2. Canonical Section Order

A conformant specification MUST contain exactly these top-level
sections, in this order. Every section is **required** unless explicitly
marked *conditional*.

| #  | Section                                | Header | Notes                             |
|----|----------------------------------------|--------|-----------------------------------|
| 1  | Title — agent role description         | `#`    |                                   |
| 2  | Summary                                | `##`   | 7 fixed rows                      |
| 3  | Definition and Goals                   | `##`   | Includes non-goals                |
| 4  | Theoretical Foundation                 | `##`   | ≥1 theory sub-block               |
| 5  | Design Purpose and Activation Triggers | `##`   | Includes deactivation             |
| 6  | Behavioral Framework                   | `##`   | 5 fixed H4 sub-blocks             |
| 7  | Parameters                             | `##`   | 8-column table                    |
| 8  | Population and Heterogeneity           | `##`   |                                   |
| 9  | Worked Numerical Examples              | `##`   | ≥3 cases + 1 edge case            |
| 10 | Validation and Calibration             | `##`   | Includes Ablation Hooks sub-block |
| 11 | Academic References                    | `##`   |                                   |
| 12 | Design Provenance and Versioning       | `##`   | Footer block                      |

Environment rules — matching mechanics, fee / latency models,
message-routing policy, content-moderation rules, and peer-network
topology — are not sections of an agent design. They belong to the
scenario / environment specification.

---

## 3. Section-by-Section Requirements

> **Convention.** The numbered labels (`### 3.x`, `#### 3.x.y`) used
> throughout this section are *internal cross-reference labels for this
> handbook only*. A conformant specification MUST use the **unnumbered**
> headers shown in the copy-paste skeleton in §5 (e.g. `## Summary`,
> `## Behavioral Framework`, `#### Decision Information Set`), and MUST
> preserve the exact header levels the skeleton shows.

### 3.1 Title

- One H1 line, sentence-cased descriptive role phrase.
- MUST NOT be a class identifier or any code-style token.
- MUST describe the agent's *role* in the market, not its
  implementation.

### 3.2 Summary

A seven-row fingerprint table. Field names and order MUST be exactly as
shown. Domain companions MAY relabel `Theory Family` value palette and
`System Role` row label per `agent-design-<domain>.md §3`.

```markdown
## Summary

| Field                 | Content                                                                  |
|-----------------------|--------------------------------------------------------------------------|
| Archetype             | <one-line role phrase, matches the H1>                                   |
| Theory Family         | <see the relevant domain companion for the value palette>                |
| System Role           | **Destabilising** / **Stabilising** / **Context-dependent** — <one-line> |
| Time Horizon          | <short / medium / long>                                                  |
| Risk Tolerance        | <low / medium / high>                                                    |
| Information Asymmetry | <none / partial / full>                                                  |
| Determinism           | <deterministic / stochastic-given-seed / non-deterministic>              |
```

The row label *System Role* refers to the agent's qualitative effect on
the dynamics of the simulated system as a whole. Domain companions MAY
substitute a domain-natural label (e.g. *Market Role*); see the
relevant `agent-design-<domain>.md`.

### 3.3 Definition and Goals

Three short paragraphs (8–14 sentences total) addressing, in order:

1. **What the agent models.** Describe the real-world participant or
   behaviour, and name the real-world counterpart class. Pick the
   counterpart from the relevant domain companion's enumeration
   (e.g. `agent-design-finance.md §4`), or supply a more specific
   counterpart with a citation.
2. **Decision goal.** State the concrete output produced (action
   selection + magnitude + any continuous action parameter such as
   price, opinion target, or message intensity) and the criterion the
   agent optimises or follows.
3. **Role inside the simulation.** Specify which **stylized facts**
   this agent is expected to help produce when active in a population.
   Pick stylized facts from the relevant domain companion's catalogue
   (e.g. `agent-design-finance.md §5`), with a citation. Then state the
   **non-goals** — behaviours this agent MUST NOT exhibit.

### 3.4 Theoretical Foundation

For each underlying theory **or documented mechanism**, supply one
sub-block with the labelled lines below. ≥1 sub-block is required.
"Theory" here is read broadly: it admits academic theories (e.g.
Prospect Theory, Information Cascades, Limits to Arbitrage), documented
behavioural patterns (e.g. anchoring, herding, disposition effect), and
named market mechanisms (e.g. margin spiral, fire-sale externality,
dealer-inventory cycle, run dynamics). Citations MUST include a DOI
when one exists.

```markdown
**<Theory Name>**:
- Theory / Study: <name>
- Citation: <full citation + DOI>
- Core Insight: <2–3 sentences>
- Mathematical Formulation: `<formula>`
- Empirical Evidence: <study, dataset, effect size>
- Relevance to This Agent: <how this agent operationalises the theory>
- Calibration Source: <paper / dataset that fixes parameter values>
- Falsification Conditions: <observable behaviours that would falsify the theory in simulation>
- Alternative Theories: <named competing theories that could be swapped in>
```

### 3.5 Design Purpose and Activation Triggers

Six fields, in this order. *Activation Triggers* answer **when** the
agent acts; *Deactivation Conditions* answer **when it stops**;
*Prerequisite Signals* answer **what must be true before it considers
acting**; *Missing-Signal Policy* answers **what the agent does when a
required input is unavailable**.

```markdown
Purpose: <one sentence — the behaviour this agent produces in the market>

Call Frequency: <every-tick / every-N-ticks / event-driven on signal X>

Prerequisite Signals (must be available for the agent to evaluate):
- <Signal A> available
- <Liquidity / time-of-day / regime indicator>

Missing-Signal Policy: <what the agent does when a prerequisite signal
is unavailable, NaN, or stale: hold / fall back to last value / abstain>

Activation Triggers:
- <Trigger A>: <action>
- <Trigger B>: <action>
- <Default>: <hold / no-op>

Deactivation Conditions:
- <Inventory / wealth threshold breached>
- <Regime flip>: <new behaviour or hibernation>

System Contribution by Regime:
| Regime     | Contribution                | Mechanism  |
|------------|-----------------------------|------------|
| <Regime A> | Stabilising / Destabilising | <one-line> |
| <Regime B> | Stabilising / Destabilising | <one-line> |

(≥2 rows required. The three columns and their order MUST NOT change.
Domain companions supply the regime label palette appropriate to the
scenario — see `agent-design-<domain>.md`. The table label
*System Contribution by Regime* MAY be relabelled in domain
companions — e.g. *Market Contribution by Regime* per
`agent-design-finance.md §6`.)

Interaction with other agents: <one sentence — who it opposes,
amplifies, or overlaps with>
```

### 3.6 Behavioral Framework

Five H4 sub-sections, in order. All MUST be present.

#### 3.6.1 Decision Information Set

A signal table plus an explicit "does NOT use" line. The *Memory
Window* column states how far back the agent looks at each signal.
Signals MAY include observations of peer behaviour (peer-trade flow,
peer-position summary, public sentiment, news/event feed) when the
environment exposes them as readable signals.

```markdown
| Signal        | Type       | Memory Window | Rationale            |
|---------------|------------|---------------|----------------------|
| `price`       | Continuous | 1 tick        | Current market price |
| `fundamental` | Continuous | 1 tick        | True F               |

Does NOT use: <list of conspicuous non-signals, e.g. `prev_price`, `momentum`>.
```

#### 3.6.2 Core Behavioral Mechanism

Numbered 5–10 step description of the agent's decision logic. Plain
English mixed with formulas. MUST NOT be code in any specific
programming language.

#### 3.6.3 Action Space

The set of actions the agent may emit and the **self-imposed
discipline** the agent applies to itself. Environment-imposed limits
(matching engine, tick grid, fee schedule, latency, message-routing
policy, content-moderation rules, regulator-imposed caps) MUST NOT
appear here — they belong to the scenario / environment
specification. Every aspect below MUST be specified.

The eight aspect *dimensions* are canonical and MUST all be visibly
covered. Their *row labels* are the canonical generic labels shown
below. Domain companions (`agent-design-<domain>.md`) MAY supply
domain-natural label substitutes — see, for example,
`agent-design-finance.md §7` for the financial-domain row labels.
Row order MUST be preserved.

```markdown
| Aspect                | Specification                                                            |
|-----------------------|--------------------------------------------------------------------------|
| Action types allowed  | <enumerate every discrete action, including no-op>                       |
| Action parameter rule | <rule for the continuous parameter of an action, e.g. price or target>   |
| Sizing rule           | <formula or rule for action magnitude / quantity>                        |
| Action lifetime       | <duration before the action expires or is auto-cancelled>                |
| Revision policy       | <when and how the agent retracts, replaces, or amends an emitted action> |
| State constraint      | <self-imposed cap on the agent's internal state>                         |
| Resource cap          | <self-imposed cap on cumulative cost, capital, or budget>                |
| Exit rule             | <self-imposed termination trigger, or "none">                            |
```

#### 3.6.4 Mathematical Model

- **Decision variable:** the quantity the agent computes per call (e.g.
  signed trade quantity, target price, target inventory).
- **Trigger function:** pseudo-code describing under what condition the
  agent emits a non-hold action. Pseudo-code MUST NOT be tied to a
  specific language; algebraic notation or English-pseudo is preferred.
- **Sizing function:** pseudo-code mapping signals to quantity.
- **State variables:** every internal variable the agent persists
  across calls, with type and initial value.
- **State-update rule:** when each state variable updates and with what
  formula. MUST be explicit about update *ordering* (pre-decide,
  post-decide, post-fill).
- **Determinism contract:** state whether the decision rule is
  deterministic given identical inputs and state, or whether it draws
  from a named distribution. If stochastic, name the distribution and
  the seed-bearing source.
- **Parameter symbol table:**

```markdown
| Symbol | Meaning   | Default Value | Source     |
|--------|-----------|---------------|------------|
| `α`    | <meaning> | <value>       | <citation> |
```

#### 3.6.5 Behavioral Properties

Four labelled lines:

- Time horizon: short / medium / long, with rationale
- Risk tolerance: low / medium / high, with rationale
- Information asymmetry: none / partial / full
- Psychological profile: cite the biases this agent embodies

### 3.7 Parameters **(MANDATORY)**

A single engine-agnostic table that documents every knob the agent
design exposes. Each row MUST use the canonical **eight columns**
below. Column names and order MUST NOT change.

- **Parameter** — exact key name, back-ticked.
- **Type** — `int` / `float` / `str` / `bool` / `enum<...>` /
  `list<T>` / `distribution<...>`.
- **Default** — concrete default value. No placeholders.
- **Valid Range** — admissible domain (`[0, 1]`, `> 0`, `int ≥ 1`,
  `{buy, sell, hold}`, named enum). Required for tuning safety.
- **Sensitivity** — `high` / `medium` / `low`. Tells the user which
  knobs matter most for emergent behaviour.
- **Description** — one-sentence meaning in plain language.
- **Impact** — direction of effect when the value increases ("Higher →
  …"). MUST state direction, not restate the description.
- **Source** — citation, calibration paper, or `Standardised`.

If the agent design exposes zero tunable parameters, write
`_No tunable parameters._` so the omission is visibly intentional.

```markdown
## Parameters

| Parameter | Type   | Default | Valid Range | Sensitivity  | Description                | Impact                         | Source     |
|-----------|--------|---------|-------------|--------------|----------------------------|--------------------------------|------------|
| `<name>`  | <type> | <value> | <domain>    | high/med/low | <one-sentence description> | Higher → <direction-of-effect> | <citation> |
```

### 3.8 Population and Heterogeneity

How the design is intended to be instantiated as one or many
copies in a market.

```markdown
| Aspect                         | Specification                                          |
|--------------------------------|--------------------------------------------------------|
| Default population size        | <1 / N=<int> / scenario-dependent>                     |
| Parameter heterogeneity policy | <shared point value / iid <distribution> / correlated> |
| Heterogeneity per parameter    | <name → distribution>                                  |
| Cross-agent correlation        | <none / Σ specified / coupling rule>                   |
| Identity persistence           | <identical across episodes / re-drawn every episode>   |
```

### 3.9 Worked Numerical Examples

Provide **at least three** worked cases plus **one edge case**, each as
a fenced block. Each case MUST show:

- The market state (real numbers, not placeholders).
- The intermediate calculation step-by-step.
- The decision (action, quantity, price).
- The state update post-decision (so the reader sees memory evolve).

The three primary cases SHOULD cover distinct trigger branches (e.g.
one buy, one sell, one hold). The edge case MUST cover at least one
of: cold-start (empty state), extreme deviation, deactivation
condition, inventory-cap clamp, regime flip, missing-signal fallback.

```markdown
### Case 1 — <branch name>
Market state: <real numbers>
Calculation:
  <step 1>
  <step 2>
Decision: <action, quantity, price>
State update: <how state changes>

### Case 2 — <branch name>
...

### Case 3 — <branch name>
...

### Edge Case — <name>
...
```

### 3.10 Validation and Calibration

How a researcher will know the design is correct and the calibration
is sound.

```markdown
**Calibration data sources** (per parameter, where applicable):
- `<param>` ← <citation, table, value>

**Expected stylized facts** when this agent dominates the population:
- <emergent property 1, e.g. mispricing half-life > 50 ticks>
- <emergent property 2, e.g. excess kurtosis > 3>
- <emergent property 3>

**Sanity bounds (red flags during simulation)**:
- <red flag 1 — what behaviour would indicate broken implementation>
- <red flag 2>
- <red flag 3>
```

#### 3.10.1 Ablation Hooks

Named knob settings that produce meaningful ablations. Each row MUST
state the hypothesis the ablation tests.

```markdown
| Ablation name | Setting     | Hypothesis tested |
|---------------|-------------|-------------------|
| `<name>`      | `<setting>` | <hypothesis>      |
```

### 3.11 Academic References

Numbered table. Every paper cited anywhere in the specification MUST
appear here.

```markdown
| # | Citation              | Notes       |
|---|-----------------------|-------------|
| 1 | <full citation + DOI> | <relevance> |
```

### 3.12 Design Provenance and Versioning

Footer block. Required.

```markdown
| Field       | Content                                         |
|-------------|-------------------------------------------------|
| Author      | <name or handle>                                |
| Reviewed by | <name or handle> (optional)                     |
| Created     | <YYYY-MM-DD>                                    |
| Version     | <semver, e.g. 1.0.0>                            |
| Change log  | one line per version (latest first)             |
| Status      | <draft / experimental / canonical / deprecated> |
```

---

## 4. Validation Checklist (Self-Check)

An author SHOULD run through this list and ensure every item is
checked before declaring the specification complete. Each unchecked
item is a blocker.

- [ ] H1 is a sentence-cased role phrase, not a class or code identifier
- [ ] §3.2 Summary has exactly the 7 canonical rows in order
- [ ] §3.3 Definition and Goals covers (a) what the agent models with a
      named real-world counterpart, (b) decision goal, (c) role +
      stylized facts produced, (d) explicit non-goals
- [ ] §3.4 Theoretical Foundation has ≥1 sub-block including Calibration
      Source, Falsification Conditions, Alternative Theories
- [ ] §3.5 declares Call Frequency, Prerequisite Signals,
      Missing-Signal Policy, Activation Triggers (with `<Default>`),
      Deactivation Conditions, regime table, and Interaction sentence
- [ ] §3.6 has all five H4 sub-blocks (Information Set, Mechanism,
      Action Space, Mathematical Model with State-Update Rule and
      Determinism Contract, Behavioral Properties)
- [ ] §3.6.3 Action Space describes only self-imposed discipline; no
      environment rules (matching engine, tick grid, fees, latency,
      message-routing policy, content-moderation rules,
      regulator-imposed caps) appear anywhere in the specification
- [ ] §3.6.3 Action Space visibly covers all eight canonical
      dimensions (Action types, Action parameter, Sizing, Lifetime,
      Revision, State constraint, Resource cap, Exit), under either
      the canonical labels or domain-natural substitutes
- [ ] No section names or describes a peer-network topology, social
      graph, or information-propagation rule (those belong to the
      scenario, not the agent)
- [ ] §3.7 Parameters table uses the canonical 8 columns: Parameter,
      Type, Default, Valid Range, Sensitivity, Description, Impact,
      Source — no missing, renamed, or reordered columns; or
      `_No tunable parameters._`
- [ ] Every Impact cell states direction of effect ("Higher → ...")
- [ ] Every Default in §3.7 has a justification trace via Source or
      §3.4 Calibration Source
- [ ] §3.8 declares default population size, heterogeneity policy, and
      cross-agent correlation
- [ ] §3.9 has ≥3 primary cases covering distinct trigger branches +
      ≥1 edge case; each case shows state evolution
- [ ] §3.10 declares calibration sources, expected stylized facts, and
      sanity bounds; §3.10.1 declares ≥1 ablation hook with hypothesis
- [ ] §3.11 lists every citation referenced anywhere in the spec
- [ ] §3.12 footer includes Author, Created, Version, Status

---

## 5. Copy-Paste Skeleton

Use this as the starting point for a new agent specification. Replace
every `<...>` and delete bracketed instructions when done. Do not add
or remove sections.

```markdown
# <Sentence-cased agent role description>

## Summary

| Field                 | Content                                                                  |
|-----------------------|--------------------------------------------------------------------------|
| Archetype             | <archetype description, same as H1>                                      |
| Theory Family         | <see the relevant domain companion for the value palette>                |
| System Role           | **Destabilising** / **Stabilising** / **Context-dependent** — <one-line> |
| Time Horizon          | <short / medium / long>                                                  |
| Risk Tolerance        | <low / medium / high>                                                    |
| Information Asymmetry | <none / partial / full>                                                  |
| Determinism           | <deterministic / stochastic-given-seed / non-deterministic>              |

## Definition and Goals

<Paragraph 1 — what the agent models, with a named real-world counterpart.>

<Paragraph 2 — decision goal: action, sizing, price level, criterion.>

<Paragraph 3 — role inside the simulation, named stylized facts produced,
explicit non-goals.>

## Theoretical Foundation

**<Theory Name>**:
- Theory / Study: <name>
- Citation: <full citation + DOI>
- Core Insight: <2–3 sentences>
- Mathematical Formulation: `<formula>`
- Empirical Evidence: <study + effect size>
- Relevance to This Agent: <how this agent operationalises it>
- Calibration Source: <paper / dataset>
- Falsification Conditions: <observable behaviours that would falsify>
- Alternative Theories: <named competing theories>

## Design Purpose and Activation Triggers

Purpose: <one sentence>

Call Frequency: <every-tick / every-N-ticks / event-driven>

Prerequisite Signals:
- <signal A> available
- <regime / liquidity indicator>

Missing-Signal Policy: <hold / fall back / abstain>

Activation Triggers:
- <Trigger A>: <action>
- <Trigger B>: <action>
- <Default>: <hold>

Deactivation Conditions:
- <condition> → <hibernate / exit>

System Contribution by Regime:
| Regime     | Contribution                | Mechanism  |
|------------|-----------------------------|------------|
| <Regime A> | Stabilising / Destabilising | <one-line> |
| <Regime B> | Stabilising / Destabilising | <one-line> |

Interaction with other agents: <one sentence>

## Behavioral Framework

#### Decision Information Set

| Signal   | Type                        | Memory Window | Rationale         |
|----------|-----------------------------|---------------|-------------------|
| `<name>` | <Continuous/Discrete/State> | <ticks>       | <why this signal> |

Does NOT use: <list>.

#### Core Behavioral Mechanism

1. <step>
2. <step>
3. <step>

#### Action Space

| Aspect                | Specification                                         |
|-----------------------|-------------------------------------------------------|
| Action types allowed  | <enumerate every discrete action, including no-op>    |
| Action parameter rule | <rule for the continuous parameter of an action>      |
| Sizing rule           | <formula or rule for action magnitude / quantity>     |
| Action lifetime       | <duration before the action expires>                  |
| Revision policy       | <when and how the agent retracts or amends an action> |
| State constraint      | <self-imposed cap on the agent's internal state>      |
| Resource cap          | <self-imposed budget / capital / leverage cap>        |
| Exit rule             | <self-imposed termination trigger, or "none">         |

#### Mathematical Model

- Decision variable: <Q*(t) or target price etc.>
- Trigger function:
  ```
  <pseudo-code>
  ```
- Sizing function:
  ```
  <pseudo-code>
  ```
- State variables: <list with type and initial value, or "none">
- State-update rule: <when each variable updates and with what formula;
  pre-decide / post-decide / post-fill ordering>
- Determinism contract: <deterministic / stochastic with named distribution>

| Symbol | Meaning   | Default Value | Source     |
|--------|-----------|---------------|------------|
| `<s>`  | <meaning> | <value>       | <citation> |

#### Behavioral Properties

- Time horizon: <short / medium / long> — <rationale>
- Risk tolerance: <low / medium / high> — <rationale>
- Information asymmetry: <none / partial / full>
- Psychological profile: <biases embodied>

## Parameters

| Parameter | Type   | Default | Valid Range | Sensitivity     | Description   | Impact               | Source     |
|-----------|--------|---------|-------------|-----------------|---------------|----------------------|------------|
| `<name>`  | <type> | <value> | <domain>    | high/medium/low | <description> | Higher → <direction> | <citation> |

## Population and Heterogeneity

| Aspect                         | Specification                                  |
|--------------------------------|------------------------------------------------|
| Default population size        | <1 / N / scenario-dependent>                   |
| Parameter heterogeneity policy | <shared point / iid distribution / correlated> |
| Heterogeneity per parameter    | <name → distribution>                          |
| Cross-agent correlation        | <none / Σ / coupling rule>                     |
| Identity persistence           | <identical / re-drawn>                         |

## Worked Numerical Examples

### Case 1 — <branch name>
Market state:  <state>
Calculation:
  <step 1>
  <step 2>
Decision: <action, quantity, price>
State update: <how state changes>

### Case 2 — <branch name>
...

### Case 3 — <branch name>
...

### Edge Case — <name>
...

## Validation and Calibration

**Calibration data sources**:
- `<param>` ← <citation, table, value>

**Expected stylized facts**:
- <emergent property 1>
- <emergent property 2>

**Sanity bounds**:
- <red flag 1>
- <red flag 2>

#### Ablation Hooks

| Ablation name | Setting     | Hypothesis tested |
|---------------|-------------|-------------------|
| `<name>`      | `<setting>` | <hypothesis>      |

## Academic References

| # | Citation              | Notes       |
|---|-----------------------|-------------|
| 1 | <full citation + DOI> | <relevance> |

## Design Provenance and Versioning

| Field       | Content                                         |
|-------------|-------------------------------------------------|
| Author      | <name or handle>                                |
| Reviewed by | <name or handle>                                |
| Created     | <YYYY-MM-DD>                                    |
| Version     | <semver, e.g. 1.0.0>                            |
| Change log  | <latest first>                                  |
| Status      | <draft / experimental / canonical / deprecated> |
```
