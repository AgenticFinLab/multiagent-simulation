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
    get_default_prompts,
    is_archetype_supported,
    is_scenario_compatible,
    parse_parameters_file,
    scenario_market_features,
    write_customized_bundle,
    write_default_scenario_bundle,
)
from ..customized.handbook_params import ParamSpec


PROJECT_ROOT = Path(__file__).resolve().parents[3]
AGENT_POOL_ROOT = PROJECT_ROOT / "examples" / "AGENT_POOL"
IMAGE_ROOT = AGENT_POOL_ROOT / "agent_images"
ICON_ROOT = IMAGE_ROOT / "icons"
FINANCE_ROOT = AGENT_POOL_ROOT / "finance"
PROFILE_ROOT = FINANCE_ROOT
CATALOG_PATH = IMAGE_ROOT / "agent_avatar_map.json"

VARIANT_DISPLAY = {"Rule": "Rule", "LLM": "LLM", "RuleLLM": "RuleLLM", "Rag": "RAG"}

# Subtle brand-aligned tint per decision engine, used to color the Default
# launch buttons on the variant_choice page. Each entry is
# (background, border, text). Kept intentionally light ("a bit of color").
VARIANT_COLORS = {
    "Rule": ("#e7f3f0", "#b6d8d0", "#1f6157"),      # teal
    "LLM": ("#e8f0fb", "#bcd3f0", "#2a5fa6"),        # blue
    "RuleLLM": ("#efeafb", "#d3c7f0", "#6544a6"),    # purple
    "Rag": ("#fdf3dd", "#f0d79a", "#97690a"),        # gold
}

# Every agent supports all decision engines by default, so the customize
# selector always offers the full set regardless of the agent.
ALL_ENGINES = ("Rule", "LLM", "RuleLLM", "Rag")


def _agent_catalog_signature() -> tuple[tuple[str, int], ...]:
    """Return a lightweight cache key for avatar metadata and PNG changes."""
    paths = []
    if CATALOG_PATH.exists():
        paths.append(CATALOG_PATH)
    if ICON_ROOT.exists():
        paths.extend(sorted(ICON_ROOT.glob("*.png")))
    if FINANCE_ROOT.exists():
        paths.extend(sorted(FINANCE_ROOT.glob("*.md")))
    return tuple((str(path), path.stat().st_mtime_ns) for path in paths)


def _scenario_probe_key(base: str, groups: dict) -> str:
    """Return a scenario key suitable for probing metadata.

    Every scenario folder ships a Rule variant; if for some reason it is
    missing, fall back to the first available variant key so we still get
    rounds/description metadata.
    """
    variants = groups.get(base) or []
    rule_key = f"{base}/Rule"
    if rule_key in variants:
        return rule_key
    return variants[0] if variants else base


