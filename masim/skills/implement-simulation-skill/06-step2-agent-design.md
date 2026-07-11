# Step 2: Design Agent Architecture

## Purpose

Translate research findings from Step 1 into a concrete agent design. This step produces the content for `simulation-bases.md §3` (Environment Design) and `§4` (Agent Taxonomy). Every design decision made here must be backed by a citation from Step 1.

<!-- Finance appendix (§4.1.F) relabels §3 as "Market Design" and §4 as "Investor Taxonomy". Other domains follow their own §4.1.{X} appendix (Opinion → §4.1.O, Epidemics → §4.1.E, Sociology → §4.1.S). -->


---

## Contract (Inputs / Outputs / Polish Hooks)

This block is the **stable I/O declaration** for Step 2. Both
`masim/skills/create-simulation-pipeline.md` and
`masim/skills/polish-simulation-pipeline.md` anchor to it.

**Inputs (consumed).**

| Source                                        | Used for                                                                                                                      |
|-----------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| Target §7 Agent Roster (rows)                 | one-to-one seed for each `simulation-bases.md §4.{N}` block                                                                   |
| Target §8 Environment Specification           | seeds `simulation-bases.md §3` (price formation, info broadcast, constraints, round granularity)                              |
| Target §4 Theoretical Anchors                 | each agent's `Theoretical Foundation` sub-block                                                                               |
| Target §9 Parameter Seeds                     | each agent's `Parameters` table + `simulation-bases.md §6`                                                                    |
| `simulation-bases.md §2` (from Step 1)        | Theory citations per agent                                                                                                    |
| `examples/AGENT_POOL/{domain}/*.md`           | AGENT_POOL three-stage match (§2.2.0)                                                                                         |
| `masim/skills/agent-design-skill.md` §3, §6   | Universal Agent Design Handbook — canonical section order and Validation Checklist                                            |
| `masim/skills/agent-icon-generation-skill.md` | Icon generation and registration for any pool agent whose icon is missing or broken, including new/forked and reused profiles |

**Outputs (produced or extended).**

| Artefact                                                           | Extent of write                                                                                                                                                                                                                              |
|--------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `examples/{ScenarioName}/simulation-bases.md §3`                   | Environment design — State Dynamics Model, Additional Mechanisms, Information Broadcast (finance appendix: Market design — Price Formation Model, …)                                                                                         |
| `examples/{ScenarioName}/simulation-bases.md §4`                   | Agent Taxonomy — one §4.{N} block per target §7 row, each conforming to `agent-design-skill.md §3.1 — §3.11` under embedded-form header levels (see `02-root-documents-spec.md §4.0`); finance appendix relabels this as "Investor Taxonomy" |
| `examples/{ScenarioName}/simulation-bases.md §5`                   | Agent Diversity Verification                                                                                                                                                                                                                 |
| `examples/{ScenarioName}/simulation-bases.md §7`                   | Communication and Round Structure                                                                                                                                                                                                            |
| `examples/{ScenarioName}/simulation-build-log.md §A`               | AGENT_POOL Reuse-or-Create Gate log — one row per candidate archetype with Stage reached, Outcome, Pool file                                                                                                                                 |
| `examples/AGENT_POOL/{domain}/{new-file}.md`                       | On `new` or `fork` outcome only — the resulting agent spec is written back to the pool as a reusable archetype                                                                                                                               |
| `examples/AGENT_POOL/agent_images/icons/{domain}-{agent-stem}.png` | Matching icon generated via `agent-icon-generation-skill.md` whenever a new/forked pool profile is created or an existing reused profile has no resolving icon                                                                               |
| `examples/AGENT_POOL/agent_images/design.md`                       | Icon mapping row added or updated for every pool profile whose icon is generated or repaired                                                                                                                                                 |

**Polish Hooks (what a polish audit re-verifies against this step).**
When `polish-simulation-pipeline.md` audits Step 2, it MUST re-run
these six checks — no new agents are invented except when the
AGENT_POOL gate itself returns `fork` or `new`:

