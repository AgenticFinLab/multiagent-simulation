# EchoChamber — Scenario Target

## §0 Meta CHANGELOG

- 2026-07-16  Polish target-file gate (Case B): target file reverse-constructed from existing artefacts (simulation-bases.md, analysis-bases.md, 4 built variants). Status set to `locked` for polish audit.
- 2026-07-16  Polish run Round 1 against skill baseline (define/agent-design/implement).
             - Step 0 (target-file gate): Case B, reverse-constructed from downstream artefacts
             - Step 1 (research audit):   Theory blocks present for all 5 archetypes; no DOIs to resolve (opinion-dynamics literature cited by name/year only — accepted gap for non-finance domain)
             - Step 2 (agent + env):      5 agents polished, AGENT_POOL three-stage match = reuse (stubs under finance/), icon-resolution gate PASS (5 PNGs generated, 5 mapping rows #75-#79 added to design.md), root doc §3/§5/§7 PASS
             - Step 3 (config audit):     4 variants polished (Rule/LLM/RuleLLM/Rag), all 16 YAML files parse, # Source: traceability present
             - Step 4 (impl audit):       4 variants polished — py_compile PASS, import smoke PASS, no-defaults PASS, RuleLLM dual-section PASS (5+5), _RAG_FALLBACK single-source fix applied
             - Steps 5-10 (review+smoke): Rule 5-round e2e PASS, LLM/RuleLLM/Rag setup-only PASS
- 2026-07-16  Polish run Round 2 re-audit: all gates re-verified green. Status transition locked -> released.

## §1 Meta

| Field         | Content                                                |
|---------------|--------------------------------------------------------|
| Name          | EchoChamber                                            |
| Domain        | opinion                                                |
| Requested By  | a77                                                    |
| Produced By   | polish-simulation-pipeline.md (reverse-constructed)    |
| Created       | 2026-07-16                                             |
| Pipeline      | masim/skills/polish-simulation-pipeline.md             |
| Target Spec   | masim/skills/define-simulation-scenario-skill.md       |
| Status        | released                                               |

## §2 Phenomenon Statement

### §2.1 Trigger

The phenomenon starts from a population of agents with moderate initial opinions distributed across the spectrum [-1, 1]. Homophilic interaction (preferential engagement with like-minded others) triggers a self-reinforcing dynamic in which in-group consensus drives opinions toward extremes.

### §2.2 Mechanism

The core mechanism is echo-chamber amplification: agents who share the same opinion sign reinforce each other's views through social proof and conformity, while discounting opposing views. This positive feedback loop increases population polarization and cluster separation. Centripetal forces (critical evaluation, bridge-building) provide a countervailing mechanism.

### §2.3 Participants

The causal participants are ideologues (in-group amplifiers), conformists (group-opinion adopters), critical thinkers (evidence-based resisters), bridge builders (cross-group engagers), and passive followers (low-engagement drifters).

### §2.4 Resolution

The simulation resolves toward a dynamic equilibrium between polarizing forces (ideologues, conformists) and depolarizing forces (critical thinkers, bridge builders), modulated by weak centripetal pull and noise. Final polarization depends on the balance of these forces across 200 rounds.

## §3 Research Goals

1. Does heterogeneous opinion interaction produce measurable polarization amplification above the initial level?
2. Does removing or weakening ideologue and conformist roles reduce peak polarization?
3. How sensitive is final polarization to the polarization_impact and centripetal_force parameters?
4. Do critical thinkers and bridge builders provide effective depolarizing pressure when cluster separation is elevated?
5. Do Rule, LLM, RuleLLM, and Rag variants differ measurably in polarization dynamics, action composition, and schema validity?

## §4 Theoretical Anchors

### §4.1 Echo Chambers and Group Polarization

| Field | Content |
|-------|---------|
| Full citation | Sunstein, C. R. (2001). *Republic.com*. Princeton University Press. |
| Key mechanism | Like-minded discussion in deliberative enclaves drives group members toward more extreme versions of their initial views. |
| Key equation | `opinion_update = in_group_weight * (mean_opinion * extremity_boost - my_opinion)` |
| Motivates agent | ideologue |
| Parameter implication | `in_group_weight` in [0.4, 0.8], `extremity_boost` in [1.1, 1.5], `out_group_discount` in [0.01, 0.10] |

### §4.2 Conformity and Social Proof

| Field | Content |
|-------|---------|
| Full citation | Asch, S. E. (1951). Effects of group pressure upon the modification and distortion of judgments. In H. Guetzkow (Ed.), *Groups, Leadership, and Men*. |
| Key mechanism | Individuals align with perceived group opinion through informational and normative conformity. |
| Key equation | `opinion_update = conformity * (local_group_mean - my_opinion)` |
| Motivates agent | conformist |
| Parameter implication | `conformity` in [0.5, 0.9], `group_proximity_threshold` in [0.2, 0.5] |

### §4.3 Persuasive Arguments and Critical Evaluation

| Field | Content |
|-------|---------|
| Full citation | Isenberg, D. J. (1986). Group polarization: A critical review and meta-analysis. *Journal of Personality and Social Psychology*, 50(6), 1141-1151. |
| Key mechanism | Critical thinkers resist social proof and move opinion slowly on merit alone; high polarization is treated as evidence of groupthink. |
| Key equation | `evidence_signal = -my_opinion * evidence_sensitivity * polarization` |
| Motivates agent | critical-thinker |
| Parameter implication | `evidence_sensitivity` in [0.4, 0.8], `critical_weight` in [0.3, 0.7] |

### §4.4 Cross-Cutting Exposure and Deliberative Democracy

| Field | Content |
|-------|---------|
| Full citation | Pariser, E. (2011). *The Filter Bubble: What the Internet Is Hiding from You*. Penguin Press. |
| Key mechanism | Cross-cutting exposure increases contact between opposing groups and reduces cluster separation; bridge builders find common ground. |
| Key equation | `opinion_update = bridge_weight * (0 - my_opinion) * centering_tendency` |
| Motivates agent | bridge-builder |
| Parameter implication | `bridge_strength` in [0.5, 1.0], `centering_tendency` in [0.3, 0.7] |

### §4.5 Passive Participation and Mass Communication

| Field | Content |
|-------|---------|
| Full citation | Lazarsfeld, P. F., & Merton, R. K. (1954). Friendship as social process: A substantive and methodological analysis. In M. Berger et al. (Eds.), *Freedom and Control in Modern Society*. |
| Key mechanism | Most participants are passive receivers who drift toward the mean without strong agency, providing background population inertia. |
| Key equation | `drift = drift_rate * (mean_opinion - my_opinion)` |
| Motivates agent | passive-follower |
| Parameter implication | `drift_rate` in [0.05, 0.2], `engagement_probability` in [0.1, 0.5] |

## §5 Stylized Facts

| # | Fact | Acceptance metric |
|---|------|-------------------|
| F1 | Group discussion among like-minded individuals produces more extreme group positions than individual pre-discussion positions. | Peak polarization > initial polarization (amplification > 1.0) |
| F2 | Conformity pressure moves individuals toward the perceived group mean. | Conformist opinion trajectories converge toward group clusters. |
| F3 | Cross-cutting exposure reduces polarization when clusters are separated. | Bridge-builder depolarize intensity correlates with cluster separation. |
| F4 | Passive majorities drift slowly and do not independently generate polarization. | PassiveFollower action_type is predominantly neutral. |
| F5 | Polarization exhibits persistence once established. | Second-half mean polarization > initial_polarization. |

## §6 Historical / Empirical Anchors

### §6.1 Political Enclave Deliberation

Like-minded political discussion creates more extreme group positions by validating shared assumptions and excluding dissenting evidence (Sunstein 2002, 2009).

### §6.2 Algorithmic Filter Bubbles

Personalized content feeds reduce cross-cutting exposure and increase information homogeneity, contributing to cluster separation (Pariser 2011; Bakshy et al. 2015).

### §6.3 Online Community Radicalization

Highly engaged online communities reward strong in-group signals and discount out-group claims, producing drift toward group extremes (Bail et al. 2018).

## §7 Agent Roster

| Agent | Kebab name | Theory family | Domain role | Primary signals | Count |
|-------|-----------|---------------|-------------|-----------------|-------|
| Ideologue | ideologue | Echo Chambers (Sunstein) | Destabilising | mean_opinion, my_opinion sign match | 6 |
| Conformist | conformist | Conformity (Asch) | Destabilising | mean_opinion, local_group_mean | 5 |
| CriticalThinker | critical-thinker | Persuasive Arguments (Isenberg) | Stabilising | polarization, my_opinion | 3 |
| BridgeBuilder | bridge-builder | Cross-Cutting Exposure (Pariser) | Stabilising | cluster_separation | 2 |
| PassiveFollower | passive-follower | Mass Communication (Lazarsfeld) | Neutral | mean_opinion | 4 |

## §8 Environment Specification

### §8.1 State Update (Polarization Dynamics)

```
polarization(t+1) = clamp(
    polarization(t) + polarization_impact * net_polarization
    + centripetal_force * (equilibrium - polarization(t)) + noise,
    0, 1
)
```

### §8.2 Broadcast Payload

`{polarization, prev_polarization, polarization_change, mean_opinion, cluster_separation, cross_cutting_exposure, num_polarizers, num_depolarizers, net_polarization_intensity, round}`

### §8.3 Action Schema

```json
{"action_type": "polarize|neutral|depolarize", "intensity": [0,1], "agent_role": str, "agent_id": str, "opinion": [-1,1]}
```

### §8.4 Round Granularity

Environment broadcast -> agents perceive/decide/act -> environment aggregates -> next round. Single-phase.

## §9 Parameter Seeds

| Parameter | Belongs to | Default | Empirical range | Source |
|-----------|-----------|---------|-----------------|--------|
| initial_polarization | environment | 0.15 | [0.05, 0.30] | simulation-bases.md §6 |
| polarization_impact | environment | 0.12 | [0.05, 0.20] | simulation-bases.md §6 |
| centripetal_force | environment | 0.01 | [0.005, 0.05] | simulation-bases.md §6 |
| noise_std | environment | 0.02 | [0.01, 0.05] | simulation-bases.md §3 |
| polarization_equilibrium | environment | 0.3 | [0.2, 0.5] | simulation-bases.md §3 |
| in_group_weight | ideologue | 0.6 | [0.4, 0.8] | simulation-bases.md §4.1 |
| spread_eagerness | ideologue | 0.9 | [0.6, 1.0] | simulation-bases.md §4.1 |
| conformity | conformist | 0.7 | [0.5, 0.9] | simulation-bases.md §4.2 |
| critical_eagerness | critical-thinker | 0.7 | [0.4, 0.9] | simulation-bases.md §4.3 |
| bridge_strength | bridge-builder | 0.8 | [0.5, 1.0] | simulation-bases.md §4.4 |
| engagement_probability | passive-follower | 0.3 | [0.1, 0.5] | simulation-bases.md §4.5 |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Notes |
|---------|--------|-------|
| Rule | Yes | Deterministic formula-driven baseline |
| LLM | Yes | Persona-only LLM reasoning |
| RuleLLM | Yes | Explicit formulas embedded in LLM prompts |
| Rag | Yes | Retrieved social-science context augments LLM |

### §10.2 Pass / Fail Criteria

1. Polarization remains bounded in [0, 1] for all 200 rounds.
2. Peak polarization exceeds initial_polarization (amplification > 1.0) in at least one variant.
3. All agent opinions remain in [-1, 1].
4. Every API action has action_type in {polarize, neutral, depolarize} with intensity in [0, 1].
5. Rule 5-round smoke completes without uncaught exceptions.
