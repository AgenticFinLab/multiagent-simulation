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
import shutil
from datetime import datetime
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Internal: discover teams already on disk
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parents[3]  # components → interface → masim → root
_CUSTOMIZED_DIR = _PROJECT_ROOT / "configs" / "CUSTOMIZED_SIMULATION"
_EXPERIMENT_CUSTOMIZED_DIR = _PROJECT_ROOT / "EXPERIMENT" / "CUSTOMIZED_SIMULATION"
# ``examples/CUSTOMIZED_SIMULATION`` is populated as a side-effect of
# ``initialize_customized_folder`` / ``copy_default_scenario_bundle``
# (both live in ``masim/interface/customized/config_writer.py``) — every
# customize-bundle snapshot has a matching subtree here.  Must be included
# in team deletion, otherwise soft-delete leaves orphan snapshots behind.
_EXAMPLES_CUSTOMIZED_DIR = _PROJECT_ROOT / "examples" / "CUSTOMIZED_SIMULATION"
_TEAM_REGISTRY = _PROJECT_ROOT / "configs" / ".team_registry"
# Soft-delete quarantine: deleted team assets are MOVED here (never `rm`-ed)
# so an accidental click can be recovered manually.  Timestamped subdirs
# avoid collisions when the same team slug is deleted twice.
_DELETED_TEAMS_DIR = _PROJECT_ROOT / "configs" / ".deleted_teams"
_BUNDLE_NAME_RE = re.compile(r"^(.+)-([0-9a-fA-F]{8})-([^-]+)$")
_TEAM_IN_SLUG_RE = re.compile(r"^team-([A-Za-z0-9_]+)-(.+)$")


def _discover_existing_teams() -> list[str]:
    """Return all known team slugs (from registry + disk scan)."""
    teams: set[str] = set()
    # Source 1: registry file (teams that have logged in at least once)
    if _TEAM_REGISTRY.exists():
        for line in _TEAM_REGISTRY.read_text().splitlines():
            name = line.strip()
            if name:
                teams.add(name)
    # Source 2: bundles on disk (fallback for teams not yet in registry)
    if _CUSTOMIZED_DIR.exists():
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


def _register_team(slug: str) -> None:
    """Append a team slug to the registry file (idempotent)."""
    existing = set()
    if _TEAM_REGISTRY.exists():
        existing = {
            line.strip()
            for line in _TEAM_REGISTRY.read_text().splitlines()
            if line.strip()
        }
    if slug not in existing:
        _TEAM_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
        with _TEAM_REGISTRY.open("a") as f:
            f.write(slug + "\n")


def _unregister_team(slug: str) -> None:
    """Remove a team slug from the registry file (idempotent, order-preserving)."""
    if not _TEAM_REGISTRY.exists():
        return
    kept: list[str] = []
    for line in _TEAM_REGISTRY.read_text().splitlines():
        s = line.strip()
        if s and s != slug:
            kept.append(s)
    _TEAM_REGISTRY.write_text(("\n".join(kept) + "\n") if kept else "")


def _collect_team_paths(slug: str) -> list[Path]:
    """Return every on-disk directory that belongs to ``slug``.

    Covers:
    * ``configs/CUSTOMIZED_SIMULATION/team-{slug}-*`` — source bundles.
    * ``EXPERIMENT/CUSTOMIZED_SIMULATION/team-{slug}-*`` — run outputs.
    * ``examples/CUSTOMIZED_SIMULATION/team-{slug}-*`` — snapshot copies
      produced by ``initialize_customized_folder`` /
      ``copy_default_scenario_bundle`` (missed by earlier revisions).

    The scan uses the strict ``TEAM_NAME_IN_SLUG_RE`` decode so we never
    delete a legacy or another-team directory whose name happens to start
    with the same characters.  Returns an empty list when nothing matches.
    """
    hits: list[Path] = []
    for root in (_CUSTOMIZED_DIR, _EXPERIMENT_CUSTOMIZED_DIR, _EXAMPLES_CUSTOMIZED_DIR):
        if not root.exists():
            continue
        for entry in root.iterdir():
            if not entry.is_dir():
                continue
            m = _BUNDLE_NAME_RE.match(entry.name)
            if not m:
                continue
            raw_slug = m.group(1)
            tm = _TEAM_IN_SLUG_RE.match(raw_slug)
            if tm and tm.group(1) == slug:
                hits.append(entry)
    return hits


