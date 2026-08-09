---
name: market-design-skill
purpose: Format-locked, unified handbook for designing a single simulation MARKET COORDINATOR agent — the environment-side player that clears trades, forms prices, propagates information, or coordinates any other shared state variable. Produces self-contained specifications suitable for inclusion under masim/agents/defines/market/{market-type}-{coordinator-stem}.md across any simulation domain.
status: canonical
audience: Authors and reviewers of MARKET COORDINATOR specifications for multi-agent simulations. This handbook is a sibling of `agent-design-skill.md`; participant agents (investors, opinion holders, depositors, etc.) belong to that handbook. Coordinator / environment / matching-engine / broadcast-hub agents belong here.
rfc2119: This document uses MUST / MUST NOT / SHOULD / MAY in the RFC-2119 sense.
---

# Simulation Market Coordinator Design Handbook

This handbook is the **single source of truth** for designing any
simulation **market coordinator** — the environment-side participant
that clears trades, forms prices, aggregates opinions, propagates
rumours, tracks reserves, or otherwise coordinates any shared state
variable that participant agents read from and write to.

A "market" in this handbook is any coordinator agent that
(a) collects inbound messages/orders from participant agents,
(b) applies a mechanism to derive one or more shared observables,
(c) broadcasts those observables back to participant agents.

The coordinator is fundamentally an agent (in the codebase it inherits
from `masim.player.general.GeneralPlayer`, same base class as
investors), but it plays the **role of the environment**. Because its
identity is dominated by the *kind of market it models*, this handbook
elevates **Market Type** to a first-class classification dimension —
present in the file name, the icon file name, the Summary table, and
the Design Provenance block.

## 0. Relationship to `agent-design-skill`

- Participant agents (investors, depositors, opinion holders,
  bank managers, hedge funds, etc.) → follow `agent-design-skill.md`,
  stored under `masim/agents/defines/{domain}/{stem}.md`.
- Market coordinators (price-formation engines, opinion
  environments, rumour-propagation hubs, order-matching engines,
  reserve trackers, etc.) → follow THIS handbook, stored under
  `masim/agents/defines/market/{market-type}-{coordinator-stem}.md`.

The two handbooks share the "agent-design DNA" (evidence provenance,
canonical section order, cross-section traceability), but the market
handbook diverges where the coordinator role demands it:

1. **Market Type** is elevated to a required top-level classifier.
2. **§3.3 Definition and Goals** describes what the coordinator
   models (matching engine / price formation / opinion aggregation /
   reserve dynamics / …), not what a participant does.
3. **§3.6 Behavioral Framework** is renamed **Coordination Framework**
   and its I/O Contract binds *inbound orders* → *broadcast payload*,
   not `<analysis>/<decision>` tags.
4. **§3.6.3 "Action Space"** is renamed **Broadcast Space** — what the
   coordinator emits to all participants each round.
5. Market coordinators MUST declare **Environmental Parameters**
   (price-impact λ, mean-reversion γ, noise σ, opinion inertia,
   propagation probability, reserve depletion rate, etc.) rather than
   individual-participant knobs.

Everything else (evidence provenance rules, cross-section consistency,
validation checklist depth) is inherited from `agent-design-skill.md`
and re-expressed in market-native language below.

## 1. When to Use This Handbook

Apply this handbook whenever you:

- Author a brand-new market-coordinator specification for the pool.
- Fork an existing coordinator into a differently-parameterised
  variant (e.g. a fast-mean-reverting stock market vs. a slow-drift
  stock market).
- Refactor legacy `class Market` / `class OpinionEnvironment` /
  `class InformationEnvironment` code into a pool-conformant profile.
- Audit that every scenario's coordinator has a matching pool profile
  and that the profile is up-to-date with the code.

If you are only editing prose inside an already-conformant section you
do not need to re-run the full validation checklist, but section
names, header levels, and table headers MUST remain identical.

## 2. Market Type Taxonomy **(MANDATORY, TOP-LEVEL CLASSIFIER)**

Every market coordinator profile MUST declare a **Market Type** as its
primary classifier. Market Type answers *"what kind of market is
this coordinator?"* and MUST be surfaced in three places:

1. The file name: `{market-type-slug}-{coordinator-stem}.md`.
2. The `## Summary` table's first row.
3. The icon file name (see `market-icon-generation-skill.md`).

### 2.1 Canonical Market Type Palette

Authors MUST pick one canonical slug from the palette below. If a
scenario truly requires a new market type, add it here in the same
commit that adds the new coordinator profile, and cite evidence for
the addition.

| Market Type slug   | English label                    | Chinese label   | Typical shared state           | Example scenarios                                             |
|--------------------|----------------------------------|-----------------|--------------------------------|---------------------------------------------------------------|
| `stock`            | Stock / Equity Market            | 股票市场        | Price, fundamental, volume     | AnchoringEffect, AssetBubble, BlackMonday1987, FlashCrash2010 |
| `fx`               | Foreign-Exchange Market          | 外汇市场        | Exchange rate, reserves, peg   | SorosPound, AsianFinancialCrisis, CarryTradeUnwind            |
| `commodity`        | Commodity Market                 | 商品市场        | Spot price, inventory          | TulipMania                                                    |
| `bond`             | Sovereign / Corporate Bond       | 债券市场        | Yield, spread, default premium | EuropeanDebtCrisis                                            |
| `deposit`          | Bank Deposit / Run Market        | 存款/挤兑市场   | Deposit stock, liquidity ratio | SVBBankRun                                                    |
| `credit`           | Credit / Lending Market          | 信贷市场        | Loan supply, credit spread     | CreditCycle, GFC2008                                          |
| `crypto`           | Crypto / Stablecoin Market       | 加密/稳定币市场 | Peg deviation, on-chain supply | LUNACollapse                                                  |
| `historical-asset` | Historical / Speculative Asset   | 历史投机市场    | Speculative price, subscribers | SouthSeaBubble                                                |
| `derivatives`      | Options / Volatility Market      | 衍生品市场      | Implied vol, gamma exposure    | Volmageddon                                                   |
| `opinion`          | Opinion / Belief Environment     | 舆论/观点场     | Opinion vector, cluster stats  | EchoChamber, ConfirmationBias, HerdingInformation             |
| `information`      | Information / Rumour Environment | 信息/谣言场     | Rumour state, adoption ratio   | RumorSpread                                                   |

### 2.2 File-Naming Rule

For a stock-market coordinator with stem `standard-price-impact`:

```
masim/agents/defines/market/stock-standard-price-impact.md
```

For an opinion environment with stem `echo-chamber-clustering`:

```
masim/agents/defines/market/opinion-echo-chamber-clustering.md
```

The `{market-type-slug}-` prefix is **not optional**. The `stem`
portion MUST be kebab-case and describe the coordination *mechanism*,
not the phenomenon (e.g. `standard-price-impact`, not `asset-bubble`,
because one mechanism drives many scenarios).

