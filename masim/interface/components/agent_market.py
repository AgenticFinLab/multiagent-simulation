"""Agent Market and experiment setup workflow for the Streamlit interface."""

from __future__ import annotations

import base64
import html
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote

import streamlit as st

from ..config_loader import (
    discover_scenario_groups,
    get_scenario_info,
    scenario_display_name,
)
from ..customized import (
    CustomizedAgentSelection,
    is_archetype_mapped,
    load_default_prompts,
    parse_parameters_file,
    write_customized_bundle,
)
from ..customized.handbook_params import ParamSpec


PROJECT_ROOT = Path(__file__).resolve().parents[3]
AGENT_POOL_ROOT = PROJECT_ROOT / "examples" / "AGENT_POOL"
IMAGE_ROOT = AGENT_POOL_ROOT / "agent_images"
PROFILE_ROOT = AGENT_POOL_ROOT / "ExtractedExampleInvestors" / "unique"
CATALOG_PATH = IMAGE_ROOT / "agent_avatar_map.json"
VARIANT_ORDER = {"Rule": 0, "LLM": 1, "RuleLLM": 2, "Rag": 3}


def _agent_catalog_signature() -> tuple[tuple[str, int], ...]:
    """Return a lightweight cache key for avatar metadata and PNG changes."""
    paths = []
    if CATALOG_PATH.exists():
        paths.append(CATALOG_PATH)
    png_root = IMAGE_ROOT / "png"
    if png_root.exists():
        paths.extend(sorted(png_root.glob("*.png")))
    return tuple((str(path), path.stat().st_mtime_ns) for path in paths)


def render_entry_choice() -> None:
    """Render the landing chooser: pre-built scenario vs. customized portfolio.

    User-facing copy only — no file paths, module names, or other code-level
    details are exposed. Live counts are computed from the scenario registry
    and agent catalog so the page reflects what is actually runnable.
    """
    _inject_market_styles()

    # Live counts driving the headline copy.
    groups = discover_scenario_groups()
    scenario_count = len(groups)
    variant_count = sum(len(v) for v in groups.values())
    try:
        agent_count = len(load_agent_catalog(_agent_catalog_signature()))
    except Exception:
        agent_count = 0

    # Friendly preview: a few representative scenario names, spaced out.
    preview_names = [
        re.sub(r"(?<!^)(?=[A-Z])", " ", name).strip()
        for name in list(groups.keys())[:6]
    ]
    if scenario_count > len(preview_names):
        preview_names.append(f"and {scenario_count - len(preview_names)} more")
    preview_text = ", ".join(preview_names) if preview_names else "—"

    with st.sidebar:
        st.title("MASIM")
        st.caption("Investment workflow")
        st.markdown("---")
        st.markdown("**Welcome**")
        st.caption("Choose how you want to start")
        st.markdown("---")
        st.caption("MASIM v0.1.0")

    st.markdown('<div class="market-kicker">Welcome</div>', unsafe_allow_html=True)
    st.title("How would you like to start?")
    st.write(
        "Pick a ready-made market scenario and run it right away, or design "
        "your own investor lineup before launching a simulation."
    )

    metric_cols = st.columns(3)
    metric_cols[0].metric("Market scenarios", scenario_count)
    metric_cols[1].metric("Runnable variants", variant_count)
    metric_cols[2].metric("Investor profiles", agent_count)

    st.markdown("&nbsp;", unsafe_allow_html=True)

    existing_col, custom_col = st.columns(2, gap="large")

    with existing_col:
        st.subheader("📊 Run a ready-made scenario")
        st.markdown(
            f"- **{scenario_count} market scenarios** ready to launch\n"
            f"- **{variant_count} agent-strategy variants** to compare\n"
            "- No portfolio setup required — jump straight in\n"
            "- Best for: exploring built-in case studies"
        )
        st.caption(f"Includes: {preview_text}")
        if st.button(
            "Run a ready-made scenario",
            type="primary",
            use_container_width=True,
            key="entry_use_existing",
        ):
            st.session_state.selected_market_agents = []
            st.session_state.workflow_stage = "workspace"
            st.session_state.current_page = "Simulation"
            st.rerun()

    with custom_col:
        st.subheader("🎨 Design your own simulation")
        st.markdown(
            f"- Pick from **{agent_count} investor profiles** with distinct styles\n"
            "- Build a custom portfolio of market participants\n"
            "- Then choose a scenario to run them through\n"
            "- Best for: bringing your own simulation idea to life"
        )
        st.caption("Select investors first, customize parameters (optional), then a scenario to simulate.")
        if st.button(
            "Design your own simulation",
            use_container_width=True,
            key="entry_customize",
        ):
            st.session_state.workflow_stage = "agents"
            st.rerun()


