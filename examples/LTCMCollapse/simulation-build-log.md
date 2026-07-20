# LTCMCollapse - Pipeline Build Log

## §0 Meta

| Field | Content |
|---|---|
| Name | LTCMCollapse |
| Target file | examples/LTCMCollapse/finance-ltcm-collapse.md |
| Target spec | masim/skills/define-simulation-scenario-skill.md v1.2.0 |
| Domain | finance |
| Pipeline | masim/skills/polish-simulation-pipeline.md |
| Status | released |

## §A AGENT_POOL Reuse-or-Create Gate Log

| Candidate archetype | Stage reached | Outcome | Pool file |
|---|---|---|---|
| convergence-arbitrageur | exact-name audit | reused and upgraded | examples/AGENT_POOL/finance/convergence-arbitrageur.md |
| leverage-trader | exact-name audit | reused and upgraded | examples/AGENT_POOL/finance/leverage-trader.md |
| risk-manager | exact-name audit | reused and upgraded | examples/AGENT_POOL/finance/risk-manager.md |
| liquidity-provider | exact-name audit | reused | examples/AGENT_POOL/finance/liquidity-provider.md |
| central-bank | exact-name audit | reused and upgraded | examples/AGENT_POOL/finance/central-bank.md |

## §B Research Notes (extends target §4 - §6)

### B.1 Core Theories

Five theory blocks were verified against stable DOI or official-report sources: limits to arbitrage, leverage cycles, procyclical risk management, funding-market liquidity spirals, and crisis coordination.

### B.2 Empirical Stylized Facts

The normalized acceptance ranges are 5%-60% for maximum deviation and drawdown, 1%-12% for per-round return volatility, finite recovery half-life after a negative trough, and strictly positive prices.

### B.3 Historical Events

The 1998 Russian default and subsequent LTCM rescue window provide the trigger, amplification, and coordination chronology. The President's Working Group report is the official primary anchor.

### B.4 Agent Taxonomy

All five target archetypes are confirmed across the target, pool profiles, icons, root documentation, four variant configurations, and implementation classes.

### B.5 Parameter Estimates

Step 4 behavior probes added an explicit order-depth normalization, process-independent seed, positive price floor, bounded four-round identification stimulus, mark-to-market leverage equity, and bounded intervention size. All are traced in target §9 and simulation-bases.md §6.

## §C Open Questions and Risks

| Issue | First raised in phase | Status |
|---|---|---|
| Formal Rag execution requires embedding resources and is outside Wenyou's current run scope. | Step 0 | deferred: static/import validation only per target §10 |
| Two stale Ray clusters consumed local resources and delayed imports. | Step 4 | resolved: stopped before formal LTCMCollapse execution |
| Investor orders were returned only inside `Action.payload`, so the framework did not dispatch them to the market. | Step 9 | resolved: every variant now also places canonical outbound messages in the decision payload |
| Convergence-arbitrageur capacity fall-through converted a full long position into an unintended sell. | Step 9 | resolved: positive and negative deviation branches are mutually exclusive and capacity-boundary probes pass |
| Initial leveraged equity equalled the maintenance threshold, allowing ordinary noise to trigger early deleveraging. | Step 9 | resolved through define-skill revise mode: initial equity includes an explicit maintenance buffer; three §11 re-validations passed |
| A Windows checkpoint conflict caused one interrupted run and state-discontinuous resume output. | Step 9 | rejected and replaced: Ray/output were cleaned and a fresh uninterrupted 200-round run passed continuity and visual review |
| Repo-wide naming audit reports 141 issues in other scenarios. | Step 10 | pre-existing and out of scope; LTCMCollapse scenario-local audit has zero issues |

## §D Build Log

| Phase | Date | Outcome | Reviewer | Notes |
|---|---|---|---|---|
| Preflight | 2026-07-20 | pass | Codex | Worktree and scenario inventory audited; Case B target gate selected. |
| Step 0 | 2026-07-20 | pass | Codex | Target created by define skill and validated three times. |
| Step 1 | 2026-07-20 | pass | Codex | Research and analysis anchors repaired and traced. |
| Step 2 | 2026-07-20 | pass | Codex | Five profiles, four icons, and embedded agent contracts pass audits. |
| Step 3 | 2026-07-20 | pass | Codex | Four canonical config families parse with prefix, topology, and parity checks. |
| Step 4 | 2026-07-20 | pass | Codex | Target revise mode, implementation repair, compile/import checks, and five-agent behavior probes completed. |
| Step 5 | 2026-07-20 | pass | Codex | Environment, round, communication, parameter, diversity, and behavior-boundary contracts were cross-checked against the locked target. |
| Step 6 | 2026-07-20 | pass | Codex | Variant code compiles, uses configuration-owned parameters, preserves direct decision fields, fails fast, and shares evaluation loaders. |
| Step 7 | 2026-07-20 | pass | Codex | Rule analysis uses shared evaluation utilities, stress-window volatility, five hard validation gates, standard outputs, and reusable variant imports. |
| Step 8 | 2026-07-20 | pass | Codex | Root documents and all eight per-variant documents meet required heading counts, trace formulas, and record actual validation scope. |
| Step 9 | 2026-07-20 | pass | Codex | Fresh uninterrupted Rule run completed 200 rounds; 10 agents each recorded 200 actions; all five gates scored 1.0 and visual continuity passed. |
| Step 10 | 2026-07-20 | pass | Codex | Sixteen YAML files, twenty Python files, four imports, LLM/RuleLLM setup and bounded behavior, Rag static contracts, five profiles, scenario naming, and four-variant WebUI discovery all passed. |