1. **Section order per agent.** Every §4.{N} block follows `agent-design-skill.md §3.1 → §3.11` canonical order under embedded-form header levels; missing sub-sections are filled from material already in the file.
2. **AGENT_POOL three-stage match re-run.** Even for agents originally reused, re-execute §2.2.0 Stage 1 → 2 → 3 against the current pool; the new outcome (`reuse` / `override` / `fork` / `new`) is recorded in the agent's §3.11 Design Provenance.
3. **§3.11 Provenance updated.** Every audited agent has its §3.11 Provenance amended with a `Polish audit: YYYY-MM-DD` entry listing structural changes (or "no structural change") and the current pool file path.
4. **Agent icon resolution.** Every referenced pool profile must resolve to exactly one valid icon. "Referenced" includes profiles named in `simulation-bases.md §4`, profiles resolved by the AGENT_POOL match, and profiles implied by variant-local identities such as `configs/{Scenario}/{Variant}/players.yml` values where `identity.replace("_", "-")` yields the expected pool stem. If the profile is `new` or `fork`, or if a reused profile has no `Icon` row, a broken link, a missing PNG, or no mapping row in `agent_images/design.md`, invoke `agent-icon-generation-skill.md` immediately. The audit is incomplete until the PNG filename is `{domain}-{agent-stem}.png`, the pool profile has the matching `Icon` row, and `agent_images/design.md` records the agent-to-icon mapping. Do not satisfy this hook with a scenario-level image or any filename that is not tied to a concrete agent stem.
5. **Handbook §6 three-PASS.** For every agent, run `agent-design-skill.md §6` Validation Checklist three consecutive times; any FAIL resets the count.
6. **Cross-variant archetype-set parity.** For every scenario with more than one built variant (target §10.1), compute the archetype set per variant as `{ _canonical_archetype(identity) : identity ∈ configs/{Scenario}/{V}/players.yml top-level keys, excluding reserved keys such as `environment` / `market` / `knowledge` }`. All built variants of the same scenario MUST have equal archetype sets — the pool profiles and icons are archetype-level assets and are shared across variants (the variant prefix is stripped by `_canonical_archetype()` before asset lookup). On mismatch, halt via `AskUserQuestion` with three canonical options: (a) align the outlier variant to the majority archetype set; (b) align the majority to the outlier; (c) accept the divergence and record it as an intentional per-variant design choice in `simulation-bases.md §4` and target §7 via define-skill revise mode. Never silently paper over parity gaps by generating extra assets. Backing tool: `scripts/audit_agent_naming.py --scenario {ScenarioName}`.

---

## 2.1 Environment / Coordinator Design

The Environment (also called the Coordinator) is the single entity that
receives every agent's action, updates the shared state, and broadcasts
the new state at the start of the next round. Design it before designing
any participant agent. In finance scenarios the Environment is called
`Market` and its update law is the price formation formula; in opinion
dynamics it is a discussion venue with an update rule over opinion
vectors; in epidemics it is a compartment / contact process; in
sociology it is a diffusion / interaction network. The domain-specific
instantiation lives in the target file's §4.1.{X} appendix.

### 2.1.1 State Update (State Dynamics) Mechanism

**Reference implementation**: `examples/{PriorScenario}/{Variant}/players.py` — the class implementing the environment coordinator (finance instantiation: `Market`).

Every environment MUST have an explicit **state update law** that maps
`(previous_state, aggregate_action, exogenous_shock)` to
`next_state`. The domain-specific form of this law is the target file's
§4.1.{X} appendix; the design task here is to (a) write down the law,
(b) name every coefficient and every exogenous term, and (c) justify
each numeric choice with a citation from Step 1.

<details>
<summary><strong>Finance appendix (§4.1.F) instantiation — Price Formation Mechanism</strong></summary>

For finance scenarios the state update law is the standard price
impact + mean reversion + noise formula:

