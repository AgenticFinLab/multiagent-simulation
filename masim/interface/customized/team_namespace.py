"""Team-namespace helpers for MASIM customized bundles.

Purpose
-------
When MASIM is deployed as a shared web service (e.g. an 8-team summer
camp on a single Huawei ECS instance), each team's bundle folders on
disk are prefixed with ``team-{team_name}-`` so:

* the same friendly project name (``MYTest``) can be reused across teams
  without folder collisions, and
* the workspace's project list can filter server-side files down to the
  bundles owned by the currently-signed-in team (plus any pre-feature
  "legacy" bundles, which stay universally visible so nothing that used
  to work stops working).

Bundle folder-name convention
-----------------------------
* Team-owned:  ``team-{team}-{project_slug}-{project_id:8hex}-{scenario}``
* Legacy:      ``{project_slug}-{project_id:8hex}-{scenario}``

The ``team-`` prefix is a **literal fixed marker**.  The team segment
itself is validated at :mod:`masim.interface.components.team_gate` to
match ``[A-Za-z0-9_]+`` — critically, hyphens are excluded there so the
parser here can rely on the FIRST hyphen after ``team-`` marking the
end of the team segment, giving a fully unambiguous decode.

This module is deliberately I/O-free.  It exposes:

* :data:`TEAM_PREFIX_LITERAL` — the literal ``"team-"`` marker.
* :data:`TEAM_NAME_IN_SLUG_RE` — the parser regex used by other helpers.
* :func:`apply_team_prefix` / :func:`strip_team_prefix` — inverses.
* :func:`owning_team_of` — decode who owns a bundle slug (``None``
  for legacy).
* :func:`is_team_prefixed` — boolean form of the above.
* :func:`is_visible_to_team` — the single choke-point predicate that
  decides whether a bundle should surface in a team's project list.
* :func:`compose_bundle_name` — the convenience assembler used at every
  bundle-creation call site so the naming rule stays in one place.

Backward compatibility
----------------------
Legacy bundles created before this feature (no ``team-`` prefix) are
treated as **shared demos, visible to every team**.  This keeps the
runtime behaviour of anything that pre-dates the multi-team feature
unchanged.  If tighter isolation of legacy content is ever needed,
:func:`is_visible_to_team` is the only site to tighten.
"""
from __future__ import annotations

import re
from typing import Optional

__all__ = [
    "TEAM_PREFIX_LITERAL",
    "TEAM_NAME_IN_SLUG_RE",
    "apply_team_prefix",
    "strip_team_prefix",
    "owning_team_of",
    "is_team_prefixed",
    "is_visible_to_team",
    "compose_bundle_name",
]

# Fixed literal marker: every team-owned slug begins with
# ``team-{validated_team_name}-``.  Making the marker a constant keeps
# all consumers in sync and gives grep-friendly discoverability.
TEAM_PREFIX_LITERAL = "team-"

# Parser regex.  ``[A-Za-z0-9_]+`` mirrors the character policy enforced
# by :mod:`team_gate._ALLOWED_CHARS_RE`, so any slug that decodes here is
# guaranteed to have been produced by a validated team name.  ``.+`` for
# the trailing project slug is greedy on purpose: real project slugs can
# and do contain hyphens (e.g. ``AnchoringEffect-tweaked``).
TEAM_NAME_IN_SLUG_RE = re.compile(r"^team-([A-Za-z0-9_]+)-(.+)$")


def apply_team_prefix(project_slug: str, team_name: str) -> str:
    """Wrap ``project_slug`` with ``team-{team_name}-``.

    Idempotent: if the slug is already prefixed with the same team, it
    is returned verbatim so double-application is a no-op.  If either
    argument is empty, the slug is returned unchanged — this lets
    bundle-creation call sites invoke the helper unconditionally without
    worrying about pre-gate code paths (which don't have a team yet).

    Args:
        project_slug: The project slug produced by ``_slugify(display_name)``.
        team_name: The current team's validated slug (lower-case).

    Returns:
        Either ``project_slug`` unchanged (empty inputs) or the prefixed
        form ``"team-{team_name}-{project_slug}"``.
    """
    if not team_name or not project_slug:
        return project_slug or ""
    if project_slug.startswith(f"{TEAM_PREFIX_LITERAL}{team_name}-"):
        return project_slug
    return f"{TEAM_PREFIX_LITERAL}{team_name}-{project_slug}"


