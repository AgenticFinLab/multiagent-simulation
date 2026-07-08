"""Focused contract tests for the polished EchoChamber LLM variant."""

import math
import unittest

from examples.EchoChamber.LLM.analysis import (
    compute_api_quality,
    compute_cluster_separation,
    compute_opinion_dispersion,
    compute_polarization_amplification,
    compute_polarization_persistence,
)
from examples.EchoChamber.LLM.players import LLMSocialAgent


def _parser_agent() -> LLMSocialAgent:
    return object.__new__(LLMSocialAgent)


class EchoChamberLLMContractTests(unittest.TestCase):
    def test_parser_accepts_canonical_social_action(self) -> None:
        response = (
            "<analysis>The camps are separating.</analysis>"
            '<decision>{"action_type":"depolarize","intensity":0.4,'
            '"reasoning":"seek common ground"}</decision>'
        )

        decision = _parser_agent()._parse_llm_response(response)

        self.assertEqual(
            decision,
            {
                "action_type": "depolarize",
                "intensity": 0.4,
                "reasoning": "seek common ground",
                "analysis": "The camps are separating.",
            },
        )

    def test_parser_rejects_noncanonical_or_invalid_output(self) -> None:
        responses = [
            '{"action_type":"neutral","intensity":0,"reasoning":"wait"}',
            '<analysis>x</analysis><decision>{"action_type":"polarize",'
            '"intensity":1.1,"reasoning":"push"}</decision>',
            '<analysis>x</analysis><decision>{"action_type":"neutral",'
            '"intensity":true,"reasoning":"wait"}</decision>',
            '<analysis>x</analysis><decision>{"action_type":"invalid",'
            '"intensity":0.2,"reasoning":"wait"}</decision>',
        ]
        for response in responses:
            with self.subTest(response=response), self.assertRaises(ValueError):
                _parser_agent()._parse_llm_response(response)

    def test_metric_contracts(self) -> None:
        self.assertEqual(
            compute_polarization_amplification([0.2, 0.4, 0.3]), 2.0
        )
        self.assertEqual(
            compute_polarization_persistence([0.1, 0.2, 0.4, 0.6]), 0.5
        )
        separation = compute_cluster_separation([0.1, 0.4, 0.3])
        self.assertEqual(separation["maximum"], 0.4)
        self.assertEqual(separation["final"], 0.3)
        self.assertAlmostEqual(separation["average"], 0.8 / 3)
        self.assertEqual(
            compute_opinion_dispersion({"a": [-0.5], "b": [0.5]}), 0.5
        )

    def test_api_quality_reports_schema_failures(self) -> None:
        quality = compute_api_quality(
            [
                {
                    "action_type": "neutral",
                    "intensity": 0.0,
                    "reasoning": "wait",
                },
                {
                    "action_type": "polarize",
                    "intensity": math.nan,
                    "reasoning": "x",
                },
            ]
        )

        self.assertEqual(quality["valid_action_rate"], 0.5)
        self.assertEqual(quality["parse_failure_rate"], 0.5)
        self.assertEqual(quality["fallback_rate"], 0.0)
        self.assertEqual(quality["retrieval_coverage"], 0.0)


if __name__ == "__main__":
    unittest.main()