```
P(t+1) = P(t) + λ · D(t) + γ · [F(t) − P(t)] + ε(t)
```

For each parameter, make an explicit calibration decision:

**λ (price impact)**:
- Empirical range: 0.01–0.05 (Hasbrouck, 1991, *Journal of Finance*, microstructure estimates)
- Choose higher λ for: bubble/crash simulations (need large price moves from concentrated selling)
- Choose lower λ for: behavioral bias simulations (smaller, persistent deviations from gradual behavior)
- Your choice: [value] — because [reason tied to phenomenon mechanics]

**γ (mean reversion)**:
- Empirical range: 0.005–0.05 (French & Roll, 1986, *Journal of Financial Economics*)
- Choose lower γ for: bubble/bias simulations (mispricing must persist; fast mean reversion destroys the phenomenon)
- Choose higher γ for: crash simulations (need recovery after cascade)
- Your choice: [value] — because [reason]

**σ (noise standard deviation)**:
- Empirical range: 0.01–0.03 per round (Roll, 1984, bid-ask bounce model)
- Too high: noise obscures the phenomenon signal
- Too low: price paths become unrealistically clean
- Typical choice: 0.015–0.02 for most simulations

**F(t) (fundamental value)**:
- Constant vs. growing: constant F is simpler and sufficient for most behavioral bias simulations; growing F is needed for long-horizon simulations
- Standard choice: constant F = 100.0 (normalization — acceptable)
</details>

<!-- Non-finance domains substitute the domain-appropriate law:
     Opinion (§4.1.O): x_i(t+1) = x_i(t) + μ · Σ_{j ∈ N(i)} w_ij · [x_j(t) − x_i(t)]  (bounded confidence / DeGroot / Deffuant-Weisbuch)
     Epidemics (§4.1.E): compartment update per SIR / SEIR: dS/dt = −β S I / N, dI/dt = β S I / N − γ I, dR/dt = γ I
     Sociology (§4.1.S): threshold adoption — agent i adopts at t+1 if fraction of adopting neighbours ≥ θ_i (Granovetter 1978)
     Every non-finance instantiation must equally list its coefficients (μ / β / γ / θ) with empirical ranges and a citation. -->

### 2.1.2 Additional Mechanism Decision Table

For EACH auxiliary environment mechanism, make an explicit Yes/No
decision. The row set below is the finance-appendix instantiation;
non-finance scenarios substitute domain-appropriate mechanisms (opinion:
homophily filter, echo-chamber threshold; epidemics: quarantine,
vaccination, social distancing; sociology: adoption caps, network
rewiring) per their §4.1.{X} appendix.

<details>
<summary><strong>Finance appendix (§4.1.F) instantiation — Market Mechanism Decision Table</strong></summary>

| Mechanism                         | Include? | Rationale                                             | Implementation trigger                               |
|-----------------------------------|----------|-------------------------------------------------------|------------------------------------------------------|
| Short-selling constraints         | [Yes/No] | [Why]                                                 | [Condition: deviation > threshold; cap at max_short] |
| Short-selling cost                | [Yes/No] | [Why]                                                 | [Cost rate reduces effective short size]             |
| Margin call / forced deleveraging | [Yes/No] | [Why — essential for leverage-based simulations]      | [equity_ratio < threshold → force sell]              |
| Price floor (P ≥ 0.01)            | Yes      | Always — prevents numerical instability               | `new_price = max(new_price, 0.01)`                   |
| Circuit breaker                   | [Yes/No] | [Why — for crash simulations that need trading halts] | [% move trigger]                                     |
</details>

### 2.1.3 Information Broadcast Design

Apply the minimal sufficiency principle: broadcast only the fields that
at least one agent actually uses. Every broadcast field must be
justified. The concrete field names are domain-specific; the schema
below is the finance-appendix instantiation.

<details>
<summary><strong>Finance appendix (§4.1.F) instantiation — Broadcast Payload</strong></summary>