## 3. Canonical Section Order

A conformant profile MUST contain at least the top-level sections
below, in order.

| #  | Section                                       | Header | Notes                                            |
|----|-----------------------------------------------|--------|--------------------------------------------------|
| 1  | Title — coordinator role phrase               | `#`    | Sentence-cased, NOT a class name                 |
| 2  | Summary                                       | `##`   | ≥8 rows including Market Type FIRST              |
| 3  | Definition and Goals                          | `##`   | Includes non-goals                               |
| 4  | Theoretical / Mechanistic Foundation          | `##`   | ≥1 sub-block                                     |
| 5  | Activation, Lifecycle, and Coordination Cadence | `##` | Init contract + `perceive/decide/act` mapping    |
| 6  | Coordination Framework                        | `##`   | ≥7 H4 sub-blocks (I/O Contract + Invariants + minimum set) |
| 7  | Environmental Parameters                      | `##`   | ≥8-column table, grouped into 4 categories (§4.7.1) |
| 8  | Worked Numerical Examples                     | `##`   | ≥3 cases + 1 edge case                           |
| 9  | Coordinator Verification and Calibration      | `##`   | Includes Ablation Hooks sub-block                |
| 10 | Academic / Empirical References               | `##`   |                                                  |
| 11 | Design Provenance and Versioning              | `##`   | Includes MANDATORY `| Icon |` row and Market Type |

## 4. Section-by-Section Requirements

### 4.1 Title

- One H1 line, sentence-cased descriptive role phrase.
- MUST NOT be a class identifier or code-style token.
- MUST describe the coordinator's *role* (e.g. "Standard price-impact
  stock market"), not its implementation (`Market`, `OpinionEnv`).

### 4.2 Summary

Fingerprint table with **at least the eight rows below, in order**.
The first row MUST be `Market Type`.

```markdown
## Summary

| Field                | Content                                                                            |
|----------------------|------------------------------------------------------------------------------------|
| Market Type          | <canonical Market Type slug + English label> (e.g. `stock` — Stock/Equity Market)  |
| Coordinator Role     | <one-line role phrase, matches the H1>                                             |
| Mechanism Family     | <e.g. Standard price-impact, Order-book matching, DeGroot averaging, SIS contagion> |
| Shared State         | <what observables the coordinator computes and broadcasts>                         |
| Broadcast Cadence    | <every-tick / every-N-ticks / event-driven>                                        |
| Determinism          | <deterministic / stochastic-given-seed / non-deterministic>                        |
| Feedback Direction   | **Stabilising** / **Amplifying** / **Neutral** / **Regime-dependent** — one-line rationale |
| Scenario Portability | <how many scenarios in the pool currently reuse this coordinator>                  |
```

**Feedback Direction** classifies whether the mechanism inherently
pushes shared state TOWARD equilibrium (Stabilising, e.g. strong
mean-reversion), AWAY from it (Amplifying, e.g. positive-feedback
opinion echo), does neither by design (Neutral, e.g. pure random
walk with no feedback), or switches direction based on state /
regime (**Regime-dependent**, e.g. standard price-impact +
mean-reversion is stabilising inside a band around the fundamental
but amplifying when speculative positions dominate net demand).
Regime-dependent MUST be decomposed inline into the regime boundary
(state / parameter threshold) and the direction on each side. This
is intrinsic to the mechanism, NOT a judgment about scenario
outcomes.

### 4.3 Definition and Goals

Three paragraphs (8–14 sentences total):

1. **What the coordinator models.** Name the real-world market or
   coordination process (a limit-order book equity market, a spot
   FX market, an interbank overnight lending market, a Twitter-like
   opinion channel, an epidemic-style rumour cascade, etc.). Cite
   evidence that this coordination structure exists and has been
   studied.
