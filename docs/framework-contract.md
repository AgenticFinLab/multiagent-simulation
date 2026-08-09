# MASim Framework Contract — `decide → act → on_fill`

> Authoritative reference for the single-chokepoint execution contract that
> `masim.agents._base.CanonicalRulePlayer`, `CanonicalLLMPlayer`,
> `CanonicalRagPlayer` and `CanonicalMarketCoordinator` enforce.
>
> **Scope**: everything under `examples/{Scenario}/{Rule,LLM,RuleLLM,Rag}/players.py`,
> `masim/agents/`, `masim/format/finalize.py`. Legacy `GeneralPlayer` scenarios
> pre-date this contract; they are catalogued as `LEGACY-BASE` by
> `scripts/audit_scenario_contract.py` and covered by the migration guide
> in §7.
>
> **Reference scenario**: `examples/AnchoringEffect/` — all four variants
> pass the contract audit clean. See its `simulation-bases.md §7.1` for
> the same rules expressed at scenario-design level.

## 1. Executive Summary

Every canonical agent runs the same four-stage lifecycle in every round:

```
Coordinator broadcast state
        │
        ▼
  perceive(observation)          ← subclass hook: on_market_data
        │
        ▼
  decide()                       ← subclass hook: decide_order (Rule)
        │                          / prompt + parse (LLM/Rag)
        │
        ▼
  act(decision_payload)          ← framework-owned; DO NOT override
   ├─ require key presence
   ├─ require_positive_bid_price
   ├─ atomic cash / position mutation
   ├─ on_fill(action, quantity, bid_price)   ← subclass hook
   └─ emit Action(action_type="investor_bid", payload=…)
        │
        ▼
Coordinator collects, prices, next round
```

Subclasses **may** override `perceive` (for observation processing),
`on_market_data`, `decide_order`, `on_fill`, `init_extras`, and the
LLM prompt / parser layer. Subclasses **must not** override `act` or
`decide` on any canonical base. This single rule collapses three
classes of anti-pattern into one enforceable boundary:

* Silent-fill of `bid_price` from `market_data["price"]` (wire-format
  contract violation).
* Double-mutation of `cash` / `position` (scenario decrements once,
  framework decrements again).
* Non-atomic anchor updates (VWAP written before the base call
  rejects the order, leaving the anchor corrupted).

Because `act` never exposes the raw `decision_payload` dict to
subclasses, these bugs stop being "code review will catch it" and
become "the API does not let you write it."

## 2. The Canonical Base Classes

| Base | File | Purpose | Subclass hooks |
|---|---|---|---|
| `CanonicalRulePlayer` | `masim/agents/_base.py:353` | Deterministic, formula-driven agents | `init_extras`, `on_market_data`, `decide_order`, `on_fill` |
| `CanonicalLLMPlayer` | `masim/agents/_base.py:589` | LLM-driven agents (prompt → decision) | `init_extras`, `on_market_data`, `_build_user_prompt`, `_parse_response`, `on_fill` |
| `CanonicalRagPlayer` | `masim/agents/_rag_base.py:64` | LLM + retrieval augmentation; inherits from `CanonicalLLMPlayer` | Same as `CanonicalLLMPlayer` plus retrieval overrides |
| `CanonicalMarketCoordinator` | `masim/agents/_coordinator_base.py:56` | Market / environment coordinator | Domain-specific price / aggregation formula overrides |

All four inherit from `masim.player.general.GeneralPlayer`, so they plug
into `GeneralSimulator` and `PlayerPersona` without any wrapper. Legacy
scenarios that still inherit `GeneralPlayer` directly bypass the
contract entirely; §7 documents the migration.

## 3. The Framework `act()` — What It Guarantees

The shared implementation lives at
`masim/agents/_base.py :: _apply_fill_and_emit_action` and is called by
both `CanonicalRulePlayer.act` and `CanonicalLLMPlayer.act`. Its
guarantees, in execution order:

1. **Key-presence check.** `action`, `quantity`, `bid_price` must be
   in `decision_payload`. Missing → `KeyError` with the exact payload
   keys observed. No silent defaults.
2. **`require_positive_bid_price`** — for `action in {"buy", "sell"}`
   and `quantity > 0`, `bid_price` must be strictly positive and
   finite. Violation → `ValueError` from
   `masim.format.finalize.require_positive_bid_price` with a stable
   error prefix identifying the class that called it.
3. **Atomic cash / position mutation** — exactly one arithmetic
   update per fill:

   ```
   BUY  → cash -= quantity * bid_price ; position += quantity
   SELL → cash += quantity * bid_price ; position -= quantity
   HOLD → no state change
   ```

4. **`on_fill(action, quantity, bid_price)`** — invoked with the
   three validated primitives (see §4).
