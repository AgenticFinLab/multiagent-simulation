"""Welcome / landing page for the MASIM web interface.

Stage 0 of the workflow: greet the user, present the brand logo and a short
introduction, and capture a **project name**. That name becomes the primary
identifier for the whole session; submitting it creates
``examples/<slug>/`` as the base run environment.

Flow: welcome  →  scenario_setup  →  variant_choice / customize  →  workspace
"""
from __future__ import annotations

import base64
import json
import re
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import streamlit as st

from ..customized.team_namespace import (
    is_visible_to_team,
    owning_team_of,
    strip_team_prefix,
)
from .team_gate import current_team

# Project root: masim/interface/components/welcome.py → up 4 levels.
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
_LOGO_PATH = _PROJECT_ROOT / "logo.jpg"
_EXAMPLES_DIR = _PROJECT_ROOT / "examples"
_CUSTOMIZED_CONFIGS_DIR = _PROJECT_ROOT / "configs" / "CUSTOMIZED_SIMULATION"

# Bundle folders live under CUSTOMIZED_SIMULATION and follow the naming
# convention ``{project_slug}-{project_id}-{scenario_base}``. The id is a
# stable 8-char hex string (``uuid.uuid4().hex[:8]``). Scenario names in
# this codebase never contain hyphens (e.g. ``AnchoringEffect``,
# ``BlackMonday1987``); slugs may. The regex therefore anchors on the
# 8-hex id in the middle and matches the scenario as a trailing
# hyphen-free token, allowing the slug to be captured greedily.
_BUNDLE_NAME_RE = re.compile(r"^(.+)-([0-9a-fA-F]{8})-([^-]+)$")

# Regex for detecting a trailing ``-<8-hex>`` id suffix on a value in the
# ``Name your project`` input. When the user selects an existing project
# chip, the input is populated with ``{display_name}-{project_id}`` so the
# text matches the chip label; we then split the input back into name and
# id parts so folder creation stays clean (folders remain
# ``examples/<slug>/`` — the id never leaks into the folder name itself).
_ID_SUFFIX_RE = re.compile(r"^(.+)-([0-9a-fA-F]{8})$")


def _split_project_input(value: str) -> tuple[str, str]:
    """Split a project-input string into ``(name_part, id_part)``.

    If ``value`` ends with ``-<8-hex>``, the trailing token is treated as
    the id and the leading portion is the display name. Otherwise the
    whole value is the name and id is empty. Enables the input to mirror
    the chip label verbatim (``MYTest-b6beb998``) while keeping the
    slug/id logically distinct downstream.
    """
    text = (value or "").strip()
    if not text:
        return "", ""
    m = _ID_SUFFIX_RE.match(text)
    if m:
        return m.group(1), m.group(2).lower()
    return text, ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _slugify(name: str) -> str:
    """Convert a display name into a filesystem-safe folder name.

    Keeps letters, digits, spaces and hyphens; collapses whitespace to a
    single underscore; strips leading/trailing separators.
    """
    slug = name.strip()
    slug = re.sub(r"[^\w\s-]", "", slug)   # drop unsafe characters
    slug = re.sub(r"\s+", "_", slug)        # whitespace → underscore
    slug = re.sub(r"_+", "_", slug)         # collapse repeats
    return slug.strip("_-")


@st.cache_data(show_spinner=False)
def _logo_data_uri() -> Optional[str]:
    """Return the brand logo as a base64 data URI (or ``None`` if missing)."""
    if not _LOGO_PATH.exists():
        return None
    b64 = base64.b64encode(_LOGO_PATH.read_bytes()).decode("ascii")
    # The file carries a .jpg extension but is PNG-encoded content.
    return f"data:image/png;base64,{b64}"