2. **Coordination goal.** State exactly what the coordinator computes
   and broadcasts each round (e.g. "aggregates buy/sell orders,
   forms one price P(t+1) via the standard price-impact model, and
   broadcasts {price, prev_price, fundamental, deviation, volume}").
3. **Role inside the simulation + non-goals.** Describe what the
   coordinator *is not* responsible for (≥2 explicit non-goals). Example
   non-goals: "MUST NOT filter individual orders based on participant
   identity"; "MUST NOT inject exogenous news shocks — that is the
   scenario driver's responsibility"; "MUST NOT enforce
   position/inventory limits on participants — that is a participant
   self-imposed constraint per `agent-design-skill.md` §3.6.3".

### 4.4 Theoretical / Mechanistic Foundation

For each underlying theory or documented mechanism, supply one
sub-block with the labelled lines below. ≥1 sub-block is required.
Coordinators built from multiple mechanisms (e.g. price-impact + noise
+ mean-reversion) MAY combine them in one sub-block if they are
inseparable, or split them into ≥2 sub-blocks if each has independent
provenance.

```markdown
**<Mechanism Name>**:
- Theory / Study: <name>
- Citation: <full citation + DOI>
- Core Insight: <2–3 sentences explaining the mechanism>
- Mathematical Formulation: `<one implementable equation>`
- Empirical Evidence: <study, dataset, effect size / stylised fact>
- Relevance to This Coordinator: <how the coordinator operationalises it>
- Calibration Source: <paper / dataset + specific numeric range>
- Falsification Conditions: <observable market-level behaviour + threshold>
- Alternative Mechanisms: <named competing mechanisms that could be swapped in>
```

Same depth rules apply as in `agent-design-skill.md` §3.4:
implementable equations only, empirical evidence with effect sizes,
citations with DOIs, and falsification conditions with quantitative
thresholds.

### 4.5 Activation, Lifecycle, and Coordination Cadence

This section binds the coordinator to the `masim` player lifecycle
(`GeneralPlayer.perceive → decide → act`) and pins down the exact
initialization contract. Nine required blocks in order.

```markdown
Purpose: <one sentence — what coordination this environment provides>

Coordination Cadence: <every-tick / every-N-ticks / event-driven-on-trigger-X>

Lifecycle Mapping (MANDATORY — binds the coordinator to
`masim.player.general.GeneralPlayer`):
- perceive(observation, prev_result):
  1. read round number from observation
  2. run the State Initialization block below ONCE on round 0 / first call
  3. drain `observation.inbounds` into aggregate signals per §4.6.1
  4. compute the state transition per §4.6.2 (READ phase only — no writes yet)
  5. commit state writes per §4.6.2 (WRITE phase)
- decide():
  1. assemble the broadcast payload from committed state
  2. return a dict conforming to §4.6.0 Outputs
- act(decision):
  1. wrap the broadcast payload as MarketBroadcast (or engine-equivalent)
  2. emit to every participant via the standard outbox

MUST NOT: perform state writes inside `decide` or `act`; perform
broadcast emission inside `perceive`. Splitting these phases correctly
is required for deterministic replay and for the round-boundary
guarantee in §4.6.6 Invariants.

State Initialization (MANDATORY — first-call contract):
- Trigger: `"<primary_state_key>" not in self.state.custom_state`
- Required extras (raise KeyError on missing):
  - <list every extras key needed for init, e.g. `initial_price`,
    `fundamental_value`, `price_impact`, `mean_reversion`, `noise_std`,
    `record_path`, `custom_state_hot_limit`>
- Initial state writes (single atomic block):
  - `state["<primary_state_key>"] = extras["<initial_key>"]`
  - `state["prev_<primary_state_key>"] = extras["<initial_key>"]`
    (equal to current on round 0 — this is what cold-start observers see)
  - `state["fundamental"] = extras["fundamental_value"]` (if applicable)
  - `state["<history_buffer>"] = HistoryBuffer(folder=..., entry_limit=hot_limit)`
- Warm-up rounds: <N rounds during which the broadcast is emitted but
  participants are expected to treat it as unreliable> — default `0`.
- Cold-start reading rule for participants: `prev_state == state` on
  round 0 SHOULD be interpreted as "no return yet", NOT as "zero return".

Inbound Message Types (what participants may send to the coordinator):
- <MessageType A>: <fields, e.g. {"action": "buy"|"sell"|"hold", "quantity": int, "bid_price": float}>
- <MessageType B>: <fields>
- <Default>: <hold / no-message>

Broadcast Trigger:
- <Trigger>: <after every round tick / after N inbound messages / …>

Missing-Input Policy: <what the coordinator does when zero participants
respond, when required extras keys are missing, when order fields are
NaN or unparseable. Recommended defaults:
- Missing required extras → raise KeyError immediately (do NOT default).
- Zero inbound orders → set aggregates to 0 and continue (this is a
  legitimate quiet round, not a failure).
- Unparseable individual order → log warning, skip that order, continue.
- NEVER silently substitute a default for a required field — that
  masks bugs (see project code-style rule).>

Exogenous Driver Boundary (MANDATORY):
- The coordinator MUST NOT generate exogenous news, shocks, regime
  flips, or parameter changes from within its own logic.
- All exogenous drivers MUST enter via one of two channels:
  (a) a distinguished inbound message from a `ScenarioDriver` /
      `NewsInjector` agent (recommended), OR
  (b) a mutation of `config.extras` performed BEFORE the coordinator's
      `perceive` on that round by the scenario runner.
- The coordinator MAY read exogenous driver state as an ordinary
  aggregate signal but MUST NOT ORIGINATE it.

Environmental Dependencies:
- Configuration extras keys required from `players.yml` (list them all;
  every listed key MUST also appear in §4.7 with a default value)
- Required scenario driver signals (news feed, exogenous shock, …), if any
- If none beyond declared extras, state "none beyond §4.7 parameters."
```

**Missing-Input Policy** is critical: per the user's code-style
preference recorded in `masim/skills/`, masking invalid inputs with
defaults is an anti-pattern. Coordinators SHOULD raise on missing
required extras, and MAY clamp only for optional deviations.

### 4.6 Coordination Framework

Six H4 sub-sections in order. All six MUST be present.

#### 4.6.0 I/O Contract **(MANDATORY, contract-strength)**

Binding interface between coordinator design and every implementation
variant declared in the target's §10.1 Variant Build Matrix (finance
default `Rule / LLM / RuleLLM / Rag`; any subset/superset/renaming
permitted). On conflict with prose elsewhere, this section wins.

Five required blocks: **Inputs**, **Outputs**, **Content
Constraints**, **Serialization Format**, **Implementer Contract
Reminder**.

```markdown
##### Inputs (per coordination call)

| Input                | Source                                | Type / Shape                                    | Required? | Notes                                                    |
|----------------------|---------------------------------------|-------------------------------------------------|-----------|----------------------------------------------------------|
| `inbound_orders`     | mailbox from participant agents       | `list[dict]` with fields per §4.5 MessageType   | yes       | Per-order schema binding                                 |
| `current_state`      | coordinator's own persisted state     | as declared in §4.6.4 Mathematical Model        | yes       | populated on first call by init                          |
| `context_metadata`   | scheduler / round header              | `round: int`, `identity: str`, `seed: int`      | yes       | Identity naming rule: `{variant}_market_{market_type}`   |
| `scenario_driver`    | scenario-level shock / news feed      | `dict` or `None`                                | no        | Only if scenario declares exogenous drivers              |

##### Outputs (per coordination call)

The coordinator MUST emit exactly one **broadcast object** per call.
Every participant reads the SAME broadcast — no per-participant
routing at this layer.

| Field            | Type   | Valid Range / Enum      | Unit                              | Required? | Meaning                                            |
|------------------|--------|-------------------------|-----------------------------------|-----------|----------------------------------------------------|
| `<state_var_1>`  | float  | domain declared in §4.6.4 | as declared                    | yes       | Primary shared state (e.g. `price`, `opinion_mean`) |
| `<prev_state>`   | float  | same as state_var_1     | as declared                       | yes       | Value at previous tick — REQUIRED for participants |
| `<fundamental>`  | float  | domain declared in §4.6.4 | as declared                    | conditional | Anchor / equilibrium reference (if the mechanism has one) |
| `<deviation>`    | float  | typically [-1, +∞)      | fraction                          | conditional | (state − fundamental) / fundamental                |
| `<volume>` etc.  | float  | ≥ 0                     | as declared                       | conditional | Round activity metric                              |
| `round`          | int    | ≥ 0                     | —                                 | yes       | Which coordination round produced this broadcast   |

Every emitted field MUST be listed here. Any downstream participant
that reads a field not declared here indicates a broken contract.

##### Content Constraints

- **Required fields**: every `Required? = yes` field MUST be present
  every round.
- **Forbidden fields**: fields not declared above MUST NOT be
  broadcast — extra fields silently break participant parsers.
- **Value ranges**: numeric fields MUST be clamped to their declared
  valid range before broadcast. Example: `price = max(new_price, 0.01)`.
- **Units and sign conventions**: state units MUST match the
  participant-side `StandardMarketState.from_market_data()` contract
  in `masim/format/`. Sign conventions MUST be stated (positive =
  buy, negative = sell) if the coordinator emits signed magnitudes.
- **Determinism markers**: if `stochastic-given-seed`, the coordinator
  MUST log the seed used per round.

##### Serialization Format

Broadcast payload MUST be a plain `dict` (no `<analysis>/<decision>`
tags — those bind participant agents, not the coordinator). The
canonical shape is:

```json
{
  "<state_var_1>": <float>,
  "<prev_state>":  <float>,
  "<fundamental>": <float>,
  "<deviation>":   <float>,
  "<volume>":      <float>,
  "round":         <int>
}
```

Every rule variant MUST emit the same dict shape. Model-driven variants
(LLM / RuleLLM / Rag) that ALSO instantiate a coordinator MUST emit
the identical dict shape — no LLM narration inside the broadcast.

##### Implementer Contract Reminder

**Implementers of this coordinator MUST re-open this §4.6.0 I/O
Contract during every coding pass** and use it as the single source of
truth for:

1. **Extras wiring** — every field declared in the Outputs table MUST
   trace back to a formula whose inputs are either (a) inbound orders
   or (b) `config.extras` keys declared in §4.7. No hidden constants.
2. **Broadcast emission** — the `perceive` / `decide` / `act` chain
   MUST populate every `Required? = yes` field and clamp
   out-of-range values before emission.
3. **`StandardMarketState.from_market_data()` compatibility** — the
   broadcast MUST satisfy the participant-side format contract; per
   the code-style rule recorded in memory, that helper MUST raise
   `KeyError` if a `Required? = yes` field is absent, so implementers
   MUST NOT silently omit fields.
4. **Variant parity** — every variant declared `Yes` in the target's
   §10.1 Variant Build Matrix MUST produce a broadcast with the SAME
   field set. To extend, edit this contract FIRST, then propagate.
5. **Contract-versus-prose conflict resolution** — if §4.6.2, §4.6.3,
   or §4.6.4 seems to contradict this contract, the contract wins.

#### 4.6.1 Input Aggregation Rules

How the coordinator turns a batch of inbound messages into aggregate
signals. Table + explicit "does NOT use" line.

```markdown
| Aggregate signal | Derivation                                  | Rationale                          |
|------------------|---------------------------------------------|------------------------------------|
| `buy_qty`        | `sum(o["quantity"] for o if action=="buy")` | Total buy pressure                 |
| `sell_qty`       | `sum(o["quantity"] for o if action=="sell")`| Total sell pressure                |
| `net_demand`     | `buy_qty - sell_qty`                        | Signed demand imbalance            |

