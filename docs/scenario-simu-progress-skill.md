# Scenario Simulation Progress Generator

> **Location**: `docs/scenario-simu-progress-skill.md`
> **Output**: `docs/simulation-progress/examples/{ScenarioName}.md`

## Trigger

When asked to generate simulation progress for a scenario, execute the steps below.

## Step 1 — Validate Scenario

1. Check `examples/{ScenarioName}/` exists and contains `Rule/` player code.
2. If not found, report error and stop.

## Step 2 — Read Scenario Docs

Read the following files to fully understand the scenario before building the tracker.

### 2a. Design Documents (in `examples/{ScenarioName}/`)

| File | Purpose |
|------|----------|
| `finance-*.md` or `*-scenario.md` | Phenomenon definition, research goals, participant archetypes |
| `simulation-bases.md` | §4 Investor Taxonomy, §6 Parameter Table (values + sources + sensitivity), §7 Round Structure, §10 Equilibrium |
| `analysis-bases.md` | §2 Core Metrics Catalogue (formulas, calibration targets), §8 Registered Metrics |

### 2b. Config Files (in `configs/{ScenarioName}/Rule/`)

| File | Extract |
|------|----------|
| `simulation.yml` | `total_rounds`, `seed`, `record_path` |
| `players.yml` | All agent types, `num_instances`, key `extras` parameters |
| `topology.yml` | `type`, hub/sources, edge list |

Also check which variants exist: `Rule/`, `LLM/`, `RuleLLM/`, `Rag/`.

### 2c. Cross-Verification

- Every parameter in Agent Inventory must cite its `simulation-bases.md §6` source.
- Every agent type must cite its `simulation-bases.md §4` subsection.
- If a param exists in `players.yml` but not in `§6`, flag it.
- If `§6` marks a parameter as **High** sensitivity, it should appear in Tunable Axes.

## Step 3 — Build Baseline Summary

Write a **Baseline** section containing:

```
> **Default**: {rounds} rounds, {total_agents} players, {topology} topology, seed {seed}
> **Variants**: ☐ Rule · ☐ LLM · ☐ RuleLLM（Rag 暂不执行）
```

### Agent Inventory Table

| ID | Agent | ×N | Key Params | Source |
|----|-------|----|------------|--------|

- **ID**: Short key from `players.yml` (strip `rule_` prefix → `AT`, `HA`, `RU`, `MT`, `NT`, `DT`, `CT`, `FA`, `LP`). Use 2-letter abbreviation derived from agent class name.
- **Agent**: Display name from `players.yml` `name:` field.
- **×N**: `num_instances` value.
- **Key Params**: Non-trivial extras (skip `initial_cash`, `initial_position`, `custom_state_hot_limit`).
- **Source**: `simulation-bases.md` §4.x subsection number.

## Step 4 — Identify Structural Dimensions

From the simulation config, list only **structural** dimensions that can be varied (NOT agent behavioral params):

| Dimension | Default | Range (≥ default) |
|-----------|---------|-------------------|

Typical dimensions: rounds, agent scale, P₀ (initial conditions), topology.
Do NOT list agent behavioral params (α, w, η, λ_LA, τ, etc.) — these are calibrated and fixed.

## Step 5 — Design Experiments

### Rules

1. **Increase only** — never remove agents, reduce counts, or decrease parameters below baseline. All increases must be reasonable and effective.
2. **No agent parameter sweeps** — agent behavioral params (α, w, η, λ_LA, τ, etc.) are calibrated from academic literature and already optimal. Do NOT vary them. Only vary **structural** dimensions: agent counts, rounds, scale, topology, initial conditions (P₀).
3. **Systematic sweeps** — vary one structural dimension at a time, hold others at default.
4. **Composite** — combine 2+ increases for interaction experiments.
5. **Scale** — multiply all agent instances uniformly.
6. **Variants** — every config runs across Rule / LLM / RuleLLM.

### Experiment Categories (pick relevant ones, each table must be thorough)

Each category gets its **own table** with enough rows to fully cover the dimension. Don't just include 2-3 rows per table — aim for comprehensive coverage:

- **Agent Amplify**: cover every agent type that exists (if 9 types → ≥9 rows, with ×2 and ×4 where applicable).
- **Mispricing**: ≥4 P₀ values with increasing deviation from fundamental value F.
- **Time Scale**: ≥3 round counts (e.g. 400 / 1000 / 2000).
- **Scale**: ≥3 uniform multipliers (×2 / ×4 / ×8).
- **Composite**: ≥5 combinations testing different interaction hypotheses (bias+bias, bias+corrective, triple combos).
- **Topology**: all supported topology types beyond baseline.

### Abbreviation Conventions

Use short parameter names in Config Change column:
- `alpha` → α
- `initial_price` → P₀
- `total_rounds` → rounds
- `num_instances` → ×N
- `price_impact` → λ
- `mean_reversion` → γ
- `noise_std` → σ
- `base_position_size` → b
- Arrow notation: `×2→×4` (increase), `200→50` (decrease rounds), `0.3→0.5` (param sweep)

## Step 6 — Assign Tasks

### Team

| Person | Role | Config Budget |
|--------|------|---------------|
| Sijia | Lead | 1 config (baseline only) |
| Wenyou | Executor | ~⅓ of remaining |
| Zihan | Executor | ~⅓ of remaining |
| Ziqi | Executor | ~⅓ of remaining |

### Assignment Logic

- Group related experiments together (same sweep → same person).
- Sijia only gets E01 baseline.
- Distribute remaining configs evenly across Wenyou / Zihan / Ziqi.

## Step 7 — Generate Output

Write to `docs/simulation-progress/examples/{ScenarioName}.md` with this structure:

```markdown
# {ScenarioName} — Experiment Progress

> **Default**: ...
> **Variants**: ☐ Rule · ☐ LLM · ☐ RuleLLM（Rag 暂不执行）

---

## Baseline

### Agent Inventory

| ID | Agent | ×N | Key Params | Source |
|----|-------|----|------------|--------|
...

### Tunable Axes (structural only, no agent params)

| Dimension | Default | Range (≥ default) |
|-----------|---------|-------------------|
...

---

## E1 — Agent Amplify

| ID | Config Change | Rounds | Agents | Variants | Assignee |
|----|---------------|--------|--------|----------|----------|
...

## E2 — Param Sweep

| ID | Config Change | Rounds | Agents | Variants | Assignee |
|----|---------------|--------|--------|----------|----------|
...

## E3 — Mispricing
...

## E4 — Time Scale
...

## E5 — Scale
...

## E6 — Composite
...

## E7 — Topology
...
```

### Rules for tables
- Each experiment category gets its **own table** (one `## E{n}` section per category).
- Every table has a `Variants` column: `☐R ☐L ☐RL`.
- When done, change `☐` to `✓` (e.g. `✓R ✓L ☐RL`).
- Do NOT add Assignment Summary or Metrics sections.

## Step 8 — Verify

After generation, verify:
1. Every category table has a Variants column.
2. No agent removal experiments (increase only).
3. All agent IDs referenced exist in the Agent Inventory.
4. No duplicate config changes.
5. All Agent Inventory params cite `simulation-bases.md §6`.
6. All Tunable Axes entries cite `§6` sensitivity rating.
