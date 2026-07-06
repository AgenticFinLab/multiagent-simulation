# ArchegosCollapse — Pipeline Build Log

## §0 Meta

| Field | Content |
|-------|---------|
| Name | ArchegosCollapse |
| Target file | Legacy example: no upstream `{domain}-{scenario}.md` was present before this normalization pass |
| Target spec | masim/skills/define-simulation-scenario-skill.md (not available for this legacy example) |
| Domain | finance |
| Pipeline | masim/skills/create-simulation-pipeline.md |
| Status | draft |

## §A AGENT_POOL Reuse-or-Create Gate Log

| Candidate archetype | Stage reached | Outcome | Pool file |
|---------------------|---------------|---------|-----------|
| ConcentratedFund | 2 | new | examples/AGENT_POOL/finance/concentrated-fund.md |
| PrimeBroker1 | 2 | new | examples/AGENT_POOL/finance/prime-broker-first-mover.md |
| PrimeBroker2 | 2 | new | examples/AGENT_POOL/finance/prime-broker-delayed-liquidator.md |
| BlockTradeBuyer | 2 | new | examples/AGENT_POOL/finance/block-trade-buyer.md |
| InformationTrader | 2 | new | examples/AGENT_POOL/finance/information-trader.md |

Gate rationale: existing `examples/AGENT_POOL/finance/*.md` includes generic behavioral, liquidity-provider, momentum, noise, and rational-updater agents. No existing pool file matched at least five Summary fingerprint rows plus the Archegos-specific mechanisms: TRS hidden leverage, prime-broker collateral liquidation race, delayed execution haircut, or liquidation-signal predatory trading.

## §B Research Notes (extends legacy simulation-bases.md §2 and §8)

The normalization pass reused citations already present in `simulation-bases.md`: Becketti (2021), FSB (2022), Gorton & Metrick (2012), Grossman & Miller (1988), Kyle (1985), Barber & Odean (2001), Brunnermeier & Pedersen (2005), Shleifer & Vishny (1997), and Hasbrouck (1991).

## §C Open Questions and Risks

- Defer: legacy example lacks the upstream target file required by the current create-simulation pipeline. This pass records the absence rather than inventing a locked target contract.
- Defer: several legacy citations are regulatory/report URLs rather than DOI-bearing peer-reviewed papers; they are retained because they are primary sources for the historical Archegos event.

## §D Build Log

| Phase | Date | Outcome | Reviewer | Notes |
|-------|------|---------|----------|-------|
| Structure check | 2026-06-30 | partial pass | Codex | Added `simulation-build-log.md`; upstream target file remains absent as legacy gap. |
| AGENT_POOL gate | 2026-06-30 | pass | Codex | All five agents classified as `new`; pool files created in `examples/AGENT_POOL/finance/`. |
| Root §4 normalization | 2026-06-30 | pass | Codex | Replaced legacy §4 with handbook-aligned embedded form and pool source links. |
| Polish supersession | 2026-07-01 | superseded | QoderWork | Superseded by polish audit; polish trail lives in target §1 Meta CHANGELOG (`finance-archegos-collapse.md`) + git history. This build-log is retained for historical reference only and is not maintained by the polish pipeline. |
| Round-2 polish supersession | 2026-07-06 | superseded | QoderWork | Superseded by Round-2 polish audit under the evaluation-first baseline (`masim/evaluation/README.md`, Pass 2 Analysis Migration Rule); Round-2 trail lives in target §1 Meta CHANGELOG + git history (`polish(archegos): step {0..closeout}` commits). Build-log remains historical reference only. |