def _list_existing_projects() -> list[dict[str, Any]]:
    """Return one row per (slug, project_id) pair discovered on disk.

    The **source of truth** is
    ``configs/CUSTOMIZED_SIMULATION/{slug}-{id}-{scenario}/`` — those
    folders are what the user has actually customized and can re-enter.
    Each discovered ``(slug, project_id)`` pair collapses into a single
    row that also records the list of scenarios that project has
    touched. The friendlier ``display_name`` is resolved from
    ``examples/<slug>/project_meta.json`` when available, otherwise
    the slug is used verbatim (with underscores rewritten as spaces
    for readability).

    Returns:
        List of dicts with keys ``display_name``, ``slug``,
        ``project_id``, ``scenarios`` (list[str]) and ``latest_mtime``
        (float), sorted by ``latest_mtime`` descending.
    """
    if not _CUSTOMIZED_CONFIGS_DIR.exists():
        return []

    # Filter: viewer sees their own bundles + legacy shared bundles.  The
    # team gate guarantees a non-empty ``viewer_team`` in the running app;
    # CLI / test callers may see everything (see :func:`is_visible_to_team`).
    viewer_team = current_team()

    # Grouping key now includes the owning team so a legacy shared bundle
    # and a team's forked customization don't collapse into a single row
    # (they may legitimately show different scenarios / mtimes and users
    # need to tell them apart).
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for entry in _CUSTOMIZED_CONFIGS_DIR.iterdir():
        if not entry.is_dir():
            continue
        match = _BUNDLE_NAME_RE.match(entry.name)
        if not match:
            continue
        raw_slug, pid, scenario = match.group(1), match.group(2), match.group(3)

        # Hide bundles owned by other teams.  ``owning_team_of`` returns
        # ``None`` for legacy (unprefixed) bundles, which the predicate
        # treats as universally visible for backward compatibility.
        if not is_visible_to_team(raw_slug, viewer_team):
            continue

        owner = owning_team_of(raw_slug) or ""
        # Strip the ``team-{team}-`` prefix from the slug so downstream
        # code (examples/<slug>/project_meta.json lookup, chip display,
        # bundle-name recomposition) sees the friendly project slug.
        display_slug = strip_team_prefix(raw_slug, owner)

        try:
            mtime = entry.stat().st_mtime
        except OSError:
            mtime = 0.0
        record = grouped.setdefault(
            (display_slug, pid, owner),
            {
                "slug": display_slug,
                "project_id": pid,
                "team": owner,               # "" for legacy / shared
                "is_legacy": owner == "",    # convenience flag for UI
                "scenarios": [],
                "latest_mtime": 0.0,
            },
        )
        record["scenarios"].append(scenario)
        if mtime > record["latest_mtime"]:
            record["latest_mtime"] = mtime

    result: list[dict[str, Any]] = []
    for (slug, pid, _owner), rec in grouped.items():
        # Prefer the friendlier project_name from examples/<slug>/meta;
        # fall back to the slug (underscores rewritten as spaces).  The
        # meta folder itself is NOT team-namespaced so this read works
        # for both legacy and team-owned rows using the stripped slug.
        display_name = slug.replace("_", " ")
        meta_path = _EXAMPLES_DIR / slug / "project_meta.json"
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                display_name = str(meta.get("project_name") or display_name)
            except (json.JSONDecodeError, OSError):
                pass
        result.append({
            "display_name": display_name,
            "slug": slug,
            "project_id": pid,
            "team": rec["team"],
            "is_legacy": rec["is_legacy"],
            "scenarios": sorted(set(rec["scenarios"])),
            "latest_mtime": rec["latest_mtime"],
        })

    result.sort(key=lambda p: p["latest_mtime"], reverse=True)
    return result


