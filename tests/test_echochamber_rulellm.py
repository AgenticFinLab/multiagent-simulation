"""Focused contract tests for the polished EchoChamber RuleLLM variant."""

import math
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from examples.EchoChamber.RuleLLM import prompts
from examples.EchoChamber.RuleLLM.analysis import (
    compute_api_quality,
    compute_cluster_separation,
    compute_opinion_dispersion,
    compute_polarization_amplification,
    compute_polarization_persistence,
)
from examples.EchoChamber.RuleLLM.players import RuleLLMSocialAgent
from masim.utils.config import load_config


def _parser_agent() -> RuleLLMSocialAgent:
    return object.__new__(RuleLLMSocialAgent)


class EchoChamberRuleLLMContractTests(unittest.TestCase):
    def test_config_loads_and_expands_all_players(self) -> None:
        config = load_config("configs/EchoChamber/RuleLLM/simulation.yml")

        self.assertEqual(len(config["players"]), 21)
        self.assertEqual(config["setting"]["total_rounds"], 200)
        ideologue_opinions = [
            player["config"]["extras"]["initial_opinion"]
            for key, player in config["players"].items()
            if key.startswith("rulellm_ideologue_")
        ]
        self.assertEqual(ideologue_opinions, [0.4] * 6)

    def test_every_system_prompt_has_persona_and_decision_rules(self) -> None:
        system_prompts = [
            prompts.RULELLM_IDEOLOGUE_SYS,
            prompts.RULELLM_CONFORMIST_SYS,
            prompts.RULELLM_CRITICAL_SYS,
            prompts.RULELLM_BRIDGE_SYS,
            prompts.RULELLM_PASSIVE_SYS,
        ]
        for system_prompt in system_prompts:
            with self.subTest(prompt=system_prompt[:40]):
                self.assertIn("== PERSONA ==", system_prompt)
                self.assertIn("== DECISION RULES", system_prompt)

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

    def test_parser_rejects_malformed_or_out_of_range_output(self) -> None:
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

    def test_decide_uses_current_lmbase_infer_output_contract(self) -> None:
        agent = _parser_agent()
        agent.identity = "rulellm_test_1"
        agent.config = SimpleNamespace(
            extras={
                "polarize_opinion_step": 0.1,
                "depolarize_opinion_step": 0.1,
                "llm": {
                    "sys_message": "unused:prompt",
                    "max_retries": 1,
                },
            }
        )
        agent.state = SimpleNamespace(
            custom_state={
                "round": 1,
                "env_data": {},
                "my_opinion": 0.2,
                "llm_client": SimpleNamespace(
                    run=lambda inputs: SimpleNamespace(
                        response=(
                            "<analysis>Hold steady.</analysis>"
                            '<decision>{"action_type":"neutral","intensity":0,'
                            '"reasoning":"wait"}</decision>'
                        )
                    )
                ),
            }
        )

        async def run_decide():
            with patch.object(agent, "_build_prompt", return_value="prompt"), patch(
                "examples.EchoChamber.RuleLLM.players.load_prompt",
                return_value="system",
            ):
                return await agent.decide()

        result = __import__("asyncio").run(run_decide())
        self.assertEqual(result["action_type"], "neutral")
        self.assertEqual(result["reasoning"], "wait")

    def test_metric_contracts(self) -> None:
        self.assertEqual(compute_polarization_amplification([0.2, 0.4]), 2.0)
        self.assertEqual(
            compute_polarization_persistence([0.1, 0.2, 0.4, 0.6]), 0.5
        )
        separation = compute_cluster_separation([0.1, 0.4, 0.3])
        self.assertEqual(separation["maximum"], 0.4)
        self.assertEqual(separation["final"], 0.3)
        self.assertEqual(
            compute_opinion_dispersion({"a": [-0.5], "b": [0.5]}), 0.5
        )
        quality = compute_api_quality(
            [
                {"action_type": "neutral", "intensity": 0.0, "reasoning": "wait"},
                {
                    "action_type": "polarize",
                    "intensity": math.nan,
                    "reasoning": "x",
                },
            ]
        )
        self.assertEqual(quality["valid_action_rate"], 0.5)


if __name__ == "__main__":
    unittest.main()
