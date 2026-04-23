"""EchoChamber Rag — RAG-augmented LLM simulation of echo chamber polarization dynamics."""

from __future__ import annotations

import importlib
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from examples.llm_utils import parse_llm_response_with_thinking
from masim.knowledge import (
    KnowledgeLoader,
    KnowledgeQuery,
    KnowledgeStore,
    ResourceManager,
)
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

from examples.EchoChamber.Rule.players import OpinionEnvironment  # noqa: F401

logger = logging.getLogger(__name__)


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from 'module:VAR' path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class RagLLMSocialAgent(GeneralPlayer):
    """Base RAG-augmented LLM social agent for EchoChamber."""

    _system_prompt_path: str = ""

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "my_opinion" not in self.state.custom_state:
            await self._initialize_agent()

        self.state.custom_state["round"] = observation.round
        if observation.inbounds:
            for inb in observation.inbounds:
                env_data = inb.payload
                self.state.custom_state["env_data"] = env_data
                self.state.custom_state["opinion_history"].append(
                    self.state.custom_state["my_opinion"]
                )

    async def _initialize_agent(self) -> None:
        extras = self.config.extras
        record_path = extras["record_path"]
        base_path = os.path.join(record_path, self.config.identity)
        custom_state_hot_limit = extras["custom_state_hot_limit"]
        self.state.custom_state["my_opinion"] = extras["initial_opinion"]
        self.state.custom_state["opinion_history"] = HistoryBuffer(
            folder=os.path.join(base_path, "opinion"),
            entry_limit=custom_state_hot_limit,
        )
        project_root = Path(__file__).parent.parent.parent
        load_dotenv(project_root / ".env")
        llm_cfg = extras["llm"]
        lm_name = llm_cfg["lm_name"]
        generation_config = llm_cfg["generation_config"]
        self.state.custom_state["lm_name"] = lm_name
        self.state.custom_state["generation_config"] = generation_config
        llm_client = LangChainAPIInference(
            lm_name=lm_name, generation_config=generation_config
        )
        self.state.custom_state["llm_client"] = llm_client
        private_knowledge = extras.get("private_knowledge", {})
        rag_cfg = private_knowledge.get("rag", extras.get("rag", {}))
        await self._initialize_rag(rag_cfg, llm_client, llm_cfg)

    async def _initialize_rag(
        self, rag_cfg: Dict[str, Any], llm_client: Any, llm_config: Dict[str, Any]
    ) -> None:
        extras = self.config.extras
        record_path = extras.get("record_path", "EXPERIMENT")
        knowledge_config = extras.get("knowledge", {})
        if not knowledge_config:
            knowledge_config = {
                "backend": "local",
                "global_uri": rag_cfg.get("docs_dir", "examples/document-sources"),
                "preprocessing": {
                    "parser": "mineru",
                    "output_position": rag_cfg.get(
                        "mineru_output_dir", "MinerU_processed"
                    ),
                },
                "rag": {
                    "output_position": rag_cfg.get("shared_rag_index_dir", "rag_index")
                },
            }
        resource_manager = ResourceManager(knowledge_config)
        private_knowledge = extras.get("private_knowledge", {})
        if not private_knowledge:
            private_knowledge = {
                "from_global_resources": ["MinerU_processed"],
                "local_resources": {"local_uri": "", "local_resources": []},
                "rag": rag_cfg,
            }
        agent_knowledge = resource_manager.resolve_agent_knowledge(
            agent_id=self.identity,
            private_knowledge=private_knowledge,
            record_path=record_path,
        )
        processed_dir = agent_knowledge["processed_dir"]
        shared_rag_dir = agent_knowledge["shared_rag_dir"]
        local_uri = agent_knowledge["local_uri"]
        local_rag_dir = agent_knowledge["local_rag_dir"]
        resolved_rag = agent_knowledge["rag"]
        os.makedirs(local_uri, exist_ok=True)
        os.makedirs(local_rag_dir, exist_ok=True)
        embed_type = resolved_rag.get("embed_type", "litellm")
        embed_api_key = resolved_rag.get("embed_api_key", "")
        if not embed_api_key:
            embed_api_key = (
                os.getenv("HUNYUAN_API_KEY", "")
                if embed_type == "litellm"
                else os.getenv("ARK_API_KEY", "")
            )
        rag_store = KnowledgeStore(
            embed_model_name=resolved_rag.get(
                "embed_model", "openai/hunyuan-embedding"
            ),
            embed_api_key=embed_api_key,
            embed_api_base=resolved_rag.get("embed_api_base", ""),
            embed_type=embed_type,
            persist_dir=local_rag_dir,
            chunk_size=int(resolved_rag.get("chunk_size", 512)),
            chunk_overlap=int(resolved_rag.get("chunk_overlap", 64)),
        )
        if os.path.isdir(local_rag_dir):
            index_files = [
                f for f in os.listdir(local_rag_dir) if not f.startswith(".")
            ]
            if index_files:
                try:
                    rag_store.load(local_rag_dir)
                    self.state.custom_state["rag_store"] = rag_store
                    self.state.custom_state["rag_cfg"] = resolved_rag
                    return
                except Exception as exc:  # pylint: disable=broad-except
                    logger.warning(
                        "[%s] Local index load failed: %s", self.identity, exc
                    )
        shared_rag_dirs = resolved_rag.get("shared_rag_index_dirs", [])
        if not shared_rag_dirs and os.path.isdir(shared_rag_dir):
            shared_rag_dirs = [shared_rag_dir]
        for s_dir in shared_rag_dirs:
            if os.path.isdir(s_dir):
                shared_files = [f for f in os.listdir(s_dir) if not f.startswith(".")]
                if shared_files:
                    try:
                        for item in shared_files:
                            src = os.path.join(s_dir, item)
                            dst = os.path.join(local_rag_dir, item)
                            if os.path.isdir(src):
                                shutil.copytree(src, dst, dirs_exist_ok=True)
                            else:
                                shutil.copy2(src, dst)
                        rag_store.load(local_rag_dir)
                        self.state.custom_state["rag_store"] = rag_store
                        self.state.custom_state["rag_cfg"] = resolved_rag
                        return
                    except Exception as exc:  # pylint: disable=broad-except
                        logger.warning(
                            "[%s] Shared copy failed: %s", self.identity, exc
                        )
        loader = KnowledgeLoader()
        if os.path.isdir(processed_dir) and os.listdir(processed_dir):
            docs = loader.load_from_dir(processed_dir)
        else:
            raise RuntimeError(
                f"[{self.identity}] No processed documents in {processed_dir}."
            )
        rag_store.build(docs)
        try:
            for item in os.listdir(local_rag_dir):
                if item.startswith("."):
                    continue
                src = os.path.join(local_rag_dir, item)
                dst = os.path.join(shared_rag_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("[%s] Copy to shared failed: %s", self.identity, exc)
        self.state.custom_state["rag_store"] = rag_store
        self.state.custom_state["rag_cfg"] = resolved_rag

    def __getstate__(self) -> Dict:
        state = self.__dict__.copy()
        if hasattr(self, "state") and hasattr(self.state, "custom_state"):
            custom = dict(self.state.custom_state)
            for key in ("llm_client", "rag_store"):
                custom.pop(key, None)
            state["state"].custom_state = custom
        return state

    def __setstate__(self, state: Dict) -> None:
        self.__dict__.update(state)
        if hasattr(self, "state") and hasattr(self.state, "custom_state"):
            custom = self.state.custom_state
            if "lm_name" in custom and "llm_client" not in custom:
                custom["llm_client"] = LangChainAPIInference(
                    lm_name=custom["lm_name"],
                    generation_config=custom["generation_config"],
                )
            if "rag_cfg" in custom and "rag_store" not in custom:
                rag_cfg = custom["rag_cfg"]
                local_rag_dir = rag_cfg.get("local_index_dir", "")
                if not local_rag_dir:
                    local_ws = rag_cfg.get("local_workspace_dir", "")
                    if local_ws:
                        local_rag_dir = os.path.join(local_ws, "rag_index")
                if not local_rag_dir:
                    return
                embed_type = rag_cfg.get("embed_type", "litellm")
                embed_api_key = rag_cfg.get("embed_api_key", "")
                if not embed_api_key:
                    embed_api_key = (
                        os.getenv("HUNYUAN_API_KEY", "")
                        if embed_type == "litellm"
                        else os.getenv("ARK_API_KEY", "")
                    )
                rag_store = KnowledgeStore(
                    embed_model_name=rag_cfg.get(
                        "embed_model", "openai/hunyuan-embedding"
                    ),
                    embed_api_key=embed_api_key,
                    embed_api_base=rag_cfg.get("embed_api_base", ""),
                    embed_type=embed_type,
                    persist_dir=local_rag_dir,
                    chunk_size=int(rag_cfg.get("chunk_size", 512)),
                    chunk_overlap=int(rag_cfg.get("chunk_overlap", 64)),
                )
                if os.path.isdir(local_rag_dir):
                    try:
                        rag_store.load(local_rag_dir)
                    except Exception as exc:  # pylint: disable=broad-except
                        logger.warning("RAG store reload failed: %s", exc)
                custom["rag_store"] = rag_store

    def _clamp_opinion(self, opinion: float) -> float:
        """Clamp opinion to valid range [-1, 1]."""
        return max(-1.0, min(1.0, opinion))

    def _apply_intensity_constraints(self, intensity: float) -> float:
        """Clamp intensity to valid range [0, 1]."""
        return max(0.0, min(1.0, intensity))

    def _build_prompt(self, env_data: Dict[str, Any]) -> str:
        my_opinion = self.state.custom_state["my_opinion"]
        round_num = self.state.custom_state.get("round", 0)
        polarization = env_data.get("polarization", 0.0)
        prev_polarization = env_data.get("prev_polarization", 0.0)
        polarization_change = env_data.get("polarization_change", 0.0)
        mean_opinion = env_data.get("mean_opinion", 0.0)
        cluster_separation = env_data.get("cluster_separation", 0.0)
        cross_cutting_exposure = env_data.get("cross_cutting_exposure", 0.5)
        num_polarizers = env_data.get("num_polarizers", 0)
        num_depolarizers = env_data.get("num_depolarizers", 0)
        net_polarization_intensity = env_data.get("net_polarization_intensity", 0.0)
        rag_store: Optional[KnowledgeStore] = self.state.custom_state.get("rag_store")
        rag_cfg: Dict[str, Any] = self.state.custom_state.get("rag_cfg", {})
        rag_context = ""
        if rag_store and rag_store.is_built():
            top_k = rag_cfg.get("top_k", 3)
            query = KnowledgeQuery(
                text=(
                    f"echo chamber polarization: opinion={my_opinion:.2f}, "
                    f"polarization={polarization:.3f}, cluster_separation={cluster_separation:.3f}"
                ),
                top_k=top_k,
                round_num=round_num,
                agent_id=self.config.identity,
            )
            result = rag_store.query(query)
            rag_context = result.formatted_text
        if not rag_context:
            rag_context = "(No relevant knowledge retrieved this round.)"
        template = load_prompt("examples.EchoChamber.Rag.prompts:RAG_USER_TEMPLATE")
        return template.format(
            round=round_num,
            polarization=polarization,
            prev_polarization=prev_polarization,
            polarization_change=polarization_change,
            mean_opinion=mean_opinion,
            cluster_separation=cluster_separation,
            cross_cutting_exposure=cross_cutting_exposure,
            num_polarizers=num_polarizers,
            num_depolarizers=num_depolarizers,
            net_polarization_intensity=net_polarization_intensity,
            my_opinion=my_opinion,
            rag_context=rag_context,
        )

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        env_data = self.state.custom_state.get("env_data", {})
        llm_client: LangChainAPIInference = self.state.custom_state["llm_client"]
        strategy_name = self.__class__.__name__
        system_prompt = load_prompt(self._system_prompt_path)
        user_prompt = self._build_prompt(env_data)
        decision = None
        for attempt in range(3):
            try:
                infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
                infer_output = llm_client.run([infer_input])
                decision = parse_llm_response_with_thinking(
                    infer_output.outputs[0].response
                )
                break
            except Exception as exc:  # pylint: disable=broad-except
                logger.warning(
                    "[%s] LLM attempt %d failed: %s", self.identity, attempt + 1, exc
                )
                if attempt == 2:
                    decision = None
        if decision is None:
            action = {
                "action_type": "neutral",
                "intensity": 0.0,
                "agent_role": strategy_name,
                "agent_id": self.identity,
                "opinion": self.state.custom_state["my_opinion"],
                "reasoning": "LLM failed: stayed neutral",
                "analysis": "",
            }
            return {
                **action,
                "outbound_messages": [
                    {"payload": action, "content_type": "social_action"}
                ],
            }
        action_type = decision.get("action_type", "neutral")
        intensity = float(decision.get("intensity", 0.0))
        intensity = self._apply_intensity_constraints(intensity)
        my_opinion = self.state.custom_state["my_opinion"]
        if action_type == "polarize":
            shift = 0.05 * (1 if my_opinion >= 0 else -1)
            my_opinion += shift
        elif action_type == "depolarize":
            my_opinion *= 0.95
        my_opinion = self._clamp_opinion(my_opinion)
        self.state.custom_state["my_opinion"] = my_opinion
        logger.debug(
            "[%s] R%s (%s): A=%s I=%.3f opinion=%.3f",
            self.identity,
            round_num,
            strategy_name,
            action_type,
            intensity,
            my_opinion,
        )
        action = {
            "action_type": action_type,
            "intensity": intensity,
            "agent_role": strategy_name,
            "agent_id": self.identity,
            "opinion": my_opinion,
            "reasoning": str(decision.get("reasoning", ""))[:120],
            "analysis": decision.get("analysis", ""),
        }
        return {
            **action,
            "outbound_messages": [{"payload": action, "content_type": "social_action"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="social_action",
            payload=decision_payload,
            source_id=self.identity,
        )


class RagLLMIdeologue(RagLLMSocialAgent):
    """RAG-augmented ideologue: strong opinion holder."""

    _system_prompt_path = "examples.EchoChamber.Rag.prompts:RAG_IDEOLOGUE_SYS"


class RagLLMConformist(RagLLMSocialAgent):
    """RAG-augmented conformist: social group aligner."""

    _system_prompt_path = "examples.EchoChamber.Rag.prompts:RAG_CONFORMIST_SYS"


class RagLLMCriticalThinker(RagLLMSocialAgent):
    """RAG-augmented critical thinker: evidence evaluator."""

    _system_prompt_path = "examples.EchoChamber.Rag.prompts:RAG_CRITICAL_SYS"


class RagLLMBridgeBuilder(RagLLMSocialAgent):
    """RAG-augmented bridge builder: cross-group engager."""

    _system_prompt_path = "examples.EchoChamber.Rag.prompts:RAG_BRIDGE_SYS"


class RagLLMPassiveFollower(RagLLMSocialAgent):
    """RAG-augmented passive follower: low-engagement participant."""

    _system_prompt_path = "examples.EchoChamber.Rag.prompts:RAG_PASSIVE_SYS"


__all__ = [
    "OpinionEnvironment",
    "RagLLMSocialAgent",
    "RagLLMIdeologue",
    "RagLLMConformist",
    "RagLLMCriticalThinker",
    "RagLLMBridgeBuilder",
    "RagLLMPassiveFollower",
]
