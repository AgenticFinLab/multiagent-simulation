# Multiagent Simulation Scenario Catalog

> Comprehensive classification and inventory of ALL simulation scenarios across disciplines.
> Scope: Human group behavior phenomena suitable for LLM multi-agent simulation.
> Primary disciplines: Finance & Economics, Sociology, Political Economy.
> Secondary: Public Health, Organizational Behavior, Environmental Economics, Technology & Innovation.
> Purpose: organize thinking, aid recall, prevent omissions, guide future additions.

## Classification Framework

Scenarios are organized along two orthogonal axes:

- **Axis 1: Phenomenon Type** — What is being simulated?
- **Axis 2: Agent Driver** — How do agents make decisions? (Rule / LLM / RuleLLM / Rag)

---

## Axis 1: Phenomenon Classification

### A. Behavioral Biases (Cognitive Psychology)

Scenarios where systematic cognitive errors drive market outcomes.

| Scenario               | Bias                         | Key Theory                                  | Core Mechanism                                               | Status |
|------------------------|------------------------------|---------------------------------------------|--------------------------------------------------------------|--------|
| OverconfidenceBias     | Overconfidence               | Daniel et al. (1998), Odean (1998)          | Over-trading, underestimation of risk                        | DONE   |
| LossAversion           | Loss aversion                | Kahneman & Tversky (1979) - Prospect Theory | Disposition to hold losses, sell gains prematurely           | DONE   |
| HerdingInformation     | Informational herding        | Bikhchandani et al. (1992)                  | Ignoring private signals to follow crowd                     | DONE   |
| AnchoringEffect        | Anchoring                    | Tversky & Kahneman (1974)                   | Insufficient adjustment from initial reference               | DONE   |
| MentalAccounting       | Mental accounting            | Thaler (1985, 1999)                         | Segregating gains/losses into separate accounts              | DONE   |
| ConfirmationBias       | Confirmation bias            | Nickerson (1998), Lord et al. (1979)        | Seeking/weighting confirmatory evidence                      | DONE   |
| GamblerFallacy         | Gambler's fallacy            | Tversky & Kahneman (1971)                   | Misinterpreting independent events as dependent              | DONE   |
| AvailabilityBias       | Availability heuristic       | Tversky & Kahneman (1973)                   | Overweighting salient/recent information                     | DONE   |
| EndowmentEffect        | Endowment effect             | Kahneman et al. (1990), Thaler (1980)       | Overvaluing owned assets vs identical unowned ones           | DONE   |
| StatusQuoBias          | Status quo bias              | Samuelson & Zeckhauser (1988)               | Preference for current state, resistance to change           | DONE   |
| SunkCostFallacy        | Sunk cost fallacy            | Arkes & Blumer (1985)                       | Continuing investment based on past unrecoverable costs      | DONE   |
| RepresentativenessBias | Representativeness heuristic | Kahneman & Tversky (1972)                   | Judging probability by similarity to prototype               | DONE   |
| FramingEffect          | Framing effect               | Tversky & Kahneman (1981)                   | Decision changes based on presentation of equivalent options | DONE   |
| HindsightBias          | Hindsight bias               | Fischhoff (1975)                            | "I knew it all along" — overestimating predictability        | DONE   |

### B. Market Microstructure Effects

Scenarios where market structure and trading mechanics produce emergent phenomena.

| Scenario             | Effect                | Key Theory                                  | Core Mechanism                                          | Status |
|----------------------|-----------------------|---------------------------------------------|---------------------------------------------------------|--------|
| AssetBubble          | Price bubble          | Greater Fool Theory, Shiller (2000)         | Momentum + leverage drives prices far from fundamentals | DONE   |
| HerdEffect           | Herding               | Banerjee (1992), Scharfstein & Stein (1990) | Social proof and informational cascades                 | DONE   |
| DispositionEffect    | Disposition effect    | Shefrin & Statman (1985)                    | Sell winners too early, hold losers too long            | DONE   |
| MomentumEffect       | Momentum anomaly      | Jegadeesh & Titman (1993)                   | Past winners continue to outperform                     | DONE   |
| ReversalEffect       | Long-term reversal    | De Bondt & Thaler (1985)                    | Past losers outperform in long run                      | DONE   |
| ShortSqueeze         | Short squeeze         | Jones & Lamont (2002)                       | Forced covering amplifies price moves                   | DONE   |
| VolatilityClustering | Volatility clustering | Engle (1982) - ARCH, GARCH                  | Volatility begets volatility                            | DONE   |
| FlashCrash           | Flash crash           | Kirilenko et al. (2017)                     | HFT withdrawal + order book collapse                    | DONE   |
| MarketCrash          | Market crash          | Genotte & Leland (1990)                     | Portfolio insurance feedback loop                       | DONE   |
| LiquidityDryup       | Liquidity dry-up      | Brunnermeier & Pedersen (2009)              | Margin spiral + liquidity spiral                        | DONE   |
| EquityPremium        | Equity premium puzzle | Mehra & Prescott (1985)                     | High equity returns vs risk-free rate                   | DONE   |
| CarryTradeUnwind     | Carry trade unwind    | Brunnermeier et al. (2009)                  | Low-yield funding currency appreciation during risk-off | DONE   |
| CreditCycle          | Credit cycle          | Geanakoplos (2010) - Leverage cycles        | Leverage expands in booms, contracts in crises          | DONE   |
| CurrencyCrisis       | Currency crisis       | Obstfeld (1996) - Second-generation models  | Self-fulfilling speculative attacks                     | DONE   |

### C. Historical Market Events

Scenarios recreating specific real-world financial crises and events.