Does NOT use: individual participant identities, participant capital
levels, bid_price fields (unless matching-engine variant), any private
state of participants.
```

**Completeness rule:** Every aggregate signal used in §4.6.2 MUST
appear here. Conversely, every signal declared here MUST be consumed
by at least one step in §4.6.2.

#### 4.6.2 Core Coordination Mechanism

Numbered 5–10 step description of the coordinator's per-round logic.
Plain English + formulas, NOT code in any specific language.

Same precision rules as `agent-design-skill.md` §3.6.2: two
independent implementers MUST produce behaviourally-equivalent logic;
each step MUST separate reads from writes; each step MUST trace to a
mechanism in §4.4 or be marked "implementation convenience".

Illustrative shape for a standard price-impact market:

```
1. READ: inbound_orders → buy_qty, sell_qty, net_demand (aggregates from §4.6.1).
2. READ: current price P(t), fundamental F, extras {λ, γ, σ}.
3. COMPUTE: ε ~ N(0, σ) — draw one noise realisation.
4. COMPUTE: P_raw = P(t) + λ·net_demand + γ·(F − P(t)) + ε.
5. COMPUTE: P(t+1) = max(P_raw, price_floor).
6. COMPUTE: deviation = (P(t+1) − F) / F.
7. COMPUTE: volume = min(buy_qty, sell_qty) + 0.5·|net_demand| (if declared).
8. WRITE: state["prev_price"] = P(t); state["price"] = P(t+1);
         state["deviation"] = deviation; state["price_history"].append(P(t+1)).
