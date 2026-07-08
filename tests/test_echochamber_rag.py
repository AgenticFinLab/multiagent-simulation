"""Focused contract and configuration tests for EchoChamber Rag."""

import math
import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from examples.EchoChamber.Rag.analysis import (
    _RAG_FALLBACK,
    analyze_rag_knowledge_effect,
    compute_api_quality,
    compute_cluster_separation,
    compute_opinion_dispersion,
    compute_polarization_amplification,
    compute_polarization_persistence,
)
from examples.EchoChamber.Rag.players import (
    RagLLMSocialAgent,
    _parse_echo_chamber_response,
)
from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config


class EchoChamberRagContractTests(unittest.TestCase):
    def test_resume_checkpoint_is_atomic_and_scenario_independent(self) -> None:
        with tempfile.TemporaryDirectory() as record_path:
            GeneralSimulator._write_resume_checkpoint(record_path, 37)
            self.assertEqual(
                GeneralSimulator._detect_resume_round(record_path), 37
            )
            with open(
                os.path.join(record_path, ".masim-progress.json"),
                encoding="utf-8",
            ) as checkpoint_file:
                self.assertEqual(
                    json.load(checkpoint_file), {"completed_round": 37}
                )

    def test_resume_recovers_legacy_echochamber_message_records(self) -> None:
        with tempfile.TemporaryDirectory() as record_path:
            messages_path = os.path.join(record_path, "environment", "messages")
            os.makedirs(messages_path)
            with open(
                os.path.join(messages_path, "msg_block_0.json"),
                "w",
                encoding="utf-8",
            ) as message_file:
                json.dump(
                    {
                        "first": {"round_num": 171},
                        "last": {"round_num": 172},
                    },
                    message_file,
                )
            self.assertEqual(
                GeneralSimulator._detect_resume_round(record_path), 172
            )

    def test_parser_accepts_only_canonical_tagged_decision(self) -> None:
        response = (
            "<analysis>Cross-cutting evidence supports moderation.</analysis>"
            '<decision>{"action_type":"depolarize","intensity":0.4,'
            '"reasoning":"build a bridge"}</decision>'
        )
        self.assertEqual(
            _parse_echo_chamber_response(response),
            {
                "action_type": "depolarize",
                "intensity": 0.4,
                "reasoning": "build a bridge",
                "analysis": "Cross-cutting evidence supports moderation.",
            },
        )

    def test_parser_rejects_malformed_or_out_of_contract_output(self) -> None:
        responses = [
            '{"action_type":"neutral","intensity":0,"reasoning":"wait"}',
            '<analysis>x</analysis><decision>{"action_type":"polarize",'
            '"intensity":1.1,"reasoning":"push"}</decision>',
            '<analysis>x</analysis><decision>{"action_type":"neutral",'
            '"intensity":true,"reasoning":"wait"}</decision>',
            '<analysis>x</analysis><decision>{"action_type":"neutral",'
            '"intensity":0,"reasoning":"wait","extra":1}</decision>',
        ]
        for response in responses:
            with self.subTest(response=response), self.assertRaises(ValueError):
                _parse_echo_chamber_response(response)

    def test_metric_contracts_and_retrieval_fallback(self) -> None:
        self.assertEqual(compute_polarization_amplification([0.2, 0.4]), 2.0)
        self.assertEqual(compute_polarization_persistence([0.1, 0.3, 0.5]), 0.4)
        self.assertEqual(
            compute_cluster_separation([0.1, 0.4]),
            {"maximum": 0.4, "final": 0.4, "average": 0.25},
        )
        self.assertEqual(
            compute_opinion_dispersion({"left": [-0.5], "right": [0.5]}), 0.5
        )
        quality = compute_api_quality(
            [
                {"action_type": "neutral", "intensity": 0.0, "reasoning": "wait"},
                {
                    "action_type": "polarize",
                    "intensity": math.nan,
                    "reasoning": "push",
                },
            ],
            [_RAG_FALLBACK, "Retrieved evidence"],
        )
        self.assertEqual(quality["valid_action_rate"], 0.5)
        self.assertEqual(quality["retrieval_coverage"], 0.5)

        rag_stats = analyze_rag_knowledge_effect(
            {
                "agent": {
                    1: {"rag_context": _RAG_FALLBACK},
                    2: {"rag_context": "evidence"},
                }
            }
        )
        self.assertEqual(rag_stats["agent"]["retrieval_failure_rate"], 0.5)

    def test_full_config_loads_and_declared_classes_import(self) -> None:
        raw = load_config("configs/EchoChamber/Rag/simulation.yml")
        config = SimulationConfig(**raw)
        self.assertEqual(config.setting["total_rounds"], 200)
        players = raw["players"]
        self.assertEqual(set(raw["topology"]["connections"]), set(players))
        for player in players.values():
            module_name, class_name = player["class"].split(":", 1)
            module = __import__(module_name, fromlist=[class_name])
            self.assertTrue(hasattr(module, class_name))

    def test_rag_query_failure_falls_back_and_opens_circuit(self) -> None:
        rag_store = Mock()
        rag_store.is_built.return_value = True
        rag_store.query.side_effect = RuntimeError("embedding endpoint returned 403")
        agent = object.__new__(RagLLMSocialAgent)
        agent.identity = "test_agent"
        agent.config = SimpleNamespace(
            identity="test_agent",
            extras={
                "llm": {
                    "user_message": "examples.EchoChamber.Rag.prompts:RAG_USER_TEMPLATE"
                }
            },
        )
        agent.state = SimpleNamespace(
            custom_state={
                "my_opinion": 0.1,
                "round": 5,
                "rag_store": rag_store,
                "rag_cfg": {"top_k": 5},
            }
        )
        env_data = {
            "polarization": 0.2,
            "prev_polarization": 0.1,
            "polarization_change": 0.1,
            "mean_opinion": 0.0,
            "cluster_separation": 0.3,
            "cross_cutting_exposure": 0.4,
            "num_polarizers": 1,
            "num_depolarizers": 1,
            "net_polarization_intensity": 0.0,
        }

        first_prompt = agent._build_prompt(env_data)
        second_prompt = agent._build_prompt(env_data)

        self.assertIn(_RAG_FALLBACK, first_prompt)
        self.assertIn(_RAG_FALLBACK, second_prompt)
        self.assertTrue(agent.state.custom_state["rag_query_disabled"])
        rag_store.query.assert_called_once()


if __name__ == "__main__":
    unittest.main()
