# AsianFinancialCrisis — Pipeline Build Log

## §0 Meta

| Field       | Content |
|-------------|---------|
| Name        | AsianFinancialCrisis |
| Target file | examples/AsianFinancialCrisis/finance-asian-financial-crisis.md |
| Target spec | masim/skills/define-simulation-scenario-skill.md (v1.2) |
| Domain      | finance |
| Pipeline    | masim/skills/create-simulation-pipeline.md |
| Status      | released |

## §A AGENT_POOL Reuse-or-Create Gate Log

| Candidate archetype | Stage reached | Outcome | Pool file |
|---------------------|---------------|---------|-----------|
| hot-money-funder | 2 | new approved | examples/AGENT_POOL/finance/hot-money-funder.md |
| contagion-trader | 3 | fork approved | examples/AGENT_POOL/finance/contagion-trader.md (parent family: examples/AGENT_POOL/finance/momentum-trader.md) |
| imf-rescuer | 2 | new approved | examples/AGENT_POOL/finance/imf-rescuer.md |
| value-contrarian | 3 | reuse with scenario override approved | examples/AGENT_POOL/finance/contrarian-trader.md |
| noise-trader | 3 | reuse approved | examples/AGENT_POOL/finance/noise-trader.md |

Gate rationale: the current repository already had a complete scenario-local AsianFinancialCrisis implementation. The gate was re-run against `examples/AGENT_POOL/finance/`: `noise-trader` and `contrarian-trader` are reusable, `momentum-trader` is only a family match for the contagion seller because the implemented mechanism combines deviation and cross-border return momentum, and no existing pool file exactly matched hot-money sudden-stop funding or IMF-style official rescue. This replay wrote new/fork standalone pool files for the non-reused archetypes.

## §B Research Notes (extends target §4 - §6)

### §B.1 Core Theories

- Radelet & Sachs (1998), DOI `10.1353/eca.1998.0009`: verifies sudden-stop / hot-money reversal mechanisms and Asian crisis currency depreciation ranges.
- Kaminsky & Reinhart (1999), DOI `10.1257/aer.89.3.473`: verifies twin-crisis and contagion framing, crisis-threshold timing, and banking / balance-of-payments interaction.
- Corsetti, Pesenti & Roubini (1999), DOI `10.1016/S0014-2921(98)00111-0`: verifies Asian crisis model, policy intervention, and moral-hazard / conditional support framing.
- Brunnermeier & Pedersen (2009), DOI `10.1093/rfs/hhn098`: verifies funding-liquidity feedback and contrarian liquidity supply after fire-sale dislocation.
- Black (1986), DOI `10.1111/j.1540-6261.1986.tb04513.x`: verifies noise-trading background liquidity and volatility.

### §B.2 Empirical Stylized Facts

F1-F5 in target §5 map to `analysis-bases.md §2`: maximum drawdown, crisis onset round, crisis velocity, return autocorrelation, and rescue activation / post-rescue slope. The deterministic Rule analysis script computes the first four directly and loads records for rescue timing diagnostics.

### §B.3 Historical Events

Target §6.1 is the 1997 Asian Financial Crisis, anchored on the Thai baht depeg on 1997-07-02 and regional spread through Indonesia, Korea, Malaysia, and other Asian markets. The scenario maps short-term creditors to `hot-money-funder`, regional common-creditor pressure to `contagion-trader`, IMF programs to `imf-rescuer`, long-horizon private capital to `value-contrarian`, and background order flow to `noise-trader`.

### §B.4 Canonical Role Taxonomy

| Candidate archetype | Theory family | Real-world counterpart | Domain role | Primary signals | Pipeline confirmation |
|---------------------|---------------|------------------------|-------------|-----------------|-----------------------|
| hot-money-funder | Sudden Stops (§4.1) | hedge fund or foreign short-term portfolio creditor | Destabilising | price, deviation, cash | confirmed |
| contagion-trader | Contagion (§4.2) | active cross-border hedge fund or regional portfolio manager | Destabilising | price, prev_price, deviation | confirmed |
| imf-rescuer | Policy Intervention (§4.3) | official sector crisis lender or sovereign stabilisation fund | Stabilising | price, deviation, cash | confirmed |
| value-contrarian | Liquidity / Funding (§4.4) | long-horizon value fund or distressed-asset investor | Stabilising | price, fundamental, deviation | confirmed |
| noise-trader | Noise Trading (§4.5) | uninformed retail or liquidity-motivated trader | Context-dependent | price, cash, position | confirmed |

### §B.5 Parameter Estimates

Target §9 parameter seeds are echoed in `simulation-bases.md §3`, `simulation-bases.md §4`, `analysis-bases.md §2`, and `configs/AsianFinancialCrisis/{Rule,LLM,RuleLLM,Rag}/players.yml`. The only normalization-only row is `fundamental value`.

## §C Open Questions and Risks

- Defer: full LLM, RuleLLM, and Rag execution requires live model or retrieval provider credentials; deterministic Rule is the required successful smoke run for this replay.
- Defer: full 200-round execution for all four variants is not run in this bounded pass; deterministic Rule smoke execution is the required successful run.

## §D Build Log

| Phase | Date | Outcome | Reviewer | Notes |
|-------|------|---------|----------|-------|
| Phase 0 - Target file load | 2026-07-05 | pass | Codex | Generated `finance-asian-financial-crisis.md` via define-simulation-scenario-skill fresh mode; §11 checked three times; pipeline locked target. |
| Phase 1 - Research | 2026-07-05 | pass | Codex | Verified core DOI anchors and mapped target §4-§6 and §9 into research notes. |
| Phase 2 - Role planning | 2026-07-05 | pass | Codex | Confirmed five target §7 archetypes, signals, roles, and diversity coverage. |
| Phase 3 - AGENT_POOL gate | 2026-07-05 | pass | Codex | Reuse/fork/new decisions recorded; new/fork standalone pool files written back under `examples/AGENT_POOL/finance/`. |
| Phase 4 - Scenario build | 2026-07-05 | pass | Codex | Root docs, variant docs, configs, code, and analysis scripts present for Rule, LLM, RuleLLM, and Rag; runner and analysis path guards repaired. |
| Phase 5 - Scenario 3-PASS review | 2026-07-05 | pass | Codex | Python compile clean; YAML parses clean; stale reference sweep clean after edits. |
| Phase 6 - Execution and final review | 2026-07-05 | pass | Codex | Fresh Rule smoke run completed 5/5 rounds from repository root; analysis loaded communication outputs and generated plots. The 5-round calibration report was INVALID with 44.8% fit, which is expected for a smoke-scale run and not a runtime blocker. |
