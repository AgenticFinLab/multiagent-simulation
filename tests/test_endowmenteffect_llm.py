import asyncio
import unittest
from types import SimpleNamespace

from masim.player.base import PlayerConfig

from examples.EndowmentEffect.LLM.players import LLMEndowedHolder


class _FakeLLM:
    def run(self, inputs):
        response = (
            "<analysis>The offer is not compelling enough to sell.</analysis>"
            '<decision>{"action":"hold","bid_price":100.0,'
            '"quantity":0,"reasoning":"keep the current position"}</decision>'
        )
        return SimpleNamespace(response=response)


class EndowmentEffectLLMSmokeTest(unittest.TestCase):
    def test_decision_serialization_and_action_lifecycle(self):
        config = PlayerConfig(
            name="EndowedHolder",
            identity="endowedholder",
            extras={
                "base_size": 300,
                "llm": {
                    "sys_message": (
                        "examples.EndowmentEffect.LLM.prompts:"
                        "LLM_ENDOWED_HOLDER_SYS"
                    ),
                    "user_message": (
                        "examples.EndowmentEffect.LLM.prompts:LLM_USER_TEMPLATE"
                    ),
                    "max_retries": 3,
                },
            },
        )
        player = LLMEndowedHolder(config)
        fake_llm = _FakeLLM()
        player.state.custom_state.update(
            {
                "cash": 800_000.0,
                "position": 500,
                "round": 1,
                "market_data": {
                    "price": 100.0,
                    "fundamental": 100.0,
                    "deviation": 0.0,
                },
                "llm_client": fake_llm,
                "llm_params": {"lm_name": "fake", "generation_config": {}},
            }
        )

        decision = asyncio.run(player.decide())
        self.assertEqual(decision["action"], "hold")
        self.assertEqual(decision["quantity"], 0)
        self.assertEqual(decision["bid_price"], 100.0)

        serialized = player.__getstate__()
        self.assertNotIn("llm_client", serialized["state"].custom_state)
        self.assertIs(player.state.custom_state["llm_client"], fake_llm)

        action = asyncio.run(player.act(decision))
        self.assertEqual(action.payload["action"], "hold")
        self.assertEqual(player.state.custom_state["cash"], 800_000.0)
        self.assertEqual(player.state.custom_state["position"], 500)


if __name__ == "__main__":
    unittest.main()
