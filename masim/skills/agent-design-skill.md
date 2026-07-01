---
name: agent-design-skill
purpose: Format-locked, unified handbook for designing a single simulation participant agent at the theory and behaviour layer. Produces self-contained specifications suitable for inclusion in any *bases.md agent taxonomy, across any simulation domain.
status: canonical
audience: Authors and reviewers of participant-agent specifications for multi-agent simulations in any domain (financial markets, social systems, opinion dynamics, organisational behaviour, etc.).
rfc2119: This document uses MUST / MUST NOT / SHOULD / MAY in the RFC-2119 sense.
---

# Simulation Agent Design Handbook

This handbook is the **single source of truth** for designing any
simulation participant agent at the *design layer*. It governs the
intrinsic specification of an agent — its theory, role, information
set, decision mechanism, action space, parameters, and validation
expectations — and is intended to produce a self-contained section
that can be embedded directly into any `*bases.md` agent taxonomy.

The handbook is **completely domain-agnostic**. It defines the
structure, depth, quality rules, and validation requirements that
every agent specification MUST follow — regardless of which simulation
domain the agent belongs to (financial markets, social systems, opinion
dynamics, epidemiology, urban traffic, ecology, or any other). No
domain-specific content (counterpart lists, theory palettes, regime
names) is hardcoded in this handbook.

When designing an agent, the authoring agent (LLM) MUST autonomously
generate all domain-appropriate content (Theory Family palette,
real-world counterpart enumeration, regime palette, Action Space
row-label substitutions if helpful) inline within the specification
itself, following the format and depth requirements specified in each
section below. This ensures the handbook scales to any domain without
modification.

A conformant specification cites this handbook and states its domain.
Sections, headers, field schemas, and the validation checklist defined
here apply uniformly to every domain.

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

1. **Evidence-grounded** — every substantive design choice (signal
   selection, mechanism logic, action constraints, mathematical
   framework, parameter values, activation conditions) MUST declare
   its evidence source. No design choice may exist without provenance.
2. **Behaviourally complete** — information set, decision mechanism,
   action space, state evolution, and edge cases are all explicit.
3. **Parameterised** — every tunable knob is named, typed, ranged,
   ranked by sensitivity, tied to a calibration source, and labelled
   with the direction of its effect.
4. **Behaviourally verifiable** — the specification declares concrete
   behavioural expectations for this individual agent (given specific
   inputs, what outputs and state changes must occur) so any
   implementation can be unit-tested against the design.
5. **Reproducible by design** — the specification declares its
   determinism semantics so any implementation can honour them.
6. **Auditable** — design provenance, version, and ablation hooks are
   declared, not implicit.
7. **Scenario-portable** — the design MUST NOT reference specific
   scenario names, absolute numeric levels, or fixed round counts; all
   numeric thresholds MUST be parameterised; decision logic MUST
   function given only the declared signals.
8. **I/O-contractual** — the specification MUST declare an explicit
   §3.6.0 I/O Contract (inputs, outputs, content constraints, and
   canonical serialization format) that binds **every implementation
   variant the target declares** in its §10.1 Variant Build Matrix
   (the variant scheme is scenario-defined and MAY be any subset,
   superset, or renaming of the illustrative Rule / LLM / RuleLLM /
   RAG default — the contract MUST hold regardless of which scheme
   is chosen). Implementers MUST re-open the contract on every
   coding pass; on conflict with prose elsewhere in the spec, the
   contract wins.

---

## 1. When to Use This Handbook

Apply this handbook whenever you:

- Author a brand-new agent specification.
- Refactor a legacy agent specification into the unified format.
- Extend an existing specification with new theory, signals,
  parameters, or validation expectations.
- Validate that a specification is *theory-complete*,
  *behaviourally-complete*, and *behaviourally-verifiable*.

If you are only editing prose inside an already-conformant section, you
do not need to re-run the full validation checklist, but section names,
header levels, and table headers MUST remain identical.

---

## 2. Canonical Section Order

A conformant specification MUST contain at least these top-level
sections, in this order. Additional sections MAY be appended after §11
if deeper coverage is warranted. Every section listed here is
**required** unless explicitly marked *conditional*.

| #  | Section                                 | Header | Notes                                 |
|----|-----------------------------------------|--------|---------------------------------------|
| 1  | Title — agent role description          | `#`    |                                       |
| 2  | Summary                                 | `##`   | >=7 rows (minimum set below)          |
| 3  | Definition and Goals                    | `##`   | Includes non-goals                    |
| 4  | Theoretical Foundation                  | `##`   | >=1 theory sub-block                  |
| 5  | Design Purpose and Activation Triggers  | `##`   | Includes deactivation                 |
| 6  | Behavioral Framework                    | `##`   | >=6 H4 sub-blocks (I/O Contract + minimum set below) |
| 7  | Parameters                              | `##`   | >=8-column table                      |
| 8  | Worked Numerical Examples               | `##`   | >=3 cases + 1 edge case               |
| 9  | Behavioral Verification and Calibration | `##`   | Includes Ablation Hooks sub-block     |
| 10 | Academic References                     | `##`   |                                       |
| 11 | Design Provenance and Versioning        | `##`   | Footer block                          |

Environment rules — matching mechanics, fee / latency models,
message-routing policy, content-moderation rules, and peer-network
topology — are not sections of an agent design. They belong to the
scenario / environment specification.

---

## 3. Section-by-Section Requirements

> **Convention.** The numbered labels (`### 3.x`, `#### 3.x.y`) used
> throughout this section are *internal cross-reference labels for this
> handbook only*. A conformant specification MUST use the **unnumbered**
> headers shown in §3 Section-by-Section Requirements (e.g. `## Summary`,
> `## Behavioral Framework`, `#### Decision Information Set`), and MUST
> preserve the exact header levels specified there.

### 3.1 Title

