# EchoChamber Rule Analysis Plan

## §1 Objectives

The Rule analysis verifies formula-driven polarization dynamics and provides the
baseline for comparing API variants.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Polarization amplification | `def compute_polarization_amplification(polarization) -> float` | `analysis-bases.md §2.1` |
| Polarization persistence | `def compute_polarization_persistence(polarization) -> float` | `analysis-bases.md §2.2` |
| Cluster separation | `def compute_cluster_separation(cluster_series) -> dict` | `analysis-bases.md §2.3` |
| Polarize activity | `def compute_polarize_activity(polarize_counts) -> float` | `analysis-bases.md §2.4` |
| Depolarize activity | `def compute_depolarize_activity(depolarize_counts) -> float` | `analysis-bases.md §2.5` |
| Opinion dispersion | `def compute_opinion_dispersion(agent_opinions) -> float` | `analysis-bases.md §2.6` |
| Quality checks | `compute_api_quality(actions, rag_contexts)` validates the shared special schema; RAG coverage is optional for Rule | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Analyze polarization, mean opinion, cluster separation, polarize/depolarize
activity, and per-agent opinion trajectories.

## §4 Phase Analysis

Use initialization, reinforcement, cluster formation, depolarizing response, and
terminal state phases from `analysis-bases.md §4`.

## §5 Cross-Variant Comparison

Rule is compared with LLM, RuleLLM, and Rag on polarization path, activity
composition, and final opinion dispersion.

## §6 Expected Results and Validation Criteria

A full Rule sample should complete 200 rounds and produce finite polarization,
cluster, activity, and opinion series. Missing metric directories, empty series,
invalid JSON, mismatched series lengths, and out-of-range state fail explicitly.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_echochamber_dynamics.png`, `02_echochamber_analysis.png`, and
`03_summary.png`.

---

## §4 Variant-Specific Observable Phenomena

Rule is the deterministic reference variant for EchoChamber. Given a fixed
seed, agent role behaviors resolve to formula-driven `polarize` / `neutral` /
`depolarize` actions with no reasoning stochasticity or retrieval noise.

| Phenomenon | How to Observe | Contrast with Baseline |
|---|---|---|
| Deterministic polarization ramp | `01_echochamber_dynamics.png` (Panel 1) shows a smooth monotonic climb across the reinforcement phase | This is the baseline; LLM variants will show jitter |
| Threshold-locked cluster formation | `01_echochamber_dynamics.png` (Panel 2) — orange `cluster_separation` curve steps up when polarizing roles cross their formula thresholds | Rule sets the reference cluster-separation trajectory |
| Symmetric activity balance | `01_echochamber_dynamics.png` (Panel 3) — red (polarize) and green (−depolarize) bars mirror around zero with rule-consistent counts | Baseline value for `depolarize_to_polarize_ratio` |
| Reproducible peak round | `summary.json → metrics.polarization.peak_round` is stable across reruns | LLM peak drifts by ±5–10 rounds; Rag drifts less |
| Analytic dispersion floor | `summary.json → metrics.opinion_dispersion` matches the analytic value from polarizing role parameters | Reference lower bound for dispersion |

Rule agents implement `social_action` selection via formula only — no LLM
completion round-trips — so `compute_api_quality()` should report a
`valid_action_rate` of 1.0 with `retrieval_coverage = 0.0` (no RAG retrieval).

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable | Phenomenon Clarity | Recommended for |
|---|---|---|---|
| 100 | Reinforcement + partial cluster formation | Low — second-half persistence sample thin | Quick smoke test |
| 200 | Full reinforcement → depolarizing response → terminal arc | Medium | Standard runs (matches §6 expected result) |
| 500 | Statistical robustness across seeds; stable `polarization_persistence` | High | Research-grade cross-variant contrasts |

### Agent Count Scaling

| Agent Count | Expected Observable | Environment Dynamics |
|---|---|---|
| Minimum viable (~10) | Cluster separation still forms but noisier; per-agent trajectories in Panel 4 are legible | Sparse — role imbalance sensitive |
| Recommended (30–50) | Clean polarization plateau; stable cluster centroids | Full echo-chamber dynamics visible |
| Large (100+) | Very stable population statistics; per-agent legend truncated to ≤10 | Diminishing marginal insight per agent |

### Parameter Sensitivity (Variant-Specific)

| Parameter | Change | Expected Effect on This Variant's Analysis |
|---|---|---|
| Polarizing-role population share | +50% | Higher `polarization_amplification`; earlier `peak_round`; larger `max_separation` |
| Polarizing-role population share | −50% | Lower amplification; peak may not resolve within 200 rounds |
| Depolarizer / bridge-builder count | +50% | Higher `depolarize_to_polarize_ratio`; lower `polarization_persistence` |
| Depolarizer / bridge-builder count | −50% | Persistent polarization plateau; `final_polarization` closer to peak |
| Interaction / influence strength | +50% | Steeper reinforcement slope; higher `opinion_dispersion` |

---

## §6 Output Files Reference

All outputs are written to `EXPERIMENT/EchoChamber/Rule/analysis/`.

| Output File | Generated By | Contents | Interpretation |
|---|---|---|---|
| `summary.json` | `main()` | Rounds, polarization stats, opinion stats, cluster stats, activity stats, dispersion, validation | `validation.is_valid` gates §6 bounds check; `metrics.polarization.amplification_ratio` reports §2.1 |
| `00_investor_bids.png` | `create_visualizations()` | 2×2 EchoChamber analysis panel (agent-opinion / action panel alias) | Panel 4 shows per-agent opinion trajectories — echo chambers appear as bifurcating fans |
| `01_echochamber_dynamics.png` | `create_visualizations()` | Same 2×2 panel written under dynamics alias | Panel 1 (polarization) and Panel 2 (mean opinion + cluster separation) are the primary dynamics view |
| `02_echochamber_analysis.png` | `create_visualizations()` | Same 2×2 panel written under analysis alias | Cross-referenced in cross-variant reports |
| `03_summary.png` | `create_visualizations()` | Same 2×2 panel written under summary alias | Compact panel referenced from top-level summaries |

The four PNG aliases are all the same 2×2 figure produced by `create_visualizations()`; they exist to satisfy the standard-output filename contract in `analysis-bases.md §7`.