def render_entry_choice() -> None:
    """Render the landing chooser: pre-built scenario vs. customized market.

    This is the landing page after launching the app. The user first
    selects *which* market dynamic to simulate (the scenario name fixes
    the scenario-level parameters such as round count and required
    market features); then chooses one of two paths:

    * **Default** — launch the pre-configured implementation
      from ``examples/<Scenario>/<Variant>/`` directly.
    * **Customize my market** — proceeds to Stage 2 with the scenario
      locked, where the user assembles their own investor lineup.

    The Rule / LLM / RuleLLM / RAG distinction is presented as an
    *agent* attribute (which decision engine the agents use),
    not as part of the scenario itself.
    """
    _inject_market_styles()

    groups = discover_scenario_groups()
    group_names = list(groups.keys())
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
        project_name = st.session_state.get("project_name", "")
        if project_name:
            st.markdown(f"**Project:** {project_name}")
        st.markdown("---")
        st.markdown("~~Stage 0. Name your project~~")
        st.markdown("**Stage 1.** Pick a scenario")
        st.caption(f"{scenario_count} scenarios available")
        st.markdown("**Stage 2.** Default agents or customize")
        st.markdown("---")
        if st.button("← Back to welcome", use_container_width=True):
            st.session_state.workflow_stage = "welcome"
            st.rerun()
        st.caption("MASIM v0.1.0")

    st.markdown(
        '<div class="market-kicker">Stage 1 of 2</div>', unsafe_allow_html=True
    )
    st.title("Pick a market scenario")
    st.write(
        "Choose the market dynamic you want to simulate. The selected "
        "scenario fixes the simulation parameters; in Stage 2 you "
        "decide whether to run the default setup or build "
        "your own market."
    )

    if not group_names:
        st.error("No simulation scenarios were found in `configs/`.")
        return

    selected_base = st.session_state.get("selected_scenario_base", "")

    # --- Scenario card grid -------------------------------------------
    cols_per_row = 3
    for start in range(0, len(group_names), cols_per_row):
        row = st.columns(cols_per_row, gap="medium")
        for col, base in zip(row, group_names[start : start + cols_per_row]):
            with col:
                _render_scenario_card(base, None, selected_base)

    # Re-read after the loop in case a click changed the selection.
    # Clicking a card sets the selection AND advances to the
    # variant_choice stage (see _render_scenario_card), so under normal
    # flow we only reach here when nothing is selected yet.
    if not st.session_state.get("selected_scenario_base", ""):
        st.info("Select a scenario above to continue.")
        return

    # Defensive: a stale selection lingered without navigating (e.g. an
    # interrupted rerun). Offer an explicit way forward instead of
    # silently auto-redirecting (which previously trapped the user).
    if st.button(
        f"Continue with {scenario_display_name(selected_base)} →",
        type="primary",
    ):
        st.session_state.workflow_stage = "variant_choice"
        st.rerun()


def _inject_variant_button_styles() -> None:
    """Tint each Default engine button (Rule/LLM/RuleLLM/RAG) with a subtle color.

    Targets the Streamlit ``st-key-<key>`` wrapper class emitted for buttons
    keyed ``stage2_default_<variant>``.
    """
    rules = []
    for variant, (bg, border, text) in VARIANT_COLORS.items():
        rules.append(
            f".st-key-stage2_default_{variant} button {{"
            f"background:{bg};border:1px solid {border};color:{text};"
            f"font-weight:700;}}"
            f".st-key-stage2_default_{variant} button:hover {{"
            f"border-color:{text};color:{text};filter:brightness(0.97);}}"
        )
    st.markdown("<style>" + "".join(rules) + "</style>", unsafe_allow_html=True)


