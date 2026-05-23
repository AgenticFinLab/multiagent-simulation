#!/usr/bin/env python
"""Regression checks for scenario-specific example contracts."""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from masim.utils.config import load_config  # noqa: E402


def prompt_constants(path: Path) -> dict[str, str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    constants: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            if not isinstance(node.value.value, str):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    constants[target.id] = node.value.value
    return constants


class ScenarioContractTest(unittest.TestCase):
    def test_pending_api_personas_use_framework_proxy_storage_schema(self):
        rows = [
            ("SVBBankRun", "LLM"),
            ("SVBBankRun", "RuleLLM"),
            ("SVBBankRun", "Rag"),
            ("SunkCostFallacy", "LLM"),
            ("SunkCostFallacy", "RuleLLM"),
            ("SunkCostFallacy", "Rag"),
            ("TulipMania", "LLM"),
            ("TulipMania", "RuleLLM"),
            ("TulipMania", "Rag"),
        ]

        missing = []
        for scenario, mechanism in rows:
            cfg = load_config(str(ROOT / "configs" / scenario / mechanism / "simulation.yml"))
            for player_key, player in cfg["players"].items():
                storage = player.get("persona", {}).get("proxy", {}).get("storage", {})
                if not storage.get("record_path"):
                    missing.append(f"{scenario}__{mechanism}:{player_key}")

        self.assertEqual(
            missing,
            [],
            "PlayerPersona requires persona.proxy.storage.record_path; old "
            "proxy.record_path-only persona.yml files fail during setup.",
        )

    def test_dynamic_trading_prompts_request_fields_read_by_players(self):
        player_files = [
            ROOT / "examples" / "SorosPound" / "LLM" / "players.py",
            ROOT / "examples" / "SorosPound" / "RuleLLM" / "players.py",
            ROOT / "examples" / "SorosPound" / "Rag" / "players.py",
            ROOT / "examples" / "SouthSeaBubble" / "LLM" / "players.py",
            ROOT / "examples" / "SouthSeaBubble" / "RuleLLM" / "players.py",
            ROOT / "examples" / "SouthSeaBubble" / "Rag" / "players.py",
            ROOT / "examples" / "StatusQuoBias" / "LLM" / "players.py",
            ROOT / "examples" / "StatusQuoBias" / "RuleLLM" / "players.py",
            ROOT / "examples" / "StatusQuoBias" / "Rag" / "players.py",
        ]

        missing = []
        for path in player_files:
            text = path.read_text(encoding="utf-8")
            if "decision[\"reasoning\"]" in text or "decision.get(\"reasoning\"" in text:
                if '"reasoning"' not in text and "'reasoning'" not in text:
                    missing.append(f"{path.relative_to(ROOT)}:reasoning")
            consumes_bid_price = 'decision["bid_price"]' in text or "decision['bid_price']" in text
            if consumes_bid_price and "bid_price" not in text:
                missing.append(f"{path.relative_to(ROOT)}:bid_price")

        self.assertEqual(
            missing,
            [],
            "Dynamic user prompts that contain the final JSON instruction must "
            "not narrow the schema below fields consumed by the player.",
        )

    def test_current_market_quantity_schemas_use_quantity_parser(self):
        player_files = [
            ROOT / "examples" / "SorosPound" / "LLM" / "players.py",
            ROOT / "examples" / "SorosPound" / "RuleLLM" / "players.py",
            ROOT / "examples" / "SorosPound" / "Rag" / "players.py",
            ROOT / "examples" / "SouthSeaBubble" / "LLM" / "players.py",
            ROOT / "examples" / "SouthSeaBubble" / "RuleLLM" / "players.py",
            ROOT / "examples" / "SouthSeaBubble" / "Rag" / "players.py",
            ROOT / "examples" / "TulipMania" / "LLM" / "players.py",
            ROOT / "examples" / "TulipMania" / "RuleLLM" / "players.py",
            ROOT / "examples" / "TulipMania" / "Rag" / "players.py",
            ROOT / "examples" / "Volmageddon" / "LLM" / "players.py",
            ROOT / "examples" / "Volmageddon" / "RuleLLM" / "players.py",
            ROOT / "examples" / "Volmageddon" / "Rag" / "players.py",
        ]

        wrong_parser = []
        for path in player_files:
            text = path.read_text(encoding="utf-8")
            if "parse_llm_quantity_response_with_thinking" not in text:
                wrong_parser.append(f"{path.relative_to(ROOT)}:missing_quantity_parser")
            if "parse_llm_response_with_thinking" in text:
                wrong_parser.append(f"{path.relative_to(ROOT)}:canonical_parser")

        self.assertEqual(
            wrong_parser,
            [],
            "Current-market quantity schemas must not reuse the canonical "
            "bid_price parser; they intentionally do not request a price field.",
        )

    def test_api_parse_failure_paths_are_contract_safe(self):
        player_files = [
            ROOT / "examples" / "SorosPound" / "LLM" / "players.py",
            ROOT / "examples" / "SorosPound" / "RuleLLM" / "players.py",
            ROOT / "examples" / "SorosPound" / "Rag" / "players.py",
            ROOT / "examples" / "SouthSeaBubble" / "LLM" / "players.py",
            ROOT / "examples" / "SouthSeaBubble" / "RuleLLM" / "players.py",
            ROOT / "examples" / "SouthSeaBubble" / "Rag" / "players.py",
            ROOT / "examples" / "StatusQuoBias" / "LLM" / "players.py",
            ROOT / "examples" / "StatusQuoBias" / "RuleLLM" / "players.py",
            ROOT / "examples" / "StatusQuoBias" / "Rag" / "players.py",
        ]

        missing = []
        for path in player_files:
            text = path.read_text(encoding="utf-8")
            has_fallback = "fallback hold after retries" in text
            has_fail_fast = "failed after {max_retries} attempts" in text
            if has_fallback:
                if "decision[\"reasoning\"]" in text:
                    missing.append(f"{path.relative_to(ROOT)}:uses direct reasoning read")
                continue
            if has_fail_fast:
                if "fallback hold after retries" in text:
                    missing.append(f"{path.relative_to(ROOT)}:mixed fallback and fail-fast")
                continue
            missing.append(f"{path.relative_to(ROOT)}:no safe parse-failure path")

        self.assertEqual(
            missing,
            [],
            "Parse-failure handling must be contract-safe: either fallback orders "
            "carry all recorded fields, or the player fails fast after retries.",
        )

    def test_liquidity_sensitive_prompts_request_provides_liquidity(self):
        prompt_files = [
            ROOT / "examples" / "LiquidityDryup" / "LLM" / "prompts.py",
            ROOT / "examples" / "LiquidityDryup" / "RuleLLM" / "prompts.py",
            ROOT / "examples" / "LiquidityDryup" / "Rag" / "prompts.py",
            ROOT / "examples" / "MarketCrash" / "RuleLLM" / "prompts.py",
            ROOT / "examples" / "MarketCrash" / "Rag" / "prompts.py",
            ROOT / "examples" / "MomentumEffect" / "RuleLLM" / "prompts.py",
            ROOT / "examples" / "MomentumEffect" / "Rag" / "prompts.py",
        ]

        missing = []
        for path in prompt_files:
            for name, value in prompt_constants(path).items():
                if "decision must be valid JSON" not in value:
                    continue
                if "provides_liquidity" not in value:
                    missing.append(f"{path.relative_to(ROOT)}:{name}")

        self.assertEqual(
            missing,
            [],
            "Prompts for players that emit liquidity-sensitive orders must "
            "request the provides_liquidity field.",
        )

    def test_liquidity_sensitive_rag_players_default_optional_liquidity_flag(self):
        player_files = [
            ROOT / "examples" / "FlashCrash" / "Rag" / "players.py",
            ROOT / "examples" / "ReversalEffect" / "Rag" / "players.py",
            ROOT / "examples" / "VolatilityClustering" / "Rag" / "players.py",
        ]

        missing = []
        for path in player_files:
            text = path.read_text(encoding="utf-8")
            if 'decision.get("provides_liquidity", False)' not in text:
                missing.append(f"{path.relative_to(ROOT)}:provides_liquidity_default")

        self.assertEqual(
            missing,
            [],
            "RAG liquidity rows should not abort if an LLM omits the optional "
            "provides_liquidity flag; default false preserves conservative depth.",
        )

    def test_rumorspread_llm_players_defines_logger(self):
        path = ROOT / "examples" / "RumorSpread" / "LLM" / "players.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        has_logger = False
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "logger":
                    has_logger = True

        self.assertTrue(has_logger)

    def test_creditcycle_api_modes_fall_back_to_hold_on_parse_failure(self):
        helper = ROOT / "examples" / "CreditCycle" / "llm_decision.py"
        player_files = [
            ROOT / "examples" / "CreditCycle" / "LLM" / "players.py",
            ROOT / "examples" / "CreditCycle" / "Rag" / "players.py",
        ]

        missing = []
        helper_text = helper.read_text(encoding="utf-8")
        if "is_parse_contract_error(exc)" not in helper_text or '"parse_contract"' not in helper_text:
            missing.append(str(helper.relative_to(ROOT)))
        for path in player_files:
            text = path.read_text(encoding="utf-8")
            if "decide_with_llm_contract(" not in text or "record_fallback(" not in text:
                missing.append(str(path.relative_to(ROOT)))

        self.assertEqual(
            missing,
            [],
            "CreditCycle API modes should hold after repeated malformed LLM output "
            "instead of aborting the whole simulation.",
        )

    def test_disposition_rag_persona_uses_framework_proxy_schema(self):
        path = ROOT / "configs" / "DispositionEffect" / "Rag" / "persona.yml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))

        self.assertIn("proxy", data)
        self.assertIn("storage", data["proxy"])
        self.assertIn("monitoring", data["proxy"])
        self.assertIn("communication", data["proxy"])
        self.assertIn("resource", data["proxy"])

    def test_disposition_rag_updates_reference_point_like_rulellm(self):
        path = ROOT / "examples" / "DispositionEffect" / "Rag" / "players.py"
        text = path.read_text(encoding="utf-8")

        required = [
            "def update_reference_point(",
            'self.state.custom_state["purchase_price"] = total_cost / position',
            'self.state.custom_state["total_cost"] = max(0, total_cost)',
        ]
        missing = [needle for needle in required if needle not in text]

        self.assertEqual(
            missing,
            [],
            "DispositionEffect RAG investors reuse the RuleLLM trading logic "
            "and must update reference points after buys/sells.",
        )

    def test_volmageddon_api_simulation_configs_have_no_top_level_llm(self):
        files = [
            ROOT / "configs" / "Volmageddon" / "LLM" / "simulation.yml",
            ROOT / "configs" / "Volmageddon" / "RuleLLM" / "simulation.yml",
            ROOT / "configs" / "Volmageddon" / "Rag" / "simulation.yml",
        ]

        offenders = []
        for path in files:
            data = load_config(str(path))
            if "llm" in data:
                offenders.append(str(path.relative_to(ROOT)))

        self.assertEqual(
            offenders,
            [],
            "SimulationConfig does not accept a top-level llm field; provider config "
            "belongs under players.yml extras.",
        )

    def test_non_positive_bid_guard_for_rows_that_hit_validate_order(self):
        player_files = [
            ROOT / "examples" / "AvailabilityBias" / "RuleLLM" / "players.py",
            ROOT / "examples" / "AvailabilityBias" / "Rag" / "players.py",
            ROOT / "examples" / "FlashCrash2010" / "Rag" / "players.py",
        ]

        missing = []
        for path in player_files:
            text = path.read_text(encoding="utf-8")
            if "if bid_price <= 0:" not in text:
                missing.append(str(path.relative_to(ROOT)))

        self.assertEqual(
            missing,
            [],
            "Rows that validate orders must normalize LLM bid_price=0 before "
            "calling validate_order.",
        )

    def test_flashcrash2010_api_orders_preserve_market_agent_type(self):
        player_files = [
            ROOT / "examples" / "FlashCrash2010" / "RuleLLM" / "players.py",
            ROOT / "examples" / "FlashCrash2010" / "Rag" / "players.py",
        ]

        missing = []
        for path in player_files:
            text = path.read_text(encoding="utf-8")
            if "def agent_type_for_strategy" not in text:
                missing.append(f"{path.relative_to(ROOT)}:helper")
            if '"agent_type": agent_type_for_strategy(strategy_name)' not in text:
                missing.append(f"{path.relative_to(ROOT)}:order")

        self.assertEqual(
            missing,
            [],
            "FlashCrash2010 market computes depth from order['agent_type']; "
            "API modes must preserve rule-equivalent agent types.",
        )

    def test_rag_payload_and_config_shape_normalizers_exist(self):
        checks = [
            (
                ROOT / "examples" / "FramingEffect" / "Rag" / "players.py",
                ["def market_update_payload", 'payload.get("type")'],
            ),
            (
                ROOT / "examples" / "GamblerFallacy" / "Rag" / "players.py",
                ["def market_update_payload", 'payload.get("type")'],
            ),
            (
                ROOT / "examples" / "RepresentativenessBias" / "Rag" / "players.py",
                [
                    'private_knowledge = extras["private_knowledge"]',
                    "from examples.RepresentativenessBias.Rule.players import Market, _info_payload",
                ],
            ),
            (
                ROOT / "examples" / "LTCMCollapse" / "Rag" / "players.py",
                ['extras.get("rag")', 'extras.get("private_knowledge", {})'],
            ),
            (
                ROOT / "examples" / "LUNACollapse" / "Rag" / "players.py",
                ['extras.get("rag")', 'extras.get("private_knowledge", {})'],
            ),
        ]

        missing = []
        for path, needles in checks:
            text = path.read_text(encoding="utf-8")
            for needle in needles:
                if needle not in text:
                    missing.append(f"{path.relative_to(ROOT)}:{needle}")

        self.assertEqual(
            missing,
            [],
            "RAG rows should tolerate routed market payloads and the current "
            "private_knowledge.rag config shape.",
        )

    def test_framing_gambler_rag_initialize_market_state(self):
        player_files = [
            ROOT / "examples" / "FramingEffect" / "Rag" / "players.py",
            ROOT / "examples" / "GamblerFallacy" / "Rag" / "players.py",
        ]
        required = [
            'self.state.custom_state["price"] = extras["initial_price"]',
            'self.state.custom_state["fundamental"] = extras["fundamental_value"]',
            'self.state.custom_state["deviation"] = 0.0',
        ]

        missing = []
        for path in player_files:
            text = path.read_text(encoding="utf-8")
            for needle in required:
                if needle not in text:
                    missing.append(f"{path.relative_to(ROOT)}:{needle}")

        self.assertEqual(
            missing,
            [],
            "FramingEffect/GamblerFallacy RAG players can be scheduled before "
            "receiving the first market broadcast; they must initialize market "
            "state from config before building prompts.",
        )

    def test_framing_gambler_rag_orders_match_rule_market_contract(self):
        player_files = [
            ROOT / "examples" / "FramingEffect" / "Rag" / "players.py",
            ROOT / "examples" / "GamblerFallacy" / "Rag" / "players.py",
        ]
        required = [
            '"from": self.identity',
            '"agent_type": self.__class__.__name__',
        ]

        missing = []
        for path in player_files:
            text = path.read_text(encoding="utf-8")
            for needle in required:
                if text.count(needle) < 2:
                    missing.append(f"{path.relative_to(ROOT)}:{needle}")

        self.assertEqual(
            missing,
            [],
            "FramingEffect/GamblerFallacy RAG players reuse Rule markets that "
            "read order['from'] and order['agent_type']; both decide() and "
            "act() order payloads must preserve those fields.",
        )

    def test_framing_gambler_rag_object_store_budget(self):
        config_files = [
            ROOT / "configs" / "FramingEffect" / "Rag" / "simulation.yml",
            ROOT / "configs" / "GamblerFallacy" / "Rag" / "simulation.yml",
        ]

        too_small = []
        for path in config_files:
            text = path.read_text(encoding="utf-8")
            if "object_store_memory: 536870912" not in text:
                too_small.append(str(path.relative_to(ROOT)))

        self.assertEqual(
            too_small,
            [],
            "These RAG rows should use at least 512MB Ray object store budget "
            "before full-round reruns.",
        )

    def test_short_squeeze_rag_market_exports_squeeze_state(self):
        path = ROOT / "examples" / "ShortSqueeze" / "Rag" / "players.py"
        text = path.read_text(encoding="utf-8")
        required = [
            '"short_interest": short_interest',
            '"squeeze_pressure": squeeze_pressure',
            'self.state.custom_state["short_interest"]',
        ]

        missing = [needle for needle in required if needle not in text]
        self.assertEqual(
            missing,
            [],
            "ShortSqueeze RAG prompts read short_interest/squeeze_pressure from "
            "market_data, so the RAG market must publish the same fields as RuleLLM.",
        )

    def test_remaining_api_fallbacks_classify_transport_errors(self):
        player_files = [
            ROOT / "examples" / "AsianFinancialCrisis" / "Rag" / "players.py",
            ROOT / "examples" / "AvailabilityBias" / "LLM" / "players.py",
            ROOT / "examples" / "AvailabilityBias" / "RuleLLM" / "players.py",
            ROOT / "examples" / "AvailabilityBias" / "Rag" / "players.py",
            ROOT / "examples" / "LTCMCollapse" / "Rag" / "players.py",
            ROOT / "examples" / "LUNACollapse" / "Rag" / "players.py",
        ]

        missing = []
        for path in player_files:
            text = path.read_text(encoding="utf-8")
            if "is_retryable_llm_error" not in text:
                missing.append(f"{path.relative_to(ROOT)}:retryable")
            has_audited_fallback = (
                "LLM fallback hold after retries" in text or "LLM parse failed" in text
            )
            has_fail_fast_contract = "LLM decision contract failed after" in text
            if not has_audited_fallback and not has_fail_fast_contract:
                missing.append(f"{path.relative_to(ROOT)}:fallback")

        self.assertEqual(
            missing,
            [],
            "Observed APITimeout/parse rows should classify transient transport "
            "errors separately from deterministic contract failures.",
        )

    def test_failed_rag_configs_provide_embed_api_key_when_players_require_it(self):
        scenarios = ["SVBBankRun", "SunkCostFallacy", "TulipMania"]

        missing = []
        for scenario in scenarios:
            player_path = ROOT / "examples" / scenario / "Rag" / "players.py"
            player_text = player_path.read_text(encoding="utf-8")
            directly_indexes_key = (
                'resolved_rag["embed_api_key"]' in player_text
                or 'rag_cfg["embed_api_key"]' in player_text
            )
            if not directly_indexes_key:
                continue

            cfg = load_config(str(ROOT / "configs" / scenario / "Rag" / "simulation.yml"))
            for player_key, player in cfg["players"].items():
                extras = player.get("config", {}).get("extras", {})
                rag = extras.get("private_knowledge", {}).get("rag", {})
                if rag and "embed_api_key" not in rag:
                    missing.append(f"{scenario}__Rag:{player_key}")

        self.assertEqual(
            missing,
            [],
            "RAG configs must provide embed_api_key when their players directly "
            "index the resolved RAG config.",
        )

    def test_failed_bid_price_prompts_explicitly_forbid_zero_for_hold(self):
        prompt_files = [
            ROOT / "examples" / "ArchegosCollapse" / "LLM" / "prompts.py",
            ROOT / "examples" / "ArchegosCollapse" / "RuleLLM" / "prompts.py",
            ROOT / "examples" / "ArchegosCollapse" / "Rag" / "prompts.py",
            ROOT / "examples" / "AsianFinancialCrisis" / "LLM" / "prompts.py",
            ROOT / "examples" / "AsianFinancialCrisis" / "RuleLLM" / "prompts.py",
            ROOT / "examples" / "AsianFinancialCrisis" / "Rag" / "prompts.py",
            ROOT / "examples" / "BlackMonday1987" / "LLM" / "prompts.py",
            ROOT / "examples" / "BlackMonday1987" / "RuleLLM" / "prompts.py",
            ROOT / "examples" / "BlackMonday1987" / "Rag" / "prompts.py",
            ROOT / "examples" / "CarryTradeUnwind" / "LLM" / "prompts.py",
            ROOT / "examples" / "CarryTradeUnwind" / "RuleLLM" / "prompts.py",
            ROOT / "examples" / "CarryTradeUnwind" / "Rag" / "prompts.py",
            ROOT / "examples" / "CurrencyCrisis" / "LLM" / "prompts.py",
            ROOT / "examples" / "DotComBubble" / "LLM" / "prompts.py",
            ROOT / "examples" / "DotComBubble" / "Rag" / "prompts.py",
            ROOT / "examples" / "EuropeanDebtCrisis" / "LLM" / "prompts.py",
            ROOT / "examples" / "LTCMCollapse" / "LLM" / "prompts.py",
            ROOT / "examples" / "LUNACollapse" / "LLM" / "prompts.py",
            ROOT / "examples" / "LUNACollapse" / "RuleLLM" / "prompts.py",
        ]

        missing = []
        for path in prompt_files:
            text = path.read_text(encoding="utf-8")
            if "bid_price" not in text:
                continue
            lower = text.lower()
            if "strictly positive" not in lower:
                missing.append(f"{path.relative_to(ROOT)}:strictly_positive")
            if "never output bid_price: 0" not in lower:
                missing.append(f"{path.relative_to(ROOT)}:never_zero")
            if "for hold" not in lower or "current price" not in lower:
                missing.append(f"{path.relative_to(ROOT)}:hold_current_price")

        self.assertEqual(
            missing,
            [],
            "Prompts that feed strict bid_price validators must tell the model "
            "that hold decisions still require a strictly positive current-price bid.",
        )

    def test_candidate_api_prompts_do_not_teach_zero_bid_price_holds(self):
        prompt_files = [
            ROOT / "examples" / "FlashCrash" / "RuleLLM" / "prompts.py",
            ROOT / "examples" / "FlashCrash" / "Rag" / "prompts.py",
        ]

        offenders = []
        for path in prompt_files:
            if "bid_price = 0.0" in path.read_text(encoding="utf-8"):
                offenders.append(str(path.relative_to(ROOT)))

        self.assertEqual(
            offenders,
            [],
            "Candidate API prompts must not teach hold decisions with bid_price=0; "
            "use current price so strict order validators and market code stay aligned.",
        )

    def test_framingeffect_rulellm_retries_parse_contract_failures(self):
        path = ROOT / "examples" / "FramingEffect" / "RuleLLM" / "players.py"
        text = path.read_text(encoding="utf-8")

        required = [
            "max_retries = 3",
            "parse_error = isinstance(exc, (ValueError, KeyError))",
            "is_retryable_llm_error(exc)",
            "LLM decision contract failed after",
        ]
        missing = [needle for needle in required if needle not in text]

        self.assertEqual(
            missing,
            [],
            "FramingEffect RuleLLM should retry stochastic malformed JSON before "
            "failing the row.",
        )

    def test_failed_numeric_overflow_rows_guard_finite_portfolio_arithmetic(self):
        player_files = [
            ROOT / "examples" / "OverconfidenceBias" / "Rule" / "players.py",
            ROOT / "examples" / "OverconfidenceBias" / "LLM" / "players.py",
            ROOT / "examples" / "OverconfidenceBias" / "RuleLLM" / "players.py",
            ROOT / "examples" / "OverconfidenceBias" / "Rag" / "players.py",
            ROOT / "examples" / "MentalAccounting" / "LLM" / "players.py",
            ROOT / "examples" / "MentalAccounting" / "Rag" / "players.py",
        ]

        missing = []
        for path in player_files:
            text = path.read_text(encoding="utf-8")
            if "safe_max_affordable" not in text:
                missing.append(f"{path.relative_to(ROOT)}:safe_max_affordable")
            if "OverconfidenceBias/Rule/players.py" in str(path):
                if "math.isfinite" not in text:
                    missing.append(f"{path.relative_to(ROOT)}:math.isfinite")
                if "_to_nonnegative_int" not in text:
                    missing.append(f"{path.relative_to(ROOT)}:_to_nonnegative_int")
                continue
            if "OverconfidenceBias" in str(path):
                if "_to_nonnegative_int" not in text:
                    missing.append(f"{path.relative_to(ROOT)}:_to_nonnegative_int")
                if "configured_order_limit" not in text:
                    missing.append(f"{path.relative_to(ROOT)}:configured_order_limit")
                continue
            if "math.isfinite" not in text:
                missing.append(f"{path.relative_to(ROOT)}:math.isfinite")

        self.assertEqual(
            missing,
            [],
            "API portfolio updates must guard cash/price arithmetic before "
            "int(cash / price) conversions.",
        )

    def test_equity_premium_api_rejects_non_finite_stock_qty(self):
        from examples.EquityPremium.decision import parse_equity_premium_decision

        bad_payloads = [
            '<decision>{"stock_qty": NaN, "reasoning": "bad"}</decision>',
            '<decision>{"stock_qty": Infinity, "reasoning": "bad"}</decision>',
        ]
        for payload in bad_payloads:
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(ValueError, "non-finite stock_qty"):
                    parse_equity_premium_decision(payload)

        llm_player = ROOT / "examples" / "EquityPremium" / "LLM" / "players.py"
        self.assertIn("math.isfinite(stock_qty)", llm_player.read_text(encoding="utf-8"))

    def test_shared_llm_parsers_reject_non_finite_numeric_fields(self):
        from examples.llm_utils import (
            parse_llm_quantity_response_with_thinking,
            parse_llm_response_with_thinking,
        )

        bad_canonical = (
            '<decision>{"action": "buy", "bid_price": NaN, '
            '"quantity": 1, "reasoning": "bad"}</decision>'
        )
        bad_quantity = (
            '<decision>{"action": "buy", "quantity": Infinity, '
            '"reasoning": "bad"}</decision>'
        )
        with self.assertRaisesRegex(ValueError, "non-finite numeric field bid_price"):
            parse_llm_response_with_thinking(bad_canonical)
        with self.assertRaisesRegex(ValueError, "non-finite numeric field quantity"):
            parse_llm_quantity_response_with_thinking(bad_quantity)

    def test_special_schema_parsers_reject_non_finite_numeric_fields(self):
        from examples.RumorSpread.llm_parser import parse_rumor_response
        from examples.SVBBankRun.decision import parse_svbbankrun_decision

        bad_rumor = (
            '<decision>{"action_type": "spread", "intensity": Infinity, '
            '"reasoning": "bad"}</decision>'
        )
        bad_bank = (
            '<decision>{"action": "buy", "quantity": NaN, '
            '"reasoning": "bad"}</decision>'
        )
        with self.assertRaisesRegex(ValueError, "non-finite intensity"):
            parse_rumor_response(bad_rumor)
        with self.assertRaisesRegex(ValueError, "non-finite SVBBankRun quantity"):
            parse_svbbankrun_decision(bad_bank)

    def test_rag_configs_include_embedding_and_chunk_contract_fields(self):
        rows = [
            ("SVBBankRun", "Rag"),
            ("SunkCostFallacy", "Rag"),
            ("TulipMania", "Rag"),
        ]

        missing = []
        required_fields = ("embed_api_key", "chunk_size", "chunk_overlap")
        for scenario, mechanism in rows:
            cfg = load_config(str(ROOT / "configs" / scenario / mechanism / "simulation.yml"))
            for player_key, player in cfg["players"].items():
                extras = player.get("config", {}).get("extras", {})
                rag = extras.get("private_knowledge", {}).get("rag", {})
                if not rag:
                    continue
                for field in required_fields:
                    if field not in rag:
                        missing.append(f"{scenario}__{mechanism}:{player_key}:{field}")

        self.assertEqual(
            missing,
            [],
            "RAG configs must provide the fields directly indexed by their "
            "KnowledgeStore setup code.",
        )


if __name__ == "__main__":
    unittest.main()