| Scenario             | Event                   | Year    | Key Theory                                           | Status |
|----------------------|-------------------------|---------|------------------------------------------------------|--------|
| BlackMonday1987      | October 19 crash        | 1987    | Brady Commission, Genotte & Leland (1990)            | DONE   |
| LTCMCollapse         | LTCM crisis             | 1998    | Shleifer & Vishny (1997) - Limits to arbitrage       | DONE   |
| DotComBubble         | Tech bubble burst       | 2000    | Shiller (2000) - Irrational exuberance               | DONE   |
| GFC2008              | Global Financial Crisis | 2008    | Brunnermeier (2009) - Liquidity spiral               | DONE   |
| FlashCrash2010       | May 6 Flash Crash       | 2010    | Kirilenko et al. (2017) - HFT dynamics               | DONE   |
| Volmageddon          | VIX ETN blow-up         | 2018    | Bergsma & Jiang (2022) - Vol product feedback        | DONE   |
| GameStopShortSqueeze | GME short squeeze       | 2021    | Jarrow & Li (2021) - Gamma squeeze                   | DONE   |
| ArchegosCollapse     | Archegos liquidation    | 2021    | Becketti (2021) - TRS leverage                       | DONE   |
| LUNACollapse         | Terra/LUNA crash        | 2022    | Klages-Mundt et al. (2020) - Algorithmic stablecoins | DONE   |
| SVBBankRun           | SVB deposit flight      | 2023    | Diamond & Dybvig (1983) - Bank runs                  | DONE   |
| EuropeanDebtCrisis   | Sovereign debt crisis   | 2010-12 | De Grauwe (2011) - Self-fulfilling sovereign default | DONE   |
| AsianFinancialCrisis | Asian currency crisis   | 1997    | Radelet & Sachs (1998) - Panic-based crisis          | DONE   |
| TulipMania           | Dutch tulip bubble      | 1637    | Garber (2000) - Bubble fundamentals                  | DONE   |
| SouthSeaBubble       | South Sea Company       | 1720    | Temin & Voth (2004) - Insider trading                | DONE   |
| SorosPound           | GBP ERM exit            | 1992    | Obstfeld (1996) - Speculative attacks                | DONE   |

---

## Coverage Matrix

### By Phenomenon Type

```
Behavioral Biases (14/14 DONE, 0 TODO, 0 FUTURE)
  DONE:     OverconfidenceBias, LossAversion, HerdingInformation, AnchoringEffect, MentalAccounting,
            ConfirmationBias, GamblerFallacy, AvailabilityBias, EndowmentEffect, StatusQuoBias
  TODO:     (none)
  FUTURE:   (none)

Market Effects (13/13 DONE, 0 TODO, 0 FUTURE)
  DONE:     AssetBubble, HerdEffect, DispositionEffect, MomentumEffect, ReversalEffect,
            ShortSqueeze, VolatilityClustering, FlashCrash, MarketCrash, LiquidityDryup, EquityPremium,
            CarryTradeUnwind
  TODO:     (none)
  FUTURE:   (none)

Historical Events (15/15 DONE, 0 TODO, 0 FUTURE)
  DONE:     BlackMonday1987, LTCMCollapse, DotComBubble, GFC2008, FlashCrash2010,
            Volmageddon, GameStopShortSqueeze, ArchegosCollapse, LUNACollapse, SVBBankRun,
            EuropeanDebtCrisis, AsianFinancialCrisis, TulipMania, SouthSeaBubble, SorosPound
  TODO:     (none)
  FUTURE:   (none)
```

### By Academic Foundation

```
Prospect Theory (Kahneman & Tversky):
  - LossAversion, DispositionEffect, EndowmentEffect, FramingEffect

Behavioral Finance (Thaler):
  - MentalAccounting, OverconfidenceBias, StatusQuoBias

Information Economics:
  - HerdingInformation, HerdEffect, ConfirmationBias, AvailabilityBias

Market Microstructure:
  - FlashCrash, FlashCrash2010, Volmageddon, ShortSqueeze, GameStopShortSqueeze

Leverage & Liquidity:
  - AssetBubble, LTCMCollapse, GFC2008, LiquidityDryup, ArchegosCollapse, CreditCycle

Banking & Runs:
  - SVBBankRun, EuropeanDebtCrisis, CurrencyCrisis

Volatility Dynamics:
  - VolatilityClustering, Volmageddon, MomentumEffect, ReversalEffect

Stablecoin & DeFi:
  - LUNACollapse

Cross-Border & Macro:
  - CarryTradeUnwind, EuropeanDebtCrisis, AsianFinancialCrisis, SorosPound
```

---

## Scenario Template Requirements

Every scenario MUST have the following deliverables:

```
examples/{ScenarioName}/
  Rule/
    players.py      - Rule-based agent implementations (Market + Investors)
    explain.md      - Theoretical foundation, agent descriptions, parameters
    analysis.py     - Post-simulation analysis
    run_{name}.py   - Entry point
    __init__.py     - Package exports
  LLM/
    players.py      - LLM-driven agents (Market from Rule + LLM Investors)
    prompts.py      - System prompts (INVESTOR PERSONALITY ONLY, NO target leakage)
    run_{name}_llm.py
    __init__.py
  RuleLLM/
    players.py      - Hybrid rule + LLM agents
    prompts.py      - System prompts (same anti-leakage rules)
    run_{name}_rulellm.py
    __init__.py
  Rag/
    players.py      - RAG-augmented LLM agents
    prompts.py      - System prompts
    run_{name}_rag.py
    __init__.py
  __init__.py

configs/{ScenarioName}/
  Rule/
    simulation.yml, players.yml, persona.yml, topology.yml
  LLM/
    simulation.yml, players.yml, persona.yml, topology.yml
  RuleLLM/
    simulation.yml, players.yml, persona.yml, topology.yml
  Rag/
    simulation.yml, players.yml, persona.yml, topology.yml
```

