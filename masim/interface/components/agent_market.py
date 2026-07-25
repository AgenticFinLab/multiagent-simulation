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
    get_market_archetype,
    get_market_description,
    get_market_icon_path,
    get_market_type,
    get_phenomenon_description,
    get_scenario_info,
    get_topology_info,
    scenario_display_name,
)
from ..customized import (
    CustomizedAgentSelection,
    RosterEntry,
    add_entry,
    apply_customized_modifications,
    apply_default_bundle_overrides,
    clear_roster,
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
    restore_state_to_session,
    save_state_from_session,
    scenario_market_features,
    set_roster,
    total_instances,
    unique_agent_types,
    update_entry,
    write_customized_bundle,
    write_default_scenario_bundle,
)
from ..customized.handbook_params import ParamSpec


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
    """Render the Default-mode market + agent parameter editor.

    Shows one expander per top-level block in ``configs/<base>/Rule/players.yml``
    (market coordinator first, then every investor).  Each block exposes
    its ``extras`` fields as ``st.number_input`` widgets (numeric) or
    ``st.text_input`` widgets (strings).  Edits are persisted under
    ``st.session_state[default_extras_<base>][<block_key>][<field>]``.

    When the user picks a Default engine, ``_launch_default_variant``
    checks whether *anything* under that session key is non-empty and,
    if so, materialises a rounds/params-adjusted bundle via
    :func:`write_default_scenario_bundle`.

    Silently no-ops if the scenario has no shipped ``Rule/players.yml``
    (e.g. rare LLM-only scenarios) — Default launch still works, users
    simply cannot tweak parameters without the reference variant.
    """
    players = extract_default_players(
        scenario_name=scenario_base, variant="Rule", project_root=PROJECT_ROOT
    )
    if not players:
        return

    session_key = _default_extras_session_key(scenario_base)
    edits: dict[str, dict[str, Any]] = st.session_state.setdefault(
        session_key, {}
    )

    with st.expander(
        "Advanced parameters — market & agent extras", expanded=False
    ):
        st.caption(
            "Fine-tune the shipped roster before launching.  Any edit "
            "here produces a reproducible copy under "
            "`configs/CUSTOMIZED_SIMULATION/Default-…/` — the shipped "
            "YAML is never mutated."
        )
        if st.button(
            "Reset to shipped defaults",
            key=f"default_extras_reset_{scenario_base}",
            help="Discard all edits below and relaunch with the shipped values.",
        ):
            st.session_state.pop(session_key, None)
            # Clear each per-widget session slot too so the next rerun
            # reflects the reset. Widget keys follow the naming below.
            for block_key, block_info in players.items():
                for extras_key in (block_info.get("extras") or {}):
                    st.session_state.pop(
                        f"defx_{scenario_base}_{block_key}_{extras_key}",
                        None,
                    )
            st.rerun()

        for block_key, block_info in players.items():
            extras = block_info.get("extras") or {}
            if not extras:
                continue
            is_market = block_key == next(iter(players))
            override_slot = (
                edits.setdefault("__market__", {})
                if is_market
                else edits.setdefault(block_key, {})
            )
            role_tag = (
                "market coordinator"
                if is_market
                else f"{block_info.get('num_instances', 1)} instance"
                + ("s" if int(block_info.get("num_instances", 1)) > 1 else "")
            )
            label = f"**{block_info.get('name') or block_key}**  · {role_tag}"
            st.markdown(label)

            cols_per_row = 3
            keys = list(extras.keys())
            for row_start in range(0, len(keys), cols_per_row):
                row_keys = keys[row_start : row_start + cols_per_row]
                cols = st.columns(len(row_keys))
                for col, extras_key in zip(cols, row_keys):
                    with col:
                        default_val = extras[extras_key]
                        current_val = override_slot.get(extras_key, default_val)
                        widget_key = (
                            f"defx_{scenario_base}_{block_key}_{extras_key}"
                        )
                        pretty = extras_key.replace("_", " ").title()
                        # bool subclasses int -> check bool first.
                        if isinstance(default_val, bool):
                            new_val = st.checkbox(
                                pretty,
                                value=bool(current_val),
                                key=widget_key,
                                help=f"Default: {default_val}",
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
                            )
                        else:
                            new_val = st.text_input(
                                pretty,
                                value=str(current_val),
                                key=widget_key,
                                help=f"Default: {default_val!r}",
                            )
                        # Only persist a slot when the value actually
                        # deviates from the shipped default — keeps the
                        # override dict tight and lets the launcher
                        # short-circuit to zero-copy when nothing changed.
                        coerced = _coerce_extras_value(default_val, new_val)
                        if coerced != default_val:
                            override_slot[extras_key] = coerced
                        else:
                            override_slot.pop(extras_key, None)

            # Prune empty per-block dicts so the launcher can detect a
            # fully-reset override state with a truthiness check.
            if not override_slot:
                if is_market:
                    edits.pop("__market__", None)
                else:
                    edits.pop(block_key, None)

        # Persist back the pruned dict.
        st.session_state[session_key] = edits


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
        _rounds_key = f"variant_rounds_{selected_base}"
        _rounds_default = shipped_rounds if shipped_rounds > 0 else 1
        if is_experience:
            # Experience mode: read-only display, no editing allowed.
            st.metric("Rounds", str(_rounds_default))
            st.session_state[_rounds_key] = _rounds_default
        else:
            # Editable rounds — user can shrink for a quick preview or extend
            # to observe long-run dynamics.  The value is persisted under
            # ``variant_rounds_<base>`` and consumed by ``_launch_default_variant``
            # (Default) and ``_write_customized_bundle`` (Customize). Leaving
            # the value untouched preserves the shipped default (zero-copy
            # launch path). Values <1 are clamped to 1 by the widget.
            _rounds_now = int(st.session_state.get(_rounds_key, _rounds_default))
            edited_rounds = st.number_input(
                "Rounds",
                min_value=1,
                max_value=100000,
                value=_rounds_now,
                step=1,
                key=f"widget_{_rounds_key}",
                help=(
                    f"Number of simulation rounds. Shipped default: "
                    f"{shipped_rounds if shipped_rounds > 0 else 'n/a'}. "
                    "Change to produce a reproducible copy under "
                    "configs/CUSTOMIZED_SIMULATION/."
                ),
            )
            st.session_state[_rounds_key] = int(edited_rounds)
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
                with col:
                    if st.button(
                        VARIANT_DISPLAY.get(variant, variant),
                        key=f"stage2_default_{variant}",
                        width="stretch",
                        disabled=_is_disabled,
                        help=(
                            "暂时禁用 (temporarily disabled)"
                            if _is_disabled
                            else (
                                f"Run {scenario_display_name(selected_base)} "
                                f"with the {variant} decision engine."
                            )
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
                    with col:
                        if st.button(
                            VARIANT_DISPLAY.get(variant, variant),
                            key=f"stage2_default_{variant}",
                            width="stretch",
                            disabled=_is_disabled,
                            help=(
                                "暂时禁用 (temporarily disabled)"
                                if _is_disabled
                                else (
                                    f"Configure {scenario_display_name(selected_base)} "
                                    f"with the {variant} engine, then launch."
                                )
                            ),
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
                    bundle_name = f"{project_slug}-{project_id}-{selected_base}"
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
    bundle_name = f"{project_slug}-{project_id}-{scenario_base}"

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

    Zero-copy fast path: if the user left both the round count and the
    market/agent extras untouched, the shipped ``configs/<Scenario>/<Variant>/``
    directory is launched directly.  Any deviation — an edited round count,
    a market extras change, or a per-agent extras change — triggers
    :func:`write_default_scenario_bundle` to produce a reproducible copy
    under ``configs/CUSTOMIZED_SIMULATION/Default-<Scenario>-<Variant>-rN/``
    with the requested overrides baked in.  The shipped YAML is never
    mutated.
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
    # parameter editor (``_render_default_param_editor``).  Structure:
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

    launch_key = scenario_key
    customized_id = None
    if rounds_changed or extras_changed:
        target_rounds = (
            int(edited_rounds)
            if edited_rounds is not None
            else shipped_rounds
        )
        if target_rounds < 1:
            target_rounds = shipped_rounds if shipped_rounds > 0 else 1
        try:
            result = write_default_scenario_bundle(
                scenario_name=base,
                variant=variant,
                total_rounds=target_rounds,
                project_root=PROJECT_ROOT,
                market_extras_override=market_over or None,
                agent_extras_overrides=agent_over or None,
            )
            launch_key = f"CUSTOMIZED_SIMULATION/{result.customized_id}"
            customized_id = result.customized_id
        except (FileNotFoundError, ValueError) as exc:
            st.error(f"Could not apply the adjusted parameters: {exc}")
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
    bundle_name = f"{project_slug}-{project_id}-{base}"

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
        )
        st.session_state[_rounds_key] = int(edited_rounds)

    st.divider()

    # ── Load player data ──────────────────────────────────────────────────
    players = extract_default_players(
        scenario_name=base, variant=variant, project_root=PROJECT_ROOT
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
                    )
        st.divider()

    # ── Confirm & Launch button ───────────────────────────────────────────
    _render_launch_button(scenario_key)


def _resolve_prompt_text(module_ref: str) -> str:
    """Resolve a 'module.path:VARIABLE' reference to its string value.

    Used to load the actual prompt text from e.g.
    'examples.AnchoringEffect.LLM.prompts:LLM_ANCHORED_TRADER_SYS'.
    Returns the resolved string, or the raw reference if import fails.
    """
    if ":" not in module_ref:
        return module_ref
    module_path, var_name = module_ref.rsplit(":", 1)
    try:
        import importlib
        mod = importlib.import_module(module_path)
        value = getattr(mod, var_name, None)
        if isinstance(value, str):
            return value
    except Exception:
        pass
    return module_ref


def _extract_persona_section(full_prompt: str) -> str:
    """Extract only the persona part from a full system prompt.

    Strips everything from the TRADING_CONSTRAINTS / ANALYSIS_DECISION_TAG
    section onward, since those are format instructions that should be locked.
    The persona is the creative content the user may want to edit.
    """
    # Known markers that signal the start of locked format instructions.
    _MARKERS = [
        "TRADING CONSTRAINTS:",
        "== FORMAT ==",
        "Respond with your thinking in",
        "Your response MUST use the following structure",
        "The decision JSON must follow this exact format",
    ]
    text = full_prompt
    # Find the earliest marker position
    cut_pos = len(text)
    for marker in _MARKERS:
        idx = text.find(marker)
        if idx != -1 and idx < cut_pos:
            cut_pos = idx
    result = text[:cut_pos].rstrip()
    # Also strip trailing blank lines left by the cut
    return result.rstrip("\n") + "\n"


def _render_default_agent_card(
    *,
    base: str,
    variant: str,
    block_key: str,
    block_info: dict[str, Any],
    edits: dict[str, dict[str, Any]],
    is_llm_variant: bool,
) -> None:
    """Render one agent card in the Default config grid (Customized-style).

    Shows: icon image → agent name → edited badge → Edit button (opens dialog).
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

    # --- Edited indicator ---
    has_edits = (
        bool(edits.get(block_key))
        or bool(edits.get("__llm__", {}).get(block_key))
        or st.session_state.get(f"dc_edited_{block_key}", False)
    )
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
) -> None:
    """Dialog overlay for editing a Default-config agent's parameters."""
    display_name = block_info.get("name") or block_key
    extras = block_info.get("extras") or {}

    st.subheader(display_name)

    # ── Parameters (extras) ───────────────────────────────────────────
    if extras:
        st.markdown("**Parameters**")
        override_slot = edits.setdefault(block_key, {})
        _render_extras_grid(
            extras=extras,
            override_slot=override_slot,
            key_prefix=f"dc_{base}_{block_key}",
        )
        if not override_slot:
            edits.pop(block_key, None)
        st.divider()

    # ── LLM Prompt & Model (only for LLM/RuleLLM/Rag engines) ────────
    if is_llm_variant:
        llm_cfg = block_info.get("llm")
        if llm_cfg:
            st.markdown("**Persona Prompt**")
            st.caption(
                "Edit the agent's persona below. The output format instruction "
                "is appended automatically — you only need to adjust the "
                "persona description."
            )

            llm_edits: dict[str, dict[str, Any]] = edits.setdefault("__llm__", {})
            agent_llm_edits = llm_edits.setdefault(block_key, {})

            # Resolve the current system prompt text
            sys_ref = llm_cfg.get("sys_message", "")
            prompt_text = agent_llm_edits.get("persona_prompt", "")
            if not prompt_text and sys_ref:
                prompt_text = _resolve_prompt_text(sys_ref)

            # Strip the format tail so users only see persona
            persona_only = _extract_persona_section(prompt_text)

            edited_prompt = st.text_area(
                "Persona Prompt",
                value=agent_llm_edits.get("persona_prompt", persona_only),
                height=220,
                key=f"dc_llm_prompt_{base}_{block_key}",
                help="Edit the agent's persona content.",
                label_visibility="collapsed",
            )
            if edited_prompt.strip() != persona_only.strip():
                agent_llm_edits["persona_prompt"] = edited_prompt.strip()
            else:
                agent_llm_edits.pop("persona_prompt", None)

            # Locked format display
            st.info(
                "**Output format** (locked — appended automatically):\n\n"
                "```\n"
                '<analysis>...</analysis><decision>JSON</decision>\n'
                "JSON: {action, bid_price, quantity, reasoning}\n"
                "```",
                icon="\U0001f512",
            )

            st.divider()

            # Model & Generation parameters
            st.markdown("**Model & Generation**")
            gen_cfg = llm_cfg.get("generation_config") or {}
            pcol1, pcol2 = st.columns(2)
            with pcol1:
                current_temp = float(
                    agent_llm_edits.get(
                        "temperature", gen_cfg.get("temperature", 0.7)
                    )
                )
                new_temp = st.slider(
                    "Temperature",
                    min_value=0.0,
                    max_value=2.0,
                    value=current_temp,
                    step=0.05,
                    key=f"dc_llm_temp_{base}_{block_key}",
                )
                if abs(new_temp - float(gen_cfg.get("temperature", 0.7))) > 0.01:
                    agent_llm_edits["temperature"] = round(new_temp, 2)
                else:
                    agent_llm_edits.pop("temperature", None)
            with pcol2:
                current_tokens = int(
                    agent_llm_edits.get(
                        "max_tokens", gen_cfg.get("max_tokens", 512)
                    )
                )
                new_tokens = st.number_input(
                    "Max Tokens",
                    min_value=64,
                    max_value=4096,
                    value=current_tokens,
                    step=64,
                    key=f"dc_llm_tokens_{base}_{block_key}",
                )
                if int(new_tokens) != int(gen_cfg.get("max_tokens", 512)):
                    agent_llm_edits["max_tokens"] = int(new_tokens)
                else:
                    agent_llm_edits.pop("max_tokens", None)

            current_model = agent_llm_edits.get(
                "lm_name", llm_cfg.get("lm_name", "")
            )
            new_model = st.text_input(
                "Model Name",
                value=current_model,
                key=f"dc_llm_model_{base}_{block_key}",
                help="LLM endpoint identifier (e.g. ark/doubao-seed-2-0-mini-260428).",
            )
            if new_model.strip() != llm_cfg.get("lm_name", ""):
                agent_llm_edits["lm_name"] = new_model.strip()
            else:
                agent_llm_edits.pop("lm_name", None)

            # Prune empty per-agent dicts
            if not agent_llm_edits:
                llm_edits.pop(block_key, None)
            if not llm_edits:
                edits.pop("__llm__", None)

    # ── Save button ────────────────────────────────────────────────────
    if st.button("保存", key="dc_edit_save", type="primary", use_container_width=True):
        st.session_state[f"dc_edited_{block_key}"] = True
        st.rerun()


def _render_extras_grid(
    *,
    extras: dict[str, Any],
    override_slot: dict[str, Any],
    key_prefix: str,
) -> None:
    """Render a responsive grid of parameter widgets for an extras dict."""
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
                    )
                else:
                    new_val = st.text_input(
                        pretty,
                        value=str(current_val),
                        key=widget_key,
                        help=f"Default: {default_val!r}",
                    )

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
    """Apply parameter edits to the bundle and enter the workspace."""
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
    llm_over = default_extras.get("__llm__") or {}
    agent_over = {
        k: v for k, v in default_extras.items()
        if k not in ("__market__", "__llm__") and v
    }

    # Write edits into the bundle's config files
    try:
        apply_default_bundle_overrides(
            config_dir=bundle.config_dir,
            total_rounds=edited_rounds,
            market_extras_override=market_over or None,
            agent_extras_overrides=agent_over or None,
        )
    except Exception as exc:
        st.error(f"Failed to apply parameter changes: {exc}")
        return

    # Apply LLM overrides (prompts + generation params) if any
    if llm_over:
        try:
            _apply_llm_overrides_to_bundle(
                config_dir=bundle.config_dir,
                example_dir=bundle.example_dir,
                llm_edits=llm_over,
                scenario_name=base,
                variant=variant,
            )
        except Exception as exc:
            st.error(f"Failed to apply LLM overrides: {exc}")
            return

    # Transition to workspace — launch from the bundle
    launch_key = f"CUSTOMIZED_SIMULATION/{bundle.customized_id}/Default/{variant}"
    st.session_state.selected_scenario = launch_key
    st.session_state.selected_market_agents = []
    st.session_state.workflow_stage = "workspace"
    st.session_state.current_page = "Simulation"
    st.session_state.customized_dir_id = bundle.customized_id
    st.rerun()


def _apply_llm_overrides_to_bundle(
    *,
    config_dir: "Path",
    example_dir: "Path",
    llm_edits: dict[str, dict[str, Any]],
    scenario_name: str,
    variant: str,
) -> None:
    """Apply LLM prompt/param edits to the bundle's players.yml and prompts.py.

    For each agent in llm_edits:
      - temperature / max_tokens / lm_name → patched in-place in players.yml
      - persona_prompt → written to a custom prompts.py that the players.yml
        sys_message reference will point to (rewired).

    The output format instruction is automatically appended to each edited
    persona so the model output stays parseable.
    """
    import re as _re
    from pathlib import Path

    players_path = config_dir / "players.yml"
    if not players_path.exists():
        return

    players_text = players_path.read_text(encoding="utf-8")
    prompts_written: dict[str, str] = {}  # var_name -> full prompt text

    for block_key, agent_edits in llm_edits.items():
        if not agent_edits:
            continue

        # --- Patch generation_config fields in players.yml ---
        if "temperature" in agent_edits:
            # Replace temperature: <old> for this agent block
            players_text = _patch_llm_yaml_field(
                players_text, block_key, "temperature",
                str(agent_edits["temperature"]),
            )
        if "max_tokens" in agent_edits:
            players_text = _patch_llm_yaml_field(
                players_text, block_key, "max_tokens",
                str(agent_edits["max_tokens"]),
            )
        if "lm_name" in agent_edits:
            players_text = _patch_llm_yaml_field(
                players_text, block_key, "lm_name",
                f'"{agent_edits["lm_name"]}"',
            )

        # --- Build custom prompt if persona was edited ---
        if "persona_prompt" in agent_edits:
            # Build a variable name from block_key
            var_name = f"CUSTOM_{block_key.upper()}_SYS"
            # Compose full prompt: edited persona + locked format tail
            from masim.format.base_prompts import (
                ANALYSIS_DECISION_TAG,
                TRADING_CONSTRAINTS,
            )
            from masim.format.order_prompts import DECISION_FORMAT_INSTRUCTION

            full_prompt = (
                agent_edits["persona_prompt"].rstrip()
                + "\n\n"
                + TRADING_CONSTRAINTS
                + "\n\n"
                + ANALYSIS_DECISION_TAG
                + "\n"
                + DECISION_FORMAT_INSTRUCTION
                + "\n"
            )
            prompts_written[var_name] = full_prompt

            # Rewrite sys_message reference in players.yml to point to
            # the custom prompts module
            bundle_module = _bundle_prompts_module_path(config_dir)
            new_ref = f"{bundle_module}:{var_name}"
            players_text = _patch_llm_yaml_field(
                players_text, block_key, "sys_message",
                f'"{new_ref}"',
            )

    # Write back players.yml
    players_path.write_text(players_text, encoding="utf-8")

    # Write custom prompts.py if any personas were edited
    if prompts_written:
        prompts_py_path = example_dir / "prompts.py"
        # Build the module file
        lines = [
            '"""Custom prompts generated by Default config editor."""\n\n',
        ]
        for var_name, prompt_text in prompts_written.items():
            # Use triple-quoted string
            escaped = prompt_text.replace('\\', '\\\\').replace('"""', '\\"\\"\\"')
            lines.append(f'{var_name} = """{escaped}"""\n\n')
        prompts_py_path.parent.mkdir(parents=True, exist_ok=True)
        prompts_py_path.write_text("".join(lines), encoding="utf-8")
        # Ensure __init__.py exists for import
        init_path = example_dir / "__init__.py"
        if not init_path.exists():
            init_path.write_text("", encoding="utf-8")


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


def _bundle_prompts_module_path(config_dir: "Path") -> str:
    """Derive the Python import path for the bundle's custom prompts.py.

    Given config_dir like ``.../configs/CUSTOMIZED_SIMULATION/{bundle}/Default/{variant}/``,
    the corresponding example module is
    ``examples.CUSTOMIZED_SIMULATION.{bundle}.Default.{variant}.prompts``.
    """
    from pathlib import Path
    parts = Path(config_dir).parts
    # Find 'CUSTOMIZED_SIMULATION' in parts and take everything after
    try:
        idx = parts.index("CUSTOMIZED_SIMULATION")
    except ValueError:
        return "prompts"
    module_parts = ["examples", "CUSTOMIZED_SIMULATION"] + list(parts[idx + 1:])
    return ".".join(module_parts) + ".prompts"


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
    all_engines = [e for e in ALL_ENGINES if e not in _DISABLED_ENGINES]
    specs = _load_param_specs(agent)

    st.markdown('<div class="market-kicker">Edit roster entry</div>', unsafe_allow_html=True)
    st.subheader(agent["display_name"])
    header_bits = [f"`{agent_type}`", f"Entry ID `{entry_id}`"]
    st.caption(" · ".join(header_bits))

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
    )

    # ---- Engine selector ------------------------------------------------
    engine_key = f"entry_{entry_id}_engine"
    if engine_key not in st.session_state:
        default_engine = entry.engine if entry.engine in all_engines else all_engines[0]
        st.session_state[engine_key] = default_engine
    elif st.session_state[engine_key] not in all_engines:
        st.session_state[engine_key] = all_engines[0]

    st.segmented_control(
        "Decision engine",
        options=all_engines,
        format_func=lambda v: VARIANT_DISPLAY.get(v, v),
        key=engine_key,
        help=(
            "Choose the decision-making engine. Rule = deterministic logic; "
            "LLM = persona-driven prompt; RuleLLM = hybrid."
        ),
    )
    if _DISABLED_ENGINES:
        st.caption(
            f"{'、'.join(VARIANT_DISPLAY.get(e, e) for e in sorted(_DISABLED_ENGINES))}"
            " 暂时禁用"
        )
    engine = st.session_state[engine_key]

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
        )

    # ---- Action buttons -------------------------------------------------
    st.divider()
    btn_save, btn_reset, btn_del, btn_close = st.columns([3, 1, 1, 1])
    with btn_save:
        if st.button(
            "Save changes",
            type="primary",
            width="stretch",
            key=f"entry_{entry_id}_save",
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
                "Clear this entry's parameter overrides and revert to "
                "handbook defaults. Engine and instance count are kept."
            ),
        ):
            update_entry(roster, entry_id, params={})
            # Also drop every entry-scoped widget so their defaults
            # repopulate from the handbook on the next open.
            for wkey in list(st.session_state.keys()):
                if wkey.startswith(f"entry_{entry_id}_input_") or (
                    wkey.startswith(f"entry_{entry_id}_llm_")
                ):
                    del st.session_state[wkey]
            save_state_from_session(project_root=PROJECT_ROOT)
            st.toast("Parameters reset", icon="↺")
            st.rerun()
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
) -> Any:
    """Render one editable widget for a parameter spec, scoped to an entry.

    Widget key format: ``entry_{entry_id}_input_{symbol}`` — unique across
    the app so two entries of the same archetype never share state.
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
        )

    if spec.kind == "int":
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

    return st.text_input(
        label_main,
        value=str(initial) if initial is not None else "",
        key=widget_key,
        help=help_text,
    )


def _render_entry_llm_extras(
    *,
    agent: dict[str, Any],
    entry_id: str,
    engine: str,
    persisted: dict[str, Any],
    edited: dict[str, Any],
) -> None:
    """Render LLM hyperparameters and editable prompt textareas for an entry.

    Widget keys are ``entry_{entry_id}_llm_{field}_{engine}`` where
    ``field`` is one of ``lm`` / ``temp`` / ``tokens`` / ``sysprompt`` /
    ``userprompt``.  Values are written into ``edited`` under the
    reserved ``__llm_*__`` sentinels so they round-trip with the rest of
    the entry's params on the next Save.

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
    """
    agent_type = agent["agent_type"]
    roster = get_roster(st.session_state)
    entries_here = entries_for_type(roster, agent_type)
    entry_count = len(entries_here)
    instance_count = sum(int(e.num_instances or 1) for e in entries_here)
    selected = entry_count > 0

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

    # --- Agent name: clickable text button -> opens profile dialog ---
    if st.button(
        agent["display_name"],
        key=f"market_profile_{agent_type}",
        type="tertiary",
        help=agent.get("intro", "View this agent's design profile"),
    ):
        _show_catalog_agent_profile_dialog(agent)

    # --- Primary action row: + Add (quick) and Configure… (opens dialog)
    if st.button(
        "+ Add",
        key=f"market_quick_add_{agent_type}",
        type="primary",
        width="stretch",
        help=(
            "Append a new roster entry for this agent with default "
            "settings (Rule engine, 1 instance). You can add the same "
            "agent multiple times with different configurations."
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
        help=(
            "Create a new roster entry and immediately open its editor "
            "to pick engine, adjust parameters, and (for LLM engines) "
            "edit the prompt before committing."
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
        st.session_state.workflow_stage = "scenario_setup"
        st.rerun()

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
            disabled=not selected or compat_blocker is not None,
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
    """Render the *My Roster* list: one row per :class:`RosterEntry`.

    This is the authoritative place for managing entries. Each row shows
    a small icon, the archetype's display name, the optional label, the
    engine chip, the instance count, and three actions:

    * **Edit** — opens the entry's edit dialog (:func:`_show_entry_edit_dialog`).
    * **Duplicate** — inserts a clone immediately below with a fresh id
      (label suffixed with "(copy)" when present).
    * **× Remove** — deletes just this row without touching the rest.

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
    # Iterate over a snapshot so remove/duplicate reruns don't fight our loop.
    for pos, entry in enumerate(list(roster), start=1):
        agent = by_type.get(entry.agent_type)
        if agent is None:
            # Roster references an archetype no longer in the catalog —
            # surface a stub with just remove available.
            with st.container(border=True):
                col_info, col_del = st.columns([6, 1])
                with col_info:
                    st.markdown(
                        f"**{html.escape(entry.agent_type)}** "
                        f"<span style='color:#c1272d'>· catalog entry missing</span>",
                        unsafe_allow_html=True,
                    )
                    st.caption(f"Entry `{entry.id}` · engine {entry.engine}")
                with col_del:
                    if st.button(
                        "× Remove",
                        key=f"roster_del_orphan_{entry.id}",
                        type="tertiary",
                    ):
                        remove_entry(roster, entry.id)
                        save_state_from_session(project_root=PROJECT_ROOT)
                        st.rerun()
            continue

        with st.container(border=True):
            icon_col, main_col, action_col = st.columns([1, 5, 3])
            with icon_col:
                img_path = Path(agent.get("image_file", ""))
                if img_path.exists():
                    st.image(str(img_path), use_container_width=True)
                else:
                    st.markdown(
                        "<div style='width:100%;aspect-ratio:1/1;"
                        "border-radius:6px;background:#e8f0fb;"
                        "display:flex;align-items:center;justify-content:center;"
                        "color:#2a5fa6;font-weight:700;'>"
                        f"{agent['display_name'][0]}</div>",
                        unsafe_allow_html=True,
                    )

            with main_col:
                # Header line: display name (+ optional label) + positional
                # badge so the user can spot which entry they're editing.
                label_html = ""
                if entry.label:
                    label_html = (
                        "<span style='margin-left:8px;padding:2px 8px;"
                        "border-radius:10px;background:#eef4ff;color:#264d80;"
                        "font-size:0.72rem;font-weight:600;'>"
                        f"{html.escape(entry.label)}</span>"
                    )
                st.markdown(
                    f"<div style='font-size:1.02rem;font-weight:600;'>"
                    f"{html.escape(agent['display_name'])}"
                    f"<span style='margin-left:8px;color:#6c757d;"
                    f"font-size:0.75rem;font-weight:500;'>#{pos}</span>"
                    f"{label_html}</div>",
                    unsafe_allow_html=True,
                )
                # Second line: engine chip + instance count + edit summary.
                param_count = sum(
                    1 for k in entry.params if not k.startswith("__llm_")
                )
                llm_edited = any(
                    k.startswith("__llm_") for k in entry.params
                )
                summary_bits = [
                    f"<span style='padding:1px 8px;border-radius:10px;"
                    f"background:#f0f4fa;color:#2a5fa6;font-size:0.72rem;"
                    f"font-weight:600;'>{html.escape(entry.engine)}</span>",
                    f"<span style='color:#6c757d;font-size:0.78rem;'>"
                    f"×{entry.num_instances} instances</span>",
                ]
                if param_count:
                    summary_bits.append(
                        f"<span style='color:#6c757d;font-size:0.78rem;'>"
                        f"{param_count} param{'s' if param_count > 1 else ''} edited</span>"
                    )
                if llm_edited:
                    summary_bits.append(
                        "<span style='color:#6c757d;font-size:0.78rem;'>"
                        "LLM overrides</span>"
                    )
                st.markdown(
                    "<div style='margin-top:2px;display:flex;gap:10px;"
                    "align-items:center;flex-wrap:wrap;'>"
                    + "".join(summary_bits)
                    + "</div>",
                    unsafe_allow_html=True,
                )
                st.caption(f"Entry id: `{entry.id}`")

            with action_col:
                edit_col, dup_col, del_col = st.columns(3)
                with edit_col:
                    if st.button(
                        "Edit",
                        key=f"roster_edit_{entry.id}",
                        width="stretch",
                        help="Open the edit dialog for this entry only.",
                    ):
                        _show_entry_edit_dialog(agent, entry.id)
                with dup_col:
                    if st.button(
                        "Duplicate",
                        key=f"roster_dup_{entry.id}",
                        width="stretch",
                        help=(
                            "Insert a copy of this entry immediately below. "
                            "Handy for tweaking a variant without losing the "
                            "original."
                        ),
                    ):
                        clone = duplicate_entry(roster, entry.id)
                        # Copy widget state so the new entry opens with the
                        # same values pre-populated on first edit.
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
                with del_col:
                    if st.button(
                        "× Remove",
                        key=f"roster_del_{entry.id}",
                        type="tertiary",
                        width="stretch",
                        help="Delete this entry without touching the others.",
                    ):
                        remove_entry(roster, entry.id)
                        # Drop scoped widget state so nothing lingers for
                        # future entries that happen to reuse the id space.
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
        bundle_name = f"{project_slug}-{project_id}-{scenario_base}"
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
            st.session_state.workflow_stage = "customize"
            st.session_state.current_page = "Simulation"
            st.rerun()


# ---------------------------------------------------------------------------
# Public alias (used by app.py)
# ---------------------------------------------------------------------------
render_scenario_setup = render_entry_choice
