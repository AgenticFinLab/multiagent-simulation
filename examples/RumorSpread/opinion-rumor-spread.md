# RumorSpread — Scenario Target

## §1 Meta

| Field       | Content                                                                                                              |
|-------------|----------------------------------------------------------------------------------------------------------------------|
| Name        | RumorSpread                                                                                                          |
| Domain      | opinion                                                                                                              |
| Phenomenon  | Unverified information propagates through gullible and distorting relayers faster than fact-checkers can correct it. |
| Pipeline    | masim/skills/polish-simulation-pipeline.md                                                                           |
| Target Spec | masim/skills/define-simulation-scenario-skill.md (v1.2)                                                              |

## §2 Phenomenon Statement

### §2.1 Trigger
A piece of unverified or ambiguous information enters a social network through an initial spreader. The information carries some emotional charge — urgency, danger, or opportunity — which motivates the first recipients to pass it on. The initial spreader's message may be incomplete, vague, or slanted in a way that invites interpretation by subsequent receivers.

### §2.2 Mechanism
Rumor propagation follows a transmission-distortion-amplification loop. Gullible spreaders accept and relay unverified claims without scrutiny. Distorting relayer agents modify the message during retransmission — sharpening emotionally salient details, levelling out qualifying context, and assimilating the content toward pre-existing beliefs. Skeptical evaluators and fact-checkers interrogate the claim and slow propagation, but their reach is limited by lower sharing frequency. Uninformed bystanders neither spread nor counter the rumor, serving as a passive audience. The net effect is that false or distorted information can spread faster and farther than corrected information, consistent with the empirical finding that false news diffuses more broadly than true news on social media.

### §2.3 Participants
Five participant classes operate: gullible accept-and-relay spreaders, distorting message-modifying relayers, skeptical evidence-demanding evaluators, investigative fact-checkers, and uninformed passive bystanders. Gullible spreaders and distorting relayers drive the propagation cascade. Skeptical evaluators and fact-checkers provide corrective braking. Bystanders receive but do not retransmit, serving as the silent audience.

### §2.4 Resolution
The rumor cascade decays when skeptical and fact-checking corrections reach enough network participants to reduce the effective reproduction rate below one, or when the information has saturated the reachable audience and novelty fades. Distortion may accumulate to the point where the message becomes implausible to even gullible receivers. The cascade ends when new transmissions fall below the skeptical-correction rate.

## §3 Research Goals

1. **Cascade reach.** Can the simulation generate rumor reach that exceeds fact-check reach, consistent with Vosoughi et al. (2018) evidence that false news spreads farther than true news?
2. **Distortion accumulation.** Does the message content show measurable distortion (leveling, sharpening, assimilation) as it passes through multiple distorting relayers?
3. **Skeptical braking.** Does the presence of skeptical evaluators and fact-checkers measurably reduce cascade size and duration?
4. **Ablation.** If the distorting relayer is removed, does message fidelity improve and cascade size fall relative to the full model?
5. **Parameter sweep and variant comparison.** How do the gullibility threshold and distortion strength parameters change cascade dynamics, and how do LLM-driven agents differ from the Rule baseline in rumor-acceptance reasoning?

## §4 Theoretical Anchors

### §4.1 Psychology of Rumor — Leveling, Sharpening, and Assimilation

