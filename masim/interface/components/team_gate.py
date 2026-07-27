"""Team gate — first-touch identity page for multi-team deployments.

Purpose
-------
When MASIM is deployed as a shared web service (e.g. a summer-camp platform
serving 8 teams simultaneously on one Huawei ECS instance), each browser
session needs a *team* label so that:

* new bundles are namespaced ``team-{team}-*`` on disk, and
* the project list in the workspace only shows the current team's bundles.

This module implements a lightweight, self-contained gate that runs BEFORE
the normal welcome page:

* If ``?team=<slug>`` is present in the URL and looks valid, it is adopted
  automatically into ``st.session_state["team_name"]``.  The team member
  can bookmark ``https://your-domain.com/?team=redwolf`` and skip the form
  on every visit.
* Otherwise the user sees a small form that asks for a team name.  On
  submit the name is validated, lower-cased, written into session state,
  AND appended to the URL as ``?team=<slug>`` so that a reload or a link
  copy keeps the identity.

The gate is deliberately independent of the rest of the workflow — it
only touches ``st.session_state["team_name"]`` and ``st.query_params``.
Downstream code (bundle naming, project-list filtering, semaphore keys)
consumes ``st.session_state["team_name"]`` and never re-parses the URL.

Design constraints (per product decisions)
------------------------------------------

* English-only team names — students agreed to use English aliases so
  filesystem paths stay ASCII-safe and no slug transliteration is needed.
* No password / PIN — the 8 teams are trusted classmates; a shared basic
  auth in front of Nginx already gates external access.  A future
  enhancement could add a per-team PIN by storing a small dict in a
  config file and comparing on submit.
"""
from __future__ import annotations

import re
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Internal: discover teams already on disk
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parents[3]  # components → interface → masim → root
_CUSTOMIZED_DIR = _PROJECT_ROOT / "configs" / "CUSTOMIZED_SIMULATION"
_BUNDLE_NAME_RE = re.compile(r"^(.+)-([0-9a-fA-F]{8})-([^-]+)$")
_TEAM_IN_SLUG_RE = re.compile(r"^team-([A-Za-z0-9_]+)-(.+)$")


def _discover_existing_teams() -> list[str]:
    """Scan disk for team slugs that already have bundles."""
    teams: set[str] = set()
    if not _CUSTOMIZED_DIR.exists():
        return []
    for entry in _CUSTOMIZED_DIR.iterdir():
        if not entry.is_dir():
            continue
        m = _BUNDLE_NAME_RE.match(entry.name)
        if not m:
            continue
        raw_slug = m.group(1)
        tm = _TEAM_IN_SLUG_RE.match(raw_slug)
        if tm:
            teams.add(tm.group(1))
    return sorted(teams)

__all__ = [
    "TEAM_NAME_KEY",
    "TEAM_NAME_MIN",
    "TEAM_NAME_MAX",
    "bootstrap_team_from_query",
    "render_team_gate",
    "current_team",
    "validate_team_name",
]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Session-state key that holds the active team name (lower-case slug).  All
# downstream code (config_writer, agent_market, analysis_view) must read
# from this single key so that swapping the source of identity later (e.g.
# to a real login) only requires changing this module.
TEAM_NAME_KEY = "team_name"

# Length bounds — kept short so the team name comfortably fits inside
# bundle directory names such as ``team-redwolf-MYTest-abc12345-Scenario``.
TEAM_NAME_MIN = 3
TEAM_NAME_MAX = 20

# Allowed characters: ASCII letters (case-insensitive at input, lower-cased
# on save), digits and underscores.  Hyphens are deliberately EXCLUDED so
# bundle folder names of the shape ``team-{team}-{slug}-{pid}-{scenario}``
# parse unambiguously — a hyphen inside the team name would let the parser
# lose track of where the team segment ends.  Spaces, dots, slashes and
# other symbols are also excluded so no path-traversal is possible via
# the team slug.
_ALLOWED_CHARS_RE = re.compile(r"^[A-Za-z0-9_]+$")

# Query-parameter name used to persist the team across reloads.
_QUERY_KEY = "team"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def current_team() -> str:
    """Return the active team name, or an empty string if the gate hasn't
    been passed yet."""
    return str(st.session_state.get(TEAM_NAME_KEY, "") or "")


def validate_team_name(raw: str) -> tuple[str, str]:
    """Validate a user-supplied team name.

    Returns a tuple ``(slug, error)`` where ``slug`` is the cleaned,
    lower-cased slug on success and ``error`` carries a human-readable
    error message on failure.  On success ``error`` is empty; on failure
    ``slug`` is empty.  This shape keeps callers branchless.
    """
    text = (raw or "").strip()
    if not text:
        return "", "Please enter a team name."
    if len(text) < TEAM_NAME_MIN:
        return "", (
            f"Team name is too short — please use at least {TEAM_NAME_MIN} "
            "characters."
        )
    if len(text) > TEAM_NAME_MAX:
        return "", (
            f"Team name is too long — please keep it within {TEAM_NAME_MAX} "
            "characters."
        )
    if not _ALLOWED_CHARS_RE.match(text):
        return "", (
            "Team name may only contain English letters (A-Z, a-z), digits "
            "(0-9) and underscores (_).  Spaces, hyphens and other symbols "
            "are not allowed."
        )
    # Reject leading/trailing underscores so slugs never render weirdly
    # (e.g. ``_redwolf`` or ``redwolf_``).
    if text[0] == "_" or text[-1] == "_":
        return "", "Team name may not start or end with an underscore ('_')."
    return text.lower(), ""