def _field_from_summary_table(markdown: str, field: str) -> str:
    pattern = rf"^\|\s*{re.escape(field)}\s*\|\s*(.*?)\s*\|\s*$"
    match = re.search(pattern, markdown, flags=re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else ""


VARIANT_DISPLAY = {"Rule": "Rule", "LLM": "LLM", "RuleLLM": "RuleLLM", "Rag": "RAG"}


def _profile_intro(markdown: str, display_name: str) -> str:
    """Build a short hover description focused on theory and role.

    The hover always leads with a ``Design Theory:`` label so users instantly
    recognise what they are reading. When no theoretical basis can be
    parsed, we fall back to the archetype description alone.
    """
    archetype = _field_from_summary_table(markdown, "Archetype")
    theory = _theory_basis(markdown)
    role = archetype or display_name
    if theory:
        return f"Design Theory: {theory}. Role: {role}."
    return f"Design Theory: —. Role: {role}."


def _available_variants(markdown: str) -> list[str]:
    """Detect which decision-engine variants this agent ships with.

    The project organises each scenario into ``Rule/``, ``LLM/``,
    ``RuleLLM/`` and ``Rag/`` subdirectories. ``Rule`` is the foundational
    engine and is always present, so we include it unconditionally. The
    remaining engines are detected via explicit markers in the
    "Consolidated Financial Theory" section of the agent's profile.
    Returned variants follow the project-wide order: Rule -> LLM ->
    RuleLLM -> Rag.
    """
    variants: list[str] = ["Rule"]
    if not markdown:
        return variants
    if re.search(r"\bLLM[- ][Dd]riven\b", markdown):
        variants.append("LLM")
    if re.search(r"\bRuleLLM\b|\bHybrid:", markdown):
        variants.append("RuleLLM")
    if re.search(r"\bRAG[- ][Aa]ugmented\b|\bRAG[- ][Dd]riven\b", markdown):
        variants.append("Rag")
    return variants


def _image_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    mime = "image/png" if path.suffix.lower() == ".png" else "image/svg+xml"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _theory_basis(markdown: str) -> str:
    """Extract a short theoretical-basis phrase from a profile markdown.

    Scans the "Consolidated Financial Theory" bullets for the first line
    that starts with ``- Theoretical basis: ...``. Strips boilerplate prefixes
    (e.g. ``simulation-bases.md Section X.X``) and trailing punctuation so the
    result is a short, user-readable citation or mechanism description such
    as ``Tversky & Kahneman, 1974`` or
    ``Brady Commission (1988) program trading feedback loops``.

    Returns an empty string when no such line exists.
    """
    if not markdown:
        return ""
    for match in re.finditer(r"-\s*Theoretical\s+basis:\s*(.+)", markdown, flags=re.IGNORECASE):
        text = match.group(1).strip()
        # Drop leading 'simulation-bases.md Section X.Y' boilerplate.
        text = re.sub(
            r"^simulation-bases\.md\s+Section\s+[\d.]+\s*[-—]?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )
        # Strip any leading list marker carried over from the source bullet.
        text = re.sub(r"^[-–—•]\s*", "", text)
        # Truncate at the first semicolon — keep one citation clause.
        # Splitting on '.' would break "et al." and year-period citations.
        text = text.split(";", 1)[0].strip()
        # Trim trailing punctuation and balance any unmatched parentheses.
        text = text.rstrip(".,; ")
        opens = text.count("(")
        closes = text.count(")")
        while closes > opens and text.endswith(")"):
            text = text[:-1].rstrip(".,; ")
            closes -= 1
        while opens > closes and text.startswith("("):
            text = text[1:].lstrip()
            opens -= 1
        if text:
            return text
    return ""


@st.cache_data(show_spinner=False)
def load_agent_catalog(_cache_signature: tuple[tuple[str, int], ...] | None = None) -> list[dict[str, Any]]:
    """Load avatar metadata and complete Markdown profiles."""
    if CATALOG_PATH.exists():
        raw_items = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    else:
        raw_items = [
            {
                "agent_type": path.stem,
                "display_name": re.sub(r"(?<!^)(?=[A-Z])", " ", path.stem),
                "image_path": f"png/{path.name}",
                "source_profile": str(PROFILE_ROOT / f"{path.stem}.md"),
            }
            for path in sorted((IMAGE_ROOT / "png").glob("*.png"))
        ]

    catalog: list[dict[str, Any]] = []
    for item in raw_items:
        agent_type = item["agent_type"]
        display_name = item.get("display_name", agent_type)
        image_path = IMAGE_ROOT / item.get("image_path", f"png/{agent_type}.png")

        source_value = item.get("source_profile", "")
        source_path = Path(source_value)
        if not source_path.is_absolute():
            source_path = (IMAGE_ROOT / source_path).resolve()
        if not source_path.exists():
            source_path = PROFILE_ROOT / f"{agent_type}.md"

        markdown = source_path.read_text(encoding="utf-8") if source_path.exists() else ""
        catalog.append(
            {
                **item,
                "agent_type": agent_type,
                "display_name": display_name,
                "image_file": str(image_path),
                "image_uri": _image_data_uri(image_path),
                "profile_file": str(source_path),
                "profile_markdown": markdown,
                "intro": _profile_intro(markdown, display_name),
                "archetype": _field_from_summary_table(markdown, "Archetype")
                or display_name,
                "scenarios": _field_from_summary_table(markdown, "Scenarios"),
                "theory_basis": _theory_basis(markdown),
                "variants": _available_variants(markdown),
            }
        )
    return catalog


def _query_agent() -> str:
    if hasattr(st, "query_params"):
        value = st.query_params.get("agent", "")
        return value[0] if isinstance(value, list) else value
    values = st.experimental_get_query_params()
    return values.get("agent", [""])[0]


def _clear_query_agent() -> None:
    if hasattr(st, "query_params"):
        st.query_params.clear()
    else:
        st.experimental_set_query_params()


def _selected_types(catalog: list[dict[str, Any]]) -> list[str]:
    return [
        agent["agent_type"]
        for agent in catalog
        if st.session_state.get(f"market_agent_{agent['agent_type']}", False)
    ]


def _inject_market_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {max-width: 1240px; padding-top: 4.5rem;}
        .market-kicker {
            color: #287a6d; font-size: 0.78rem; font-weight: 750;
            text-transform: uppercase; letter-spacing: 0;
            margin-bottom: 0.35rem;
        }
        .agent-card {
            border: 1px solid #dce2e8; border-radius: 8px;
            background: #ffffff; overflow: hidden; min-height: 220px;
            box-shadow: 0 1px 2px rgba(20, 32, 44, 0.06);
        }
        .agent-image-link {
            display: block; position: relative; aspect-ratio: 1 / 1;
            overflow: hidden; background: #eef3f6;
        }
        .agent-image-link img {
            width: 100%; height: 100%; object-fit: cover; display: block;
            transition: transform 160ms ease;
        }
        .agent-image-link:hover img {transform: scale(1.025);}
        .agent-hover {
            position: absolute; inset: auto 0 0 0; padding: 0.75rem;
            background: rgba(17, 25, 35, 0.92); color: #f7fafc;
            font-size: 0.74rem; line-height: 1.42;
            opacity: 0; transform: translateY(6px);
            transition: opacity 150ms ease, transform 150ms ease;
        }
        .agent-image-link:hover .agent-hover,
        .agent-image-link:focus .agent-hover {opacity: 1; transform: translateY(0);}
        .agent-card-copy {padding: 0.55rem 0.6rem 0.6rem;}
        .agent-card-name {font-size: 0.8rem; font-weight: 700; color: #17212b; line-height: 1.2;}
        .agent-card-meta {
            font-size: 0.66rem; color: #68737d; margin-top: 0.18rem;
            line-height: 1.25;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
            overflow: hidden; text-overflow: ellipsis;
        }
        .agent-variants {
            display: flex; gap: 0.2rem; flex-wrap: wrap;
            margin-top: 0.32rem;
        }
        .agent-variant-chip {
            font-size: 0.56rem; font-weight: 700; line-height: 1.4;
            padding: 0.04rem 0.34rem;
            border-radius: 8px;
            background: #eef3f6; color: #41525f;
            border: 1px solid #dde4ea;
            letter-spacing: 0.03em;
        }
        .agent-variants-label {
            font-size: 0.56rem; color: #8a96a3; letter-spacing: 0.04em;
            text-transform: uppercase; margin-top: 0.32rem;
            display: block;
        }
        .agent-status-chip {
            display: inline-block; margin-top: 0.32rem;
            font-size: 0.6rem; font-weight: 700; line-height: 1.4;
            padding: 0.06rem 0.4rem; border-radius: 8px;
            letter-spacing: 0.02em;
        }
        .agent-status-chip.selected {
            background: #e7f3f0; color: #1f6157;
            border: 1px solid #b6d8d0;
        }
        .agent-status-chip.muted {
            background: #f3f5f7; color: #8a96a3;
            border: 1px solid #e1e6ea;
        }
        .agent-card.active {
            border-color: #287a6d;
            box-shadow: 0 0 0 2px rgba(40, 122, 109, 0.18);
        }
        .profile-banner {
            border-left: 4px solid #287a6d; background: #f3f7f6;
            padding: 0.9rem 1rem; margin: 0.4rem 0 1rem;
        }
        .portfolio-strip {
            display: flex; gap: 0.45rem; flex-wrap: wrap;
            padding: 0.5rem 0 0.25rem;
        }
        .portfolio-chip {
            display: inline-flex; align-items: center; gap: 0.38rem;
            border: 1px solid #dce2e8; border-radius: 6px;
            padding: 0.28rem 0.48rem; background: #fff;
            color: #26323d; font-size: 0.74rem;
        }
        .portfolio-chip img {width: 24px; height: 24px; border-radius: 4px; object-fit: cover;}
        /* Teal accent for the "Design your own simulation" entry button. */
        .st-key-entry_customize button {
            background-color: #287a6d !important;
            color: #ffffff !important;
            border: 1px solid #287a6d !important;
        }
        .st-key-entry_customize button:hover {
            background-color: #1f6157 !important;
            border-color: #1f6157 !important;
        }
        .st-key-entry_customize button:focus,
        .st-key-entry_customize button:active {
            background-color: #1f6157 !important;
            border-color: #1f6157 !important;
            box-shadow: 0 0 0 2px rgba(40, 122, 109, 0.35) !important;
        }
        @media (max-width: 700px) {
            .block-container {padding-top: 3.75rem;}
            .agent-card {min-height: 230px;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_workflow_sidebar(step: int, selected_count: int) -> None:
    with st.sidebar:
        st.title("MASIM")
        st.caption("Investment workflow")
        st.markdown("---")
        st.markdown(f"**{'1. Agent Market' if step == 1 else '✓ Agent Market'}**")
        st.caption(f"{selected_count} agents selected")
        st.markdown(f"**{'2. Simulation Setup' if step == 2 else '2. Simulation Setup'}**")
        st.markdown("---")
        st.caption("MASIM v0.1.0")


def render_back_to_start_bar(
    *,
    key_suffix: str,
    reset_runtime: bool = False,
) -> None:
    """Render a small right-aligned "Back to start" button at the top of
    the main content area, available on every post-entry page.

    Args:
        key_suffix: caller-specific suffix to keep widget keys unique across
            pages that may render in the same session (e.g. ``"agents"``,
            ``"setup"``, ``"workspace"``).
        reset_runtime: when True, also clear simulation/replay state so the
            user returns to a clean welcome page after a run was started.
    """
    btn_col, _ = st.columns([1, 6])
    with btn_col:
        if st.button(
            "← Back to start",
            key=f"main_back_to_start_{key_suffix}",
            use_container_width=True,
            help="Return to the welcome page.",
        ):
            st.session_state.workflow_stage = "entry"
            if reset_runtime:
                st.session_state.simulation_running = False
                st.session_state.simulation_completed = False
                st.session_state.replay_active = False
                st.session_state.replay_rounds = []
                st.session_state.replay_index = 0
                st.session_state.viewed_round_idx = 0
                st.session_state.sys_messages = []
            st.rerun()


def _render_profile(agent: dict[str, Any]) -> None:
    st.markdown('<div id="agent-profile"></div>', unsafe_allow_html=True)
    heading, close = st.columns([5, 1])
    with heading:
        st.markdown('<div class="market-kicker">Agent profile</div>', unsafe_allow_html=True)
        st.subheader(agent["display_name"])
    with close:
        if st.button("Close", use_container_width=True, key="close_market_profile"):
            _clear_query_agent()
            st.rerun()

    image_col, profile_col = st.columns([1, 2.8], gap="large")
    with image_col:
        st.image(agent["image_file"], use_container_width=True)
        st.caption(agent["agent_type"])
    with profile_col:
        st.markdown(
            f'<div class="profile-banner">{html.escape(agent["intro"])}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(agent["profile_markdown"] or "Profile content is unavailable.")
    st.divider()


def _load_param_specs(agent: dict[str, Any]) -> list[ParamSpec]:
    """Return the parsed Parameters table for an agent (cached on disk mtime)."""
    profile_path = agent.get("profile_file")
    if not profile_path:
        return []
    return parse_parameters_file(profile_path)


def _render_param_panel(agent: dict[str, Any]) -> None:
    """Render the left-side editable parameter panel for an active agent.

    Behaviour:
    - Engine selector (segmented control) at the top.
    - One widget per parameter row: number_input for numerics, selectbox
      for enums, text_input as a fallback.
    - "Reset to defaults" reverts the agent's edits to the handbook
      defaults; "Add to portfolio" persists params and ticks the
      Add-to-Market checkbox in one atomic action.
    """
    agent_type = agent["agent_type"]
    # Always expose all four standard decision engines. Engines whose
    # concrete classes have not been wired yet are still shown so the
    # user can preview parameters and prompts; the bundle writer will
    # surface a TODO marker when a binding is missing.
    all_engines = ["Rule", "LLM", "RuleLLM", "Rag"]
    detected = set(agent.get("variants", []) or ["Rule"])
    specs = _load_param_specs(agent)

    st.markdown('<div class="market-kicker">Customize</div>', unsafe_allow_html=True)
    st.subheader(agent["display_name"])
    st.caption(agent["agent_type"])

    # ---- Engine selector ------------------------------------------------
    engine_key = f"market_engine_{agent_type}"
    if engine_key not in st.session_state or st.session_state[engine_key] not in all_engines:
        # Prefer the first detected engine (usually Rule) on first render.
        st.session_state[engine_key] = next(
            (e for e in all_engines if e in detected), all_engines[0]
        )

    def _engine_label(v: str) -> str:
        base = VARIANT_DISPLAY.get(v, v)
        return base if v in detected else f"{base} (preview)"

    st.segmented_control(
        "Decision engine",
        options=all_engines,
        format_func=_engine_label,
        key=engine_key,
        help=(
            "Choose the decision-making engine. Rule = deterministic logic; "
            "LLM = persona-driven prompt; RuleLLM = hybrid; RAG = "
            "retrieval-augmented. Engines marked '(preview)' are not yet "
            "shipped with a concrete class for this archetype — your "
            "customization will be saved but the bundle writer will mark "
            "them as TODO until the binding lands."
        ),
    )
    engine = st.session_state[engine_key]

    if engine not in detected:
        st.info(
            f"`{engine}` is in preview for this archetype — parameters and "
            f"prompts you set here are persisted, but the generated bundle "
            f"will need a class binding before it can run."
        )

    if not is_archetype_mapped(agent_type):
        st.warning(
            "This archetype does not yet have a registered class binding. "
            "You can still edit parameters; the generated bundle will "
            "include a `TODO_unmapped_archetype` marker that must be "
            "resolved before launch."
        )

    if not specs:
        st.info(
            "This agent's handbook has no `## Parameters` table; "
            "defaults will be used as-is."
        )

    # ---- Per-parameter widgets -----------------------------------------
    persisted = (
        st.session_state.setdefault("customized_params", {})
        .setdefault(agent_type, {})
        .setdefault(engine, {})
    )
    edited: dict[str, Any] = {}
    with st.container():
        for spec in specs:
            value = _render_param_widget(agent_type, engine, spec, persisted)
            edited[spec.symbol] = value

    # ---- LLM-engine extras (prompt + hyperparameters) ------------------
    if engine in {"LLM", "RuleLLM", "Rag"}:
        _render_llm_extras(agent, agent_type, engine, persisted, edited)

    # ---- Action buttons -------------------------------------------------
    st.divider()
    btn_add, btn_reset, btn_close = st.columns([2, 1, 1])
    with btn_add:
        already_in = bool(st.session_state.get(f"market_agent_{agent_type}", False))
        primary_label = "Update in portfolio" if already_in else "Add to portfolio"
        if st.button(primary_label, type="primary", use_container_width=True,
                     key=f"customized_add_{agent_type}"):
            persisted.clear()
            persisted.update(edited)
            st.session_state[f"market_agent_{agent_type}"] = True
            st.toast(f"{agent['display_name']} → portfolio", icon="✓")
            st.rerun()
    with btn_reset:
        if st.button("Reset", use_container_width=True,
                     key=f"customized_reset_{agent_type}"):
            persisted.clear()
            for sub_key in list(st.session_state.keys()):
                if sub_key.startswith(f"customized_input_{agent_type}_{engine}_"):
                    del st.session_state[sub_key]
            st.rerun()
    with btn_close:
        if st.button("Close", use_container_width=True,
                     key=f"customized_close_{agent_type}"):
            st.session_state.customized_active_agent = None
            st.rerun()


def _render_param_widget(
    agent_type: str,
    engine: str,
    spec: ParamSpec,
    persisted: dict[str, Any],
) -> Any:
    """Render one editable widget for a parameter spec, return its value.

    UX rule: the row shows ONLY the human-readable label (and the
    widget itself).  Every piece of metadata — description, default,
    range, units, sensitivity, impact, raw config key, source — lives
    inside the widget's ``help`` tooltip and is revealed on demand
    when the user hovers the ``?`` icon Streamlit renders next to the
    label.  No gray captions are emitted below the widget.
    """
    widget_key = f"customized_input_{agent_type}_{engine}_{spec.symbol}"
    initial = persisted.get(spec.symbol, spec.default_value)
    label_main = spec.display_label
    help_text = _compose_help(spec)

    if spec.kind == "enum":
        options = spec.enum_values or []
        try:
            index = options.index(initial) if initial in options else 0
        except ValueError:
            index = 0
        return st.selectbox(
            label_main,
            options=options or [str(initial or "")],
            index=index,
            key=widget_key,
            help=help_text,
        )

    if spec.kind == "int":
        # Streamlit's number_input rejects None; coerce missing values
        # to 0 so the widget can render.
        coerced = int(initial) if isinstance(initial, (int, float)) else 0
        kwargs: dict[str, Any] = {"step": 1, "key": widget_key, "help": help_text}
        if spec.numeric_low is not None and spec.numeric_low != float("-inf"):
            kwargs["min_value"] = int(spec.numeric_low)
        if spec.numeric_high is not None and spec.numeric_high != float("inf"):
            kwargs["max_value"] = int(spec.numeric_high)
        return st.number_input(label_main, value=coerced, **kwargs)

    if spec.kind == "float":
        coerced_f = float(initial) if isinstance(initial, (int, float)) else 0.0
        kwargs = {"key": widget_key, "help": help_text, "format": "%.6g"}
        if spec.numeric_low is not None and spec.numeric_low != float("-inf"):
            kwargs["min_value"] = float(spec.numeric_low)
        if spec.numeric_high is not None and spec.numeric_high != float("inf"):
            kwargs["max_value"] = float(spec.numeric_high)
        return st.number_input(label_main, value=coerced_f, **kwargs)

    # Free-text fallback (covers list-valued defaults like
    # ``[-0.01, -0.02, ...]`` and Greek-letter symbols).
    return st.text_input(
        label_main,
        value=str(initial) if initial is not None else "",
        key=widget_key,
        help=help_text,
    )


def _render_llm_extras(
    agent: dict[str, Any],
    agent_type: str,
    engine: str,
    persisted: dict[str, Any],
    edited: dict[str, Any],
) -> None:
    """Render LLM hyperparameters and editable prompt textareas.

    Two prompts are exposed because every LLM player in this codebase
    follows the same two-message contract: a *system prompt* that
    defines the persona once, and a *user prompt template* that is
    rendered every round with the current market state injected via
    ``str.format(**vars)``.  Both are editable here; both are persisted
    under reserved sentinel keys so they round-trip with the rest of
    the agent's customized params:

        ``__llm_lm_name__``, ``__llm_temperature__``, ``__llm_max_tokens__``,
        ``__llm_system_prompt__``, ``__llm_user_prompt__``.
    """
    st.markdown("---")
    st.markdown(f"**LLM settings** — *{VARIANT_DISPLAY.get(engine, engine)} engine*")

    lm_key = f"customized_llm_lm_{agent_type}_{engine}"
    temp_key = f"customized_llm_temp_{agent_type}_{engine}"
    tok_key = f"customized_llm_tokens_{agent_type}_{engine}"
    sys_key = f"customized_llm_sysprompt_{agent_type}_{engine}"
    usr_key = f"customized_llm_userprompt_{agent_type}_{engine}"

    lm_default = persisted.get("__llm_lm_name__", "ark/doubao-seed-2-0-mini-260428")
    temp_default = float(persisted.get("__llm_temperature__", 0.7))
    tok_default = int(persisted.get("__llm_max_tokens__", 512))
    sys_default = str(persisted.get("__llm_system_prompt__", ""))
    usr_default = str(persisted.get("__llm_user_prompt__", ""))

    # Pre-fill the textareas with the shipped default prompt so users
    # can SEE the actual prompt the agent will run with, instead of
    # staring at an empty box. ``shipped_*`` is the upstream default
    # imported from the example codebase; ``*_default`` is whatever the
    # user has typed so far. We treat "persisted matches the shipped
    # default" as "still default", and the textarea simply renders the
    # shipped string as its initial value.
    shipped_sys, shipped_user = load_default_prompts(agent_type, engine)
    if not sys_default and shipped_sys:
        sys_default = shipped_sys
    if not usr_default and shipped_user:
        usr_default = shipped_user
    has_shipped_sys = bool(shipped_sys)
    has_shipped_user = bool(shipped_user)

    edited["__llm_lm_name__"] = st.text_input(
        "Model identifier",
        value=lm_default,
        key=lm_key,
        help=(
            "Any identifier accepted by `LangChainAPIInference` — for "
            "example `ark/doubao-seed-2-0-mini-260428`, "
            "`openai/gpt-4o-mini`. **Config key:** `lm_name`."
        ),
    )
    col_t, col_n = st.columns(2)
    with col_t:
        edited["__llm_temperature__"] = st.number_input(
            "Temperature",
            value=temp_default,
            min_value=0.0,
            max_value=2.0,
            step=0.1,
            format="%.2f",
            key=temp_key,
            help=(
                "Sampling randomness. 0.0 = deterministic; 0.7 = balanced; "
                ">1.0 = highly creative. **Config key:** `temperature`."
            ),
        )
    with col_n:
        edited["__llm_max_tokens__"] = st.number_input(
            "Max response tokens",
            value=tok_default,
            min_value=64,
            max_value=8192,
            step=64,
            key=tok_key,
            help=(
                "Hard cap on response length per decision. "
                "**Config key:** `max_tokens`."
            ),
        )

    sys_placeholder = (
        "No default persona is registered for this archetype + engine yet. "
        "Type a system prompt here: describe the persona, beliefs, and "
        "trading approach. Do not reveal the underlying market mechanism "
        "or ground-truth formulas."
    )
    sys_label = (
        "System prompt (default persona shown below — edit to customize)"
        if has_shipped_sys else
        "System prompt (no default registered — type a custom persona)"
    )
    with st.expander(sys_label, expanded=True):
        if has_shipped_sys:
            st.caption(
                "This is the actual default persona shipped with the "
                "example codebase. Edit any text here to override; the "
                "bundle writer will materialize your version into the "
                "generated `prompts.py` and reference it from "
                "`players.yml`."
            )
        else:
            st.caption(
                "No default persona has been registered for this "
                "archetype + engine combination yet. Type your own below "
                "— the bundle writer will save it into the generated "
                "`prompts.py`."
            )
        edited["__llm_system_prompt__"] = st.text_area(
            "System prompt",
            value=sys_default,
            placeholder=sys_placeholder,
            height=260,
            key=sys_key,
            label_visibility="collapsed",
            help=(
                "Plain-text persona prompt sent as the system message on "
                "every call. Avoid leaking quantitative thresholds or "
                "naming the simulated phenomenon. **Config key:** "
                "`llm.sys_message`."
            ),
        )

    usr_placeholder = (
        "No default per-round template is registered for this archetype "
        "+ engine yet. Type a Python ``str.format`` template that will be "
        "rendered every round with current market state injected. "
        "Available placeholders (scenario-dependent) include: {round}, "
        "{price}, {prev_price}, {fundamental}, {price_change}, "
        "{deviation}, {cash}, {position}, {portfolio_value}."
    )
    usr_label = (
        "User prompt template (default shown below — edit to customize)"
        if has_shipped_user else
        "User prompt template (no default registered — type your own)"
    )
    with st.expander(usr_label, expanded=True):
        if has_shipped_user:
            st.caption(
                "This is the actual per-round template shipped with the "
                "example codebase. The player class fills in placeholders "
                "such as `{round}`, `{price}`, `{cash}` every tick. Edit "
                "to override; the bundle writer will save your version."
            )
        else:
            st.caption(
                "No default per-round template has been registered for "
                "this archetype + engine combination yet. Type your own "
                "below using `str.format` placeholders."
            )
        edited["__llm_user_prompt__"] = st.text_area(
            "User prompt template",
            value=usr_default,
            placeholder=usr_placeholder,
            height=300,
            key=usr_key,
            label_visibility="collapsed",
            help=(
                "Python `str.format` template sent as the user message on "
                "every round. Unknown placeholders raise KeyError at "
                "runtime, so only use the ones the scenario provides. "
                "**Config key:** `llm.user_message`."
            ),
        )


def _compose_help(spec: ParamSpec) -> str:
    """Build the multi-line tooltip shown when the user hovers ``?``.

    All per-parameter metadata is consolidated here so the row stays
    visually clean by default.  Streamlit renders the ``help`` argument
    as Markdown, so we use Markdown bullets for legibility.
    """
    bits: list[str] = []
    # Description first — the bulk of the explanation.  Skip when the
    # display label already shows the description (schema-1 handbooks),
    # to avoid duplication.
    if spec.description and spec.description != spec.display_label:
        bits.append(spec.description)
    facts: list[str] = []
    if spec.default:
        facts.append(f"**Default:** `{spec.default}`")
    if spec.valid_range:
        facts.append(f"**Range:** `{spec.valid_range}`")
    if spec.units:
        facts.append(f"**Units:** {spec.units}")
    if spec.sensitivity:
        facts.append(f"**Sensitivity:** {spec.sensitivity}")
    if spec.impact:
        facts.append(f"**Impact:** {spec.impact}")
    if spec.source:
        facts.append(f"**Source:** {spec.source}")
    # Raw config key shown last — power-user reference for cross-
    # checking ``players.yml`` without polluting the visible row.
    facts.append(f"**Config key:** `{spec.symbol}`")
    if facts:
        bits.append("\n".join(f"- {f}" for f in facts))
    return "\n\n".join(bits)


def _render_agent_card(agent: dict[str, Any]) -> None:
    """Render one card in the agent grid.

    The card image links to the read-only profile (existing behaviour).
    A small "Customize" button below the avatar promotes the agent to
    the active slot in the parameter panel on the left, and a "Selected"
    badge shows when the agent is already part of the portfolio.
    """
    agent_type = agent["agent_type"]
    href = f"?agent={quote(agent_type)}#agent-profile"
    selected = bool(st.session_state.get(f"market_agent_{agent_type}", False))
    is_active = st.session_state.get("customized_active_agent") == agent_type
    badge = (
        "<span class='agent-status-chip selected'>✓ in portfolio</span>"
        if selected else "<span class='agent-status-chip muted'>not selected</span>"
    )
    card = f"""
    <div class="agent-card{(' active' if is_active else '')}">
      <a class="agent-image-link" href="{href}" target="_self"
         title="{html.escape(agent['intro'], quote=True)}"
         aria-label="Open {html.escape(agent['display_name'])} profile">
        <img src="{agent['image_uri']}" alt="{html.escape(agent.get('alt_text', agent['display_name']))}">
        <span class="agent-hover">{html.escape(agent['intro'])}</span>
      </a>
      <div class="agent-card-copy">
        <div class="agent-card-name">{html.escape(agent['display_name'])}</div>
        {badge}
      </div>
    </div>
    """
    st.markdown(card, unsafe_allow_html=True)

    # "Customize" promotes this agent to the active slot in the
    # left-side parameter panel.  A second click on an already-active
    # agent collapses the panel (toggle behaviour).
    label = "Editing…" if is_active else "Customize"
    if st.button(
        label,
        key=f"market_customize_{agent_type}",
        use_container_width=True,
        help=(
            "Open this agent's parameter panel on the left. "
            "Click again to collapse it."
        ),
    ):
        st.session_state.customized_active_agent = (
            None if is_active else agent_type
        )
        st.rerun()


def render_agent_market() -> None:
    """Render step one: browse profiles and compose an investor portfolio."""
    _inject_market_styles()
    catalog = load_agent_catalog(_agent_catalog_signature())

    # Streamlit removes widget keys while their page is not rendered. Restore
    # checkboxes from the durable portfolio list when users return from setup.
    saved_selection = set(st.session_state.get("selected_market_agents", []))
    for agent in catalog:
        key = f"market_agent_{agent['agent_type']}"
        if key not in st.session_state:
            st.session_state[key] = agent["agent_type"] in saved_selection

    _render_workflow_sidebar(1, len(_selected_types(catalog)))

    render_back_to_start_bar(key_suffix="agents")
    st.markdown('<div class="market-kicker">Step 1 of 2</div>', unsafe_allow_html=True)
    st.title("Agent Market")
    st.write("Build an investor portfolio from the available market archetypes.")
    st.caption(
        "Each card lets you pick the decision engine — "
        "**Rule** (deterministic logic), **LLM** (language-model reasoning), "
        "**RuleLLM** (hybrid), or **RAG** (retrieval-augmented). "
        "Engines have different parameter sets you will configure in Step 2."
    )

    requested_agent = _query_agent()
    by_type = {agent["agent_type"]: agent for agent in catalog}
    if requested_agent in by_type:
        _render_profile(by_type[requested_agent])

    selected_before = _selected_types(catalog)
    controls, count = st.columns([4, 1])
    with controls:
        search = st.text_input(
            "Search agents",
            placeholder="Search by name, role, or scenario",
            label_visibility="collapsed",
        )
    with count:
        st.metric("Selected", len(selected_before))

    query = search.strip().lower()
    filtered = [
        agent
        for agent in catalog
        if not query
        or query in agent["display_name"].lower()
        or query in agent["agent_type"].lower()
        or query in agent["archetype"].lower()
        or query in agent["scenarios"].lower()
    ]

    if not filtered:
        st.info("No agents match this search.")
    else:
        active_agent_type = st.session_state.get("customized_active_agent")
        active_agent = by_type.get(active_agent_type) if active_agent_type else None
        if active_agent is not None:
            panel_col, grid_col = st.columns([5, 7], gap="large")
            grid_columns_per_row = 4
            with panel_col:
                _render_param_panel(active_agent)
            grid_container = grid_col
        else:
            grid_columns_per_row = 6
            grid_container = st.container()

        with grid_container:
            for start in range(0, len(filtered), grid_columns_per_row):
                columns = st.columns(grid_columns_per_row, gap="small")
                for column, agent in zip(
                    columns, filtered[start : start + grid_columns_per_row]
                ):
                    with column:
                        _render_agent_card(agent)

    selected = _selected_types(catalog)
    st.session_state.selected_market_agents = selected
    st.divider()
    reset_col, proceed_col = st.columns([1, 3])
    with reset_col:
        if st.button("Clear selection", use_container_width=True, disabled=not selected):
            for agent in catalog:
                st.session_state[f"market_agent_{agent['agent_type']}"] = False
            st.session_state.selected_market_agents = []
            st.rerun()
    with proceed_col:
        if st.button(
            "Proceed to simulation setup",
            type="primary",
            use_container_width=True,
            disabled=not selected,
        ):
            _clear_query_agent()
            st.session_state.workflow_stage = "setup"
            st.rerun()


def _render_portfolio_chips(agents: list[dict[str, Any]]) -> None:
    chips = []
    for agent in agents:
        chips.append(
            '<span class="portfolio-chip">'
            f'<img src="{agent["image_uri"]}" alt="">'
            f'{html.escape(agent["display_name"])}'
            "</span>"
        )
    st.markdown(
        f'<div class="portfolio-strip">{"".join(chips)}</div>',
        unsafe_allow_html=True,
    )


def render_simulation_setup() -> None:
    """Render step two: choose a scenario and variant, then review the roster."""
    _inject_market_styles()
    catalog = load_agent_catalog(_agent_catalog_signature())
    selected_types = st.session_state.get("selected_market_agents", [])
    selected_set = set(selected_types)
    selected_agents = [a for a in catalog if a["agent_type"] in selected_set]

    if not selected_agents:
        st.session_state.workflow_stage = "agents"
        st.rerun()

    _render_workflow_sidebar(2, len(selected_agents))
    render_back_to_start_bar(key_suffix="setup")
    st.markdown('<div class="market-kicker">Step 2 of 2</div>', unsafe_allow_html=True)
    st.title("Simulation Setup")

    back_col, summary_col = st.columns([1, 4])
    with back_col:
        if st.button("Back", use_container_width=True):
            st.session_state.workflow_stage = "agents"
            st.rerun()
    with summary_col:
        _render_portfolio_chips(selected_agents)

    groups = discover_scenario_groups()
    group_names = list(groups)
    if not group_names:
        st.error("No simulation scenarios were found.")
        return

    current = st.session_state.get("selected_scenario", "")
    current_group = current.split("/", 1)[0] if current else group_names[0]
    default_group = group_names.index(current_group) if current_group in group_names else 0

    scenario_col, variant_col = st.columns([2, 3], gap="large")
    with scenario_col:
        selected_group = st.selectbox(
            "Scenario",
            group_names,
            index=default_group,
            format_func=scenario_display_name,
            key="market_scenario_group",
        )

    variant_keys = sorted(
        groups[selected_group],
        key=lambda key: VARIANT_ORDER.get(key.split("/")[-1], 99),
    )
    variant_labels = [key.split("/", 1)[1] if "/" in key else key for key in variant_keys]
    current_variant = current.split("/", 1)[1] if "/" in current else ""
    default_variant = (
        variant_labels.index(current_variant) if current_variant in variant_labels else 0
    )
    with variant_col:
        selected_variant = st.radio(
            "Variant",
            variant_labels,
            index=default_variant,
            horizontal=True,
            key=f"market_variant_{selected_group}",
        )

    selected_scenario = variant_keys[variant_labels.index(selected_variant)]
    st.session_state.selected_scenario = selected_scenario
    info = get_scenario_info(selected_scenario)

    market_col, mode_col, rounds_col = st.columns(3)
    market_col.metric("Market", scenario_display_name(selected_group))
    mode_col.metric("Variant", selected_variant)
    rounds_col.metric("Rounds", info.get("total_rounds", "N/A"))
    if info.get("description"):
        st.caption(info["description"])

    st.divider()
    st.subheader("Selected investor details")
    for agent in selected_agents:
        with st.expander(agent["display_name"], expanded=False):
            image_col, detail_col = st.columns([1, 3], gap="large")
            with image_col:
                st.image(agent["image_file"], use_container_width=True)
                st.caption(agent["agent_type"])
            with detail_col:
                st.markdown(agent["profile_markdown"] or "Profile content is unavailable.")

    st.divider()
    if st.button("Open simulation workspace", type="primary", use_container_width=True):
        target_scenario = _maybe_write_customized_bundle(
            selected_agents=selected_agents,
            base_scenario=selected_scenario,
        )
        if target_scenario is not None:
            st.session_state.selected_scenario = target_scenario
        st.session_state.workflow_stage = "workspace"
        st.session_state.current_page = "Simulation"
        st.rerun()


def _maybe_write_customized_bundle(
    *,
    selected_agents: list[dict[str, Any]],
    base_scenario: str,
) -> str | None:
    """Materialise a customized bundle when the user has edited any params.

    Returns the new scenario key (e.g. ``"CUSTOMIZED_SIMULATION/Customized-001/Rule"``)
    when a bundle is written, or ``None`` when no customization is
    pending (so the caller keeps the originally chosen scenario).
    """
    customized_params = st.session_state.get("customized_params") or {}
    # Only the agents currently in the portfolio matter; ignore stale
    # edits for agents the user later removed.
    active_edits = {
        agent["agent_type"]: customized_params.get(agent["agent_type"], {})
        for agent in selected_agents
        if customized_params.get(agent["agent_type"])
    }
    if not active_edits:
        return None

    selections: list[CustomizedAgentSelection] = []
    for agent in selected_agents:
        agent_type = agent["agent_type"]
        engine = st.session_state.get(
            f"market_engine_{agent_type}",
            (agent.get("variants") or ["Rule"])[0],
        )
        params = customized_params.get(agent_type, {}).get(engine, {})
        if not params:
            # No edits for this agent in the chosen engine — fall back
            # to handbook defaults (params left empty so the bundle
            # writer applies class defaults).
            params = {}
        selections.append(
            CustomizedAgentSelection(
                archetype=agent_type,
                display_name=agent["display_name"],
                engine=engine,
                params=params,
                num_instances=1,
            )
        )

    try:
        result = write_customized_bundle(
            selections=selections,
            base_scenario=base_scenario,
            project_root=PROJECT_ROOT,
        )
    except Exception as exc:
        st.error(f"Failed to materialise customized bundle: {exc}")
        return None

    st.session_state.customized_dir_id = result.customized_id
    # Pick the engine of the first selected agent for the bundle's
    # displayed variant.  All agents share one bundle; the engine
    # label is purely cosmetic here since the bundle is self-contained.
    primary_engine = selections[0].engine if selections else "Rule"
    new_key = f"CUSTOMIZED_SIMULATION/{result.customized_id}"
    st.toast(
        f"Customized bundle written: {result.customized_id} "
        f"(based on {base_scenario})",
        icon="✨",
    )
    return new_key


def render_selected_portfolio_strip() -> None:
    """Render the selected market portfolio in the simulation workspace."""
    _inject_market_styles()
    catalog = load_agent_catalog(_agent_catalog_signature())
    selected = set(st.session_state.get("selected_market_agents", []))
    agents = [agent for agent in catalog if agent["agent_type"] in selected]
    if not agents:
        return

    heading, action = st.columns([5, 1])
    with heading:
        st.caption("Selected investor portfolio")
        _render_portfolio_chips(agents)
    with action:
        if st.button("Edit portfolio", use_container_width=True):
            st.session_state.workflow_stage = "agents"
            st.session_state.current_page = "Simulation"
            st.rerun()
