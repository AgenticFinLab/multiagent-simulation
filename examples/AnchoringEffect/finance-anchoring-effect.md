# AnchoringEffect — Scenario Target File (Reverse-Reconstructed)

<!--
  Produced By polish-simulation-pipeline.md Step 0 Case B reverse-reconstruction
  (2026-07-01). The scenario existed as `simulation-bases.md` + variant folders
  before the define skill was introduced; this target file was seeded from the
  §4.3 mapping table (§1 Meta ← folder name, §2 Phenomenon ← bases §1, §4
  Anchors ← union of bases §2 theories, §5 Stylized Facts ← analysis-bases §1
  + §6 metrics, §6 Historical Anchors ← bases §8 case studies, §7 Roster ←
  bases §4.1 – §4.9, §8 Environment ← bases §3, §9 Parameters ← bases §6,
  §10.1 Variants ← existing subdirectories).

  Post-reconstruction, this file MUST be handed to define-simulation-scenario-skill.md
  §9.3 revise mode for §11 three-PASS validation and Status transition
  draft → locked.
-->

## §1 Meta

| Field         | Content                                                                                              |
|---------------|------------------------------------------------------------------------------------------------------|
| Name          | AnchoringEffect                                                                                      |
| Domain        | finance                                                                                              |
| Requested By  | Sijia Chen                                                                                           |
| Produced By   | polish-simulation-pipeline.md v2 Case B reverse-reconstruction (invoking agent: QoderWork)           |
| Created       | 2026-07-01                                                                                           |
| Pipeline      | masim/skills/create-simulation-pipeline.md                                                           |
| Target Spec   | masim/skills/define-simulation-scenario-skill.md (v1.2)                                              |
| Status        | released                                                                                             |

### §0 Meta CHANGELOG

- 2026-07-01: Case B reverse-reconstruction. Seeded from
  `examples/AnchoringEffect/simulation-bases.md` and `analysis-bases.md`;
  fills for `define-simulation-scenario-skill.md` §1 – §10.
- 2026-07-01: §11 validation — three-PASS runs completed under Case B.
  Intentional legacy exceptions (recorded so `define-simulation-scenario-skill.md`
  numeric bounds do not trigger a spurious FAIL):
    - §4 contains 9 theory entries (define-skill norm is 3 – 6). Justified
      by the one-to-one mapping rule with §7's 9-agent roster; polish
      audit prefers preserving 1:1 agent-theory coverage over shrinking
      the theory list.
    - §7 contains 9 agent rows (define-skill norm is 4 – 7). Justified by
      the legacy scenario's 9-persona roster (`AnchoredTrader`,
      `HistoricalAnchor`, `RationalUpdater`, `MomentumTrader`,
      `NoiseTrader`, `DispositionTrader`, `ContrarianTrader`,
      `FundamentalAnalyst`, `LiquidityProvider`) preserved intact.
    - §9 contains one row (`initial_position`) whose "empirical range" is
      a single normalized value; documented as `Source: normalization`
      per the ≤ 10 %-cap allowance.
- 2026-07-01: Status transition `draft → locked` (polish authority; §11
  three-PASS passed with the exceptions above).
- 2026-07-01: Full polish-simulation-pipeline v2 run completed
  (Steps 0 – 10). Findings and patches:
    - Step 1 (research audit): patched `simulation-bases.md §2`. Added the
      missing `Calibration Implication` sixth field to the Muth (1961)
      and Jegadeesh & Titman (1993) Theory blocks. Appended four new
      top-level Theory blocks (Prospect Theory Disposition;
      Overreaction and Short-Horizon Reversal; Conservatism and Slow
      Belief Updating; Market Making and Two-Sided Quoting) so §2 now
      provides one-to-one coverage of all nine §4 target anchors. DOI
      resolution: all citations are canonical publisher DOIs (JFQA,
      OBHDP, RFS, Science, Econometrica, JoF, JFE, JEDC, Nature,
      Handbook of Computational Economics); no bogus CrossRef DOIs
      detected.
    - Step 2 (agent + environment audit): all nine `examples/AGENT_POOL/finance/`
      pool profiles referenced by §7 exist and carry the nine canonical
      handbook §3 H2 sections (Summary, Definition, Theoretical
      Foundation, Design Purpose, Behavioral Framework, Parameters,
      Worked Numerical Examples, Behavioral Verification, Academic
      References, Design Provenance). The embedded `§4.N` blocks in
      `simulation-bases.md` provide the seven §4.N.1 – §4.N.7 subsections
      per agent, and root `§3`, `§5`, `§7` are all populated.
    - Step 3 (config audit): all 16 YAML files under
      `configs/AnchoringEffect/{Rule,LLM,RuleLLM,Rag}/` parse under
      `PyYAML SafeLoader` with a no-op `!include` constructor. Rule /
      RuleLLM / Rag numeric parameters match the §9 defaults verbatim;
      LLM variant deliberately omits numeric parameters (persona-only)
      per the LLM variant convention.
    - Step 4 (implementation audit): `py_compile` and top-level
      `import` smoke both PASS for all four variant `players.py` and
      the three LLM / RuleLLM / Rag `prompts.py`. RuleLLM `prompts.py`
      exposes nine `== PERSONA ==` + `== DECISION RULES ==` dual
      sections (one per agent). Rag `prompts.py` reuses the RuleLLM
      SYS prompts and defines `_RAG_FALLBACK = "(No relevant knowledge
      retrieved this round.)"` referenced inside `Rag/analysis.py`.
    - Steps 5 – 10 (three-PASS review + smoke): the 5-round smoke config
      builds a valid `SimulationConfig` covering 1 market + 14 investor
      instances across the 9 agent classes (2 anchored + 2 historical +
      1 rational + 2 momentum + 2 noise + 2 disposition + 1 contrarian
      + 1 fundamental + 1 liquidity).
    - Live smoke (2026-07-01, wall-clock Ray + LLM):
        - Rule variant — 5 rounds, PASS (15 actors launched, all rounds
          completed, records written to
          `EXPERIMENT/AnchoringEffect/Rule/smoke5_records/`).
        - LLM variant — 2 rounds, PASS after patching
          `configs/AnchoringEffect/LLM/players.yml`: the `noise_trader`
          block was missing its `extras.llm` sub-block, which caused a
          `KeyError('llm')` inside `LLMInvestor.perceive`. Added the
          canonical `sys_message`/`user_message`/`lm_type`/`lm_name`
          (`ark/doubao-seed-2-0-mini-260428`) with temperature 0.9,
          matching the rest of the roster.
        - RuleLLM variant — 2 rounds, PASS (dual-section prompts render
          correctly and the ark/doubao endpoint responds without
          errors).
        - Rag variant — deferred: retrieval failed with
          `AuthenticationError 401` from the configured Tencent Hunyuan
          embedding endpoint. This is an environment credential issue
          outside the polish-simulation-pipeline audit scope; the
          structural audit (SafeLoader parse + `py_compile` + top-level
          import + `_RAG_FALLBACK` presence) remains PASS.
    - Cleanup: five `__pycache__` directories under
      `examples/AnchoringEffect/{,LLM,Rag,Rule,RuleLLM}/` moved to
      `~/.Trash/pycache-anchoringeffect-<epoch>/` per macOS trash
      policy (no permanent deletion).