- One H1 line, sentence-cased descriptive role phrase.
- MUST NOT be a class identifier or any code-style token.
- MUST describe the agent's *role* in the simulated system, not its
  implementation.

### 3.2 Summary

A fingerprint table with at least the following seven rows. Field
names and order for these minimum rows MUST be as shown. Additional
rows MAY be appended to capture domain-specific dimensions that
deepen the agent's characterisation.

```markdown
## Summary

| Field                 | Content                                                              |
|-----------------------|----------------------------------------------------------------------|
| Archetype             | <one-line role phrase, matches the H1>                               |
| Theory Family         | <from a domain-appropriate palette of 4–8 theory families>           |
| Behavioral Tendency   | **Diverging** / **Converging** / **Adaptive** — <one-line rationale> |
| Time Horizon          | <short / medium / long>                                              |
| Risk Tolerance        | <low / medium / high>                                                |
| Information Asymmetry | <none / partial / full>                                              |
| Determinism           | <deterministic / stochastic-given-seed / non-deterministic>          |
```

The row label *Behavioral Tendency* classifies the agent's inherent
behavioural direction — whether its decision logic tends to push its
target variable AWAY from a reference equilibrium (Diverging), TOWARD
a reference equilibrium (Converging), or switches direction based on
conditions (Adaptive). The "reference equilibrium" is
domain-determined (e.g. fundamental value in finance, consensus in
opinion dynamics, carrying capacity in ecology). This is an intrinsic
classification of the agent's nature, NOT a judgment about its effect
on any system.

The *Theory Family* value MUST be drawn from a coherent palette of
4–8 theory families appropriate to the agent's domain. The authoring
agent generates this palette based on the scenario domain.

### 3.3 Definition and Goals

Three short paragraphs (8–14 sentences total) addressing, in order:

1. **What the agent models.** Describe the real-world participant or
   behaviour, and name the real-world counterpart class. The
   counterpart MUST be drawn from a domain-appropriate enumeration of
   >=6 participant types (generated by the authoring agent for the
   target domain). If no enumeration entry fits, supply a more
   specific counterpart with a citation.
2. **Decision goal.** State the concrete output produced (action
   selection + magnitude + any continuous action parameter such as
   price, opinion target, or message intensity) and the criterion the
   agent optimises or follows.
3. **Behavioural role inside the simulation.** Describe what this
   agent *does* as an individual participant — its characteristic
   actions, decision patterns, and how it responds to different
   conditions. Then state the **non-goals** — behaviours this agent
   MUST NOT exhibit (>=2 explicit non-goals required).

### 3.4 Theoretical Foundation

For each underlying theory **or documented mechanism**, supply one
sub-block with the labelled lines below. >=1 sub-block is required.
"Theory" here is read broadly: it admits academic theories (e.g.
Prospect Theory, Information Cascades, Social Identity Theory, Bounded
Rationality), documented behavioural patterns (e.g. anchoring, herding,
conformity bias, disposition effect), and named mechanisms (e.g.
fire-sale externality, opinion polarisation, threshold-based contagion,
resource depletion spiral, run dynamics).

**Depth rules:**
- Agents embodying >=2 distinct mechanisms MUST have >=2 theory blocks.
- "Core Insight" MUST explain the mechanism in 2–3 sentences — not
  merely name it.
- "Mathematical Formulation" MUST be a single implementable equation
  or inequality that maps inputs to an output relevant to the agent's
  decision. Placeholders like "complex model" are forbidden.
- "Empirical Evidence" MUST cite at least one dataset with a reported
  effect size, confidence interval, or statistical significance level.
- "Calibration Source" MUST provide a specific numeric range or table
  reference from which parameter defaults can be drawn. A bare paper
  title without a value is insufficient.
