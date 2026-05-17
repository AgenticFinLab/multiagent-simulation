# Runtime Failure Patterns

## Purpose

This file captures runtime lessons from full-round experiment execution. It
extends the structural revision guide with empirical failure patterns that only
appear when examples are run at scale.

Use this file after a scenario already passes the structural checks in
`07-validation-checklist.md`, and before classifying a failed full run as a
scenario failure.

---

## §1 Failure Taxonomy

| Class | Typical Evidence | Meaning | Correct Response |
|---|---|---|---|
| Config/schema bug | `KeyError`, unsupported `SimulationConfig` field, unresolved prompt ref | Project bug | Fix source config/code, rerun clean |
| Prompt/parser contract bug | Model output lacks a field later read by `players.py` | Project bug | Align prompt, parser, and player field contract |
| Special parser schema | Rumor/news/social-action fields do not match trading fields | Design-specific | Validate against the scenario parser, not canonical trading schema |
| API/account contamination | `AccountOverdue`, auth failure, quota/rate-limit burst | Invalid batch evidence | Restore API state and rerun affected rows |
| Native resource failure | `SIGABRT`, `boost::system_error`, thread creation failure, Ray OOM | Runtime resource problem | Lower concurrency/thread counts; rerun clean |
| Normal slow run | Round progress keeps advancing but wall time is long | Not failure by itself | Use progress-aware timeout and let it run |
| Stall | No new round within stall window | Abnormal runtime | Stop row, preserve logs, classify root cause |
| Numeric instability | Extreme prices, NaN/inf, explosive quantities | Level-2 quality risk | Do not patch blindly; classify and inspect scenario math |

---

## §2 Known Project Patterns And Fix Rules

### §2.1 Required Decision Fields

If code reads `decision["field"]` or `order["field"]`, the effective prompt and
parser must require or produce that field.

Examples discovered during execution:
- `provides_liquidity` was required by liquidity-sensitive markets.
- `reasoning` was read by Volmageddon API players.
- CreditCycle API modes required `action`, `bid_price`, `quantity`, and
  `reasoning` with bounded quantities.

Do not add fields mechanically. Add only fields consumed by code or required by
the scenario's parser.

### §2.2 Special Schemas

Some scenarios are not canonical trading-order schemas:
- `RumorSpread`
- `EchoChamber`
- selected custom portfolio schemas such as `EquityPremium`

These must be audited by reading `players.py` and the scenario parser. Do not
force `bid_price`, `quantity`, or `provides_liquidity` into a non-trading action
schema.

### §2.3 API Fallbacks

Malformed LLM output is different from missing config data. A scenario-local
fallback is acceptable only when:
- prompt and parser contracts are already explicit;
- fallback applies to malformed stochastic output, not missing source fields;
- transport errors retry separately from parse-contract errors;
- fatal provider errors such as auth/quota still fail loudly;
- fallback count/reason is visible for later quality review.

The successful pattern is a helper that classifies:
- parse-contract error: no repeated full LLM calls; conservative explicit hold;
- transient API error: bounded retry;
- quota/auth/config error: fail the row.

### §2.4 RAG Runtime Constraints

RAG rows can fail late with native thread/resource errors even after many
successful rounds. A row that aborts at round 155/200 with `SIGABRT` is not a
prompt or API failure.

Default RAG policy:
- one RAG worker per machine until stable;
- cap Ray CPUs with `MASIM_RAY_NUM_CPUS`;
- set BLAS thread env vars to `1`;
- use longer hard timeout than nonRAG rows;
- use stall timeout to detect no-progress hangs.

### §2.5 Progress-Aware Timeout

Do not classify a long run as failure if it still prints `Round x/y` progress.
Use:

```bash
--progress-every-rounds 20 \
--progress-poll-seconds 10
```

Recommended full-run limits:

```bash
# LLM and RuleLLM
--timeout-seconds 43200 \
--stall-timeout-seconds 3600

# Rag
--timeout-seconds 86400 \
--stall-timeout-seconds 7200
```

### §2.6 Concurrency Budget

Budget declared Ray CPUs, not just observed CPU percentages.

On a 32-vCPU machine, a safe starting point is:
- four nonRAG workers x 5 CPUs;
- one RAG worker x 8 CPUs;
- stagger starts by at least 60 seconds;
- leave a small reserve for OS/Ray overhead.

Avoid starting four windows that each export `MASIM_RAY_NUM_CPUS=16`; that
declares 64 CPUs and can overload the machine even if runs still progress.

---

## §3 Runtime Evidence Rules

### §3.1 Clean Output Directories

Every rerun must use a fresh output directory. Do not overwrite partial
timeout/native-abort directories when producing final evidence.

### §3.2 Batch Contamination

If API account/auth/quota failures appear mid-batch, rows after that timestamp
are not valid functional failures. Restore provider state and rerun.

### §3.3 Accepted Sample Standard

A full `SUCCESS` row is Level-1 execution evidence only. Final resource samples
should later be reviewed for:
- full configured round count;
- complete isolated artifacts;
- fallback rate and fallback type;
- price/volume/portfolio structural sanity;
- scenario-specific validity metrics.

### §3.4 Failure Report Minimum Fields

Each failed row report should record:
- scenario and mechanism;
- output directory;
- commit;
- API model and embedding model;
- status, exit code, duration;
- max observed round and total rounds;
- first actionable traceback or native/runtime marker;
- classification from §1;
- whether the fix should be local to one scenario or propagated by static audit.

---

## §4 When To Propagate A Fix

Propagate across rows only when static evidence proves the same contract exists:
- same field read by player/market code;
- same missing prompt/parser field;
- same framework config schema violation;
- same RAG embedding/provider shape.

Do not propagate:
- prompt strategy/persona changes;
- non-trading schema changes into trading schemas, or vice versa;
- market formula changes based on one extreme run;
- fallback behavior without observed or statically proven need.

---

## §5 Relationship To The Experiment Ledger

Detailed raw evidence should stay in local experiment assets, for example:

`EXPERIMENT/fix-scenarios-20260515/knowledge/bugfix-ledger.md`

This guide should only contain stable patterns that are reusable across future
example revisions.
