# Non-financial social information participants

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Non-financial social information participants |
| Merged profiles | 11 |
| Scenarios | EchoChamber, RumorSpread |
| Observed names | Bridge Builder, Conformist, Critical Thinker, Distorting Relayer, Fact Checker, Gullible Spreader, Ideologue, Passive Bystander, Passive Follower, Skeptical Evaluator, Uninformed Bystander |

## Consolidated Definition and Goals

- **EchoChamber / Bridge Builder**: **Summary**: Cross-group engager that reduces separation between opinion clusters. **Theoretical and Empirical Basis**: Cross-cutting exposure and deliberative democracy. **Design Purpose**: Counteract silo formation and provide strong depolarizing pressure when clusters are far apart. **Behavioral Framework**: Pulls its own opinion toward zero and emits depolarizing actions when cluster separation is elevated. **Decision Process**: Update opinion by `bridge_weight * (0 - my_opinion) * centering_tendency`; if `cluster_separation > 0.5`, emit `depolarize` with intensity `bridge_strength * min(cluster_separation, 1.0)`, with a weaker rule for separation above `0.2`. **Worked Numerical Example**: Cluster separation `0.8` and bridge strength `0.8` produce a depolarizing intensity of `0.64`. **Academic References**: Filter-bubble, deliberative-democracy, and cross-cutting exposure literature.
- **EchoChamber / Conformist**: **Summary**: Group-oriented follower that adopts perceived local opinion. **Theoretical and Empirical Basis**: Conformity, social proof, and informational cascades. **Design Purpose**: Reinforce group tendencies without independent conviction. **Behavioral Framework**: Moves toward a local group mean derived from the population mean and the sign of current opinion. **Decision Process**: Update opinion using `conformity * (local_group_mean - my_opinion)`. If `abs(my_opinion) > group_proximity_threshold`, emit `polarize` with intensity `abs(my_opinion) * conformity_eagerness`. **Worked Numerical Example**: Opinion `0.2`, local mean `0.6`, and conformity `0.7` move opinion by `0.28` toward the group. **Academic References**: Conformity experiments and social-proof models.
- **EchoChamber / Critical Thinker**: **Summary**: Evidence-oriented agent that resists group pressure. **Theoretical and Empirical Basis**: Persuasive-arguments theory and independent evidence evaluation. **Design Purpose**: Provide stabilizing pressure when polarization becomes high. **Behavioral Framework**: Treats high polarization as evidence that views should move toward the center. **Decision Process**: Compute `evidence_signal = -my_opinion * evidence_sensitivity * polarization`, update slowly using `critical_weight`, and emit `depolarize` when `polarization > 0.3`. **Worked Numerical Example**: Opinion `0.6`, polarization `0.7`, and evidence_sensitivity `0.6` create a negative signal that pulls the agent toward the center. **Academic References**: Group-polarization and persuasive-arguments research.
- **EchoChamber / Ideologue**: **Summary**: Strong opinion holder that amplifies in-group consensus. **Theoretical and Empirical Basis**: Echo-chamber and group-polarization theory. **Design Purpose**: Drive polarization when the environment leans toward the agent's side. **Behavioral Framework**: Treats same-sign mean opinion as validation and opposing mean opinion as discounted out-group information. **Decision Process**: If `my_opinion * mean_opinion > 0`, update toward `mean_opinion * extremity_boost` using `in_group_weight`; otherwise discount the opposing signal using `out_group_discount`. If `abs(my_opinion) > 0.3`, emit `polarize` with intensity `abs(my_opinion) * spread_eagerness`. **Worked Numerical Example**: Opinion `0.5` and mean `0.4` produce in-group validation and a polarizing action around `0.5 * 0.9 = 0.45`. **Academic References**: Echo chambers, enclave deliberation, and group polarization literature.
- **EchoChamber / Passive Bystander**: LLM-driven passive bystander -- low engagement, occasional group alignment, background mass. Theory: simulation-bases.md Section 4.5.
- **EchoChamber / Passive Follower**: **Summary**: Low-engagement participant that occasionally aligns with the population. **Theoretical and Empirical Basis**: Mass communication and passive audience models. **Design Purpose**: Provide background population inertia and stochastic engagement. **Behavioral Framework**: Drifts toward mean opinion and usually stays neutral. **Decision Process**: Move by `drift_rate * (mean_opinion - my_opinion)`. With probability `engagement_probability`, emit weak neutral or polarizing behavior depending on opinion strength; otherwise emit `neutral`. **Worked Numerical Example**: Opinion `0.1`, mean `0.4`, and drift rate `0.1` move opinion by `0.03`. **Academic References**: Mass communication and low-engagement audience literature.
- **RumorSpread / Distorting Relayer**: **Summary**: Moderate believer that reshapes information while transmitting it. **Theoretical and Empirical Foundation**: Leveling, sharpening, and assimilation in serial transmission. **Design Purpose and Activation Scenarios**: Raises both belief and distortion when the claim is already moderately believed. **Behavioral Framework**: Applies `sharpening_factor * distortion`, then leveling toward rounded belief; emits `spread` when `my_belief > 0.25`. **Decision Process Walkthrough**: Compute sharpening bias, update belief using `credulity`, apply leveling, then relay with `my_belief * relay_eagerness`. **Worked Numerical Example**: Belief `0.40` and relay eagerness `0.70` produce base intensity `0.28`. **Academic References**: Allport and Postman (1947); Bartlett-style serial reproduction literature.
- **RumorSpread / Fact Checker**: **Summary**: Professional verifier that actively debunks false or distorted claims. **Theoretical and Empirical Foundation**: Active rumor denial and misinformation correction research. **Design Purpose and Activation Scenarios**: Corrects when public belief is large enough to matter, with stronger action when distortion makes errors easier to identify. **Behavioral Framework**: Belief moves strongly toward truth; correction intensity equals `fact_check_strength * (1 - my_belief) * (1 + distortion_sensitivity * distortion) * credibility_discount`. **Decision Process Walkthrough**: If environment belief exceeds `0.3`, compute discounted correction; otherwise ignore. **Worked Numerical Example**: Strength `0.8`, belief `0.1`, distortion `0.5`, sensitivity `0.5`, and discount `0.6` yield `0.54`. **Academic References**: DiFonzo and Bordia (2007); Lewandowsky et al. (2012).
- **RumorSpread / Gullible Spreader**: **Summary**: Highly credulous transmitter that amplifies unverified claims. **Theoretical and Empirical Foundation**: Rumor transmission under ambiguity; Allport and Postman (1947), Vosoughi et al. (2018). **Design Purpose and Activation Scenarios**: Activates when personal belief exceeds a low threshold and creates primary positive feedback. **Behavioral Framework**: Information set is environment belief and distortion. Personal belief moves toward public belief by `credulity`; spread intensity is `my_belief * spread_eagerness * (1 + distortion_amplification * distortion)`. **Decision Process Walkthrough**: Update belief, test `my_belief > 0.2`, then emit `spread` with bounded intensity or `ignore`. **Worked Numerical Example**: With belief `0.50`, eagerness `0.90`, distortion `0.20`, and amplification `0.30`, intensity is `0.50 * 0.90 * 1.06 = 0.477`. **Academic References**: Allport and Postman (1947); Vosoughi et al. (2018).
- **RumorSpread / Skeptical Evaluator**: **Summary**: Evidence-oriented participant that resists social proof. **Theoretical and Empirical Foundation**: Correction and skepticism literature; Lewandowsky et al. (2012), Ecker et al. (2022). **Design Purpose and Activation Scenarios**: Provides stabilizing pressure when personal belief remains below the correction threshold. **Behavioral Framework**: Combines a truth pull with weak social pull: `skepticism * (truth_value - my_belief) + (1 - skepticism) * 0.1 * (env_belief - my_belief)`. **Decision Process Walkthrough**: Update belief toward truth; if below `belief_threshold`, emit `correct` with `(1 - my_belief) * correction_eagerness`. **Worked Numerical Example**: Belief `0.20` and correction eagerness `0.60` produce correction intensity `0.48`. **Academic References**: Lewandowsky et al. (2012); Ecker et al. (2022).
- **RumorSpread / Uninformed Bystander**: **Summary**: Low-engagement participant that adds background participation and noise. **Theoretical and Empirical Foundation**: Passive audience and minimal engagement models. **Design Purpose and Activation Scenarios**: Adds stochastic weak transmission without systematic correction. **Behavioral Framework**: Personal belief drifts weakly toward public belief. With `engagement_probability`, the agent may spread with probability `spread_probability`; otherwise it ignores. **Decision Process Walkthrough**: Update belief by `0.1 * (env_belief - my_belief)`, sample engagement, then emit weak `spread` or `ignore`. **Worked Numerical Example**: Belief `0.25`, random spread multiplier `0.30`, and engagement produce intensity `0.075`. **Academic References**: Shibutani (1966); social-media participation studies.

