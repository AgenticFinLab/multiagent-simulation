import asyncio
import unittest
from types import SimpleNamespace

from masim.player.base import PlayerConfig

from examples.DotComBubble.RuleLLM.players import RuleLLMMomentumFollower


class _FakeLLM:
    def __init__(self) -> None:
        self.inputs = None

    def run(self, inputs):
        self.inputs = inputs
        response = (
            '<analysis>Momentum is positive.</analysis>'
            '<decision>{"action":"buy","bid_price":102.0,'
            '"quantity":500,"reasoning":"follow the configured trend rule"}</decision>'
        )
        return SimpleNamespace(response=response)


class _TimeoutLLM:
    def __init__(self) -> None:
        self.calls = 0

    def run(self, inputs):
        self.calls += 1
        raise TimeoutError("Request timed out")


class RuleLLMSmokeTest(unittest.TestCase):
    @staticmethod
    def _player(llm):
        config = PlayerConfig(
            name="MomentumFollower",
            identity="momentumfollower",
            extras={
                "initial_cash": 100_000.0,
                "initial_position": 0,
                "llm": {
                    "sys_message": (
                        "examples.DotComBubble.RuleLLM.prompts:"
                        "RULELLM_MOMENTUM_FOLLOWER_SYS"
                    ),
                    "user_message": (
                        "examples.DotComBubble.RuleLLM.prompts:RULELLM_USER_TEMPLATE"
                    ),
                },
            },
        )
        player = RuleLLMMomentumFollower(config)
        player.state.custom_state.update(
            {
                "cash": 100_000.0,
                "position": 0,
                "round": 2,
                "market_data": {
                    "price": 102.0,
                    "fundamental": 100.0,
                    "deviation": 0.02,
                },
                "price_history": [99.0, 102.0],
                "llm_client": llm,
                "llm_params": {"lm_name": "fake", "generation_config": {}},
            }
        )
        return player

    def test_momentum_decision_and_action_lifecycle(self):
        fake_llm = _FakeLLM()
        player = self._player(fake_llm)

        decision = asyncio.run(player.decide())
        self.assertEqual(decision["action"], "buy")
        self.assertEqual(decision["quantity"], 500)
        self.assertIn("One-Round Price Change: +3.03%", fake_llm.inputs[0].user_msg)

        serialized = player.__getstate__()
        self.assertNotIn("llm_client", serialized["state"].custom_state)
        self.assertIs(player.state.custom_state["llm_client"], fake_llm)

        action = asyncio.run(player.act(decision))
        self.assertEqual(action.payload["action"], "buy")
        self.assertEqual(player.state.custom_state["cash"], 49_000.0)
        self.assertEqual(player.state.custom_state["position"], 500)

    def test_timeout_falls_back_to_hold_without_aborting_round(self):
        timeout_llm = _TimeoutLLM()
        player = self._player(timeout_llm)

        decision = asyncio.run(player.decide())

        self.assertEqual(timeout_llm.calls, 3)
        self.assertEqual(decision["action"], "hold")
        self.assertEqual(decision["quantity"], 0)
        self.assertTrue(decision["llm_fallback"])
        self.assertIn("Request timed out", decision["reasoning"])


if __name__ == "__main__":
    unittest.main()