def owning_team_of(project_slug: str) -> Optional[str]:
    """Decode which team owns ``project_slug`` (``None`` for legacy).

    A slug is considered team-owned when it matches
    :data:`TEAM_NAME_IN_SLUG_RE`.  All other slugs (including any pre-
    feature bundle that happens to start with a ``team-`` fragment that
    isn't followed by a validator-legal team name) return ``None`` and
    are treated as shared / legacy content.
    """
    if not project_slug:
        return None
    m = TEAM_NAME_IN_SLUG_RE.match(project_slug)
    return m.group(1) if m else None


def strip_team_prefix(project_slug: str, team_name: str = "") -> str:
    """Return ``project_slug`` with any ``team-{team_name}-`` marker removed.

    When ``team_name`` is provided the helper only strips that specific
    prefix (guarding against accidentally stripping another team's marker
    from a slug you weren't expecting).  When ``team_name`` is empty the
    helper auto-detects the team via :data:`TEAM_NAME_IN_SLUG_RE` and
    strips whatever team it finds.

    Non-prefixed slugs are returned unchanged, so this function is safe
    to call defensively on any slug — legacy or team-owned.
    """
    if not project_slug:
        return project_slug or ""
    if team_name:
        marker = f"{TEAM_PREFIX_LITERAL}{team_name}-"
        if project_slug.startswith(marker):
            return project_slug[len(marker):]
        return project_slug
    m = TEAM_NAME_IN_SLUG_RE.match(project_slug)
    return m.group(2) if m else project_slug


def is_team_prefixed(project_slug: str) -> bool:
    """Convenience boolean form of :func:`owning_team_of`."""
    return owning_team_of(project_slug) is not None


def is_visible_to_team(project_slug: str, viewer_team: str) -> bool:
    """Should a bundle with ``project_slug`` appear in ``viewer_team``'s list?

    Visibility rules:

    * Bundle owned by ``viewer_team``  → visible.
    * Legacy bundle (no team prefix)   → visible (shared demo).
    * Bundle owned by another team     → hidden.

    An empty ``viewer_team`` (should not happen in production because
    the team gate blocks the app until a name is set) is treated as a
    special "see everything" mode; that keeps CLI diagnostics working
    when this helper is exercised outside a Streamlit session.
    """
    owner = owning_team_of(project_slug)
    if owner is None:
        return True  # legacy — visible to everyone
    if not viewer_team:
        return True  # unauthenticated / CLI context — no filtering
    return owner == viewer_team


def compose_bundle_name(
    project_slug: str,
    project_id: str,
    scenario: str,
    team_name: str = "",
) -> str:
    """Assemble the on-disk bundle folder name.

    This is the single source of truth for how a bundle folder is named,
    so every creation call site can stay a one-liner.  The format is:

    * Team-owned: ``team-{team}-{slug}-{project_id}-{scenario}``
    * No-team:    ``{slug}-{project_id}-{scenario}``  (empty team_name)

    Args:
        project_slug: Project slug from ``_slugify(display_name)`` — will
            NOT be double-prefixed if it already carries the team marker.
        project_id: The 8-char hex project id from ``project_meta.json``.
        scenario: Base scenario name (must be hyphen-free — the
            surrounding codebase enforces this via ``_BUNDLE_NAME_RE``
            and repeated ``rsplit("-", 1)`` parsers).
        team_name: The currently-signed-in team's validated slug (may
            be empty in pre-gate / CLI contexts).

    Returns:
        The assembled bundle folder name.
    """
    prefixed_slug = apply_team_prefix(project_slug, team_name)
    return f"{prefixed_slug}-{project_id}-{scenario}"