- "Falsification Conditions" MUST be stated as observable behaviours
  of THIS individual agent with quantitative thresholds (e.g. "if this
  agent does not reverse its position within 20 ticks of a signal
  crossing the threshold, the theory is falsified").
- Citations MUST include a DOI when one exists.

```markdown
**<Theory Name>**:
- Theory / Study: <name>
- Citation: <full citation + DOI>
- Core Insight: <2–3 sentences explaining the mechanism>
- Mathematical Formulation: `<implementable formula>`
- Empirical Evidence: <study, dataset, effect size>
- Relevance to This Agent: <how this agent operationalises the theory>
- Calibration Source: <paper / dataset + specific numeric range>
- Falsification Conditions: <observable individual-agent behaviour + threshold>
- Alternative Theories: <named competing theories that could be swapped in>
```

### 3.5 Design Purpose and Activation Triggers

Eight fields, in this order. *Activation Triggers* answer **when** the
agent acts; *Deactivation Conditions* answer **when it stops**;
*Prerequisite Signals* answer **what must be true before it considers
acting**; *Missing-Signal Policy* answers **what the agent does when a
required input is unavailable**; *Behavioral Adaptation by Condition*
declares how the agent's own behaviour changes under varying external
conditions; *Environmental Dependencies* declares what inputs this
agent requires from its operating environment.

```markdown
Purpose: <one sentence — what behaviour this agent exhibits>

Call Frequency: <every-tick / every-N-ticks / event-driven on signal X>

Prerequisite Signals (must be available for the agent to evaluate):
- <Signal A> available
- <Regime / context indicator>

Missing-Signal Policy: <what the agent does when a prerequisite signal
is unavailable, NaN, or stale: hold / fall back to last value / abstain>

Activation Triggers:
- <Trigger A>: <action>
- <Trigger B>: <action>
- <Default>: <hold / no-op>

Deactivation Conditions:
- <State / resource threshold breached>
- <Regime flip>: <new behaviour or hibernation>

Behavioral Adaptation by Condition:
| Condition     | Behavioral change                    | Mechanism  |
|---------------|--------------------------------------|------------|
| <Condition A> | <how this agent's behaviour changes> | <one-line> |
| <Condition B> | <how this agent's behaviour changes> | <one-line> |

(>=2 rows required. The three columns and their order MUST NOT change.
The condition labels MUST be domain-appropriate — the authoring agent
generates a palette of >=2 external conditions relevant to the target
scenario. This table describes how the agent's OWN behaviour adapts,
not what it "contributes" to any system.)

Environmental Dependencies: <what external signals or agent-generated
inputs this agent requires to function — e.g. "requires a real-time
data feed", "requires observable peer-action summaries". If none beyond
the declared signal table, state "none beyond §3.6.1 signals.">
```


### 3.6 Behavioral Framework

Six H4 sub-sections are the required minimum, in this order. All
six MUST be present. Additional H4 sub-sections MAY be appended
after §3.6.5 to deepen the behavioural specification (e.g. learning
dynamics, memory management, social signalling strategy).

**Ordering rationale.** The I/O Contract (§3.6.0) is placed FIRST
because every downstream implementation — regardless of which
variant scheme the target declares in its §10.1 Variant Build
Matrix (Rule / LLM / RuleLLM / RAG is the finance-default
illustration; other domains MAY declare any subset, superset, or
renaming) and regardless of which engine or prompt template
ultimately executes it — MUST honour the same input surface, the
same output object, and the same serialization format. Placing the
contract before the decision mechanism guarantees that implementers
see the binding interface the moment they open the specification.

#### 3.6.0 I/O Contract **(MANDATORY, contract-strength)**

This sub-section is the **binding interface between design and
implementation**. Every implementation variant declared for this
agent in the target's §10.1 Variant Build Matrix — whatever the
scheme (the finance-default `Rule / LLM / RuleLLM / RAG` is one
example; other domains MAY declare any subset, superset, or
renaming, and future variants MAY be added) — MUST conform to the
inputs, outputs, content constraints, and serialization format
declared here. On conflict with prose elsewhere in this
specification, this section wins.

**Reading convention.** When any rule below (or any rule in a
sibling skill document) enumerates literal variant names, project
them onto the *capability-class* categories used by this handbook.
The implement layer pins a fixed canonical set of variant labels
— currently `Rule`, `LLM`, `RuleLLM`, `Rag` — declared and versioned
in `masim/skills/implement-simulation-skill/01-mandatory-structure.md
§ Canonical Variant Set`; that section is the authoritative mapping
from those four labels to their capability classes. The stable
capability categories are: **rule-driven**, **model-driven**,
**hybrid (rule + model)**, **retrieval-augmented**, and any future
class introduced through the explicit upgrade procedure documented
in that section. All contract obligations in this handbook attach
to the *class*, so that the same design-level rule automatically
covers every literal label that maps onto that class.

The I/O Contract has five required blocks: **Inputs**, **Outputs**,
**Content Constraints**, **Serialization Format**, and **Implementer
Contract Reminder**. All five MUST be filled. "N/A" is not
permitted — if a block does not apply, the author MUST justify why
in one sentence.

```markdown
##### Inputs (per decision call)

| Input                   | Source                  | Type / Shape             | Required? | Notes                                       |
|-------------------------|-------------------------|--------------------------|-----------|---------------------------------------------|
| `<signal_name>`         | environment / peer feed | `float` / `int` / `enum` | yes / no  | maps to a row in §3.6.1                     |
| `<state_variable>`      | agent's own persisted state | as declared in §3.6.4 | yes       | populated on first call by §3.6.4 init      |
| `<context_metadata>`    | scheduler / round header | e.g. `round: int`, `identity: str` | yes | round number, agent identity, seed if any |
| `<retrieved_knowledge>` | retrieval store (retrieval-augmented variants only) | `list[str]` | retrieval variants only | required only for any variant that performs external retrieval (the finance-default `Rag` is one such variant, but any target-declared retrieval variant qualifies); falls back to a declared sentinel if empty |

Every row MUST appear either in §3.6.1 Decision Information Set
(signals) or in §3.6.4 Mathematical Model (state variables). No
input in this table may be undeclared elsewhere.

##### Outputs (per decision call)

The agent MUST emit exactly one **decision object** per call. The
object's schema (all required fields, their types, their valid
ranges, and their units) is declared here and MUST be honoured by
every implementation variant.

| Field           | Type    | Valid Range / Enum                                         | Unit     | Required? | Meaning                                                        |
|-----------------|---------|------------------------------------------------------------|----------|-----------|----------------------------------------------------------------|
| `action`        | enum    | `{"<action_A>", "<action_B>", "hold"}` (from §3.6.3)       | —        | yes       | discrete action selected this call                             |
| `<param_1>`     | float   | matches §3.6.3 Action parameter rule                       | as declared | conditional | continuous parameter of the action (e.g. bid price)         |
| `<sizing_var>`  | float   | matches §3.6.3 Sizing rule                                 | as declared | yes    | action magnitude / quantity                                    |
| `reasoning`     | string  | length declared by author (default: 1–3 sentences; MAY be tightened, loosened, or replaced with a token cap) | —        | yes       | audit trail explaining WHY (also consumed by analysis skills)  |

The enum of `action` values MUST exactly match the "Action types
allowed" row in §3.6.3. The valid range of every other field MUST
exactly match the corresponding §3.6.3 rule. No field may
contradict §3.6.3.

For agents that emit compound actions (e.g. simultaneous
buy-and-sell quotes, or multi-target opinion moves), the decision
object MAY carry a list-of-actions field instead of a scalar
`action`; the schema then MUST enumerate the per-item field set
verbatim.

##### Content Constraints

- **Required fields**: every row marked `Required? = yes` in the
  Outputs table MUST be present on every call.
- **Forbidden fields**: fields not declared in the Outputs table
  MUST NOT be emitted (extra fields break downstream parsers).
- **Value ranges**: every emitted numeric field MUST fall inside
  its declared valid range; out-of-range values MUST be clamped by
  the agent (implementer responsibility) before emission.
- **Units and sign conventions**: units MUST match the declared
  column verbatim (e.g. price in the same units as `fundamental`,
  quantity in shares/contracts/units-of-position). Sign conventions
  MUST be stated (e.g. positive = buy, negative = sell) if the
  action space uses signed magnitudes.
- **Determinism markers**: if the decision is
  `stochastic-given-seed`, the emitted object MUST carry the seed
  used, or the implementation MUST log it deterministically per
  round.

##### Serialization Format

The agent's output MUST be serialised in the canonical tagged form
below so that **every implementation variant declared in the
target's §10.1 Variant Build Matrix** — whatever its name
(rule-driven, model-driven, retrieval-augmented, hybrid, or any
future variant class) — yields byte-comparable output structures:

    <analysis>...free-form reasoning, length as declared in the Outputs table (default guidance: 1–5 sentences)...</analysis>
    <decision>{"action": "<one of the declared enum values>",
                "<param_1>": <float>,
                "<sizing_var>": <float>,
                "reasoning": "<audit-trail explanation; length as declared in the Outputs table>"}</decision>

Rules that every variant MUST honour:

1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT
   optional. Parsers key on them.
2. The `<decision>` block MUST contain a single valid JSON object
   whose keys exactly match the Outputs table. Trailing commas,
   comments, or code fences inside `<decision>` are forbidden.
3. **Rule-driven variants** (deterministic, no model in the loop)
   MAY generate `<analysis>` from a deterministic template (e.g.
   `f"Rule fired: {trigger}"`), but the tags and JSON schema MUST
   still be present so downstream analysis tooling remains uniform.
4. **Model-driven variants** (any variant that consults an LLM,
   rule-plus-LLM hybrid, retrieval-augmented LLM, or future
   model-based class — regardless of literal variant name) MUST
   include this exact tag+JSON requirement in the system or user
   prompt so the model cannot omit or paraphrase the format.
5. **Retrieval-augmented variants** (any variant that reads
   external knowledge into the input surface — the finance-default
   `Rag` is one example) MUST additionally declare a fallback
   sentinel for the `retrieved_knowledge` input (e.g.
   `"(No relevant knowledge retrieved this round.)"`) and MUST
   inject it verbatim when retrieval returns empty; the fallback
   sentinel is part of this contract, not an implementation detail.

Variant classification is by capability, not literal name; the
target §10.1 Variant Build Matrix decides which classes are built
and what names they carry.

The field names shown above (`action`, `<param_1>`, `<sizing_var>`,
`reasoning`) are canonical **placeholders**. The authoring agent
MUST rename them to domain-natural identifiers (e.g. `bid_price`,
`quantity`, `opinion_shift`, `post_intensity`) that match §3.6.3,
and MUST update every row of the Outputs table in the same pass.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this §3.6.0 I/O Contract
during every coding pass and MUST use it as the single source of
truth for the following six activities.** Do NOT rely on prose
elsewhere; when this section and any other section disagree, this
section wins.

1. **Signal wiring** — every input row above MUST map to a real
   read against the environment / state / round header. If the
   engine cannot supply an input listed here, the implementation is
   incomplete.
2. **Decision emission** — the code path that emits a decision
   MUST populate every `Required? = yes` field, and MUST clamp any
   out-of-range numeric to its declared valid range.
3. **Prompt drafting (any model-driven variant)** — for every
   variant that consults a model (LLM, rule-plus-LLM hybrid,
   retrieval-augmented LLM, or any future model-based class named
   in target §10.1), the prompt template MUST spell out the tag
   pattern and the JSON schema literally, so the model cannot
   invent new fields or drop declared ones. Use a verbatim example
   that shows the closing `</decision>` tag.
4. **Parser tests** — the implementation MUST include a smoke test
   that (i) verifies the tag pattern is present, (ii) parses the
   `<decision>` JSON, (iii) asserts every required field is present
   and inside its valid range.
5. **Variant parity** — every variant declared `Yes` in the
   target's §10.1 Variant Build Matrix (whatever the scheme —
   finance defaults to `Rule / LLM / RuleLLM / Rag`, other domains
   MAY declare any subset, superset, or renaming) MUST produce
   output objects with the SAME field set. If a variant needs an
   extra field, extend this contract FIRST, then propagate to every
   declared variant.
6. **Contract-versus-prose conflict resolution** — if the mechanism
   in §3.6.2, the action space in §3.6.3, or the mathematical model
   in §3.6.4 seems to contradict this contract, the contract wins.
   Open a design revision and reconcile the other section in the
   same commit.

Cross-references:
- Every Input row here MUST also appear in §3.6.1 (signals) or
  §3.6.4 (state variables).
- Every Output field here MUST be reachable from the §3.6.3 Action
  Space specification (types, ranges, sizing).
- Every field's evidence / rationale MUST be traceable to §3.4 or
  §3.7 per the §4 Evidence Provenance requirement.
```

#### 3.6.1 Decision Information Set

A signal table plus an explicit "does NOT use" line. The *Memory
Window* column states how far back the agent looks at each signal.
Signals MAY include observations of peer behaviour (peer-action flow,
peer-state summary, public sentiment, news/event feed) when the
environment exposes them as readable signals.

**Completeness rule:** Every signal listed here MUST be consumed by at
least one step in §3.6.2 Core Behavioral Mechanism. Conversely, every
external input referenced in §3.6.2 MUST appear in this table.

```markdown
| Signal          | Type       | Memory Window | Rationale                          |
|-----------------|------------|---------------|------------------------------------|
| `<signal_name>` | Continuous | <N ticks>     | <why this agent needs this signal> |
| `<signal_name>` | Discrete   | <N ticks>     | <why this agent needs this signal> |

Does NOT use: <list of conspicuous non-signals that a reader might expect
this agent to consume, but it deliberately ignores>.
```

#### 3.6.2 Core Behavioral Mechanism

Numbered 5–10 step description of the agent's decision logic. Plain
English mixed with formulas. MUST NOT be code in any specific
programming language.

**Depth and precision rules:**
- The mechanism MUST be precise enough that two independent
  implementers, given only this specification, produce behaviourally
  equivalent logic (identical outputs for identical inputs and state).
- MUST cover ALL trigger branches declared in §3.5 Activation
  Triggers — every activation trigger maps to at least one mechanism
  step; every mechanism step traces to at least one trigger.
- MUST explicitly distinguish state-reads (inputs consumed) from
  state-writes (state variables updated) at each step. Any clear
  notation that makes this separation unambiguous is acceptable (e.g.
  "Read: ...; Compute: ...; Write: ..." or equivalent).
- Each step MUST trace to a specific theory from §3.4 Theoretical
  Foundation, OR be explicitly marked "(implementation convenience —
  no theoretical claim)" when the step is purely mechanical.