def _quarantine_team(slug: str) -> tuple[int, Path]:
    """Move every asset owned by ``slug`` into the soft-delete quarantine.

    Uses :func:`shutil.move` (never ``rm``) so an accidental click can
    always be recovered by moving the timestamped folder back into place.
    Also drops ``slug`` from ``.team_registry`` so the quick-select
    dropdown stops offering it.

    Returns ``(moved_count, quarantine_root)`` — the caller can surface
    ``quarantine_root`` so the user knows where their data went.
    """
    paths = _collect_team_paths(slug)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    quarantine_root = _DELETED_TEAMS_DIR / f"{stamp}-{slug}"
    if paths:
        quarantine_root.mkdir(parents=True, exist_ok=True)
        for src in paths:
            # Preserve the FULL parent path (relative to the project
            # root) so bundles coming from ``configs/CUSTOMIZED_SIMULATION``
            # don't collide with bundles from
            # ``EXPERIMENT/CUSTOMIZED_SIMULATION`` — both parents share
            # the same leaf name and would otherwise nest inside each
            # other after two consecutive ``shutil.move`` calls.
            try:
                rel_parent = src.parent.relative_to(_PROJECT_ROOT)
            except ValueError:
                rel_parent = Path(src.parent.name)
            dest_parent = quarantine_root / rel_parent
            dest_parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest_parent / src.name))
    # Registry cleanup happens even when nothing was on disk — the slug
    # may still be lingering there from a first-touch login that never
    # produced any bundles.
    _unregister_team(slug)
    return len(paths), quarantine_root

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
        _register_team(slug)


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

        # --- Prefill from quick-select (must happen BEFORE widget renders) ---
        _prefill = st.session_state.pop("_prefill_team", "")
        if _prefill:
            st.session_state["team_gate_input"] = _prefill

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
                _register_team(slug)
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
                    "📋 <b>已有团队</b>（点击填入上方输入框）:</span></div>",
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
                            st.session_state["_prefill_team"] = team
                            st.rerun()

                # --- Manage / delete teams (destructive) ---
                _render_team_delete_panel(existing)

        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
        st.caption(
            "🔒 Team names are used only to namespace files on the server. "
            "There is no password — please stick to your assigned handle."
        )