9. EMIT:  broadcast {price, prev_price, fundamental, deviation, volume, round}.
```

#### 4.6.3 Broadcast Space

The set of fields the coordinator may emit and the **structural
discipline** it self-imposes. Environment-level regulator caps or
matching-engine tick rules MUST NOT appear here — they belong in the
scenario/environment overlay.

Eight canonical dimensions (row order MUST be preserved):

```markdown
| Aspect                    | Specification                                                                     |
|---------------------------|-----------------------------------------------------------------------------------|
| Broadcast fields          | <enumerate every emitted field, matching §4.6.0 Outputs verbatim>                 |
| State transition rule     | <formula for state_var(t+1) as function of state(t) and aggregates>               |
| Price/state floor & ceiling | <e.g. `max(new_price, 0.01)`; or `"none"` with justification>                   |
| Freshness policy          | <every-tick / stale-if-no-orders>                                                 |
| Revision policy           | <can a broadcast be retracted or amended within a round? typically "no">          |
| State-history retention   | <e.g. hot buffer of last N ticks + cold spill to disk via HistoryBuffer>          |
| Resource cap              | <coordinator-side memory / state buffer cap; typically "unbounded, spilled">      |
| Termination rule          | <when the coordinator stops broadcasting: usually round == total_rounds>          |
```

Environment overlays (matching-engine tick grid, fee schedule,
latency model, circuit breakers, content-moderation rules) MUST NOT
appear here.

#### 4.6.4 Mathematical Model

Formalise the coordinator's decision logic in unambiguous mathematical
notation. The following content aspects MUST all be addressed:

1. **Broadcast output(s)** — what quantity/quantities the coordinator
   computes each round. Name every variable and its type/domain.
2. **State transition logic** — the complete mathematical mapping
   from (aggregates, state, extras) to broadcast. Precise enough that
   two independent implementers converge behaviourally.
3. **State variables** — every persisted internal variable, with type
   and initial value (usually seeded from `config.extras` on first
   call).
4. **State evolution ordering** — pre-broadcast / post-broadcast.
5. **Determinism contract** — deterministic / stochastic-given-seed /
   non-deterministic. Name distributions and seed sources.
6. **Parameter symbol table** — every symbol used anywhere in §4.6.
   No undeclared symbols. Same 4-column shape as
   `agent-design-skill.md` §3.6.4.

```markdown
| Symbol   | Meaning                     | Default Value  | Source                      |
|----------|-----------------------------|----------------|-----------------------------|
| `lambda` | price impact per unit demand| 0.01           | Kyle 1985; scenario extras  |
| `gamma`  | mean-reversion speed        | 0.01           | Brock & Hommes 1998         |
| `sigma`  | noise std dev               | 0.1            | Empirical calibration       |
```

#### 4.6.5 Coordination Properties

Four labelled lines:

- Time granularity: sub-second / tick / round-based / daily
- Feedback loop: negative / positive / mixed — with rationale
- Information environment: symmetric / asymmetric — what info the
  coordinator makes public
- Stochasticity profile: which sources of randomness the coordinator
  introduces (typically the noise term ε)

#### 4.6.6 Invariants and Failure Modes **(MANDATORY)**

This sub-section is the coordinator's **structural correctness
contract**. Every listed invariant MUST hold after every completed
round, and every listed failure mode MUST have an explicit,
documented behaviour (either "raise", "clamp with logged warning",
or "continue with degenerate broadcast + specified fields set to
sentinel").

Invariants are stronger than the sanity bounds of §4.9 (which are
diagnostic tests). Invariants are **contractual guarantees the
coordinator makes to participants** and to any downstream analysis
tool. Violation means the implementation is broken.

Round-boundary Invariants (MUST hold at the boundary between
round `t` and round `t+1`):

```markdown
| # | Invariant                                                       | Enforcement                          |
|---|-----------------------------------------------------------------|--------------------------------------|
| 1 | `broadcast[t+1].prev_<state> == broadcast[t].<state>`           | State-write ordering (§4.5 lifecycle) |
| 2 | Every `Required? = yes` field in §4.6.0 is present + non-null   | `decide` assertion                   |
| 3 | Every numeric broadcast field satisfies its §4.6.0 valid range  | Clamp before emission                |
| 4 | Broadcast `round` field increments by exactly 1 each cadence tick | Set from `observation.round`         |
| 5 | (If mechanism has floor/ceiling) State stays inside [floor, ceiling] | Clamp in step 5 of §4.6.2       |
| 6 | (If mechanism is deterministic-given-seed) Two runs with same seed and same inbound orders produce byte-equal broadcasts | Deterministic random draws only |
```

Domain-Specific Invariants (author MUST add if applicable, else
justify absence in one line):

- **Non-negativity**: `price >= 0`, `reserves >= 0`, `deposit_stock >= 0`
- **Probability domain**: `opinion_mean ∈ [-1, +1]` or `[0, 1]`
- **Conservation**: `sum(shares_held_by_participants) == float_supply`
  (only if the coordinator is authoritative for the ledger)
- **Monotonicity**: `cumulative_volume(t+1) >= cumulative_volume(t)`
- **Bounded velocity**: `|state(t+1) - state(t)| <= max_move` (circuit
  breaker — usually enforced by scenario, not coordinator)

Failure Modes (documented behaviour under each degenerate condition;
covers what §4.5 Missing-Input Policy left implicit):

```markdown
| Condition                                    | Coordinator behaviour                                       | Broadcast effect                              |
|----------------------------------------------|-------------------------------------------------------------|-----------------------------------------------|
| Zero inbound orders                          | Continue; aggregates = 0                                    | Broadcast produced with no-demand state move  |
| All inbound orders same sign (all buy)       | Continue                                                    | Broadcast reflects one-sided demand           |
| Aggregate `|net_demand|` > sensible cap      | Log warning; continue (do NOT auto-clamp aggregates)        | May trigger floor/ceiling clamp of state     |
| Individual order malformed / missing fields  | Skip that order; log; continue with remaining               | Aggregate excludes the bad order              |
| Required extras key missing                  | Raise `KeyError` from `perceive`                            | No broadcast that round; simulation halts     |
| Optional extras key missing                  | Use documented default                                      | Normal broadcast                              |
| State transition produces NaN / Inf          | Raise `ValueError` from `perceive`; do NOT emit a broadcast | Simulation halts (implementation defect)      |
| Broadcast field fails §4.6.0 range check     | Clamp to nearest valid value; log warning                   | Normal broadcast with clamped value           |
| Scenario driver mutates extras mid-round     | Read new value on next `perceive`; log the change           | Next broadcast reflects the new parameter     |
```

Every row in Failure Modes MUST be replayable — i.e. running the
same seed with the same inbound sequence MUST reproduce the same
failure classification.

### 4.7 Environmental Parameters **(MANDATORY)**

Engine-agnostic parameter table(s) with the canonical **eight columns**
(same schema as `agent-design-skill.md` §3.7):

Parameter · Type · Default · Valid Range · Sensitivity · Description ·
Impact · Source.

Every parameter listed here MUST also appear as a required (or
explicitly optional) key in the `extras:` block of the coordinator's
line in `players.yml`. Every mechanism / structural parameter MUST
appear in at least one formula in §4.6.4 (no orphans). High-sensitivity
mechanism parameters MUST cite empirical data (Type 1–3 evidence),
not "Standardised" or "author estimate".

If the coordinator exposes zero tunable parameters, write
`_No tunable parameters._` with a justification sentence — but this
is extremely rare (even a pure-random-walk coordinator has σ).

#### 4.7.1 Parameter Categorisation **(MANDATORY)**

Coordinator parameters MUST be grouped into the four categories
below. Each category is a separate sub-table. Empty categories are
allowed (write `_None._`) but the category headers MUST all appear.

**Category A — Initial Conditions.** Seed values written to
`custom_state` on the first call. These affect the trajectory but
have no ongoing effect once the coordinator is running.

- Examples: `initial_price`, `initial_reserves`, `initial_opinion_mean`.
- Sensitivity is measured as the effect of a ±10% change in the
  initial value on the state trajectory averaged over the first
  `min(20, total_rounds)` rounds.

**Category B — Mechanism Coefficients.** Parameters that appear
literally inside the transition equations of §4.6.4.

- Examples: `price_impact` (λ), `mean_reversion` (γ), `noise_std` (σ),
  `opinion_inertia`, `propagation_probability`.
- Every Category B parameter MUST appear in ≥ 1 §4.6.4 formula.
- High-sensitivity Category B parameters MUST cite empirical data
  (Type 1–3 evidence).

**Category C — Structural / Boundary Parameters.** Parameters that
define state-space boundaries, clamps, floors, ceilings, or cadence
tuning that are structural rather than mechanistic.

- Examples: `price_floor`, `price_ceiling`, `broadcast_every_n_rounds`,
  `warmup_rounds`, `max_history_lookback`.
- These MAY use `Standardised` as Source when they encode a project
  convention.

**Category D — Recording / Infrastructure Parameters.** Parameters
that affect logging, persistence, and replay but MUST NOT affect the
broadcast trajectory.

- Examples: `record_path`, `custom_state_hot_limit`, `log_level`.
- Category D parameters MUST have Sensitivity = `low` on the
  broadcast trajectory (i.e. changing them does not change the
  numerical output of the simulation, only its on-disk footprint or
  observability).
- If a "recording" parameter is discovered to affect the trajectory,
  it MUST be reclassified into Category A, B, or C.

Each sub-table uses the same 8-column schema. Example skeleton:

```markdown
##### A. Initial Conditions

| Parameter          | Type    | Default | Valid Range | Sensitivity | Description                | Impact                              | Source          |
|--------------------|---------|---------|-------------|-------------|----------------------------|-------------------------------------|-----------------|
| `initial_price`    | float   | 100.0   | > 0         | medium      | Round-0 price seed         | Higher -> higher initial trajectory | Scenario config |

##### B. Mechanism Coefficients