---

## Quality Checklist (per scenario)

- [ ] explain.md contains Theoretical Foundation with academic citations
- [ ] Every agent has Theoretical Basis documented
- [ ] LLM prompts describe ONLY investor personality — NO simulation target words
- [ ] Action() uses correct constructor: `Action(action_type=..., payload=..., source_id=...)`
- [ ] No function-level imports (all at file top, grouped stdlib → third-party → local)
- [ ] No inline comments (comments above code only)
- [ ] No defensive `.get()` on known config keys (use `dict["key"]`)
- [ ] All parameters from YAML configs (no hardcoded values)
- [ ] Type hints on all function signatures
- [ ] Google-style docstrings on all public methods
- [ ] English-only comments and documentation
- [ ] `py_compile` passes on all .py files

**Framework-contract layer** (`docs/framework-contract.md`, `docs/llm-coding-rules.md` §11):

- [ ] Every financial player inherits from a canonical base (`CanonicalRulePlayer` / `CanonicalLLMPlayer` / `CanonicalRagPlayer` / `CanonicalMarketCoordinator`), NOT `GeneralPlayer`
- [ ] No `players.py` file overrides `act()` on a canonical subclass (framework act is authoritative)
- [ ] No `players.py` file overrides `decide()` to bypass the payload contract — `decide()` returns `{action, quantity, bid_price, ...}`
- [ ] Per-fill state (VWAP anchor, cost basis, purchase price, avg entry price, acquired units) is updated only inside `on_fill(action, quantity, bid_price)`, never inside `act()` / `decide()`
- [ ] Zero silent-fill fallbacks: no `bid_price = market_data["price"]`, no `payload.get("bid_price", state.price)` anywhere in scenario code
- [ ] Zero direct `state.custom_state["cash" | "position"] ±= ...` mutations outside the base — the base is the single point of truth
- [ ] STRATEGY-id filters use canonical class attributes (`SomeArchetype.STRATEGY`), not hard-coded PascalCase class names or kebab literals
- [ ] `scripts/audit_scenario_contract.py --scenario {ThisScenario}` reports zero CRITICAL/HIGH findings (`STRUCT-ACT`, `STRUCT-DECIDE`, `SEM-SILENT-FILL`, `SEM-CASH-MUT`)
- [ ] For any archetype touched, `PYTHONPATH=. python3 verify_archetype_fixes.py` still reports 24/24 PASS

---

## NEW DOMAIN EXPANSION

> The following sections expand the simulation catalog beyond financial markets
> to cover all human group behavior phenomena suitable for LLM multi-agent simulation.
> Disciplines: Sociology, Political Economy, Public Health, Game Theory,
> Organizational Behavior, Technology & Innovation, Environmental Economics,
> Labor & Institutional Economics, Urban & Spatial Sociology.

---

### D. Social Contagion & Information Dynamics (Sociology)

Scenarios where information, beliefs, and behaviors spread through populations via social influence.

| Scenario             | Phenomenon                          | Key Theory                                             | Core Mechanism                                                | Status |
|----------------------|-------------------------------------|--------------------------------------------------------|---------------------------------------------------------------|--------|
| RumorSpread          | Rumor propagation                   | Allport & Postman (1947) - Psychology of Rumor         | Distortion and amplification through serial transmission      | NEW    |
| EchoChamber          | Polarization by homophily           | Sunstein (2001) - Echo Chambers; Pariser (2011)        | Like-minded reinforcement drives extremity                    | NEW    |
| MisinformationSpread | False info propagation              | Vosoughi et al. (2018) - Spread of true and false news | False news spreads faster/deeper than truth                   | NEW    |
| ViralContent         | Content virality                    | Watts (2002) - Global cascades; Goel et al. (2012)     | Small triggers cascade through vulnerable network structure   | NEW    |
| CancelCulture        | Social media pile-on                | Nguyen (2020) - Cancel culture as sanction             | Moral condemnation cascades into collective punishment        | NEW    |
| InformationCascade   | Sequential ignoring of private info | Bikhchandani et al. (1992)                             | Later actors disregard private signals to follow predecessors | NEW    |
| AttentionEconomy     | Attention as scarce resource        | Wu (2016) - Attention merchants                        | Competition for user attention drives extreme content         | NEW    |

### E. Collective Behavior & Social Movements (Sociology)

Scenarios where individuals coordinate or cascade into group action, from protests to revolutions.

| Scenario             | Phenomenon                     | Key Theory                                       | Core Mechanism                                                 | Status |
|----------------------|--------------------------------|--------------------------------------------------|----------------------------------------------------------------|--------|
| SocialMovement       | Protest emergence              | Granovetter (1978) - Threshold models            | Each person joins when enough others have joined               | NEW    |
| Revolution           | Regime change via cascade      | Kuran (1991) - Preference falsification          | Hidden preferences revealed when critical mass defects         | NEW    |
| RiotEmergence        | Peaceful-to-violent escalation | Granovetter (1978); Berk (1974)                  | Violence thresholds crossed sequentially                       | NEW    |
| PanicBuying          | Hoarding under threat          | Hobfoll (1989) - Conservation of resources       | Perceived scarcity triggers preemptive hoarding                | NEW    |
| BystanderEffect      | Diffusion of responsibility    | Darley & Latane (1968)                           | More bystanders = less likely any individual helps             | NEW    |
| SchellingSegregation | Emergent segregation           | Schelling (1971) - Dynamic models of segregation | Mild homophily preferences produce extreme segregation         | NEW    |
| StampedePanic        | Physical crowd panic           | Helbing et al. (2000) - Escape panic             | Herding instinct in physical escape overrides rational routing | NEW    |
| MoralPanic           | Societal fear amplification    | Cohen (1972) - Folk devils and moral panics      | Media amplification of threat creates public hysteria          | NEW    |

