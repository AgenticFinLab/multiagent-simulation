# EchoChamber Rule Variant — explain.md

## §1 Overview

The Rule variant implements EchoChamber with deterministic mathematical formulas grounded in Sunstein (2001) echo chamber theory. Each agent type applies a fixed formula derived from its theoretical archetype — Ideologues amplify in-group consensus, Conformists adopt prevailing opinion, CriticalThinkers depolarize based on evidence, BridgeBuilders center toward neutral. This provides the mechanically exact baseline for polarization dynamics.

| Aspect             | Detail                                                                                                                                                                           |
|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Variant            | Rule                                                                                                                                                                             |
| Simulation         | EchoChamber                                                                                                                                                                      |
| Decision Mechanism | Threshold formulas on `polarization`, `mean_opinion`, `cluster_separation`                                                                                                       |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                                                                                                                                  |
| Market Broadcast   | `polarization`, `prev_polarization`, `mean_opinion`, `cluster_separation`, `cross_cutting_exposure`, `num_polarizers`, `num_depolarizers`, `net_polarization_intensity`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 Ideologue (simulation-bases.md §4.1)

| Theory Component                        | Implementation                                                                         |
|-----------------------------------------|----------------------------------------------------------------------------------------|
| In-group amplification (Sunstein, 2001) | `opinion_update = in_group_weight * (mean_opinion * extremity_boost − my_opinion)`     |
| Out-group rejection                     | `opinion_update = out_group_discount * (mean_opinion − my_opinion)` when opposite sign |
| Polarizing action when opinion strong   | `if                                                                                    |

### §2.2 Conformist (simulation-bases.md §4.2)

| Theory Component                        | Implementation                                                          |
|-----------------------------------------|-------------------------------------------------------------------------|
| Social conformity (Asch, 1951)          | `opinion_update = conformity * (local_group_mean − my_opinion)`         |
| Local group determination               | Adjusts `local_group_mean` based on sign alignment with current opinion |
| Polarize when opinion exceeds threshold | `if                                                                     |

### §2.3 CriticalThinker (simulation-bases.md §4.3)

| Theory Component                                | Implementation                                                                  |
|-------------------------------------------------|---------------------------------------------------------------------------------|
| Evidence-driven opinion update (Isenberg, 1986) | `evidence_signal = −my_opinion * evidence_sensitivity * polarization`           |
| Slow opinion movement                           | `opinion_update = critical_weight * (evidence_signal − my_opinion * 0.1) * 0.3` |
| Depolarize when polarization high               | `if polarization > 0.3: action = "depolarize"; intensity =                      |

### §2.4 BridgeBuilder (simulation-bases.md §4.4)

| Theory Component                                  | Implementation                                                                  |
|---------------------------------------------------|---------------------------------------------------------------------------------|
| Centering force (Sunstein deliberative democracy) | `opinion_update = bridge_weight * (0.0 − my_opinion) * centering_tendency`      |
| Depolarize proportional to cluster separation     | `if cluster_separation > 0.5: intensity = bridge_strength * cluster_separation` |

### §2.5 PassiveFollower (simulation-bases.md §4.5)

| Theory Component                                     | Implementation                                             |
|------------------------------------------------------|------------------------------------------------------------|
| Mass communication drift (Lazarsfeld & Merton, 1954) | `drift = drift_rate * (mean_opinion − my_opinion)`         |
| Random engagement                                    | `if random() < engagement_probability: act; else: neutral` |

## §3 Market Mechanism

```
P(t+1) = P(t) + alpha * NetPolarization(t) + beta * CentripetalForce(t) + epsilon(t)
alpha = polarization_impact (e.g., 0.05)
beta = centripetal_force (e.g., 0.02), target center = 0.3
NetPolarization = Σ polarize_intensity − Σ depolarize_intensity
```

OpinionEnvironment broadcasts `env_data` dict to all agents every round. Agents read `polarization`, `mean_opinion`, `cluster_separation` to compute their opinion updates.

## §4 Variant Architecture

| Component     | Detail                                                                           |
|---------------|----------------------------------------------------------------------------------|
| Base class    | `BaseSocialAgent(GeneralPlayer)`                                                 |
| Inference     | None (deterministic formulas)                                                    |
| Context       | `env_data` from OpinionEnvironment broadcast                                     |
| Output format | `{action_type, intensity, agent_role, agent_id, opinion}` in `outbound_messages` |
| Retry logic   | N/A — deterministic                                                              |

## §5 Config Reference

Config file: `configs/EchoChamber/Rule/simulation.yml`

Key extras per agent:
- `OpinionEnvironment`: `initial_polarization`, `polarization_impact`, `centripetal_force`, `noise_std`, `record_path`, `custom_state_hot_limit`
- `Ideologue`: `initial_opinion`, `in_group_weight`, `extremity_boost`, `out_group_discount`, `spread_eagerness`
- `Conformist`: `initial_opinion`, `conformity`, `conformity_eagerness`, `group_proximity_threshold`
- `CriticalThinker`: `initial_opinion`, `critical_weight`, `critical_eagerness`, `evidence_sensitivity`
- `BridgeBuilder`: `initial_opinion`, `bridge_weight`, `bridge_strength`, `centering_tendency`
- `PassiveFollower`: `initial_opinion`, `engagement_probability`, `drift_rate`, `alignment_strength`

## §6 Running Instructions

```bash
python examples/EchoChamber/Rule/run_echo_chamber.py -c configs/EchoChamber/Rule/simulation.yml
```

## §7 Output Artifacts

- `{record_path}/{identity}/polarization/` — HistoryBuffer: polarization per round
- `{record_path}/{identity}/mean_opinion/` — HistoryBuffer: mean opinion per round
- `{record_path}/{identity}/cluster_separation/` — HistoryBuffer: cluster separation per round
- `{record_path}/{identity}/polarize_count/` — HistoryBuffer: polarizer count per round
- `{record_path}/{identity}/depolarize_count/` — HistoryBuffer: depolarizer count per round
- `{record_path}/{agent_identity}/opinion/` — per-agent opinion history

## §8 Known Limitations

- Deterministic formulas do not capture individual heterogeneity within agent types
- `out_group_discount` is a fixed scalar — real ideological resistance is more complex
- Passive followers have no memory of past rounds — drift is purely memoryless
- Noise term in polarization dynamics can occasionally reverse strong polarization trends

## §9 References

See `simulation-bases.md §4` for agent parameter sources and theoretical derivations.
See `analysis-bases.md §2` for metric definitions and Python function signatures.