- Total steps MUST be 5–10. If fewer than 5, the mechanism is
  under-specified. If more than 10, decompose into named
  sub-mechanisms referenced by step number.

#### 3.6.3 Action Space

The set of actions the agent may emit and the **self-imposed
discipline** the agent applies to itself. Environment-imposed limits
(matching engine, tick grid, fee schedule, latency, message-routing
policy, content-moderation rules, regulator-imposed caps) MUST NOT
appear here — they belong to the scenario / environment
specification. Every aspect below MUST be specified.

The eight aspect *dimensions* are canonical and MUST all be visibly
covered. Row order MUST be preserved.

**Precision rule:** Every row MUST be answerable with a concrete
formula, threshold, or named constant. "Depends on context" or "varies"
is forbidden — if it varies, specify the rule that governs the
variation. The Sizing rule in particular MUST reference only declared
signals (§3.6.1) and parameters (§3.7); its form (closed-form
expression, decision table, optimisation objective, heuristic rule) is
flexible provided it is unambiguously implementable.

```markdown
| Aspect                | Specification                                                                    |
|-----------------------|----------------------------------------------------------------------------------|
| Action types allowed  | <enumerate every discrete action, including no-op>                               |
| Action parameter rule | <rule for the continuous parameter of an action, e.g. target value or intensity> |
| Sizing rule           | <formula or rule for action magnitude / quantity>                                |
| Action lifetime       | <duration before the action expires or is auto-cancelled>                        |
| Revision policy       | <when and how the agent retracts, replaces, or amends an emitted action>         |
| State constraint      | <self-imposed cap on the agent's internal state>                                 |
| Resource cap          | <self-imposed cap on cumulative cost, capital, or budget>                        |
| Exit rule             | <self-imposed termination trigger, or "none">                                    |
```