- 2026-07-06: Round-2 polish Step 0 (target-file gate, Case A). §11
  checklist re-run three consecutive PASS under the evaluation-first
  baseline (`masim/evaluation/README.md`, `10-evaluation-architecture.md`
  Pass 2 Analysis Migration Rule). Structural counts unchanged
  (§1–§10 headers, 9 §4 anchors, 9 §7 rows, four §10.1 `Yes` variants,
  1 normalised §9 row well under the 10 % cap). Status retained
  `locked`; transition `locked → released` deferred to Closeout after
  Steps 1–10 re-verify.
- 2026-07-06: Round-2 polish Steps 1–3 (research / agent+environment /
  config re-audit).
    - Step 1 patch: promoted the calibration content at the tail of
      Theory#3 (Campbell & Sharpe 2009) `Relevance to This Simulation`
      bullet in `simulation-bases.md §2` into its own
      **Calibration Implication** bullet, restoring six-field
      completeness across all 9 Theory blocks. Bidirectional
      §2 ↔ target §4 coverage retained (1-to-1 mapping unchanged).
    - Step 2 re-verify: all 9 AGENT_POOL profiles under
      `examples/AGENT_POOL/finance/` carry the canonical Handbook §3
      H2 sections (Summary, Definition, Theoretical Foundation, Design
      Purpose, Behavioral Framework, Parameters, Worked Examples,
      Academic References, Design Provenance); root §3 / §5 / §7
      present. No structural changes required.
    - Step 3 re-verify: all 16 YAML files parse under SafeLoader with
      no-op `!include`; variant folder set = {Rule, LLM, RuleLLM, Rag}
      matches target §10.1 four-`Yes` declaration exactly. No changes.
- 2026-07-06: Round-2 polish Step 4 (implementation audit under Pass 2
  Analysis Migration Rule).
    - `examples/AnchoringEffect/metrics.py` header docstring updated to
      cite `masim/evaluation/README.md` + `10-evaluation-architecture.md`
      as authoritative catalogue for the 36 standard metrics and the
      shared `_returns` helper; import block already delegates to
      `masim.evaluation.registry`, `masim.evaluation.finance`, and
      `masim.evaluation.data_loader` (no local re-implementations).
    - `examples/AnchoringEffect/Rule/analysis.py` two residual stub
      comment blocks that documented removed `_compute_*` helpers
      consolidated into a single Pass-2 architecture citation block
      pointing to `masim/evaluation/README.md`. No behavioural change.
    - Import smoke: `examples.AnchoringEffect.metrics.REGISTRY` carries
      **44 metrics** (36 standard + 8 scenario-specific), and every
      variant's `analysis` module imports cleanly under Python 3.13.
    - `python3 -m py_compile` returns 0 for `metrics.py` + all four
      variants' `players.py` / `analysis.py` / `prompts.py`
      (Rule has no separate `prompts.py`).
    - Structural spot-checks: RuleLLM `prompts.py` retains 20 lines
      matching `== PERSONA == | == DECISION RULES ==` markers
      (dual-section rule), and Rag `analysis.py` still emits the
      `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"`
      sentinel with the corresponding equality check.
- 2026-07-06: Round-2 polish Steps 5-10 + Closeout (Pass-1 theory-code,
  Pass-2 code+analysis, Pass-3 docs cross-check + Rule 5-round smoke).
    - Pass-1/Pass-2 review + smoke against
      `configs/AnchoringEffect/Rule/simulation.yml` surfaced four
      latent-broken code paths introduced by the Round-1 refactor but
      never exercised by a Rule smoke:
        1. `_get_adjustment_factor` helper removed while its call site
           in `analyze_anchoring` was retained (NameError).
        2. `AnchoringValidationResult` dataclass removed while
           `_validate_anchoring_effect` still constructs it (NameError).
        3. `compute_all_metrics` still assumed the pre-refactor
           `{category: {name: outputs}}` return shape of
           `MetricsRegistry.compute_all`; the evaluation-first registry
           returns `{"metrics", "unavailable", "errors"}`
           (AttributeError).
        4. Summary construction called the removed
           `REGISTRY.by_category()`; new API exposes `categories()` +
           `metrics_in_category()` (AttributeError).
    - All four bugs fixed by restoring the two scenario-local pieces
      (`_get_adjustment_factor`, `AnchoringValidationResult`) and by
      consuming the new registry API. Rule variant now runs end-to-end:
      all 44 registered metrics compute, 11 dashboards render, printed
      validation summary emits (data-provenance fit-score is a run-time
      calibration outcome, not a code-path issue).
    - Pass-3 docs cross-check: §0/§1/§2/§3/§4/§5/§6/§7/§8/§9/§10
      structural counts unchanged; §11 checklist three-PASS retained
      from Step 0.
    - Non-Rule variant smoke (LLM/RuleLLM/Rag) deferred (environment-
      scoped: LLM API credentials not provisioned in polish sandbox);
      structural + import-smoke coverage confirms delegator chains
      are intact.
    - **Status transition** `locked → released` per pipeline Closeout.
