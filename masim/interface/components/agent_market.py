"""Agent Market and experiment setup workflow for the Streamlit interface."""

from __future__ import annotations

import base64
import html
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote  # noqa: F401 – kept for potential external use

import streamlit as st

from ..config_loader import (
    discover_scenario_groups,
    get_agents_info,
    get_finance_scenario_content,
    get_finance_scenario_path,
    get_market_description,
    get_market_type,
    get_phenomenon_description,
    get_scenario_info,
    get_simulation_bases_content,
    get_simulation_bases_path,
    get_topology_info,
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
OPINION_ROOT = AGENT_POOL_ROOT / "opinion"
PROFILE_ROOT = FINANCE_ROOT
CATALOG_PATH = IMAGE_ROOT / "agent_avatar_map.json"

# All domain directories to scan for agent profiles.
_DOMAIN_ROOTS: list[tuple[str, Path]] = [
    ("finance", FINANCE_ROOT),
    ("opinion", OPINION_ROOT),
]

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
    paths: list[Path] = []
    if CATALOG_PATH.exists():
        paths.append(CATALOG_PATH)
    if ICON_ROOT.exists():
        paths.extend(sorted(ICON_ROOT.glob("*.png")))
    for _domain, root in _DOMAIN_ROOTS:
        if root.exists():
            paths.extend(sorted(root.glob("*.md")))
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
        mode = st.session_state.get("mode", "")
        project_name = st.session_state.get("project_name", "")
        if mode == "project" and project_name:
            st.markdown(f"**Project:** {project_name}")
        elif mode == "experience":
            st.markdown("**Mode:** Experience")
        st.markdown("---")
        st.markdown("~~Stage 0. Choose a mode~~")
        st.markdown("**Stage 1.** Pick a scenario")
        st.caption(f"{scenario_count} scenarios available")
        if mode == "experience":
            st.markdown("**Stage 2.** Select engine and run")
        else:
            st.markdown("**Stage 2.** Default or customize")
        st.markdown("---")
        if st.button("\u2190 Back to welcome", width="stretch"):
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
        mode = st.session_state.get("mode", "")
        project_name = st.session_state.get("project_name", "")
        if mode == "project" and project_name:
            st.markdown(f"**Project:** {project_name}")
        elif mode == "experience":
            st.markdown("**Mode:** Experience")
        st.markdown("---")
        st.markdown("~~Stage 1. Pick a scenario~~")
        if mode == "experience":
            st.markdown("**Stage 2.** Select engine and run")
        else:
            st.markdown("**Stage 2.** Default or customize")
        st.markdown("---")
        if st.button("\u2190 Back to scenarios", width="stretch"):
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
    is_experience = st.session_state.get("mode") == "experience"

    name_col, rounds_col, features_col = st.columns([3, 1, 2])
    with name_col:
        st.markdown(
            f"<div class='scenario-confirm-chip'>\u2713 "
            f"{html.escape(scenario_display_name(selected_base))}"
            f"</div>",
            unsafe_allow_html=True,
        )
    with rounds_col:
        try:
            shipped_rounds = int(info.get("total_rounds") or 0)
        except (TypeError, ValueError):
            shipped_rounds = 0
        # Rounds are locked to the value shipped with the scenario —
        # the user picks the market, not the schedule length.
        st.metric("Rounds", shipped_rounds if shipped_rounds > 0 else "\u2014")
    with features_col:
        feats = scenario_market_features(selected_base)
        st.metric(
            "Market features",
            ", ".join(sorted(feats)) if feats else "standard",
        )

    # --- Market situation explainer -----------------------------------
    # Spell out what the "Market features" metric above means so users
    # understand what the simulated market looks like before picking an
    # engine. "standard" is the baseline state every scenario ships;
    # anything extra is listed as additional feature streams.
    feats_now = scenario_market_features(selected_base)
    _STANDARD_MARKET = (
        "<b>standard</b> — every agent sees the baseline market state: "
        "<code>price</code>, <code>prev_price</code>, <code>fundamental</code>, "
        "<code>deviation</code>, <code>round</code>. No extra data feeds are "
        "broadcast; agents trade a single asset on price signals alone."
    )
    _FEATURE_DOCS = {
        "credit_spread": (
            "broadcasts a credit-spread series alongside price, letting "
            "agents react to funding stress and default risk."
        ),
        "multi_asset": (
            "exposes two or more correlated assets, so agents can rotate "
            "between markets instead of trading a single instrument."
        ),
        "microstructure_book": (
            "streams limit-order-book depth (bids / asks / imbalance) so "
            "agents can react to liquidity and short-horizon flow."
        ),
        "tranche_metrics": (
            "publishes structured-credit tranche metrics (attachment, "
            "detachment, expected loss) for securitization scenarios."
        ),
        "defi_protocol": (
            "exposes on-chain protocol state (peg, reserves, redemption "
            "queue) so agents can react to DeFi-specific dynamics."
        ),
        "vol_surface": (
            "streams a volatility surface (ATM vol, skew, term structure) "
            "so agents can trade options / vol products."
        ),
    }
    if feats_now:
        rows = "".join(
            f"<li style='margin:2px 0;'><code>{html.escape(f)}</code> — "
            f"{_FEATURE_DOCS.get(f, 'extra feature stream exposed to agents.')}"
            f"</li>"
            for f in sorted(feats_now)
        )
        situation_body = (
            f"<div style='font-size:12.5px;line-height:1.6;color:#374955;'>"
            f"{_STANDARD_MARKET}<br/>"
            f"<span style='color:#1a2633;font-weight:600;'>Plus:</span>"
            f"<ul style='margin:4px 0 0 20px;padding:0;'>{rows}</ul>"
            f"</div>"
        )
    else:
        situation_body = (
            f"<div style='font-size:12.5px;line-height:1.6;color:#374955;'>"
            f"{_STANDARD_MARKET}"
            f"</div>"
        )
    st.markdown(
        "<div style='margin-top:6px;padding:10px 14px;"
        "background:#fbfcfd;border:1px dashed #dde4ea;border-radius:8px;'>"
        "<div style='font-size:12px;font-weight:700;color:#1a2633;"
        "letter-spacing:0.03em;text-transform:uppercase;margin-bottom:6px;'>"
        "Market situation</div>"
        + situation_body
        + "</div>",
        unsafe_allow_html=True,
    )

    # --- Simulation scenario description ------------------------------
    # Explicitly spell out (1) what phenomenon this scenario simulates,
    # (2) what market is being modeled and (3) how the market dynamic is
    # modeled, so users understand the simulation before picking a
    # decision engine. The scenario brief comes from the canonical
    # ``examples/{Scenario}/simulation-bases.md`` (Phenomenon Name row),
    # and a click-through opens the full ``finance-{scenario}.md``
    # target-spec definition file in a dialog.
    market_type = get_market_type(selected_base)
    market_desc = get_market_description(selected_base)
    scenario_desc = info.get("description", "")
    phenomenon_desc = get_phenomenon_description(selected_base)
    finance_path = get_finance_scenario_path(selected_base)

    if (
        market_type
        or market_desc
        or scenario_desc
        or phenomenon_desc
    ):
        st.markdown(
            "<div style='margin-top:12px;padding:14px 16px;"
            "background:#f7f9fc;border:1px solid #dde4ea;border-radius:8px;'>"
            "<div style='font-size:13px;font-weight:700;color:#1a2633;"
            "margin-bottom:8px;'>Simulation scenario</div>"
            + (
                f"<div style='font-size:13px;line-height:1.65;color:#374955;"
                f"margin-bottom:6px;'>"
                f"<b>Phenomenon:</b> {html.escape(phenomenon_desc)}"
                f"</div>"
                if phenomenon_desc
                else ""
            )
            + (
                f"<div style='font-size:13px;line-height:1.65;color:#374955;"
                f"margin-bottom:6px;'>"
                f"<b>Market modeled:</b> {html.escape(market_type)}"
                f"</div>"
                if market_type
                else ""
            )
            + (
                f"<div style='font-size:13px;line-height:1.65;color:#374955;"
                f"margin-bottom:6px;'>"
                f"<b>Market dynamics:</b> {html.escape(market_desc)}"
                f"</div>"
                if market_desc
                else ""
            )
            + (
                f"<div style='font-size:13px;line-height:1.65;color:#374955;'>"
                f"<b>Simulation focus:</b> {html.escape(scenario_desc)}"
                f"</div>"
                if scenario_desc
                else ""
            )
            + "</div>",
            unsafe_allow_html=True,
        )

        # Click-through to the canonical finance-{scenario}.md definition.
        # Rendered as a scoped text-link button beneath the info card so
        # users can drill into the full target-spec scenario definition
        # (meta, phenomenon statement, anchors, stylized facts, historical
        # anchors, roster, environment, parameters, variants, references).
        if finance_path is not None:
            st.markdown(
                "<style>"
                '[class*="st-key-view_bases_"] button{'
                'background:transparent !important;'
                'border:none !important;box-shadow:none !important;'
                'padding:2px 0 !important;margin:2px 0 6px 2px !important;'
                'min-height:0 !important;height:auto !important;'
                'color:#2a5fa6 !important;font-weight:600 !important;'
                'font-size:12.5px !important;text-align:left !important;'
                'justify-content:flex-start !important;'
                '}'
                '[class*="st-key-view_bases_"] button:hover{'
                'color:#1a4a8f !important;text-decoration:underline !important;'
                'background:transparent !important;'
                '}'
                "</style>",
                unsafe_allow_html=True,
            )
            finance_rel = finance_path.name
            with st.container(key=f"view_bases_{selected_base}"):
                if st.button(
                    f"\U0001f4d6  View the full scenario definition ({finance_rel}) \u2192",
                    key=f"btn_view_bases_{selected_base}",
                    help=(
                        f"Open examples/{selected_base}/{finance_rel} "
                        "\u2014 phenomenon statement, anchors, stylized facts, "
                        "roster, environment, parameters, and references."
                    ),
                    type="tertiary",
                ):
                    _show_finance_scenario_dialog(selected_base)

    st.divider()
    
    if is_experience:
        # Experience mode: comprehensive read-only display + engine buttons.
        probe_key = _scenario_probe_key(selected_base, groups)
        agents = get_agents_info(probe_key)
        # Filter out the market coordinator for display.
        player_agents = [a for a in agents if a["role"] != "coordinator"]

        roster_col, topo_col = st.columns([3, 2], gap="medium")

        with roster_col:
            st.markdown("**Agents in this scenario**")
            if player_agents:
                total_instances = sum(a["instances"] for a in player_agents)
                st.caption(
                    f"{len(player_agents)} agent types, "
                    f"{total_instances} total instances — click any agent name "
                    "to view its design profile"
                )
                # Scoped CSS:
                # * .masim-avatar-img / .masim-avatar-fallback: pure visual
                #   avatar (non-interactive).
                # * .st-key-agent_label_<pid> button: the AGENT NAME beside
                #   the avatar is the click target, styled as a compact
                #   text-link (transparent background, no border, hover
                #   underline + blue).
                st.markdown(
                    "<style>"
                    '.masim-avatar-img{'
                    'width:56px;height:56px;border-radius:50%;'
                    'border:2px solid #dde4ea;'
                    'box-shadow:0 1px 3px rgba(0,0,0,0.08);'
                    'object-fit:cover;display:block;background:#e8f0fb;'
                    '}'
                    '.masim-avatar-fallback{'
                    'width:56px;height:56px;border-radius:50%;'
                    'border:2px solid #dde4ea;'
                    'box-shadow:0 1px 3px rgba(0,0,0,0.08);'
                    'display:flex;align-items:center;justify-content:center;'
                    'background:#e8f0fb;color:#2a5fa6;font-weight:700;'
                    'font-size:0.85rem;'
                    '}'
                    # Zero out every wrapper Streamlit adds around the
                    # label button so the box shrinks to the text glyphs.
                    '[class*="st-key-agent_label_"],'
                    '[class*="st-key-agent_label_"] .stElementContainer,'
                    '[class*="st-key-agent_label_"] div[data-testid="stElementContainer"],'
                    '[class*="st-key-agent_label_"] div[data-testid="stButton"]{'
                    'gap:0 !important;margin:0 !important;padding:0 !important;'
                    '}'
                    # The button itself: pill-shaped text label with a
                    # subtle gray background frame.
                    '[class*="st-key-agent_label_"] button{'
                    'background:#eef1f4 !important;'
                    'border:1px solid #dde4ea !important;'
                    'box-shadow:none !important;'
                    'border-radius:6px !important;'
                    'padding:4px 8px !important;margin:0 !important;'
                    'min-height:0 !important;height:auto !important;'
                    'width:auto !important;max-width:100% !important;'
                    'color:#374955 !important;font-weight:600 !important;'
                    'text-align:left !important;'
                    'justify-content:flex-start !important;'
                    'white-space:normal !important;'
                    'word-break:break-word !important;'
                    '}'
                    # Universal descendant: force compact font-size and
                    # tight line-height on EVERY inner wrapper.
                    '[class*="st-key-agent_label_"] button,'
                    '[class*="st-key-agent_label_"] button *{'
                    'font-size:0.7rem !important;'
                    'line-height:1.15 !important;'
                    '}'
                    '[class*="st-key-agent_label_"] button p,'
                    '[class*="st-key-agent_label_"] button div{'
                    'margin:0 !important;padding:0 !important;'
                    'font-weight:600 !important;color:inherit !important;'
                    '}'
                    '[class*="st-key-agent_label_"] button:hover,'
                    '[class*="st-key-agent_label_"] button:hover *{'
                    'color:#2a5fa6 !important;'
                    'background:#e4ecf6 !important;'
                    'border-color:#c9d6e6 !important;'
                    'text-decoration:none !important;'
                    '}'
                    "</style>",
                    unsafe_allow_html=True,
                )
                # Layout: 3 chips per row (pure-image avatar + clickable
                # text label to the right). vertical_alignment="center"
                # re-centres the compact label against the 56 px avatar.
                per_row = 3
                for row_start in range(0, len(player_agents), per_row):
                    row_agents = player_agents[row_start : row_start + per_row]
                    cols = st.columns(per_row, gap="small")
                    for col, a in zip(cols, row_agents):
                        with col:
                            player_id = a["id"]
                            archetype = _canonical_archetype(player_id)
                            icon_path = (
                                ICON_ROOT
                                / f"finance-{archetype.replace('_', '-')}.png"
                            )
                            count = a["instances"]
                            display_name = html.escape(a["name"])
                            count_suffix = (
                                f" \u00d7{count}" if count > 1 else ""
                            )
                            tip = (
                                a.get("theory")
                                or a.get("principle")
                                or "Click to view design profile"
                            )
                            avatar_col, label_col = st.columns(
                                [1, 2],
                                gap="small",
                                vertical_alignment="center",
                            )
                            with avatar_col:
                                # Pure visual avatar (non-clickable).
                                if icon_path.exists():
                                    uri = _image_data_uri(icon_path)
                                    st.markdown(
                                        f'<img class="masim-avatar-img" '
                                        f'src="{uri}" alt="{display_name}" />',
                                        unsafe_allow_html=True,
                                    )
                                else:
                                    initial = html.escape(
                                        a["name"][:2].upper()
                                        if a["name"]
                                        else "?"
                                    )
                                    st.markdown(
                                        f'<div class="masim-avatar-fallback">'
                                        f'{initial}</div>',
                                        unsafe_allow_html=True,
                                    )
                            with label_col:
                                # Clickable text label -> opens .md profile.
                                label_text = f"{a['name']}{count_suffix}"
                                with st.container(
                                    key=f"agent_label_{player_id}"
                                ):
                                    clicked = st.button(
                                        label_text,
                                        key=f"btn_agent_label_{player_id}",
                                        help=tip,
                                        type="tertiary",
                                    )
                                    if clicked:
                                        _show_agent_profile_dialog(a)
            else:
                st.caption("No agent information available.")

        with topo_col:
            st.markdown("**Network topology**")
            from .topology_d3 import render_d3_topology
            topo = get_topology_info(probe_key)
            if topo["nodes"]:
                render_d3_topology(topo, agents, height=420)
            else:
                st.caption("No topology data available.")

        st.divider()

        # Engine buttons.
        variant_keys = groups.get(selected_base) or []
        st.markdown("**Select a decision engine to run**")
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
                        width="stretch",
                        help=(
                            f"Run {scenario_display_name(selected_base)} "
                            f"with the {variant} decision engine."
                        ),
                    ):
                        _launch_default_variant(key)
    else:
        # Project mode: Default + Customized side by side.
        default_col, custom_col = st.columns(2, gap="large")

        with default_col:
            variant_keys = groups.get(selected_base) or []
            st.markdown("**Default**")
            st.caption(
                "Launch the pre-configured scenario directly. "
                "The diagram below previews the shipped agent lineup and "
                "network topology; each button below launches a decision "
                "engine."
            )

            # Dynamic topology preview mirroring Experience mode. It gives
            # the user an at-a-glance sense of the shipped agent roster and
            # how the agents connect before they commit to a decision engine.
            probe_key = _scenario_probe_key(selected_base, groups)
            default_agents = get_agents_info(probe_key)
            default_topo = get_topology_info(probe_key)
            if default_topo.get("nodes"):
                from .topology_d3 import render_d3_topology
                render_d3_topology(default_topo, default_agents, height=340)
            else:
                st.caption("No topology data available for this scenario.")

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
                            width="stretch",
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
                "Select agents for simulation \u2192",
                key="stage2_go_customize",
                type="primary",
                width="stretch",
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


