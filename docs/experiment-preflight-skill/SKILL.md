---
name: experiment-preflight-check
description: Use when preparing full-round MASim experiment batches, especially before launching tmux jobs across machines or rerunning failed scenario-mode rows.
---

# Experiment Preflight Check

## Purpose

Use this skill before launching any full configured-round experiment batch. It
turns previous failure experience into a repeatable gate so broad runs do not
fail from known config, prompt, API, or scheduling issues.

This skill is narrower than `docs/example-revision-guide/`: that guide repairs
examples; this skill decides whether selected rows are ready to run now.

## Required Inputs

Prepare these before checking:

- Git commit/branch expected on each machine.
- Row list as `Scenario__Mechanism`.
- Machine plan: tmux session names, CPU budget per session, RAG/nonRAG split.
- Output directories.
- API/env expectations: `ARK_API_KEY`, `HUNYUAN_API_KEY`, `MINERU_API_KEY`.
- Current accepted-success ledger, so already accepted rows are not rerun.

## Gate 1: Repository And Environment

On every execution machine:

```bash
cd /root/autodl-tmp/AgenticFinLab/multiagent-simulation
git rev-parse --short HEAD
git status --short
source /root/miniconda3/etc/profile.d/conda.sh
conda activate LMSim
source scripts/env.sh
python scripts/check_environment.py
```

Pass criteria:

- Commit is the intended one.
- Worktree is clean or documented.
- `check_environment.py` passes.
- API keys are set when API modes or RAG are scheduled.

## Gate 2: Row Discovery And Clean Output

For each row:

```bash
python scripts/run_example_matrix.py \
  --dry-run \
  --scenario <Scenario> \
  --mechanism <Mechanism> \
  --isolated-artifacts \
  --conda-bin /root/miniconda3/bin/conda \
  --output-dir <preflight-output>/rows/<Scenario>__<Mechanism>
```

Pass criteria:

- Every planned row dry-runs to exactly one experiment.
- Runner path and config snapshot are produced.
- Final output directories for the real run do not already exist, unless the
  rerun policy explicitly says they are disposable.

## Gate 3: Config And Class Contract

Check every planned row:

- `configs/<Scenario>/<Mechanism>/simulation.yml` exists and loads.
- Runner `examples/<Scenario>/<Mechanism>/run_*.py` exists.
- Every configured player class imports through `masim.utils.config.load_class`.
- `total_rounds` is the intended full configured count, normally 200.
- `persona.yml` uses the framework schema expected by the current loader.
- `topology.yml` keys match expanded player identities.
- No unsupported top-level `simulation.yml` keys such as `llm`.

If this gate fails, fix config/code first. Do not start the batch.

## Gate 4: API Prompt And Parser Contract

For API rows (`LLM`, `RuleLLM`, `Rag`), inspect effective prompts and players:

- Every `extras.llm.sys_message` and `extras.llm.user_message` reference
  resolves, unless the player intentionally uses class-level or dynamic prompts.
- `lm_name` is the intended model, currently
  `ark/doubao-seed-2-0-mini-260428`.
- Fields read as `decision["field"]` or `order["field"]` are produced by the
  parser or required by the effective prompt.
- Trading rows request exactly the trading fields consumed by code:
  `action`, `bid_price` if used, `quantity`, `reasoning`, and scenario-specific
  extras such as `provides_liquidity` only when consumed.
- Current-market quantity schemas that explicitly do not consume price fields
  must use a quantity-order parser and must not reuse a canonical parser that
  requires `bid_price`.
- Dynamic user prompts built inside `players.py` must not narrow or contradict
  the schema already stated in system prompts. The most recent failure pattern
  was a correct system prompt but a dynamic user prompt that only requested
  `action` and `quantity`, causing missing `reasoning` at order construction.
- Fallback decisions must contain the same fields later recorded into orders.
  A fallback that returns only `action` and `quantity` is not valid when the
  order writes `decision["reasoning"]` or other consumed fields.
- Special schemas such as `RumorSpread` and `EchoChamber` are checked against
  their scenario parser; do not force canonical trading fields into them.