```
Standard broadcast (all simulations):
  price         — current market price (all agents need this)
  fundamental   — intrinsic value (agents making deviation-based decisions)
  deviation     — (price − fundamental) / fundamental (pre-computed for convenience)
  round         — current round number (frequency-controlled agents)

Optional (add only if a specific agent needs it):
  prev_price    — previous price (for agents computing returns in-code)
  return_pct    — return in percentage (for LLM readability in prompts)
  volume        — total shares traded (for volume-sensitive agents)
  bubble_ratio  — price / fundamental (for bubble simulations)
  net_demand    — signed net demand (for agents reading crowd sentiment)
```
</details>

<!-- Non-finance instantiations of the broadcast payload:
     Opinion (§4.1.O): {mean_opinion, opinion_variance, cluster_count, round}
     Epidemics (§4.1.E): {S_frac, I_frac, R_frac, R_effective, round}
     Sociology (§4.1.S): {adoption_fraction, active_agents, round}
     Any additional field must be justified by at least one agent's decision rule. -->

**Decision rule**: If no agent in the design uses a field, don't broadcast it.

---

## 2.2 Agent Taxonomy Design

<!-- Finance appendix (§4.1.F) relabels this section as "Investor Taxonomy Design". -->

Design 4-6 agent types. Fewer than 4 produces insufficient behavioral diversity; more than 6 makes calibration unwieldy.

### 2.2.0 AGENT_POOL Reuse-or-Create Gate (MANDATORY)

Before writing any new per-agent specification, every candidate archetype
MUST pass through the **reuse-or-create gate** rooted at
`examples/AGENT_POOL/<domain>/`. The gate exists because the project has
already accumulated dozens of agent archetypes across scenarios; duplicating
an existing archetype under a new name fragments the calibration evidence
and pollutes downstream comparison.

**Candidate source.** The candidate roster is **not** invented inside Step 2.
It is read from the target file's **§7 Agent Roster** (specified by
`masim/skills/define-simulation-scenario-skill.md`), which the pipeline's
Phase 2 has already mirrored into `simulation-build-log.md §B.4` with a
`Pipeline confirmation` column. Each row of §B.4 is a single candidate to
push through the gate below.

The gate runs as a **three-stage match** against the domain folder that
fits the new scenario (for finance-domain scenarios this is
`examples/AGENT_POOL/finance/`; for opinion-dynamics or other domains, create
a new sibling folder named after the domain in lowercase kebab-case if it
does not already exist).

**Stage 1 — Filename scan.** List every `*.md` file in the relevant domain
folder. Map each filename (kebab-case role phrase) to the candidate's
intended role. A close filename match (e.g. candidate "trend-follower" vs
existing `momentum-trader.md`) is a strong signal to inspect further.

**Stage 2 — Summary fingerprint check.** For every plausible candidate from
Stage 1, read **only** the H1 line and the Summary table (the 7 fingerprint
rows). Compare:

- Archetype phrase
- Theory Family
- Behavioral Tendency / Market Role
- Time Horizon, Risk Tolerance, Information Asymmetry

If at least 5 of the 7 fingerprint rows match the new candidate, escalate
to Stage 3. If fewer than 5 match, this archetype is genuinely new — proceed
to design.

**Stage 3 — Full-text inspection.** For every Stage-2 escalation, read the
full file (Definition and Goals, Theoretical Foundation, Decision
Information Set, Core Behavioral Mechanism, Parameters). Decide one of:

- **Reuse as-is.** The existing archetype already covers the candidate.
  Reference the existing file by relative path from `simulation-bases.md §4`
  (e.g. `> Reuses agent profile: examples/AGENT_POOL/finance/momentum-trader.md`)
  and embed only the variant-specific population/instance count and
  parameter calibration. The full handbook block is NOT duplicated in
  `simulation-bases.md §4` — only the reuse pointer and the calibration
  delta.