# Variant prefixes attached to identity strings in scenario configs.
# Assets (icons, .md profiles) are keyed by the pure archetype stem, so the
# prefix is stripped before path resolution.
_VARIANT_PREFIXES: tuple[str, ...] = ("rule_", "llm_", "rulellm_", "ragllm_")


def _canonical_archetype(player_id: str) -> str:
    """Strip a known ``{variant}_`` prefix, returning the pure archetype stem."""
    for prefix in _VARIANT_PREFIXES:
        if player_id.startswith(prefix):
            return player_id[len(prefix):]
    return player_id


@st.dialog("Agent design profile", width="large")
def _show_agent_profile_dialog(agent: dict) -> None:
    """Modal that renders the full agent .md profile.

    Loads the file from ``examples/AGENT_POOL/{domain}/{player_id_kebab}.md``.
    Supports both finance/ and opinion/ domains.
    Falls back to a caption when the profile file does not exist.
    """
    player_id = agent["id"]
    archetype = _canonical_archetype(player_id)
    md_stem = archetype.replace("_", "-")

    # Resolve icon from the correct domain.
    icon_path: Path | None = None
    for domain, _root in _DOMAIN_ROOTS:
        candidate = ICON_ROOT / f"{domain}-{md_stem}.png"
        if candidate.exists():
            icon_path = candidate
            break
    if icon_path is None:
        icon_path = ICON_ROOT / f"finance-{md_stem}.png"

    header_cols = st.columns([1, 6], gap="small")
    with header_cols[0]:
        if icon_path.exists():
            st.image(str(icon_path), width=56)
    with header_cols[1]:
        st.markdown(f"### {agent['name']}")
        subtitle = agent.get("theory") or agent.get("principle") or ""
        if subtitle:
            st.caption(subtitle)
        instances = agent.get("instances", 1)
        if instances > 1:
            st.caption(f"{instances} instances in this scenario")
    st.divider()

    # Resolve profile .md from the correct domain directory.
    md_path: Path | None = None
    for _domain, root in _DOMAIN_ROOTS:
        candidate = root / f"{md_stem}.md"
        if candidate.exists():
            md_path = candidate
            break
    if md_path and md_path.exists():
        st.markdown(md_path.read_text(encoding="utf-8"))
    else:
        st.caption(
            f"No profile file found at examples/AGENT_POOL/*/{ md_stem}.md."
        )


