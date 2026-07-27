"""Deprecated shim — canonical location is :mod:`masim.format.state`.

The canonical definition of :class:`StandardMarketState` was migrated to
:mod:`masim.format` on 2026-07-24 to enforce the framework-wide rule that
*every fixed inter-module structure lives under masim/format/*. New code
MUST import from :mod:`masim.format.state` (or :mod:`masim.format`
directly). This module is kept only as a thin re-export shim so that the
~100 existing import sites in ``masim/agents/*.py`` and the wider
codebase continue to work; it will be deleted once all callers have been
migrated.
"""

from __future__ import annotations

from masim.format.state import REQUIRED_BROADCAST_FIELDS, StandardMarketState

__all__ = ["StandardMarketState", "REQUIRED_BROADCAST_FIELDS"]