### F. Public Health & Crisis Response (Sociology + Public Health)

Scenarios where human behavior determines health and safety outcomes.

| Scenario             | Phenomenon                      | Key Theory                                       | Core Mechanism                                         | Status |
|----------------------|---------------------------------|--------------------------------------------------|--------------------------------------------------------|--------|
| VaccineHesitancy     | Social influence on vaccination | Basu et al. (2008) - Vaccination game theory     | Free-riding on herd immunity reduces vaccination rates | NEW    |
| EpidemicPanic        | Behavioral disease response     | Funk et al. (2009) - Behavior and disease spread | Fear-driven behavior change alters epidemic trajectory | NEW    |
| QuarantineCompliance | Rule adherence under cost       | Reluga (2010) - Game theory of social distancing | Short-term cost creates non-compliance incentive       | NEW    |
| AnticipatoryAnxiety  | Pre-crisis anxiety cascade      | Barlow (2002) - Anxiety and its disorders        | Uncertainty amplifies fear ahead of confirmed threat   | NEW    |
| MedicalRumoring      | Health misinformation           | Chou et al. (2018) - Health misinformation       | Anecdotal evidence overrides medical authority         | NEW    |

### G. Political Economy & Governance

Scenarios where strategic interaction between political and economic actors produces emergent outcomes.

| Scenario              | Phenomenon                       | Key Theory                                      | Core Mechanism                                                | Status |
|-----------------------|----------------------------------|-------------------------------------------------|---------------------------------------------------------------|--------|
| ArmsRace              | Mutual military escalation       | Richardson (1939); Schelling (1960)             | Fear-driven arms accumulation, no equilibrium                 | NEW    |
| TradeWar              | Escalating protectionism         | Bagwell & Staiger (1990) - Managed trade        | Retaliatory tariffs reduce both sides' welfare                | NEW    |
| RegulatoryCapture     | Regulated capture regulator      | Stigler (1971) - Economic regulation            | Industry influence bends rules in its favor                   | NEW    |
| VotingParadox         | Irrational voter turnout         | Downs (1957) - Economic theory of democracy     | Voting is irrational yet people vote — social motivations     | NEW    |
| SanctionsEscalation   | Economic coercion dynamics       | Hufbauer et al. (2007) - Sanctions reconsidered | Sanctions hurt senders too, creating resolve tests            | NEW    |
| PoliticalPolarization | Population splitting to extremes | DiMaggio et al. (1996); Axelrod (1997)          | Homophilic interaction drives moderate population to extremes | NEW    |
| LobbiesInfluence      | Interest group pressure          | Grossman & Helpman (1994) - Protection for sale | Organized minorities dominate dispersed majorities            | NEW    |
| NationReputation      | Interstate trust/reputation      | Oye (1985) - Cooperation under anarchy          | Past actions shape future trust and cooperation               | NEW    |

### H. Economic Crises & Market Failures (Economics, beyond existing)

Macroeconomic and structural failure scenarios not yet covered.

| Scenario              | Phenomenon                       | Key Theory                                    | Core Mechanism                                                         | Status |
|-----------------------|----------------------------------|-----------------------------------------------|------------------------------------------------------------------------|--------|
| Hyperinflation        | Self-reinforcing inflation       | Cagan (1956) - Monetary dynamics              | Expected inflation drives spending, actualizing inflation              | NEW    |
| DeflationarySpiral    | Self-reinforcing deflation       | Fisher (1933) - Debt-deflation                | Falling prices increase real debt, reducing spending further           | NEW    |
| Stagflation           | Inflation + stagnation           | Blinder (1979); Phelps (1967)                 | Supply shock + demand management create policy trap                    | NEW    |
| ResourceCurse         | Resource wealth instability      | Sachs & Warner (2001); Ross (2001)            | Resource wealth enables rent-seeking, crowding out productive activity | NEW    |
| TragedyOfCommons      | Shared resource overuse          | Hardin (1968); Ostrom (1990)                  | Individual rationality produces collective ruin                        | NEW    |
| PriceWar              | Destructive price competition    | Kreps & Scheinkman (1983)                     | Sequential undercutting destroys industry profits                      | NEW    |
| MarketForLemons       | Adverse selection                | Akerlof (1970) - Market for lemons            | Asymmetric information drives out quality goods                        | NEW    |
| MoralHazard           | Risk-taking with protection      | Pauly (1968); Holmstrom (1979)                | Insurance/protection reduces incentive for caution                     | NEW    |
| MatchingMarket        | Two-sided matching               | Gale & Shapley (1962); Roth (1984)            | Strategic manipulation in centralized matching                         | NEW    |
| PlatformNetworkEffect | Winner-take-all dynamics         | Katz & Shapiro (1985); Rochet & Tirole (2003) | Network externalities lock users into dominant platform                | NEW    |
| SupplyChainDisruption | Cascading supply failure         | Carvalho et al. (2021)                        | Just-in-time fragility amplifies shocks through supply network         | NEW    |
| GigEconomyRace        | Race to bottom in platform labor | Prassl (2018) - Humans as a service           | Competition among workers drives down wages/conditions                 | NEW    |

### I. Social Norms & Cultural Dynamics (Sociology)

