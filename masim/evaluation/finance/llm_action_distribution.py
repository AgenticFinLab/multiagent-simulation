"""Shared LLM action-distribution audit (implement-simulation-skill §7.2).

Every LLM variant is required by the review skill
(``masim/skills/implement-simulation-skill/09-step5-to-10-review.md``
§7.2) to expose ``analyze_action_distribution(agent_records) -> dict``.

Historically each scenario carried its own copy of this function which
lead to drift.  Per Step 7.1 of the same skill ("evaluation-first"),
the reusable helper lives here and each scenario's LLM analysis module
simply re-exports it.

The function accepts either

    (a) an already-extracted ``agent_records`` mapping
        ``{agent_id: [round_payload_dict, ...]}`` or
        ``{agent_id: {round_num: round_payload_dict}}``; or
    (b) a MASim ``results`` object — in which case per-agent LLM
        turns are extracted from ``results.players_by_role("player")``
        using ``player.turns.payloads()`` (falling back to
        ``player.turns.field(...)`` when the payload accessor is
        unavailable).

Returns a well-typed dict::

    {
      "per_agent": {
         agent_id: {
             "actions": {"buy": n, "sell": n, "hold": n, ...},
             "mean_reasoning_len":  float,
             "median_reasoning_len": float,
             "decision_entropy":     float,   # base-2 bits
             "total_rounds":         int,
         },
         ...
      },
      "aggregate": {
         "actions":             {...},
         "action_fractions":    {...},
         "decision_entropy":    float,
         "mean_reasoning_len":  float,
         "total_rounds":        int,
         "num_agents":          int,
      },
    }

The function is deliberately defensive:

* missing ``reasoning`` (or ``analysis``) field → contributes length 0;
* ambiguous action → default to ``"hold"``;
* if the payload carries a scenario-specific action label (e.g.
  ``opinion``, ``adopt``, ``polarize``) rather than buy/sell/hold, the
  counter is extended dynamically so alternative action spaces still
  produce a valid distribution and entropy;
* empty inputs never raise — an empty ``per_agent`` / zeroed
  ``aggregate`` block is returned instead.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Union

__all__ = ["analyze_action_distribution"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


_CANONICAL_ACTIONS = ("buy", "sell", "hold")


def _infer_action(payload: Mapping[str, Any]) -> str:
    """Return a lowercase action label from an LLM decision payload.

    Priority:
        1. Explicit ``_skipped=True`` marker → ``"_skipped"`` (bootstrap
           placeholder produced by ``_noop_order``; MUST be excluded from
           real action-distribution statistics);
        2. Explicit ``_clipped=True`` marker → ``"_clipped_hold"``
           (buy/sell intent that was clipped to 0 by ``_finalize_order``
           due to insufficient cash/position; distinct from a genuine
           hold decision — silently coercing it inflates the hold bucket
           and understates decisiveness);
        3. Non-Mapping input → ``"_malformed"`` (do NOT coerce to "hold");
        4. Explicit ``action`` field (any non-empty string is lowercased);
        5. Signed ``quantity``: ``>0`` → buy, ``<0`` → sell, ``0`` → hold;
        6. Otherwise → ``"_malformed"`` (do NOT coerce to "hold" — a fake
           hold pollutes decision-entropy and action-frequency metrics).
    """
    if not isinstance(payload, Mapping):
        return "_malformed"
    if payload.get("_skipped"):
        return "_skipped"
    if payload.get("_clipped"):
        return "_clipped_hold"
    raw_action = payload.get("action")
    if raw_action is not None:
        action = str(raw_action).strip().lower()
        if action:
            return action
    # No explicit action → try to infer from quantity
    qty = payload.get("quantity")
    try:
        if qty is not None:
            q = float(qty)
            if q > 0:
                return "buy"
            if q < 0:
                return "sell"
            return "hold"
    except (TypeError, ValueError):
        pass
    return "_malformed"


def _reasoning_length(payload: Mapping[str, Any]) -> int:
    """Return the length in characters of the ``reasoning`` field.

    Falls back to the ``analysis`` field when ``reasoning`` is absent
    (some scenarios' contract uses ``analysis``).  Missing → 0.
    """
    if not isinstance(payload, Mapping):
        return 0
    text = payload.get("reasoning")
    if text is None or text == "":
        text = payload.get("analysis", "")
    if text is None:
        return 0
    return len(str(text))


def _shannon_entropy(counts: Mapping[str, int]) -> float:
    """Base-2 Shannon entropy over ``counts`` (0 if empty / degenerate)."""
    total = sum(int(v) for v in counts.values())
    if total <= 0:
        return 0.0
    entropy = 0.0
    for c in counts.values():
        c_int = int(c)
        if c_int <= 0:
            continue
        p = c_int / total
        entropy -= p * math.log2(p)
    return float(entropy)


def _median(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2 == 1:
        return float(ordered[mid])
    return float((ordered[mid - 1] + ordered[mid]) / 2.0)


def _payloads_iter(rounds_obj: Any) -> Iterable[Mapping[str, Any]]:
    """Yield payload dicts from either a list or a ``{round: payload}`` dict."""
    if rounds_obj is None:
        return []
    if isinstance(rounds_obj, Mapping):
        return list(rounds_obj.values())
    if isinstance(rounds_obj, (list, tuple)):
        return list(rounds_obj)
    # Anything else (e.g. generator) → materialise
    try:
        return list(rounds_obj)
    except TypeError:
        return []


def _extract_from_results(results: Any) -> Dict[str, List[Mapping[str, Any]]]:
    """Extract ``{agent_id: [payload, ...]}`` from a MASim results object.

    Falls back to ``player.turns.field(name)`` when ``payloads()`` is
    not available on the store.
    """
    per_agent: Dict[str, List[Mapping[str, Any]]] = {}
    players = results.players_by_role("player")
    for agent_id, player in players.items():
        turns = getattr(player, "turns", None)
        if turns is None:
            continue
        payloads_map: Dict[int, Mapping[str, Any]] = {}
        if hasattr(turns, "payloads"):
            try:
                got = turns.payloads()
                if isinstance(got, Mapping):
                    payloads_map = dict(got)
            except Exception:  # noqa: BLE001 — never crash the audit
                payloads_map = {}
        if not payloads_map and hasattr(turns, "field"):
            # Reassemble a payload-shaped dict from selected fields.
            fields_of_interest = ("action", "quantity", "reasoning", "analysis")
            per_round: Dict[int, Dict[str, Any]] = {}
            for name in fields_of_interest:
                try:
                    vals = turns.field(name) or {}
                except Exception:  # noqa: BLE001
                    vals = {}
                for round_num, v in (vals or {}).items():
                    per_round.setdefault(round_num, {})[name] = v
            payloads_map = per_round  # type: ignore[assignment]
        if payloads_map:
            # Preserve round order
            per_agent[agent_id] = [
                payloads_map[r] for r in sorted(payloads_map.keys())
                if isinstance(payloads_map[r], Mapping)
            ]
    return per_agent


def _normalise_records(
    agent_records: Any,
) -> Dict[str, List[Mapping[str, Any]]]:
    """Coerce accepted input shapes into ``{agent_id: [payload, ...]}``."""
    if agent_records is None:
        return {}
    # Duck-typed check for a Results object.
    if hasattr(agent_records, "players_by_role"):
        return _extract_from_results(agent_records)
    if not isinstance(agent_records, Mapping):
        return {}
    normalised: Dict[str, List[Mapping[str, Any]]] = {}
    for agent_id, rounds_obj in agent_records.items():
        payloads = [p for p in _payloads_iter(rounds_obj) if isinstance(p, Mapping)]
        if payloads:
            normalised[str(agent_id)] = payloads
    return normalised


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def analyze_action_distribution(
    agent_records: Union[Mapping[str, Any], Any, None],
) -> Dict[str, Any]:
    """Compute per-agent LLM action metrics + an aggregate block.

    Parameters
    ----------
    agent_records
        Either a mapping ``{agent_id: [payload, ...] or {round: payload}}``
        or a MASim ``results`` object (has ``players_by_role``).  ``None``
        or an empty mapping returns a zeroed audit rather than raising.

    Returns
    -------
    dict
        See module docstring for the exact shape.
    """
    records = _normalise_records(agent_records)

    per_agent: Dict[str, Dict[str, Any]] = {}
    aggregate_counts: Dict[str, int] = {a: 0 for a in _CANONICAL_ACTIONS}
    aggregate_skipped: int = 0
    aggregate_malformed: int = 0
    aggregate_clipped: int = 0
    all_reasoning_lens: List[int] = []

    for agent_id, payloads in records.items():
        if not payloads:
            continue
        counts: Dict[str, int] = {a: 0 for a in _CANONICAL_ACTIONS}
        skipped_count = 0
        malformed_count = 0
        clipped_count = 0
        reasoning_lens: List[int] = []
        for payload in payloads:
            action = _infer_action(payload)
            if action == "_skipped":
                skipped_count += 1
                # Do NOT include reasoning length for synthetic bootstrap
                # placeholders — they have no real reasoning.
                continue
            if action == "_malformed":
                malformed_count += 1
                continue
            if action == "_clipped_hold":
                # Constraint-clipped intended trade — count separately so
                # the canonical hold bucket reflects only genuine holds.
                clipped_count += 1
                reasoning_lens.append(_reasoning_length(payload))
                continue
            counts[action] = counts.get(action, 0) + 1
            reasoning_lens.append(_reasoning_length(payload))

        total_rounds = sum(counts.values())
        if (
            total_rounds == 0
            and skipped_count == 0
            and malformed_count == 0
            and clipped_count == 0
        ):
            continue

        mean_len = (
            float(sum(reasoning_lens) / len(reasoning_lens))
            if reasoning_lens else 0.0
        )
        median_len = _median(reasoning_lens)
        entropy = _shannon_entropy(counts)

        per_agent[agent_id] = {
            "actions": dict(counts),
            "skipped_rounds": int(skipped_count),
            "malformed_rounds": int(malformed_count),
            "clipped_hold_rounds": int(clipped_count),
            "mean_reasoning_len": round(mean_len, 4),
            "median_reasoning_len": round(median_len, 4),
            "decision_entropy": round(entropy, 4),
            "total_rounds": int(total_rounds),
        }
        for key, val in counts.items():
            aggregate_counts[key] = aggregate_counts.get(key, 0) + int(val)
        aggregate_skipped += skipped_count
        aggregate_malformed += malformed_count
        aggregate_clipped += clipped_count
        all_reasoning_lens.extend(reasoning_lens)

    aggregate_total = sum(aggregate_counts.values())
    aggregate = {
        "actions": dict(aggregate_counts),
        "action_fractions": {
            k: (v / aggregate_total if aggregate_total else 0.0)
            for k, v in aggregate_counts.items()
        },
        "decision_entropy": round(_shannon_entropy(aggregate_counts), 4),
        "mean_reasoning_len": (
            round(float(sum(all_reasoning_lens) / len(all_reasoning_lens)), 4)
            if all_reasoning_lens else 0.0
        ),
        "total_rounds": int(aggregate_total),
        "skipped_rounds": int(aggregate_skipped),
        "malformed_rounds": int(aggregate_malformed),
        "clipped_hold_rounds": int(aggregate_clipped),
        "num_agents": len(per_agent),
    }
    return {"per_agent": per_agent, "aggregate": aggregate}