The eight row labels above are canonical generic labels. If a
domain-natural label is clearer for the target scenario (e.g. "Order
types allowed" instead of "Action types allowed" in a trading domain),
the specification MAY substitute it — provided the substitution is
stated explicitly and the row order is preserved.

Environment-imposed limits (matching engine, tick grid, fee schedule,
latency model, message-rate caps, regulator-imposed circuit breakers)
MUST NOT appear here.

#### 3.6.4 Mathematical Model

This section MUST formalize the agent's decision logic in unambiguous
mathematical or logical notation. The structural format is flexible —
choose whatever mathematical framework best fits the agent's decision
architecture (e.g. threshold-based triggering, utility optimisation,
Bayesian updating, rule tables, gradient-based adaptation, policy
functions, state machines, or any other).

Regardless of the chosen framework, the following **content aspects**
MUST all be explicitly addressed:

1. **Decision output** — what quantity or action the agent computes per
   call. Name the variable(s) and their type/domain.
2. **Decision logic formalization** — the complete mathematical or
   logical mapping from inputs (signals) and internal state to the
   decision output. MUST be precise enough that two independent
   implementers produce behaviourally equivalent logic. MUST cover
   every activation trigger declared in §3.5 (i.e. every condition
   under which the agent acts or holds). Pseudo-code, equations,
   inequalities, or decision tables are all acceptable; specific
   programming languages are NOT.
3. **State variables** — every internal variable the agent persists
   across calls, with type and initial value.
4. **State evolution** — how and when each state variable updates.
   MUST be explicit about update *ordering* relative to the decision
   (e.g. pre-decide, post-decide, post-execution). Each variable MUST
   be assigned exactly one update phase.
5. **Determinism contract** — state whether the decision is
   deterministic given identical inputs and state, or stochastic. If
   stochastic, name the distribution(s) and the seed-bearing source.
6. **Parameter symbol table** — MUST list every symbol used anywhere
   in §3.6 (mechanism steps, decision formalization, state-update
   formulas). No undeclared symbols are permitted.

```markdown
| Symbol  | Meaning   | Default Value | Source     |
|---------|-----------|---------------|------------|
| `alpha` | <meaning> | <value>       | <citation> |
```

**Quality rules:**
- The formalization MUST NOT be a vague prose description; it MUST be
  translatable to executable logic without interpretation.
- Every branch of the decision logic MUST be explicit (no implicit
  "otherwise do nothing").
- The mapping from §3.5 Activation Triggers to decision-logic branches
  MUST be traceable (a reader can identify which part of the
  formalization handles each trigger).

#### 3.6.5 Behavioral Properties

Four labelled lines:

- Time horizon: short / medium / long, with rationale
- Risk tolerance: low / medium / high, with rationale
- Information asymmetry: none / partial / full
- Psychological profile: cite the biases or rationality assumptions
  this agent embodies

### 3.7 Parameters **(MANDATORY)**

A single engine-agnostic table that documents every knob the agent
design exposes. Each row MUST use at minimum the canonical **eight
columns** below. Column names and order for these eight MUST NOT
change. Additional columns MAY be appended to the right to capture
extra metadata (e.g. `Calibration Date`, `Regime Sensitivity`).

- **Parameter** — exact key name, back-ticked.
- **Type** — `int` / `float` / `str` / `bool` / `enum<...>` /
  `list<T>` / `distribution<...>`.
- **Default** — concrete default value. No placeholders.
- **Valid Range** — admissible domain (`[0, 1]`, `> 0`, `int >= 1`,
  `{action_A, action_B, hold}`, named enum). Required for tuning safety.
- **Sensitivity** — `high` / `medium` / `low`.
- **Description** — one-sentence meaning in plain language.
- **Impact** — direction of effect when the value increases ("Higher ->
  ..."). MUST state direction, not restate the description. SHOULD be
  quantitative where feasible (e.g. "Higher -> 2x response latency").
- **Source** — citation, calibration paper, or `Standardised`.

**Depth and quality rules:**
- Minimum 3 parameter rows for any non-trivial agent. Agents with
  fewer MUST include an explicit justification sentence below the table.
- Every parameter with Sensitivity=high MUST have Source citing
  empirical data (not "Standardised" or "author estimate").
- Sensitivity labeling criteria:
  - **high** = +/-10% change in this parameter produces >2x change in
    the agent's primary behavioural output metric.
  - **medium** = noticeable but sub-2x effect on behavioural output.
  - **low** = minimal effect within the valid range.
- Every parameter MUST appear in at least one formula in §3.6.4
  (no orphan parameters that exist only in the table).

If the agent design exposes zero tunable parameters, write
`_No tunable parameters._` with a justification sentence.

```markdown
## Parameters

| Parameter | Type   | Default | Valid Range | Sensitivity  | Description                | Impact                          | Source     |
|-----------|--------|---------|-------------|--------------|----------------------------|---------------------------------|------------|
| `<name>`  | <type> | <value> | <domain>    | high/med/low | <one-sentence description> | Higher -> <direction-of-effect> | <citation> |
```

### 3.8 Worked Numerical Examples

Provide **at least three** worked cases plus **one edge case**, each as
a fenced block. Each case MUST show:

- The system state (real numbers, not placeholders).
- The intermediate calculation step-by-step.
- The decision (action type, magnitude, continuous parameter if any).
- The state update post-decision (so the reader sees memory evolve).

**Quality rules:**
- All numeric values MUST be drawn from the Default column of §3.7
  (not invented ad-hoc). If a scenario-specific value is needed, state
  it explicitly and justify.
- The three primary cases MUST collectively cover ALL non-hold branches
  of the decision logic in §3.6.4. If the logic has 4 branches
  (e.g. act-up, act-down, hold, deactivate), provide 4 primary cases.
- The edge case MUST demonstrate at least one of: cold-start (empty
  state), extreme deviation, deactivation condition, cap-clamp,
  regime-flip, or missing-signal fallback from §3.5.
- Each calculation MUST show every intermediate variable so a reader
  can manually verify each step in sequence (single-step verifiability).

```markdown
### Case 1 — <branch name>
System state: <real numbers from defaults>
Calculation:
  <step 1: variable = formula = numeric result>
  <step 2: ...>
Decision: <action type, magnitude, continuous parameter>
State update: <variable: old_value -> new_value>

### Case 2 — <branch name>
...

### Case 3 — <branch name>
...

### Edge Case — <name>
...
```

### 3.9 Behavioral Verification and Calibration

How a researcher will know this individual agent's implementation is
correct and its parameters are well-calibrated. This section concerns
the **agent as a single participant** — NOT population-level or
emergent system outcomes (those belong to the scenario specification).

**Quality rules:**
- Behavioral expectations MUST describe what THIS agent does given
  specific inputs — not what a population of agents produces.
- Minimum 3 sanity bounds, each stated as a falsifiable IF-THEN
  condition about this agent's individual behaviour (e.g. "IF the
  agent receives a signal above threshold AND does not act, THEN
  implementation is broken").
- Ablation hooks MUST state the expected change in this agent's
  individual behaviour AND the metric to measure it.

```markdown
**Calibration data sources** (per parameter, where applicable):
- `<param>` <- <citation, table, specific value or range>

**Expected individual behaviour** (what this agent MUST do when
correctly implemented):
- Given <input condition 1>, agent MUST <specific action/response>
- Given <input condition 2>, agent MUST <specific action/response>
- Given <input condition 3>, agent MUST <specific action/response>

**Sanity bounds (red flags indicating broken implementation)**:
- IF <agent does X when it should do Y> THEN <broken because ...>
- IF <agent violates its own declared constraint> THEN <broken because ...>
- IF <agent's output is outside declared valid range> THEN <broken because ...>
```

#### 3.9.1 Ablation Hooks

Named knob settings that produce meaningful ablations. Each row MUST
state the hypothesis, the expected direction, and the metric.

```markdown
| Ablation name | Setting     | Hypothesis tested | Expected direction  | Metric            |
|---------------|-------------|-------------------|---------------------|-------------------|
| `<name>`      | `<setting>` | <hypothesis>      | <increase/decrease> | <what to measure> |
```


### 3.10 Academic References

Numbered table. Every paper cited anywhere in the specification MUST
appear here. No citation in any section (§3.4, §3.7 Source, §3.9
Calibration, etc.) is permitted to be absent from this table.

```markdown
| # | Citation              | Notes       |
|---|-----------------------|-------------|
| 1 | <full citation + DOI> | <relevance> |
```

### 3.11 Design Provenance and Versioning

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

## 4. Evidence Provenance Requirement

Every substantive design choice in a conformant specification MUST
declare its **evidence source**. This rule applies ACROSS ALL sections
(§3.3–§3.9), not only to the Theoretical Foundation. A "substantive
design choice" is any claim, value, threshold, signal selection,
mechanism step, constraint, or mathematical formulation that shapes
the agent's behaviour.

### 4.1 Evidence Type Taxonomy

Each evidence source MUST be classified into one of the following
categories. Higher-numbered categories carry weaker epistemic weight;
authors SHOULD prefer lower-numbered sources where available.

| # | Evidence Type              | Format requirement                                                        |
|---|----------------------------|---------------------------------------------------------------------------|
| 1 | **Peer-reviewed research** | Full citation + DOI; specific finding (table, figure, equation number)    |
| 2 | **Domain textbook**        | Author, title, edition, chapter/section/page; specific principle or model |
| 3 | **Empirical dataset**      | Dataset name, source, time range, sample size; specific statistic cited   |
| 4 | **Practitioner consensus** | Named community/standard + reference document (e.g. CFA curriculum, etc.) |
| 5 | **Logical derivation**     | "Derived from [cited element within this spec]" + derivation sketch       |
| 6 | **Expert judgment**        | Author's domain expertise; MUST state the assumption explicitly and mark  |
|   |                            | with ⚠️ so reviewers can challenge or replace it with stronger evidence    |

### 4.2 Application Rules

- **§3.3 Definition and Goals:** The real-world counterpart claim MUST
  cite evidence (Type 1–4) that this participant type exists and
  behaves as described.
- **§3.4 Theoretical Foundation:** Already mandates Type 1–3 evidence
  via its depth rules.
- **§3.5 Activation Triggers:** Each trigger condition and each
  deactivation condition MUST cite WHY this condition is
  behaviourally relevant (Type 1–5).
- **§3.6.1 Decision Information Set:** Each signal's inclusion MUST
  cite evidence that real-world participants of this type use this
  information (Type 1–5). The "Does NOT use" list SHOULD cite
  evidence for deliberate exclusion.
- **§3.6.2 Core Behavioral Mechanism:** Already requires tracing each
  step to §3.4 (which is evidence-backed). Steps marked
  "implementation convenience" are exempt.
- **§3.6.3 Action Space:** Self-imposed constraints (state cap,
  resource cap, exit rule) MUST cite WHY this constraint exists
  (Type 1–6). "None" is permitted only if explicitly justified.
- **§3.6.4 Mathematical Model:** The choice of mathematical framework
  MUST cite its source (Type 1–5). If the formalization is original,
  classify as Type 5 or 6 with explicit derivation.
- **§3.7 Parameters:** Already mandates a Source column per row.
  High-sensitivity parameters MUST NOT use Type 6.
- **§3.9 Verification:** Calibration data sources already cite
  evidence. Sanity bounds MUST trace to mechanism logic (Type 5).

### 4.3 Inline Evidence Notation

Evidence sources SHOULD be cited inline using a compact notation that
references the §3.10 Academic References table:

```
[Ref #] or [Ref #, Table 3] or [Textbook, Ch. 5] or [Expert judgment ⚠️]
```

This notation keeps the specification readable while ensuring every
claim is traceable. A reviewer MUST be able to trace any design choice
back to its declared source within 30 seconds.

### 4.4 Minimum Evidence Coverage

- A conformant specification MUST have ≥80% of its substantive design
  choices backed by Type 1–4 evidence.
- Type 6 (expert judgment) MUST NOT account for >20% of evidence
  sources across the entire specification.
- Every Type 6 citation MUST be marked with ⚠️ and is considered a
  technical-debt item to be resolved in future versions.

---

## 5. Cross-Section Consistency Rules

A conformant specification MUST satisfy ALL of the following
traceability constraints. These rules ensure internal coherence across
sections and prevent orphan content.

- Every **parameter** in §3.7 MUST appear in at least one formula in
  §3.6.4 Mathematical Model.
- Every **signal** in §3.6.1 Decision Information Set MUST be consumed
  by at least one step in §3.6.2 Core Behavioral Mechanism.
- Every **activation trigger** in §3.5 MUST map to a branch in the
  decision logic formalization of §3.6.4.
- Every **worked example** in §3.8 MUST use Default values from §3.7
  (or explicitly state and justify any deviation).
- Every **expected behaviour** in §3.9 MUST be traceable to the
  mechanism in §3.6.2 (the reader must be able to see HOW the
  mechanism produces the declared individual-level response).
- Every **citation** anywhere in the specification (§3.4, §3.7 Source,
  §3.9, etc.) MUST appear in the §3.10 Academic References table.
- Every **symbol** used in §3.6 (mechanism, decision formalization,
  state-update formulas) MUST be declared in §3.6.4 Parameter
  symbol table.
- The **"Does NOT use"** list in §3.6.1 MUST NOT contradict any signal
  actually consumed in §3.6.2.
- Every **Input row** in §3.6.0 I/O Contract MUST appear either as a
  signal in §3.6.1 or as a state variable in §3.6.4. No input in the
  contract may be undeclared elsewhere.
- Every **Output field** in §3.6.0 I/O Contract MUST be reachable
  from the §3.6.3 Action Space: `action` enum values MUST match
  "Action types allowed" verbatim; every numeric output field's valid
  range MUST match the corresponding §3.6.3 rule (Action parameter
  rule, Sizing rule, State constraint, or Resource cap).
- The **canonical tag pattern** (`<analysis>...</analysis><decision>{JSON}</decision>`)
  declared in §3.6.0 MUST be honoured by **every implementation
  variant declared `Yes` in the target's §10.1 Variant Build
  Matrix** — regardless of the scheme (finance defaults to
  `Rule / LLM / RuleLLM / Rag`; other domains MAY declare any
  subset, superset, or renaming). No variant may add or drop
  declared output fields without first extending §3.6.0.

---

## 6. Validation Checklist (Self-Check)

An author MUST run through this list and ensure every item is checked
before declaring the specification complete. Each unchecked item is a
blocker.

**Structural completeness:**
- [ ] H1 is a sentence-cased role phrase, not a class or code identifier
- [ ] §3.2 Summary has at least the 7 canonical rows in order;
      additional rows permitted
- [ ] §3.3 Definition and Goals covers (a) what the agent models with a
      named real-world counterpart from a domain-appropriate enumeration, (b)
      decision goal, (c) behavioural role + >=2 explicit non-goals
- [ ] §3.4 Theoretical Foundation has >=1 sub-block; compound agents
      have >=2 sub-blocks; each sub-block has all 9 labelled lines
- [ ] §3.5 declares Call Frequency, Prerequisite Signals,
      Missing-Signal Policy, Activation Triggers (with `<Default>`),
      Deactivation Conditions, Behavioral Adaptation table (>=2 rows),
      and Environmental Dependencies
- [ ] §3.6 has all six H4 sub-blocks (I/O Contract, Information Set,
      Mechanism, Action Space, Mathematical Model, Behavioral Properties)
- [ ] §3.6.0 I/O Contract fills all five required blocks (Inputs,
      Outputs, Content Constraints, Serialization Format, Implementer
      Contract Reminder); no block is left as "N/A" without a
      one-sentence justification
- [ ] §3.6.0 Outputs table names every required field with a Type,
      a Valid Range / Enum, a Unit, a Required? flag, and a Meaning
- [ ] §3.6.0 Serialization Format block declares the literal
      `<analysis>...</analysis><decision>{JSON}</decision>` tag
      pattern and states the retrieval fallback sentinel (or an
      explicit "no retrieval-augmented variant declared in target
      §10.1" justification)

**Depth and precision:**
- [ ] §3.4 every "Mathematical Formulation" is a single implementable
      equation; every "Empirical Evidence" cites an effect size; every
      "Calibration Source" provides a numeric range
- [ ] §3.6.2 has 5–10 steps; each step separates state-reads from
      state-writes; every step traces to §3.4 or is marked
      "implementation convenience"
- [ ] §3.6.2 is precise enough for two independent implementers to
      produce behaviourally equivalent logic
- [ ] §3.6.3 Action Space: every row is a concrete formula/threshold;
      the Sizing rule references only declared signals and parameters;
      no environment rules present
- [ ] §3.6.3 Action Space visibly covers all eight canonical
      dimensions under either generic or domain-specific row labels
- [ ] §3.6.4 decision logic covers all §3.5 Activation Triggers;
      state evolution specifies ordering; parameter symbol table has
      no undeclared symbols
- [ ] §3.7 has >=3 rows (or justified fewer); every high-sensitivity
      parameter cites empirical data; every parameter appears in §3.6.4;
      every Impact is directional
- [ ] §3.8 uses Default values from §3.7; covers all non-hold trigger
      branches; edge case demonstrates deactivation/cap/regime-flip;
      every step is single-step verifiable

**Behavioral verification:**
- [ ] §3.9 behavioural expectations describe individual agent
      responses (not population-level emergent phenomena); >=3 sanity
      bounds as falsifiable IF-THEN statements; ablation hooks state
      direction and metric

**Cross-section consistency (§5 rules):**
- [ ] Every §3.7 parameter appears in §3.6.4
- [ ] Every §3.6.1 signal is consumed in §3.6.2
- [ ] Every §3.5 trigger maps to a §3.6.4 decision-logic branch
- [ ] Every §3.8 example uses §3.7 defaults
- [ ] Every §3.9 behavioural expectation traces to §3.6.2
- [ ] Every citation appears in §3.10
- [ ] No undeclared symbols in §3.6
- [ ] Every §3.6.0 Input row is declared as a signal in §3.6.1 or
      as a state variable in §3.6.4
- [ ] Every §3.6.0 Output field is reachable from §3.6.3 Action
      Space (enum values match "Action types allowed"; numeric
      ranges match the corresponding §3.6.3 rules)
- [ ] The `<analysis>/<decision>` tag pattern in §3.6.0 is honoured
      by **every implementation variant declared `Yes` in the
      target's §10.1 Variant Build Matrix** (whatever the scheme —
      finance-default `Rule / LLM / RuleLLM / Rag`, or any other
      subset/superset/renaming); variants add no undeclared output
      fields

**Evidence provenance (§4 rules):**
- [ ] ≥80% of substantive design choices cite Type 1–4 evidence
- [ ] Type 6 (expert judgment) accounts for ≤20% of total evidence;
      every Type 6 is marked with ⚠️
- [ ] Every signal in §3.6.1 cites evidence for inclusion
- [ ] Every self-imposed constraint in §3.6.3 cites evidence
- [ ] Mathematical framework in §3.6.4 cites its source
- [ ] Every activation trigger in §3.5 cites behavioural relevance
- [ ] Reviewer can trace any design choice to its declared source
      within 30 seconds

**Scenario-portability:**
- [ ] No specific scenario names, absolute numeric levels, or fixed round
      counts appear anywhere in the specification
- [ ] All numeric thresholds are parameterised via §3.7
- [ ] Decision logic functions given only §3.6.1 declared signals
- [ ] No peer-network topology, social graph, or environment rules
      (matching engine, tick grid, fees, latency, message-routing,
      content-moderation, regulator-imposed caps) appear anywhere

---

## 7. Status

| Field   | Content                                                                 |
|---------|-------------------------------------------------------------------------|
| Version | 2.3.1                                                                   |
| Created | 2025-06-11 (v1.0.0); last minor bump 2026-07-01 (v2.3.1)                |
| Status  | canonical                                                               |
| Domains | Domain-agnostic (all simulation domains)                                |
| Change log | 2026-07-01 v2.3.1: de-hardcoded the variant scheme throughout §3.6.0, §5, and §6. Literal `Rule / LLM / RuleLLM / RAG` enumerations replaced with references to the target's §10.1 Variant Build Matrix and with capability-class terminology (rule-driven / model-driven / retrieval-augmented) so any subset, superset, or renaming stays contract-conformant. Retrieval-fallback rule generalised to "any retrieval-augmented variant". <br> 2026-07-01 v2.3.0: added mandatory §3.6.0 I/O Contract (Inputs, Outputs, Content Constraints, Serialization Format `<analysis>...</analysis><decision>{JSON}</decision>`, Implementer Contract Reminder); tightened §5 consistency rules and §6 validation checklist accordingly. |