def create_run_environment(
    display_name: str,
    *,
    preferred_id: Optional[str] = None,
) -> Path:
    """Create ``examples/<slug>/`` as the base run environment.

    Also writes a small ``project_meta.json`` recording the display name,
    a stable 8-char ``project_id`` (used to compose customized-bundle folder
    names), and the creation timestamp. Idempotent: reuses the folder and
    meta if they already exist; back-fills a missing ``project_id`` on
    legacy projects created before the id was persisted.

    Args:
        display_name: The user-visible project name.
        preferred_id: Optional 8-char hex id to adopt (e.g. when reusing
            a project picked from the existing-projects chip list). Only
            applied when the on-disk meta has no id yet; existing ids are
            never overwritten.

    Returns:
        The created (or existing) project directory path.
    """
    slug = _slugify(display_name)
    project_dir = _EXAMPLES_DIR / slug
    project_dir.mkdir(parents=True, exist_ok=True)

    meta_path = project_dir / "project_meta.json"
    if meta_path.exists():
        # Back-fill project_id for legacy projects that predate the field.
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            meta = {}
        if not meta.get("project_id"):
            meta["project_id"] = preferred_id or uuid.uuid4().hex[:8]
            meta.setdefault("project_name", display_name.strip())
            meta.setdefault("slug", slug)
            meta.setdefault(
                "created_at", datetime.now().isoformat(timespec="seconds")
            )
            meta_path.write_text(
                json.dumps(meta, indent=2), encoding="utf-8"
            )
    else:
        meta_path.write_text(
            json.dumps(
                {
                    "project_name": display_name.strip(),
                    "slug": slug,
                    "project_id": preferred_id or uuid.uuid4().hex[:8],
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    return project_dir


def _read_project_id(slug: str) -> str:
    """Read the persisted ``project_id`` for a given slug, or empty string."""
    if not slug:
        return ""
    meta_path = _EXAMPLES_DIR / slug / "project_meta.json"
    if not meta_path.exists():
        return ""
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""
    return str(meta.get("project_id", ""))


# ---------------------------------------------------------------------------
# Scenario isolation: copy scenario into project folder
# ---------------------------------------------------------------------------

_CONFIGS_DIR = _PROJECT_ROOT / "configs"


def copy_scenario_to_project(project_slug: str, scenario_base: str) -> None:
    """Copy a scenario's configs and examples into the project-local dirs.

    Creates:
        - ``configs/{project_slug}/{scenario_base}/`` (all variant subdirs)
        - ``examples/{project_slug}/{scenario_base}/`` (skill code, markdown)

    Uses ``shutil.copytree(dirs_exist_ok=True)`` so re-running is idempotent.
    ``__pycache__`` directories are skipped.
    """
    def _ignore_pycache(directory: str, contents: list[str]) -> list[str]:
        return [c for c in contents if c == "__pycache__"]

    # --- configs ---
    src_configs = _CONFIGS_DIR / scenario_base
    dst_configs = _CONFIGS_DIR / project_slug / scenario_base
    if src_configs.exists():
        shutil.copytree(
            src_configs, dst_configs,
            ignore=_ignore_pycache, dirs_exist_ok=True,
        )

    # --- examples ---
    src_examples = _EXAMPLES_DIR / scenario_base
    dst_examples = _EXAMPLES_DIR / project_slug / scenario_base
    if src_examples.exists():
        shutil.copytree(
            src_examples, dst_examples,
            ignore=_ignore_pycache, dirs_exist_ok=True,
        )


def _inject_welcome_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {max-width: 880px; padding-top: 4.5rem;}
        .welcome-logo-wrap {text-align: center; margin: 0.5rem 0 0.25rem;}
        .welcome-logo-wrap img {
            width: 210px; height: 210px; object-fit: contain;
            filter: drop-shadow(0 6px 18px rgba(20, 32, 44, 0.12));
        }
        .welcome-title {
            text-align: center; font-size: 2.1rem; font-weight: 800;
            color: #17212b; letter-spacing: 0.01em; margin: 0.2rem 0 0.1rem;
        }
        .welcome-kicker {
            text-align: center; color: #287a6d; font-size: 0.8rem;
            font-weight: 750; text-transform: uppercase;
            letter-spacing: 0.14em; margin-bottom: 0.35rem;
        }
        .welcome-lead {
            text-align: center; color: #46535f; font-size: 1.0rem;
            line-height: 1.6; max-width: 620px; margin: 0.35rem auto 0.9rem;
        }
        .welcome-feature-row {
            display: flex; gap: 0.6rem; justify-content: center;
            flex-wrap: wrap; margin: 0.4rem 0 1.4rem;
        }
        .welcome-chip {
            font-size: 0.72rem; font-weight: 700; color: #41525f;
            background: #eef3f6; border: 1px solid #dde4ea;
            border-radius: 20px; padding: 0.28rem 0.75rem;
            letter-spacing: 0.02em;
        }
        .welcome-card-label {
            font-size: 0.78rem; font-weight: 750; color: #287a6d;
            text-transform: uppercase; letter-spacing: 0.08em;
            margin-bottom: 0.2rem;
        }
        /* Existing-projects picker (chips below the name input).
           Design targets: compact, refined typography; clear visual
           hierarchy between the (bold) project name and the (subtle,
           monospace) 8-char id; tight but breathable spacing. */
        .welcome-projects-hint {
            font-size: 0.66rem; color: #8892a0;
            text-transform: uppercase; letter-spacing: 0.09em;
            font-weight: 600; margin: 0.65rem 0 0.35rem 0;
        }
        /* Base chip button. Two-line max via wrap; consistent min-height
           keeps rows visually aligned. */
        [class*="st-key-welcome_pick_project_"] button {
            font-size: 0.72rem !important;
            padding: 4px 10px !important;
            min-height: 30px !important;
            height: auto !important;
            line-height: 1.3 !important;
            border-radius: 7px !important;
            border: 1px solid #e2e8ee !important;
            background: #fafbfc !important;
            color: #3a4653 !important;
            box-shadow: none !important;
            white-space: normal !important;
            word-break: break-word !important;
            text-align: center !important;
            width: 100% !important;
            transition: border-color 0.15s, background 0.15s, color 0.15s !important;
        }
        [class*="st-key-welcome_pick_project_"] button:hover {
            border-color: #2a5fa6 !important;
            background: #f0f5fb !important;
            color: #17212b !important;
        }
        /* Selected chip state: rendered as ``type="primary"`` so we can
           target it distinctly without a per-chip class. Streamlit tags
           the primary variant via both the ``kind`` attribute (older
           versions) and ``data-testid`` (newer versions); we cover both. */
        [class*="st-key-welcome_pick_project_"] button[kind="primary"],
        [class*="st-key-welcome_pick_project_"] button[data-testid*="primary"] {
            background: #2a5fa6 !important;
            border-color: #2a5fa6 !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            box-shadow: 0 0 0 2px rgba(42, 95, 166, 0.15) !important;
        }
        [class*="st-key-welcome_pick_project_"] button[kind="primary"]:hover,
        [class*="st-key-welcome_pick_project_"] button[data-testid*="primary"]:hover {
            background: #234f8f !important;
            border-color: #234f8f !important;
            color: #ffffff !important;
        }
        /* Streamlit wraps button label markdown in a <p>; the default
           <p> margin adds unwanted vertical whitespace inside chips. */
        [class*="st-key-welcome_pick_project_"] button p {
            margin: 0 !important;
            line-height: 1.3 !important;
        }
        /* The id portion of a chip label is rendered as inline code
           (backtick-wrapped in the markdown label) so it visually reads
           as metadata: monospace font, smaller size, softer color, and
           no code-block background. */
        [class*="st-key-welcome_pick_project_"] button code {
            background: transparent !important;
            padding: 0 !important;
            border: none !important;
            font-size: 0.66rem !important;
            font-weight: 500 !important;
            color: #8892a0 !important;
            letter-spacing: 0.02em !important;
        }
        [class*="st-key-welcome_pick_project_"] button[kind="primary"] code,
        [class*="st-key-welcome_pick_project_"] button[data-testid*="primary"] code {
            color: rgba(255, 255, 255, 0.82) !important;
        }
        /* Overflow caption below the chip grid. */
        .welcome-projects-more {
            font-size: 0.68rem; color: #8892a0;
            margin: 0.4rem 0 0 0; font-style: italic;
        }
        /* Mode cards */
        .mode-card {
            border: 1.5px solid #dde4ea; border-radius: 12px;
            padding: 1.2rem 1rem; text-align: center;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        .mode-card:hover {
            border-color: #287a6d;
            box-shadow: 0 2px 12px rgba(40, 122, 109, 0.10);
        }
        .mode-card-disabled {
            border: 1.5px solid #e8ecf0; border-radius: 12px;
            padding: 1.2rem 1rem; text-align: center;
            opacity: 0.5; cursor: not-allowed;
        }
        .mode-card-title {
            font-size: 1.05rem; font-weight: 750; color: #17212b;
            margin-bottom: 0.3rem;
        }
        .mode-card-desc {
            font-size: 0.82rem; color: #5c6b78; line-height: 1.5;
            margin-bottom: 0.7rem;
        }
        .mode-badge-soon {
            display: inline-block; font-size: 0.65rem; font-weight: 700;
            color: #8a9aab; background: #f0f3f6; border-radius: 10px;
            padding: 0.15rem 0.55rem; text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        /* Mode button colors via st-key targeting */
        .st-key-mode_experience button {
            background: #e7f3f0; border: 1.5px solid #b6d8d0;
            color: #1f6157; font-weight: 700;
        }
        .st-key-mode_experience button:hover {
            border-color: #1f6157; filter: brightness(0.97);
        }
        .st-key-mode_project button {
            background: #e8f0fb; border: 1.5px solid #bcd3f0;
            color: #2a5fa6; font-weight: 700;
        }
        .st-key-mode_project button:hover {
            border-color: #2a5fa6; filter: brightness(0.97);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------


def render_welcome() -> None:
    """Stage 0: mode selection + optional project-name capture.

    Three modes:
    - Experience: browse and run shipped scenarios directly (no project folder).
    - Project: create an isolated project folder, then customize scenarios.
    - Competition: placeholder (disabled).
    """
    _inject_welcome_styles()

    with st.sidebar:
        st.title("MASIM")
        st.caption("Multi-Agent Financial Simulation")
        st.markdown("---")
        st.markdown("**Stage 0.** Choose a mode")
        st.markdown("Stage 1. Pick a scenario")
        st.markdown("Stage 2. Run or customize")
        st.markdown("---")
        st.caption("MASIM v0.1.0")

    logo_uri = _logo_data_uri()
    if logo_uri:
        st.markdown(
            f'<div class="welcome-logo-wrap"><img src="{logo_uri}" '
            f'alt="MASIM logo"></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="welcome-kicker">Welcome</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="welcome-title">Multi-Agent Financial Simulation</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="welcome-lead">Simulate how heterogeneous investors '
        "interact under real market dynamics. Pick a scenario, assemble your "
        "agents, and watch the market unfold round by round.</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="welcome-feature-row">'
        '<span class="welcome-chip">40+ market scenarios</span>'
        '<span class="welcome-chip">Rule / LLM / RuleLLM engines</span>'
        '<span class="welcome-chip" style="opacity:0.5">RAG (暂不可用)</span>'
        '<span class="welcome-chip">Customizable investor roster</span>'
        "</div>",
        unsafe_allow_html=True,
    )

    # --- Mode cards -------------------------------------------------------
    col_exp, col_proj, col_comp = st.columns(3, gap="medium")

    with col_exp:
        st.markdown(
            '<div class="mode-card">'
            '<div class="mode-card-title">Explore Scenarios</div>'
            '<div class="mode-card-desc">'
            'Run pre-defined <b style="color:#1f6157">default</b> scenarios as-is. '
            "View results without any configuration."
            "</div></div>",
            unsafe_allow_html=True,
        )
        if st.button(
            "Enter Experience mode",
            key="mode_experience",
            width="stretch"
        ):
            st.session_state.mode = "experience"
            st.session_state.project_name = ""
            st.session_state.project_slug = ""
            st.session_state.project_dir = ""
            st.session_state.workflow_stage = "scenario_setup"
            st.rerun()

    with col_proj:
        st.markdown(
            '<div class="mode-card">'
            '<div class="mode-card-title">Build a Project</div>'
            '<div class="mode-card-desc">'
            '<b style="color:#2a5fa6">Customize</b> agents, edit configs. '
            "All work isolated to a project folder."
            "</div></div>",
            unsafe_allow_html=True,
        )
        if st.button(
            "Start a project",
            key="mode_project",
            width="stretch"
        ):
            st.session_state.mode = "project"
            st.rerun()

    with col_comp:
        st.markdown(
            '<div class="mode-card-disabled">'
            '<div class="mode-card-title">Arena</div>'
            '<div class="mode-card-desc">'
            "Competitive multi-agent tournaments."
            "</div>"
            '<span class="mode-badge-soon">coming soon</span>'
            "</div>",
            unsafe_allow_html=True,
        )
        st.button(
            "Arena mode",
            key="mode_competition",
            disabled=True,
            width="stretch"
        )

    # --- Project name input (shown only when Project mode is selected) ----
    if st.session_state.get("mode") == "project":
        st.markdown("---")
        _, mid, _ = st.columns([1, 3, 1])
        with mid:
            st.markdown(
                '<div class="welcome-card-label">Name your project</div>',
                unsafe_allow_html=True,
            )
            # A chip-click on an existing project stashes its display name
            # into this pending slot; we apply it to the widget's session_state
            # key BEFORE the text_input is instantiated so Streamlit picks up
            # the new value on the current run.
            #
            # IMPORTANT: We use ``session_state[key]`` as the SOLE source of
            # truth for the widget's value — no ``value=`` parameter is
            # passed. Combining ``value=`` with a pre-set session_state key
            # in Streamlit can silently prefer whichever the current version
            # deems the "newer" source, which caused chip clicks to not
            # visibly update the input on some renders.
            if "welcome_project_name_input" not in st.session_state:
                # First-render initialization from any externally-set project
                # name (e.g. one persisted from a prior session).
                st.session_state["welcome_project_name_input"] = (
                    st.session_state.get("project_name", "")
                )
            pending = st.session_state.pop("_welcome_pending_name", None)
            if pending is not None:
                st.session_state["welcome_project_name_input"] = pending
            pending_id = st.session_state.pop("_welcome_pending_id", None)
            if pending_id is not None:
                # Adopt the picked project's persisted id so downstream
                # bundle names line up with the on-disk folders.
                st.session_state["project_id"] = pending_id
            project_name = st.text_input(
                "Project name",
                placeholder="e.g. My First Market Study",
                label_visibility="collapsed",
                key="welcome_project_name_input",
            )
            st.caption(
                "This becomes the main identifier for this session. "
                "A run environment is created at `examples/<name>/`."
            )

            # --- Existing projects picker (live filter as user types) ---
            existing_projects = _list_existing_projects()
            # The input may hold either a bare name ("MyProj") or the
            # chip-style ``{name}-{id}`` ("MyProj-b6beb998") when a chip
            # is selected. All downstream logic below — filtering, slug
            # computation, existence checks, folder creation — must
            # operate on the name part only, while the id part (if any)
            # feeds ``preferred_id`` for id reuse.
            input_name_part, input_id_part = _split_project_input(
                project_name
            )
            if existing_projects:
                query = input_name_part.casefold()
                if query:
                    matches = [
                        p for p in existing_projects
                        if query in p["display_name"].casefold()
                        or query in p["slug"].casefold()
                    ]
                else:
                    matches = existing_projects
                hint_label = (
                    f"Existing projects matching \u201c{project_name}\u201d"
                    if query else "Existing projects"
                )
                st.markdown(
                    f'<div class="welcome-projects-hint">{hint_label} '
                    f'\u00b7 {len(matches)} of {len(existing_projects)}</div>',
                    unsafe_allow_html=True,
                )
                if not matches:
                    st.caption(
                        "No existing project matches \u2014 keep typing to "
                        "create a new one."
                    )
                else:
                    # Row-major grid: fixed 4 chips per row, wrapping into
                    # additional rows below. Using a fresh ``st.columns``
                    # call per row (rather than a single one indexed by
                    # ``idx % 4``) ensures chips lay out horizontally
                    # row-by-row instead of stacking vertically inside
                    # each column. Up to 12 chips are surfaced; more
                    # than that is a signal to refine the search.
                    visible = matches[:12]
                    per_row = 4
                    # Currently-selected chip is tracked as "slug::pid";
                    # a click on the same chip toggles it back off.
                    selected_key = st.session_state.get(
                        "_welcome_selected_project", ""
                    )
                    for row_start in range(0, len(visible), per_row):
                        row_slice = visible[row_start:row_start + per_row]
                        # Always allocate `per_row` slots so the last row
                        # stays left-aligned with the ones above (empty
                        # trailing slots are simply not filled).
                        chip_cols = st.columns(per_row, gap="small")
                        for idx, proj in enumerate(row_slice):
                            with chip_cols[idx]:
                                pid = proj.get("project_id") or ""
                                # Markdown label: bold name + inline-code
                                # id gives clear visual hierarchy between
                                # the human-readable label and the machine
                                # identifier. CSS above strips the code
                                # tag's default background and monospaces
                                # the id in a subtle gray.
                                chip_label = (
                                    f"**{proj['display_name']}** \u2009`{pid}`"
                                    if pid else f"**{proj['display_name']}**"
                                )
                                this_key = f"{proj['slug']}::{pid}"
                                is_selected = (selected_key == this_key)
                                if st.button(
                                    chip_label,
                                    key=f"welcome_pick_project_{proj['slug']}_{pid or 'nopid'}",
                                    type="primary" if is_selected else "secondary",
                                    help=(
                                        f"Reuse '{proj['display_name']}' "
                                        f"(examples/{proj['slug']}/). "
                                        "Click again to deselect."
                                    ),
                                    width="stretch",
                                ):
                                    if is_selected:
                                        # Toggle off: clear selection, wipe
                                        # the pending name (empty string is
                                        # applied to the widget key on the
                                        # next run), and drop the adopted id.
                                        st.session_state.pop(
                                            "_welcome_selected_project", None
                                        )
                                        st.session_state[
                                            "_welcome_pending_name"
                                        ] = ""
                                        st.session_state.pop("project_id", None)
                                    else:
                                        # Select (or switch to) this chip.
                                        # Populate the input with the full
                                        # chip-style label (``name-id``) so
                                        # the visible text mirrors the chip.
                                        st.session_state[
                                            "_welcome_selected_project"
                                        ] = this_key
                                        st.session_state[
                                            "_welcome_pending_name"
                                        ] = (
                                            f"{proj['display_name']}-{pid}"
                                            if pid else proj["display_name"]
                                        )
                                        if pid:
                                            st.session_state[
                                                "_welcome_pending_id"
                                            ] = pid
                                    st.rerun()
                    if len(matches) > len(visible):
                        st.markdown(
                            f'<div class="welcome-projects-more">'
                            f'\u2026 {len(matches) - len(visible)} more '
                            'hidden \u2014 refine the name to narrow down.'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                    # Auto-deselect when the user has diverged from the
                    # selected chip by typing manually. The invariant is
                    # "chip selected ⇔ input == '<display_name>-<pid>'"
                    # (or bare display_name when pid is missing). Any
                    # divergence — including removing the id suffix —
                    # means the user is starting a fresh project, so we
                    # drop selection and the adopted id.
                    if selected_key:
                        sel_slug, _, sel_pid = selected_key.partition("::")
                        sel_display = next(
                            (
                                p["display_name"]
                                for p in existing_projects
                                if p["slug"] == sel_slug
                                and p["project_id"] == sel_pid
                            ),
                            None,
                        )
                        if sel_display is not None:
                            expected = (
                                f"{sel_display}-{sel_pid}"
                                if sel_pid else sel_display
                            )
                            if (project_name or "").strip() != expected:
                                st.session_state.pop(
                                    "_welcome_selected_project", None
                                )
                                st.session_state.pop("project_id", None)

            # ``project_name`` may hold ``{name}-{id}``; slugify and
            # folder-existence must operate on the name part only.
            slug_source, id_from_input = _split_project_input(project_name)
            slug_preview = _slugify(slug_source) if slug_source else ""
            if slug_source and not slug_preview:
                st.warning(
                    "Please use at least one letter or number in the name."
                )
            elif slug_preview:
                existing = (_EXAMPLES_DIR / slug_preview).exists()
                note = (
                    "will reuse existing folder" if existing
                    else "will be created"
                )
                st.caption(f"\u2192 `examples/{slug_preview}/` ({note})")

            if st.button(
                "Create & continue \u2192",
                type="primary",
                width="stretch",
                disabled=not slug_preview,
            ):
                # Prefer the id embedded in the input suffix (from chip
                # selection) so downstream folder naming matches the
                # on-disk CUSTOMIZED_SIMULATION bundles exactly. Fall back
                # to any id already carried in session state.
                adopted_id = id_from_input or st.session_state.get(
                    "project_id"
                ) or None
                project_dir = create_run_environment(
                    slug_source, preferred_id=adopted_id
                )
                st.session_state.project_name = slug_source
                st.session_state.project_slug = slug_preview
                st.session_state.project_dir = str(project_dir)
                # Re-read the id from disk so session state always matches
                # what create_run_environment persisted — the definitive
                # value used by downstream bundle folder naming.
                st.session_state["project_id"] = _read_project_id(slug_preview)
                st.session_state.workflow_stage = "scenario_setup"
                st.rerun()
