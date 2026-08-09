"""AnchoringEffect LLM variant package.

All archetypes live in :mod:`examples.AnchoringEffect.LLM.players` and
are referenced by their explicit classpath from
``configs/AnchoringEffect/LLM/players.yml`` (e.g.
``"examples.AnchoringEffect.LLM.players:LLMAnchoredTrader"``). This
``__init__`` deliberately re-exports nothing — the module-level surface
is authoritative, so a stale hand-maintained ``__all__`` here cannot
drift out of sync with :mod:`.players`.
"""