@st.dialog("Scenario simulation definition", width="large")
def _show_finance_scenario_dialog(scenario_base: str) -> None:
    """Modal that renders the ``finance-{scenario}.md`` target spec.

    The file lives at ``examples/{scenario_base}/finance-{name}.md`` and
    is the reverse-reconstructed / target-spec scenario definition
    (meta, phenomenon statement, anchors, stylized facts, historical
    anchors, roster, environment, parameters, variants, references).
    Rendering it in a dialog lets users drill into the full definition
    without leaving the ``Choose how to run it`` page.
    """
    display = scenario_display_name(scenario_base)
    st.markdown(f"### \U0001f4d6 {html.escape(display)} \u2014 scenario definition")
    path = get_finance_scenario_path(scenario_base)
    if path is None:
        st.warning(
            f"No `finance-*.md` scenario definition found for **{display}**."
        )
        st.info(
            f"Expected at: `examples/{scenario_base}/finance-<name>.md`"
        )
        return
    st.caption(f"Source: `examples/{scenario_base}/{path.name}`")
    st.divider()
    content = get_finance_scenario_content(scenario_base) or ""
    # Strip the leading H1 title \u2014 we already show a header above.
    lines = content.split("\n")
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    st.markdown("\n".join(lines).lstrip("\n"))


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
    """Load agent metadata and profiles from all domain directories + icons/.

    The canonical agent pool is the set of ``{domain}/*.md`` specs that
    have a matching ``agent_images/icons/{domain}-<stem>.png`` icon.
    When an explicit ``agent_avatar_map.json`` exists it takes precedence.
    """
    if CATALOG_PATH.exists():
        raw_items = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    else:
        raw_items = []
        for domain, root in _DOMAIN_ROOTS:
            if not root.exists():
                continue
            for md_path in sorted(root.glob("*.md")):
                icon_name = f"{domain}-{md_path.stem}.png"
                if (ICON_ROOT / icon_name).exists():
                    raw_items.append(
                        {
                            "agent_type": md_path.stem,
                            "display_name": _kebab_to_title(md_path.stem),
                            "image_path": f"icons/{icon_name}",
                            "source_profile": str(md_path),
                            "domain": domain,
                        }
                    )

    catalog: list[dict[str, Any]] = []
    for item in raw_items:
        agent_type = item["agent_type"]
        display_name = item.get("display_name", agent_type)
        image_path = IMAGE_ROOT / item.get("image_path", f"png/{agent_type}.png")
        domain = item.get("domain", "finance")

        source_value = item.get("source_profile", "")
        source_path = Path(source_value)
        if not source_path.is_absolute():
            source_path = (IMAGE_ROOT / source_path).resolve()
        if not source_path.exists():
            # Fallback: look in the domain-specific directory
            domain_root = AGENT_POOL_ROOT / domain
            source_path = domain_root / f"{agent_type}.md"

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
        /* Agent-grid card buttons: compact sizing to match full-width icons. */
        [class*="st-key-market_profile_"] button {
            font-size: 0.72rem !important;
            padding: 3px 6px !important;
            min-height: 0 !important;
            height: auto !important;
            line-height: 1.25 !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 100%;
        }
        [class*="st-key-market_customize_"] button {
            font-size: 0.7rem !important;
            padding: 4px 8px !important;
            min-height: 0 !important;
            height: auto !important;
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


def _render_customize_sidebar(
    scenario_base: str,
    selected_agents: list[dict[str, Any]],
) -> None:
    """Sidebar shown during the Stage-2 customize flow.

    Surfaces the locked scenario at the top so the user always knows
    which simulation they are building agents for; the only navigation
    out of this stage is the back button rendered in the main column.

    A compact **Live market preview** panel is embedded here so the user
    can see the current market topology while scrolling the agent grid.
    It re-renders on every checkbox toggle in the main column.
    """
    with st.sidebar:
        st.title("MASIM")
        st.caption("Investment workflow")
        st.markdown("---")
        st.markdown("**✓ Stage 1.** Scenario")
        st.caption(scenario_display_name(scenario_base) if scenario_base else "—")
        st.markdown("**Stage 2.** Select agents")
        st.caption(f"{len(selected_agents)} agents in market")
        st.markdown("---")
        st.markdown("**Live market preview**")
        _render_live_market_preview(selected_agents, height=280)
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
            width="stretch",
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
        if st.button("Close", width="stretch", key="close_market_profile"):
            _clear_query_agent()
            st.rerun()

    image_col, profile_col = st.columns([1, 2.8], gap="large")
    with image_col:
        if Path(agent["image_file"]).exists():
            st.image(agent["image_file"], width=200)
        st.caption(agent["agent_type"])
    with profile_col:
        st.markdown(
            f'<div class="profile-banner">{html.escape(agent["intro"])}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(agent["profile_markdown"] or "Profile content is unavailable.")
    st.divider()


@st.dialog("Agent design profile", width="large")
def _show_catalog_agent_profile_dialog(agent: dict[str, Any]) -> None:
    """Modal that renders a full agent .md profile from the catalog dict.

    This is the customize-page variant of the dialog. It receives a
    catalog entry (with keys ``agent_type``, ``display_name``,
    ``image_file``, ``profile_markdown``, ``domain``, ``intro``) and
    renders the profile in a dialog overlay — preserving session state.
    """
    header_cols = st.columns([1, 6], gap="small")
    with header_cols[0]:
        img = Path(agent["image_file"])
        if img.exists():
            st.image(str(img), width=56)
    with header_cols[1]:
        st.markdown(f"### {agent['display_name']}")
        st.caption(agent.get("archetype", agent["agent_type"]))
    st.divider()
    st.markdown(agent.get("profile_markdown") or "Profile content is unavailable.")


def _load_param_specs(agent: dict[str, Any]) -> list[ParamSpec]:
    """Return the parsed Parameters table for an agent (cached on disk mtime)."""
    profile_path = agent.get("profile_file")
    if not profile_path:
        return []
    return parse_parameters_file(profile_path)


@st.dialog("Customize Agent", width="large")
def _show_customize_dialog(agent: dict[str, Any]) -> None:
    """Dialog overlay for agent customization.

    Opened by the Customize button on each agent card. Replaces the
    previous layout-reshuffling approach (panel_col + grid_col) with a
    lightweight modal that doesn't force a full grid re-render.
    """
    _render_param_panel(agent)


def _render_param_panel(agent: dict[str, Any]) -> None:
    """Render the editable parameter panel for an agent.

    Can be called standalone (inside a dialog, container, or column).

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
        if st.button(primary_label, type="primary", width="stretch",
                     key=f"customized_add_{agent_type}"):
            persisted.clear()
            persisted.update(edited)
            st.session_state[f"market_agent_{agent_type}"] = True
            st.toast(f"{agent['display_name']} → market", icon="✅")
            st.rerun()
    with btn_reset:
        if st.button("Reset", width="stretch",
                     key=f"customized_reset_{agent_type}"):
            persisted.clear()
            for sub_key in list(st.session_state.keys()):
                if sub_key.startswith(f"customized_input_{agent_type}_{engine}_"):
                    del st.session_state[sub_key]
            st.rerun()
    with btn_close:
        if st.button("Close", width="stretch",
                     key=f"customized_close_{agent_type}"):
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

    Performance-critical: rendered ~200 times per page load.

    Image uses ``st.image(path, use_container_width=True)`` so Streamlit
    deduplicates the binary across reruns (browser-cached) and renders
    at full column width, preserving source resolution on Retina
    displays.

    Clicking the agent name opens the profile in a dialog overlay.
    The Customize button opens the parameter dialog — no grid
    reshuffling required.
    """
    agent_type = agent["agent_type"]
    selected = bool(st.session_state.get(f"market_agent_{agent_type}", False))

    # --- Image (browser-cached, full-column width) -------------------
    img_path = Path(agent["image_file"])
    if img_path.exists():
        st.image(str(img_path), use_container_width=True)
    else:
        st.markdown(
            "<div style='width:100%;aspect-ratio:1/1;border-radius:8px;"
            "background:#e8f0fb;display:flex;align-items:center;"
            "justify-content:center;color:#2a5fa6;font-weight:700;"
            f"font-size:1.4rem;'>{agent['display_name'][0]}</div>",
            unsafe_allow_html=True,
        )

    # --- Selection badge (compact pill beneath image) ----------------
    badge = (
        "<div style='text-align:center;margin:4px 0 2px;'>"
        "<span style='display:inline-block;font-size:0.68rem;padding:2px 8px;"
        "border-radius:10px;background:#d4edda;color:#155724;font-weight:600;'>"
        "\u2713 in market</span></div>"
        if selected
        else "<div style='text-align:center;margin:4px 0 2px;'>"
        "<span style='display:inline-block;font-size:0.68rem;padding:2px 8px;"
        "border-radius:10px;background:#f0f2f4;color:#6c757d;'>"
        "not selected</span></div>"
    )
    st.markdown(badge, unsafe_allow_html=True)

    # --- Agent name: clickable text button -> opens profile dialog ---
    if st.button(
        agent["display_name"],
        key=f"market_profile_{agent_type}",
        type="tertiary",
        help=agent.get("intro", "View this agent's design profile"),
    ):
        _show_catalog_agent_profile_dialog(agent)

    # --- Customize: opens the parameter dialog (no grid reshuffle) ---
    if st.button(
        "Customize",
        key=f"market_customize_{agent_type}",
        width="stretch",
        help="Open this agent's parameter and engine editor.",
    ):
        _show_customize_dialog(agent)


def _class_to_agent_type(class_name: str) -> str:
    """Convert a PascalCase player class name to a kebab-case md stem.

    Examples:
        ``AnchoredTrader`` -> ``anchored-trader``
        ``LLMAnchoredTrader`` -> ``anchored-trader`` (leading LLM prefix
        stripped so both Rule and LLM variants map to the same profile).
    """
    name = class_name.split(":")[-1]
    if name.startswith("LLM") and len(name) > 3 and name[3].isupper():
        name = name[3:]
    # Insert hyphens between lowercase/digit and uppercase boundaries.
    kebab = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", name)
    return kebab.lower()


def _default_agent_types_for_scenario(
    scenario_base: str,
    catalog: list[dict[str, Any]],
) -> tuple[list[str], list[str]]:
    """Return (available, missing) agent_types for the scenario's Rule default.

    ``available`` are catalog agent_types that map to a default player class
    and can be checked in the market grid. ``missing`` are class names whose
    kebab form has no matching entry in the AGENT_POOL catalog (usually
    because the icon has not been authored yet).
    """
    probe_key = _scenario_probe_key(scenario_base, discover_scenario_groups())
    agents = get_agents_info(probe_key)
    catalog_types = {agent["agent_type"] for agent in catalog}

    available: list[str] = []
    missing: list[str] = []
    seen: set[str] = set()
    for info in agents:
        if info.get("role") == "coordinator":
            continue
        class_str = info.get("class", "") or ""
        if not class_str:
            continue
        kebab = _class_to_agent_type(class_str)
        if not kebab or kebab in seen:
            continue
        seen.add(kebab)
        if kebab in catalog_types:
            available.append(kebab)
        else:
            missing.append(class_str.split(":")[-1] or kebab)
    return available, missing


def _render_live_market_preview(
    selected_agents: list[dict[str, Any]],
    height: int = 260,
) -> None:
    """Render a compact star topology of the currently selected agents.

    Uses the same D3 renderer that powers the Experience mode topology,
    fed a synthetic ``market`` hub with a spoke to each selected agent.
    Icons are supplied via the ``icon_uris`` override so opinion-domain
    agents (whose icons are ``opinion-*.png``) render correctly too.
    """
    from .topology_d3 import render_d3_topology

    if not selected_agents:
        st.caption(
            "No agents selected yet. Click **Load default agents** or pick "
            "agents from the grid to preview the market topology here."
        )
        return

    node_ids = [a["agent_type"] for a in selected_agents]
    topology = {
        "topology_type": "star",
        "sources": ["market"],
        "nodes": ["market"] + node_ids,
        "connections": {"market": node_ids},
    }
    agent_records = [
        {
            "id": a["agent_type"],
            "name": a["display_name"],
            "theory": a.get("archetype", ""),
            "instances": 1,
            "role": "player",
        }
        for a in selected_agents
    ]
    icon_uris = {
        a["agent_type"]: a.get("image_uri", "") for a in selected_agents
    }
    render_d3_topology(topology, agent_records, height=height, icon_uris=icon_uris)


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

    # Compute the current selection ONCE up front so the sidebar preview and
    # the main-column grid share a single source of truth. The preview lives
    # in the sidebar (see _render_customize_sidebar) and re-renders on every
    # rerun triggered by a checkbox toggle in the grid.
    selected_types_now = _selected_types(catalog)
    selected_agents_now = [
        a for a in catalog if a["agent_type"] in set(selected_types_now)
    ]

    _render_customize_sidebar(scenario_base, selected_agents_now)

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

    # Pre-compute the Default preset targets. The selection snapshot
    # (selected_agents_now / selected_types_now) was already computed above,
    # before the sidebar preview was rendered.
    default_available, default_missing = _default_agent_types_for_scenario(
        scenario_base, catalog
    )

    # Compact row directly beneath the chip: just the Default preset button.
    # The live topology preview lives in the left sidebar and updates every
    # time an agent is toggled in the grid below.
    default_btn_col, _spacer = st.columns([1, 3])
    with default_btn_col:
        default_help = (
            "Auto-select the agents shipped with this scenario's Default "
            "configuration (" + str(len(default_available)) + " available)."
        )
        if default_missing:
            default_help += (
                " Not in pool yet: " + ", ".join(default_missing) + "."
            )
        if st.button(
            "Load default agents",
            width="stretch",
            disabled=not default_available,
            key="customize_load_default_top",
            help=default_help,
        ):
            wanted = set(default_available)
            for agent in catalog:
                st.session_state[f"market_agent_{agent['agent_type']}"] = (
                    agent["agent_type"] in wanted
                )
            st.session_state.selected_market_agents = list(default_available)
            st.rerun()

    st.write(
        "Select the agents you want in the simulation. Click an agent's "
        "**name** to view its profile, use **Customize** to edit its "
        "parameters, and (for LLM engines) tweak the persona / per-round "
        "prompt. Each agent's decision engine is set per-card. The "
        "**Live market preview** in the left sidebar updates automatically."
    )

    # Legacy inline profile (query-param based) kept for bookmarked URLs.
    requested_agent = _query_agent()
    by_type = {agent["agent_type"]: agent for agent in catalog}
    if requested_agent in by_type:
        _render_profile(by_type[requested_agent])

    selected_before = _selected_types(catalog)

    # ---- Agent grid: wrapped in @st.fragment for scoped reruns ------
    # Only search / grid widgets trigger fragment-local reruns.
    # Full-page reruns (sidebar preview, Load default, Clear, Launch)
    # still happen through their own buttons outside this scope.
    @st.fragment
    def _agent_grid_fragment() -> None:
        controls, count = st.columns([4, 1])
        with controls:
            search = st.text_input(
                "Search agents",
                placeholder="Search by name, role, or scenario",
                label_visibility="collapsed",
            )
        with count:
            st.metric("Selected", len(_selected_types(catalog)))

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
            grid_columns_per_row = 6
            for start in range(0, len(filtered), grid_columns_per_row):
                columns = st.columns(grid_columns_per_row, gap="small")
                for column, agent in zip(
                    columns, filtered[start : start + grid_columns_per_row]
                ):
                    with column:
                        _render_agent_card(agent)

    _agent_grid_fragment()

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
            width="stretch",
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
            width="stretch",
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
        # In Project mode we replace the plain ``standard`` fallback with
        # ``customizable`` to signal that the scenario can be tailored
        # (rounds, agents, params) on the following stages.
        feats = scenario_market_features(scenario_base)
        if feats:
            feats_text = ", ".join(sorted(feats))
        else:
            mode = st.session_state.get("mode", "experience")
            feats_text = (
                "customizable" if mode == "project" else "standard"
            )
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
            width="stretch",
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
        if st.button("Edit market", width="stretch"):
            st.session_state.workflow_stage = "customize"
            st.session_state.current_page = "Simulation"
            st.rerun()


# ---------------------------------------------------------------------------
# Public alias (used by app.py)
# ---------------------------------------------------------------------------
render_scenario_setup = render_entry_choice