5. **Emit `Action`** — `Action(action_type="investor_bid",
   payload=decision_payload, source_id=agent.identity)`.

If any step (1) or (2) raises, steps (3)–(5) do not run. This is the
atomic-state guarantee: a rejected record leaves `cash`, `position`,
and every anchor variable untouched. Callers **should not** wrap
`act()` in `try / except` to "recover" from a validation failure —
the failure signals that the upstream `decide` / prompt / parser
produced a malformed record, and swallowing it hides a bug that will
otherwise manifest downstream as silently corrupted state.

## 4. The `on_fill` Extension Point

Signature (identical on `CanonicalRulePlayer` and `CanonicalLLMPlayer`,
inherited by `CanonicalRagPlayer`):

```python
def on_fill(self, action: str, quantity: float, bid_price: float) -> None:
    """Post-fill hook. Default: no-op."""
```

Contract:

| Property | Guarantee |
|---|---|
| Invocation timing | After (1)–(3) above, before (5). |
| `action` | One of `"buy"`, `"sell"`, `"hold"` — exactly the string that appeared in `decision_payload["action"]`. |
| `quantity` | `float(decision_payload["quantity"])`. Guaranteed `≥ 0` by the wire-format contract (`InvestorOrder.from_dict`), but `quantity == 0` is possible for degenerate orders — filter it in the hook if needed. |
| `bid_price` | `float(decision_payload["bid_price"])`. For `action in {"buy", "sell"}` with `quantity > 0`, guaranteed `> 0` and finite. For `action == "hold"`, may be any value including zero. |
| `self.state.custom_state["cash"]` | Already reflects this fill. |
| `self.state.custom_state["position"]` | Already reflects this fill. |
| Failure isolation | If validation raised, `on_fill` was not called. Any state you touch inside `on_fill` is updated only on success. |
| Return value | Ignored. Use `None`. |

Reconstructing pre-fill position when you need it (typical for VWAP):

```python
def on_fill(self, action, quantity, bid_price):
    if action != "buy" or quantity <= 0:
        return
    new_pos = float(self.state.custom_state["position"])
    old_pos = new_pos - quantity                              # pre-fill
    old_anchor = float(self.state.custom_state.get("cost_basis") or bid_price)
    self.state.custom_state["cost_basis"] = (
        old_anchor * old_pos + bid_price * quantity
    ) / new_pos
```

The five canonical archetypes that use `on_fill` today —
`disposition-trader`, `disposition-investor`, `endowed-holder`,
`institutional-investor`, `long-term-investor` — live in
`masim/agents/{disposition_trader,disposition_investor,endowed_holder,institutional_investor,long_term_investor}.py`
and are the reference implementations.

`long-term-investor` is the atypical case: it maintains its own
denominator (`acquired_units`) independent of `position` because
DCA aggregates a specific "acquisition" sub-history separate from the
current inventory. When you write a new archetype, decide up front
whether the anchor's denominator is `position` (recover pre-fill via
`new_pos - quantity`) or a private accumulator; the two patterns are
not interchangeable.

## 5. What the Framework Does *Not* Do

`_apply_fill_and_emit_action` deliberately stops short of the
following. If any of these responsibilities matter for your archetype,
they belong in `decide_order` / `on_fill` / `perceive`, not in a
shadow `act`:

* **Rejecting orders on cash / inventory constraints.** The
  finance-appendix reference (`AssetBubble`) clips oversize orders in
  `decide_order` (Rule) or in the prompt (LLM/Rag) via
  `masim.format.finalize.clip_order_to_liquidity`. `act` will happily
  execute a fill that drives cash negative — because it treats the
  incoming `decision_payload` as an authoritative post-clip record.
* **Fee / commission / slippage.** Not in the base. If your scenario
  models them, apply them inside `decide_order` before the payload
  leaves the subclass, so `bid_price` on the wire is already the
  effective execution price.
* **Order matching or book aggregation.** That is
  `CanonicalMarketCoordinator`'s job in its `perceive`/`decide`
  cycle, not the investor `act`'s.
* **Anchor initialisation.** Seed anchors in `on_market_data` or
  `init_extras`, not in `on_fill` (which only fires on actual fills,
  never on the first round).

## 6. Prohibited Overrides — Design-Level Anti-Patterns

The audit script `scripts/audit_scenario_contract.py` flags all of
these; each is described here so authors know why they exist.

### 6.1 `act` override on a canonical subclass — `STRUCT-ACT`

```python
# FORBIDDEN
class MyTrader(CanonicalRulePlayer):
    async def act(self, decision_payload):
        if decision_payload.get("bid_price", 0) <= 0:
            decision_payload["bid_price"] = self.state.custom_state["market_data"]["price"]
        return await super().act(decision_payload)
```