def bootstrap_team_from_query() -> None:
    """Adopt a valid ``?team=<slug>`` URL parameter into session state.

    Called ONCE at app startup, before ``main()`` decides which page to
    render.  Idempotent: if the session already has a team, or the URL
    doesn't carry one, this is a no-op.  Invalid URL values are silently
    ignored — the user will see the gate form and can correct their input.
    """
    # Session already established — nothing to do.  Deliberately overwrite
    # only when the current session team is empty, so a page reload with
    # a stale bookmark can't hijack an already-authenticated session.
    if current_team():
        return
    try:
        raw = st.query_params.get(_QUERY_KEY, "")
    except Exception:
        # ``st.query_params`` is a Streamlit ≥1.30 API; on older builds it
        # may raise.  Fail closed to the form.
        return
    # ``st.query_params.get`` can return either a str or a list depending
    # on Streamlit version — normalise to a single string.
    if isinstance(raw, (list, tuple)):
        raw = raw[0] if raw else ""
    slug, err = validate_team_name(str(raw))
    if slug and not err:
        st.session_state[TEAM_NAME_KEY] = slug


def render_team_gate() -> None:
    """Render the team-name input form.

    Called from ``main()`` when ``current_team()`` is empty.  Blocks the
    rest of the app: the caller must ``return`` immediately after this
    function so the welcome/workflow pages don't render underneath.

    On successful submit the team name is written into
    ``st.session_state[TEAM_NAME_KEY]`` AND ``st.query_params[_QUERY_KEY]``
    (so bookmarking the URL preserves identity), then the app is rerun so
    the normal workflow takes over.
    """
    # Centre the form in a narrow column so it looks intentional even on
    # a wide desktop monitor.  Streamlit doesn't offer a native "centered
    # card" primitive, so we approximate it with a 3-column layout.
    _left, middle, _right = st.columns([1, 2, 1])
    with middle:
        st.markdown(
            "<div style='height:2.5rem'></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<h1 style='text-align:center;margin-bottom:0.2rem;'>"
            "👋 Welcome to MASIM</h1>"
            "<p style='text-align:center;color:#9ba8bb;margin-top:0;'>"
            "Multi-Agent Financial Simulation — Summer Camp Platform</p>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown(
                "#### 🏷️ Choose your team name",
            )
            st.caption(
                "Pick a short English handle for your team — this becomes "
                "your workspace identity so your projects stay separate "
                "from other teams'."
            )

            st.markdown(
                f"**命名规则**: {TEAM_NAME_MIN}-{TEAM_NAME_MAX} 个字符，"
                "仅允许英文字母、数字和下划线 `_`（不能包含空格、连字符或中文）"
            )

            with st.form("team_gate_form", clear_on_submit=False):
                team_input = st.text_input(
                    "Team name",
                    key="team_gate_input",
                    max_chars=TEAM_NAME_MAX,
                    placeholder="e.g. redwolf",
                    label_visibility="collapsed",
                )
                submitted = st.form_submit_button(
                    "Enter platform  →",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                slug, err = validate_team_name(team_input)
                if err:
                    st.error(err)
                    return
                # Persist to session state and mirror to URL so a reload
                # or link-copy keeps the identity.  Setting a query param
                # value triggers a rerun automatically in Streamlit ≥1.30.
                st.session_state[TEAM_NAME_KEY] = slug
                try:
                    st.query_params[_QUERY_KEY] = slug
                except Exception:
                    # Older Streamlit — best-effort only; the session
                    # state assignment is enough for this browser tab.
                    pass
                st.rerun()

            # --- Examples section ---
            st.markdown(
                "<div style='margin-top:0.6rem;padding:0.6rem 0.8rem;"
                "background:#f0f4f8;border-radius:6px;font-size:0.85rem;'>"
                "✅ <b>有效示例</b>: <code>redwolf</code> · "
                "<code>team_alpha</code> · <code>bluefox3</code> · "
                "<code>GroupA</code><br>"
                "❌ <b>无效示例</b>: <code>red-wolf</code>(含连字符) · "
                "<code>ab</code>(太短) · <code>_team</code>(下划线开头) · "
                "<code>我的团队</code>(中文)"
                "</div>",
                unsafe_allow_html=True,
            )

            # --- Existing teams quick-select ---
            existing = _discover_existing_teams()
            if existing:
                st.markdown(
                    "<div style='margin-top:0.8rem;'>"
                    "<span style='font-size:0.85rem;color:#4a4a4a;'>"
                    "📋 <b>已有团队</b>（点击直接进入）:</span></div>",
                    unsafe_allow_html=True,
                )
                cols = st.columns(min(len(existing), 4))
                for i, team in enumerate(existing):
                    with cols[i % min(len(existing), 4)]:
                        if st.button(
                            team,
                            key=f"_quick_team_{team}",
                            use_container_width=True,
                        ):
                            st.session_state[TEAM_NAME_KEY] = team
                            try:
                                st.query_params[_QUERY_KEY] = team
                            except Exception:
                                pass
                            st.rerun()

        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
        st.caption(
            "🔒 Team names are used only to namespace files on the server. "
            "There is no password — please stick to your assigned handle."
        )