- **Reuse with parameter adjustment.** Same as above, but the new scenario
  needs different defaults. Document the per-parameter delta in
  `simulation-bases.md §4.{N}.6` (Parameters) under a "Scenario calibration
  override" sub-heading. The pool file is NOT modified.
- **Fork.** The existing archetype is close but a substantive mechanism
  differs (different signal set, different mathematical model, different
  activation logic). Treat as new design (skip to §2.2.2) and store the
  result as a new file in the pool with a distinct filename. The fork's
  Theoretical Foundation MUST cite the parent file and explicitly call out
  the mechanism difference.
- **Design new.** No existing archetype matched. Proceed to §2.2.2.

**Audit log.** The gate's decisions MUST be captured in
`examples/{Scenario}/simulation-build-log.md §A` (see
`04-step0-load-target.md §0.3`) as a small table:

```markdown
| Candidate archetype | Stage reached | Outcome            | Pool file (if reused) |
|---------------------|---------------|--------------------|-----------------------|
| <name>              | 1 / 2 / 3     | reuse / fork / new | <relative path>       |
```

**Where to store new designs.** Every newly designed agent that survives
§2.2.2 + the validation gate in §2.2.3 MUST be written back to
`examples/AGENT_POOL/<domain>/<kebab-name>.md` so that future scenarios can
reuse it. The file uses the **standalone** handbook header levels (H1 for
title, H2 for sections, H4 for behavioral framework sub-blocks) — NOT the
embedded form used inside `simulation-bases.md §4`. The same content is
then re-levelled and copied into `simulation-bases.md §4.{N}` for the
scenario being built.

**Icon requirement for every pool-backed agent.** Immediately after writing
`examples/AGENT_POOL/<domain>/<kebab-name>.md` for a `new` or `fork`
outcome, invoke `masim/skills/agent-icon-generation-skill.md`. For
`reuse` and `reuse with parameter adjustment` outcomes, inspect the reused
pool profile before closing the gate. If the profile has no `Icon` row, the
linked PNG does not exist, the filename does not match
`<domain>-<kebab-name>.png`, or `agent_images/design.md` has no mapping row
for the profile, invoke the same icon skill as a repair step. The gate is
not complete until:

- `examples/AGENT_POOL/agent_images/icons/<domain>-<kebab-name>.png` exists.
- The pool profile's Design Provenance table has exactly one `Icon` row
  linking to `../agent_images/icons/<domain>-<kebab-name>.png`.
- `examples/AGENT_POOL/agent_images/design.md` has a mapping row for the
  profile, pairing `examples/AGENT_POOL/<domain>/<kebab-name>.md` with
  `<domain>-<kebab-name>.png`.

If image generation is unavailable, halt and report the missing icon as a
blocking asset task; do not insert a broken or placeholder icon link.

### 2.2.1 Taxonomy Design Principles

<!-- Finance appendix (§4.1.F) relabels "agent type" as "investor type" throughout §2.2. -->

**Principle 1 — Theory-first**: Start from each theory in `simulation-bases.md §2`. Each theory should produce exactly one agent type.

**Principle 2 — Conflicting incentives**: At least one agent type must be stabilizing (mean-reversion, value-buying, dampening) to create the competitive dynamic that makes the phenomenon an emergent property rather than a guaranteed outcome.

**Principle 3 — Role coverage**: Ensure the following roles are covered:
- Primary phenomenon driver: the agent that initiates the target dynamic (destabilizing)
- Amplifier: an agent that makes the phenomenon worse once started (destabilizing)
- Stabilizer: an agent that provides corrective force (stabilizing)
- Background noise: an agent whose action is weakly correlated with the phenomenon signal, providing baseline activity (neutral; finance instantiation: random-order noise trader providing liquidity)
- Optional: a secondary phenomenon driver or a specialized observer

**Principle 4 — Distinct information sets**: No two agent types should use identical information signals with identical processing. Diversity in information processing is what creates interesting emergent dynamics.