Scenarios where norms, conventions, and culture emerge and evolve through interaction.

| Scenario             | Phenomenon                       | Key Theory                                               | Core Mechanism                                                 | Status |
|----------------------|----------------------------------|----------------------------------------------------------|----------------------------------------------------------------|--------|
| NormEmergence        | Convention formation             | Young (1996) - Economics of convention; Bicchieri (2006) | Repeated interaction converges on shared behavioral rules      | NEW    |
| CulturalDiffusion    | Cultural practice spread         | Rogers (1962) - Diffusion of innovations; Axelrod (1997) | Innovations spread through adopter categories                  | NEW    |
| ConformityExperiment | Asch-like group pressure         | Asch (1951) - Effects of group pressure                  | Individuals deny own perception to conform with group          | NEW    |
| ObedienceToAuthority | Milgram-like compliance          | Milgram (1963) - Behavioral study of obedience           | Authority commands override personal morality                  | NEW    |
| TabooViolation       | Social sanction for taboo breach | Fershtman & Gneezy (2001); Douglas (1966)                | Norm violations trigger coordinated social punishment          | NEW    |
| LanguageEvolution    | Linguistic convention emergence  | Lewis (1969) - Convention; Nowak & Krakauer (1999)       | Communication efficiency drives language convergence           | NEW    |
| FashionCycle         | Trend emergence and decay        | Simmel (1904) - Fashion; Pesendorfer (1995)              | Elite differentiation vs mass imitation drives cyclic turnover | NEW    |

### J. Game Theory Classics

Foundational strategic interaction models that produce rich emergent dynamics in multi-agent settings.

| Scenario         | Phenomenon                    | Key Theory                                       | Core Mechanism                                           | Status |
|------------------|-------------------------------|--------------------------------------------------|----------------------------------------------------------|--------|
| PrisonersDilemma | Cooperation vs defection      | Flood & Dresher (1950); Axelrod (1984)           | Individual rationality leads to collective suboptimality | NEW    |
| PublicGoodsGame  | Voluntary contribution        | Ledyard (1995); Fehr & Schmidt (1999)            | Free-riding undermines public good provision             | NEW    |
| UltimatumGame    | Fairness vs rationality       | Guth et al. (1982)                               | Fairness concerns cause rejection of rational offers     | NEW    |
| StagHunt         | Coordination with risk        | Skyrms (2004) - Stag Hunt                        | Safe solo payoff vs risky cooperative payoff             | NEW    |
| BattleOfSexes    | Conflict in coordination      | Luce & Raiffa (1957)                             | Both prefer coordination but disagree on how             | NEW    |
| HawkDove         | Brinkmanship                  | Maynard Smith (1982) - Evolution and game theory | Escalation risks mutual destruction                      | NEW    |
| TrustGame        | Investment and reciprocity    | Berg et al. (1995)                               | Trust enables gains but creates vulnerability            | NEW    |
| AssuranceGame    | Coordination with safe option | Sen (1967) - Assurance game                      | Coordination failure when safe option chosen             | NEW    |

### K. Organizational Behavior

Scenarios where group decision-making dynamics produce systematic failures or successes.

| Scenario            | Phenomenon                 | Key Theory                           | Core Mechanism                                                | Status |
|---------------------|----------------------------|--------------------------------------|---------------------------------------------------------------|--------|
| Groupthink          | Cohesive group failure     | Janis (1972) - Victims of groupthink | Suppression of dissent produces catastrophic decisions        | NEW    |
| AbileneParadox      | Nobody wants the consensus | Harvey (1974) - Abilene Paradox      | False belief about others' preferences drives unwanted action | NEW    |
| SocialLoafing       | Effort reduction in groups | Latane et al. (1979) - Social impact | Individual effort decreases as group size increases           | NEW    |
| OrganizationalSilos | Information hoarding       | Tushman & Nadler (1978)              | Departmental boundaries prevent information flow              | NEW    |
| ParkinsonLaw        | Administrative bloat       | Parkinson (1955) - Parkinson's Law   | Work expands to fill time; staff grows regardless of need     | NEW    |
| PeterPrinciple      | Promotion to incompetence  | Peter & Hull (1969)                  | Competence-based promotion eventually fails                   | NEW    |

### L. Technology & Innovation Economics

Scenarios where technological change, innovation races, and digital dynamics produce emergent outcomes.

| Scenario               | Phenomenon                          | Key Theory                                       | Core Mechanism                                             | Status |
|------------------------|-------------------------------------|--------------------------------------------------|------------------------------------------------------------|--------|
| AIArmsRace             | Competitive AI with safety tradeoff | Bostrom (2014); Armstrong et al. (2016)          | Speed pressure sacrifices safety; first-mover advantage    | NEW    |
| CryptocurrencyAdoption | Network trust in crypto             | Halaburda & Sarvary (2016); Baur & Dimpfl (2018) | Network effects and trust determine adoption               | NEW    |
| DataPrivacyParadox     | Stated vs revealed privacy          | Acquisti & Grossklags (2005)                     | People say they value privacy but trade it for convenience | NEW    |
| DeepfakeThreat         | Synthetic media erosion of trust    | Chesney & Citron (2019)                          | Widespread synthetic media degrades trust in all media     | NEW    |
| AlgorithmicBias        | ML system discrimination            | O'Neil (2016) - Weapons of math destruction      | Historical bias embedded in automated decisions            | NEW    |
| TechAdoptionS Curve    | Technology diffusion pattern        | Rogers (1962) - Diffusion of innovations         | S-shaped adoption curve through innovators to laggards     | NEW    |

### M. Environmental & Resource Economics

Scenarios where shared environmental resources create strategic dilemmas.