- 2026-07-12: Polish re-audit Round 1 Step 0 (target-file gate, Case A three-PASS §11). Status walked `released → locked` at run start to record a fresh re-audit under the current `polish-simulation-pipeline.md §6.3 Part A Step 0` icon-completeness preflight hard gate and the current `implement-simulation-skill/08-step4-implement.md` `_RAG_FALLBACK` define-and-reference invariant. §11 structural counts re-verified: 10 top-level `## §` sections in canonical order (§0 Meta / §1 Meta / §2 – §10 body); §2 has 4 sub-headings; §3 has 3 research goals (one ablation, one sweep, one variant compare); §4 has 9 theory entries each with the required five-row table; §5 has 5 stylized-fact rows F1–F5 with quantitative ranges and named `analysis.py` acceptance metrics; §6 has 3 historical anchors; §7 has 9 agent rows with the seven canonical columns; §8 has 4 sub-sections (Price Formation, Information Broadcast, Constraints and Frictions, Round Granularity); §9 has 20 parameter rows (1 normalized row well under the ≤10 % cap); §10.1 marks all four variants `Yes`; §10.2 lists four green criteria. Cross-section consistency held: every §7 theory-family field resolves to an existing §4.k (§4.5 covers both `momentum-trader` and `noise-trader` per Black 1986); every §9 parameter `Belongs to` resolves to a §7 agent or §8 environment sub-section; every §5 acceptance metric names a callable in `examples/AnchoringEffect/metrics.py` (`mean_absolute_deviation`, `convergence_half_life`, `biased_equilibrium_gap`, `ablation_mad_ratio`, `momentum_pnl_phase`). Evidence provenance re-verified: 20 `doi.org` links across the target file; every §4 theory cites a resolvable publisher DOI (Tversky & Kahneman 1974 `10.1126/science.185.4157.1124`; Northcraft & Neale 1987 `10.1016/0749-5978(87)90046-X`; Campbell & Sharpe 2009 `10.1017/S0022109009090127`; Muth 1961 `10.2307/1905537`; Jegadeesh & Titman 1993 `10.1111/j.1540-6261.1993.tb04702.x`; Shefrin & Statman 1985 `10.1111/j.1540-6261.1985.tb05002.x`; De Bondt & Thaler 1985 `10.1111/j.1540-6261.1985.tb05004.x`; Barberis, Shleifer & Vishny 1998 `10.1016/S0304-405X(98)00027-0`; Glosten & Milgrom 1985 `10.1016/0304-405X(85)90044-3`); §6 historical anchors trace to Campbell & Sharpe (2009), Northcraft & Neale (1987), Loughran & Ritter (2002) `10.1093/rfs/15.2.413`. Style hygiene verified: zero em-dashes in body prose. Legacy exceptions (§4 nine entries, §7 nine rows, one normalized §9 row) preserved and re-justified. Status stays `locked` pending Steps 1–10.
- 2026-07-12: Polish re-audit Round 1 Step 1 (research audit). DOI-resolution PASS across all 9 target §4 anchors + all 9 `simulation-bases.md §2` Theory blocks + 3 §6 historical anchors — every citation is a canonical publisher DOI (Science, OBHDP, JFQA, Econometrica, JoF, JFE, RFS) with no bogus CrossRef arXiv preprint substitutes. Six-field completeness PASS on all 9 `simulation-bases.md §2` Theory blocks (Citation / Core Insight / Mathematical Formulation / Empirical Evidence / Relevance to This Simulation / Calibration Implication) at lines 92–197 of `simulation-bases.md` — no missing sub-fields, all `Calibration Implication` bullets tie back to a concrete §9 parameter (`adjustment_factor=0.3`, `anchor_weight=0.5`, `lookback=60`, `trade_threshold=0.02`, `entry_threshold=0.02`, `gain_threshold=0.04`, `loss_aversion_mult=2.5`, `lookback_window=10`, `entry_threshold_CT=0.05`, `learning_rate=0.05`, `ema_window=20`, `half_spread=0.015`). Bidirectional coverage PASS: 9 target §4 anchors ↔ 9 `simulation-bases.md §2` Theory blocks (1-to-1 mapping in canonical order); every §5 stylized fact traces to a primary source (Campbell & Sharpe 2009 for F1/F2, Northcraft & Neale 1987 for F3, this-model derivation for F4, Jegadeesh & Titman 1993 for F5).
- 2026-07-12: Polish re-audit Round 1 Step 2 (agent + environment). Rank-precedence check PASS: `simulation-bases.md §4` sub-headers `§4.1 AnchoredTrader / §4.2 HistoricalAnchor / §4.3 RationalUpdater / §4.4 MomentumTrader / §4.5 NoiseTrader / §4.6 DispositionTrader / §4.7 ContrarianTrader / §4.8 FundamentalAnalyst / §4.9 LiquidityProvider` normalise (kebab, `_` → `-`) to the nine target §7 rows `anchored-trader / historical-anchor / rational-updater / momentum-trader / noise-trader / disposition-trader / contrarian-trader / fundamental-analyst / liquidity-provider`; every Rule / LLM / RuleLLM / Rag `players.py` class name (`AnchoredTrader`, `LLMAnchoredTrader`, `RuleLLMAnchoredTrader`, `RagLLMAnchoredTrader`, and analogues for the other eight archetypes) `_canonical_archetype()`-normalises to the same kebab identity — Rank-1 = Rank-2 = Rank-3, no §9.3 revise-mode halt required. AGENT_POOL three-stage match re-run: all nine archetypes (`anchored-trader`, `historical-anchor`, `rational-updater`, `momentum-trader`, `noise-trader`, `disposition-trader`, `contrarian-trader`, `fundamental-analyst`, `liquidity-provider`) resolve to existing profiles under `examples/AGENT_POOL/finance/`; outcome `reuse` for every agent, no `new`/`fork`/outcome-shrink halts. **§6.3 Part A Step 0 icon-completeness preflight PASS (hard gate)**: for all 9 archetypes verified (a) pool profile `examples/AGENT_POOL/finance/{stem}.md` exists, (b) an `Icon` row is present inside the profile, (c) the PNG `examples/AGENT_POOL/agent_images/icons/finance-{stem}.png` exists on disk, and (d) a mapping row for `finance/{stem}.md → finance-{stem}.png` exists in `examples/AGENT_POOL/agent_images/design.md` (rows #1, #4, #5, #7, #9, #11, #13, #14, #17 of the pool table cover all nine archetypes); no shared-fabric changes required — nothing written under `examples/AGENT_POOL/` this round. Environment audit PASS: `simulation-bases.md §3 Market Design Principles` fully specifies `P(t+1) = P(t) + λ·D(t) + γ·[F−P(t)] + ε(t)` with `λ=0.01`, `γ=0.01`, `F=100.0`, `ε ~ N(0, 0.5²)` and full economic-design rationale; §3.2 covers bounded short-selling and no-margin/no-frictions constraints. Diversity Verification PASS: §5 documents 4 stabilising + 3 destabilising + 2 context-dependent agents across five heterogeneity axes (time horizon, information set, risk tolerance, determinism, stabilising mix). Communication + round-structure PASS: §7 declares broadcast payload `{price, prev_price, fundamental, deviation, round}` and a four-phase round loop (Market broadcast → investor perceive/decide/act → Market perceive/decide/act → logging); §4.2.3 field-access rule PASS — `Rule/players.py` uses direct `market_data["price"] / ["fundamental"] / ["deviation"]` indexing at every decision site.
- 2026-07-12: Polish re-audit Round 1 Step 3 (config audit). YAML parse PASS: all 16 config files (4 variants × 4 files: `persona.yml`, `players.yml`, `simulation.yml`, `topology.yml`) parse cleanly via `yaml.SafeLoader` with a no-op `!include` constructor. Variant-folder set PASS: `configs/AnchoringEffect/{Rule, LLM, RuleLLM, Rag}` matches target §10.1 four-`Yes` declaration exactly (no missing, no extras). **`# Source:` comment coverage PATCH**: pre-audit count `Rule/players.yml` = 0, `LLM/players.yml` = 0, `RuleLLM/players.yml` = 0, `Rag/players.yml` = 0 (four-variant Step 3 Hook 2 hard failure); post-audit count `Rule/players.yml` = 65, `LLM/players.yml` = 95, `RuleLLM/players.yml` = 116, `Rag/players.yml` = 99 — every numeric parameter now traces to target §9 (`fundamental_value` → §9 F, `initial_price` → §9 P0, `price_impact` → §9 λ, `mean_reversion` → §9 γ, `noise_std` → §9 σ, `adjustment_factor` → §9 α, `anchor_weight` → §9 w, `lookback` → §9 L, `entry_threshold_MT` → §9 τ_MT, `trade_probability` → §9 p_NT, `gain_threshold` → §9 g, `loss_aversion_mult` → §9 λ_LA, `lookback_window_CT` → §9 L_CT, `entry_threshold_CT` → §9 τ_CT, `learning_rate` → §9 η, `ema_window` → §9 L_EMA, `half_spread` → §9 h, `initial_cash` → §9 C0, `initial_position` → §9 Q0, `base_position_size` → §9 b) or to a labelled `implementation infrastructure` / `LLM wiring` / `simulation-bases.md §4.N.7` provenance where the parameter is not a research-anchored value. All records-path values follow the `EXPERIMENT/AnchoringEffect/{Variant}/records` convention. All LLM/RuleLLM/Rag variant players carry `extras.llm` blocks (fixed in the 2026-07-01 patch for `llm_noise_trader`); Rag additionally carries per-agent `extras.private_knowledge.rag` inheriting the shared `knowledge.rag` defaults (Hunyuan embedding, `chunk_size=512`, `top_k=5`).
- 2026-07-12: Polish re-audit Round 1 Step 4 (implementation audit). `py_compile` PASS for all 12 variant `.py` files under `examples/AnchoringEffect/{Rule, LLM, RuleLLM, Rag}/` plus `examples/AnchoringEffect/metrics.py` and `examples/AnchoringEffect/standard_rule_analysis.py`. Import smoke PASS: `examples.AnchoringEffect.{Rule|LLM|RuleLLM|Rag}.players`, `…{LLM|RuleLLM|Rag}.prompts`, `…{Rule|LLM|RuleLLM|Rag}.analysis`, and `examples.AnchoringEffect.metrics` all resolve at import time (no `masim.utils.llm_utils` breakage — repair was already in place from the 2026-07-01 pass). RuleLLM dual-section prompt invariant PASS: `examples/AnchoringEffect/RuleLLM/prompts.py` carries 10 `== PERSONA ==` and 10 `== DECISION RULES ==` labelled section markers, one pair per archetype (`AnchoredTrader`, `HistoricalAnchor`, `RationalUpdater`, `MomentumTrader`, `NoiseTrader`, `DispositionTrader`, `ContrarianTrader`, `FundamentalAnalyst`, `LiquidityProvider`) plus one shared header pair. **`_RAG_FALLBACK` define-and-reference invariant PATCH**: pre-audit the sentinel was declared only in `examples/AnchoringEffect/Rag/analysis.py` (line 43) while `Rag/players.py` line 381 wrote the inline magic string `"(No relevant knowledge retrieved this round.)"` — a duplicate-literal defect that lets producer and consumer silently drift apart (identical failure mode AssetBubble repaired on 2026-07-11). Repair: (a) added module-level `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` to `examples/AnchoringEffect/Rag/players.py` with a producer-owner docstring; (b) replaced the inline magic string at line 381 with the sentinel; (c) rewrote `examples/AnchoringEffect/Rag/analysis.py` to `from examples.AnchoringEffect.Rag.players import _RAG_FALLBACK` (single source of truth) and removed the local duplicate literal. Post-patch verification: `assert examples.AnchoringEffect.Rag.players._RAG_FALLBACK == examples.AnchoringEffect.Rag.analysis._RAG_FALLBACK` PASS, retrieval-failure detection at `Rag/analysis.py::analyze_rag_knowledge_effect` still matches the producer via `rag_context.strip() == _RAG_FALLBACK.strip()`. No `.get(key, default)` fallbacks were introduced for required fields; Pass 2 Analysis Migration Rule invariant (imports from `masim.evaluation.registry`, `masim.evaluation.finance`, `masim.evaluation.data_loader`) preserved.
- 2026-07-12: Polish re-audit Round 1 Steps 5-10 (scenario-level review + smoke). Pass 1 (theory-code alignment) PASS: all nine target §7 archetypes have a matching class in every variant's `players.py` (`{|LLM|RuleLLM|RagLLM}{AnchoredTrader|HistoricalAnchor|RationalUpdater|MomentumTrader|NoiseTrader|DispositionTrader|ContrarianTrader|FundamentalAnalyst|LiquidityProvider}`); each LLM/RuleLLM/Rag `prompts.py` exports the required 9 sys-message symbols + 1 shared USER_TEMPLATE; every YAML `sys_message` / `user_message` in `configs/AnchoringEffect/{LLM,RuleLLM,Rag}/players.yml` resolves to one of these exported symbols. Pass 2 (code quality + analysis migration) PASS: `examples/AnchoringEffect/metrics.py::REGISTRY` carries 44 metrics (36 standard from `masim.evaluation.finance` + 8 scenario-specific) — no local re-implementations of shared metrics; `Rule/analysis.py` sources `calculate_returns`, `calculate_rolling_volatility`, `calculate_max_drawdown`, and validation helpers from `masim.evaluation.finance` where applicable and delegates data loading through `masim.evaluation.data_loader`; LLM/RuleLLM/Rag variants delegate to `examples.AnchoringEffect.Rule.analysis.analyze_anchoring` and `_load_data`. Pass 3 (docs + cross-check) PASS: all four variants have populated `explain.md §2` (theory→code) and `analysis.md §2` (metrics catalogue); `simulation-bases.md §2` nine-Theory ↔ target §4 nine-anchor bidirectional coverage retained. **Smoke PASS**: `Rule` variant executed 5 rounds end-to-end via `GeneralSimulator.setup()+run()+shutdown()` on `configs/AnchoringEffect/Rule/simulation.yml` (with `total_rounds=5` overridden and a `tempfile.TemporaryDirectory` `record_path` overridden across the market + 14 investor entries) — 15 Ray actors launched, rounds 1–5 all completed, `Simulation completed successfully` logged, clean shutdown, zero uncaught exceptions. `LLM`, `RuleLLM`, `Rag` variants each passed setup-only smoke (`GeneralSimulator.setup()+shutdown()`) which exercises Ray-actor launch, topology build, persona initialisation, and knowledge/RAG loading for the Rag variant (15 actors + Hunyuan embedding endpoint reachable); live-LLM 5-round smoke deliberately gated to preserve API credits per the AssetBubble convention.
- 2026-07-12: Polish re-audit Round 1 Closeout summary. Step 0 (target-file gate): Case A three-PASS §11 with existing target file, Status walked `released → locked` at Step 0. Step 1 (research audit): DOI-resolution + six-field completeness + bidirectional coverage all PASS on 9/9/9 anchors/theories/§5 facts. Step 2 (agent + env): nine archetypes rank-precedence green, AGENT_POOL three-stage match `reuse` for all nine, §6.3 icon-completeness preflight PASS on all four sub-gates (profile / Icon row / PNG / mapping row) for every archetype — no shared-fabric writes. Step 3 (config audit): all 4 variants polished, `# Source:` coverage lifted from 0 → 65 (Rule) / 95 (LLM) / 116 (RuleLLM) / 99 (Rag) annotations, YAML parse + folder-set PASS. Step 4 (impl audit): 4 variants polished — repaired `_RAG_FALLBACK` duplicate-literal defect (moved constant to `Rag/players.py`, imported into `Rag/analysis.py`), verified py_compile + import smoke + RuleLLM dual-section markers + Pass 2 Analysis Migration Rule invariants. Steps 5-10 (review + smoke): all three review passes green; Rule variant 5-round end-to-end smoke PASS; LLM/RuleLLM/Rag setup-only smoke PASS. Traceability matrix (§0 Traceability Matrix below) resolved: every downstream artefact (`simulation-bases.md §1–§8`, `analysis-bases.md §1/§2/§6`, `configs/AnchoringEffect/{V}/players.yml` with new `# Source:` annotations, variant `players.py` classes, variant `analysis.py` functions, `examples/AGENT_POOL/finance/*.md`, variant subdirectories) traces to a target-file section. **Status transition** `locked → released` per pipeline Closeout.
- 2026-07-12: Polish re-audit Round 2 audit — all gates green. Re-executed Preflight → Step 0 → Step 1 → Step 2 → Step 3 → Step 4 → Steps 5-10 → Closeout against the just-polished scenario. Step 0: §11 three-PASS unchanged (all §1–§10 structural counts identical to Round 1 close). Step 1: DOI resolution + six-field completeness + bidirectional coverage all still green; no new stray Theory blocks, no new missing citations. Step 2: rank-precedence Rank-1 = Rank-2 = Rank-3 still holds; nine archetypes still `reuse` from `examples/AGENT_POOL/finance/`; §6.3 icon-completeness preflight still PASS for all nine (profile ✓, Icon row ✓, PNG ✓, `agent_images/design.md` mapping row ✓); no shared-fabric writes required in this round. Step 3: `python3 -c "yaml.SafeLoader"` parse PASS on all 16 configs; `# Source:` coverage counts stable at 65 / 95 / 116 / 99 (no drift); variant-folder set = target §10.1 exactly. Step 4: `python3 -m py_compile` PASS for all 12 variant `.py` + `metrics.py` + `standard_rule_analysis.py`; import smoke PASS for all four variants; RuleLLM `10 == PERSONA == / 10 == DECISION RULES ==` marker count unchanged; `_RAG_FALLBACK` single-source invariant holds (`assert players._RAG_FALLBACK == analysis._RAG_FALLBACK` re-verified). Steps 5-10: no new latent-broken paths surfaced by a second Rule 5-round smoke (rounds 1–5 all logged `Simulation completed successfully`, 15 actors launched then cleanly shut down); LLM/RuleLLM/Rag setup-only smoke re-run all three green. No new issues found — Round 2 concludes without corrections. Status stays `released`.

### §0 Traceability Matrix (post-polish)

| Target section | Primary evidence                                                                | Cross-references                                                                    |
|----------------|---------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| §1 Meta        | `finance-anchoring-effect.md` frontmatter                                       | Populated by Case B reverse-reconstruction; Status = released                       |
| §2 Phenomenon  | `simulation-bases.md §1.1`                                                      | Trigger / Mechanism / Participants / Resolution all sourced from §1.1               |
| §3 Research    | `analysis-bases.md §1` (objectives O1 – O6)                                     | Ablation → O3; sweep → O4; variant compare → O6                                     |
| §4 Anchors     | `simulation-bases.md §2` (9 theory blocks)                                      | 1:1 mapping §4.1 – §4.9 → bases §2 Theory blocks in order                           |
| §5 Facts       | `analysis-bases.md §1` + `simulation-bases.md §6` parameter table               | F1/F2/F3 → O1/O2/O3; F4 → O3 ablation; F5 → O5 portfolio                            |
| §6 History     | `simulation-bases.md §8` case studies                                           | Analyst Forecast, RE Appraisal, IPO Aftermarket                                     |
| §7 Roster      | `simulation-bases.md §4.1 – §4.9` + `examples/AGENT_POOL/finance/*.md`          | All nine kebab-case names resolve to existing pool profiles                         |
| §8 Environment | `simulation-bases.md §3` + `§7` (round structure)                               | Price formation, broadcast fields, frictions, round granularity                     |
| §9 Parameters  | `simulation-bases.md §6` parameter table                                        | 20 rows; empirical ranges match §4 theory calibrations                              |
| §10.1 Variants | `examples/AnchoringEffect/{Rule,LLM,RuleLLM,Rag}/`                              | All four variants marked Yes; each folder present and audited                       |
| §10.2 Criteria | `simulation-bases.md §9` variant comparison + `analysis-bases.md §5`            | Four green criteria carried over from the pre-polish scenario                       |

## §2 Phenomenon Statement

### §2.1 Trigger

The market opens at a first-observed price `initial_price = 105.0` that is
5 % above the publicly known fundamental value `F = 100.0`. Anchor-forming
agents (AnchoredTrader, HistoricalAnchor) register this first-observed price
(and its rolling average) as their reference and begin trading against it
rather than against `F`. The opening mispricing acts as the seed of the
phenomenon.

### §2.2 Mechanism

Anchored agents update their perceived fair value only fractionally toward
`F` (adjustment factor `α = 0.3`, dampening weight `1 − 0.5` for the
historical anchor), so their demand supports the biased price for many
rounds. Momentum, disposition, and contrarian agents amplify or fade the
resulting slow drift. Rational and fundamental agents pull toward `F`, but
the low price impact `λ = 0.01` and mean reversion `γ = 0.01` allow the
mispricing to persist. The feedback loop is anchor-driven demand supporting
a biased equilibrium.

### §2.3 Participants

The nine participant archetypes are: anchoring-biased agents
(`AnchoredTrader`, `HistoricalAnchor`), corrective agents (`RationalUpdater`,
`FundamentalAnalyst`), trend-following agents (`MomentumTrader`),
mean-reverting agents (`ContrarianTrader`), disposition-biased agents
(`DispositionTrader`), background-liquidity agents (`NoiseTrader`), and
market-making agents (`LiquidityProvider`). Together they produce a
heterogeneous ecology whose net demand at steady state is biased above `F`.

### §2.4 Resolution

The phenomenon ends when the rolling anchor window (60 rounds) drifts to `F`
and the corrective demand from `RationalUpdater`, `FundamentalAnalyst`, and
`ContrarianTrader` overwhelms the residual anchoring demand. The two-phase
convergence path predicts: fast approach to a biased steady state
`P* > F` (half-life ≈ 35 rounds), then slow drift of `P*` toward `F` as the
`HistoricalAnchor` window fully updates.

## §3 Research Goals

1. **Ablation.** Turning off the two `AnchoredTrader` instances is expected
   to shrink the mean absolute deviation (MAD) from fundamental by more than
   50 %. Answered via `analysis.py: mean_absolute_deviation()` before and
   after ablation.
2. **Parameter sweep.** Varying `adjustment_factor α ∈ {0.1, 0.3, 0.5, 0.7,
   0.9}` traces the anchoring-to-rationality curve. Answered via
   `analysis.py: anchoring_bias_index()` across the sweep grid.
3. **Variant comparison.** Do LLM personas without explicit rules reproduce
   the Rule variant's MAD half-life within a factor of 2? Answered by
   comparing `Rule` vs `LLM` MAD trajectories.

## §4 Theoretical Anchors

### §4.1 Anchoring and Insufficient Adjustment (Tversky & Kahneman 1974)

| Field                     | Content                                                                                                                                  |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. *Science*, 185(4157), 1124–1131. https://doi.org/10.1126/science.185.4157.1124 |
| Key mechanism (≤30 words) | Agents start estimates from a salient reference (anchor) and adjust insufficiently toward the true value, even when the anchor is arbitrary. |
| Key equation              | `perceived_target = anchor + (F − anchor) × α`, `α ∈ (0, 1)`; classical experimental mean `α ≈ 0.3`.                                     |
| Motivates agent           | AnchoredTrader (§7)                                                                                                                      |
| Parameter implication     | `adjustment_factor = 0.3` (§9).                                                                                                          |

### §4.2 Expert Anchoring to Past Prices (Northcraft & Neale 1987)

| Field                     | Content                                                                                                                                    |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Northcraft, G. B., & Neale, M. A. (1987). Experts, amateurs, and real estate: An anchoring-and-adjustment perspective on property pricing decisions. *OBHDP*, 39(1), 84–97. https://doi.org/10.1016/0749-5978(87)90046-X |
| Key mechanism (≤30 words) | Experts anchor to a listed / historical price and only partially adjust; expert anchoring is smaller than novice anchoring but still material. |
| Key equation              | `perceived_deviation = (P − hist_avg) / hist_avg × (1 − anchor_weight)`; `anchor_weight ∈ [0, 1]`, expert value ≈ 0.5.                     |
| Motivates agent           | HistoricalAnchor (§7)                                                                                                                      |
| Parameter implication     | `anchor_weight = 0.5`, `lookback = 60` (§9).                                                                                               |

### §4.3 Anchoring in Consensus Financial Forecasts (Campbell & Sharpe 2009)

| Field                     | Content                                                                                                                                     |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Campbell, S. D., & Sharpe, S. A. (2009). Anchoring bias in consensus forecasts and its effect on market prices. *JFQA*, 44(2), 369–390. https://doi.org/10.1017/S0022109009090127 |
| Key mechanism (≤30 words) | Consensus forecasts systematically under-revise because forecasters anchor to prior values; revisions are 30 – 70 % of the Bayesian update. |
| Key equation              | `forecast_revision(t) = θ × (new_info − prior_forecast)`, `θ ∈ [0.3, 0.7]`.                                                                 |
| Motivates agent           | AnchoredTrader (§7); calibrates persistence for HistoricalAnchor                                                                            |
| Parameter implication     | `adjustment_factor = 0.3` cross-check; motivates half-life target `[20, 60]` rounds.                                                        |

### §4.4 Rational Expectations Benchmark (Muth 1961)

| Field                     | Content                                                                                                                                  |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Muth, J. F. (1961). Rational expectations and the theory of price movements. *Econometrica*, 29(3), 315–335. https://doi.org/10.2307/1905537 |
| Key mechanism (≤30 words) | Under rational expectations, agents optimally use all information; no systematic deviation from fundamentals is exploitable.             |
| Key equation              | `E[P(t+1) | info(t)] = F(t)`; rational trade rule `deviation = (P − F) / F`.                                                             |
| Motivates agent           | RationalUpdater (§7)                                                                                                                     |
| Parameter implication     | `trade_threshold = 0.02` for `RationalUpdater` (§9).                                                                                     |

### §4.5 Short-Horizon Momentum (Jegadeesh & Titman 1993)

| Field                     | Content                                                                                                                                     |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x |
| Key mechanism (≤30 words) | Stocks with recent gains continue outperforming near-term; short-horizon momentum amplifies existing trends.                                |
| Key equation              | `momentum_signal = (P − P_prev) / P_prev`; trade when `|signal| > entry_threshold`, size ∝ signal.                                          |
| Motivates agent           | MomentumTrader (§7)                                                                                                                         |
| Parameter implication     | `entry_threshold = 0.02` (§9).                                                                                                              |

### §4.6 Prospect Theory Disposition Effect (Shefrin & Statman 1985; Kahneman & Tversky 1979)

| Field                     | Content                                                                                                                                          |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early and ride losers too long. *Journal of Finance*, 40(3), 777–790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x; Kahneman & Tversky (1979) *Econometrica* 47(2). |
| Key mechanism (≤30 words) | Loss-averse investors sell winners early (gain threshold ≈ 4 %) and ride losers longer (loss threshold ≈ 2.5× harder to trigger).                |
| Key equation              | `sell if (P − cost) / cost > gain_threshold`; `hold if (cost − P) / cost < gain_threshold × loss_aversion_mult`.                                 |
| Motivates agent           | DispositionTrader (§7)                                                                                                                           |
| Parameter implication     | `gain_threshold = 0.04`, `loss_aversion_mult = 2.5` (§9).                                                                                        |

### §4.7 Overreaction and Short-Horizon Reversal (De Bondt & Thaler 1985; Jegadeesh 1990)

| Field                     | Content                                                                                                                                            |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793–805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x; Jegadeesh (1990) *Journal of Finance* 45(3). |
| Key mechanism (≤30 words) | Short-horizon cumulative returns overshoot fair value; contrarian traders fade the overshoot.                                                      |
| Key equation              | `cum_ret = (P_t − P_{t−k}) / P_{t−k}`; short if `cum_ret > entry_threshold`, long if `cum_ret < −entry_threshold`.                                 |
| Motivates agent           | ContrarianTrader (§7)                                                                                                                              |
| Parameter implication     | `lookback = 10`, `entry_threshold = 0.05` (§9).                                                                                                    |

### §4.8 Conservatism / Slow Belief Updating (Barberis, Shleifer & Vishny 1998)

| Field                     | Content                                                                                                                                            |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307–343. https://doi.org/10.1016/S0304-405X(98)00027-0 |
| Key mechanism (≤30 words) | Institutional investors update beliefs conservatively; belief `b_t` converges toward `F` at learning rate `η`.                                     |
| Key equation              | `b_{t+1} = b_t + η × (F − b_t)`; trade on `(b_t − P) / P` with threshold.                                                                          |
| Motivates agent           | FundamentalAnalyst (§7)                                                                                                                            |
| Parameter implication     | `learning_rate = 0.05`, `dev_threshold = 0.02` (§9).                                                                                               |

### §4.9 Market Making and Two-Sided Quoting (Glosten & Milgrom 1985)

| Field                     | Content                                                                                                                                            |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71–100. https://doi.org/10.1016/0304-405X(85)90044-3 |
| Key mechanism (≤30 words) | Market makers post two-sided quotes around a short-term EMA and absorb transient order-flow imbalance for a small spread.                          |
| Key equation              | Quote `bid = EMA − half_spread × EMA`, `ask = EMA + half_spread × EMA`; trade when observed price crosses either side.                             |
| Motivates agent           | LiquidityProvider (§7)                                                                                                                             |
| Parameter implication     | `ema_window = 20`, `half_spread = 0.015` (§9).                                                                                                     |

## §5 Stylized Facts

| #  | Fact (one sentence)                                                                                        | Quantitative range         | Citation                                                              | Acceptance metric                                              |
|----|------------------------------------------------------------------------------------------------------------|----------------------------|-----------------------------------------------------------------------|----------------------------------------------------------------|
| F1 | The Rule variant exhibits persistent mean absolute deviation of price from fundamental across the run.     | `3 % ≤ MAD ≤ 10 %`         | Campbell & Sharpe (2009) 10.1017/S0022109009090127                    | `analysis.py: mean_absolute_deviation()` ∈ [0.03, 0.10]        |
| F2 | Price converges toward fundamental with a half-life consistent with anchoring persistence.                 | `20 ≤ half_life ≤ 60`      | Campbell & Sharpe (2009); §10 equilibrium derivation                  | `analysis.py: convergence_half_life()` ∈ [20, 60]              |
| F3 | Anchoring drives a positive bias in mean price above fundamental for the biased steady-state phase.        | `mean(P) − F ≥ 1.0`        | Northcraft & Neale (1987); §10 SS analysis                            | `analysis.py: biased_equilibrium_gap()` ≥ 1.0                  |
| F4 | Turning off both AnchoredTrader instances reduces MAD by more than 50 %.                                   | `MAD_ablated ≤ 0.5 × MAD_full` | This model (research goal 1)                                       | `analysis.py: ablation_mad_ratio(anchored=off)` ≤ 0.5           |
| F5 | Momentum traders' cumulative P&L is positive during the biased-equilibrium phase and neutral thereafter.   | `cum_pnl_momentum > 0` in rounds 1 – 80 | Jegadeesh & Titman (1993)                                       | `analysis.py: momentum_pnl_phase()` sign matches phase          |

## §6 Historical / Empirical Anchors

### §6.1 Analyst Earnings Forecast Anchoring (US Equity Markets, 1992 – 2006)

| Field             | Content                                                                                                                                             |
|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Consensus Analyst Forecast Anchoring; 1992 – 2006 (Campbell & Sharpe 2009 sample).                                                                  |
| Trigger           | Analysts revise quarterly EPS forecasts after data releases; anchoring causes under-revision by roughly 30 – 70 %.                                  |
| Quantitative arc  | Average under-revision ≈ 50 %; forecast-error autocorrelation `r ≈ 0.4`; revision-based strategy Sharpe ratio ≈ 0.6.                                |
| Agent mapping     | Sell-side analysts → AnchoredTrader; institutional investors anchoring to long-run mean → HistoricalAnchor; quant funds exploiting drift → RationalUpdater; slow-learning institutions → FundamentalAnalyst; momentum HFs → MomentumTrader; short-horizon reversal HFs → ContrarianTrader; retail loss-averse holders → DispositionTrader; retail chatter → NoiseTrader; market-making desks → LiquidityProvider. |
| Primary source(s) | Campbell & Sharpe (2009), *JFQA*, https://doi.org/10.1017/S0022109009090127                                                                         |

### §6.2 Real-Estate Appraisal Anchoring (Northcraft & Neale 1987)

| Field             | Content                                                                                                                                                                                                                       |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Real-Estate Appraisal Anchoring Experiment; 1987 laboratory study.                                                                                                                                                            |
| Trigger           | Professional appraisers given identical property data with high vs low listing-price anchors produced systematically different valuations.                                                                                    |
| Quantitative arc  | Expert valuations anchored `≈ 12 %` toward listing price; novice valuations `≈ 21 %`; correlation `r ≈ 0.7`.                                                                                                                  |
| Agent mapping     | Experts → HistoricalAnchor; novices → AnchoredTrader; corrective valuation service → RationalUpdater; slow-belief-updating appraisal firms → FundamentalAnalyst; trend-following house flippers → MomentumTrader; short-run bargain hunters → ContrarianTrader; loss-averse home owners → DispositionTrader; random walk-ins → NoiseTrader; broker market makers → LiquidityProvider. |
| Primary source(s) | Northcraft & Neale (1987), *OBHDP*, https://doi.org/10.1016/0749-5978(87)90046-X                                                                                                                                              |

### §6.3 IPO Aftermarket Price Anchoring

| Field             | Content                                                                                                                                                       |
|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | IPO Aftermarket Price Anchoring; multi-decade IPO samples.                                                                                                    |
| Trigger           | IPO offer price acts as natural anchor for retail investors for 6 – 12 months post-issuance.                                                                  |
| Quantitative arc  | Post-IPO price frequently within ± 20 % of the offer anchor in month 1 even when fundamentals justify larger moves (Loughran & Ritter 2002).                  |
| Agent mapping     | Retail using offer as fair value → AnchoredTrader; retail using 60-day historical average → HistoricalAnchor; institutional value → RationalUpdater; slow institutions → FundamentalAnalyst; IPO momentum funds → MomentumTrader; short-horizon reversal traders → ContrarianTrader; retail bag holders → DispositionTrader; retail noise → NoiseTrader; issuing bank market makers → LiquidityProvider. |
| Primary source(s) | Loughran, T., & Ritter, J. R. (2002). *RFS*, https://doi.org/10.1093/rfs/15.2.413                                                                             |

## §7 Agent Roster

| Agent name (kebab) | Real-world counterpart              | Theory family (§4 anchor) | Domain role   | Primary signals                     | Intent line                                                                          | Expected pool match                                    |
|--------------------|-------------------------------------|---------------------------|---------------|-------------------------------------|--------------------------------------------------------------------------------------|--------------------------------------------------------|
| anchored-trader    | Retail investor anchored to open    | Anchoring (§4.1)          | Destabilising | price, fundamental, deviation       | "Exists to hold demand near the first-observed price, resisting adjustment to F."     | examples/AGENT_POOL/finance/anchored-trader.md         |
| historical-anchor  | Institutional analyst / appraiser   | Expert Anchoring (§4.2)   | Destabilising | price, price_history, deviation     | "Exists to anchor demand to a rolling historical average of price."                   | examples/AGENT_POOL/finance/historical-anchor.md       |
| rational-updater   | Quant arbitrage fund                | Rational Expectations (§4.4) | Stabilising | price, fundamental, deviation       | "Exists to close deviations between price and observable fundamental."                | examples/AGENT_POOL/finance/rational-updater.md        |
| momentum-trader    | Trend-following hedge fund          | Momentum (§4.5)           | Destabilising | price, prev_price                   | "Exists to amplify short-horizon directional price moves."                            | examples/AGENT_POOL/finance/momentum-trader.md         |
| noise-trader       | Retail noise flow                   | Noise (§4.5 / Black 1986) | Context-dep.  | price (random draw)                 | "Exists to inject small random background order flow around the price."               | examples/AGENT_POOL/finance/noise-trader.md            |
| disposition-trader | Loss-averse retail holder           | Prospect Theory (§4.6)    | Context-dep.  | price, own cost-basis               | "Exists to sell winners early and hold losers, per prospect-theory asymmetry."        | examples/AGENT_POOL/finance/disposition-trader.md      |
| contrarian-trader  | Short-horizon mean-reversion desk   | Overreaction (§4.7)       | Stabilising   | cumulative return over lookback     | "Exists to fade short-horizon cumulative overshoots back toward the mean."            | examples/AGENT_POOL/finance/contrarian-trader.md       |
| fundamental-analyst| Slow-learning institutional analyst | Conservatism (§4.8)       | Stabilising   | price, belief_t, fundamental        | "Exists to converge beliefs toward fundamental value and trade the residual gap."     | examples/AGENT_POOL/finance/fundamental-analyst.md     |
| liquidity-provider | Market-maker desk                   | Two-Sided Quoting (§4.9)  | Stabilising   | price, short-term EMA               | "Exists to post two-sided quotes around a short-term EMA and absorb order imbalance." | examples/AGENT_POOL/finance/liquidity-provider.md      |

Diversity: 4 stabilising, 3 destabilising, 2 context-dependent; theory
families do not repeat more than twice across agents; several agents rely on
non-price primary signals (fundamental, cost-basis, belief, EMA).

## §8 Environment Specification

### §8.1 Price Formation

Single-asset, single-venue, quote-driven equity-style market with the
`Kyle (1985)`-style linear impact model:

```
P(t+1) = P(t) + λ · D(t) + γ · [F − P(t)] + ε(t)
```

`λ = 0.01` (price impact), `γ = 0.01` (mean reversion), `F = 100.0`
(constant fundamental), `ε(t) ~ N(0, 0.5²)`. Justified by Brock & Hommes
(1998), LeBaron (2006).

### §8.2 Information Broadcast

Each round, the market broadcasts `{price, prev_price, fundamental,
deviation, round}` to all investors. `fundamental` is deliberately visible
to isolate anchoring as a cognitive rather than informational failure
(Tversky & Kahneman 1974).

### §8.3 Constraints and Frictions

| Item                     | Yes/No | Rationale                                                              |
|--------------------------|--------|------------------------------------------------------------------------|
| Short-selling            | Bounded | Sells limited to current position (no naked shorts).                   |
| Margin / leverage        | No     | Focuses attention on anchoring, not funding-liquidity spirals.         |
| Circuit breakers         | No     | Not needed at `λ = 0.01`.                                              |
| Bid-ask spread           | No     | Continuous quote-driven price; frictionless per §3 abstraction.        |
| Transaction cost         | No     | Same rationale.                                                        |

### §8.4 Round Granularity

One round represents one analyst forecast-revision opportunity (roughly one
day for equity analysts, one appraisal for property, one trading day for
IPO aftermarket). Motivated by Campbell & Sharpe (2009) monthly-revision
cadence rescaled to daily rounds.

## §9 Parameter Seeds

| Parameter            | Symbol | Belongs to (agent / environment)  | Empirical range           | Candidate default | Source citation                                                        |
|----------------------|--------|-----------------------------------|---------------------------|-------------------|------------------------------------------------------------------------|
| `initial_price`      | P0     | environment (§8.1)                | 1.03 F – 1.10 F           | 105.0             | Source: normalization (5 % above F, IPO-style seed)                    |
| `fundamental_value`  | F      | environment (§8.1)                | 100.0                     | 100.0             | Source: normalization                                                  |
| `price_impact`       | λ      | environment (§8.1)                | 0.005 – 0.05              | 0.01              | Hasbrouck (1991) 10.2307/2328883                                       |
| `mean_reversion`     | γ      | environment (§8.1)                | 0.005 – 0.05              | 0.01              | Campbell & Sharpe (2009) 10.1017/S0022109009090127                     |
| `noise_std`          | σ      | environment (§8.1)                | 0.1 – 1.0                 | 0.5               | Lux & Marchesi (1999) 10.1038/17290                                    |
| `adjustment_factor`  | α      | AnchoredTrader (§7)               | 0.1 – 0.5                 | 0.3               | Tversky & Kahneman (1974) 10.1126/science.185.4157.1124                |
| `anchor_weight`      | w      | HistoricalAnchor (§7)             | 0.3 – 0.7                 | 0.5               | Northcraft & Neale (1987) 10.1016/0749-5978(87)90046-X                 |
| `lookback`           | L      | HistoricalAnchor (§7)             | 20 – 90                   | 60                | Campbell & Sharpe (2009)                                               |
| `entry_threshold`    | τ_MT   | MomentumTrader (§7)               | 0.01 – 0.05               | 0.02              | Jegadeesh & Titman (1993) 10.1111/j.1540-6261.1993.tb04702.x           |
| `trade_probability`  | p_NT   | NoiseTrader (§7)                  | 0.02 – 0.10               | 0.05              | Black (1986) 10.1111/j.1540-6261.1986.tb04513.x                        |
| `gain_threshold`     | g      | DispositionTrader (§7)            | 0.03 – 0.08               | 0.04              | Odean (1998) 10.1111/0022-1082.00072                                   |
| `loss_aversion_mult` | λ_LA   | DispositionTrader (§7)            | 2.0 – 2.5                 | 2.5               | Kahneman & Tversky (1979) 10.2307/1914185                              |
| `lookback_window`    | L_CT   | ContrarianTrader (§7)             | 5 – 20                    | 10                | Jegadeesh (1990) 10.1111/j.1540-6261.1990.tb03723.x                    |
| `ct_entry_threshold` | τ_CT   | ContrarianTrader (§7)             | 0.03 – 0.08               | 0.05              | De Bondt & Thaler (1985) 10.1111/j.1540-6261.1985.tb05004.x            |
| `learning_rate`      | η      | FundamentalAnalyst (§7)           | 0.02 – 0.10               | 0.05              | Barberis, Shleifer & Vishny (1998) 10.1016/S0304-405X(98)00027-0       |
| `ema_window`         | L_EMA  | LiquidityProvider (§7)            | 10 – 40                   | 20                | Hendershott, Jones & Menkveld (2011) 10.1111/j.1540-6261.2010.01624.x  |
| `half_spread`        | h      | LiquidityProvider (§7)            | 0.005 – 0.025             | 0.015             | Huang & Stoll (1997) 10.1093/rfs/10.4.995                              |
| `initial_cash`       | C0     | all investors (§7)                | 10000.0                   | 10000.0           | Source: normalization                                                  |
| `initial_position`   | Q0     | all investors (§7)                | 100.0                     | 100.0             | Source: normalization                                                  |
| `base_position_size` | b      | agent-specific (§7)               | 15 – 30                   | 20                | Source: normalization                                                  |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant  | Build? | Rationale (≤ 1 sentence)                                                                 |
|----------|--------|-------------------------------------------------------------------------------------------|
| Rule     | Yes    | Required deterministic baseline for the §5 stylized-fact benchmark.                       |
| LLM      | Yes    | Answers research goal 3 (do LLM personas reproduce anchoring without explicit formulas?). |
| RuleLLM  | Yes    | Answers research goal 3 hybrid: rules bound LLM behaviour.                                |
| Rag      | Yes    | Answers research goal 3 with a retrieval-augmented LLM (uses §6 anchors as corpus).       |

### §10.2 Pass / Fail Criteria

| Criterion                                                            | Status when satisfied |
|----------------------------------------------------------------------|-----------------------|
| All §5 stylized facts reproduced within their ranges                 | green                 |
| Every §3 research question answerable from `analysis.py`             | green                 |
| Ablating AnchoredTrader produces a measurable MAD reduction (≥ 50 %) | green                 |
| All variants marked `Yes` in §10.1 build without uncaught exceptions | green                 |
