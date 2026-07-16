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
from typing import Optional

import streamlit as st

# Project root: masim/interface/components/welcome.py → up 4 levels.
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
_LOGO_PATH = _PROJECT_ROOT / "logo.jpg"
_EXAMPLES_DIR = _PROJECT_ROOT / "examples"


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


def _list_existing_projects() -> list[dict[str, str]]:
    """Return metadata for every existing project under ``examples/``.

    A directory is treated as a project iff it contains a
    ``project_meta.json`` file. The list is sorted by ``created_at``
    descending (most recent first) with a slug fallback for entries
    that lack a timestamp.

    Returns:
        List of dicts with keys ``display_name``, ``slug``, ``created_at``.
    """
    if not _EXAMPLES_DIR.exists():
        return []
    projects: list[dict[str, str]] = []
    for entry in _EXAMPLES_DIR.iterdir():
        if not entry.is_dir():
            continue
        meta_path = entry / "project_meta.json"
        if not meta_path.exists():
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        projects.append(
            {
                "display_name": str(meta.get("project_name") or entry.name),
                "slug": str(meta.get("slug") or entry.name),
                "created_at": str(meta.get("created_at", "")),
            }
        )
    projects.sort(key=lambda p: p["created_at"], reverse=True)
    return projects


def create_run_environment(display_name: str) -> Path:
    """Create ``examples/<slug>/`` as the base run environment.

    Also writes a small ``project_meta.json`` recording the display name and
    creation timestamp. Idempotent: reuses the folder if it already exists.

    Returns:
        The created (or existing) project directory path.
    """
    slug = _slugify(display_name)
    project_dir = _EXAMPLES_DIR / slug
    project_dir.mkdir(parents=True, exist_ok=True)

    meta_path = project_dir / "project_meta.json"
    if not meta_path.exists():
        meta_path.write_text(
            json.dumps(
                {
                    "project_name": display_name.strip(),
                    "slug": slug,
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    return project_dir


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
        /* Existing-projects picker (chips below the name input) */
        .welcome-projects-hint {
            font-size: 0.72rem; color: #7a8794;
            text-transform: uppercase; letter-spacing: 0.06em;
            font-weight: 700; margin: 0.35rem 0 0.15rem 0;
        }
        [class*="st-key-welcome_pick_project_"] button {
            font-size: 0.78rem !important;
            padding: 3px 10px !important;
            min-height: 0 !important;
            height: auto !important;
            line-height: 1.4 !important;
            border-radius: 999px !important;
            border: 1px solid #d5dde5 !important;
            background: #f6f8fa !important;
            color: #2a3742 !important;
            box-shadow: none !important;
            white-space: nowrap;
        }
        [class*="st-key-welcome_pick_project_"] button:hover {
            border-color: #2a5fa6 !important;
            background: #eaf0f8 !important;
            color: #17212b !important;
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
        '<span class="welcome-chip">Rule / LLM / RuleLLM / RAG engines</span>'
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
            pending = st.session_state.pop("_welcome_pending_name", None)
            if pending is not None:
                st.session_state["welcome_project_name_input"] = pending
            default_name = st.session_state.get("project_name", "")
            project_name = st.text_input(
                "Project name",
                value=default_name,
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
            if existing_projects:
                query = (project_name or "").strip().casefold()
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
                    # Show up to 8 matches as clickable chips, most recent first.
                    visible = matches[:8]
                    chip_cols = st.columns(min(len(visible), 4), gap="small")
                    for idx, proj in enumerate(visible):
                        col = chip_cols[idx % len(chip_cols)]
                        with col:
                            if st.button(
                                proj["display_name"],
                                key=f"welcome_pick_project_{proj['slug']}",
                                help=f"Reuse project '{proj['display_name']}' (examples/{proj['slug']}/)",
                                width="stretch",
                            ):
                                # Stash the pick and rerun; the pending slot
                                # will be applied to the text_input on the
                                # next run before the widget is re-created.
                                st.session_state["_welcome_pending_name"] = (
                                    proj["display_name"]
                                )
                                st.rerun()
                    if len(matches) > len(visible):
                        st.caption(
                            f"\u2026 {len(matches) - len(visible)} more "
                            "hidden \u2014 refine the name to narrow down."
                        )

            slug_preview = _slugify(project_name) if project_name else ""
            if project_name and not slug_preview:
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
                project_dir = create_run_environment(project_name)
                st.session_state.project_name = project_name.strip()
                st.session_state.project_slug = slug_preview
                st.session_state.project_dir = str(project_dir)
                # Generate a short unique ID for this project session.
                # Used to name customized bundle folders:
                # {project_name}-{scenario}-{project_id}
                if not st.session_state.get("project_id"):
                    st.session_state["project_id"] = uuid.uuid4().hex[:8]
                st.session_state.workflow_stage = "scenario_setup"
                st.rerun()
