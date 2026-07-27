# Repository and Config Gates

## Purpose

Use these gates to prove that each execution machine has the intended code and
that every planned scenario-mode row resolves through the MASim config system
before spending runtime or API budget.

## Gate 1: Repository And Environment

On every execution machine:

```bash
cd <project-root>/multiagent-simulation
git rev-parse --short HEAD
git status --short
source <conda-root>/etc/profile.d/conda.sh
conda activate LMSim
python -c "import masim, streamlit; print('imports OK')"
```

Pass criteria:

- Commit is the intended one.
- Worktree is clean or documented.
- `masim` and `streamlit` import cleanly.
- API keys are set when API modes or RAG are scheduled.

## Gate 2: Row Discovery And Clean Output

For each row:

```bash
python examples/<Scenario>/<Mechanism>/run_<scenario_lower>_<mechanism_lower>.py \
  -c configs/<Scenario>/<Mechanism>/simulation.yml \
  --dry-run
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
