"""Agent Market and experiment setup workflow for the Streamlit interface."""

from __future__ import annotations

import base64
import functools
import html
import json
import re
from pathlib import Path
from typing import Any, Dict
from urllib.parse import quote  # noqa: F401 – kept for potential external use

import streamlit as st

from ..config_loader import (
    CATEGORY_DESCRIPTIONS,
    CATEGORY_LABELS,
    CATEGORY_ORDER,
    discover_scenario_groups,
    discover_scenarios_by_category,
    get_agents_info,
    get_finance_scenario_content,
    get_finance_scenario_path,
    get_market_archetype,
    get_market_description,
    get_market_icon_path,
    get_market_type,
    get_phenomenon_description,
    get_rulellm_prompt_for_agent,
    get_scenario_info,
    get_topology_info,
    resolve_scenario_rulellm_prompts,
    scenario_display_name,
)
from ..customized import (
    CustomizedAgentSelection,
    RosterEntry,
    add_entry,
    apply_customized_modifications,
    apply_default_bundle_overrides,
    clear_roster,
    compose_bundle_name,
    copy_default_scenario_bundle,
    duplicate_entry,
    entries_for_type,
    extract_default_players,
    extract_market_extras,
    find_entry,
    get_default_prompts,
    get_roster,
    initialize_customized_folder,
    is_archetype_supported,
    is_scenario_compatible,
    migrate_from_legacy_state,
    parse_parameters_file,
    remove_entry,
    required_features,
    restore_state_to_session,
    save_state_from_session,
    scenario_market_features,
    set_roster,
    total_instances,
    unique_agent_types,
    update_entry,
    write_customized_bundle,
)
from ..customized.handbook_params import ParamSpec
from .team_gate import current_team


PROJECT_ROOT = Path(__file__).resolve().parents[3]
AGENT_POOL_ROOT = PROJECT_ROOT / "examples" / "AGENT_POOL"
IMAGE_ROOT = AGENT_POOL_ROOT / "agent_images"
ICON_ROOT = IMAGE_ROOT / "icons"
# Market coordinator icons live one level under the participant-icon root.
# Filename convention: {market-type}-{coordinator-stem}.png (see
# masim/skills/market-icon-generation-skill.md). Path resolution for a
# given scenario is delegated to config_loader.get_market_icon_path(),
# which reads the ``archetype:`` field from the scenario's players.yml.
MARKET_ICON_ROOT = ICON_ROOT / "market"
FINANCE_ROOT = AGENT_POOL_ROOT / "finance"
OPINION_ROOT = AGENT_POOL_ROOT / "opinion"
PROFILE_ROOT = FINANCE_ROOT


# All domain directories to scan for agent profiles.
_DOMAIN_ROOTS: list[tuple[str, Path]] = [
    ("finance", FINANCE_ROOT),
    ("opinion", OPINION_ROOT),
]

VARIANT_DISPLAY = {
    "Rule": "Rule",
    "LLM": "LLM",
    "RuleLLM": "RuleLLM (📖 sample)",
    "Rag": "RAG",
}

# Tooltip / help text for the disabled Rag engine — visible when hovering
# the greyed-out button so students understand *why* it is unavailable.
DISABLED_ENGINE_HELP: Dict[str, str] = {
    "Rag": (
        "🔒 Retrieval-Augmented Generation (RAG) is temporarily unavailable "
        "in this teaching build. It will return once the knowledge-base "
        "backend is finalised."
    ),
}

# Explanatory text shown near the RuleLLM engine wherever it is selectable —
# tells students RuleLLM is a read-only sample, not something to edit.
RULELLM_SAMPLE_NOTICE = (
    "🔒 **RuleLLM is a read-only teaching sample.** It shows how the "
    "quantitative rules from the Rule engine are embedded inside an LLM "
    "prompt (see the `== DECISION RULES ==` block). Prompts, parameters "
    "and agent counts are locked so the sample stays faithful — pick "
    "**Rule** or **LLM** if you want to modify the configuration."
)

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

# Engines temporarily disabled in the UI (shown grayed-out, non-operable).
_DISABLED_ENGINES: set[str] = {"Rag"}


def _agent_catalog_signature() -> tuple[tuple[str, int], ...]:
    """Return a lightweight cache key for avatar metadata and PNG changes."""
    paths: list[Path] = []
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
        project_id = st.session_state.get("project_id", "")
        if mode == "project" and project_name:
            label = (
                f"{project_name}-{project_id}" if project_id else project_name
            )
            st.markdown(f"**Project:** {label}")
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
        if st.button("← Back", width="stretch"):
            st.session_state.workflow_stage = "welcome"
            st.rerun()
        st.caption("MASIM v0.1.0")

    st.markdown(
        '<div class="market-kicker">Stage 1 of 2</div>', unsafe_allow_html=True
    )
    st.title("Pick a simulation scenario")
    st.write(
        "Choose the market phenomenon you want to simulate. Each scenario "
        "is anchored to a specific market family (stock, FX, credit, "
        "crypto, deposit, derivatives, information, or opinion). In "
        "Stage 2 you decide whether to run the default setup or build "
        "your own market."
    )

    if not group_names:
        st.error("No simulation scenarios were found in `configs/`.")
        return

    selected_base = st.session_state.get("selected_scenario_base", "")

    # --- Category tabs (lazy-loaded scenario cards) --------------------
    # Only the currently-active tab renders its 4 cards, so first-paint
    # cost is 4 cards instead of 12.  Tabs also organise the pedagogy:
    # Behavioral Biases / Market Mechanisms / Historical Crises.
    scenarios_by_cat = discover_scenarios_by_category()
    active_categories = [c for c in CATEGORY_ORDER if scenarios_by_cat.get(c)]

    if not active_categories:
        st.warning(
            "No curated scenarios matched the visibility whitelist. "
            "Check `_SCENARIO_CATEGORIES` in `config_loader.py`."
        )
        return

    tab_labels = [CATEGORY_LABELS[c] for c in active_categories]
    tabs = st.tabs(tab_labels)
    for cat_key, tab in zip(active_categories, tabs):
        with tab:
            caption = CATEGORY_DESCRIPTIONS.get(cat_key, "")
            if caption:
                st.caption(caption)
            bases_in_cat = scenarios_by_cat[cat_key]
            # 4 cards per row — matches the typical 4-per-category layout.
            cols_per_row = 4
            for start in range(0, len(bases_in_cat), cols_per_row):
                row = st.columns(cols_per_row, gap="medium")
                for col, base in zip(
                    row, bases_in_cat[start : start + cols_per_row]
                ):
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


def _default_extras_session_key(scenario_base: str) -> str:
    """Session-state key holding the Default-mode extras override dict.

    The dict has the shape ``{"__market__": {extras_key: value}, "<agent_key>":
    {extras_key: value}}`` where ``<agent_key>`` matches a top-level block in
    ``configs/<Scenario>/Rule/players.yml``.  ``_launch_default_variant``
    reads this dict and forwards it to
    :func:`write_default_scenario_bundle` so any edits land on disk.
    """
    return f"default_extras_{scenario_base}"


def _coerce_extras_value(default_value: Any, new_value: Any) -> Any:
    """Cast a widget value back to the type of the shipped default.

    ``st.number_input`` returns ``int`` for int defaults and ``float`` for
    float defaults; ``st.text_input`` always returns ``str``.  We only
    round-trip through this helper when the user actually edits the
    value, so passing ``None`` / mismatched types is fine — we fall back
    to the widget's own type in that case.
    """
    if isinstance(default_value, bool):
        return bool(new_value)
    if isinstance(default_value, int) and not isinstance(default_value, bool):
        try:
            return int(new_value)
        except (TypeError, ValueError):
            return new_value
    if isinstance(default_value, float):
        try:
            return float(new_value)
        except (TypeError, ValueError):
            return new_value
    return new_value