### 2.2.2 Per-Agent Specification — Authored Under the Universal Agent Design Handbook

Each agent type is specified under the **Universal Agent Design Handbook**
at `masim/skills/agent-design-skill.md`. The handbook is the single source of
truth for the intrinsic specification of any participant agent; the
domain-specific row labels, value palettes, and worked instantiation
rules are folded inline into `02-root-documents-spec.md §4.1.{X}`, one
appendix per domain (finance = §4.1.F, opinion = §4.1.O, epidemics =
§4.1.E, sociology = §4.1.S). (There is no separate `agent-design-finance.md`
file — that name appears in older drafts and has been retired.)

For each agent type, the author MUST:

1. Open `agent-design-skill.md` and use **§3 Section-by-Section Requirements**
   as the structural skeleton (§3.1 through §3.11).
2. Fill in every section per the handbook's section-by-section requirements.
   Use the handbook's exact section names, header levels, table column
   names, and validation requirements.
3. Apply the **domain-instantiation rules** in `02-root-documents-spec.md
   §4.1.{X}` corresponding to the target's Domain field. Pick the Theory
   Family value from §4.1.{X}.1, the real-world counterpart from
   §4.1.{X}.2, the stylized facts from §4.1.{X}.3, and the regime palette
   from §4.1.{X}.4. Instantiate the **Action Space** using the
   domain-specific row labels in §4.1.{X}.5 and apply any relabels the
   appendix specifies (e.g., finance appendix relabels `Behavioral
   Tendency` → `Market Role` and `Behavioral Adaptation by Condition` →
   `Market Contribution by Regime`).

   <details>
   <summary><strong>Finance appendix (§4.1.F) instantiation — Action-Space row labels</strong></summary>

   Instantiate the Action Space rows as: `Order types allowed`, `Price
   level rule`, `Order quantity rule`, `Order lifetime`, `Cancellation
   policy`, `Inventory constraint`, `Wealth / leverage cap`, `Stop-loss
   / kill rule`. Relabel `Behavioral Tendency` as `Market Role` and
   `Behavioral Adaptation by Condition` as `Market Contribution by
   Regime`.
   </details>

   <!-- Non-finance instantiations of the Action Space:
        Opinion (§4.1.O): {Speech types allowed, Opinion-shift rule, Broadcast frequency, Rebuttal policy, Confidence bound, Silence trigger}
        Epidemics (§4.1.E): {Contact classes allowed, Contact rate rule, Isolation policy, Vaccine acceptance, Testing frequency, Symptom-report rule}
        Sociology (§4.1.S): {Adoption action space, Adoption threshold rule, Broadcast policy, Peer selection, Abandonment trigger, Persistence policy}
        `Behavioral Tendency` and `Behavioral Adaptation by Condition` are relabelled per each appendix. -->
4. Embed the completed entry into `simulation-bases.md §4` per
   `02-root-documents-spec.md §4.0` (header levels shifted down by two:
   agent title at `###`, handbook §3.x sections at `####`, handbook
   §3.6.y sub-blocks at `######`; numbering scheme `4.{N}.x`).
5. Run the handbook's **§6 Validation Checklist** against the entry. Every
   unchecked item is a blocker. The author MUST repeat the checklist run
   three times (per the project convention encoded in
   `masim/skills/create-simulation-pipeline.md`): three consecutive PASS runs
   are required before the entry is accepted.

**Required design inputs.** Before opening the handbook skeleton, ensure the
following inputs are available from Step 1 (research) and §2.1 (environment
design) of this guide; the handbook fields cannot be filled without them.