def _render_team_delete_panel(existing: list[str]) -> None:
    """Collapsible danger-zone panel for removing a team and its data.

    Kept inside an ``st.expander`` (collapsed by default) so first-time
    visitors never brush against a destructive control by accident.
    Every team gets its own **two-step** confirmation:

    1. Click the 🗑️ trash button next to the team name.  This just marks
       the team as "pending delete" in session state — nothing on disk
       has been touched yet.
    2. A confirmation row appears: the user must **type the exact team
       slug** and click **Confirm delete**.  Only then does
       :func:`_quarantine_team` move the assets to
       ``configs/.deleted_teams/{timestamp}-{slug}/``.

    Deleted assets are never ``rm``-ed; they are moved into a
    timestamped quarantine folder, so an accidental click can be
    reversed by moving the folder back manually.
    """
    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
    with st.expander("🗑️ 管理 / 删除团队 (Manage / delete teams)", expanded=False):
        st.caption(
            "危险操作。删除后该团队的项目配置与实验结果会被移动到 "
            "`configs/.deleted_teams/` 子目录（时间戳归档），可人工恢复；"
            "但当前 UI 不会再显示它。"
        )
        _pending_key = "_team_delete_pending"
        pending = st.session_state.get(_pending_key, "")

        for team in existing:
            row_left, row_right = st.columns([4, 1], gap="small")
            with row_left:
                st.markdown(
                    f"<div style='padding:0.35rem 0;'>"
                    f"<code style='background:#f3f4f6;padding:2px 6px;"
                    f"border-radius:4px;'>{team}</code></div>",
                    unsafe_allow_html=True,
                )
            with row_right:
                if st.button(
                    "🗑️",
                    key=f"_del_team_btn_{team}",
                    help=f"Move team '{team}' and all its bundles to the quarantine folder.",
                    use_container_width=True,
                ):
                    st.session_state[_pending_key] = team
                    # Clear any previous confirmation input so the new
                    # row starts empty.
                    st.session_state.pop("_team_delete_confirm_input", None)
                    st.rerun()

            # Inline confirmation row for the currently-pending team.
            if pending == team:
                # Pre-flight scan so we can tell the user exactly how
                # many folders will be moved.
                affected = len(_collect_team_paths(team))
                st.warning(
                    f"⚠️ 即将删除团队 **`{team}`** — 会移动 **{affected}** 个"
                    f"目录（configs/CUSTOMIZED_SIMULATION + EXPERIMENT/CUSTOMIZED_SIMULATION）。"
                    "请在下方输入框输入团队名以确认。"
                )
                confirm_left, confirm_mid, confirm_right = st.columns(
                    [3, 1, 1], gap="small"
                )
                with confirm_left:
                    typed = st.text_input(
                        "Type the team name to confirm",
                        key="_team_delete_confirm_input",
                        placeholder=team,
                        label_visibility="collapsed",
                    )
                with confirm_mid:
                    if st.button(
                        "✅ Confirm",
                        key=f"_del_team_confirm_{team}",
                        type="primary",
                        use_container_width=True,
                        disabled=(typed.strip().lower() != team.lower()),
                    ):
                        moved, quarantine_root = _quarantine_team(team)
                        # If the user is deleting their own signed-in
                        # team (unlikely from the pre-gate screen, but
                        # possible if this panel is embedded elsewhere
                        # later), wipe the identity keys too.
                        if current_team() == team:
                            st.session_state.pop(TEAM_NAME_KEY, None)
                            try:
                                st.query_params.pop(_QUERY_KEY, None)
                            except Exception:
                                pass
                        # Independent of ``current_team()`` also drop the
                        # ``?team=`` URL query if it happens to STILL
                        # point at the deleted slug — e.g. a stale link
                        # a user pasted from Slack.  Leaving it in place
                        # would immediately re-materialise the deleted
                        # team on the next rerun via
                        # ``bootstrap_team_from_query``.
                        else:
                            try:
                                if st.query_params.get(_QUERY_KEY, "") == team:
                                    st.query_params.pop(_QUERY_KEY, None)
                            except Exception:
                                pass
                        st.session_state.pop(_pending_key, None)
                        st.session_state.pop(
                            "_team_delete_confirm_input", None
                        )
                        # Also clear any stale "prefill" pointing at the
                        # team we just removed, so the input field
                        # doesn't repopulate it on next rerun.
                        if st.session_state.get("_prefill_team") == team:
                            st.session_state.pop("_prefill_team", None)
                        # Wipe transient welcome-page chip pointers so a
                        # subsequent welcome render cannot repopulate the
                        # project-name input from a project that no
                        # longer has any on-disk bundles.  These keys are
                        # normally single-use (popped on read in
                        # ``welcome.py``) but a race between deletion and
                        # the next welcome render can leave them stuck
                        # for one extra rerun.
                        for _stale in (
                            "_welcome_pending_name",
                            "_welcome_pending_id",
                            "_welcome_selected_project",
                        ):
                            st.session_state.pop(_stale, None)
                        try:
                            rel = quarantine_root.relative_to(_PROJECT_ROOT)
                            location = str(rel)
                        except ValueError:
                            location = str(quarantine_root)
                        st.success(
                            f"团队 `{team}` 已删除 — 移动了 {moved} 个目录到 "
                            f"`{location}` （如需恢复请人工移回）。"
                        )
                        st.rerun()
                with confirm_right:
                    if st.button(
                        "Cancel",
                        key=f"_del_team_cancel_{team}",
                        use_container_width=True,
                    ):
                        st.session_state.pop(_pending_key, None)
                        st.session_state.pop(
                            "_team_delete_confirm_input", None
                        )
                        st.rerun()