## Consolidated Financial Theory

- Theory: simulation-bases.md Section 4.4 -- BridgeBuilder
- Theoretical basis: Sunstein (2001) deliberative democracy; Pariser (2011) serendipity
- LLM-driven bridge builder -- engages across groups, depolarizes by finding common ground. Theory: simulation-bases.md Section 4.4.
- RuleLLM bridge builder -- centering formula + LLM cross-group engagement reasoning. Theory: simulation-bases.md Section 4.4.
- RAG-augmented bridge builder -- cross-group engagement with deliberative democracy literature. Theory: simulation-bases.md Section 4.4.
- Theory: simulation-bases.md Section 4.2 -- Conformist
- Theoretical basis: Asch (1951) conformity; Sunstein (2001) group polarization;
- LLM-driven conformist -- adopts prevailing group opinion, reinforcing homophily. Theory: simulation-bases.md Section 4.2.
- RuleLLM conformist -- Asch conformity formula + LLM group alignment reasoning. Theory: simulation-bases.md Section 4.2.
- RAG-augmented conformist -- group alignment with social conformity literature. Theory: simulation-bases.md Section 4.2.
- Theory: simulation-bases.md Section 4.3 -- CriticalThinker
- Theoretical basis: Isenberg (1986) persuasive arguments vs social comparison;
- LLM-driven critical thinker -- evaluates evidence independently, resists social proof. Theory: simulation-bases.md Section 4.3.
- RuleLLM critical thinker -- Isenberg depolarization formula + LLM evidence evaluation. Theory: simulation-bases.md Section 4.3.
- RAG-augmented critical thinker -- evidence evaluation with persuasive-arguments literature. Theory: simulation-bases.md Section 4.3.
- Theory: simulation-bases.md Section 4.1 -- Ideologue
- Theoretical basis: Sunstein (2001) echo chamber amplification; group polarization
- LLM-driven ideologue -- amplifies in-group consensus, rejects out-group information. Theory: simulation-bases.md Section 4.1.
- RuleLLM ideologue -- in-group amplification formula + LLM reasoning on echo chamber dynamics. Theory: simulation-bases.md Section 4.1.
- RAG-augmented ideologue -- in-group amplification with literature context. Theory: simulation-bases.md Section 4.1.
- LLM-driven passive bystander -- low engagement, occasional group alignment, background mass. Theory: simulation-bases.md Section 4.5.
- Theory: simulation-bases.md Section 4.5 -- PassiveFollower
- Theoretical basis: Lazarsfeld & Merton (1954) mass communication; passive followers
- RuleLLM passive follower -- Lazarsfeld drift formula + LLM low-engagement reasoning. Theory: simulation-bases.md Section 4.5.
- RAG-augmented passive follower -- low-engagement drift with mass communication literature. Theory: simulation-bases.md Section 4.5.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| EchoChamber | Bridge Builder | [EchoChamber__BridgeBuilder.md](../EchoChamber__BridgeBuilder.md) |
| EchoChamber | Conformist | [EchoChamber__Conformist.md](../EchoChamber__Conformist.md) |
| EchoChamber | Critical Thinker | [EchoChamber__CriticalThinker.md](../EchoChamber__CriticalThinker.md) |
| EchoChamber | Ideologue | [EchoChamber__Ideologue.md](../EchoChamber__Ideologue.md) |
| EchoChamber | Passive Bystander | [EchoChamber__PassiveBystander.md](../EchoChamber__PassiveBystander.md) |
| EchoChamber | Passive Follower | [EchoChamber__PassiveFollower.md](../EchoChamber__PassiveFollower.md) |
| RumorSpread | Distorting Relayer | [RumorSpread__DistortingRelayer.md](../RumorSpread__DistortingRelayer.md) |
| RumorSpread | Fact Checker | [RumorSpread__FactChecker.md](../RumorSpread__FactChecker.md) |
| RumorSpread | Gullible Spreader | [RumorSpread__GullibleSpreader.md](../RumorSpread__GullibleSpreader.md) |
| RumorSpread | Skeptical Evaluator | [RumorSpread__SkepticalEvaluator.md](../RumorSpread__SkepticalEvaluator.md) |
| RumorSpread | Uninformed Bystander | [RumorSpread__UninformedBystander.md](../RumorSpread__UninformedBystander.md) |