| Input                          | Drives handbook section                                                 |
|--------------------------------|-------------------------------------------------------------------------|
| Real-world counterpart class   | §3.3 Definition and Goals (paragraph 1)                                 |
| Primary theory + DOI citation  | §3.4 Theoretical Foundation                                             |
| Calibration source per knob    | §3.4 Calibration Source / §3.7 Source column                            |
| Activation · deactivation rule | §3.5 Activation Triggers / Deactivation                                 |
| Decision signals + rationale   | §3.6.1 Decision Information Set                                         |
| Trigger and sizing formulas    | §3.6.4 Mathematical Model                                               |
| Self-imposed risk discipline   | §3.6.3 Action Space                                                     |
| Per-knob default + range       | §3.7 Parameters                                                         |
| ≥3 worked cases + 1 edge case  | §3.8 Worked Numerical Examples                                          |
| Expected stylized facts        | §3.9 Behavioral Verification and Calibration                            |
| Heterogeneity policy           | Embedded-form extension §4.{N}.7 (see `02-root-documents-spec.md §4.0`) |

If any input above is unavailable, return to Step 1 (research) before
proceeding — do not invent values to fill the handbook.

### 2.2.3 Diversity Verification

After designing all agent types, verify diversity:

| Criterion                     | Required                                       | How to Verify                                                                                                            |
|-------------------------------|------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| Time horizons                 | ≥2 distinct                                    | E.g., "high-frequency" vs "long-horizon" agent                                                                           |
| Information signals           | ≥2 distinct primary signals                    | Different agents key on different broadcast fields (finance: some use deviation, others use return or volume)            |
| Risk / sensitivity tolerances | Range from Low to Extreme                      | At least one Low and one High/Extreme                                                                                    |
| Conflicting incentives        | ≥1 pair whose actions oppose in the same round | Finance appendix example: BlockTradeBuyer buys when PrimeBrokers sell                                                    |
| Stabilizing agents            | ≥1                                             | System state would diverge to a degenerate value without one (finance instantiation: price would go to zero or infinity) |
| Destabilizing agents          | ≥2                                             | Needed for cascade / self-reinforcing dynamics                                                                           |

---

## 2.3 Communication Structure

All simulations use the same star topology:

```
Topology: Star
Center: Environment Coordinator (1 instance)
Leaves: All agent instances

Message types:
  Coordinator → Agents: broadcast (round start) — carries environment state fields
  Agents → Coordinator: action — carries the domain-specific action payload
                        (see target §4.1.{X} appendix)

Synchrony: Synchronous — all agents decide in the same round based on the same broadcast
```

<!-- Finance appendix (§4.1.F) instantiation of the topology:
     Center: Market (1 instance)
     Coordinator → Agents: broadcast — carries {price, fundamental, deviation, round, ...}
     Agents → Coordinator: order — carries {action ∈ {buy,sell,hold}, quantity, bid_price}
     Non-finance instantiations: Opinion → speech / opinion-shift payload; Epidemics → contact / isolation event; Sociology → adoption / abandonment event. -->

The topology YAML (`topology.yml`) follows the reference scenarios exactly for structure. Only the agent names change.

---

## 2.4 LLM Persona Design Principles

For each agent type, the LLM persona is derived from the handbook entry's
**Behavioral Properties** sub-block (handbook §3.6.5; embedded form
`4.{N}.5.5 Behavioral Properties`) together with the **Theoretical
Foundation** (handbook §3.4; embedded form `4.{N}.3 Theoretical Foundation`)
and the **Definition and Goals** (handbook §3.3; embedded form
`4.{N}.2 Definition and Goals`). The persona MUST NOT introduce traits or
biases that are not traceable to one of these three sources. Key rules:

1. **No phenomenon name in prompts**: The system prompt describes the
   agent's personality, not the phenomenon event that the simulation is
   trying to reproduce. Finance-appendix example: write "You are a
   leveraged carry trader" — not "You are trading during a carry trade
   unwind crisis." Non-finance analogues: describe an opinionated
   commentator, not "you are participating in a polarization cascade";
   describe a susceptible individual with a specific risk attitude, not
   "you are living through the peak of an outbreak."

