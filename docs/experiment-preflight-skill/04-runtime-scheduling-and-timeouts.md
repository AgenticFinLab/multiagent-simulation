# Runtime Scheduling and Timeouts

## Purpose

Use this file to plan tmux windows, Ray CPU budgets, stagger timing, and timeout
policy after the row/config/API gates have passed.

## Runtime Scheduling

Budget declared Ray CPUs per machine.

Safe starting plan for a 32-vCPU machine:

- nonRAG: up to four windows x 5 CPUs;
- RAG: one window x 8 CPUs;
- stagger starts by at least 60 seconds;
- do not add windows if load is already high or old runs are active.

Avoid repeating the historical overcommit pattern: four windows each exporting
`MASIM_RAY_NUM_CPUS=16` on one 32-vCPU machine.

## Timeout Policy

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