| Field                     | Content                                                                                                                                                                             |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Allport, G. W., & Postman, L. (1947). *The Psychology of Rumor*. Henry Holt and Company. (Book; stable URL via APA PsycNET: https://psycnet.apa.org/record/1947-01538-000)          |
| Key mechanism (≤30 words) | As information passes serially through a chain, it is levelled (details dropped), sharpened (salient elements emphasised), and assimilated (distorted toward pre-existing schemas). |
| Key equation              | message_fidelity(t) = message_fidelity(0) * (1 - distortion_rate)^(n_relayers); distortion_rate = f(emotional_salience, schema_congruence).                                         |
| Motivates agent           | distorting-relayer (§7)                                                                                                                                                             |
| Parameter implication     | distortion_rate range 0.05 to 0.30 per transmission, default 0.15; sharpening_bias range 0.10 to 0.40, default 0.25.                                                                |

### §4.2 False News Spreads Faster and Deeper than Truth

| Field                     | Content                                                                                                                                                      |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Vosoughi, S., Roy, D., & Aral, S. (2018). The spread of true and false news online. *Science*, 359(6380), 1146-1151. https://doi.org/10.1126/science.aap9559 |
| Key mechanism (≤30 words) | False news diffuses significantly farther, faster, deeper, and more broadly than true news on social media, driven by novelty and emotional arousal.         |
| Key equation              | Cascade size follows R0-like reproduction number; false-news R0 empirically higher (cascade depth ~1.5x, breadth ~1.3x) than true-news R0.                   |
| Motivates agent           | gullible-spreader (§7)                                                                                                                                       |
| Parameter implication     | gullibility_threshold range 0.10 to 0.50, default 0.30; share_probability range 0.20 to 0.80, default 0.50.                                                  |

### §4.3 Misinformation Correction and the Continued-Influence Effect

| Field                     | Content                                                                                                                                                                                                                                                                     |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Lewandowsky, S., Ecker, U. K. H., Seifert, C. M., Schwarz, N., & Cook, J. (2012). Misinformation and its correction: Continued influence and successful debiasing. *Psychological Science in the Public Interest*, 13(3), 106-131. https://doi.org/10.1177/1529100612451018 |
| Key mechanism (≤30 words) | Corrections reduce but rarely eliminate misinformation's influence; the continued-influence effect means retracted claims still affect reasoning after explicit correction.                                                                                                 |
| Key equation              | Correction reach = fact_checker_broadcast_rate * audience_size; effective correction reduces but does not zero out prior rumor exposure effect.                                                                                                                             |
| Motivates agent           | skeptical-evaluator (§7), fact-checker (§7)                                                                                                                                                                                                                                 |
| Parameter implication     | correction_decay_factor range 0.50 to 0.90, default 0.70 (fraction of prior exposure that persists after correction).                                                                                                                                                       |

## §5 Stylized Facts

| #  | Fact (one sentence)                                                                | Quantitative range                                     | Citation                                                            | Acceptance metric                                                 |
|----|------------------------------------------------------------------------------------|--------------------------------------------------------|---------------------------------------------------------------------|-------------------------------------------------------------------|
| F1 | Rumor cascade reaches more agents than fact-check cascade.                         | rumor_reach / factcheck_reach > 1.2                    | Vosoughi et al. (2018), https://doi.org/10.1126/science.aap9559     | `analysis.py: _rumor_vs_factcheck_reach_ratio()` > 1.2            |
| F2 | Message fidelity declines as the number of relayer hops increases.                 | fidelity(N) < fidelity(0); monotonic decrease          | Allport & Postman (1947)                                            | `analysis.py: _message_fidelity_decay()` monotonic negative slope |
| F3 | Cascade duration is shorter when skeptical and fact-checking agents are present.   | duration_full < duration_without_skeptics              | Lewandowsky et al. (2012), https://doi.org/10.1177/1529100612451018 | `analysis.py: _skeptical_braking_effect()` > 0                    |
| F4 | Distorting-relayer messages carry higher emotional salience than source messages.  | emotional_salience_relayed > emotional_salience_source | Allport & Postman (1947)                                            | `analysis.py: _distortion_salience_increase()` > 0                |
| F5 | Gullible-spreader share probability exceeds skeptical-evaluator share probability. | p_share_gullible > p_share_skeptical                   | Vosoughi et al. (2018), https://doi.org/10.1126/science.aap9559     | `analysis.py: _gullible_vs_skeptical_share_ratio()` > 1.0         |

## §6 Historical / Empirical Anchors

### §6.1 Vosoughi-Roy-Aral Twitter Rumor Study (2006-2017)

| Field             | Content                                                                                                                                                                                                                                                                                                                                                                               |
|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Vosoughi, Roy, and Aral Twitter rumor-cascade study, 2006-2017.                                                                                                                                                                                                                                                                                                                       |
| Trigger           | Analysis of approximately 126,000 rumor cascades tweeted by roughly 3 million accounts, classified as true or false by six independent fact-checking organisations.                                                                                                                                                                                                                   |
| Quantitative arc  | Falsehood reached 1,500 people roughly six times faster than truth; false political news was the most viral category. False cascades were deeper (longer retweet chains) and broader (more unique users per cascade) than true cascades.                                                                                                                                              |
| Agent mapping     | `gullible-spreader` maps to users who retweeted false claims without verification; `distorting-relayer` maps to users who modified claims during sharing; `skeptical-evaluator` maps to users who questioned or fact-checked claims; `fact-checker` maps to professional and volunteer fact-checking organisations; `uninformed-bystander` maps to passive readers who did not share. |
| Primary source(s) | Vosoughi, Roy & Aral (2018), https://doi.org/10.1126/science.aap9559                                                                                                                                                                                                                                                                                                                  |

### §6.2 COVID-19 Misinformation Wave (2020)

| Field             | Content                                                                                                                                                                                                                                                                                                                |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | COVID-19 misinformation and infodemic, early 2020.                                                                                                                                                                                                                                                                     |
| Trigger           | Widespread uncertainty about a novel pathogen created fertile ground for unverified claims about treatments, origins, and public-health measures.                                                                                                                                                                      |
| Quantitative arc  | WHO declared an infodemic alongside the pandemic. Misinformation about fake cures and conspiracy theories spread widely on social platforms, with some false claims reaching millions before debunking. Fact-checking organisations saw unprecedented volume, but corrections consistently lagged behind rumor spread. |
| Agent mapping     | `gullible-spreader` maps to users sharing unverified treatment claims; `distorting-relayer` maps to those who exaggerated or modified health advice; `skeptical-evaluator` maps to public-health communicators; `fact-checker` maps to WHO and CDC communication teams.                                                |
| Primary source(s) | WHO (2020), Infodemic management; Lewandowsky et al. (2012), https://doi.org/10.1177/1529100612451018; Ecker et al. (2022), https://doi.org/10.1038/s44159-021-00006-y                                                                                                                                                 |

## §7 Agent Roster

| Agent name (kebab)   | Real-world counterpart                                                | Theory family (§4 anchor)                    | Domain role       | Primary signals                     | Intent line                                                                                                                       | Expected pool match |
|----------------------|-----------------------------------------------------------------------|----------------------------------------------|-------------------|-------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|---------------------|
| gullible-spreader    | social media user who shares without verification                     | False News Diffusion (§4.2)                  | Destabilising     | message_content, neighbour_shares   | "Exists to accept and relay unverified claims without scrutiny when emotional charge exceeds a threshold."                        | (none — likely new) |
| distorting-relayer   | social media user who modifies and embellishes during sharing         | Rumor Psychology (§4.1)                      | Destabilising     | message_content, emotional_salience | "Exists to modify information during retransmission through levelling, sharpening, and assimilation toward pre-existing beliefs." | (none — likely new) |
| skeptical-evaluator  | critical-thinking social media user or community fact-checker         | Misinformation Correction (§4.3)             | Stabilising       | message_content, evidence_quality   | "Exists to interrogate claims by demanding evidence, reducing propagation by sharing less often and with caveats."                | (none — likely new) |
| fact-checker         | professional fact-checking organisation or institutional communicator | Misinformation Correction (§4.3)             | Stabilising       | message_content, correction_reach   | "Exists to broadcast verified corrections that partially counteract prior rumor exposure through authoritative debunking."        | (none — likely new) |
| uninformed-bystander | passive social media reader who does not share                        | (passive audience — no active theory anchor) | Context-dependent | message_content                     | "Exists to receive information without retransmitting it, representing the silent majority audience."                             | (none — likely new) |

Diversity notes: two destabilising (gullible-spreader, distorting-relayer), two stabilising (skeptical-evaluator, fact-checker), and one context-dependent passive audience member (uninformed-bystander). Theory families span serial-transmission distortion, false-news diffusion, and misinformation correction. The `opinion` domain AGENT_POOL directory does not yet exist; all agents are tagged as likely new pending pool creation. An §A Domain Palette Appendix for the opinion domain should be produced during Step 2.

## §8 Environment Specification

### §8.1 Social Graph

Static small-world network with N agents, where each agent is connected to a subset of peers (average degree ~4-8). Information propagates along edges in both directions. Network topology is fixed for a given run. Degree distribution approximates a social-media follower graph with a small number of high-degree hubs and many low-degree leaf nodes. Source: Watts & Strogatz (1998) small-world model.

### §8.2 Communication Protocol

Synchronous round-based communication. In each round, every agent observes the messages shared by its network neighbours in the previous round. Agents decide whether to share (retransmit) each observed message, possibly with modification, based on their decision rules. Messages contain content (the claim or information payload), source attribution, and an emotional-salience tag. Agents may share at most one message per round. Source: Vosoughi et al. (2018) cascade model.

### §8.3 Information Sources

A single exogenous rumor is injected into the network at round 1 through a randomly selected initial spreader. No further exogenous information arrives during the run. The rumor content is a short textual claim with an initial emotional-salience score. Fact-checking corrections are endogenous — produced by skeptical evaluators and fact-checkers — rather than externally injected.

### §8.4 Round Granularity

Each round approximates one social-media sharing cycle — roughly one hour of online activity, or enough time for a user to see a post and decide whether to share it. A 200-round run covers initial injection, cascade growth, peak virality, and eventual decay or saturation phases.

## §9 Parameter Seeds

| Parameter                     | Symbol     | Belongs to (agent / environment) | Empirical range               | Candidate default | Source citation                                                     |
|-------------------------------|------------|----------------------------------|-------------------------------|-------------------|---------------------------------------------------------------------|
| population size               | N          | environment (§8.1)               | normalised simulation scale   | 20 agents         | Source: normalization                                               |
| average network degree        | d_avg      | environment (§8.1)               | 3 to 10                       | 5                 | Watts & Strogatz (1998)                                             |
| gullibility threshold         | theta_gull | gullible-spreader (§7)           | 0.10 to 0.50                  | 0.30              | Vosoughi et al. (2018), https://doi.org/10.1126/science.aap9559     |
| share probability (gullible)  | p_share_g  | gullible-spreader (§7)           | 0.20 to 0.80                  | 0.50              | Vosoughi et al. (2018), https://doi.org/10.1126/science.aap9559     |
| distortion rate               | r_dist     | distorting-relayer (§7)          | 0.05 to 0.30 per transmission | 0.15              | Allport & Postman (1947)                                            |
| sharpening bias               | b_sharp    | distorting-relayer (§7)          | 0.10 to 0.40                  | 0.25              | Allport & Postman (1947)                                            |
| skepticism threshold          | theta_skep | skeptical-evaluator (§7)         | 0.40 to 0.80                  | 0.60              | Lewandowsky et al. (2012), https://doi.org/10.1177/1529100612451018 |
| share probability (skeptical) | p_share_s  | skeptical-evaluator (§7)         | 0.05 to 0.30                  | 0.15              | Lewandowsky et al. (2012), https://doi.org/10.1177/1529100612451018 |
| correction broadcast rate     | r_corr     | fact-checker (§7)                | 0.10 to 0.50 per round        | 0.25              | Lewandowsky et al. (2012), https://doi.org/10.1177/1529100612451018 |
| correction decay factor       | d_corr     | fact-checker (§7)                | 0.50 to 0.90                  | 0.70              | Lewandowsky et al. (2012), https://doi.org/10.1177/1529100612451018 |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale                                                                                                                                      |
|---------|--------|------------------------------------------------------------------------------------------------------------------------------------------------|
| Rule    | Yes    | Deterministic baseline for cascade reach, message-fidelity decay, and skeptical-braking effect.                                                |
| LLM     | Yes    | Tests whether persona-driven rumor-acceptance reasoning amplifies or moderates cascade dynamics relative to Rule baseline.                     |
| RuleLLM | Yes    | Tests whether explicit rumor-propagation rules inside LLM reasoning preserve distortion structure while allowing judgmental sharing decisions. |
| Rag     | Yes    | Tests whether retrieved misinformation-literature context changes sharing propensity, skepticism, or correction effectiveness.                 |

### §10.2 Pass / Fail Criteria

| Criterion                                                                                                                                   | Status when satisfied |
|---------------------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| Deterministic variant initializes agents, runs, writes records, and completes without uncaught exceptions.                                  | green                 |
| At least one rumor-propagation mechanism activates: cascade reach exceeding fact-check reach, message-fidelity decay, or skeptical braking. | green                 |
| Analysis loads records and computes core metrics from §5.                                                                                   | green                 |
| All four variants declared Yes in §10.1 build and produce required output artefacts.                                                        | green                 |