2. **Persona derives from cited theory only**: Every trait in the persona
   MUST trace back to a citation in handbook §3.4 (“Calibration Source” /
   citation chain). “Overconfident” MUST cite Barber & Odean (2001) or an
   equivalent source named in the entry.

3. **Three-layer persona structure**:
   - Who they are (professional identity, experience) — from
     handbook §3.3 paragraph 1 (real-world counterpart class).
   - How they process information (cognitive style, biases, heuristics) —
     from handbook §3.6.5 Psychological profile and §3.6.1 Decision
     Information Set.
   - How they act (decision style, risk / sensitivity tolerance, response to stress) —
     from handbook §3.6.5 (Time horizon, Risk tolerance) and §3.5
     (Activation · Deactivation · Regime contribution).

4. **Canonical output format** (mandatory at end of every system prompt):
   The output payload is domain-specific — it is the JSON schema that
   `players.py` will parse into an action. The payload MUST be listed in
   the target's §4.1.{X} appendix so that every LLM prompt produces the
   same fields. Finance-appendix instantiation:

   ```
   OUTPUT FORMAT:
   First output your reasoning inside <analysis>...</analysis> tags,
   then output your decision inside <decision>...</decision> tags.
   The decision must be valid JSON:
   {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
   IMPORTANT: bid_price and quantity MUST be numeric values (e.g., 10.5), NOT expressions or formulas.
   ```

   <!-- Non-finance instantiations of the output payload:
        Opinion (§4.1.O): {"speech_act": "assert"|"defer"|"silent", "opinion": float in [-1,1], "confidence": float, "reasoning": string}
        Epidemics (§4.1.E): {"contact_action": "meet"|"avoid", "contact_count": int, "test": bool, "reasoning": string}
        Sociology (§4.1.S): {"decision": "adopt"|"reject"|"defer", "confidence": float, "reasoning": string}
        Every payload must be listed in the domain appendix; every field must be numeric literal or enum, not an expression. -->

   Never use `<think>` — always `<analysis>`.

---

## 2.5 Design Validation Before Proceeding

Before moving to Step 3, verify:

**Environment design**:
- [ ] Every coefficient in the state-update law has a specific literature citation (finance-appendix instantiation: λ, γ, σ values)
- [ ] Every broadcast field justified (no orphan fields without a consuming agent)
- [ ] All applicable environment mechanisms decided Yes/No with rationale (finance-appendix instantiation: short-selling, margin call, circuit breaker per §2.1.2)

**Agent taxonomy**:
- [ ] 4–7 agent types designed (handbook minimum 4, maximum 7 per
      `02-root-documents-spec.md §4.2`)
- [ ] AGENT_POOL reuse-or-create gate (§2.2.0) executed for every candidate;
      decisions logged in `examples/{Scenario}/simulation-build-log.md §A`
- [ ] Every agent maps to exactly one primary theory cited in
      `simulation-bases.md §2`
- [ ] At least one stabilizing and at least two destabilizing agents
- [ ] No two agents use identical information + processing combination
- [ ] Every trigger threshold has a literature-calibrated value (or explicit
      approximation), traceable via handbook §3.4 Calibration Source
- [ ] Each agent entry passes the handbook's §6 Validation Checklist
      (`agent-design-skill.md §6`) end-to-end — **three consecutive PASS
      runs** required per §2.2.2 step 5 — no unchecked items
- [ ] Every newly designed agent has been written back to
      `examples/AGENT_POOL/<domain>/<kebab-name>.md` in standalone header form
- [ ] Every referenced pool agent has passed
      `agent-icon-generation-skill.md` validation: PNG exists, pool `Icon`
      row exists, and `agent_images/design.md` contains the
      `{domain}/{agent-stem}.md` to `{domain}-{agent-stem}.png` mapping row

**Conflict check**:
- [ ] Can you describe a scenario where one agent's action opposes another's in the same round? (finance-appendix instantiation: one buys while another sells)
- [ ] Does the phenomenon still emerge if the stabilizing agents are slightly stronger? (robustness)