The pattern reintroduces the exact silent-fill bug
`require_positive_bid_price` exists to eliminate: by the time
`super().act(...)` runs, `bid_price > 0` holds, but the value in it
was fabricated from `market_data`, not from the decision that
produced the order. Downstream state (`cost_basis`, `avg_entry_price`,
volume-weighted anchors, PnL) is corrupted, and no error is raised.

The fix is unconditional: **remove the override**. If the LLM /
prompt / rule sometimes produces a zero `bid_price`, that is an
upstream bug in the finaliser or the LLM schema validator, not
something the archetype should paper over.

### 6.2 `decide` override on a canonical subclass — `STRUCT-DECIDE`

```python
# FORBIDDEN
class MyTrader(CanonicalRulePlayer):
    async def decide(self):
        market = self.state.custom_state["market_data"]
        return {"action": "buy", "quantity": 10, "bid_price": market["price"]}
```

Canonical `decide` on `CanonicalRulePlayer` and `CanonicalLLMPlayer`
routes through `masim.format.finalize.finalize_rule_order` /
`finalize_llm_order`, which apply category-aware wire-format
validation. A raw dict returned from a subclass `decide` bypasses that
finaliser entirely and produces a payload that only accidentally
satisfies `_apply_fill_and_emit_action`'s guards.

The fix is to move the decision logic into `decide_order(state)
-> InvestorOrder` (Rule) or into `_build_user_prompt` +
`_parse_response` (LLM / Rag). Both routes go through the finaliser
by construction.

### 6.3 Cash / position mutation inside `decide` or `act` — `SEM-CASH-MUT`

```python
# FORBIDDEN inside decide()/act()
self.state.custom_state["cash"] -= quantity * bid_price
self.state.custom_state["position"] += quantity
```

The framework mutates `cash` and `position` exactly once per fill,
inside `_apply_fill_and_emit_action`. A duplicate mutation in
`decide` or `act` **double-counts every fill**, corrupts every metric
that reads `cash` / `position`, and typically diverges from the
framework's arithmetic (e.g., using `market_data["price"]` where the
framework uses `bid_price`).

Legitimate cash-mutation sites are `__init__`, `init_extras`,
`_initialize_state`, `_seed_state`, and `on_fill` — anywhere else
raises the audit flag.

### 6.4 Silent-fill fallback assignment — `SEM-SILENT-FILL`

```python
# FORBIDDEN
bid_price = market_data["price"]
bid_price = self.state.custom_state["purchase_price"]
bid_price = price if quantity != 0 else 0.0
```

Any assignment to `bid_price` from a non-literal source that is not
the decision itself is a silent-fill. The audit script filters out
the legitimate defensive form (`max_affordable = cash / bid_price if
bid_price > 0 else 0`) — that is arithmetic guard, not a fallback
bid_price.

## 7. Legacy `GeneralPlayer` Scenarios — Migration Guide

Approximately 176 `players.py` files across the corpus still inherit
directly from `masim.player.general.GeneralPlayer`. The audit script
labels these `LEGACY-BASE` and does not run the `STRUCT-ACT` /
`STRUCT-DECIDE` structural checks on them, since they never signed
the canonical contract. However, the `SEM-CASH-MUT` and
`SEM-SILENT-FILL` checks still fire — legacy scenarios exhibit the
anti-patterns in full force (typically ~491 HIGH `SEM-CASH-MUT`
findings in `decide` / `act` blocks, plus ~61 `SEM-SILENT-FILL`
occurrences).

Migration recipe (per player class):

1. Change base class: `class Foo(GeneralPlayer)` →
   `class Foo(CanonicalRulePlayer)` (or `CanonicalLLMPlayer` /
   `CanonicalRagPlayer`).
2. Delete `perceive` if it only does state-init + market_data
   extraction; move state-init to `init_extras`, keep `on_market_data`
   for per-round observation processing.
3. Replace `decide` returning a raw dict with `decide_order(state)
   -> InvestorOrder`.
4. **Delete** the local `act` override. Move any post-fill state
   updates (VWAP anchors, counters) into `on_fill(action, quantity,
   bid_price)`.
5. Remove every `self.state.custom_state["cash"] ±= ...` and
   `self.state.custom_state["position"] ±= ...` inside `decide` /
   `act`. The framework does exactly one such mutation per fill.
6. Remove every `bid_price = market_data["price"]` and equivalent
   silent-fill fallbacks. If `bid_price` is genuinely optional for
   your action space (`participation_order` category), route through
   `finalize_llm_order` — it distinguishes the category.