| Scenario           | Phenomenon                   | Key Theory                                     | Core Mechanism                                  | Status |
|--------------------|------------------------------|------------------------------------------------|-------------------------------------------------|--------|
| ClimateNegotiation | Int'l climate agreement      | Barrett (1994) - Self-enforcing agreements     | Free-riding undermines cooperative abatement    | NEW    |
| Overfishing        | Fishery depletion            | Clark (1973) - Overexploitation; Hardin (1968) | Open access + discounting drives stock collapse | NEW    |
| PollutionGame      | Upstream-downstream dynamics | Copeland & Taylor (1994)                       | Polluter gains, downstream bears cost           | NEW    |
| WaterScarcity      | Shared water conflict        | Dinar et al. (2007) - Water allocation         | Competing demands exceed renewable supply       | NEW    |
| Desertification    | Land degradation cascade     | Reij et al. (2009)                             | Feedback between overuse and degradation        | NEW    |

### N. Historical Social Events (Non-Financial)

Real-world events where human group behavior produced notable outcomes, beyond financial markets.

| Scenario            | Event                           | Year    | Key Theory                                                    | Status |
|---------------------|---------------------------------|---------|---------------------------------------------------------------|--------|
| ArabSpring          | Arab world revolts              | 2011    | Kuran (1991) - Preference falsification; Howard et al. (2011) | NEW    |
| FrenchRevolution    | Regime collapse                 | 1789    | Kuran (1991); Tilly (1978) - From mobilization to revolution  | NEW    |
| ColdWarEscalation   | Nuclear arms race               | 1947-91 | Schelling (1960); Richardson (1939)                           | NEW    |
| CubanMissileCrisis  | Brinkmanship resolution         | 1962    | Schelling (1966) - Arms and influence                         | NEW    |
| SalemWitchTrials    | Mass hysteria                   | 1692    | Boyer & Nissenbaum (1974); Mullen et al. (2003)               | NEW    |
| McCarthyism         | Red Scare persecution           | 1950-54 | Arendt (1951); Mullen et al. (2003)                           | NEW    |
| CivilRightsMovement | Non-violent social change       | 1954-68 | McAdam (1982); Morris (1984)                                  | NEW    |
| FallOfBerlinWall    | Cascade of regime defection     | 1989    | Kuran (1991); Lohmann (1994)                                  | NEW    |
| COVIDPanicBuying    | Pandemic hoarding               | 2020    | Hobfoll (1989); Steelman & McCaffrey (2013)                   | NEW    |
| MeTooMovement       | Social norm cascade             | 2017    | Bicchieri (2006) - Norm shift; Sunstein (2019)                | NEW    |
| OpiumWars           | Trade conflict escalation       | 1839-60 | Fairbank (1953); Polachek (1992)                              | NEW    |
| RwandanGenocide     | Propaganda-driven mass violence | 1994    | Straus (2006); Yanagizawa-Drott (2014)                        | NEW    |

### O. Additional Behavioral Biases (Cognitive Psychology)

Cognitive biases beyond the existing 14 that drive systematic errors in group settings.

| Scenario            | Phenomenon                       | Key Theory                                       | Core Mechanism                                         | Status |
|---------------------|----------------------------------|--------------------------------------------------|--------------------------------------------------------|--------|
| DunningKrugerEffect | Incompetent overconfidence       | Kruger & Dunning (1999)                          | Lack of metacognitive skill prevents self-assessment   | NEW    |
| SurvivorshipBias    | Ignoring failures                | Elton et al. (1996)                              | Only survivors visible, distorting outcome assessment  | NEW    |
| BandwagonEffect     | Following the crowd              | Leibenstein (1950)                               | Adoption increases solely because others adopted       | NEW    |
| NormalcyBias        | Underestimating disaster         | Omer & Alon (1994); Drabek (1999)                | Normalcy assumption prevents disaster preparation      | NEW    |
| OptimismBias        | Overestimating positive outcomes | Weinstein (1980); Sharot (2011)                  | Systematic overestimation of favorable outcomes        | NEW    |
| AuthorityBias       | Overweighting authority          | Milgram (1963); Zelditch (2001)                  | Perceived authority overrides independent judgment     | NEW    |
| HaloEffect          | Trait spillover                  | Thorndike (1920); Nisbett & Wilson (1977)        | One positive trait biases assessment of all others     | NEW    |
| PlanningFallacy     | Underestimating time/cost        | Buehler et al. (1994); Kahneman & Tversky (1979) | Optimistic scenarios ignore distributional information | NEW    |
| IllusionOfControl   | Skill attribution to chance      | Langer (1975)                                    | Personal involvement creates false sense of control    | NEW    |
| BaseRateFallacy     | Ignoring prior probabilities     | Bar-Hillel (1980)                                | Specific evidence overwhelms base rate statistics      | NEW    |

### P. Labor & Institutional Economics

Scenarios where labor markets, institutions, and contracts produce emergent dynamics.

| Scenario              | Phenomenon               | Key Theory                                | Core Mechanism                                          | Status |
|-----------------------|--------------------------|-------------------------------------------|---------------------------------------------------------|--------|
| WageNegotiation       | Collective bargaining    | Nash (1950); Rubinstein (1982)            | Bargaining power, outside options, strike threat        | NEW    |
| LaborMarketSignaling  | Education as signal      | Spence (1973); Stiglitz (1975)            | Costly signaling separates high/low ability             | NEW    |
| EfficiencyWage        | Above-market wage puzzle | Shapiro & Stiglitz (1984)                 | Higher wages reduce shirking via unemployment threat    | NEW    |
| InsiderOutsiderTheory | Dual labor markets       | Lindbeck & Snower (1988)                  | Insiders protect positions against outsider competition | NEW    |
| UnionCollectiveAction | Union formation          | Olson (1965) - Logic of collective action | Selective incentives needed to overcome free-riding     | NEW    |