| Parameter        | Type  | Default | Valid Range | Sensitivity | Description                     | Impact                                          | Source                  |
|------------------|-------|---------|-------------|-------------|---------------------------------|-------------------------------------------------|-------------------------|
| `price_impact`   | float | 0.01    | ≥ 0         | high        | λ in P(t+1) = P(t) + λ·NetD + …  | Higher -> price more responsive to demand       | Kyle 1985; Table 3      |
| `mean_reversion` | float | 0.01    | [0, 1]      | high        | γ pulling price toward F        | Higher -> faster return to fundamental          | Brock & Hommes 1998 §4  |
| `noise_std`      | float | 0.1     | ≥ 0         | medium      | σ of ε ~ N(0, σ²) added per tick | Higher -> more idiosyncratic price oscillation | Empirical calibration   |

##### C. Structural / Boundary Parameters

| Parameter     | Type  | Default | Valid Range | Sensitivity | Description                        | Impact                                        | Source        |
|---------------|-------|---------|-------------|-------------|------------------------------------|-----------------------------------------------|---------------|
| `price_floor` | float | 0.01    | ≥ 0         | low         | Absolute lower clamp on price      | Higher -> earlier clamp during collapse       | Standardised  |

##### D. Recording / Infrastructure Parameters

| Parameter                 | Type | Default | Valid Range | Sensitivity | Description                             | Impact                              | Source        |
|---------------------------|------|---------|-------------|-------------|-----------------------------------------|-------------------------------------|---------------|
| `record_path`             | str  | ""      | non-empty   | low         | Root directory for HistoryBuffer spills | Higher size -> more disk usage      | Standardised  |
| `custom_state_hot_limit`  | int  | 10000   | ≥ 1         | low         | HistoryBuffer hot-tier size             | Higher -> more RAM, less disk I/O   | Standardised  |
```

### 4.8 Worked Numerical Examples

At least three worked cases plus one edge case. Same shape as
`agent-design-skill.md` §3.8: real numeric state → step-by-step
calculation → broadcast → state update. Numeric values MUST be drawn
from §4.7 Defaults. The three primary cases MUST collectively cover
ALL non-trivial branches of the transition logic (e.g. net_demand > 0,
net_demand < 0, net_demand ≈ 0). The edge case MUST demonstrate one
of: cold-start (round 0), missing-order fallback, price-floor clamp,
extreme-shock behaviour.

### 4.9 Coordinator Verification and Calibration

How a researcher will know the coordinator is correctly implemented
and well-calibrated. Concerns the coordinator as an environment
mechanism — NOT emergent scenario-level outcomes (those belong to the
scenario spec).

```markdown
**Calibration data sources** (per parameter):
- `<param>` ← <citation, table, specific value or range>

**Expected coordinator behaviour** (what the coordinator MUST do
when correctly implemented):
- Given `net_demand > 0` and stable fundamental, MUST push price up
- Given `net_demand < 0` and stable fundamental, MUST push price down
- Given `net_demand == 0`, MUST reduce |price − fundamental| by γ

**Sanity bounds (red flags indicating broken implementation)**:
- IF price falls below the declared floor THEN clamp is broken
- IF broadcast omits any Required? = yes field THEN contract is broken
- IF net_demand > 0 yet price falls (in absence of large mean-reversion
  or noise draw dominating) THEN sign convention is broken