7. Re-run `PYTHONPATH=. python3 scripts/audit_scenario_contract.py
   --scenario YourScenario`. Both `STRUCT-*` and `SEM-*` categories
   should be zero for the migrated variant.
8. Run one round of the scenario to confirm cash / position figures
   match the pre-migration baseline (they should — the framework
   arithmetic is identical to what the deleted `act` was doing).

`AnchoringEffect/Rule/players.py` is the target end state: a pure
re-export of canonical classes with no `class Foo(...)` definitions
in the scenario file at all. Not every scenario reaches that level of
compression (some have genuine scenario-specific state), but every
scenario should reach zero `STRUCT-*` and zero `SEM-CASH-MUT` /
`SEM-SILENT-FILL` findings.

## 8. Audit — `scripts/audit_scenario_contract.py`

Structural (AST) + semantic (regex) audit that walks every
`examples/*/{Rule,LLM,RuleLLM,Rag}/players.py` file. Finding
taxonomy:

| Kind | Severity | Meaning |
|---|---|---|
| `STRUCT-ACT` | CRITICAL | Canonical subclass overrides `act`. |
| `STRUCT-DECIDE` | CRITICAL | Canonical subclass overrides `decide`. |
| `SEM-SILENT-FILL` | HIGH | Fallback assignment to `bid_price` from a non-literal source. |
| `SEM-CASH-MUT` | HIGH (inside `decide`/`act`) / MEDIUM (elsewhere) | Direct `self.state.custom_state["cash"]` mutation outside the framework path. |
| `LEGACY-BASE` | INFO | File inherits `GeneralPlayer`; predates the canonical contract. |
| `PARSE-ERROR` / `READ-ERROR` | HIGH | AST could not parse the file. |

Invocation:

```bash
# Full-corpus text report (exit 1 if any CRITICAL/HIGH)
PYTHONPATH=. python3 scripts/audit_scenario_contract.py

# Suppress the LEGACY-BASE informational rows
PYTHONPATH=. python3 scripts/audit_scenario_contract.py --no-legacy-info

# Machine-readable JSON
PYTHONPATH=. python3 scripts/audit_scenario_contract.py --json > audit.json

# Restrict to specific scenarios
PYTHONPATH=. python3 scripts/audit_scenario_contract.py \
  --scenario AnchoringEffect DispositionEffect
```

CI integration: fail the pipeline when either `STRUCT-*` count is
non-zero for any scenario that has been migrated to the canonical
bases. Do not gate on `LEGACY-BASE` — migrating those files is a
scheduled workstream, not a per-commit blocker.

## 9. Verification — `verify_archetype_fixes.py`

The reference verification script lives at the workspace root
(temporarily, since it is dev-time infrastructure rather than
production code) and exercises every anchor-tracking archetype
against three payload shapes: valid BUY, missing `bid_price`, and
zero `bid_price`. The relevant checks:

* Valid BUY updates the anchor to the exact VWAP value the framework
  computed (e.g., `(100·100 + 120·10) / 110 = 101.8182`).
* Missing `bid_price` raises `KeyError` and leaves the anchor
  untouched (atomic state).
* Zero `bid_price` raises `ValueError` from
  `require_positive_bid_price` and leaves the anchor untouched.
* AnchoringEffect `metrics.py` sources strategy identifiers from
  canonical class attributes (`RuleAnchoredTrader.STRATEGY` …),
  yielding kebab-case values that match the wire format.

Current baseline: 24 / 24 passing. Any change to
`_apply_fill_and_emit_action`, `on_fill`, or `require_positive_bid_price`
should be validated with:

```bash
PYTHONPATH=. python3 verify_archetype_fixes.py
```

before landing.

## 10. Related Reading

* `masim/agents/_base.py` — `CanonicalRulePlayer`, `CanonicalLLMPlayer`,
  `_apply_fill_and_emit_action`, `on_fill` default no-op.
* `masim/agents/_rag_base.py` — `CanonicalRagPlayer` (RAG plumbing on
  top of `CanonicalLLMPlayer`).
* `masim/agents/_coordinator_base.py` — `CanonicalMarketCoordinator`.
* `masim/format/finalize.py` — `require_positive_bid_price`,
  `finalize_rule_order`, `finalize_llm_order`, `emit_order_envelope`.
* `masim/format/order.py` — `InvestorOrder`, `BUY`, `SELL`, `HOLD`.
* `examples/AnchoringEffect/simulation-bases.md §7.1` — the contract
  expressed at scenario-design level, with the ALLOWED / FORBIDDEN
  code skeleton for a variant.
* `docs/llm-coding-rules.md §11` — the same rules in coding-checklist
  form.
* `docs/structure.md §2` — where this contract sits in the overall
  execution pipeline.
