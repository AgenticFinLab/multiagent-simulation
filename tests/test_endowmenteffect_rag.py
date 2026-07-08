import asyncio
import unittest
from types import SimpleNamespace

from masim.player.base import PlayerConfig

from examples.EndowmentEffect.Rag import prompts
from examples.EndowmentEffect.Rag.analysis import (
    _RAG_FALLBACK,
    analyze_rag_knowledge_effect,
)
from examples.EndowmentEffect.Rag.players import RagLLMEndowedHolder


class _FakeLLM:
    def run(self, inputs):
        response = (
            "<analysis>Retrieved evidence supports holding this round.</analysis>"
            '<decision>{"action":"hold","bid_price":100.0,'
            '"quantity":0,"reasoning":"reservation price is not met"}</decision>'
        )
        return SimpleNamespace(response=response)


class _FakeRagResult:
    formatted_text = "Retrieved evidence"


class _FakeRagStore:
    def is_built(self):
        return True

    def query(self, query):
        return _FakeRagResult()


class EndowmentEffectRagSmokeTest(unittest.TestCase):
    def test_decision_serialization_and_rag_payload(self):
        config = PlayerConfig(
            name="EndowedHolder",
            identity="endowedholder",
            extras={
                "base_size": 300,
                "llm": {
                    "sys_message": (
                        "examples.EndowmentEffect.Rag.prompts:"
                        "RAG_ENDOWED_HOLDER_SYS"
                    ),
                    "user_message": (
                        "examples.EndowmentEffect.Rag.prompts:RAG_USER_TEMPLATE"
                    ),
                    "max_retries": 3,
                },
            },
        )
        player = RagLLMEndowedHolder(config)
        fake_llm = _FakeLLM()
        fake_rag_store = _FakeRagStore()
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
                "rag_store": fake_rag_store,
                "rag_cfg": {"top_k": 5},
                "llm_params": {"lm_name": "fake", "generation_config": {}},
            }
        )

        decision = asyncio.run(player.decide())
        self.assertEqual(decision["action"], "hold")
        self.assertEqual(decision["quantity"], 0)
        self.assertEqual(decision["bid_price"], 100.0)
        self.assertEqual(decision["rag_context"], "Retrieved evidence")
        self.assertEqual(
            decision["outbound_messages"][0]["payload"]["rag_context"],
            "Retrieved evidence",
        )

        serialized = player.__getstate__()
        self.assertNotIn("llm_client", serialized["state"].custom_state)
        self.assertNotIn("rag_store", serialized["state"].custom_state)
        self.assertIs(player.state.custom_state["llm_client"], fake_llm)
        self.assertIs(player.state.custom_state["rag_store"], fake_rag_store)

        action = asyncio.run(player.act(decision))
        self.assertEqual(action.payload["action"], "hold")
        self.assertEqual(player.state.custom_state["cash"], 800_000.0)
        self.assertEqual(player.state.custom_state["position"], 500)

    def test_rag_coverage_requires_context_field(self):
        stats = analyze_rag_knowledge_effect(
            {
                "endowedholder": [
                    {"rag_context": _RAG_FALLBACK},
                    {"rag_context": "Retrieved evidence"},
                ]
            }
        )

        self.assertEqual(stats["total_payloads"], 2)
        self.assertEqual(stats["context_payloads"], 2)
        self.assertEqual(stats["fallback_payloads"], 1)
        self.assertEqual(stats["retrieval_payloads"], 1)
        self.assertEqual(stats["fallback_rate"], 0.5)
        self.assertEqual(stats["retrieval_rate"], 0.5)

        with self.assertRaises(ValueError):
            analyze_rag_knowledge_effect({"endowedholder": [{"action": "hold"}]})

    def test_prompts_keep_rulellm_contract_markers(self):
        for prompt in (
            prompts.RAG_ENDOWED_HOLDER_SYS,
            prompts.RAG_STATUS_QUO_SELLER_SYS,
            prompts.RAG_RATIONAL_ARBITRAGEUR_SYS,
            prompts.RAG_NEW_BUYER_SYS,
            prompts.RAG_NOISE_TRADER_SYS,
        ):
            self.assertIn("== PERSONA ==", prompt)
            self.assertIn("== DECISION RULES ==", prompt)

        self.assertIn("{rag_context}", prompts.RAG_USER_TEMPLATE)


if __name__ == "__main__":
    unittest.main()