### Q. Urban & Spatial Sociology

Scenarios where spatial distribution and location decisions produce emergent social patterns.

| Scenario        | Phenomenon                  | Key Theory                              | Core Mechanism                                            | Status |
|-----------------|-----------------------------|-----------------------------------------|-----------------------------------------------------------|--------|
| Gentrification  | Neighborhood transformation | Smith (1979); Freeman (2005)            | In-migration raises costs, displacing original residents  | NEW    |
| UrbanSprawl     | Suburban expansion          | Brueckner (2000); Glaeser & Kahn (2004) | Individual location decisions produce inefficient sprawl  | NEW    |
| NIMBYDynamics   | Opposition to development   | Fischel (2001) - Homevoter hypothesis   | Residents protect property values by blocking development | NEW    |
| SpatialMismatch | Jobs-housing disconnect     | Kain (1968) - Housing segregation       | Segregation disconnects workers from employment           | NEW    |

### R. Information Warfare & Cyber (Political Science)

Scenarios where information is weaponized for strategic advantage.

| Scenario             | Phenomenon                       | Key Theory                                         | Core Mechanism                                                  | Status |
|----------------------|----------------------------------|----------------------------------------------------|-----------------------------------------------------------------|--------|
| InfluenceOperation   | State disinformation             | Benkler et al. (2018); Woolley & Howard (2018)     | Coordinated inauthentic behavior shapes opinion                 | NEW    |
| CyberAttackCascade   | Cascading infrastructure failure | Lelarge (2009); Gao et al. (2016)                  | Single point failure cascades through interdependent systems    | NEW    |
| ElectionInterference | Electoral manipulation           | Rid (2020) - Active measures                       | Foreign actors exploit domestic divisions to influence outcomes | NEW    |
| PropagandaSpread     | State propaganda diffusion       | Ellul (1965) - Propaganda; Herman & Chomsky (1988) | Repetition and authority make propaganda effective              | NEW    |

### S. Network Science & Complexity

Scenarios where network topology and cascading dynamics produce emergent macro-phenomena.

| Scenario               | Phenomenon              | Key Theory                           | Core Mechanism                                       | Status |
|------------------------|-------------------------|--------------------------------------|------------------------------------------------------|--------|
| CascadingFailure       | Infrastructure collapse | Watts (2002); Buldyrev et al. (2010) | Interdependent network failure cascades              | NEW    |
| PreferentialAttachment | Rich-get-richer         | Barabasi & Albert (1999)             | Popular nodes attract more connections               | NEW    |
| SmallWorldCascade      | Local-global cascade    | Watts & Strogatz (1998)              | Shortcuts enable global cascades from local triggers | NEW    |
| EpidemicThreshold      | Tipping point in spread | Pastor-Satorras & Vespignani (2001)  | Below threshold: dies out; above: global epidemic    | NEW    |

---

## Updated Coverage Matrix

### By Phenomenon Type

```
=== FINANCIAL (IMPLEMENTED) ===

Behavioral Biases (14/14 DONE)
  DONE: OverconfidenceBias, LossAversion, HerdingInformation, AnchoringEffect, MentalAccounting,
        ConfirmationBias, GamblerFallacy, AvailabilityBias, EndowmentEffect, StatusQuoBias,
        SunkCostFallacy, RepresentativenessBias, FramingEffect, HindsightBias

Market Effects (14/14 DONE)
  DONE: AssetBubble, HerdEffect, DispositionEffect, MomentumEffect, ReversalEffect,
        ShortSqueeze, VolatilityClustering, FlashCrash, MarketCrash, LiquidityDryup, EquityPremium,
        CarryTradeUnwind, CreditCycle, CurrencyCrisis

Historical Financial Events (15/15 DONE)
  DONE: BlackMonday1987, LTCMCollapse, DotComBubble, GFC2008, FlashCrash2010,
        Volmageddon, GameStopShortSqueeze, ArchegosCollapse, LUNACollapse, SVBBankRun,
        EuropeanDebtCrisis, AsianFinancialCrisis, TulipMania, SouthSeaBubble, SorosPound

=== INTERDISCIPLINARY (PROPOSED) ===

D. Social Contagion & Information Dynamics (7 NEW)
  NEW: RumorSpread, EchoChamber, MisinformationSpread, ViralContent, CancelCulture,
       InformationCascade, AttentionEconomy

E. Collective Behavior & Social Movements (8 NEW)
  NEW: SocialMovement, Revolution, RiotEmergence, PanicBuying, BystanderEffect,
       SchellingSegregation, StampedePanic, MoralPanic

F. Public Health & Crisis Response (5 NEW)
  NEW: VaccineHesitancy, EpidemicPanic, QuarantineCompliance, AnticipatoryAnxiety,
       MedicalRumoring

G. Political Economy & Governance (8 NEW)
  NEW: ArmsRace, TradeWar, RegulatoryCapture, VotingParadox, SanctionsEscalation,
       PoliticalPolarization, LobbiesInfluence, NationReputation

H. Economic Crises & Market Failures (12 NEW)
  NEW: Hyperinflation, DeflationarySpiral, Stagflation, ResourceCurse, TragedyOfCommons,
       PriceWar, MarketForLemons, MoralHazard, MatchingMarket, PlatformNetworkEffect,
       SupplyChainDisruption, GigEconomyRace

I. Social Norms & Cultural Dynamics (7 NEW)
  NEW: NormEmergence, CulturalDiffusion, ConformityExperiment, ObedienceToAuthority,
       TabooViolation, LanguageEvolution, FashionCycle

J. Game Theory Classics (8 NEW)
  NEW: PrisonersDilemma, PublicGoodsGame, UltimatumGame, StagHunt, BattleOfSexes,
       HawkDove, TrustGame, AssuranceGame

K. Organizational Behavior (6 NEW)
  NEW: Groupthink, AbileneParadox, SocialLoafing, OrganizationalSilos,
       ParkinsonLaw, PeterPrinciple

L. Technology & Innovation Economics (6 NEW)
  NEW: AIArmsRace, CryptocurrencyAdoption, DataPrivacyParadox, DeepfakeThreat,
       AlgorithmicBias, TechAdoptionS Curve

M. Environmental & Resource Economics (5 NEW)
  NEW: ClimateNegotiation, Overfishing, PollutionGame, WaterScarcity, Desertification

N. Historical Social Events (12 NEW)
  NEW: ArabSpring, FrenchRevolution, ColdWarEscalation, CubanMissileCrisis,
       SalemWitchTrials, McCarthyism, CivilRightsMovement, FallOfBerlinWall,
       COVIDPanicBuying, MeTooMovement, OpiumWars, RwandanGenocide

O. Additional Behavioral Biases (10 NEW)
  NEW: DunningKrugerEffect, SurvivorshipBias, BandwagonEffect, NormalcyBias,
       OptimismBias, AuthorityBias, HaloEffect, PlanningFallacy, IllusionOfControl,
       BaseRateFallacy

P. Labor & Institutional Economics (5 NEW)
  NEW: WageNegotiation, LaborMarketSignaling, EfficiencyWage, InsiderOutsiderTheory,
       UnionCollectiveAction

Q. Urban & Spatial Sociology (4 NEW)
  NEW: Gentrification, UrbanSprawl, NIMBYDynamics, SpatialMismatch

R. Information Warfare & Cyber (4 NEW)
  NEW: InfluenceOperation, CyberAttackCascade, ElectionInterference, PropagandaSpread

S. Network Science & Complexity (4 NEW)
  NEW: CascadingFailure, PreferentialAttachment, SmallWorldCascade, EpidemicThreshold

=== SUMMARY ===
  Financial (implemented):  43 scenarios (14+14+15)
  Interdisciplinary (NEW):  111 scenarios
  TOTAL:                   154 scenarios
```