If one row reveals a shared missing field, run a static audit over related rows
before patching only the observed row.

Run the tracked contract regression before launching API batches:

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate LMSim
source scripts/env.sh
python scripts/test_scenario_contracts.py
```

## Gate 5: RAG Assets And Embedding

For each `Rag` row:

- `knowledge` and `private_knowledge.rag` resolve to usable directories.
- `examples/document-sources/MinerU_processed` exists and has files.
- `examples/document-sources/rag_index` exists or can be built.
- Embedding config is:

```yaml
embed_type: "litellm"
embed_model: "openai/hunyuan-embedding"
embed_api_key: "{{ HUNYUAN_API_KEY }}"
```

- Hunyuan key is set on the machine.

RAG rows should be launched more conservatively than nonRAG rows because native
thread aborts can appear after many successful rounds.

## Gate 6: Runtime Scheduling

Budget declared Ray CPUs per machine.

Safe starting plan for a 32-vCPU machine:

- nonRAG: up to four windows x 5 CPUs;
- RAG: one window x 8 CPUs;
- stagger starts by at least 60 seconds;
- do not add windows if load is already high or old runs are active.

Avoid repeating the historical overcommit pattern: four windows each exporting
`MASIM_RAY_NUM_CPUS=16` on one 32-vCPU machine.

## Gate 7: Timeout Policy

Use full configured rounds. Do not run 20-round canaries as final samples.

Recommended full-run flags:

```bash
# LLM / RuleLLM
--timeout-seconds 43200 \
--stall-timeout-seconds 3600 \
--progress-poll-seconds 10 \
--progress-every-rounds 20

# Rag
--timeout-seconds 86400 \
--stall-timeout-seconds 7200 \
--progress-poll-seconds 10 \
--progress-every-rounds 20
```

Long runtime is acceptable while rounds progress. A stall is abnormal when no
new round appears inside the stall window.

## Gate 8: Failure Classification Before Fixing

When a row fails, classify first:

| Evidence | Class | Action |
|---|---|---|
| `KeyError`, unresolved prompt, unsupported config field | config/contract bug | fix source and rerun clean |
| malformed LLM output without decision JSON | prompt/parser/API-output contract | strengthen contract or scenario-local counted fallback |
| auth/quota/account overdue | API contamination | restore provider state and rerun affected rows |
| `SIGABRT`, thread resource error, Ray OOM | runtime resource | reduce concurrency/thread caps |
| no round progress inside stall window | stall | preserve logs and inspect setup/runtime boundary |
| extreme price/NaN/inf with exit 0 | quality risk | do Level-2 quality review; do not call it a code success issue |

Do not patch strategy, persona, or market logic just to make a row finish
unless the root cause is proven to be a bug rather than intended scenario
dynamics.

## Launch Readiness Checklist

Start the batch only when all are true:

- [ ] Row list excludes accepted success samples unless a rerun is intentional.
- [ ] Every row dry-runs to one experiment.
- [ ] Config/class/prompt/RAG checks pass.
- [ ] Output directories are clean.
- [ ] API keys and embedding assets are present.
- [ ] Machine CPU budget is documented and not overcommitted.
- [ ] Timeout/stall flags are included.
- [ ] tmux session names are unique.
- [ ] RAG rows are limited to the planned RAG concurrency.
- [ ] Known issue classes from
  `docs/example-revision-guide/08-runtime-failure-patterns.md` are reviewed.

## Post-Run Minimum Review

After a batch completes:

- Copy only `SUCCESS` rows with complete isolated artifacts into the resource
  pack.
- Rebuild the success ledger.
- For failed rows, record status, exit code, duration, max round, first
  actionable error, and classification.
- For success rows, later run Level-2 checks for round count, structural fields,
  fallback rate, price/volume/portfolio sanity, and RAG retrieval health.
- Treat runner `SUCCESS` as provisional if logs contain Ray unhandled errors,
  tracebacks, fatal/native abort text, or heavy parser fallback. Such rows
  should stay out of the resource pack until repaired and rerun.