```

#### 4.9.1 Ablation Hooks

```markdown
| Ablation name         | Setting            | Hypothesis tested                                | Expected direction | Metric                       |
|-----------------------|--------------------|--------------------------------------------------|--------------------|------------------------------|
| `no-mean-reversion`   | `gamma = 0`        | Removes fundamental anchor                       | more path-dependent | var(price) over N rounds     |
| `high-noise`          | `sigma *= 10`      | Overwhelms deterministic signal                  | random-walk-like    | ACF(price) → 0               |
| `zero-price-impact`   | `lambda = 0`       | Orders no longer move the price                  | price = fundamental | mean |price − fundamental|   |
```

### 4.10 Academic / Empirical References

Numbered table identical in shape to `agent-design-skill.md` §3.10.
Every citation anywhere in the profile MUST appear here.

### 4.11 Design Provenance and Versioning

Footer block. **MANDATORY**. MUST include a `Market Type` row and an
`Icon` row (both are unique to this handbook).

```markdown
| Field       | Content                                                          |
|-------------|------------------------------------------------------------------|
| Market Type | <canonical slug + English label — MUST match §4.2 Summary row 1> |
| Author      | <name or handle>                                                 |
| Reviewed by | <name or handle> (optional)                                      |
| Created     | <YYYY-MM-DD>                                                     |
| Version     | <semver, e.g. 1.0.0>                                             |
| Status      | <draft / experimental / canonical / deprecated>                  |
| Icon        | `![](../agent_images/icons/market/{market-type}-{stem}.png)`     |
```

Version history is tracked externally (in the pipeline build log). No
`Change log` row is stored inside the profile.

## 5. Evidence Provenance Requirement

Same 6-category taxonomy and same coverage rules as
`agent-design-skill.md` §4:

- ≥80% of substantive design choices cite Type 1–4 evidence.
- Type 6 (expert judgment) ≤ 20% of total evidence; every Type 6
  citation MUST be marked with ⚠️.
- High-sensitivity parameters MUST NOT use Type 6.

Every mechanism step, aggregate rule, transition equation, and
parameter default MUST have an inline evidence tag pointing to a row
in the §4.10 References table.

## 6. Cross-Section Consistency Rules

A conformant profile MUST satisfy ALL of the following:

- Every **parameter** in §4.7 MUST appear in at least one formula in
  §4.6.4 Mathematical Model — EXCEPT Category D (recording /
  infrastructure) parameters, which are exempt because they must not
  influence the trajectory.
- Every **aggregate signal** in §4.6.1 MUST be consumed by at least
  one step in §4.6.2 Core Coordination Mechanism.
- Every **inbound message field** declared in §4.5 MUST be read by an
  aggregation rule in §4.6.1.
- Every **broadcast field** in §4.6.0 Outputs MUST be produced by a
  step in §4.6.2 and MUST also appear in the §4.6.3 Broadcast Space
  row `Broadcast fields`.
- Every **State Initialization** extras key in §4.5 MUST appear in
  §4.7 (usually Category A or C) with a matching default.
- Every **Lifecycle Mapping** step in §4.5 MUST have a corresponding
  read/compute/write in §4.6.2 (no lifecycle step that touches state
  outside the mechanism definition).
- Every **round-boundary invariant** in §4.6.6 MUST be enforced by an
  explicit step in §4.6.2 (invariant #1 by state-write ordering,
  invariant #3 by clamp step, etc.).
- Every **failure-mode row** in §4.6.6 MUST be consistent with §4.5
  Missing-Input Policy (no contradiction between the two).
- Every **worked example** in §4.8 MUST use Default values from §4.7.
- Every **expected behaviour** in §4.9 MUST be traceable to §4.6.2.
- Every **citation** anywhere in the profile MUST appear in §4.10.
- Every **symbol** used in §4.6 MUST be declared in §4.6.4 Parameter
  symbol table.
- The **Market Type** slug in §4.2 Summary row 1 MUST match the
  `Market Type` row in §4.11 Design Provenance AND MUST match the
  file-name prefix on disk.
- The **Icon** row in §4.11 MUST point to
  `../agent_images/icons/market/{market-type}-{stem}.png` — see the
  sibling handbook `market-icon-generation-skill.md`.

**Scenario binding (`archetype:` field, expanded in §8):**

- Every shipped scenario under `configs/` (excluding
  `CUSTOMIZED_SIMULATION/`, `TEMPLATES/`, `Demo/`) MUST declare
  `archetype: {stem}` as the first child of its coordinator top-level
  YAML key in every variant's `players.yml`. `_ARCHETYPE_FALLBACK`
  in `config_loader.py` SHOULD be empty in a fully-migrated repo
  (kept only as a safety net for un-materialised customized copies).
- The `archetype:` value MUST exactly match a file stem in
  `masim/agents/defines/market/` — see §8.2 for the canonical set.
- The `Scenario Portability` row in every archetype profile (§4.2)
  MUST enumerate all scenarios whose `players.yml → archetype:`
  binds to that profile, with **Full ✅** or **Approximated ⚠**
  markers per the legend in §8.5.

## 7. Validation Checklist (Self-Check)

**Structural completeness:**

- [ ] File name is `masim/agents/defines/market/{market-type}-{stem}.md`
      and `{market-type}` is a canonical slug from §2.1
- [ ] H1 is a sentence-cased role phrase, not a class identifier
- [ ] §4.2 Summary has ≥8 rows in order, with `Market Type` as row 1
- [ ] §4.3 Definition covers (a) what the coordinator models with a
      cited real-world counterpart, (b) coordination goal, (c) role +
      ≥2 explicit non-goals
- [ ] §4.4 Foundation has ≥1 sub-block with all 9 labelled lines
- [ ] §4.5 declares Lifecycle Mapping (perceive/decide/act phases),
      State Initialization (extras keys + writes + warm-up rounds),
      Coordination Cadence, Inbound Message Types (with fields),
      Broadcast Trigger, Missing-Input Policy, Exogenous Driver
      Boundary, and Environmental Dependencies
- [ ] §4.6 has all SEVEN H4 sub-blocks (I/O Contract, Input
      Aggregation, Coordination Mechanism, Broadcast Space,
      Mathematical Model, Coordination Properties, Invariants and
      Failure Modes)
- [ ] §4.6.0 I/O Contract fills all five required blocks
- [ ] §4.6.0 Outputs table names every broadcast field with Type,
      Valid Range, Unit, Required flag, Meaning
- [ ] §4.6.0 Serialization Format is a plain-dict schema, NOT
      `<analysis>/<decision>` tags (those bind participants only)
- [ ] §4.6.6 Round-boundary Invariants covers time-consistency
      (`prev == previous state`), required-field presence, valid-range
      clamps, `round` monotonicity, and (if deterministic-given-seed)
      replay determinism
- [ ] §4.6.6 Failure Modes covers zero-order, malformed-order,
      missing-extras, NaN-transition, and range-violation cases with
      explicit behaviours

**Depth and precision:**

- [ ] §4.4 every "Mathematical Formulation" is a single implementable
      equation; every "Empirical Evidence" cites an effect size; every
      "Calibration Source" provides a numeric range
- [ ] §4.6.2 has 5–10 steps; each step separates reads from writes;
      every step traces to §4.4 or is marked "implementation convenience"
- [ ] §4.6.3 Broadcast Space visibly covers all eight canonical
      dimensions
- [ ] §4.6.4 formalisation covers every branch of the transition
      logic and every activation trigger from §4.5
- [ ] §4.7 has ≥3 parameter rows (or justified fewer); every
      high-sensitivity mechanism parameter cites empirical data
- [ ] §4.7.1 groups parameters into A/B/C/D categories with the
      category headers present even when empty; Category D has all
      rows at Sensitivity = low
- [ ] §4.8 uses §4.7 Defaults; covers positive/negative/zero net-demand
      branches; edge case demonstrates cold-start / floor / shock

**Cross-section consistency (§6 rules):**

- [ ] Every §4.7 parameter appears in §4.6.4 (except Category D)
- [ ] Every §4.5 State Initialization extras key appears in §4.7
- [ ] Every §4.6.1 aggregate is consumed in §4.6.2
- [ ] Every §4.6.0 broadcast field appears in §4.6.3 row 1
- [ ] Every §4.6.6 round-boundary invariant is enforced by a specific
      §4.6.2 step
- [ ] §4.5 Missing-Input Policy is consistent with §4.6.6 Failure Modes
- [ ] Every §4.8 example uses §4.7 defaults
- [ ] Every §4.9 expected behaviour traces to §4.6.2
- [ ] Every citation appears in §4.10
- [ ] No undeclared symbols in §4.6
- [ ] Market Type slug is consistent across file name, §4.2 row 1,
      §4.11 Market Type row, and Icon path

**Evidence provenance (§5 rules):**

- [ ] ≥80% of substantive choices cite Type 1–4 evidence
- [ ] Type 6 ≤ 20% and each is marked ⚠️
- [ ] High-sensitivity parameters do not use Type 6

**Icon linkage (§4.11 row `Icon`):**

- [ ] `Icon` row present in §4.11 Design Provenance
- [ ] Icon path is exactly `../agent_images/icons/market/{market-type}-{stem}.png`
- [ ] PNG file exists on disk (or the icon-generation skill has been
      queued as a follow-up task)
- [ ] `masim/agents/defines/agent_images/design.md` has a mapping row
      for `market/{market-type}-{stem}.md` → `market/{market-type}-{stem}.png`

## 8. Scenario Binding — the `archetype:` field **(MANDATORY)**

Scenarios reference market coordinator profiles the same way they
reference participant profiles: through an explicit `archetype:` key
inside the coordinator's YAML block in
`configs/{scenario}/{variant}/players.yml`. This binding is what
lets the runtime, the UI sidebar, the topology preview, the market
profile dialog, and the analysis modules all agree on **which of the
nine canonical market coordinators governs this scenario**.

### 8.1 Where the field lives

The `archetype:` key is a direct child of the **coordinator's
top-level YAML key** in `players.yml`. Three coordinator key
patterns exist in the codebase — the field is placed identically
in all three:

```yaml
# Pattern 1 — standard scenarios (single canonical coordinator key)
market:
  archetype: stock-standard-price-impact  # -> masim/agents/defines/market/stock-standard-price-impact.md
  scale: ...
  price_impact: ...