### By Academic Foundation

```
Prospect Theory (Kahneman & Tversky):
  - LossAversion, DispositionEffect, EndowmentEffect, FramingEffect, OptimismBias

Behavioral Finance (Thaler):
  - MentalAccounting, OverconfidenceBias, StatusQuoBias, SunkCostFallacy

Information Economics:
  - HerdingInformation, HerdEffect, ConfirmationBias, AvailabilityBias,
    MisinformationSpread, MarketForLemons, LaborMarketSignaling

Market Microstructure:
  - FlashCrash, FlashCrash2010, Volmageddon, ShortSqueeze, GameStopShortSqueeze

Leverage & Liquidity:
  - AssetBubble, LTCMCollapse, GFC2008, LiquidityDryup, ArchegosCollapse, CreditCycle

Banking & Runs:
  - SVBBankRun, EuropeanDebtCrisis, CurrencyCrisis

Volatility Dynamics:
  - VolatilityClustering, Volmageddon, MomentumEffect, ReversalEffect

Stablecoin & DeFi:
  - LUNACollapse, CryptocurrencyAdoption

Cross-Border & Macro:
  - CarryTradeUnwind, EuropeanDebtCrisis, AsianFinancialCrisis, SorosPound,
    TradeWar, SanctionsEscalation, ClimateNegotiation

Threshold Models (Granovetter):
  - SocialMovement, RiotEmergence, SchellingSegregation, VaccineHesitancy

Preference Falsification (Kuran):
  - Revolution, ArabSpring, FallOfBerlinWall, Groupthink, AbileneParadox

Diffusion & Cascades (Rogers / Watts):
  - ViralContent, CulturalDiffusion, TechAdoptionSCurve, EpidemicThreshold,
    SmallWorldCascade, CascadingFailure

Game Theory (Axelrod / Nash):
  - PrisonersDilemma, PublicGoodsGame, UltimatumGame, StagHunt, BattleOfSexes,
    HawkDove, TrustGame, AssuranceGame, ArmsRace

Social Norms (Bicchieri / Young):
  - NormEmergence, TabooViolation, FashionCycle, CancelCulture, MeTooMovement

Obedience & Authority (Milgram / Zelditch):
  - ObedienceToAuthority, AuthorityBias, PropagandaSpread, McCarthyism

Collective Behavior (Le Bon / Smelser):
  - PanicBuying, StampedePanic, MoralPanic, BystanderEffect, EpidemicPanic

Environmental Economics (Hardin / Ostrom):
  - TragedyOfCommons, Overfishing, ClimateNegotiation, PollutionGame,
    WaterScarcity, ResourceCurse

Organizational (Janis / Parkinson):
  - Groupthink, AbileneParadox, SocialLoafing, OrganizationalSilos,
    ParkinsonLaw, PeterPrinciple

Innovation & Technology (Perez / Bostrom):
  - AIArmsRace, DataPrivacyParadox, DeepfakeThreat, AlgorithmicBias,
    PlatformNetworkEffect, GigEconomyRace

Political Economy (Stigler / Schelling):
  - RegulatoryCapture, VotingParadox, PoliticalPolarization, LobbiesInfluence,
    NationReputation, ElectionInterference
```