def _render_default_param_editor(scenario_base: str) -> None:
    """DEPRECATED — dead code retained only to guard against re-import.

    Historically this function drove the Default-mode parameter editor,
    but the actual live path is :func:`_render_default_config_page`
    (which routes through :func:`_render_extras_grid` and
    :func:`_show_default_edit_dialog` — both correctly propagate
    ``disabled=is_rulellm`` so RuleLLM samples stay read-only).

    The previous body did NOT propagate the RuleLLM lock (widgets had no
    ``disabled=`` kwarg), so leaving it callable would silently break the
    read-only teaching contract if anyone re-wired it.  It now raises to
    make accidental reuse fail loudly.
    """
    raise RuntimeError(
        "_render_default_param_editor is deprecated dead code. Use "
        "_render_default_config_page (which correctly propagates the "
        "RuleLLM read-only lock through _render_extras_grid)."
    )


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
        project_id = st.session_state.get("project_id", "")
        if mode == "project" and project_name:
            label = (
                f"{project_name}-{project_id}" if project_id else project_name
            )
            st.markdown(f"**Project:** {label}")
        elif mode == "experience":
            st.markdown("**Mode:** Experience")
        st.markdown("---")
        st.markdown("~~Stage 1. Pick a scenario~~")
        if mode == "experience":
            st.markdown("**Stage 2.** Select engine and run")
        else:
            st.markdown("**Stage 2.** Default or customize")
        st.markdown("---")
        if st.button("← Back", width="stretch"):
            # Purge scenario-scoped ephemeral state before returning to
            # Stage 1.  Without this cleanup, revisiting a different
            # scenario in the same session leaves stale ``variant_rounds_*``
            # / ``default_extras_*`` widget keys behind — the next scenario
            # then shows the previous one's rounds/extras until the user
            # manually re-edits, and any launch keeps writing to the
            # stale bundle.  We deliberately preserve mode/project/team
            # keys and the workflow_stage transition below.
            _outgoing_base = st.session_state.get("selected_scenario_base", "")
            if _outgoing_base:
                _scenario_scoped_keys = [
                    f"variant_rounds_{_outgoing_base}",
                    f"default_extras_{_outgoing_base}",
                    f"widget_customize_variant_rounds_{_outgoing_base}",
                    f"dc_rounds_{_outgoing_base}",
                ]
                for _k in _scenario_scoped_keys:
                    st.session_state.pop(_k, None)
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

    name_col, logo_col, features_col = st.columns([3, 1, 2])
    with name_col:
        st.markdown(
            f"<div class='scenario-confirm-chip'>\u2713 "
            f"{html.escape(scenario_display_name(selected_base))}"
            f"</div>",
            unsafe_allow_html=True,
        )
    # The rounds editor previously lived in this middle column, but it is
    # already available inside both the Default sub-page
    # (``render_default_config`` — Rounds input at ``dc_rounds_<base>``) and
    # the Customize sub-page (``render_customize`` — Rounds input at
    # ``widget_customize_variant_rounds_<base>``). All simulation
    # modifications — round count, market extras, agent extras, LLM
    # prompts — now live *inside* the Default or Customized sub-page as
    # part of the modification workflow, and this top strip only carries
    # scenario identification.
    #
    # We still seed ``variant_rounds_<selected_base>`` here so any launch
    # path that reads the key before the user visits a sub-page (defensive
    # against future entry points) receives the shipped default rather
    # than ``None``. Sub-page widgets keep the same key and will
    # override the value the moment the user edits it.
    try:
        shipped_rounds = int(info.get("total_rounds") or 0)
    except (TypeError, ValueError):
        shipped_rounds = 0
    _rounds_key = f"variant_rounds_{selected_base}"
    if _rounds_key not in st.session_state:
        st.session_state[_rounds_key] = shipped_rounds if shipped_rounds > 0 else 1
    with logo_col:
        if not is_experience:
            _logo_path = PROJECT_ROOT / "logo.jpg"
            if _logo_path.exists():
                _logo_uri = _image_data_uri(_logo_path)
                if _logo_uri:
                    st.markdown(
                        f'<div class="variant-choice-logo-wrap">'
                        f'<img src="{_logo_uri}" alt="Project logo"></div>',
                        unsafe_allow_html=True,
                    )
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

    # Append actual market parameter values from the scenario config.
    _market_params = extract_market_extras(
        bundle_name="",  # no bundle yet; will fall back to shipped scenario
        scenario_name=selected_base,
        project_root=PROJECT_ROOT,
    )
    if _market_params:
        _param_chips = "  ".join(
            f"<code style='font-size:11px;background:#eef3f6;"
            f"padding:1px 5px;border-radius:3px;'>"
            f"{html.escape(k)}={v}</code>"
            for k, v in _market_params.items()
        )
        situation_body += (
            f"<div style='margin-top:8px;padding-top:7px;"
            f"border-top:1px solid #e8ecf0;font-size:11.5px;"
            f"color:#46535f;line-height:1.8;'>"
            f"<span style='font-weight:600;color:#1a2633;'>"
            f"Initial parameters:</span> {_param_chips}</div>"
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

    # Resolve the market coordinator icon so the panel header carries a
    # visual cue for the market family (matches the icon used on the
    # Stage-1 scenario card).
    scenario_market_icon = get_market_icon_path(selected_base)
    if scenario_market_icon and scenario_market_icon.exists():
        _icon_uri = _image_data_uri(scenario_market_icon)
        market_icon_node = (
            f'<img src="{_icon_uri}" alt="" '
            f'style="width:48px;height:48px;border-radius:10px;'
            f'object-fit:cover;border:1px solid #dde4ea;background:#fff;'
            f'flex-shrink:0;box-shadow:0 1px 2px rgba(20,32,44,0.05);" />'
            if _icon_uri else ""
        )
    else:
        market_icon_node = ""

    if (
        market_type
        or market_desc
        or scenario_desc
        or phenomenon_desc
    ):
        _header_html = (
            "<div style='display:flex;align-items:center;gap:10px;"
            "margin-bottom:10px;'>"
            f"{market_icon_node}"
            "<div style='display:flex;flex-direction:column;min-width:0;'>"
            "<div style='font-size:13px;font-weight:700;color:#1a2633;"
            "line-height:1.25;'>Simulation scenario</div>"
            + (
                f"<div style='font-size:11px;font-weight:600;color:#287a6d;"
                f"text-transform:uppercase;letter-spacing:0.06em;"
                f"line-height:1.4;margin-top:2px;'>"
                f"{html.escape(market_type)}</div>"
                if market_type
                else ""
            )
            + "</div></div>"
        )
        st.markdown(
            "<div style='margin-top:12px;padding:14px 16px;"
            "background:#f7f9fc;border:1px solid #dde4ea;border-radius:8px;'>"
            + _header_html
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

        # Shared scoped styling for the drill-through link cards. Each
        # target (finance-*.md scenario definition, and market coordinator
        # archetype profile) is rendered as a bordered rectangular button
        # rather than a plain text link, so users can find the market
        # definitions at a glance instead of missing a subtle 12 px link.
        market_archetype_stem = get_market_archetype(selected_base)
        if finance_path is not None or market_archetype_stem:
            st.markdown(
                "<style>"
                '[class*="st-key-view_bases_"] button,'
                '[class*="st-key-view_archetype_"] button{'
                'background:#ffffff !important;'
                'border:1px solid #cfd8e3 !important;'
                'border-left:3px solid #2a5fa6 !important;'
                'box-shadow:0 1px 2px rgba(20,32,44,0.05) !important;'
                'padding:10px 14px !important;'
                'margin:0 !important;'
                'min-height:52px !important;height:auto !important;'
                'color:#2a5fa6 !important;font-weight:700 !important;'
                'font-size:13px !important;'
                'text-align:left !important;'
                'justify-content:flex-start !important;'
                'width:100% !important;'
                'white-space:normal !important;'
                'line-height:1.35 !important;'
                'transition:border-color .15s, box-shadow .15s, background .15s;'
                '}'
                '[class*="st-key-view_bases_"] button:hover,'
                '[class*="st-key-view_archetype_"] button:hover{'
                'border-color:#2a5fa6 !important;'
                'background:#f3f7fc !important;'
                'box-shadow:0 2px 6px rgba(42,95,166,0.15) !important;'
                'color:#1a4a8f !important;'
                'text-decoration:none !important;'
                '}'
                '[class*="st-key-view_archetype_"] button{'
                'border-left-color:#287a6d !important;'
                'color:#1f6157 !important;'
                '}'
                '[class*="st-key-view_archetype_"] button:hover{'
                'border-color:#287a6d !important;'
                'background:#f3f7f6 !important;'
                'box-shadow:0 2px 6px rgba(40,122,109,0.15) !important;'
                'color:#1a5348 !important;'
                '}'
                "</style>",
                unsafe_allow_html=True,
            )

        # Small caption above the link strip so users know what to expect.
        if finance_path is not None or market_archetype_stem:
            st.markdown(
                "<div style='margin-top:14px;margin-bottom:6px;"
                "font-size:11px;font-weight:700;color:#68737d;"
                "text-transform:uppercase;letter-spacing:0.08em;'>"
                "Market definitions"
                "</div>",
                unsafe_allow_html=True,
            )

        # Render the two drill-through link cards side-by-side when both
        # exist. Layout picks between one and two columns automatically.
        _link_targets: list[str] = []
        if finance_path is not None:
            _link_targets.append("finance")
        if market_archetype_stem:
            _link_targets.append("archetype")
        if _link_targets:
            _link_cols = st.columns(len(_link_targets), gap="small")
            for _col, _kind in zip(_link_cols, _link_targets):
                with _col:
                    if _kind == "finance" and finance_path is not None:
                        finance_rel = finance_path.name
                        with st.container(key=f"view_bases_{selected_base}"):
                            if st.button(
                                f"\U0001f4d6  Scenario definition \u2014 "
                                f"{finance_rel} \u2192",
                                key=f"btn_view_bases_{selected_base}",
                                help=(
                                    f"Open examples/{selected_base}/{finance_rel} "
                                    "\u2014 phenomenon statement, anchors, "
                                    "stylized facts, roster, environment, "
                                    "parameters, and references."
                                ),
                                width="stretch",
                            ):
                                _show_finance_scenario_dialog(selected_base)
                    elif _kind == "archetype" and market_archetype_stem:
                        with st.container(
                            key=f"view_archetype_{selected_base}"
                        ):
                            if st.button(
                                f"\U0001f3db\ufe0f  Market coordinator "
                                f"\u2014 {market_archetype_stem} \u2192",
                                key=f"btn_view_archetype_{selected_base}",
                                help=(
                                    f"Open examples/AGENT_POOL/market/"
                                    f"{market_archetype_stem}.md "
                                    "\u2014 shared coordinator profile bound "
                                    "to this scenario via players.yml "
                                    "\u2192 market.archetype:."
                                ),
                                width="stretch",
                            ):
                                _show_market_archetype_dialog(selected_base)

    st.divider()
    
    if is_experience:
        # Experience mode: comprehensive read-only display + engine buttons.
        probe_key = _scenario_probe_key(selected_base, groups)
        agents = get_agents_info(probe_key)
        # Filter out the market coordinator for display.
        player_agents = [a for a in agents if a["role"] != "coordinator"]

        roster_col, topo_col = st.columns([3, 2], gap="medium")

        with roster_col:
            # Lazy: keep the (potentially expensive) avatar grid hidden
            # behind an expander so it doesn't render on every scenario
            # switch.  The label carries a live count so users know
            # what's inside without opening it.
            if player_agents:
                # NOTE: use a distinct local name so we don't shadow the
                # imported ``total_instances`` helper (masim.interface.
                # customized.roster.total_instances) inside this scope.
                # Shadowing was harmless in practice — no other call sites
                # here need the helper — but it made static readers assume
                # ``total_instances`` was the function everywhere in the
                # file and set a trap for future maintainers who add a
                # helper call inside this branch.
                total_instance_count = sum(
                    a["instances"] for a in player_agents
                )
                _agents_label = (
                    f"Agents in this scenario — "
                    f"{len(player_agents)} types · {total_instance_count} instances"
                )
            else:
                _agents_label = "Agents in this scenario"
            with st.expander(_agents_label, expanded=False):
                if player_agents:
                    st.caption(
                        f"{len(player_agents)} agent types, "
                        f"{total_instance_count} total instances — click any agent name "
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
            from .topology_d3 import market_icon_uri, render_d3_topology_with_expand
            topo = get_topology_info(probe_key)
            if topo["nodes"]:
                # Feed the scenario's market coordinator icon into the
                # ``market`` hub node so it renders the correct market
                # family (stock / FX / credit / …) instead of the
                # generic gold-circle fallback.
                _hub_icons = {"market": market_icon_uri(selected_base)}
                render_d3_topology_with_expand(
                    topo,
                    agents,
                    height=420,
                    icon_uris=_hub_icons,
                    key=f"experience_stage2_{selected_base}",
                    title="Network topology",
                    dialog_caption=scenario_display_name(selected_base),
                )
            else:
                st.markdown("**Network topology**")
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
                _is_disabled = variant in _DISABLED_ENGINES
                if _is_disabled:
                    _help = DISABLED_ENGINE_HELP.get(
                        variant, "暂时禁用 (temporarily disabled)"
                    )
                elif variant == "RuleLLM":
                    _help = (
                        f"📖 Run {scenario_display_name(selected_base)} "
                        f"using the read-only RuleLLM sample — showcases how "
                        f"quantitative rules are embedded in the LLM prompt."
                    )
                else:
                    _help = (
                        f"Run {scenario_display_name(selected_base)} with "
                        f"the {variant} decision engine."
                    )
                with col:
                    if st.button(
                        VARIANT_DISPLAY.get(variant, variant),
                        key=f"stage2_default_{variant}",
                        width="stretch",
                        disabled=_is_disabled,
                        help=_help,
                    ):
                        _launch_default_variant(key)
    else:
        # Project mode: Default + Customized side by side.
        default_col, custom_col = st.columns(2, gap="large")

        with default_col:
            variant_keys = groups.get(selected_base) or []
            st.markdown("**Default**")
            st.caption(
                "Run the pre-configured scenario with adjustable market "
                "and agent parameters. Select a decision engine below to "
                "review and configure the simulation before launching."
            )

            if not variant_keys:
                st.info("No default variants available for this scenario.")
            else:
                chip_cols = st.columns(min(len(variant_keys), 4), gap="small")
                for col, key in zip(chip_cols, variant_keys):
                    variant = key.split("/", 1)[1] if "/" in key else key
                    _is_disabled = variant in _DISABLED_ENGINES
                    if _is_disabled:
                        _help = DISABLED_ENGINE_HELP.get(
                            variant, "暂时禁用 (temporarily disabled)"
                        )
                    elif variant == "RuleLLM":
                        _help = (
                            f"📖 Configure {scenario_display_name(selected_base)} "
                            f"with the read-only RuleLLM sample — parameters "
                            f"and prompt are locked; only viewing / launching "
                            f"is allowed."
                        )
                    else:
                        _help = (
                            f"Configure {scenario_display_name(selected_base)} "
                            f"with the {variant} engine, then launch."
                        )
                    with col:
                        if st.button(
                            VARIANT_DISPLAY.get(variant, variant),
                            key=f"stage2_default_{variant}",
                            width="stretch",
                            disabled=_is_disabled,
                            help=_help,
                        ):
                            st.session_state.default_config_key = key
                            st.session_state.workflow_stage = "default_config"
                            st.rerun()

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
                # Record the bundle name for later lazy initialization.
                # The actual file copy is deferred to launch time
                # (inside _write_customized_bundle) to avoid redundant
                # copies when the user hasn't committed yet.
                project_slug = st.session_state.get("project_slug", "")
                project_id = st.session_state.get("project_id", "0000")
                if project_slug:
                    bundle_name = compose_bundle_name(
                        project_slug, project_id, selected_base, current_team()
                    )
                    st.session_state["customized_bundle_name"] = bundle_name
                st.session_state.workflow_stage = "customize"
                st.rerun()


def _initialize_bundle_on_entry(scenario_base: str) -> None:
    """Create the customized bundle folder for the picked scenario.

    Called immediately after the user picks a scenario in Stage 1 (only
    in Project mode). Naming: ``{project_slug}-{project_id}-{scenario_base}``.
    If the bundle already exists for the same project + scenario, skip.
    """
    # Only Project mode gets a customized bundle folder — Experience
    # mode is read-only and has no Customize flow.
    project_slug = st.session_state.get("project_slug", "")
    if not project_slug:
        return

    project_id = st.session_state.get("project_id", "0000")
    bundle_name = compose_bundle_name(
        project_slug, project_id, scenario_base, current_team()
    )

    # Re-entry guard: same project + same scenario → reuse existing folder.
    existing_bundle = st.session_state.get("customized_bundle_name", "")
    if existing_bundle == bundle_name:
        return  # Already initialized for this project + scenario.

    # Different scenario? Generate a new bundle (old folder stays on disk).
    try:
        initialize_customized_folder(
            bundle_name=bundle_name,
            scenario_name=scenario_base,
            project_root=PROJECT_ROOT,
        )
    except (FileNotFoundError, OSError) as exc:
        st.error(f"Could not initialize customized folder: {exc}")
        return

    st.session_state["customized_bundle_name"] = bundle_name


def _launch_default_variant(scenario_key: str) -> None:
    """Send the user to the workspace with a default variant.

    Creates a team-namespaced bundle under ``CUSTOMIZED_SIMULATION/`` using
    the same nested ``{bundle}/Default/{Variant}/`` structure as Project
    mode, then applies any round-count or extras overrides.  This guarantees
    that every run — even an unmodified Experience-mode launch — writes to
    its own EXPERIMENT subtree with a unique Ray namespace, giving full
    multi-team isolation.

    When no team is set (local dev), the shipped config is used directly as
    a zero-copy fast path.
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

    # Pick up any market/agent extras edits produced by the Default
    # parameter editor (see ``_render_default_config_page`` /
    # ``_render_extras_grid`` — both correctly propagate ``disabled=is_rulellm``
    # so RuleLLM samples stay read-only).  Structure:
    # ``{"__market__": {extras_key: value}, "<agent_key>": {...}}``.
    default_extras = st.session_state.get(
        _default_extras_session_key(base), {}
    ) or {}
    market_over = default_extras.get("__market__") or {}
    agent_over = {
        k: v
        for k, v in default_extras.items()
        if k != "__market__" and v
    }

    rounds_changed = (
        edited_rounds is not None
        and shipped_rounds > 0
        and int(edited_rounds) != shipped_rounds
    )
    extras_changed = bool(market_over) or bool(agent_over)

    # In multi-team deployments, ALWAYS create a team-namespaced bundle so
    # that the record_path is isolated per-team — even when rounds/extras
    # are unchanged.  Without this, the zero-copy fast path would let all
    # teams write to the same shipped EXPERIMENT/{Scenario}/{Variant}/ dir.
    needs_bundle = rounds_changed or extras_changed or bool(current_team())

    launch_key = scenario_key
    customized_id = None
    if needs_bundle:
        target_rounds = (
            int(edited_rounds)
            if edited_rounds is not None and int(edited_rounds) > 0
            else shipped_rounds
        )
        if target_rounds < 1:
            target_rounds = shipped_rounds if shipped_rounds > 0 else 1

        # Deterministic bundle name — same nested format as Project mode.
        # slug="exp", project_id="00000000" marks Experience-mode bundles;
        # the team prefix and scenario suffix ensure uniqueness per team.
        bundle_name = compose_bundle_name(
            "exp", "00000000", base, current_team()
        )
        try:
            result = copy_default_scenario_bundle(
                scenario_name=base,
                variant=variant,
                bundle_name=bundle_name,
                project_root=PROJECT_ROOT,
            )
            # Apply round/extras overrides on top of the copied bundle.
            if rounds_changed or extras_changed:
                apply_default_bundle_overrides(
                    config_dir=result.config_dir,
                    total_rounds=target_rounds,
                    market_extras_override=market_over or None,
                    agent_extras_overrides=agent_over or None,
                )
            launch_key = (
                f"CUSTOMIZED_SIMULATION/{bundle_name}/Default/{variant}"
            )
            customized_id = bundle_name
        except (FileNotFoundError, ValueError) as exc:
            st.error(f"Could not prepare scenario bundle: {exc}")
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


# ---------------------------------------------------------------------------
# Default Config page — intermediate parameter editing before simulation
# ---------------------------------------------------------------------------


def render_default_config() -> None:
    """Render the Default configuration page.

    Entered after the user picks a decision engine in the Project-mode
    Default column.  Shows market parameters, agent cards with editable
    extras, and a Confirm button that launches the simulation.
    """
    scenario_key = st.session_state.get("default_config_key", "")
    if not scenario_key:
        st.warning("No engine selected. Returning to scenario picker.")
        st.session_state.workflow_stage = "variant_choice"
        st.rerun()
        return

    base = scenario_key.split("/", 1)[0]
    variant = scenario_key.split("/", 1)[1] if "/" in scenario_key else "Rule"

    # ── Resolve project bundle name ──────────────────────────────────────
    project_slug = st.session_state.get("project_slug", "project")
    project_id = st.session_state.get("project_id", "0000")
    bundle_name = compose_bundle_name(
        project_slug, project_id, base, current_team()
    )

    # ── Copy scenario to bundle on first entry ────────────────────────────
    # Idempotent: only copies if the bundle doesn't already exist.
    try:
        bundle = copy_default_scenario_bundle(
            scenario_name=base,
            variant=variant,
            bundle_name=bundle_name,
            project_root=PROJECT_ROOT,
        )
        st.session_state["default_config_bundle"] = bundle
        st.session_state["customized_bundle_name"] = bundle_name
    except FileNotFoundError as exc:
        st.error(f"Could not prepare scenario bundle: {exc}")
        return

    # ── Back button ───────────────────────────────────────────────────────
    render_back_to_stage1_bar(
        key_suffix="default_config",
        target_stage="variant_choice",
    )

    # ── Title ─────────────────────────────────────────────────────────────
    st.title(f"{scenario_display_name(base)} · {VARIANT_DISPLAY.get(variant, variant)}")
    is_rulellm = (variant == "RuleLLM")
    if is_rulellm:
        st.info(RULELLM_SAMPLE_NOTICE, icon="📖")
        st.caption(
            "This page is a read-only teaching sample: parameters and prompts "
            "are locked, but you can still click **Confirm & Launch** to run "
            "the sample simulation and see how the rule-embedded prompt "
            "drives agent behavior."
        )
    else:
        st.caption(
            "Review and adjust the market environment and agent parameters below. "
            "Click **Confirm & Launch** at the bottom to start the simulation."
        )

    st.divider()

    # ── Rounds editor ─────────────────────────────────────────────────────
    info = get_scenario_info(scenario_key)
    try:
        shipped_rounds = int(info.get("total_rounds") or 0)
    except (TypeError, ValueError):
        shipped_rounds = 0
    _rounds_key = f"variant_rounds_{base}"
    _rounds_default = shipped_rounds if shipped_rounds > 0 else 1
    _rounds_now = int(st.session_state.get(_rounds_key, _rounds_default))

    rounds_col, _ = st.columns([2, 4])
    with rounds_col:
        edited_rounds = st.number_input(
            "Total Rounds",
            min_value=1,
            max_value=100000,
            value=_rounds_now,
            step=1,
            key=f"dc_rounds_{base}",
            help=(
                f"Number of simulation rounds. Shipped default: "
                f"{shipped_rounds if shipped_rounds > 0 else 'n/a'}."
            ),
            disabled=is_rulellm,
        )
        st.session_state[_rounds_key] = int(edited_rounds)

    st.divider()

    # ── Load player data ──────────────────────────────────────────────────
    # Read from the *bundle*'s players.yml so the UI reflects on-disk edits
    # persisted by the Save button in the edit dialog. The bundle is created
    # by :func:`copy_default_scenario_bundle` above (idempotent).
    players = extract_default_players(
        scenario_name=base,
        variant=variant,
        project_root=PROJECT_ROOT,
        players_yml_path=bundle.players_yaml,
    )
    if not players:
        st.info("No configurable parameters for this scenario.")
        _render_launch_button(scenario_key)
        return

    session_key = _default_extras_session_key(base)
    edits: dict[str, dict[str, Any]] = st.session_state.setdefault(session_key, {})

    # Separate market coordinator from investor agents
    player_items = list(players.items())
    market_key, market_info = player_items[0]
    agent_items = player_items[1:]

    # ── Market Parameters ─────────────────────────────────────────────────
    market_extras = market_info.get("extras") or {}
    if market_extras:
        st.subheader("Market Environment")
        market_override = edits.setdefault("__market__", {})
        _render_extras_grid(
            extras=market_extras,
            override_slot=market_override,
            key_prefix=f"dc_{base}_market",
            disabled=is_rulellm,
        )
        if not market_override:
            edits.pop("__market__", None)
        st.divider()

    # ── Agent Cards (icon + name + Edit dialog) ─────────────────────────
    is_llm_variant = variant in ("LLM", "RuleLLM", "Rag")
    if agent_items:
        st.subheader("Agents")
        per_row = 6
        for row_start in range(0, len(agent_items), per_row):
            row = agent_items[row_start : row_start + per_row]
            cols = st.columns(per_row, gap="medium")
            for col, (block_key, block_info) in zip(cols, row):
                with col:
                    _render_default_agent_card(
                        base=base,
                        variant=variant,
                        block_key=block_key,
                        block_info=block_info,
                        edits=edits,
                        is_llm_variant=is_llm_variant,
                        bundle=bundle,
                    )
        st.divider()

    # ── Confirm & Launch button ───────────────────────────────────────────
    _render_launch_button(scenario_key)


def _resolve_prompt_text(module_ref: str) -> str:
    """Resolve a 'module.path:VARIABLE' reference to its string value.

    Used to load the actual prompt text from e.g.
    'examples.AnchoringEffect.LLM.prompts:LLM_ANCHORED_TRADER_SYS'.
    Returns the resolved string, or the raw reference if import fails.

    Delegates to :func:`masim.agents._base._load_dotted` so shipped and
    CUSTOMIZED_SIMULATION bundle references (whose directory names contain
    hyphens illegal in Python import syntax) both resolve through the same
    file-path-fallback code path.
    """
    if ":" not in module_ref:
        return module_ref
    try:
        from masim.agents._base import _load_dotted
        value = _load_dotted(module_ref)
        if isinstance(value, str):
            return value
    except Exception:
        pass
    return module_ref


def _extract_persona_section(full_prompt: str) -> str:
    """Extract only the persona part from a full system prompt.

    Thin wrapper around :func:`masim.format.order_prompts.extract_persona`
    kept for backwards compatibility with the Default-config editor and
    the customized entry-edit dialog.  Both routes now share a single
    definition of "where the persona ends" so the two flows cannot drift.
    """
    from masim.format.order_prompts import extract_persona

    persona = extract_persona(full_prompt)
    # Preserve historical caller expectation: ensure a trailing newline
    # so downstream string concatenation looks clean.
    return persona.rstrip("\n") + "\n"


def _render_default_agent_card(
    *,
    base: str,
    variant: str,
    block_key: str,
    block_info: dict[str, Any],
    edits: dict[str, dict[str, Any]],
    is_llm_variant: bool,
    bundle,  # CustomizedBundleResult
) -> None:
    """Render one agent card in the Default config grid (Customized-style).

    Shows: icon image → agent name → edited badge → Edit button (opens dialog).
    The "✓ 已修改" badge is derived by comparing the bundle's on-disk files
    against the shipped originals — no in-memory sentinel is consulted. This
    matches the direct-disk-write Save model documented above the
    :func:`_save_default_agent_edits_to_disk` helper.
    """
    archetype = _canonical_archetype(block_key)
    icon_path = ICON_ROOT / f"finance-{archetype.replace('_', '-')}.png"
    display_name = block_info.get("name") or block_key

    # --- Icon image (full-column width, like Customized cards) ---
    if icon_path.exists():
        st.image(str(icon_path), use_container_width=True)
    else:
        st.markdown(
            "<div style='width:100%;aspect-ratio:1/1;border-radius:8px;"
            "background:#e8f0fb;display:flex;align-items:center;"
            "justify-content:center;color:#2a5fa6;font-weight:700;"
            f"font-size:1.4rem;'>{html.escape(display_name[0])}</div>",
            unsafe_allow_html=True,
        )

    # --- Agent name ---
    num_instances = block_info.get("num_instances", 1)
    instance_badge = f" ×{num_instances}" if num_instances > 1 else ""
    st.markdown(
        f"<p style='text-align:center;margin:2px 0;font-weight:600;"
        f"font-size:0.85rem;'>{html.escape(display_name)}{instance_badge}</p>",
        unsafe_allow_html=True,
    )

    # --- Edited indicator (disk-derived) ---
    has_edits = False
    llm_cfg_for_badge = block_info.get("llm") if is_llm_variant else None
    sys_ref_for_badge = (llm_cfg_for_badge or {}).get("sys_message", "")
    extras_keys_for_badge = tuple((block_info.get("extras") or {}).keys())
    try:
        has_edits = _is_default_agent_edited_on_disk(
            bundle=bundle,
            base=base,
            variant=variant,
            block_key=block_key,
            sys_ref=sys_ref_for_badge,
            extras_keys=extras_keys_for_badge,
        )
    except Exception:
        # Defensive: never let a badge-compute crash the entire config page.
        has_edits = False

    if has_edits:
        st.markdown(
            "<div style='text-align:center;margin:2px 0;'>"
            "<span style='display:inline-block;font-size:0.68rem;padding:2px 8px;"
            "border-radius:10px;background:#d4edda;color:#155724;"
            "font-weight:600;'>✓ 已修改</span></div>",
            unsafe_allow_html=True,
        )

    # --- Edit button (opens dialog) ---
    if st.button(
        "编辑",
        key=f"dc_edit_btn_{base}_{block_key}",
        use_container_width=True,
    ):
        _show_default_edit_dialog(
            base=base,
            variant=variant,
            block_key=block_key,
            block_info=block_info,
            edits=edits,
            is_llm_variant=is_llm_variant,
            bundle=bundle,
        )


@st.dialog("Edit Agent", width="large")
def _show_default_edit_dialog(
    *,
    base: str,
    variant: str,
    block_key: str,
    block_info: dict[str, Any],
    edits: dict[str, dict[str, Any]],
    is_llm_variant: bool,
    bundle,  # CustomizedBundleResult
) -> None:
    """Dialog overlay for editing a Default-config agent's parameters.

    On Save, every edit is written *directly* to the bundle's on-disk
    ``prompts.py`` and ``players.yml`` via
    :func:`_save_default_agent_edits_to_disk`. No in-memory sentinel is
    kept between reruns; widget default values are re-read from those
    files on every dialog open. The persona edit is confined to the
    ``_XXX_PERSONA`` triple-quoted block so the definition-site concat
    line (``LLM_XXX_SYS = _XXX_PERSONA + "\\n\\n" + FORMAT_TAIL``) stays
    intact — the reader still sees the entire prompt composition in one
    place.

    When ``variant == "RuleLLM"``, everything is rendered read-only (sample
    view) — the dialog serves as a teaching example that shows how the
    quantitative Rule engine's decision rules get embedded inside an LLM
    prompt. Save is disabled and the persona textarea is force-loaded
    from the actual scenario RuleLLM configs so students see the real
    ``==DECISION RULES==`` block.
    """
    display_name = block_info.get("name") or block_key
    extras = block_info.get("extras") or {}
    is_rulellm = (variant == "RuleLLM")

    st.subheader(display_name)
    if is_rulellm:
        st.info(RULELLM_SAMPLE_NOTICE, icon="📖")

    # ── Parameters (extras) ───────────────────────────────────────────
    # Extras are still edited via a session-scoped override slot so the
    # user can compare pending changes before clicking Save. The slot is
    # flushed to disk (or discarded) when the Save/Cancel buttons run.
    override_slot: dict[str, Any] = dict(edits.get(block_key) or {})
    if extras:
        st.markdown("**Parameters**")
        _render_extras_grid(
            extras=extras,
            override_slot=override_slot,
            key_prefix=f"dc_{base}_{block_key}",
            disabled=is_rulellm,
        )
        st.divider()

    # ── LLM Prompt & Model (only for LLM/RuleLLM/Rag engines) ────────
    # Locals captured at widget-mount time; consumed by the Save handler.
    persona_edit_body: str | None = None
    temperature_edit: float | None = None
    max_new_tokens_edit: int | None = None
    lm_name_edit: str | None = None
    llm_cfg = block_info.get("llm") if is_llm_variant else None

    if is_llm_variant and llm_cfg:
        st.markdown("**Persona Prompt**")
        st.caption(
            "Edit the agent's persona below. The output format instruction "
            "is appended automatically at the definition site inside "
            "prompts.py — you only need to adjust the persona description."
            if not is_rulellm else
            "Read-only sample. Below is the actual RuleLLM system prompt "
            "for this agent in this scenario — notice how the "
            "`== DECISION RULES ==` block encodes the same quantitative "
            "logic that the pure Rule engine uses."
        )

        sys_ref = llm_cfg.get("sys_message", "")

        # --- Resolve the persona body to prefill the textarea ---
        # Priority: bundle prompts.py (already edited) → shipped prompts.py.
        # For RuleLLM sample view, always show the full shipped RuleLLM
        # system prompt (persona + embedded rules) verbatim.
        if is_rulellm:
            _prompt_data = get_rulellm_prompt_for_agent(base, block_key)
            initial_persona = (_prompt_data or {}).get("sys", "") if _prompt_data else ""
        else:
            bundle_body, _ = _read_bundle_persona_body(bundle.example_dir, sys_ref)
            if bundle_body:
                initial_persona = bundle_body
            else:
                public_const = _public_const_from_sys_ref(sys_ref)
                initial_persona = _read_shipped_persona_body(base, variant, public_const)

        edited_prompt = st.text_area(
            "Persona Prompt",
            value=initial_persona,
            height=220,
            key=f"dc_llm_prompt_{base}_{block_key}",
            help=(
                "Read-only — this is a teaching sample."
                if is_rulellm else
                "Edit the agent's persona content."
            ),
            label_visibility="collapsed",
            disabled=is_rulellm,
        )
        if not is_rulellm:
            # Preserve the exact persona-body string on Save when it
            # differs from what is currently on disk. Whitespace-only
            # changes are ignored to avoid noisy diffs.
            if edited_prompt.strip() != (initial_persona or "").strip():
                persona_edit_body = edited_prompt

        # Locked format display — mirrors what's actually concatenated
        # at the def-site in prompts.py (FORMAT_TAIL from
        # masim.format.<category>).
        st.info(
            "**Output format** (locked — concatenated at the def-site in "
            "prompts.py as `LLM_XXX_SYS = _XXX_PERSONA + \"\\n\\n\" + "
            "FORMAT_TAIL`):\n\n"
            "```\n"
            '<analysis>...</analysis><decision>JSON</decision>\n'
            "JSON schema: see masim/format/{limit_order|maker_taker_order|"
            "participation_order}.py\n"
            "```",
            icon="\U0001f512",
        )

        st.divider()

        # Model & Generation parameters
        st.markdown("**Model & Generation**")
        gen_cfg = llm_cfg.get("generation_config") or {}
        pcol1, pcol2 = st.columns(2)
        with pcol1:
            current_temp = float(gen_cfg.get("temperature", 0.7))
            new_temp = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=current_temp,
                step=0.05,
                key=f"dc_llm_temp_{base}_{block_key}",
                disabled=is_rulellm,
            )
            if not is_rulellm and abs(new_temp - current_temp) > 1e-6:
                temperature_edit = round(new_temp, 2)
        with pcol2:
            # Shipped YAML uses ``max_new_tokens`` (not ``max_tokens``).
            current_tokens = int(gen_cfg.get("max_new_tokens", 512))
            new_tokens = st.number_input(
                "Max New Tokens",
                min_value=64,
                max_value=4096,
                value=current_tokens,
                step=64,
                key=f"dc_llm_tokens_{base}_{block_key}",
                disabled=is_rulellm,
            )
            if not is_rulellm and int(new_tokens) != current_tokens:
                max_new_tokens_edit = int(new_tokens)

        current_model = llm_cfg.get("lm_name", "")
        new_model = st.text_input(
            "Model Name",
            value=current_model,
            key=f"dc_llm_model_{base}_{block_key}",
            help="LLM endpoint identifier (e.g. ark/doubao-seed-2-0-mini-260428).",
            disabled=is_rulellm,
        )
        if not is_rulellm and new_model.strip() != current_model:
            lm_name_edit = new_model.strip()

    # ── Save button ────────────────────────────────────────────────────
    if st.button(
        "保存",
        key="dc_edit_save",
        type="primary",
        use_container_width=True,
        disabled=is_rulellm,
        help=("RuleLLM 只作为教学样例展示，无可保存的修改。"
              if is_rulellm else None),
    ):
        try:
            _save_default_agent_edits_to_disk(
                bundle=bundle,
                base=base,
                variant=variant,
                block_key=block_key,
                sys_ref=(llm_cfg or {}).get("sys_message", ""),
                persona_body=persona_edit_body,
                temperature=temperature_edit,
                max_new_tokens=max_new_tokens_edit,
                lm_name=lm_name_edit,
                extras_override=(override_slot or None),
            )
        except Exception as exc:
            st.error(f"保存失败: {exc}")
            return

        # Clear the in-memory extras slot — disk is now the source of truth.
        edits.pop(block_key, None)
        # Close the dialog and refresh the grid so the badge picks up the
        # freshly-written disk state on the next render.
        st.rerun(scope="fragment")


def _render_extras_grid(
    *,
    extras: dict[str, Any],
    override_slot: dict[str, Any],
    key_prefix: str,
    disabled: bool = False,
) -> None:
    """Render a responsive grid of parameter widgets for an extras dict.

    When ``disabled=True`` (e.g. RuleLLM sample view), each widget is
    greyed-out and no overrides are recorded — the current values are
    shown for reference only.
    """
    cols_per_row = 3
    keys = list(extras.keys())
    for row_start in range(0, len(keys), cols_per_row):
        row_keys = keys[row_start : row_start + cols_per_row]
        cols = st.columns(len(row_keys))
        for col, extras_key in zip(cols, row_keys):
            with col:
                default_val = extras[extras_key]
                current_val = override_slot.get(extras_key, default_val)
                widget_key = f"{key_prefix}_{extras_key}"
                pretty = extras_key.replace("_", " ").title()

                if isinstance(default_val, bool):
                    new_val = st.checkbox(
                        pretty,
                        value=bool(current_val),
                        key=widget_key,
                        help=f"Default: {default_val}",
                        disabled=disabled,
                    )
                elif isinstance(default_val, (int, float)):
                    new_val = st.number_input(
                        pretty,
                        value=(
                            float(current_val)
                            if isinstance(default_val, float)
                            else int(current_val)
                        ),
                        format=(
                            "%.6g"
                            if isinstance(default_val, float)
                            else "%d"
                        ),
                        key=widget_key,
                        help=f"Default: {default_val}",
                        disabled=disabled,
                    )
                else:
                    new_val = st.text_input(
                        pretty,
                        value=str(current_val),
                        key=widget_key,
                        help=f"Default: {default_val!r}",
                        disabled=disabled,
                    )

                if disabled:
                    # Don't record any overrides while in read-only mode.
                    continue
                coerced = _coerce_extras_value(default_val, new_val)
                if coerced != default_val:
                    override_slot[extras_key] = coerced
                else:
                    override_slot.pop(extras_key, None)


def _render_launch_button(scenario_key: str) -> None:
    """Render the Confirm & Launch button at the bottom of the config page."""
    _, center_col, _ = st.columns([2, 2, 2])
    with center_col:
        if st.button(
            "✓ Confirm & Launch",
            key="dc_confirm_launch",
            type="primary",
            use_container_width=True,
        ):
            _launch_from_default_config(scenario_key)


def _launch_from_default_config(scenario_key: str) -> None:
    """Apply parameter edits to the bundle and enter the workspace.

    LLM persona / generation / lm_name / per-agent extras edits have
    already been written to the bundle by the Save button inside
    :func:`_show_default_edit_dialog` (direct-disk-write model). This
    launch handler only flushes the still-in-memory ``__market__`` extras
    and the rounds edit — Confirm & Launch is the point at which those
    two become permanent.
    """
    base = scenario_key.split("/", 1)[0]
    variant = scenario_key.split("/", 1)[1] if "/" in scenario_key else "Rule"

    bundle = st.session_state.get("default_config_bundle")
    if not bundle:
        st.error("Bundle not found. Please go back and select an engine again.")
        return

    # Gather user edits from session state
    _rounds_key = f"variant_rounds_{base}"
    info = get_scenario_info(scenario_key)
    try:
        shipped_rounds = int(info.get("total_rounds") or 0)
    except (TypeError, ValueError):
        shipped_rounds = 0
    edited_rounds = int(
        st.session_state.get(_rounds_key, shipped_rounds if shipped_rounds > 0 else 1)
    )

    session_key = _default_extras_session_key(base)
    default_extras = st.session_state.get(session_key, {}) or {}
    market_over = default_extras.get("__market__") or {}

    # Flush market extras + rounds. Per-agent extras and LLM edits are
    # already on disk via the Save button.
    try:
        apply_default_bundle_overrides(
            config_dir=bundle.config_dir,
            total_rounds=edited_rounds,
            market_extras_override=market_over or None,
            agent_extras_overrides=None,
        )
    except Exception as exc:
        st.error(f"Failed to apply parameter changes: {exc}")
        return

    # Transition to workspace — launch from the bundle
    launch_key = f"CUSTOMIZED_SIMULATION/{bundle.customized_id}/Default/{variant}"
    st.session_state.selected_scenario = launch_key
    st.session_state.selected_market_agents = []
    st.session_state.workflow_stage = "workspace"
    st.session_state.current_page = "Simulation"
    st.session_state.customized_dir_id = bundle.customized_id
    st.rerun()


def _patch_llm_yaml_field(
    text: str, block_key: str, field: str, new_value: str
) -> str:
    """Patch a YAML field value within a specific agent block's llm section.

    Simple line-level replacement: finds the first occurrence of
    ``field: <old_value>`` that appears after the block_key header line,
    and replaces the value. Preserves surrounding formatting.
    """
    import re as _re

    # Find block start
    block_pattern = _re.compile(
        rf"^{_re.escape(block_key)}\s*:", flags=_re.MULTILINE
    )
    block_match = block_pattern.search(text)
    if not block_match:
        return text

    # Search for the field within this block (before next top-level key)
    block_start = block_match.end()
    # Find next top-level key (non-indented line with colon)
    next_block = _re.search(r"^\S+\s*:", text[block_start:], flags=_re.MULTILINE)
    block_end = block_start + next_block.start() if next_block else len(text)

    block_section = text[block_start:block_end]
    # Match the field line (indented)
    field_pattern = _re.compile(
        rf"^(\s+{_re.escape(field)}\s*:\s*).+$", flags=_re.MULTILINE
    )
    field_match = field_pattern.search(block_section)
    if not field_match:
        return text

    # Replace
    replacement = field_match.group(1) + new_value
    new_section = (
        block_section[: field_match.start()]
        + replacement
        + block_section[field_match.end():]
    )
    return text[:block_start] + new_section + text[block_end:]


# ---------------------------------------------------------------------------
# Default-mode Save handler — direct disk-persistence for prompts.py + players.yml
# ---------------------------------------------------------------------------
#
# The Default-mode edit dialog (:func:`_show_default_edit_dialog`) now writes
# every persona / generation-config / extras edit directly to the bundle's
# on-disk files the moment the user clicks "保存". No in-memory sentinel
# (``dc_edited_{block_key}``, ``edits["__llm__"]``) survives across reruns;
# the "✓ 已修改" badge is computed by comparing bundle files against the
# shipped originals. This makes the persona edit visible in ONE place —
# ``examples/CUSTOMIZED_SIMULATION/{bundle}/Default/{variant}/prompts.py`` —
# and preserves the definition-site concat pattern
# ``LLM_XXX_SYS = _XXX_PERSONA + "\n\n" + FORMAT_TAIL`` so anyone reading
# prompts.py sees the entire final prompt at a glance.

def _shipped_prompts_py_path(base: str, variant: str) -> Path:
    """Absolute path to the shipped scenario's prompts.py for this variant."""
    return PROJECT_ROOT / "examples" / base / variant / "prompts.py"


def _shipped_players_yml_path(base: str, variant: str) -> Path:
    """Absolute path to the shipped scenario's players.yml for this variant."""
    return PROJECT_ROOT / "configs" / base / variant / "players.yml"


def _public_const_from_sys_ref(sys_ref: str) -> str:
    """Extract ``LLM_MOMENTUM_SYS`` from ``examples.X.Y.prompts:LLM_MOMENTUM_SYS``."""
    return sys_ref.rsplit(":", 1)[-1] if ":" in sys_ref else sys_ref


def _persona_var_for_public_const(
    prompts_text: str, public_const: str
) -> str | None:
    """Locate the private persona variable used to compose ``public_const``.

    Scans ``prompts_text`` for a line matching the definition-site concat
    pattern::

        LLM_MOMENTUM_SYS = _MOMENTUM_PERSONA + "\\n\\n" + FORMAT_TAIL

    and returns ``"_MOMENTUM_PERSONA"``. Returns ``None`` when no such
    assignment exists — signalling the file no longer follows the standard
    def-site pattern (in which case the caller should raise).
    """
    pat = re.compile(
        rf"^{re.escape(public_const)}\s*=\s*(_[A-Z][A-Z0-9_]*)\s*\+",
        flags=re.MULTILINE,
    )
    m = pat.search(prompts_text)
    return m.group(1) if m else None


def _read_persona_body(prompts_text: str, persona_var: str) -> str | None:
    """Return the *inner* body of ``<persona_var> = \"\"\"...\"\"\"``.

    ``None`` when the variable is not found or is not assigned via a
    triple-quoted string literal.
    """
    pat = re.compile(
        rf'^{re.escape(persona_var)}\s*=\s*"""(.*?)"""',
        flags=re.MULTILINE | re.DOTALL,
    )
    m = pat.search(prompts_text)
    return m.group(1) if m else None


def _replace_persona_body(
    prompts_text: str, persona_var: str, new_body: str
) -> str:
    """Replace the triple-quoted body of ``<persona_var>``.

    ``new_body`` should NOT include the surrounding ``\"\"\"`` fences.
    Raises :class:`ValueError` when no assignment site is located — silent
    no-op would let a Save click appear successful while nothing was
    written, which is exactly the class of bug this refactor eradicates.
    """
    pat = re.compile(
        rf'(^{re.escape(persona_var)}\s*=\s*""")(.*?)(""")',
        flags=re.MULTILINE | re.DOTALL,
    )
    new_text, count = pat.subn(
        lambda m: m.group(1) + new_body + m.group(3), prompts_text
    )
    if count == 0:
        raise ValueError(
            f"_replace_persona_body: cannot locate assignment site for "
            f"{persona_var!r} in prompts.py — the file no longer follows "
            f"the definition-site concat convention "
            f"(expected: '{persona_var} = \"\"\"...\"\"\"')."
        )
    return new_text


# NOTE: The former _bundle_sys_message_ref helper was removed. Bundle-local
# sys_message / user_message references are now composed once at bundle
# creation time inside
# ``masim.interface.customized.config_writer._retarget_scenario_references``.
# There is no longer a "compose the retarget at Save time" flow — Save only
# rewrites the persona body inside the bundle's own prompts.py.


def _save_default_agent_edits_to_disk(
    *,
    bundle,  # CustomizedBundleResult
    base: str,
    variant: str,
    block_key: str,
    sys_ref: str,
    persona_body: str | None,
    temperature: float | None,
    max_new_tokens: int | None,
    lm_name: str | None,
    extras_override: dict[str, Any] | None,
) -> None:
    """Persist a single Save click to bundle disk files.

    - ``persona_body``: inner text of ``_XXX_PERSONA = \"\"\"...\"\"\"``
      (no surrounding fences). ``None`` skips the persona rewrite. When
      given, ``players.yml``'s ``sys_message`` for this agent is also
      re-pointed to the bundle's own prompts.py so the runtime picks up
      the edited persona.
    - ``temperature`` / ``max_new_tokens`` / ``lm_name``: generation
      config edits; ``None`` skips that field. YAML field names match the
      shipped format (``max_new_tokens``, not ``max_tokens``).
    - ``extras_override``: agent-block extras (numeric parameters). When
      non-empty, delegates to :func:`apply_default_bundle_overrides` so
      market-level and agent-level extras use the same tested code path.

    All disk writes happen inside this function — the caller should NOT
    write to ``bundle.example_dir`` or ``bundle.config_dir`` directly.
    """
    prompts_py = bundle.example_dir / "prompts.py"
    players_yml = bundle.config_dir / "players.yml"

    # ── Persona edit ────────────────────────────────────────────────────
    if persona_body is not None:
        if not prompts_py.exists():
            raise FileNotFoundError(
                f"Bundle prompts.py not found at {prompts_py}. "
                f"Did copy_default_scenario_bundle run?"
            )
        prompts_text = prompts_py.read_text(encoding="utf-8")
        public_const = _public_const_from_sys_ref(sys_ref)
        persona_var = _persona_var_for_public_const(prompts_text, public_const)
        if persona_var is None:
            raise ValueError(
                f"Cannot locate persona variable for {public_const!r} in "
                f"{prompts_py}. Expected pattern: "
                f"'{public_const} = _XXX_PERSONA + \"\\n\\n\" + FORMAT_TAIL'."
            )
        prompts_text = _replace_persona_body(
            prompts_text, persona_var, persona_body
        )
        prompts_py.write_text(prompts_text, encoding="utf-8")

    # ── players.yml patches ─────────────────────────────────────────────
    # NOTE: sys_message is NOT retargeted here anymore.
    # ``copy_default_scenario_bundle`` already rewrites every
    # ``examples.<ScenarioName>.…`` reference to
    # ``examples.CUSTOMIZED_SIMULATION.{bundle}.Default.…`` when the bundle
    # is created, so the yaml's sys_message points at the bundle's own
    # prompts.py from run 1. A Save that rewrites the persona body writes
    # directly into that bundle-local prompts.py — no yaml patch needed.
    players_text = players_yml.read_text(encoding="utf-8") if players_yml.exists() else ""
    dirty = False

    if temperature is not None and players_text:
        players_text = _patch_llm_yaml_field(
            players_text, block_key, "temperature", f"{float(temperature)}"
        )
        dirty = True

    if max_new_tokens is not None and players_text:
        players_text = _patch_llm_yaml_field(
            players_text, block_key, "max_new_tokens", str(int(max_new_tokens))
        )
        dirty = True

    if lm_name is not None and players_text:
        players_text = _patch_llm_yaml_field(
            players_text, block_key, "lm_name", f'"{lm_name}"'
        )
        dirty = True

    if dirty:
        players_yml.write_text(players_text, encoding="utf-8")

    # ── Agent extras (numeric parameters) ───────────────────────────────
    if extras_override:
        apply_default_bundle_overrides(
            config_dir=bundle.config_dir,
            total_rounds=_current_total_rounds(bundle.config_dir),
            agent_extras_overrides={block_key: dict(extras_override)},
        )


def _current_total_rounds(config_dir: Path) -> int:
    """Read the current ``total_rounds`` from a bundle's simulation.yml.

    Used to feed :func:`apply_default_bundle_overrides` when only extras
    (not rounds) are being persisted; the callee requires a value but
    accepts the file's current value as a no-op patch.
    """
    import yaml as _yaml
    sim = config_dir / "simulation.yml"
    if not sim.exists():
        return 1
    try:
        data = _yaml.safe_load(sim.read_text(encoding="utf-8"))
    except _yaml.YAMLError:
        return 1
    if isinstance(data, dict):
        tr = data.get("total_rounds")
        if isinstance(tr, int) and tr >= 1:
            return tr
    return 1


def _read_bundle_persona_body(
    example_dir: Path, sys_ref: str
) -> tuple[str, str]:
    """Read the persona body currently living in a bundle's prompts.py.

    Returns ``(persona_body, persona_var)`` — persona_var is the private
    variable name so the caller can rewrite the same site on Save. Both
    values are empty strings when the file / assignment cannot be found;
    the dialog uses this as a signal to fall back to the shipped copy.
    """
    prompts_py = example_dir / "prompts.py"
    if not prompts_py.exists():
        return "", ""
    text = prompts_py.read_text(encoding="utf-8")
    public_const = _public_const_from_sys_ref(sys_ref)
    persona_var = _persona_var_for_public_const(text, public_const)
    if not persona_var:
        return "", ""
    body = _read_persona_body(text, persona_var) or ""
    return body, persona_var


def _read_shipped_persona_body(
    base: str, variant: str, public_const: str
) -> str:
    """Read the same-named persona body from the shipped prompts.py.

    Used both as a fallback when the bundle file has drifted from the
    def-site pattern and by :func:`_is_default_agent_edited_on_disk` to
    compute the "✓ 已修改" badge.
    """
    shipped = _shipped_prompts_py_path(base, variant)
    if not shipped.exists():
        return ""
    text = shipped.read_text(encoding="utf-8")
    persona_var = _persona_var_for_public_const(text, public_const)
    if not persona_var:
        return ""
    return _read_persona_body(text, persona_var) or ""


def _read_agent_block_yaml_fields(
    players_text: str, block_key: str, fields: tuple[str, ...]
) -> dict[str, str]:
    """Extract literal RHS values of specified fields inside an agent block.

    Values are returned as raw strings (whatever appears after the ``:``
    up to end-of-line) so callers can do lexical equality checks between
    bundle and shipped copies without needing full YAML parsing.
    """
    block_pat = re.compile(rf"^{re.escape(block_key)}\s*:", flags=re.MULTILINE)
    m = block_pat.search(players_text)
    if not m:
        return {}
    start = m.end()
    nxt = re.search(r"^\S+\s*:", players_text[start:], flags=re.MULTILINE)
    end = start + nxt.start() if nxt else len(players_text)
    section = players_text[start:end]
    out: dict[str, str] = {}
    for field in fields:
        fm = re.search(
            rf"^\s+{re.escape(field)}\s*:\s*(.+?)\s*$",
            section, flags=re.MULTILINE,
        )
        if fm:
            out[field] = fm.group(1).strip()
    return out


def _is_default_agent_edited_on_disk(
    *,
    bundle,  # CustomizedBundleResult
    base: str,
    variant: str,
    block_key: str,
    sys_ref: str,
    extras_keys: tuple[str, ...] = (),
) -> bool:
    """True when the bundle's on-disk state diverges from shipped defaults.

    Compares four dimensions:
    1. persona body (``_XXX_PERSONA`` triple-quoted content)
    2. generation config (``temperature``, ``max_new_tokens``, ``lm_name``)
    3. ``sys_message`` reference (differs when persona is edited — the
       reference is re-pointed at the bundle's own prompts.py)
    4. per-agent numeric extras (``initial_cash``, etc.) when
       ``extras_keys`` is provided

    Any single divergence flips the badge on. Returns ``False`` cleanly
    when either file is missing.
    """
    public_const = _public_const_from_sys_ref(sys_ref)

    # 1) Persona body
    bundle_body, _ = _read_bundle_persona_body(bundle.example_dir, sys_ref)
    shipped_body = _read_shipped_persona_body(base, variant, public_const)
    if (bundle_body or "").strip() != (shipped_body or "").strip():
        return True

    # 2 & 3) YAML-level fields
    bundle_players = bundle.config_dir / "players.yml"
    shipped_players = _shipped_players_yml_path(base, variant)
    if not bundle_players.exists() or not shipped_players.exists():
        return False
    b_text = bundle_players.read_text(encoding="utf-8")
    s_text = shipped_players.read_text(encoding="utf-8")

    yaml_fields = ("temperature", "max_new_tokens", "lm_name")
    b_vals = _read_agent_block_yaml_fields(b_text, block_key, yaml_fields)
    s_vals = _read_agent_block_yaml_fields(s_text, block_key, yaml_fields)
    # sys_message is intentionally excluded from this comparison because
    # ``copy_default_scenario_bundle`` retargets every sys_message from
    # ``examples.<Scenario>.…`` to
    # ``examples.CUSTOMIZED_SIMULATION.{bundle}.Default.…`` at bundle
    # creation time, so a fresh (unedited) bundle would otherwise be
    # flagged as "edited" purely because of the retargeting bookkeeping.
    # Actual persona edits are caught by the persona-body compare above.
    if b_vals != s_vals:
        return True

    # 4) Per-agent numeric extras
    if extras_keys:
        b_ext = _read_agent_block_yaml_fields(b_text, block_key, extras_keys)
        s_ext = _read_agent_block_yaml_fields(s_text, block_key, extras_keys)
        if b_ext != s_ext:
            return True

    return False



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
    """Convert an image file to a data URI. Cached to avoid re-encoding on every rerun."""
    return _image_data_uri_cached(str(path))


@functools.lru_cache(maxsize=256)
def _image_data_uri_cached(path_str: str) -> str:
    path = Path(path_str)
    if not path.exists():
        return ""
    data = path.read_bytes()
    # Detect actual format via magic bytes (extension can be misleading).
    if data[:8].startswith(b"\x89PNG\r\n\x1a\n"):
        mime = "image/png"
    elif data[:3] in (b"\xff\xd8\xff", b"\xff\xd8"):
        mime = "image/jpeg"
    elif path.suffix.lower() == ".svg" or b"<svg" in data[:512]:
        mime = "image/svg+xml"
    else:
        # Fallback based on extension.
        ext = path.suffix.lower()
        mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".svg": "image/svg+xml", ".webp": "image/webp"}.get(ext, "image/png")
    encoded = base64.b64encode(data).decode("ascii")
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


@st.dialog("Market coordinator archetype", width="large")
def _show_market_archetype_dialog(scenario_base: str) -> None:
    """Modal that renders the coordinator archetype profile for a scenario.

    Resolves the archetype stem via
    :func:`config_loader.get_market_archetype` (which reads
    ``players.yml -> market.archetype:``) and renders the corresponding
    profile file at ``examples/AGENT_POOL/market/{stem}.md``. This mirrors
    ``_show_agent_profile_dialog`` for players, giving the market
    coordinator first-class documentation drill-through.
    """
    stem = get_market_archetype(scenario_base)
    if not stem:
        st.warning(
            "No market archetype could be resolved for this scenario "
            f"(**{html.escape(scenario_base)}**). Check that "
            "`configs/{scenario}/{variant}/players.yml` has an "
            "`archetype:` field in the coordinator block."
        )
        return

    profile_path = AGENT_POOL_ROOT / "market" / f"{stem}.md"
    icon_path = ICON_ROOT / "market" / f"{stem}.png"

    header_cols = st.columns([1, 6], gap="small")
    with header_cols[0]:
        if icon_path.exists():
            st.image(str(icon_path), width=64)
    with header_cols[1]:
        st.markdown(f"### {html.escape(stem)}")
        st.caption(
            f"Bound to scenario `{scenario_base}` via "
            "`players.yml \u2192 market.archetype:` \u2014 see "
            "`masim/skills/market-design-skill.md` for the field spec."
        )
    st.divider()

    if not profile_path.exists():
        st.warning(
            f"Archetype profile missing at "
            f"`examples/AGENT_POOL/market/{stem}.md`. Add the profile "
            "following `masim/skills/market-design-skill.md`."
        )
        return
    st.caption(f"Source: `examples/AGENT_POOL/market/{profile_path.name}`")
    content = profile_path.read_text(encoding="utf-8")
    # Strip the leading H1 to avoid double-titles in the modal.
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
    """
    raw_items: list[dict[str, Any]] = []
    # A handful of stems (e.g. ``distorting-relayer``) ship in BOTH the
    # finance and opinion domains with their own icon + profile. The grid
    # keys every widget by ``agent_type`` (the stem), so emitting both would
    # collide (StreamlitDuplicateElementKey). Dedupe by stem, keeping the
    # first domain in ``_DOMAIN_ROOTS`` (finance) to match the finance-first
    # icon/profile resolution used elsewhere in this module.
    seen_types: set[str] = set()
    for domain, root in _DOMAIN_ROOTS:
        if not root.exists():
            continue
        for md_path in sorted(root.glob("*.md")):
            if md_path.stem in seen_types:
                continue
            icon_name = f"{domain}-{md_path.stem}.png"
            if (ICON_ROOT / icon_name).exists():
                seen_types.add(md_path.stem)
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
        image_path = IMAGE_ROOT / item["image_path"]
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
    """Distinct archetypes present in the current roster, in catalog order.

    The old flat model tracked selection via ``market_agent_{type}`` flags;
    with the roster refactor, selection is derived from the presence of at
    least one :class:`RosterEntry` for that archetype. The result is
    intersected with the catalog to keep icon-grid rendering deterministic
    even when the roster has entries for archetypes the current catalog
    signature no longer knows about.
    """
    roster = get_roster(st.session_state)
    active = set(unique_agent_types(roster))
    return [agent["agent_type"] for agent in catalog if agent["agent_type"] in active]


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
        /* Header row: market icon + (name / market-type). Icon is a
           square 44 px tile with a soft border so it reads at a glance
           without overwhelming the card. */
        .scenario-header {
            display: flex; align-items: center; gap: 0.55rem;
            margin-bottom: 0.35rem;
        }
        .scenario-header-text {
            display: flex; flex-direction: column; min-width: 0; flex: 1;
        }
        .scenario-icon {
            width: 44px; height: 44px; border-radius: 8px;
            object-fit: cover; flex-shrink: 0;
            border: 1px solid #e2e8ee; background: #fafbfc;
            box-shadow: 0 1px 2px rgba(20, 32, 44, 0.05);
        }
        .scenario-icon.fallback {
            display: flex; align-items: center; justify-content: center;
            color: #b6c1cc; font-size: 1.2rem;
        }
        .scenario-name {
            font-size: 0.95rem; font-weight: 700; color: #17212b;
            line-height: 1.25;
            overflow: hidden; text-overflow: ellipsis;
            white-space: nowrap;
        }
        .scenario-market {
            font-size: 0.68rem; font-weight: 600; color: #287a6d;
            text-transform: uppercase; letter-spacing: 0.06em;
            line-height: 1.3; margin-top: 0.1rem;
            overflow: hidden; text-overflow: ellipsis;
            white-space: nowrap;
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
        .variant-choice-logo-wrap {
            display: flex; align-items: center; justify-content: center;
            width: 100%; height: 100%;
        }
        .variant-choice-logo-wrap img {
            height: 3rem; width: auto; max-width: 100%;
            object-fit: contain; border-radius: 6px;
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
        label = "← Back"
        help_text = 'Return to the "Choose how to run it" page.'
    else:
        label = "← Back"
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


@st.dialog("Edit roster entry", width="large")
def _show_entry_edit_dialog(agent: dict[str, Any], entry_id: str) -> None:
    """Dialog overlay for editing ONE roster entry.

    Opened by the Edit / Configure buttons in the customize page.  The
    entry_id argument scopes every widget key inside the dialog so
    multiple entries of the same archetype can be edited independently
    without stepping on each other's widget state.
    """
    _render_entry_edit_panel(agent, entry_id)


def _render_entry_edit_panel(agent: dict[str, Any], entry_id: str) -> None:
    """Render the editable parameter panel for one roster entry.

    Everything inside this panel is scoped by ``entry_id`` — the entry
    can be a fresh one that was just added by the +Add button, or an
    existing entry the user opened via the "My Roster" list.

    On **Save changes**: writes engine / num_instances / label / params
    back into the ``RosterEntry`` in session state, then closes the
    dialog with a toast.

    On **Reset to defaults**: clears the entry's ``params`` dict and
    every entry-scoped widget so the fields fall back to handbook
    defaults on the next open.

    On **Delete this entry**: removes the entry from the roster (with
    an inline confirmation) and closes the dialog.
    """
    roster = get_roster(st.session_state)
    entry = find_entry(roster, entry_id)
    if entry is None:
        st.error(
            "This roster entry no longer exists — it may have been "
            "removed in another tab. Close this dialog and try again."
        )
        if st.button("Close", key=f"entry_missing_close_{entry_id}"):
            st.rerun()
        return

    agent_type = agent["agent_type"]
    # Keep Rag in the button row so students still SEE it exists, but it will
    # be rendered disabled with a tooltip explaining why it is unavailable.
    all_engines = list(ALL_ENGINES)
    selectable_engines = [e for e in all_engines if e not in _DISABLED_ENGINES]
    specs = _load_param_specs(agent)

    st.markdown('<div class="market-kicker">Edit roster entry</div>', unsafe_allow_html=True)
    st.subheader(agent["display_name"])
    header_bits = [f"`{agent_type}`", f"Entry ID `{entry_id}`"]
    st.caption(" · ".join(header_bits))

    # ---- Engine selector (initialised FIRST so the RuleLLM read-only lock is
    # available to every widget below — including the label input directly
    # underneath.  Historically the label was rendered before ``engine_key``
    # was seeded, so on the first frame after opening a RuleLLM entry the
    # label input was NOT disabled, letting users type into what should be
    # a read-only teaching sample and breaking the lock contract.
    engine_key = f"entry_{entry_id}_engine"
    if engine_key not in st.session_state:
        default_engine = (
            entry.engine if entry.engine in selectable_engines else selectable_engines[0]
        )
        st.session_state[engine_key] = default_engine
    elif st.session_state[engine_key] not in selectable_engines:
        st.session_state[engine_key] = selectable_engines[0]

    engine = st.session_state[engine_key]
    is_rulellm = (engine == "RuleLLM")

    # ---- Optional label -------------------------------------------------
    label_key = f"entry_{entry_id}_label"
    if label_key not in st.session_state:
        st.session_state[label_key] = entry.label or ""
    st.text_input(
        "Preset label (optional)",
        key=label_key,
        placeholder="e.g. Aggressive, Cautious, Whale…",
        help=(
            "Optional nickname shown next to this entry in the "
            "**My Roster** list. Leave empty to fall back to the "
            "archetype's default name."
        ),
        disabled=is_rulellm,
    )

    # ---- Engine selector buttons ---------------------------------------
    # Render engine picker as an explicit row of buttons so we can disable
    # specific engines (Rag) individually — segmented_control does not
    # support per-option disabled state.
    st.markdown("**Decision engine**")
    current_engine = engine
    engine_cols = st.columns(len(all_engines))
    for _idx, _eng in enumerate(all_engines):
        _is_disabled = _eng in _DISABLED_ENGINES
        _is_current = (_eng == current_engine)
        _label = ("● " if _is_current else "○ ") + VARIANT_DISPLAY.get(_eng, _eng)
        _help = DISABLED_ENGINE_HELP.get(
            _eng,
            "Rule = deterministic logic; LLM = persona-driven prompt; "
            "RuleLLM = read-only sample (rules embedded in LLM prompt).",
        )
        with engine_cols[_idx]:
            if st.button(
                _label,
                key=f"entry_{entry_id}_engine_btn_{_eng}",
                type=("primary" if _is_current and not _is_disabled else "secondary"),
                width="stretch",
                disabled=_is_disabled,
                help=_help,
            ):
                st.session_state[engine_key] = _eng
                # Use fragment-scoped rerun so the dialog stays open.
                # st.rerun() defaults to scope="app" which closes the dialog.
                st.rerun(scope="fragment")

    if is_rulellm:
        st.info(RULELLM_SAMPLE_NOTICE, icon="📖")

    # ---- Instance count -------------------------------------------------
    ninst_key = f"entry_{entry_id}_ninst"
    if ninst_key not in st.session_state:
        st.session_state[ninst_key] = int(entry.num_instances or 1)
    st.number_input(
        "Instances",
        min_value=1,
        max_value=100,
        step=1,
        key=ninst_key,
        help=(
            "How many independent copies of THIS configured entry to spawn. "
            "Each instance receives its own identity and record path; they "
            "share the same class, engine, and parameter values but act "
            "independently. **Config key:** `num_instances`."
        ),
        disabled=is_rulellm,
    )

    # ---- Per-parameter widgets -----------------------------------------
    if not specs:
        st.info(
            "This agent's handbook has no `## Parameters` table; "
            "defaults will be used as-is."
        )
    edited: dict[str, Any] = {}
    persisted_params = dict(entry.params)
    with st.container():
        for spec in specs:
            value = _render_entry_param_widget(
                entry_id=entry_id,
                spec=spec,
                persisted=persisted_params,
                disabled=is_rulellm,
            )
            edited[spec.symbol] = value

    # ---- LLM-engine extras (prompt + hyperparameters) ------------------
    if engine in {"LLM", "RuleLLM", "Rag"}:
        _render_entry_llm_extras(
            agent=agent,
            entry_id=entry_id,
            engine=engine,
            persisted=persisted_params,
            edited=edited,
            disabled=is_rulellm,
        )

    # ---- Action buttons -------------------------------------------------
    st.divider()
    btn_save, btn_reset, btn_del, btn_close = st.columns([3, 1, 1, 1])
    _save_help = (
        DISABLED_ENGINE_HELP.get("Rag") if engine == "Rag"
        else ("RuleLLM is a read-only sample — nothing to save."
              if is_rulellm else None)
    )
    with btn_save:
        if st.button(
            "Save changes",
            type="primary",
            width="stretch",
            key=f"entry_{entry_id}_save",
            disabled=is_rulellm,
            help=_save_help,
        ):
            update_entry(
                roster,
                entry_id,
                engine=st.session_state.get(engine_key, engine),
                num_instances=int(st.session_state.get(ninst_key, 1) or 1),
                label=st.session_state.get(label_key) or None,
                params=edited,
            )
            save_state_from_session(project_root=PROJECT_ROOT)
            st.toast(
                f"{agent['display_name']} entry updated",
                icon="✅",
            )
            st.rerun()
    with btn_reset:
        if st.button(
            "Reset",
            width="stretch",
            key=f"entry_{entry_id}_reset",
            help=(
                "RuleLLM is a read-only sample — nothing to reset."
                if is_rulellm else
                "Clear this entry's parameter overrides and revert to "
                "handbook defaults. Engine, instance count, and preset "
                "label are kept."
            ),
            disabled=is_rulellm,
        ):
            update_entry(roster, entry_id, params={})
            # Also drop every entry-scoped widget so their defaults
            # repopulate from the handbook on the next open.  We
            # deliberately DO NOT delete ``entry_{id}_label`` /
            # ``entry_{id}_engine`` / ``entry_{id}_instances`` — those
            # three carry cross-reset intent (the user's preset label
            # and engine/instance picks) and the help text above
            # explicitly promises they are preserved.  Silent LLM
            # prompt widgets (``entry_{id}_llm_*``) DO get dropped
            # because they are considered part of the "parameter
            # overrides" a reset is expected to clear.
            for wkey in list(st.session_state.keys()):
                if wkey.startswith(f"entry_{entry_id}_input_") or (
                    wkey.startswith(f"entry_{entry_id}_llm_")
                ):
                    del st.session_state[wkey]
            save_state_from_session(project_root=PROJECT_ROOT)
            st.toast("Parameters reset", icon="↺")
            st.rerun(scope="fragment")
    with btn_del:
        if st.button(
            "× Delete",
            width="stretch",
            key=f"entry_{entry_id}_delete",
            help="Remove this entry from the roster.",
        ):
            remove_entry(roster, entry_id)
            # Drop scoped widget state so nothing lingers.
            for wkey in list(st.session_state.keys()):
                if wkey.startswith(f"entry_{entry_id}_"):
                    del st.session_state[wkey]
            save_state_from_session(project_root=PROJECT_ROOT)
            st.toast(
                f"{agent['display_name']} entry removed",
                icon="🗑️",
            )
            st.rerun()
    with btn_close:
        if st.button(
            "Close",
            width="stretch",
            key=f"entry_{entry_id}_close",
        ):
            st.rerun()


def _render_entry_param_widget(
    *,
    entry_id: str,
    spec: ParamSpec,
    persisted: dict[str, Any],
    disabled: bool = False,
) -> Any:
    """Render one editable widget for a parameter spec, scoped to an entry.

    Widget key format: ``entry_{entry_id}_input_{symbol}`` — unique across
    the app so two entries of the same archetype never share state.

    When ``disabled=True`` (e.g. RuleLLM sample view), the widget is
    rendered greyed-out but still shows the current handbook default.
    """
    widget_key = f"entry_{entry_id}_input_{spec.symbol}"
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
            disabled=disabled,
        )

    if spec.kind == "int":
        coerced = int(initial) if isinstance(initial, (int, float)) else 0
        kwargs: dict[str, Any] = {
            "step": 1, "key": widget_key, "help": help_text,
            "disabled": disabled,
        }
        if spec.numeric_low is not None and spec.numeric_low != float("-inf"):
            kwargs["min_value"] = int(spec.numeric_low)
        if spec.numeric_high is not None and spec.numeric_high != float("inf"):
            kwargs["max_value"] = int(spec.numeric_high)
        return st.number_input(label_main, value=coerced, **kwargs)

    if spec.kind == "float":
        coerced_f = float(initial) if isinstance(initial, (int, float)) else 0.0
        kwargs = {
            "key": widget_key, "help": help_text, "format": "%.6g",
            "disabled": disabled,
        }
        if spec.numeric_low is not None and spec.numeric_low != float("-inf"):
            kwargs["min_value"] = float(spec.numeric_low)
        if spec.numeric_high is not None and spec.numeric_high != float("inf"):
            kwargs["max_value"] = float(spec.numeric_high)
        return st.number_input(label_main, value=coerced_f, **kwargs)

    return st.text_input(
        label_main,
        value=str(initial) if initial is not None else "",
        key=widget_key,
        help=help_text,
        disabled=disabled,
    )


def _render_entry_llm_extras(
    *,
    agent: dict[str, Any],
    entry_id: str,
    engine: str,
    persisted: dict[str, Any],
    edited: dict[str, Any],
    disabled: bool = False,
) -> None:
    """Render LLM hyperparameters and editable prompt textareas for an entry.

    Widget keys are ``entry_{entry_id}_llm_{field}_{engine}`` where
    ``field`` is one of ``lm`` / ``temp`` / ``tokens`` / ``sysprompt`` /
    ``userprompt``.  Values are written into ``edited`` under the
    reserved ``__llm_*__`` sentinels so they round-trip with the rest of
    the entry's params on the next Save.

    When ``disabled=True`` (RuleLLM read-only sample), all widgets are
    greyed-out AND the persona prompt is force-loaded from the actual
    scenario RuleLLM players.yml (via
    :func:`get_rulellm_prompt_for_agent`) so the student sees the real
    ``==DECISION RULES==`` block instead of the mirrored plain-LLM prompt
    that ``customized/agent_catalog.py`` would otherwise return.

    IMPORTANT: the key names above must stay in lock-step with the
    ``_llm_widget_map`` inside :func:`_build_selections_from_session` —
    that map is what folds unsaved prompt edits back into the launch
    payload.  Renaming here without updating there silently drops any
    prompt edit the user has typed but not yet clicked "Save" on.
    """
    st.markdown("---")
    st.markdown(f"**LLM settings** — *{VARIANT_DISPLAY.get(engine, engine)} engine*")

    lm_key = f"entry_{entry_id}_llm_lm_{engine}"
    temp_key = f"entry_{entry_id}_llm_temp_{engine}"
    tok_key = f"entry_{entry_id}_llm_tokens_{engine}"
    sys_key = f"entry_{entry_id}_llm_sysprompt_{engine}"
    usr_key = f"entry_{entry_id}_llm_userprompt_{engine}"

    lm_default = persisted.get("__llm_lm_name__", "ark/doubao-seed-2-0-mini-260428")
    temp_default = float(persisted.get("__llm_temperature__", 0.7))
    tok_default = int(persisted.get("__llm_max_tokens__", 512))
    sys_default = str(persisted.get("__llm_system_prompt__", ""))
    usr_default = str(persisted.get("__llm_user_prompt__", ""))

    shipped_sys, shipped_user = get_default_prompts(agent["agent_type"], engine)
    if not sys_default and shipped_sys:
        sys_default = shipped_sys
    if not usr_default and shipped_user:
        usr_default = shipped_user

    # For RuleLLM samples, override BOTH the persona and per-round templates
    # with the actual scenario-specific text from configs/{Scenario}/RuleLLM
    # so the student sees the real "==DECISION RULES==" block. The mirrored
    # prompts returned by get_default_prompts() come from the plain LLM
    # variant (customized/agent_catalog.py:199-202) and lack scenario rules.
    if engine == "RuleLLM":
        scenario_base = st.session_state.get("selected_scenario_base", "")
        if scenario_base:
            _prompt_data = get_rulellm_prompt_for_agent(
                scenario_base, agent["agent_type"]
            )
            real_sys = (_prompt_data or {}).get("sys", "") if _prompt_data else ""
            real_usr = (_prompt_data or {}).get("user", "") if _prompt_data else ""
            if real_sys:
                sys_default = real_sys
            if real_usr:
                usr_default = real_usr

    has_shipped_sys = bool(shipped_sys) or engine == "RuleLLM"
    has_shipped_user = bool(shipped_user) or engine == "RuleLLM"

    edited["__llm_lm_name__"] = st.text_input(
        "Model identifier",
        value=lm_default,
        key=lm_key,
        help=(
            "Any identifier accepted by `LangChainAPIInference` — for "
            "example `ark/doubao-seed-2-0-mini-260428`, "
            "`openai/gpt-4o-mini`. **Config key:** `lm_name`."
        ),
        disabled=disabled,
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
            disabled=disabled,
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
            disabled=disabled,
        )

    sys_placeholder = (
        "No default persona is registered for this archetype + engine yet. "
        "Type a persona description here: beliefs, trading approach, risk "
        "attitude, etc. The output-format contract "
        "(analysis/decision tags, JSON schema) is appended automatically — "
        "do NOT include it here."
    )
    sys_label = (
        "Persona prompt (default persona shown below — edit to customize)"
        if has_shipped_sys else
        "Persona prompt (no default registered — type a custom persona)"
    )
    # Strip the locked format tail from the persisted value so the user
    # only sees / edits the persona portion.  Mirrors the Default-config
    # editor: the DECISION_FORMAT_INSTRUCTION + ANALYSIS_DECISION_TAG +
    # TRADING_CONSTRAINTS block is auto-appended by the bundle writer
    # (see ``_build_prompts_module``), so surfacing it here would let
    # the user accidentally break the LLM output contract.
    persona_only_default = _extract_persona_section(sys_default).rstrip()

    with st.expander(sys_label, expanded=True):
        if has_shipped_sys:
            st.caption(
                "This is the actual default persona shipped with the "
                "example codebase. Edit the persona description below — the "
                "output-format contract (analysis/decision tags + decision "
                "JSON schema) shown further down is appended automatically "
                "when the bundle is written, so you cannot accidentally "
                "break the LLM output contract."
            )
        else:
            st.caption(
                "No default persona has been registered for this "
                "archetype + engine combination yet. Type your persona "
                "description below — the output-format contract shown "
                "further down is auto-appended by the bundle writer."
            )
        edited["__llm_system_prompt__"] = st.text_area(
            "Persona prompt",
            value=persona_only_default,
            placeholder=sys_placeholder,
            height=260,
            key=sys_key,
            label_visibility="collapsed",
            help=(
                "Persona-only content: identity, beliefs, trading style. "
                "Do NOT include analysis/decision tags or the JSON schema "
                "— those are locked and appended automatically. "
                "**Config key:** `llm.sys_message` (persona portion)."
            ),
            disabled=disabled,
        )

        # Locked format contract — visible so the user knows exactly what
        # will be appended to their persona at bundle-write time.
        st.info(
            "**Output format** (locked — appended automatically to your "
            "persona at Launch time):\n\n"
            "```\n"
            "TRADING CONSTRAINTS:\n"
            "- Cannot spend more than your available cash\n"
            "- Cannot sell more shares than you currently hold\n"
            "\n"
            "Respond with your thinking in <analysis>...</analysis> tags "
            "followed by your decision in <decision>...</decision> tags.\n"
            "\n"
            "The decision JSON must follow this exact format:\n"
            "{\n"
            "    \"action\": \"buy\" | \"sell\" | \"hold\",\n"
            "    \"bid_price\": <float>,\n"
            "    \"quantity\": <float>,\n"
            "    \"reasoning\": <str>,\n"
            "}\n"
            "```",
            icon="\U0001f512",
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
            disabled=disabled,
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


def _render_agent_card(
    agent: dict[str, Any],
    *,
    scenario_provided_features: set[str] | None = None,
) -> None:
    """Render one card in the agent grid.

    Roster-aware: multiple entries per archetype are surfaced as an
    aggregate badge (``N entries · M×``) and a compact secondary link
    labelled "Manage N entries" that scrolls the user to the *My Roster*
    section below.

    Two primary actions on every card:

      * **+ Add** — append a new :class:`RosterEntry` for this archetype
        with default engine (Rule) and instance count 1. Immediate;
        surfaces a toast.
      * **Configure…** — append a fresh entry *and* open the edit dialog
        so the user can pick engine / edit params / adjust instance count
        before the entry is committed to the roster.

    When *scenario_provided_features* is given, the card checks the
    agent's ``REQUIRES_FEATURES`` declaration and disables action buttons
    if any required feature is missing from the current scenario.
    """
    agent_type = agent["agent_type"]
    roster = get_roster(st.session_state)
    entries_here = entries_for_type(roster, agent_type)
    entry_count = len(entries_here)
    instance_count = sum(int(e.num_instances or 1) for e in entries_here)
    selected = entry_count > 0

    # --- Compatibility check against scenario features ------------------
    agent_required = set(required_features(agent_type))
    if scenario_provided_features is not None and agent_required:
        missing_features = agent_required - scenario_provided_features
    else:
        missing_features = set()
    is_compatible = not missing_features

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

    # --- Status badge (compact pill beneath image) -------------------
    if selected:
        # Show engine breakdown when heterogeneous.
        engines = {e.engine for e in entries_here}
        engine_label = (
            next(iter(engines)) if len(engines) == 1 else "mixed"
        )
        parts = [f"\u2713 {engine_label}"]
        if entry_count > 1:
            parts.append(f"{entry_count} entries")
        if instance_count != entry_count:
            parts.append(f"\u00d7{instance_count}")
        badge_text = " · ".join(parts)

        badge = (
            "<div style='text-align:center;margin:4px 0 2px;'>"
            "<span style='display:inline-block;font-size:0.68rem;padding:2px 8px;"
            "border-radius:10px;background:#d4edda;color:#155724;font-weight:600;'>"
            f"{html.escape(badge_text)}</span></div>"
        )
    else:
        badge = (
            "<div style='text-align:center;margin:4px 0 2px;'>"
            "<span style='display:inline-block;font-size:0.68rem;padding:2px 8px;"
            "border-radius:10px;background:#f0f2f4;color:#6c757d;'>"
            "not in roster</span></div>"
        )
    st.markdown(badge, unsafe_allow_html=True)

    # --- Incompatibility badge (shown only when features are missing) ---
    if not is_compatible:
        missing_list = ", ".join(sorted(missing_features))
        incompat_badge = (
            "<div style='text-align:center;margin:2px 0 4px;'>"
            "<span style='display:inline-block;font-size:0.62rem;padding:2px 6px;"
            "border-radius:8px;background:#fff3cd;color:#856404;'>"
            f"Requires: {html.escape(missing_list)}</span></div>"
        )
        st.markdown(incompat_badge, unsafe_allow_html=True)

    # --- Agent name: clickable text button -> opens profile dialog ---
    if st.button(
        agent["display_name"],
        key=f"market_profile_{agent_type}",
        type="tertiary",
        help=agent.get("intro", "View this agent's design profile"),
    ):
        _show_catalog_agent_profile_dialog(agent)

    # --- Primary action row: + Add (quick) and Configure… (opens dialog)
    _incompat_help = (
        f"This agent requires market features ({', '.join(sorted(missing_features))}) "
        "that the current scenario does not provide. Choose a compatible "
        "scenario or pick a different agent."
    ) if not is_compatible else None

    if st.button(
        "+ Add",
        key=f"market_quick_add_{agent_type}",
        type="primary",
        width="stretch",
        disabled=not is_compatible,
        help=(
            _incompat_help
            if not is_compatible
            else (
                "Append a new roster entry for this agent with default "
                "settings (Rule engine, 1 instance). You can add the same "
                "agent multiple times with different configurations."
            )
        ),
    ):
        add_entry(roster, agent_type=agent_type, engine="Rule", num_instances=1)
        save_state_from_session(project_root=PROJECT_ROOT)
        st.toast(f"Added {agent['display_name']}", icon="➕")
        st.rerun()

    if st.button(
        "Configure…",
        key=f"market_configure_{agent_type}",
        type="tertiary",
        width="stretch",
        disabled=not is_compatible,
        help=(
            _incompat_help
            if not is_compatible
            else (
                "Create a new roster entry and immediately open its editor "
                "to pick engine, adjust parameters, and (for LLM engines) "
                "edit the prompt before committing."
            )
        ),
    ):
        new_entry = add_entry(
            roster, agent_type=agent_type, engine="Rule", num_instances=1
        )
        save_state_from_session(project_root=PROJECT_ROOT)
        _show_entry_edit_dialog(agent, new_entry.id)

    # --- Secondary action: quick jump to the Roster list for management
    if selected:
        st.markdown(
            "<div style='text-align:center;margin-top:2px;'>"
            "<span style='font-size:0.68rem;color:#6c757d;'>"
            f"Manage in <b>My Roster</b> below ({entry_count} "
            f"{'entry' if entry_count == 1 else 'entries'})"
            "</span></div>",
            unsafe_allow_html=True,
        )


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


@st.dialog("Live market preview", width="large")
def _show_market_preview_dialog(selected_agents: list[dict[str, Any]]) -> None:
    """Deprecated stand-alone dialog kept only for backwards compatibility.

    The live-market-preview expand affordance now flows through the shared
    ``render_d3_topology_with_expand`` helper in ``topology_d3.py``.
    """
    if not selected_agents:
        st.caption(
            "No agents selected yet. Pick agents from the grid to preview "
            "the market topology here."
        )
        return
    st.caption(f"{len(selected_agents)} agents connected to the market hub")
    _render_live_market_preview(selected_agents, height=620, with_expand=False)


def _render_live_market_preview(
    selected_agents: list[dict[str, Any]],
    height: int = 260,
    *,
    with_expand: bool = True,
) -> None:
    """Render a compact star topology of the currently selected agents.

    Uses the same D3 renderer that powers the Experience mode topology,
    fed a synthetic ``market`` hub with a spoke to each selected agent.
    Icons are supplied via the ``icon_uris`` override so opinion-domain
    agents (whose icons are ``opinion-*.png``) render correctly too.
    """
    from .topology_d3 import market_icon_uri, render_d3_topology, render_d3_topology_with_expand

    if not selected_agents:
        st.markdown("**Live market preview**")
        st.caption(
            "No agents selected yet. Click **Load default agents** or pick "
            "agents from the grid to preview the market topology here."
        )
        return

    node_ids = [a["agent_type"] for a in selected_agents]
    roster = get_roster(st.session_state)
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
            "instances": total_instances(roster, a["agent_type"]) or 1,
            "role": "player",
        }
        for a in selected_agents
    ]
    icon_uris = {
        a["agent_type"]: a.get("image_uri", "") for a in selected_agents
    }
    # Attach the market coordinator icon so the hub in the customize
    # preview visually matches the scenario's market family.
    _preview_base = st.session_state.get("selected_scenario_base", "")
    _market_uri = market_icon_uri(_preview_base)
    if _market_uri:
        icon_uris["market"] = _market_uri
    if with_expand:
        render_d3_topology_with_expand(
            topology,
            agent_records,
            height=height,
            icon_uris=icon_uris,
            key="live_market_preview",
            title="Live market preview",
            dialog_caption=(
                f"{len(selected_agents)} agents connected to the market hub"
            ),
        )
    else:
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
        # NOTE: ``st.rerun()`` does NOT abort the current run, so we MUST
        # ``return`` immediately; otherwise everything below (state restore,
        # legacy migration, sidebar render, etc.) would execute with an
        # empty ``scenario_base`` and can pollute session state.
        st.session_state.workflow_stage = "scenario_setup"
        st.rerun()
        return

    # --- Restore persisted selection state on fresh session entry ---
    # If a bundle exists but no roster has been loaded in memory (e.g.
    # after a page refresh or app restart), attempt to recover from disk.
    bundle_name = st.session_state.get("customized_bundle_name", "")
    if bundle_name and not get_roster(st.session_state):
        restore_state_to_session(
            bundle_name=bundle_name, project_root=PROJECT_ROOT
        )

    _inject_market_styles()
    catalog = load_agent_catalog(_agent_catalog_signature())

    # One-time in-session migration: if a legacy flat selection still
    # exists in session state (from a pre-refactor UI load) but the
    # roster is empty, fold the flat state into a fresh roster so the
    # user's previous work isn't lost when they navigate back to the
    # Customize page.
    if not get_roster(st.session_state):
        legacy_selected = list(
            st.session_state.get("selected_market_agents", []) or []
        )
        if legacy_selected:
            legacy_engines: dict[str, str] = {}
            legacy_ninst: dict[str, int] = {}
            for agent_type in legacy_selected:
                legacy_engines[agent_type] = st.session_state.get(
                    f"market_engine_{agent_type}", "Rule"
                )
                try:
                    legacy_ninst[agent_type] = int(
                        st.session_state.get(
                            f"customized_num_instances_{agent_type}", 1
                        ) or 1
                    )
                except (TypeError, ValueError):
                    legacy_ninst[agent_type] = 1
            legacy_params = st.session_state.get("customized_params") or {}
            entries = migrate_from_legacy_state(
                selected_agents=legacy_selected,
                engines=legacy_engines,
                num_instances=legacy_ninst,
                params=legacy_params,
            )
            set_roster(st.session_state, entries)

    # Derived cache: ``selected_market_agents`` used to be the flat
    # source of truth. We now compute it from the roster on every render
    # so downstream consumers (sidebar, chips, preview) keep working.
    roster_snapshot = get_roster(st.session_state)
    st.session_state.selected_market_agents = unique_agent_types(roster_snapshot)

    # Compute the current selection ONCE up front so the sidebar preview and
    # the main-column grid share a single source of truth.
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
        try:
            shipped_rounds = int(info.get("total_rounds") or 0)
        except (TypeError, ValueError):
            shipped_rounds = 0
        feats = scenario_market_features(scenario_base)
        feats_text = ", ".join(sorted(feats)) if feats else "standard"

        # Editable rounds — mirrors the widget on the variant_choice page
        # so the user can also adjust the round count from inside the
        # Customize flow.  Persisted under the same session key
        # (``variant_rounds_<base>``) so ``_write_customized_bundle``
        # picks it up unchanged.
        _rounds_key = f"variant_rounds_{scenario_base}"
        _rounds_default = shipped_rounds if shipped_rounds > 0 else 1
        _rounds_now = int(
            st.session_state.get(_rounds_key, _rounds_default)
        )
        chip_col, num_col = st.columns([3, 1])
        with chip_col:
            st.markdown(
                f"<div class='scenario-confirm-chip' style='margin-top:14px'>"
                f"🔒 {html.escape(scenario_display_name(scenario_base))} · "
                f"{html.escape(feats_text)}"
                f"</div>",
                unsafe_allow_html=True,
            )
        with num_col:
            edited_rounds = st.number_input(
                "Rounds",
                min_value=1,
                max_value=100000,
                value=_rounds_now,
                step=1,
                key=f"widget_customize_{_rounds_key}",
                help=(
                    f"Number of simulation rounds. Shipped default: "
                    f"{shipped_rounds if shipped_rounds > 0 else 'n/a'}."
                ),
            )
            st.session_state[_rounds_key] = int(edited_rounds)

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
            # Roster semantics: the default preset REPLACES the current
            # roster with one entry per default archetype so the user
            # gets a clean starting point.  Any bespoke entries the user
            # added get overwritten — matching the pre-refactor behaviour
            # of the flat checkbox reset.
            clear_roster(st.session_state)
            # Also drop every entry-scoped widget key so stale values
            # from the previous roster cannot leak into the fresh entries.
            for wkey in list(st.session_state.keys()):
                if wkey.startswith("entry_"):
                    del st.session_state[wkey]
            roster_now = get_roster(st.session_state)
            for agent_type in default_available:
                add_entry(
                    roster_now,
                    agent_type=agent_type,
                    engine="Rule",
                    num_instances=1,
                )
            st.session_state.selected_market_agents = list(default_available)
            save_state_from_session(project_root=PROJECT_ROOT)
            st.rerun()

    st.write(
        "Click **+ Add** on any agent card to append a new roster entry. "
        "The same agent can appear multiple times with different engines "
        "and parameters — click **Configure…** to edit before committing, "
        "or open the **My Roster** list below to Edit / Duplicate / Remove "
        "any entry independently. Click an agent's **name** for its full "
        "design profile."
    )

    # Legacy inline profile (query-param based) kept for bookmarked URLs.
    requested_agent = _query_agent()
    by_type = {agent["agent_type"]: agent for agent in catalog}
    if requested_agent in by_type:
        _render_profile(by_type[requested_agent])

    # ---- Agent grid: wrapped in @st.fragment for scoped reruns ------
    # Only search / grid widgets trigger fragment-local reruns.
    # Full-page reruns (sidebar preview, Load default, Clear, Launch)
    # still happen through their own buttons outside this scope.
    #
    # LAZY LOADING: agents are split by *thematic category* into
    # ``st.tabs()`` (Crisis / Mechanics / Behavioral / Momentum /
    # Fundamental / Opinion / Other) — only the ACTIVE tab renders its
    # cards on each rerun, so the landing view only pays the image-decode
    # / roster-check cost for one category at a time.  Categories that
    # have zero agents in the catalog are hidden.
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
            roster_here = get_roster(st.session_state)
            st.metric(
                "Roster entries",
                len(roster_here),
                delta=(
                    f"{total_instances(roster_here)} instances"
                    if roster_here
                    else None
                ),
                delta_color="off",
            )

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

        # Hide agents whose REQUIRES_FEATURES aren't satisfied by the
        # current scenario.  These specialist agents (designed for specific
        # coordinator types like DeFi/FX/credit) cannot function in the
        # selected scenario and would only confuse users.
        _provided = scenario_market_features(scenario_base)
        filtered = [
            agent
            for agent in filtered
            if set(required_features(agent["agent_type"])).issubset(_provided)
        ]

        if not filtered:
            st.info("No agents match this search.")
            return

        # Group by *thematic category* for tab-based lazy loading. Finer
        # than the raw finance/opinion domain split so a 200-agent pool
        # (~195 finance + ~5 opinion) surfaces as five browsable buckets
        # instead of one giant Finance tab.  Order = display order;
        # matching is first-wins so the ambiguous "leveraged-buyer" style
        # stems land in the most specific bucket that mentions them.
        #
        # Rules are keyword-substring based against the agent_type stem
        # (kebab-case).  A stem may hit many patterns — the first winning
        # rule assigns it, so put highly specific / low-ambiguity rules
        # first (crisis actors are named, mechanics uses precise terms
        # like "hft" / "market-maker", biases are lexically distinctive).
        # Anything that matches no rule falls into "Other" so nothing is
        # dropped from the catalog.
        _CATEGORY_RULES: list[tuple[str, str, tuple[str, ...]]] = [
            (
                "crisis",
                "🔥 Crisis & Systemic",
                (
                    "depositor", "run-", "panic", "forced-seller", "forced-",
                    "central-bank", "regulator", "contagion", "sovereign",
                    "imf", "ecb", "minsky", "distressed", "creditor",
                    "default-", "bank-manager", "rescuer", "intervenor",
                    "flight-", "carry-", "peg-", "rating-agency",
                    "prime-broker", "speculative-attacker", "pro-cyclical",
                    "counter-cyclical", "periphery-", "stablecoin",
                    "funding-currency",
                ),
            ),
            (
                "mechanics",
                "⚡ Market Mechanics",
                (
                    "hft", "high-frequency", "algorithmic", "algo-",
                    "market-maker", "arbitrag", "stop-loss", "block-trade",
                    "flash-", "liquidity-provider", "liquidity-demander",
                    "liquidity-seeker", "index-tracker", "index-arbitrag",
                    "gamma", "convergence-", "program-trader",
                    "technical-trader", "portfolio-insurer",
                    "risk-parity", "vol-etn", "short-vol", "short-seller",
                    "active-rebalancer", "opportunistic-trader",
                    "volatility-trader",
                ),
            ),
            (
                "behavioral",
                "🧠 Behavioral Biases",
                (
                    "anchor", "anchored", "overconfident", "hindsight",
                    "disposition", "framing", "gain-frame", "loss-frame",
                    "endow", "loss-averse", "myopic", "mental-account",
                    "hot-hand", "house-money", "category-overgen",
                    "break-even", "commitment", "regret", "availability",
                    "confirmation", "recency", "narrative-believer",
                    "gambler", "base-rate", "escalat", "sunk-cost",
                    "prospect", "frame-invariant", "inertial-",
                    "status-quo", "self-attributor", "recent-event",
                    "streak-reversal", "tax-aware", "risk-averse",
                    "risk-neutral", "opportunity-cost", "outcome-learner",
                    "slow-adapter", "self-fulfilling", "aggressive-",
                    "bottom-fisher",
                ),
            ),
            (
                "momentum",
                "🌊 Momentum & Herding",
                (
                    "momentum", "trend", "herd", "cascade", "follower",
                    "chaser", "media-influenced", "greater-fool",
                    "speculator", "retail-", "ipo-flip", "hot-money",
                    "evangelist", "conformist", "default-follower",
                    "gullible", "ideologue", "new-buyer", "sentiment-",
                    "social-media", "pattern-matcher", "distorting-",
                    "opinion-environment", "information-environment",
                    "noise-trader", "passive-bystander",
                    "skeptical-evaluator", "early-exit",
                ),
            ),
            (
                "fundamental",
                "📊 Fundamental & Informed",
                (
                    "fundamental", "value-investor", "value-buyer",
                    "value-trader", "informed", "analyst", "bayesian",
                    "calibrated", "critical-thinker", "fact-checker",
                    "expert", "intrinsic-value", "mbs-originator",
                    "bond-trader", "long-horizon", "long-term",
                    "institutional", "insider", "contrarian",
                    "independent-", "conservative-", "balanced-",
                    "concentrated-fund", "core-bond", "index-fund",
                    "index-holder", "hedge", "rational-", "leverage-",
                    "leveraged-", "de-fi", "equity-trader",
                    "passive-investor", "risk-manager",
                    "process-evaluator", "selective-scanner",
                    "information-trader", "bridge-builder",
                ),
            ),
        ]

        def _classify(agent: dict[str, Any]) -> tuple[str, str]:
            if agent.get("domain") == "opinion":
                return ("opinion", "💬 Opinion Agents")
            stem = agent.get("agent_type", "").lower()
            for key, label, patterns in _CATEGORY_RULES:
                for pat in patterns:
                    if pat in stem:
                        return (key, label)
            return ("other", "📎 Other")

        _CATEGORY_ORDER = [
            "crisis", "mechanics", "behavioral", "momentum",
            "fundamental", "opinion", "other",
        ]
        _CATEGORY_LABELS = {k: lbl for k, lbl, _ in _CATEGORY_RULES}
        _CATEGORY_LABELS["opinion"] = "💬 Opinion Agents"
        _CATEGORY_LABELS["other"] = "📎 Other"

        by_category: dict[str, list[dict[str, Any]]] = {}
        for agent in filtered:
            key, _label = _classify(agent)
            by_category.setdefault(key, []).append(agent)
        active_categories = [c for c in _CATEGORY_ORDER if by_category.get(c)]

        # Pre-compute the scenario's provided features for card-level gating.
        _scenario_feats: set[str] = scenario_market_features(scenario_base)

        def _render_grid(agents: list[dict[str, Any]]) -> None:
            grid_columns_per_row = 6
            for start in range(0, len(agents), grid_columns_per_row):
                columns = st.columns(grid_columns_per_row, gap="small")
                for column, agent in zip(
                    columns, agents[start : start + grid_columns_per_row]
                ):
                    with column:
                        _render_agent_card(
                            agent,
                            scenario_provided_features=_scenario_feats,
                        )

        if len(active_categories) <= 1:
            # Single-category result set (typical when the search box
            # narrows the pool) — no need for tabs; render inline.
            _render_grid(
                by_category.get(active_categories[0], [])
                if active_categories
                else []
            )
            return

        tab_labels = [
            f"{_CATEGORY_LABELS[c]} ({len(by_category[c])})"
            for c in active_categories
        ]
        tabs = st.tabs(tab_labels)
        for category, tab in zip(active_categories, tabs):
            with tab:
                _render_grid(by_category[category])

    _agent_grid_fragment()

    selected = _selected_types(catalog)
    st.session_state.selected_market_agents = selected
    selected_agents = [a for a in catalog if a["agent_type"] in set(selected)]

    # Auto-remove incompatible agents from the roster.  Since the grid
    # already hides specialist agents, any incompatible entries are leftovers
    # from a previous session or a scenario switch — silently clean them up.
    if selected_agents:
        roster_types = [a["agent_type"] for a in selected_agents]
        ok, _reasons = is_scenario_compatible(scenario_base, roster_types)
        if not ok:
            provided = scenario_market_features(scenario_base)
            bad_types = [
                atype for atype in roster_types
                if not set(required_features(atype)).issubset(provided)
            ]
            if bad_types:
                roster = get_roster(st.session_state)
                for entry in list(roster):
                    if entry.agent_type in bad_types:
                        remove_entry(roster, entry.id)
                save_state_from_session(project_root=PROJECT_ROOT)
                st.rerun()

    st.divider()
    if selected_agents:
        st.markdown("**Current market**")
        _render_market_chips(selected_agents)

    # ---- My Roster: full entry-level management ---------------------
    # Rendered even when empty so first-time users see the affordance
    # and know where their +Add clicks are going.
    st.markdown("---")
    _render_my_roster(catalog)

    # --- Market Parameters Editor ---
    bundle_name = st.session_state.get("customized_bundle_name", "")
    if bundle_name:
        with st.expander("Market Parameters", expanded=False):
            st.caption(
                "Edit the market coordinator's parameters. These control "
                "price dynamics, impact coefficients, and noise in the "
                "simulation."
            )
            # Load defaults from the bundle's Rule/players.yml.
            default_extras = extract_market_extras(
                bundle_name=bundle_name,
                scenario_name=scenario_base,
                project_root=PROJECT_ROOT,
            )
            if default_extras:
                # Initialize persisted overrides from session state or disk.
                persisted_market = st.session_state.setdefault(
                    "customized_market_extras", {}
                )
                edited_market: dict = {}
                cols_per_row = 3
                keys = list(default_extras.keys())
                for row_start in range(0, len(keys), cols_per_row):
                    row_keys = keys[row_start : row_start + cols_per_row]
                    cols = st.columns(len(row_keys))
                    for col, param_key in zip(cols, row_keys):
                        with col:
                            default_val = default_extras[param_key]
                            current_val = persisted_market.get(
                                param_key, default_val
                            )
                            # Render as float input.
                            label = param_key.replace("_", " ").title()
                            widget_key = f"market_extra_{param_key}"
                            new_val = st.number_input(
                                label,
                                value=float(current_val),
                                format="%.6g",
                                key=widget_key,
                                help=f"Default: {default_val}",
                            )
                            edited_market[param_key] = new_val

                # Update session state if user changed anything.
                if edited_market != persisted_market:
                    st.session_state["customized_market_extras"] = edited_market
                    save_state_from_session(project_root=PROJECT_ROOT)
            else:
                st.info("No editable market parameters found for this scenario.")

    # --- Config preview: dry-run the bundle write to show the exact YAML
    # the user is about to launch.  Uses the same code path as the actual
    # Launch button so what they see is precisely what runs.  Rendered
    # inside a collapsed expander so it stays out of the way but is a
    # click away when the user wants to audit the config.
    if selected_agents:
        _render_config_preview(
            selected_agents=selected_agents,
            scenario_base=scenario_base,
        )

    reset_col, launch_col = st.columns([1, 3])
    with reset_col:
        if st.button(
            "Clear selection",
            width="stretch",
            disabled=not selected,
            key="customize_clear",
        ):
            clear_roster(st.session_state)
            # Also drop every entry-scoped widget key so no stale widget
            # state lingers if the user immediately adds new entries.
            for wkey in list(st.session_state.keys()):
                if wkey.startswith("entry_"):
                    del st.session_state[wkey]
            st.session_state.selected_market_agents = []
            save_state_from_session(project_root=PROJECT_ROOT)
            st.rerun()
    with launch_col:
        if st.button(
            "Launch simulation →",
            type="primary",
            width="stretch",
            disabled=not selected,
            key="customize_launch",
        ):
            target = _write_customized_bundle(
                selected_agents=selected_agents,
                scenario_base=scenario_base,
            )
            if target is None:
                return
            # Persist AFTER _write_customized_bundle: that helper sweeps
            # live widget state into ``customized_params`` and merges every
            # unsaved dialog edit. Calling save_state_from_session here
            # (instead of before) guarantees the on-disk state file mirrors
            # exactly what was rendered into players.yml.
            save_state_from_session(project_root=PROJECT_ROOT)
            _clear_query_agent()
            st.session_state.selected_scenario = target
            # Post-launch the simulation page must mirror Experience mode:
            # a purely read-only workspace with no "Edit market" strip in the
            # body. That strip is driven by ``selected_market_agents`` being
            # non-empty (see ``render_selected_market_strip``), so clear it
            # here after the bundle is written to disk.
            st.session_state.selected_market_agents = []
            st.session_state.workflow_stage = "workspace"
            st.session_state.current_page = "Simulation"
            st.rerun()


def _render_market_chips(agents: list[dict[str, Any]]) -> None:
    """Render the compact "current market" strip.

    Instance counts are aggregated across every roster entry that shares
    the same ``agent_type`` so an archetype configured twice (e.g. 3
    Aggressive + 2 Cautious NoiseTraders) surfaces the total (×5) rather
    than the per-entry count.
    """
    roster = get_roster(st.session_state)
    chips = []
    for agent in agents:
        ninst = total_instances(roster, agent["agent_type"])
        entry_count = len(entries_for_type(roster, agent["agent_type"]))
        badge = ""
        if ninst > 1 or entry_count > 1:
            badge = (
                f'<span style="margin-left:6px;padding:1px 6px;'
                f'border-radius:8px;background:#2a5fa6;color:white;'
                f'font-size:0.7rem;font-weight:600;">×{ninst}</span>'
            )
        chips.append(
            '<span class="market-chip">'
            f'<img src="{agent["image_uri"]}" alt="">'
            f'{html.escape(agent["display_name"])}{badge}'
            "</span>"
        )
    st.markdown(
        f'<div class="market-strip">{"".join(chips)}</div>',
        unsafe_allow_html=True,
    )


def _render_my_roster(catalog: list[dict[str, Any]]) -> None:
    """Render the *My Roster* list as a compact multi-column grid.

    The panel doubles as a live visual overview of the entire lineup, so
    entries are laid out in a grid (up to three per row) with a small
    icon, a tight info block, and a single narrow action column that
    stacks **Edit**, **Duplicate**, and **×** vertically to save
    horizontal space.

    * **Edit** — opens the entry's edit dialog (:func:`_show_entry_edit_dialog`).
    * **Duplicate** — inserts a clone immediately below with a fresh id
      (label suffixed with "(copy)" when present).
    * **×** — deletes just this row without touching the rest.

    Empty roster renders a friendly hint pointing users at the grid /
    Load default agents button above.
    """
    roster = get_roster(st.session_state)
    st.markdown("**My Roster**")
    if not roster:
        st.caption(
            "No entries yet — click **+ Add** on any agent card above to "
            "append a fresh roster row, or **Load default agents** to seed "
            "the scenario's shipped lineup."
        )
        return

    st.caption(
        f"{len(roster)} entries · "
        f"{total_instances(roster)} total instances. "
        "Each row is an independent configuration — the same agent can "
        "appear multiple times with different engines or parameters."
    )

    by_type = {a["agent_type"]: a for a in catalog}
    roster_snapshot = list(roster)
    # Emoji-only action buttons (✏️ / 📋 / 🗑️) are narrow enough to
    # comfortably fit three cards per row again — giving the panel a
    # dense at-a-glance overview of the whole lineup. Trailing empty
    # slots keep card widths consistent when the roster count is not a
    # multiple of the row size.
    cards_per_row = 3
    total = len(roster_snapshot)
    for row_start in range(0, total, cards_per_row):
        row_slice = roster_snapshot[row_start : row_start + cards_per_row]
        columns = st.columns(cards_per_row, gap="small")
        for offset, entry in enumerate(row_slice):
            pos = row_start + offset + 1
            with columns[offset]:
                _render_roster_card(entry, pos, by_type.get(entry.agent_type))
        # Fill trailing empty slots so the row keeps a consistent width.
        for empty_slot in range(len(row_slice), cards_per_row):
            with columns[empty_slot]:
                st.empty()


def _render_roster_card(
    entry: RosterEntry,
    pos: int,
    agent: dict[str, Any] | None,
) -> None:
    """Render one bordered card for a single roster entry.

    Layout inside the bordered card::

        ┌──────────────────────────┐
        │ [icon] Name #pos label   │  ← top row: fixed-width icon + info
        │        engine ×N params  │
        │        entry-id          │
        ├──────────────────────────┤
        │ [Edit] [Dup] [×]         │  ← full-width action bar (3 equal cols)
        └──────────────────────────┘

    The action bar spans the full inner width of the card so the three
    tertiary buttons each get roughly one third of the card width and
    stay inside the border regardless of how narrow the outer grid
    column gets (three cards per row on a typical screen).
    """
    roster = get_roster(st.session_state)

    # Missing-catalog stub: keep a compact one-liner + delete affordance.
    if agent is None:
        with st.container(border=True):
            info_col, del_col = st.columns([4, 1])
            with info_col:
                st.markdown(
                    f"<div style='font-size:0.82rem;font-weight:600;'>"
                    f"{html.escape(entry.agent_type)}</div>"
                    f"<div style='color:#c1272d;font-size:0.68rem;'>"
                    f"catalog entry missing · engine {html.escape(entry.engine)}"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            with del_col:
                if st.button(
                    "🗑️",
                    key=f"roster_del_orphan_{entry.id}",
                    type="tertiary",
                    width="stretch",
                    help="Remove this orphaned entry.",
                ):
                    remove_entry(roster, entry.id)
                    save_state_from_session(project_root=PROJECT_ROOT)
                    st.rerun()
        return

    with st.container(border=True):
        # --- Top row: fixed-width icon + info block --------------------
        # ``vertical_alignment="center"`` glues the info stack to the
        # icon's vertical mid-line so short info blocks don't float at
        # the top while the icon dangles to the right.
        icon_col, info_col = st.columns(
            [1, 5], gap="small", vertical_alignment="center"
        )

        with icon_col:
            img_path = Path(agent.get("image_file", ""))
            if img_path.exists():
                # Fixed pixel width so the icon never fights the info
                # column for horizontal space (use_container_width would
                # blow up on wide viewports and squeeze the info).
                st.image(str(img_path), width=44)
            else:
                st.markdown(
                    "<div style='width:44px;height:44px;border-radius:6px;"
                    "background:#e8f0fb;display:flex;align-items:center;"
                    "justify-content:center;color:#2a5fa6;font-weight:700;"
                    "font-size:0.85rem;'>"
                    f"{html.escape(agent['display_name'][0])}</div>",
                    unsafe_allow_html=True,
                )

        with info_col:
            # Line 1: display name (compact) + optional label chip + pos badge.
            label_html = ""
            if entry.label:
                label_html = (
                    "<span style='margin-left:6px;padding:1px 6px;"
                    "border-radius:8px;background:#eef4ff;color:#264d80;"
                    "font-size:0.62rem;font-weight:600;'>"
                    f"{html.escape(entry.label)}</span>"
                )
            st.markdown(
                "<div style='font-size:0.78rem;font-weight:600;"
                "line-height:1.15;overflow:hidden;text-overflow:ellipsis;'>"
                f"{html.escape(agent['display_name'])}"
                "<span style='margin-left:6px;color:#8a97a5;"
                "font-size:0.62rem;font-weight:500;'>"
                f"#{pos}</span>"
                f"{label_html}</div>",
                unsafe_allow_html=True,
            )
            # Line 2: engine chip + instance count + tiny edit hints.
            param_count = sum(
                1 for k in entry.params if not k.startswith("__llm_")
            )
            llm_edited = any(k.startswith("__llm_") for k in entry.params)
            summary_bits = [
                "<span style='padding:1px 6px;border-radius:8px;"
                "background:#f0f4fa;color:#2a5fa6;font-size:0.62rem;"
                f"font-weight:600;'>{html.escape(entry.engine)}</span>",
                "<span style='color:#6c757d;font-size:0.64rem;'>"
                f"×{entry.num_instances} instances</span>",
            ]
            if param_count:
                summary_bits.append(
                    "<span style='color:#6c757d;font-size:0.64rem;'>"
                    f"{param_count} param{'s' if param_count > 1 else ''} edited</span>"
                )
            if llm_edited:
                summary_bits.append(
                    "<span style='color:#6c757d;font-size:0.64rem;'>"
                    "LLM edits</span>"
                )
            st.markdown(
                "<div style='margin-top:2px;display:flex;gap:8px;"
                "align-items:center;flex-wrap:wrap;'>"
                + "".join(summary_bits)
                + "</div>"
                "<div style='margin-top:1px;color:#9aa3ad;"
                "font-size:0.58rem;font-family:ui-monospace,monospace;"
                "line-height:1.15;overflow:hidden;text-overflow:ellipsis;"
                "white-space:nowrap;'>"
                f"{html.escape(entry.id)}</div>",
                unsafe_allow_html=True,
            )

        # --- Bottom action bar: full-width row, 3 equal columns --------
        # Sitting on its own row inside the same bordered container
        # guarantees the buttons stay flush with the card frame instead
        # of overflowing the previous narrow side column. Labels are
        # emoji-only (✏️ / 📋 / 🗑️) for a compact overview grid —
        # hover tooltips carry the full description for discoverability.
        act_edit, act_dup, act_del = st.columns(3, gap="small")
        with act_edit:
            if st.button(
                "✏️",
                key=f"roster_edit_{entry.id}",
                width="stretch",
                type="tertiary",
                help="Edit — open this entry's editor dialog.",
            ):
                _show_entry_edit_dialog(agent, entry.id)
        with act_dup:
            if st.button(
                "📋",
                key=f"roster_dup_{entry.id}",
                width="stretch",
                type="tertiary",
                help=(
                    "Duplicate — insert a copy of this entry immediately "
                    "below. Handy for tweaking a variant without losing "
                    "the original."
                ),
            ):
                clone = duplicate_entry(roster, entry.id)
                # Copy widget state so the new entry opens with the same
                # values pre-populated on first edit.
                if clone is not None:
                    src_prefix = f"entry_{entry.id}_"
                    dst_prefix = f"entry_{clone.id}_"
                    for wkey in list(st.session_state.keys()):
                        if wkey.startswith(src_prefix):
                            tail = wkey[len(src_prefix):]
                            st.session_state[dst_prefix + tail] = (
                                st.session_state[wkey]
                            )
                save_state_from_session(project_root=PROJECT_ROOT)
                st.toast("Entry duplicated", icon="📄")
                st.rerun()
        with act_del:
            if st.button(
                "🗑️",
                key=f"roster_del_{entry.id}",
                width="stretch",
                type="tertiary",
                help="Remove — delete this entry (does not touch the others).",
            ):
                remove_entry(roster, entry.id)
                # Drop scoped widget state so nothing lingers for future
                # entries that happen to reuse the id space.
                prefix = f"entry_{entry.id}_"
                for wkey in list(st.session_state.keys()):
                    if wkey.startswith(prefix):
                        del st.session_state[wkey]
                save_state_from_session(project_root=PROJECT_ROOT)
                st.toast("Entry removed", icon="🗑️")
                st.rerun()


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

    # Resolve the scenario's market coordinator so the card carries a
    # clear visual identifier for the market family (Stock / FX / Credit /
    # Crypto / Deposit / Derivatives / Opinion / Information / Bond).
    # Both the archetype-driven icon and the human-readable market-type
    # label live in ``config_loader``; here we just glue them together.
    icon_path = get_market_icon_path(
        _scenario_probe_key(scenario_base, groups)
    )
    market_type_label = get_market_type(
        _scenario_probe_key(scenario_base, groups)
    ) or ""
    if icon_path and icon_path.exists():
        icon_uri = _image_data_uri(icon_path)
        icon_node = (
            f'<img class="scenario-icon" src="{icon_uri}" alt="" />'
            if icon_uri else '<div class="scenario-icon fallback">\u25a0</div>'
        )
    else:
        icon_node = '<div class="scenario-icon fallback">\u25a0</div>'

    st.markdown(
        f"""
        <div class="scenario-card {state_class}">
          <div class="scenario-header">
            {icon_node}
            <div class="scenario-header-text">
              <div class="scenario-name">{html.escape(name)}</div>
              <div class="scenario-market">{html.escape(market_type_label)}</div>
            </div>
          </div>
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
            st.session_state.workflow_stage = "variant_choice"
            st.rerun()


def _render_config_preview(
    *,
    selected_agents: list[dict[str, Any]],
    scenario_base: str,
) -> None:
    """Show a read-only preview of the config that Launch will materialise.

    Two-tier disclosure so it stays out of the way:

    - **Roster summary** (always visible inside the expander) — one row
      per selected agent listing archetype, engine, num_instances, and
      the count of customized parameters.  This lets the user verify at
      a glance that the checkbox toggles, engine picks, and instance
      spinners match their intent before spending a launch on a wrong
      config.
    - **Generated `players.yml`** (button-gated) — renders the exact
      YAML text that Launch would write.  Behind a button because
      producing it requires running the config-writer against the on-
      disk bundle, which we don't want to trigger on every rerun.
    """
    with st.expander("Preview generated config", expanded=False):
        st.caption(
            "Verify that the roster below matches what you intend to "
            "launch.  Numbers reflect the current session state; the "
            "Launch button uses this exact snapshot."
        )
        by_type = {a["agent_type"]: a for a in selected_agents}
        roster = get_roster(st.session_state)
        rows: list[dict[str, Any]] = []
        for pos, entry in enumerate(roster, start=1):
            agent = by_type.get(entry.agent_type)
            display_name = (
                agent["display_name"] if agent else entry.agent_type
            )
            # Merge entry.params with live entry-scoped widget snapshot
            # so the preview reflects unsaved edits.
            widget_prefix = f"entry_{entry.id}_input_"
            live_widget_keys = {
                k[len(widget_prefix):]
                for k in st.session_state.keys()
                if k.startswith(widget_prefix)
            }
            all_symbols = set(entry.params.keys()) | live_widget_keys
            handbook_syms = {
                s for s in all_symbols if not s.startswith("__llm_")
            }
            llm_syms = {s for s in all_symbols if s.startswith("__llm_")}
            label_display = entry.label or ""
            rows.append({
                "#": pos,
                "Agent": display_name,
                "Label": label_display,
                "Archetype": entry.agent_type,
                "Engine": entry.engine,
                "Instances": int(entry.num_instances or 1),
                "Custom params": len(handbook_syms),
                "LLM overrides": len(llm_syms),
                "Entry id": entry.id,
            })
        if rows:
            st.dataframe(rows, width="stretch", hide_index=True)
        else:
            st.info("No entries in the roster yet.")

        # Rounds + market-extras summary.
        rounds_now = int(
            st.session_state.get(f"variant_rounds_{scenario_base}", 0) or 0
        )
        market_extras = st.session_state.get("customized_market_extras") or {}
        summary_bits: list[str] = []
        if rounds_now:
            summary_bits.append(f"**Rounds:** {rounds_now}")
        if market_extras:
            summary_bits.append(
                f"**Market overrides:** {len(market_extras)} key(s) — "
                + ", ".join(f"`{k}={v}`" for k, v in market_extras.items())
            )
        if summary_bits:
            st.markdown(" · ".join(summary_bits))

        # Optional deep-dive: regenerate the YAML on demand.  Uses the
        # same code path as Launch so the preview is an EXACT match for
        # what will run.  Kept behind a button so opening the expander
        # doesn't touch disk.
        if st.button(
            "Regenerate & show players.yml",
            key="customize_preview_regen",
            help=(
                "Run the bundle writer against the current session "
                "state and display the resulting YAML.  Safe: rewrites "
                "the bundle files that Launch would rewrite anyway."
            ),
        ):
            bundle_name = st.session_state.get("customized_bundle_name", "")
            if not bundle_name:
                st.warning(
                    "Bundle folder has not been initialized yet. "
                    "Select at least one agent and click Launch once "
                    "to create it, or re-enter the Customize flow."
                )
                return
            # Same selection-building logic as _write_customized_bundle
            # so preview = reality.  We do NOT call the full launcher
            # here to avoid the side-effect of switching workflow_stage.
            try:
                _preview_write_bundle(
                    selected_agents=selected_agents,
                    scenario_base=scenario_base,
                    bundle_name=bundle_name,
                )
            except Exception as exc:
                st.error(f"Preview generation failed: {exc}")
                return
            players_path = (
                PROJECT_ROOT / "configs" / "CUSTOMIZED_SIMULATION"
                / bundle_name / "players.yml"
            )
            sim_path = (
                PROJECT_ROOT / "configs" / "CUSTOMIZED_SIMULATION"
                / bundle_name / "simulation.yml"
            )
            if sim_path.exists():
                st.markdown("**simulation.yml**")
                st.code(sim_path.read_text(encoding="utf-8"), language="yaml")
            if players_path.exists():
                st.markdown("**players.yml**")
                st.code(
                    players_path.read_text(encoding="utf-8"),
                    language="yaml",
                )
            else:
                st.warning(f"Expected players.yml at {players_path} but none found.")


def _preview_write_bundle(
    *,
    selected_agents: list[dict[str, Any]],
    scenario_base: str,
    bundle_name: str,
) -> None:
    """Regenerate the customized bundle files on disk without navigating.

    Extracted from :func:`_write_customized_bundle` and used by the
    Preview expander.  It intentionally does NOT flip
    ``workflow_stage`` or ``selected_scenario`` so the user stays on
    the Customize page.  Any exception bubbles up to the caller.
    """
    selections = _build_selections_from_session(
        selected_agents=selected_agents, persist_merge=True,
    )
    edited_rounds = st.session_state.get(f"variant_rounds_{scenario_base}")
    market_extras = st.session_state.get("customized_market_extras") or None
    apply_customized_modifications(
        bundle_name=bundle_name,
        selections=selections,
        scenario_name=scenario_base,
        project_root=PROJECT_ROOT,
        total_rounds=(
            int(edited_rounds) if edited_rounds is not None else None
        ),
        market_extras_override=market_extras,
    )


def _build_selections_from_session(
    *,
    selected_agents: list[dict[str, Any]],
    persist_merge: bool = True,
) -> list[CustomizedAgentSelection]:
    """Collect ``CustomizedAgentSelection`` list from the live roster.

    Iterates :func:`get_roster` in list order and emits one
    :class:`CustomizedAgentSelection` per :class:`RosterEntry`.  This
    means the same archetype can appear multiple times in the resulting
    list — the bundle writer's key-deduplication logic (see
    ``config_writer._render_agent_block``) handles that transparently by
    suffixing the second, third, … entry keys with ``_2``, ``_3`` etc.

    Widget sweep: for the currently active edit dialog (if any) the
    entry-scoped widget keys (``entry_{entry.id}_input_*`` and
    ``entry_{entry.id}_llm_*_<engine>``) are folded on top of the
    entry's stored ``params`` so unsaved dialog edits still flow into
    the preview / launch path.  When ``persist_merge`` is true, the
    merged params are written back into the entry so subsequent renders
    keep the same values.

    ``selected_agents`` is retained purely to source the ``display_name``
    for :class:`CustomizedAgentSelection`; the roster is the source of
    truth for which entries to emit.
    """
    display_by_type: dict[str, str] = {
        a["agent_type"]: a["display_name"] for a in selected_agents
    }

    roster = get_roster(st.session_state)
    selections: list[CustomizedAgentSelection] = []
    for entry in roster:
        agent_type = entry.agent_type
        engine = entry.engine or ALL_ENGINES[0]

        # ---- Engine override MUST resolve first ------------------------
        # If the user is currently editing an entry in the dialog and
        # has flipped the engine segmented control (e.g. Rule → LLM) but
        # not yet clicked Save, the live LLM widgets below are keyed
        # with the *new* engine suffix.  Reading the override up front
        # ensures the widget sweep looks for the right keys and does
        # not silently drop unsaved prompt edits.
        engine_wkey = f"entry_{entry.id}_engine"
        if engine_wkey in st.session_state:
            live_engine = st.session_state[engine_wkey]
            if live_engine:
                engine = str(live_engine)
                if persist_merge:
                    entry.engine = engine

        # ---- Sweep entry-scoped widget state (unsaved dialog edits) ----
        widget_snapshot: dict[str, Any] = {}
        param_prefix = f"entry_{entry.id}_input_"
        for wkey in list(st.session_state.keys()):
            if wkey.startswith(param_prefix):
                symbol = wkey[len(param_prefix):]
                widget_snapshot[symbol] = st.session_state[wkey]

        _llm_widget_map = {
            f"entry_{entry.id}_llm_lm_{engine}": "__llm_lm_name__",
            f"entry_{entry.id}_llm_temp_{engine}": "__llm_temperature__",
            f"entry_{entry.id}_llm_tokens_{engine}": "__llm_max_tokens__",
            f"entry_{entry.id}_llm_sysprompt_{engine}": "__llm_system_prompt__",
            f"entry_{entry.id}_llm_userprompt_{engine}": "__llm_user_prompt__",
        }
        for wkey, sentinel in _llm_widget_map.items():
            if wkey in st.session_state:
                widget_snapshot[sentinel] = st.session_state[wkey]

        # ---- Merge with entry-persisted params (widgets win ties) -----
        merged_params = dict(entry.params)
        merged_params.update(widget_snapshot)

        if persist_merge and widget_snapshot:
            # Write the merged params back so the next render sees the
            # same values (idempotent).
            entry.params = dict(merged_params)

        # ---- Optional instance-count widget override (spinner) --------
        ninst_wkey = f"entry_{entry.id}_ninst"
        ninst = int(entry.num_instances or 1)
        if ninst_wkey in st.session_state:
            try:
                ninst = int(st.session_state[ninst_wkey] or 1)
            except (TypeError, ValueError):
                ninst = int(entry.num_instances or 1)
        if ninst < 1:
            ninst = 1
        if persist_merge:
            entry.num_instances = ninst

        # Prefer the label from the widget when the dialog is open so
        # unsaved label edits still flow through to the preview.
        label_wkey = f"entry_{entry.id}_label"
        label = entry.label
        if label_wkey in st.session_state:
            raw_label = st.session_state[label_wkey]
            label = None if raw_label in (None, "") else str(raw_label)

        display_name = display_by_type.get(agent_type, agent_type)
        if label:
            display_name = f"{display_name} · {label}"

        selections.append(
            CustomizedAgentSelection(
                archetype=agent_type,
                display_name=display_name,
                engine=engine,
                params=dict(merged_params),
                num_instances=ninst,
            )
        )
    return selections


def _write_customized_bundle(
    *,
    selected_agents: list[dict[str, Any]],
    scenario_base: str,
) -> str | None:
    """Apply user's customization and launch from Customized-agents/.

    Returns the new scenario key (e.g.
    ``CUSTOMIZED_SIMULATION/MyProject-Scenario-abc12345/Customized-agents``)
    or ``None`` on failure. The Customized-agents/ subfolder is created
    lazily by apply_customized_modifications if it doesn't exist yet.
    """
    # Read bundle name from session state (set when entering Customize flow).
    bundle_name = st.session_state.get("customized_bundle_name", "")
    if not bundle_name:
        # Fallback: compute the bundle name from session state.
        project_slug = st.session_state.get("project_slug", "project")
        project_id = st.session_state.get("project_id", "0000")
        bundle_name = compose_bundle_name(
            project_slug, project_id, scenario_base, current_team()
        )
        st.session_state["customized_bundle_name"] = bundle_name

    roster_archetypes = [a["agent_type"] for a in selected_agents]
    compatible, reasons = is_scenario_compatible(scenario_base, roster_archetypes)
    if not compatible:
        st.error(
            "This scenario is not compatible with the current roster:\n\n"
            + "\n".join(f"- {r}" for r in reasons)
        )
        return None

    selections = _build_selections_from_session(
        selected_agents=selected_agents, persist_merge=True,
    )

    try:
        # Carry any user-adjusted round count from the variant_choice page
        # into the generated bundle (None => keep the shipped count).
        edited_rounds = st.session_state.get(f"variant_rounds_{scenario_base}")
        # Carry market parameter overrides from the Market Parameters editor.
        market_extras = st.session_state.get("customized_market_extras") or None
        result = apply_customized_modifications(
            bundle_name=bundle_name,
            selections=selections,
            scenario_name=scenario_base,
            project_root=PROJECT_ROOT,
            total_rounds=(
                int(edited_rounds) if edited_rounds is not None else None
            ),
            market_extras_override=market_extras,
        )
    except Exception as exc:
        st.error(f"Failed to materialise customized bundle: {exc}")
        return None

    st.session_state.customized_dir_id = result.customized_id
    st.toast(
        f"Customized bundle written: {result.customized_id} "
        f"(scenario {scenario_base})",
        icon="\u2728",
    )
    return f"CUSTOMIZED_SIMULATION/{result.customized_id}/Customized-agents"


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
            # The legacy flat ``selected_market_agents`` list is only a
            # sidebar-chip cache; the authoritative source of truth for
            # Stage 2 is the roster (``get_roster``).  We MUST clear the
            # cache before jumping into Customize, otherwise the one-time
            # legacy-flat-selection migration in ``render_customize``
            # (lines ~3491-3540) fires again on top of an already-populated
            # roster and double-counts every previously selected agent.
            st.session_state["selected_market_agents"] = []
            st.session_state.workflow_stage = "customize"
            st.session_state.current_page = "Simulation"
            st.rerun()


# ---------------------------------------------------------------------------
# Public alias (used by app.py)
# ---------------------------------------------------------------------------
render_scenario_setup = render_entry_choice
