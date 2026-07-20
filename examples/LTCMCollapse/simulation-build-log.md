# LTCMCollapse - Pipeline Build Log

## §0 Meta

| Field | Content |
|---|---|
| Name | LTCMCollapse |
| Target file | examples/LTCMCollapse/finance-ltcm-collapse.md |
| Target spec | masim/skills/define-simulation-scenario-skill.md v1.2.0 |
| Domain | finance |
| Pipeline | masim/skills/polish-simulation-pipeline.md |
| Status | locked (upgraded to `released` on closeout) |

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

## §D Build Log

| Phase | Date | Outcome | Reviewer | Notes |
|---|---|---|---|---|
| Preflight | 2026-07-20 | pass | Codex | Worktree and scenario inventory audited; Case B target gate selected. |
| Step 0 | 2026-07-20 | pass | Codex | Target created by define skill and validated three times. |
| Step 1 | 2026-07-20 | pass | Codex | Research and analysis anchors repaired and traced. |
| Step 2 | 2026-07-20 | pass | Codex | Five profiles, four icons, and embedded agent contracts pass audits. |
| Step 3 | 2026-07-20 | pass | Codex | Four canonical config families parse with prefix, topology, and parity checks. |
| Step 4 | 2026-07-20 | pass | Codex | Target revise mode, implementation repair, compile/import checks, and five-agent behavior probes completed. |