# Pattern 2 — opinion-domain scenarios (EchoChamber family)
# Coordinator key follows the pattern `{variant}_opinion_environment:`
# where {variant} is one of: rule, llm, ragllm, rulellm. The four
# variants exist because participant reasoning depth changes per
# variant, but the archetype binding is identical in every variant.
rule_opinion_environment:      # (or llm_opinion_environment:, etc.)
  archetype: opinion-echo-chamber-clustering  # -> masim/agents/defines/market/opinion-echo-chamber-clustering.md
  ...

# Pattern 3 — information-domain scenarios (RumorSpread family)
# Same variant convention: `{variant}_information_environment:`.
rule_information_environment:  # (or llm_information_environment:, etc.)
  archetype: information-sis-contagion  # -> masim/agents/defines/market/information-sis-contagion.md
  ...
```

Note on variant-prefixed keys: the loader recognises any top-level
key that literally equals `market:` OR ends in `_opinion_environment`
OR `_information_environment`. This lets participant-variant
scaffolding evolve without requiring changes to the archetype
binding contract. See `_find_coordinator_block()` in
`config_loader.py`.

The trailing comment `# -> masim/agents/defines/market/{stem}.md` is
**recommended, not required**; the loader ignores it. It exists so
that a reader scanning `players.yml` can jump to the profile
without opening the config loader.

### 8.2 Field format rules

- **Value type**: string, MUST equal the archetype file stem — the
  file name at `masim/agents/defines/market/{value}.md` without the
  `.md` extension.
- **Canonical set** (9 archetypes as of 2026-07-17):
  `stock-standard-price-impact`,
  `opinion-echo-chamber-clustering`,
  `information-sis-contagion`,
  `fx-currency-peg-and-attack`,
  `bond-yield-spread-inverse`,
  `crypto-algostable-depeg`,
  `derivatives-vol-feedback`,
  `deposit-bank-run-diamond-dybvig`,
  `credit-minsky-cycle`.
- **No inline overrides**: if a scenario needs a different
  mechanism, add a **new** archetype profile — do not fork the
  field into `archetype-plus-patch` style.
- **One archetype per coordinator**: multi-coordinator scenarios
  (each of which has its own top-level YAML key) declare the field
  once per coordinator block. Standard scenarios have exactly one
  coordinator, so exactly one `archetype:` key.

### 8.3 Resolution semantics (implemented in `masim/interface/config_loader.py`)

The runtime resolves an archetype in three tiers, in order:

1. **Explicit** — parse `players.yml` for the scenario's default
   variant, locate the coordinator block, read `archetype:`. This is
   the authoritative source.
2. **Fallback table** — if the `players.yml` is missing the field
   (legacy scenarios, config still being migrated), the
   `_ARCHETYPE_FALLBACK` dict in `config_loader.py` maps the
   scenario key to the intended archetype. This is a
   migration/bridge mechanism and SHOULD be empty in a fully
   migrated repo.
3. **Default** — if neither the field nor the fallback table
   resolves, return `stock-standard-price-impact`. This preserves
   backward compatibility with older workflows.

The exposed loader functions are:

- `get_market_archetype(scenario_name) -> Optional[str]` — returns
  the resolved stem, or `None` if the scenario itself does not
  exist.
- `get_market_icon_path(scenario_name) -> Optional[Path]` — returns
  the absolute path to the icon PNG (or `None` if the PNG has not
  yet been generated).
- `get_market_type(scenario_name) -> str` — returns the
  human-readable label ("Stock Market", "FX Market", "Bond
  Market", "Crypto Market", "Derivatives Market", "Deposit Market",
  "Credit Market", "Opinion Field", "Information Field") derived
  from the archetype stem via `_ARCHETYPE_MARKET_TYPE`.

### 8.4 UI consumption

- **`masim/interface/components/sidebar.py`** — topology preview
  renders the archetype icon as the hub node (falls back to a gold
  FancyBboxPatch if the PNG is absent).
- **`masim/interface/components/agent_market.py`** — the "View the
  market coordinator archetype" button opens
  `_show_market_archetype_dialog()`, which renders
  `masim/agents/defines/market/{stem}.md` in a Streamlit dialog, with the
  icon as header, mirroring the "View the scenario definition"
  drill-through for player agents.

### 8.5 Full vs Approximated status

The archetype binding declares **intended mechanism**, not
current code fidelity. Every archetype profile MUST include a
`Scenario Portability` row that lists bound scenarios and marks
each one as:

- **Full ✅** — coordinator code implements the archetype's
  mechanism signature verbatim (aggregate rules, transition
  equations, invariants).
- **Approximated ⚠** — archetype bound for icon/UI/narrative
  purposes, but the coordinator code currently uses the
  standard price-impact formula.

The profile MUST also include a `Scenario Status` row that
explains this legend inline. This keeps academic honesty
(readers see exactly what is implemented today) while
preserving the design target for future upgrades.

### 8.6 Manual migration recipe

For each variant `players.yml` under `configs/`:

1. Detect the coordinator top-level key (matches
   `^market:`, `^\w+_opinion_environment:`,
   `^\w+_information_environment:`).
2. Look up the scenario stem → archetype stem in the mapping
   table maintained in `market-icon-generation-skill.md`.
3. Add `archetype: {stem}  # -> masim/agents/defines/market/{stem}.md`
   as the first child of the coordinator block, updating in
   place if the field already exists.

### 8.7 Cross-section consistency

Add these rules to §6:

- Every scenario in `examples/` MUST have `archetype:` set in every
  variant's `players.yml`; the `_ARCHETYPE_FALLBACK` table SHOULD
  be empty in a fully-migrated repo.
- The `archetype:` value MUST exactly match a file stem in
  `masim/agents/defines/market/`.
- The `Scenario Portability` row in every archetype profile MUST
  enumerate all scenarios whose `players.yml → archetype:` binds
  to that profile, with Full/Approximated markers.

### 8.8 Related handbooks

- `market-icon-generation-skill.md` — describes how the PNG
  referenced by `get_market_icon_path()` is generated and where it
  lives (`agent_images/icons/market/{stem}.png`).
- `agent-design-skill.md` — the participant-side analogue; the
  `class:` field in a player block plays the same role as
  `archetype:` in a coordinator block.

## 9. Status

| Field   | Content                                                    |
|---------|------------------------------------------------------------|
| Version | 1.2.0                                                      |
| Created | 2026-07-16 (v1.0.0); revised 2026-07-16 (v1.1.0 — added Lifecycle Mapping, State Initialization contract, §4.6.6 Invariants & Failure Modes, §4.7.1 parameter categorisation, Regime-dependent Feedback Direction, Exogenous Driver Boundary); revised 2026-07-17 (v1.2.0 — added §8 Scenario Binding: `archetype:` field convention, resolution semantics, UI consumption, Full/Approximated status, injection workflow) |
| Status  | canonical                                                  |
| Domains | All simulation domains that expose an environment-side player |
| Sibling | `agent-design-skill.md` (participant-agent handbook); `market-icon-generation-skill.md` (icon handbook) |