def render_variant_choice() -> None:
    """Stage 2: choose Default or Customized (build your own market).

    Rendered on its own page after the user selects a scenario in Stage 1.
    """
    _inject_market_styles()
    _inject_variant_button_styles()

    selected_base = st.session_state.get("selected_scenario_base", "")
    if not selected_base:
        # Guard: shouldn't happen, but bounce back to Stage 1.
        st.session_state.workflow_stage = "scenario_setup"
        st.rerun()
        return

    groups = discover_scenario_groups()

    with st.sidebar:
        st.title("MASIM")
        st.caption("Investment workflow")
        st.markdown("---")
        st.markdown("~~Stage 1. Pick a scenario~~")
        st.markdown("**Stage 2.** Default agents or customize")
        st.markdown("---")
        if st.button("← Back to scenarios", use_container_width=True):
            st.session_state.workflow_stage = "scenario_setup"
            st.session_state.pop("selected_scenario_base", None)
            st.rerun()
        st.caption("MASIM v0.1.0")

    st.markdown(
        '<div class="market-kicker">Stage 2 of 2</div>', unsafe_allow_html=True
    )
    st.title("Choose how to run it")

    # --- Selected-scenario info strip ---------------------------------
    info = get_scenario_info(_scenario_probe_key(selected_base, groups))
    name_col, rounds_col, features_col = st.columns([3, 1, 2])
    with name_col:
        st.markdown(
            f"<div class='scenario-confirm-chip'>✓ "
            f"{html.escape(scenario_display_name(selected_base))}"
            f"</div>",
            unsafe_allow_html=True,
        )
        if info.get("description"):
            st.caption(info["description"])
    with rounds_col:
        # Editable round count. Keyed by scenario so each scenario keeps its
        # own value and the widget auto-resets when the user switches
        # scenarios. The shipped default seeds the initial value; changing
        # it never mutates the shipped YAML (a copy is generated at launch).
        try:
            shipped_rounds = int(info.get("total_rounds") or 0)
        except (TypeError, ValueError):
            shipped_rounds = 0
        st.number_input(
            "Rounds",
            min_value=1,
            value=shipped_rounds if shipped_rounds > 0 else 1,
            step=1,
            key=f"variant_rounds_{selected_base}",
            help=(
                "Adjust the number of simulation rounds. Leaving it at the "
                "default launches the shipped config unchanged; changing it "
                "generates a reproducible copy with the new count."
            ),
        )
    with features_col:
        feats = scenario_market_features(selected_base)
        st.metric(
            "Market features",
            ", ".join(sorted(feats)) if feats else "standard",
        )

    st.divider()

    default_col, custom_col = st.columns(2, gap="large")

    with default_col:
        variant_keys = groups.get(selected_base) or []
        st.markdown("**Default**")
        st.caption(
            "Launch the pre-configured scenario directly. "
            "Each button represents a different decision engine."
        )
        if not variant_keys:
            st.info("No default variants available for this scenario.")
        else:
            chip_cols = st.columns(min(len(variant_keys), 4), gap="small")
            for col, key in zip(chip_cols, variant_keys):
                variant = key.split("/", 1)[1] if "/" in key else key
                with col:
                    if st.button(
                        VARIANT_DISPLAY.get(variant, variant),
                        key=f"stage2_default_{variant}",
                        use_container_width=True,
                        help=(
                            f"Run {scenario_display_name(selected_base)} "
                            f"with the {variant} decision engine."
                        ),
                    ):
                        _launch_default_variant(key)

    with custom_col:
        st.markdown("**Customized**")
        st.caption(
            "Select agents from the pool, edit each agent's parameters, "
            "optionally rewrite LLM prompts, then launch. The chosen "
            "scenario stays locked while you build."
        )
        if st.button(
            "Select agents for simulation →",
            key="stage2_go_customize",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.workflow_stage = "customize"
            st.rerun()


def _launch_default_variant(scenario_key: str) -> None:
    """Send the user to the workspace with a default variant.

    If the user adjusted the round count on the variant_choice page, we
    never mutate the shipped config: instead a reproducible copy is
    generated under ``configs/CUSTOMIZED_SIMULATION/Default-...-rN`` and
    that bundle is launched. Leaving rounds at the shipped default keeps
    the current zero-copy behaviour.
    """
    base = scenario_key.split("/", 1)[0]
    variant = scenario_key.split("/", 1)[1] if "/" in scenario_key else "Rule"

    # Shipped round count for comparison.
    info = get_scenario_info(scenario_key)
    try:
        shipped_rounds = int(info.get("total_rounds") or 0)
    except (TypeError, ValueError):
        shipped_rounds = 0
    edited_rounds = st.session_state.get(f"variant_rounds_{base}")

    launch_key = scenario_key
    customized_id = None
    if (
        edited_rounds is not None
        and shipped_rounds > 0
        and int(edited_rounds) != shipped_rounds
    ):
        try:
            result = write_default_scenario_bundle(
                scenario_name=base,
                variant=variant,
                total_rounds=int(edited_rounds),
                project_root=PROJECT_ROOT,
            )
            launch_key = f"CUSTOMIZED_SIMULATION/{result.customized_id}"
            customized_id = result.customized_id
        except (FileNotFoundError, ValueError) as exc:
            st.error(f"Could not apply the adjusted round count: {exc}")
            return

    st.session_state.selected_scenario = launch_key
    # Prefix with project slug so all path helpers resolve to the project-local
    # copy (configs/{project}/{scenario}/{variant}, etc.).
    project_slug = st.session_state.get("project_slug", "")
    if project_slug and not launch_key.startswith(project_slug + "/"):
        st.session_state.selected_scenario = f"{project_slug}/{launch_key}"
    st.session_state.selected_market_agents = []
    st.session_state.workflow_stage = "workspace"
    st.session_state.current_page = "Simulation"
    # Track (or clear) the generated bundle id so the sidebar / workspace
    # can label the run correctly.
    if customized_id is not None:
        st.session_state.customized_dir_id = customized_id
    else:
        st.session_state.pop("customized_dir_id", None)
    st.rerun()


def _field_from_summary_table(markdown: str, field: str) -> str:
    pattern = rf"^\|\s*{re.escape(field)}\s*\|\s*(.*?)\s*\|\s*$"
    match = re.search(pattern, markdown, flags=re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else ""


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


def _kebab_to_title(stem: str) -> str:
    """Convert a kebab-case file stem to a Title-Cased display name."""
    return " ".join(part.capitalize() for part in stem.split("-"))


@st.cache_data(show_spinner=False)
def load_agent_catalog(_cache_signature: tuple[tuple[str, int], ...] | None = None) -> list[dict[str, Any]]:
    """Load agent metadata and profiles from finance/ + icons/.

    The canonical agent pool is the set of ``finance/*.md`` specs that
    have a matching ``agent_images/icons/finance-<stem>.png`` icon (the
    ``finance-`` prefix encodes the agent's domain). When an explicit
    ``agent_avatar_map.json`` exists it takes precedence.
    """
    if CATALOG_PATH.exists():
        raw_items = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    else:
        raw_items = [
            {
                "agent_type": md_path.stem,
                "display_name": _kebab_to_title(md_path.stem),
                "image_path": f"icons/finance-{md_path.stem}.png",
                "source_profile": str(md_path),
            }
            for md_path in sorted(FINANCE_ROOT.glob("*.md"))
            if (ICON_ROOT / f"finance-{md_path.stem}.png").exists()
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
        .market-strip {
            display: flex; gap: 0.45rem; flex-wrap: wrap;
            padding: 0.5rem 0 0.25rem;
        }
        .market-chip {
            display: inline-flex; align-items: center; gap: 0.38rem;
            border: 1px solid #dce2e8; border-radius: 6px;
            padding: 0.28rem 0.48rem; background: #fff;
            color: #26323d; font-size: 0.74rem;
        }
        .market-chip img {width: 24px; height: 24px; border-radius: 4px; object-fit: cover;}
        /* Teal accent for the Stage-1 "Customize my roster" CTA. */
        .st-key-stage1_go_customize button {
            background-color: #287a6d !important;
            color: #ffffff !important;
            border: 1px solid #287a6d !important;
        }
        .st-key-stage1_go_customize button:hover {
            background-color: #1f6157 !important;
            border-color: #1f6157 !important;
        }
        .st-key-stage1_go_customize button:focus,
        .st-key-stage1_go_customize button:active {
            background-color: #1f6157 !important;
            border-color: #1f6157 !important;
            box-shadow: 0 0 0 2px rgba(40, 122, 109, 0.35) !important;
        }
        @media (max-width: 700px) {
            .block-container {padding-top: 3.75rem;}
            .agent-card {min-height: 230px;}
        }
        /* Step-2 scenario cards. Compatibility is conveyed by border
           colour and the inline status badge. Disabled cards are
           visually muted but still readable so users can hover the
           reason. */
        .scenario-card {
            border: 1px solid #dce2e8; border-radius: 10px;
            background: #ffffff; padding: 0.85rem 0.95rem;
            min-height: 168px; display: flex; flex-direction: column;
            box-shadow: 0 1px 2px rgba(20, 32, 44, 0.06);
        }
        .scenario-card.ready {border-left: 4px solid #287a6d;}
        .scenario-card.blocked {
            border-left: 4px solid #c1543c; background: #fbf6f5;
            opacity: 0.92;
        }
        .scenario-card.active {
            box-shadow: 0 0 0 2px rgba(40, 122, 109, 0.22);
            border-color: #287a6d;
        }
        .scenario-name {
            font-size: 0.95rem; font-weight: 700; color: #17212b;
            line-height: 1.25; margin-bottom: 0.18rem;
        }
        .scenario-meta {
            font-size: 0.7rem; color: #68737d; margin-bottom: 0.35rem;
        }
        .scen-badge {
            display: inline-block; font-size: 0.62rem; font-weight: 700;
            padding: 0.06rem 0.46rem; border-radius: 8px;
            letter-spacing: 0.02em; line-height: 1.5;
            margin-bottom: 0.35rem;
        }
        .scen-badge.ok {
            background: #e7f3f0; color: #1f6157;
            border: 1px solid #b6d8d0;
        }
        .scen-badge.bad {
            background: #f8e3dd; color: #88321b;
            border: 1px solid #e3b8ac;
        }
        .scenario-desc {
            font-size: 0.74rem; color: #41525f; line-height: 1.36;
            margin-bottom: 0.3rem;
            display: -webkit-box; -webkit-line-clamp: 3;
            -webkit-box-orient: vertical; overflow: hidden;
        }
        .scen-reasons {
            margin: 0.2rem 0 0 0.95rem; padding: 0;
            font-size: 0.68rem; color: #6f3826; line-height: 1.42;
        }
        .scenario-confirm-chip {
            display: inline-flex; align-items: center;
            font-size: 0.78rem; font-weight: 700; color: #1f6157;
            background: #e7f3f0; border: 1px solid #b6d8d0;
            padding: 0.28rem 0.7rem; border-radius: 14px;
            letter-spacing: 0.01em;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_customize_sidebar(scenario_base: str, selected_count: int) -> None:
    """Sidebar shown during the Stage-2 customize flow.

    Surfaces the locked scenario at the top so the user always knows
    which simulation they are building agents for; the only navigation
    out of this stage is the back button rendered in the main column.
    """
    with st.sidebar:
        st.title("MASIM")
        st.caption("Investment workflow")
        st.markdown("---")
        st.markdown("**✓ Stage 1.** Scenario")
        st.caption(scenario_display_name(scenario_base) if scenario_base else "—")
        st.markdown("**Stage 2.** Select agents")
        st.caption(f"{selected_count} agents in market")
        st.markdown("---")
        st.caption("MASIM v0.1.0")


def render_back_to_stage1_bar(
    *,
    key_suffix: str,
    reset_runtime: bool = False,
    target_stage: str = "scenario_setup",
) -> None:
    """Render a small "Back" button at the top of any post-Stage-1 page.

    Args:
        key_suffix: caller-specific suffix to keep widget keys unique
            across pages (e.g. ``"customize"``, ``"workspace"``).
        reset_runtime: when True, also clear simulation/replay state so
            the user returns to a clean page after a run.
        target_stage: workflow stage to return to. ``"scenario_setup"``
            (default) goes all the way back to the scenario picker;
            ``"variant_choice"`` returns to the "Choose how to run it"
            page while keeping the committed scenario.
    """
    if target_stage == "variant_choice":
        label = "← Back to run options"
        help_text = 'Return to the "Choose how to run it" page.'
    else:
        label = "← Back to scenario"
        help_text = "Return to the scenario picker (Stage 1)."
    btn_col, _ = st.columns([1, 6])
    with btn_col:
        if st.button(
            label,
            key=f"main_back_to_stage1_{key_suffix}",
            use_container_width=True,
            help=help_text,
        ):
            st.session_state.workflow_stage = target_stage
            # Only forget the chosen scenario when going all the way back
            # to Stage 1; variant_choice still needs it to render.
            if target_stage == "scenario_setup":
                st.session_state.pop("selected_scenario_base", None)
            if reset_runtime:
                st.session_state.simulation_running = False
                st.session_state.simulation_completed = False
                st.session_state.replay_active = False
                st.session_state.replay_rounds = []
                st.session_state.replay_index = 0
                st.session_state.viewed_round_idx = 0
                st.session_state.sys_messages = []
                # Clear customized-bundle id so the next launch doesn't
                # carry over a stale CUSTOMIZED_SIMULATION key.
                st.session_state.pop("customized_dir_id", None)
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
      defaults; "Add to market" persists params and ticks the
      Add-to-Market checkbox in one atomic action.
    """
    agent_type = agent["agent_type"]
    # Every agent supports all decision engines by default, so the selector
    # always offers the full set (Rule / LLM / RuleLLM / RAG).
    all_engines = list(ALL_ENGINES)
    specs = _load_param_specs(agent)

    st.markdown('<div class="market-kicker">Customize</div>', unsafe_allow_html=True)
    st.subheader(agent["display_name"])
    st.caption(agent["agent_type"])

    # ---- Engine selector ------------------------------------------------
    engine_key = f"market_engine_{agent_type}"
    if engine_key not in st.session_state or st.session_state[engine_key] not in all_engines:
        st.session_state[engine_key] = all_engines[0]

    st.segmented_control(
        "Decision engine",
        options=all_engines,
        format_func=lambda v: VARIANT_DISPLAY.get(v, v),
        key=engine_key,
        help=(
            "Choose the decision-making engine. Rule = deterministic logic; "
            "LLM = persona-driven prompt; RuleLLM = hybrid; RAG = "
            "retrieval-augmented. Every agent supports all engines."
        ),
    )
    engine = st.session_state[engine_key]

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
        primary_label = "Update in market" if already_in else "Add to market"
        if st.button(primary_label, type="primary", use_container_width=True,
                     key=f"customized_add_{agent_type}"):
            persisted.clear()
            persisted.update(edited)
            st.session_state[f"market_agent_{agent_type}"] = True
            st.toast(f"{agent['display_name']} → market", icon="✅")
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
    shipped_sys, shipped_user = get_default_prompts(agent_type, engine)
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
    badge shows when the agent is already part of the market.
    """
    agent_type = agent["agent_type"]
    href = f"?agent={quote(agent_type)}#agent-profile"
    selected = bool(st.session_state.get(f"market_agent_{agent_type}", False))
    is_active = st.session_state.get("customized_active_agent") == agent_type
    badge = (
        "<span class='agent-status-chip selected'>✓ in market</span>"
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


def render_customize() -> None:
    """Stage 2 (Customized): select agents for the locked scenario.

    The scenario chosen in Stage 1 is shown as a non-editable header
    with a back button. The user selects agents from the pool (shown as
    icons), edits each agent's parameters (and prompts, for LLM engines),
    then clicks *Launch simulation* to materialise a customized bundle
    and proceed to the workspace.
    """
    scenario_base = st.session_state.get("selected_scenario_base", "")
    if not scenario_base:
        # Defensive: a customize stage with no scenario locked is
        # nonsensical — send the user back to Stage 1.
        st.session_state.workflow_stage = "scenario_setup"
        st.rerun()

    _inject_market_styles()
    catalog = load_agent_catalog(_agent_catalog_signature())

    # Streamlit drops widget keys for un-rendered pages; restore the
    # checkbox state from the durable market list when users return
    # to this stage from the workspace.
    saved_selection = set(st.session_state.get("selected_market_agents", []))
    for agent in catalog:
        key = f"market_agent_{agent['agent_type']}"
        if key not in st.session_state:
            st.session_state[key] = agent["agent_type"] in saved_selection

    _render_customize_sidebar(scenario_base, len(_selected_types(catalog)))

    render_back_to_stage1_bar(
        key_suffix="customize",
        target_stage="variant_choice",
    )

    st.markdown(
        '<div class="market-kicker">Stage 2 of 2</div>', unsafe_allow_html=True
    )
    title_col, lock_col = st.columns([2, 3])
    with title_col:
        st.title("Select & Setup Agents")
    with lock_col:
        info = get_scenario_info(
            _scenario_probe_key(scenario_base, discover_scenario_groups())
        )
        rounds = info.get("total_rounds", "—")
        feats = scenario_market_features(scenario_base)
        feats_text = ", ".join(sorted(feats)) if feats else "standard"
        st.markdown(
            f"<div class='scenario-confirm-chip' style='margin-top:14px'>"
            f"🔒 {html.escape(scenario_display_name(scenario_base))} · "
            f"{rounds} rounds · {html.escape(feats_text)}"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.write(
        "Select the agents you want in the simulation. Click an agent's "
        "icon to view its profile, use **Customize** to edit its "
        "parameters, and (for LLM engines) tweak the persona / per-round "
        "prompt. Each agent's decision engine is set per-card."
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
    selected_agents = [a for a in catalog if a["agent_type"] in set(selected)]

    # Inline compatibility warning: surface incompatible archetypes
    # before the user attempts to launch.
    compat_blocker = None
    if selected_agents:
        roster = [a["agent_type"] for a in selected_agents]
        ok, reasons = is_scenario_compatible(scenario_base, roster)
        if not ok:
            compat_blocker = reasons

    st.divider()
    if selected_agents:
        st.markdown("**Current market**")
        _render_market_chips(selected_agents)
        if compat_blocker:
            st.error(
                "The current market is incompatible with "
                f"**{scenario_display_name(scenario_base)}**:\n\n"
                + "\n".join(f"- {r}" for r in compat_blocker)
            )

    reset_col, launch_col = st.columns([1, 3])
    with reset_col:
        if st.button(
            "Clear selection",
            use_container_width=True,
            disabled=not selected,
            key="customize_clear",
        ):
            for agent in catalog:
                st.session_state[f"market_agent_{agent['agent_type']}"] = False
            st.session_state.selected_market_agents = []
            st.rerun()
    with launch_col:
        if st.button(
            "Launch simulation →",
            type="primary",
            use_container_width=True,
            disabled=not selected or compat_blocker is not None,
            key="customize_launch",
        ):
            target = _write_customized_bundle(
                selected_agents=selected_agents,
                scenario_base=scenario_base,
            )
            if target is None:
                return
            _clear_query_agent()
            st.session_state.selected_scenario = target
            st.session_state.workflow_stage = "workspace"
            st.session_state.current_page = "Simulation"
            st.rerun()


def _render_market_chips(agents: list[dict[str, Any]]) -> None:
    chips = []
    for agent in agents:
        chips.append(
            '<span class="market-chip">'
            f'<img src="{agent["image_uri"]}" alt="">'
            f'{html.escape(agent["display_name"])}'
            "</span>"
        )
    st.markdown(
        f'<div class="market-strip">{"".join(chips)}</div>',
        unsafe_allow_html=True,
    )


def _render_scenario_card(
    scenario_base: str,
    roster_archetypes: list[str] | None,
    selected_base: str,
) -> None:
    """Render one card in a scenario grid.

    When ``roster_archetypes`` is ``None`` (Stage-1 picker, no roster
    yet) the card is rendered without a compatibility badge — every
    scenario is selectable. When a roster is provided (legacy callers),
    a green / red compatibility badge is computed from
    ``is_scenario_compatible`` and incompatible scenarios are disabled.
    """
    has_roster = roster_archetypes is not None
    if has_roster:
        compatible, reasons = is_scenario_compatible(
            scenario_base, roster_archetypes
        )
    else:
        compatible, reasons = True, []

    groups = discover_scenario_groups()
    info = get_scenario_info(_scenario_probe_key(scenario_base, groups))
    rounds = info.get("total_rounds", "—")
    description = (info.get("description") or "").strip()
    if len(description) > 160:
        description = description[:160].rstrip() + "…"
    name = scenario_display_name(scenario_base)
    is_selected = scenario_base == selected_base
    state_class = ("ready" if compatible else "blocked") + (
        " active" if is_selected else ""
    )

    if has_roster:
        if compatible:
            badge = (
                f"<span class='scen-badge ok'>All {len(roster_archetypes)} "
                f"agents supported</span>"
            )
        else:
            badge = "<span class='scen-badge bad'>Disabled — incompatible</span>"
    else:
        # Show the market-features tag so users see what each scenario
        # implies (e.g. ``leverage``, ``short_selling``) before picking.
        feats = scenario_market_features(scenario_base)
        feats_text = ", ".join(sorted(feats)) if feats else "standard"
        badge = (
            f"<span class='scen-badge ok'>{html.escape(feats_text)}</span>"
        )

    reason_html = ""
    if has_roster and not compatible and reasons:
        items = "".join(f"<li>{html.escape(r)}</li>" for r in reasons)
        reason_html = f"<ul class='scen-reasons'>{items}</ul>"
    st.markdown(
        f"""
        <div class="scenario-card {state_class}">
          <div class="scenario-name">{html.escape(name)}</div>
          <div class="scenario-meta">{rounds} rounds</div>
          {badge}
          <div class="scenario-desc">{html.escape(description)}</div>
          {reason_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
    # Selection button — only rendered when the scenario is compatible
    # (or when there is no roster yet, i.e. Stage-1).
    if not has_roster or compatible:
        btn_label = "✓ Selected" if is_selected else "Select"
        if st.button(
            btn_label,
            key=f"scen_card_{scenario_base}",
            disabled=is_selected,
            use_container_width=True,
        ):
            st.session_state.selected_scenario_base = scenario_base
            # Copy scenario into project-local dirs if a project is active.
            project_slug = st.session_state.get("project_slug", "")
            if project_slug:
                from masim.interface.components.welcome import copy_scenario_to_project
                copy_scenario_to_project(project_slug, scenario_base)
            st.session_state.workflow_stage = "variant_choice"
            st.rerun()


def _write_customized_bundle(
    *,
    selected_agents: list[dict[str, Any]],
    scenario_base: str,
) -> str | None:
    """Always materialise a customized bundle from the user's roster.

    Returns the new scenario key (e.g. ``CUSTOMIZED_SIMULATION/Customized-007``)
    or ``None`` on failure. Defense-in-depth: re-validates compatibility
    before invoking the writer (the Stage-2 inline check already gates this).
    """
    roster_archetypes = [a["agent_type"] for a in selected_agents]
    compatible, reasons = is_scenario_compatible(scenario_base, roster_archetypes)
    if not compatible:
        st.error(
            "This scenario is not compatible with the current roster:\n\n"
            + "\n".join(f"- {r}" for r in reasons)
        )
        return None

    customized_params = st.session_state.get("customized_params") or {}
    selections: list[CustomizedAgentSelection] = []
    for agent in selected_agents:
        agent_type = agent["agent_type"]
        engine = st.session_state.get(
            f"market_engine_{agent_type}",
            ALL_ENGINES[0],
        )
        params = customized_params.get(agent_type, {}).get(engine, {}) or {}
        selections.append(
            CustomizedAgentSelection(
                archetype=agent_type,
                display_name=agent["display_name"],
                engine=engine,
                params=dict(params),
                num_instances=1,
            )
        )

    try:
        # Carry any user-adjusted round count from the variant_choice page
        # into the generated bundle (None => keep the shipped count).
        edited_rounds = st.session_state.get(f"variant_rounds_{scenario_base}")
        result = write_customized_bundle(
            selections=selections,
            scenario_name=scenario_base,
            project_root=PROJECT_ROOT,
            total_rounds=(
                int(edited_rounds) if edited_rounds is not None else None
            ),
        )
    except Exception as exc:
        st.error(f"Failed to materialise customized bundle: {exc}")
        return None

    st.session_state.customized_dir_id = result.customized_id
    st.toast(
        f"Customized bundle written: {result.customized_id} "
        f"(scenario {scenario_base})",
        icon="✨",
    )
    return f"CUSTOMIZED_SIMULATION/{result.customized_id}"


def render_selected_market_strip() -> None:
    """Render the selected market agents in the simulation workspace."""
    _inject_market_styles()
    catalog = load_agent_catalog(_agent_catalog_signature())
    selected = set(st.session_state.get("selected_market_agents", []))
    agents = [agent for agent in catalog if agent["agent_type"] in selected]
    if not agents:
        return

    heading, action = st.columns([5, 1])
    with heading:
        st.caption("Selected market agents")
        _render_market_chips(agents)
    with action:
        if st.button("Edit market", use_container_width=True):
            st.session_state.workflow_stage = "customize"
            st.session_state.current_page = "Simulation"
            st.rerun()


# ---------------------------------------------------------------------------
# Public alias (used by app.py)
# ---------------------------------------------------------------------------
render_scenario_setup = render_entry_choice
