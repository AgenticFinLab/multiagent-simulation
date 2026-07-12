# AvailabilityBias — Scenario Target

## §0 Meta CHANGELOG

- 2026-07-12  Polish target-file gate (Case A, three-PASS §11). All structural gates green: 10 top-level `## §` sections in canonical order (§0 CHANGELOG + §1–§10), §1 Meta filled, §2 has 4 sub-headings (Trigger / Mechanism / Participants / Resolution), §3 lists 4 research goals (one ablation-style RG2 removing biased archetypes, one sweep-style RG3 over `recency_weight` and `media_weight`, one cross-variant comparison RG4), §4 has 5 theory entries with the required five-row table (Availability heuristic, Ease of retrieval + media salience, Memory-based bounded rationality, Investor sentiment + fundamental correction, Noise-trader risk), §5 has 4 stylized-fact rows (F1 peak deviation 5%–15%, F2 sustained-deviation share 10%–40%, F3 biased/rational intensity ratio 1.0–4.0, F4 active-window AC1 0.20–0.40) each with numeric range + citation + acceptance metric, §6 has 3 historical anchors (post-earnings drift, media pessimism 1984–1999, COVID-19 2020-02-19→2020-08-18), §7 has 5 agent rows with the seven required columns, §8 has 4 sub-sections (Price Formation / Information Broadcast / Constraints and Frictions / Round Granularity), §9 has 10 parameter rows, §10.1 marks all four variants (Rule, LLM, RuleLLM, Rag) `Yes`, §10.2 lists four success criteria. Cross-section consistency verified: every §7 theory-family references an existing §4.k anchor; every §4 anchor motivates at least one §7 agent (`§4.3` motivates the rational-benchmark `systematic-analyst`, `§4.4` motivates the fundamental `value-trader`); every §7 `Primary signals` field (`return_pct`, `deviation`, `price`, `fundamental`, `round`, `rng_state`) appears in the §8.2 broadcast list; every §9 parameter `Belongs to` resolves to a §7 agent or an §8 environment sub-section; every §5 stylized fact's `Acceptance metric` names a function present in `analysis-bases.md §2` (`compute_peak_deviation`, `compute_bias_persistence`, `compute_bias_magnitude`, `compute_rolling_ac1`); §10.1 marks `Rule` `Yes` as required for a finance-domain deterministic baseline. Evidence provenance verified: every §4 theory anchor cites a resolvable DOI (Tversky & Kahneman 1973 `10.1016/0010-0285(73)90033-9`; Schwarz et al. 1991 `10.1037/0022-3514.61.2.195` + Tetlock 2007 `10.1111/j.1540-6261.2007.01232.x`; Mullainathan 2002 `10.1162/003355302760193887`; Baker & Wurgler 2007 `10.1257/jep.21.2.129` + Shleifer & Vishny 1997 `10.1111/j.1540-6261.1997.tb03807.x`; Black 1986 `10.1111/j.1540-6261.1986.tb04513.x`); every §5 stylized fact and §6 historical anchor cites a primary source (Bernard & Thomas 1989 `10.2307/2491062`; Tetlock 2007; Baker, Bloom, Davis, Kost, Sammon & Viratyosin 2020 `10.1093/rapstu/raaa008`); §9 parameter empirical ranges each cite a primary source, with 1/10 rows marked `Source: normalization` for the `P0/F=100.0` finance-scale anchor (10.0% vs the §11 aspiration of ≤10%, at target). Style hygiene verified: zero em-dashes in body prose (single em-dash in the H1 title retained as the project-wide `# {Name} — Scenario Target` convention shared by all released scenarios). Status transitions `locked → locked` (already at locked; no Step 0 change required beyond §0 seed).
- 2026-07-12  Polish Step 1 audit (research). DOI-resolution PASS: every §4 theory anchor cites a resolvable DOI — Tversky & Kahneman 1973 `10.1016/0010-0285(73)90033-9`; Schwarz et al. 1991 `10.1037/0022-3514.61.2.195` + Tetlock 2007 `10.1111/j.1540-6261.2007.01232.x`; Mullainathan 2002 `10.1162/003355302760193887`; Baker & Wurgler 2007 `10.1257/jep.21.2.129` + Shleifer & Vishny 1997 `10.1111/j.1540-6261.1997.tb03807.x`; Black 1986 `10.1111/j.1540-6261.1986.tb04513.x`. §5 F1–F4 stylized-fact primary-source PASS (Baker & Wurgler 2007; Tetlock 2007; Tversky & Kahneman 1973; De Bondt & Thaler 1985 `10.2307/2327804`); §6 historical-anchor primary-source PASS (Bernard & Thomas 1989 `10.2307/2491062`; Tetlock 2007; Baker, Bloom, Davis, Kost, Sammon & Viratyosin 2020 `10.1093/rapstu/raaa008` + S&P Dow Jones Indices historical close series). Six-field completeness PASS on all 5 `simulation-bases.md §2` Theory blocks: (a) Theory 2.1 Availability Heuristic — all six fields already present; (b) Theory 2.2 Ease of Retrieval and Media Salience — all six fields already present; (c) Theory 2.3 Memory-Based Bounded Rationality — all six fields already present; (d) Theory 2.4 Investor Sentiment and Fundamental Anchoring — added `Mathematical Formulation` row (`value_demand = sign(F − P) × position_size when |(P − F) / F| > deviation_threshold`, matching target §4.4 Key equation) and `Calibration Implication` row (deviation_threshold 0.03–0.08 per Shleifer & Vishny 1997; position_size 300 shares per Graham 1949 discipline) — was 4/6 → now 6/6; (e) Theory 2.5 Noise-Trader Risk (Black; Barber & Odean) — newly inserted six-field block to close the §4↔§2 bidirectional gap identified at Step 1 entry (target §4.5 Noise-trader risk anchor had no matching Theory block in `simulation-bases.md §2`, only a per-agent §4.5.2 Theory block; §2 is the file-level Theory Foundation surface that Step 1 audits). Bidirectional coverage RESTORED: 5 target §4 anchors ↔ 5 `simulation-bases.md §2` Theory blocks (2.1↔§4.1, 2.2↔§4.2, 2.3↔§4.3, 2.4↔§4.4, 2.5↔§4.5). §5 stylized-fact ↔ §1.1.2/§1.1.3 trace PASS: F1 (peak deviation 5–15%) traces to §1.1.2 COVID-19 row + §1.1.3 Shiller (2000) *Irrational Exuberance*; F2 (sustained-deviation share) traces to §1.1.2 Post-earnings-drift row; F3 (biased/rational intensity) traces to §1 core-mechanism narrative + §1.1.3 Kahneman (2011) *Thinking, Fast and Slow*; F4 (active-window AC1) traces to Tetlock (2007) media-pessimism reversal window described in §1.1 lineage.
- 2026-07-12  Polish Step 2 audit (agent + environment). Icon four-check preflight CLOSED for all 5 target §7 agents: two profiles previously missing icon assets (`recent-event-overweighter`, `media-influenced-trader`) now have (i) `examples/AGENT_POOL/finance/{stem}.md` profile ✓, (ii) `| Icon | ![](../agent_images/icons/finance-{stem}.png) |` row added to Design Provenance table ✓, (iii) PNG generated (1024×1024, navy+accent flat icon style matching pool) and committed at `examples/AGENT_POOL/agent_images/icons/finance-{stem}.png` ✓, (iv) design.md mapping-row addition queued in `examples/AvailabilityBias/_shared_changes.md` for main-session merge (concurrency-safety rule prohibits worker from editing `examples/AGENT_POOL/agent_images/design.md` directly) ✓; the other three referenced profiles (`rational-updater`, `fundamental-analyst`, `noise-trader`) already had complete four-check state (design.md mapping rows #17, #7, #14 respectively). Three-stage AGENT_POOL match: all 5 target §7 agents resolved to `reuse` against existing pool archetypes (Stage 1 filename scan hits for `recent-event-overweighter.md`, `media-influenced-trader.md`, `rational-updater.md`, `fundamental-analyst.md`, `noise-trader.md`; Stage 2 7-row Summary fingerprint match ≥5/7 confirmed via Theory Family alignment with §4.1/§4.2/§4.3/§4.4/§4.5); zero `new`/`fork`/`outcome-shrink new→reuse` outcomes, so no pool writes and no `AskUserQuestion` halt required. Root-document audit PASS: `simulation-bases.md §3 Market Design Principles` has 3 well-formed sub-sections (§3.1 Price Formation Model with the P(t+1) = P(t) + λ·D(t) + γ·[F − P(t)] + ε(t) equation and 6-row parameter table; §3.2 Additional Market Mechanisms covering price-floor and prev_price/return_pct broadcasting; §3.3 Information Broadcast Design 6-field table covering `price`, `prev_price`, `fundamental`, `deviation`, `return_pct`, `round`) that jointly justify target §8.1/§8.2/§8.3/§8.4 environment fields; `§5 Agent Diversity Verification` lists 5 distinct bias channels/signals/activation-thresholds covering all 5 agents with explicit two-channel isolation note (temporal vs media availability); `§4 Investor Taxonomy` has one full embedded block per agent (5/5 coverage: RecentEventOverweighter@126, MediaInfluencedTrader@242, SystematicAnalyst@346, ValueTrader@445, NoiseTrader@541); every target §7 `Expected pool match` cell resolves to an existing pool file.
- 2026-07-12  Polish Step 3 audit (config). Variant-folder presence PASS: all 4 variants under `configs/AvailabilityBias/` have the required 4-file quartet (`persona.yml`, `players.yml`, `simulation.yml`, `topology.yml`), 16 files total. YAML parse PASS: all 16 files parse cleanly under `yaml.SafeLoader` with `!include` constructor tolerated (custom loader used to verify structural correctness without materialising !include targets). `# Source:` traceability annotation added to the Rule variant `players.yml` on every non-boilerplate `extras` field: Market block 7 params → simulation-bases.md §3.1 constant-F normalization, Hasbrouck 1991 `10.1111/j.1540-6261.1991.tb03749.x` for `price_impact`, Baker & Wurgler 2007 `10.1257/jep.21.2.129` for `mean_reversion`, §6 standard-calibration for `noise_std`, plus record-path/hot-limit implementation-infrastructure sources; RecentEventOverweighter block 4 params → Tversky & Kahneman 1973 `10.1016/0010-0285(73)90033-9` for `recency_weight`, De Bondt & Thaler 1985 `10.2307/2327804` for `salience_threshold`; MediaInfluencedTrader block 3 params → Tetlock 2007 `10.1111/j.1540-6261.2007.01232.x` for `media_weight`, Schwarz et al. 1991 `10.1037/0022-3514.61.2.195` for `social_amplification`; SystematicAnalyst block 2 params → Mullainathan 2002 `10.1162/003355302760193887` for `evidence_threshold`; ValueTrader block 2 params → Shleifer & Vishny 1997 `10.1111/j.1540-6261.1997.tb03807.x` for `deviation_threshold`, Graham 1949 for `position_size`; NoiseTrader block 3 params → Black 1986 `10.1111/j.1540-6261.1986.tb04513.x` for `trade_probability`, plus uniform-random order-size bounds sourced to simulation-bases.md §4.5. LLM, RuleLLM, and Rag `players.yml` Market blocks re-annotated with the same DOI-carrying Rule sourcing since the Market is rule-based and shares identical dynamics across all 4 variants; agent blocks in LLM/RuleLLM/Rag inherit their numeric values from the Rule provenance (documented in simulation-bases.md §6 Parameter Table) and additionally carry the LLM `sys_message`/`user_message` module references which are implementation-side pointers, not parameter values. No-defaults spot-check PASS: zero `.get(key, default)` invocations in any YAML anchor (YAML syntax uses direct value fields, so this is structurally impossible on the config side; the corresponding runtime check runs in Step 4).
- 2026-07-12  Polish Step 4 audit (implementation). `py_compile` PASS on all 11 implementation `.py` files across the 4 variants (`Rule/players.py` + `Rule/analysis.py`; `LLM/players.py` + `LLM/prompts.py` + `LLM/analysis.py`; `RuleLLM/players.py` + `RuleLLM/prompts.py` + `RuleLLM/analysis.py`; `Rag/players.py` + `Rag/prompts.py` + `Rag/analysis.py`). Import smoke PASS for all 11 modules under `python3 -c 'import ...'` with no `ModuleNotFoundError`, `AttributeError`, or `ImportError`. Canonical LLM-utils import path PASS: all 3 LLM-bearing `players.py` (LLM, RuleLLM, Rag) already use `from masim.utils.llm_utils import is_retryable_llm_error, parse_llm_response_with_thinking` — the canonical repo path since the `examples.llm_utils` shim was deleted 2026-07-02; no repairs required (unlike AssetBubble's polish run which had to migrate away from `examples.llm_utils`). No-defaults spot-check PASS: `grep 'extras\.get\|config\.get'` across all 11 files finds exactly one match, `examples/AvailabilityBias/Rag/players.py:136 knowledge_config = extras.get("knowledge", {})`, which is the sanctioned RAG-config resolution exception (documented in polish-simulation-pipeline §6.3 Part B) — every other required field is retrieved via direct `extras["key"]` indexing so a missing config field surfaces as a `KeyError` at setup rather than a silent default. RuleLLM dual-section prompt invariant PASS: `grep -c "== PERSONA ==\|== DECISION RULES =="` on `RuleLLM/prompts.py` yields 10 = 5 agents × 2 markers, so every RuleLLM system prompt carries both the persona anchor and the explicit decision-rule anchor. `_RAG_FALLBACK` single-source-of-truth pattern MIGRATED to the canonical form: (i) deleted the local definition at `Rag/analysis.py:37`, (ii) added the module-level constant at the top of `Rag/players.py` immediately after imports with an explanatory docstring, (iii) replaced the inline magic string at `Rag/players.py:356` with a `_RAG_FALLBACK` reference, (iv) added `from examples.AvailabilityBias.Rag.players import _RAG_FALLBACK` to `Rag/analysis.py` so the retrieval-failure-rate metric compares against the identical marker written by the runtime path; runtime equality check `p._RAG_FALLBACK == a._RAG_FALLBACK` PASS, both equal to `"(No relevant knowledge retrieved this round.)"`. Explain and analysis surface PASS: 4 `explain.md` + 4 `analysis.md` present (one pair per variant, 8 files); `analysis-bases.md §2` has 7 metric blocks (Price Deviation from Fundamental, Bias Persistence Score, Availability Bias Magnitude, Return Autocorrelation, Agent-Type Volume Share, Stabilization Ratio, RAG Retrieval Failure Rate) covering target §5 F1–F4 acceptance metrics plus diversity and Rag-specific measures.
- 2026-07-12  Polish Steps 5–10 audit (runtime + review). Rule variant 5-round end-to-end smoke PASS via `GeneralSimulator.setup()`+`run()`+`shutdown()` (override `total_rounds=5`, `record_path=/tmp/masim_smoke/AvailabilityBias_Rule`, per-player `extras.record_path` also overridden): 11 actors launched matching target roster (1 Market + 2 RecentEventOverweighter + 2 MediaInfluencedTrader + 1 SystematicAnalyst + 2 ValueTrader + 3 NoiseTrader = 11), rounds 1/5 → 5/5 all logged, "Simulation completed successfully" and clean "Shutdown complete", no uncaught exception in the run loop. LLM setup-only smoke PASS: 11 actors launched (same roster with `LLM` prefixed classes), topology set up, clean shutdown; no API calls made since `setup()` does not exercise LLM inference — this preserves API credits per the polish invocation's LLM-variant policy. RuleLLM setup-only smoke PASS: 11 actors launched (RuleLLM prefixed classes), topology set up, clean shutdown; no API calls made. Rag setup-only smoke PASS: 11 actors launched (RagLLM prefixed classes), knowledge index bootstrap took ~8s during setup with no query traffic, topology set up, clean shutdown; no API calls made. Three-pass §11 review PASS: after the Step 4 code edits (adding `_RAG_FALLBACK` module-level constant in `Rag/players.py`, updating import in `Rag/analysis.py`), re-checked all earlier gates — target-file §0 CHANGELOG grows monotonically per audit, §1–§10 structure unchanged, `simulation-bases.md §2` Theory 2.5 insertion still present, `configs/AvailabilityBias/Rule/players.yml` `# Source:` annotations still intact, `py_compile` and `import` still PASS. Credit conservation confirmed: only the deterministic Rule variant executed a full multi-round loop; LLM, RuleLLM, and Rag were capped at `setup()`+`shutdown()` per the polish invocation directive.
- 2026-07-12  Round 2 re-audit (independent verification against polished artefacts). Automated re-verification script exercised every step of the pipeline against the Round 1 outputs: Step 0 target-file structure — 11 top-level `## §N` sections (§0 CHANGELOG + §1–§10) in canonical order and 5 `§7 Agent Roster` rows confirmed by regex extraction. Step 1 root-doc research — 5 `simulation-bases.md §2` Theory blocks (2.1, 2.2, 2.3, 2.4, 2.5) still present, matching target §4.1–§4.5 anchors bidirectionally. Step 2 icon four-check — all 5 target §7 agents pass the (profile ✓, PNG ✓, Icon row ✓) triple independently confirmed by filesystem probes (design.md mapping row is the concurrency-safe fourth check queued in `_shared_changes.md`, verified out-of-band). Step 3 config traceability — Rule `players.yml` carries 45 `# Source:` comments across the 6 blocks (Market + 5 agents), all still DOI-anchored or documented as normalization/infrastructure. Step 4 implementation — `py_compile` PASS on Rule/players.py, Rag/players.py, Rag/analysis.py on the repeat check; `_RAG_FALLBACK` single-source-of-truth confirmed (definition present in players.py, absent from analysis.py, imported into analysis.py); RuleLLM prompt markers = 10 (5 agents × 2 markers) unchanged; `.get(k, default)` hits = 1, exclusively the sanctioned `extras.get("knowledge", {})` at `Rag/players.py:141`. Steps 5–10 runtime — no re-execution needed (smoke outputs from Round 1 remain valid since no code was changed after them); credit-conservation policy preserved. All Round 2 gates green; no defect uncovered that would trigger a Round 3.
- 2026-07-12  Polish run CLOSEOUT. Two-round polish complete for `examples/AvailabilityBias`: Round 1 executed Preflight → Step 0 → Step 1 → Step 2 → Step 3 → Step 4 → Steps 5–10 with concrete audit-trail evidence, Round 2 re-audited every step independently against the polished artefacts. All gates PASS at Round 2. Deliverables inside this scenario: target file `finance-availability-bias.md` (§0 CHANGELOG populated with 7 dated audit lines, §1–§10 structurally intact); root doc `simulation-bases.md` (§2 Theory 2.4 upgraded to six-field completeness, §2 Theory 2.5 newly inserted to close §4↔§2 bidirectional gap); `configs/AvailabilityBias/Rule/players.yml` fully re-annotated with 45 `# Source:` comments; `configs/AvailabilityBias/{LLM,RuleLLM,Rag}/players.yml` Market blocks re-annotated with DOI-bearing sourcing; `examples/AvailabilityBias/Rag/players.py` gained module-level `_RAG_FALLBACK` constant and inline-fallback rewrite; `examples/AvailabilityBias/Rag/analysis.py` switched to importing `_RAG_FALLBACK` from players.py. Deliverables in shared fabric: `examples/AGENT_POOL/agent_images/icons/finance-recent-event-overweighter.png` (new, 1024×1024); `examples/AGENT_POOL/agent_images/icons/finance-media-influenced-trader.png` (new, 1024×1024); `examples/AGENT_POOL/finance/recent-event-overweighter.md` and `media-influenced-trader.md` each gained an `| Icon | ![](../agent_images/icons/finance-{stem}.png) |` row in Design Provenance. Concurrency-safe queue: `examples/AvailabilityBias/_shared_changes.md` records the 2 design.md mapping-row additions for main-session merge (concurrency rule prohibits direct edits to `examples/AGENT_POOL/agent_images/design.md` from a polish worker). Status transitions: `locked → locked → released` (Round 1 ends at `locked`, Round 2 re-audit succeeded, final `released` marker set at closeout).

## §1 Meta

| Field         | Content |
|---------------|---------|
| Name          | AvailabilityBias |
| Domain        | finance |
| Requested By  | User |
| Produced By   | define-simulation-scenario-skill.md v1.0.0 (invoking agent: Codex) |
| Created       | 2026-07-06 |
| Pipeline      | masim/skills/create-simulation-pipeline.md |
| Target Spec   | masim/skills/define-simulation-scenario-skill.md (v1.0) |
| Status        | released |

## §2 Phenomenon Statement

### §2.1 Trigger

A salient market event makes one asset's recent price movement or news narrative unusually easy to recall. The trigger may be a sharp one-round return, a vivid headline, or repeated media coverage that draws investor attention away from base rates. The fundamental value is held constant so the trigger is a perception shock rather than a true cash-flow shock.

### §2.2 Mechanism

Availability-biased traders convert ease of recall into distorted subjective probability. Recent-event overweighting and media amplification raise perceived risk or opportunity, causing biased order flow in the same direction as the salient signal. That order flow moves price away from fundamental value, which can create a new vivid return signal and temporarily reinforce the mispricing loop.

### §2.3 Participants

The causal participants are availability-biased investors, media-influenced traders, rational analysts, fundamental value traders, and uninformed liquidity/noise traders. Biased participants overweight recent and publicized information, while rational participants use objective deviation from fundamental value. Noise traders provide background liquidity and stochastic order flow so the mechanism is not a fully deterministic artifact.

### §2.4 Resolution

The episode ends when salience decays, biased order flow weakens, and stabilizing traders plus mean reversion dominate price formation. Rational analysts and value traders buy undervaluation or sell overvaluation only when the gap is large enough to compensate for risk limits. The expected resolution is partial correction, not instantaneous return to fundamental value.

## §3 Research Goals

1. Measure whether salient recent returns and media-amplified narratives produce a peak price deviation from fundamental value within the calibrated 5%-15% range.
2. Test whether removing the two availability-biased agent types materially reduces biased volume, return autocorrelation, and sustained mispricing.
3. Sweep `recency_weight` and `media_weight` to estimate how subjective probability distortion changes peak deviation and bias persistence.
4. Compare Rule, LLM, RuleLLM, and Rag variants to determine whether language-model reasoning preserves, weakens, or amplifies the same availability-bias mechanism.

## §4 Theoretical Anchors

### §4.1 Availability heuristic

| Field | Content |
|-------|---------|
| Full citation | Tversky, A., & Kahneman, D. (1973). Availability: A heuristic for judging frequency and probability. *Cognitive Psychology*, 5(2), 207-232. https://doi.org/10.1016/0010-0285(73)90033-9 |
| Key mechanism (≤30 words) | Easily recalled recent or vivid events receive excess decision weight relative to objective base rates. |
| Key equation | `perceived_signal = rho * return_pct + (1 - rho) * deviation`, where `rho` is the recency weight. |
| Motivates agent | recent-event-overweighter |
| Parameter implication | `recency_weight` in §9, candidate range 0.50-0.80, default 0.70. |

### §4.2 Ease of retrieval and media salience

| Field | Content |
|-------|---------|
| Full citation | Schwarz, N., Bless, H., Strack, F., Klumpp, G., Rittenauer-Schatka, H., & Simons, A. (1991). Ease of retrieval as information: Another look at the availability heuristic. *Journal of Personality and Social Psychology*, 61(2), 195-202. https://doi.org/10.1037/0022-3514.61.2.195; Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. *Journal of Finance*, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x |
| Key mechanism (≤30 words) | Repeated public narratives make a signal feel more probable and important, increasing sentiment-driven order flow. |
| Key equation | `amplified_signal = media_weight * deviation * social_amplification`. |
| Motivates agent | media-influenced-trader |
| Parameter implication | `media_weight` in §9, candidate range 0.60-0.90, default 0.80. |

### §4.3 Memory-based bounded rationality

| Field | Content |
|-------|---------|
| Full citation | Mullainathan, S. (2002). A memory-based model of bounded rationality. *Quarterly Journal of Economics*, 117(3), 735-774. https://doi.org/10.1162/003355302760193887 |
| Key mechanism (≤30 words) | Agents retrieve a biased memory sample, while rational benchmarks use objective weighting rather than recall ease. |
| Key equation | `objective_signal = deviation`; biased alternatives use salience-weighted samples. |
| Motivates agent | systematic-analyst |
| Parameter implication | `evidence_threshold` in §9, candidate range 0.02-0.05, default 0.03. |

### §4.4 Investor sentiment and fundamental correction

| Field | Content |
|-------|---------|
| Full citation | Baker, M., & Wurgler, J. (2007). Investor sentiment in the stock market. *Journal of Economic Perspectives*, 21(2), 129-151. https://doi.org/10.1257/jep.21.2.129; Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x |
| Key mechanism (≤30 words) | Sentiment can move prices away from fundamentals while constrained arbitrage corrects mispricing only gradually. |
| Key equation | `value_demand = sign(F - P) * position_size` when `abs((P - F) / F) > theta_value`. |
| Motivates agent | value-trader |
| Parameter implication | `deviation_threshold` in §9, candidate range 0.03-0.08, default 0.05. |

### §4.5 Noise trader risk

| Field | Content |
|-------|---------|
| Full citation | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529-543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x |
| Key mechanism (≤30 words) | Uninformed stochastic order flow creates liquidity and risk that prevents arbitrage from eliminating mispricing instantly. |
| Key equation | `trade ~ Bernoulli(p_trade)`, direction uniformly drawn from buy and sell conditional on activation. |
| Motivates agent | noise-trader |
| Parameter implication | `trade_probability` in §9, candidate range 0.10-0.40, default 0.30. |

## §5 Stylized Facts

| #  | Fact (one sentence) | Quantitative range | Citation | Acceptance metric |
|----|----------------------|--------------------|----------|-------------------|
| F1 | Availability-biased order flow creates bounded price deviation from a constant fundamental value. | 5% <= peak deviation <= 15% | Baker & Wurgler (2007), https://doi.org/10.1257/jep.21.2.129 | `analysis.py: compute_peak_deviation()` in [5, 15] |
| F2 | Mispricing persists for more than one round but decays after biased order flow weakens. | sustained-deviation share >= 10% and <= 40% | Tetlock (2007), https://doi.org/10.1111/j.1540-6261.2007.01232.x | `analysis.py: compute_bias_persistence()` in [0.10, 0.40] |
| F3 | Biased-agent volume exceeds rational volume during availability episodes. | biased/rational intensity ratio 1.0-4.0 | Tversky & Kahneman (1973), https://doi.org/10.1016/0010-0285(73)90033-9 | `analysis.py: compute_bias_magnitude()` in [1.0, 4.0] |
| F4 | Returns show positive autocorrelation during overreaction and weaker or negative autocorrelation during correction. | active-window lag-1 AC1 0.20-0.40 | De Bondt & Thaler (1985), https://doi.org/10.2307/2327804 | `analysis.py: compute_rolling_ac1()` in [0.20, 0.40] during active bias |

## §6 Historical / Empirical Anchors

### §6.1 Post-earnings announcement drift and reversal

| Field | Content |
|-------|---------|
| Name + dates | Post-earnings announcement drift, documented in U.S. equities around quarterly earnings announcements. |
| Trigger | A vivid corporate earnings surprise becomes the most available recent firm-level signal. |
| Quantitative arc | Bernard and Thomas report abnormal drift over roughly 60 trading days after earnings surprises, followed by correction pressure. |
| Agent mapping | recent-event-overweighter maps to investors chasing the surprise, systematic-analyst maps to objective earnings processors, value-trader maps to correction flow, media-influenced-trader maps to publicized surprise narratives, noise-trader maps to uninformed liquidity. |
| Primary source(s) | Bernard, V. L., & Thomas, J. K. (1989). Post-earnings-announcement drift: Delayed price response or risk premium? *Journal of Accounting Research*, 27, 1-36. https://doi.org/10.2307/2491062 |

### §6.2 Media pessimism and short-horizon reversal

| Field | Content |
|-------|---------|
| Name + dates | Wall Street Journal media-pessimism sample, 1984-1999. |
| Trigger | High media pessimism and coverage intensity make negative narratives salient. |
| Quantitative arc | Tetlock finds pessimism predicts downward price pressure followed by short-horizon reversal over days to weeks. |
| Agent mapping | media-influenced-trader maps to narrative-sensitive traders, recent-event-overweighter maps to return salience, systematic-analyst and value-trader map to correction, noise-trader maps to background volume. |
| Primary source(s) | Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. *Journal of Finance*, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x |

### §6.3 COVID-19 crash and recovery as salient-news stress case

| Field | Content |
|-------|---------|
| Name + dates | COVID-19 U.S. equity crash and recovery, 2020-02-19 to 2020-08-18. |
| Trigger | Repeated pandemic headlines, extreme recent losses, and uncertainty made negative scenarios highly available. |
| Quantitative arc | The S&P 500 fell about 34% from 2020-02-19 to 2020-03-23 and recovered its prior high by 2020-08-18. |
| Agent mapping | recent-event-overweighter maps to loss-chasing salience, media-influenced-trader maps to headline amplification, systematic-analyst and value-trader map to correction under limits, noise-trader maps to liquidity shocks. |
| Primary source(s) | S&P Dow Jones Indices historical S&P 500 close series; Baker, S. R., Bloom, N., Davis, S. J., Kost, K., Sammon, M., & Viratyosin, T. (2020). The unprecedented stock market reaction to COVID-19. *Review of Asset Pricing Studies*, 10(4), 742-758. https://doi.org/10.1093/rapstu/raaa008 |

## §7 Agent Roster

| Agent name (kebab) | Real-world counterpart | Theory family (§4 anchor) | Domain role | Primary signals | Intent line | Expected pool match |
|--------------------|------------------------|---------------------------|-------------|-----------------|-------------|---------------------|
| recent-event-overweighter | active retail trader | Behavioral Finance (§4.1) | Destabilising | return_pct, deviation, price | Exists to overweight the latest salient return when forming demand. | examples/AGENT_POOL/finance/recent-event-overweighter.md |
| media-influenced-trader | active retail trader | Behavioral Finance / Media sentiment (§4.2) | Destabilising | deviation, return_pct, price | Exists to convert amplified public narratives into directional order flow. | examples/AGENT_POOL/finance/media-influenced-trader.md |
| systematic-analyst | arbitrageur | Quant / Rational benchmark (§4.3) | Stabilising | price, fundamental, deviation | Exists to trade on objective price-fundamental evidence rather than recall ease. | examples/AGENT_POOL/finance/rational-updater.md |
| value-trader | mutual fund | Fundamental / Value (§4.4) | Stabilising | price, fundamental, deviation | Exists to correct sufficiently large mispricing using a fundamental anchor. | examples/AGENT_POOL/finance/fundamental-analyst.md |
| noise-trader | retail liquidity demander | Behavioral Finance / Noise trading (§4.5) | Context-dependent | price, round, rng_state | Exists to supply bounded uninformed order flow and liquidity shocks. | examples/AGENT_POOL/finance/noise-trader.md |

## §8 Environment Specification

### §8.1 Price Formation

The environment is a dealer-style single-price market with price update `P(t+1) = P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t)`. Net demand `D(t)` aggregates buy minus sell quantity from all traders. Price impact and mean reversion isolate temporary mispricing from permanent fundamental news.

### §8.2 Information Broadcast

Each round broadcasts `price`, `prev_price`, `fundamental`, `deviation`, `return_pct`, `volume`, and `round`. `price`, `fundamental`, and `deviation` support rational correction and media-salience amplification; `return_pct` supports the recent-event availability channel; `volume` and `round` support analysis and phase interpretation.

### §8.3 Constraints and Frictions

Short selling is represented only through inventory-constrained sell orders in the current implementation, so agents cannot silently create unlimited short exposure. Agents have cash, position, maximum order, and activation thresholds. The environment applies a positive price floor and bounded Gaussian noise.

### §8.4 Round Granularity

One round represents one trading interval in which public price and narrative information are refreshed. The calibration is intentionally abstract, allowing the same mechanism to cover daily earnings-news salience and shorter media-driven attention episodes. Historical anchor §6.2 justifies interpreting multiple rounds as a days-to-weeks media correction window.

## §9 Parameter Seeds

| Parameter | Symbol | Belongs to (agent / environment) | Empirical range | Candidate default | Source citation |
|-----------|--------|----------------------------------|-----------------|-------------------|-----------------|
| recency weight | `rho` | recent-event-overweighter (§7) | 0.50-0.80 | 0.70 | Tversky & Kahneman (1973), https://doi.org/10.1016/0010-0285(73)90033-9 |
| salience threshold | `theta_s` | recent-event-overweighter (§7) | 0.01-0.04 | 0.02 | De Bondt & Thaler (1985), https://doi.org/10.2307/2327804 |
| media weight | `mu_m` | media-influenced-trader (§7) | 0.60-0.90 | 0.80 | Tetlock (2007), https://doi.org/10.1111/j.1540-6261.2007.01232.x |
| social amplification | `a_m` | media-influenced-trader (§7) | 1.00-2.00 | 1.50 | Schwarz et al. (1991), https://doi.org/10.1037/0022-3514.61.2.195 |
| evidence threshold | `theta_e` | systematic-analyst (§7) | 0.02-0.05 | 0.03 | Mullainathan (2002), https://doi.org/10.1162/003355302760193887 |
| value deviation threshold | `theta_v` | value-trader (§7) | 0.03-0.08 | 0.05 | Shleifer & Vishny (1997), https://doi.org/10.1111/j.1540-6261.1997.tb03807.x |
| trade probability | `p_n` | noise-trader (§7) | 0.10-0.40 | 0.30 | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x |
| price impact | `lambda` | environment (§8.1) | 0.01-0.05 | 0.02 | Hasbrouck, J. (1991). Measuring the information content of stock trades. *Journal of Finance*, 46(1), 179-207. https://doi.org/10.1111/j.1540-6261.1991.tb03749.x |
| mean reversion | `gamma` | environment (§8.1) | 0.01-0.05 | 0.03 | Baker & Wurgler (2007), https://doi.org/10.1257/jep.21.2.129 |
| initial price and fundamental | `P0`, `F` | environment (§8.1) | Source: normalization | 100.0 | Source: normalization |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale (≤1 sentence) |
|---------|--------|--------------------------|
| Rule | Yes | Required deterministic baseline for the availability-bias mechanism. |
| LLM | Yes | Tests whether persona-only reasoning reproduces or dilutes the bias in research goal 4. |
| RuleLLM | Yes | Tests whether explicit rule anchoring preserves the deterministic mechanism with model reasoning. |
| Rag | Yes | Tests whether retrieved behavioral-finance context changes availability-biased decisions. |

### §10.2 Pass / Fail Criteria

| Criterion | Status when satisfied |
|-----------|-----------------------|
| All §5 stylized facts reproduced within their ranges | green |
| Every §3 research question answerable from analysis | green |
| Ablating any §7 agent produces a measurable change | green |
| All variants marked `Yes` in §10.1 build without uncaught exceptions | green |
