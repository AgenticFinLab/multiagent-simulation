"""EchoChamber Rag — RAG-augmented LLM simulation of echo chamber polarization dynamics."""

from __future__ import annotations

import importlib
import json
import logging
import math
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.utils.llm_utils import is_retryable_llm_error
from masim.knowledge import (
    KnowledgeLoader,
    KnowledgeQuery,
    KnowledgeStore,
    ResourceManager,
)
from masim.player.base import Action, Observation
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

# Re-exported for use by callers who import from this module
from examples.EchoChamber.Rule.players import OpinionEnvironment

logger = logging.getLogger(__name__)

_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def _parse_echo_chamber_response(response_text: str) -> Dict[str, Any]:
    """Parse the canonical tagged EchoChamber decision contract."""
    analysis_match = re.search(r"<analysis>(.*?)</analysis>", response_text, re.DOTALL)
    decision_match = re.search(r"<decision>(.*?)</decision>", response_text, re.DOTALL)
    if analysis_match is None or not analysis_match.group(1).strip():
        raise ValueError("Missing or empty <analysis> section")
    if decision_match is None or not decision_match.group(1).strip():
        raise ValueError("Missing or empty <decision> section")

    analysis = analysis_match.group(1).strip()
    decision_json = decision_match.group(1).strip()
    try:
        parsed = json.loads(decision_json)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Failed to parse decision JSON: {decision_json[:100]}"
        ) from exc
    if not isinstance(parsed, dict):
        raise ValueError("Decision payload must be a JSON object")

    required_fields = ["action_type", "intensity", "reasoning"]
    missing = [f for f in required_fields if f not in parsed or parsed[f] is None]
    if missing:
        raise ValueError(f"Fields missing or null in LLM response: {missing}")
    extra = sorted(set(parsed) - set(required_fields))
    if extra:
        raise ValueError(f"Unexpected decision fields: {extra}")
    action_type = str(parsed["action_type"]).lower()
    if action_type not in {"polarize", "neutral", "depolarize"}:
        raise ValueError(f"Invalid action_type: {parsed['action_type']!r}")
    if isinstance(parsed["intensity"], bool):
        raise ValueError(f"Invalid intensity: {parsed['intensity']!r}")
    try:
        intensity = float(parsed["intensity"])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid intensity: {parsed['intensity']!r}") from exc
    if not math.isfinite(intensity) or not 0.0 <= intensity <= 1.0:
        raise ValueError(f"Intensity outside [0, 1]: {intensity!r}")
    if not isinstance(parsed["reasoning"], str):
        raise ValueError("Reasoning must be a string")
    reasoning = parsed["reasoning"].strip()
    if not reasoning:
        raise ValueError("Empty reasoning")

    parsed["action_type"] = action_type
    parsed["intensity"] = intensity
    parsed["reasoning"] = reasoning
    parsed["analysis"] = analysis
    return parsed


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
        project_root = Path(__file__).resolve().parents[3]
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
        await self._initialize_rag()

    async def _initialize_rag(self) -> None:
        extras = self.config.extras
        record_path = extras["record_path"]
        knowledge_config = extras["knowledge"]
        if not knowledge_config:
            raise ValueError(f"[{self.identity}] extras.knowledge must not be empty")
        resource_manager = ResourceManager(knowledge_config)
        private_knowledge = extras["private_knowledge"]
        if not private_knowledge:
            raise ValueError(
                f"[{self.identity}] extras.private_knowledge must not be empty"
            )
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
        embed_type = resolved_rag["embed_type"]
        embed_api_key = resolved_rag["embed_api_key"]
        if not embed_api_key:
            embed_api_key = (
                os.getenv("HUNYUAN_API_KEY", "")
                if embed_type == "litellm"
                else os.getenv("ARK_API_KEY", "")
            )
        rag_store = KnowledgeStore(
            embed_model_name=resolved_rag["embed_model"],
            embed_api_key=embed_api_key,
            embed_api_base=resolved_rag["embed_api_base"],
            embed_type=embed_type,
            persist_dir=local_rag_dir,
            chunk_size=int(resolved_rag["chunk_size"]),
            chunk_overlap=int(resolved_rag["chunk_overlap"]),
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
                except Exception as exc:
                    logger.warning(
                        "[%s] Local index load failed: %s", self.identity, exc
                    )
        shared_rag_dirs = resolved_rag["shared_rag_index_dirs"]
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
                    except Exception as exc:
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
        except Exception as exc:
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
                local_rag_dir = rag_cfg["local_index_dir"]
                if not local_rag_dir:
                    local_ws = rag_cfg["local_workspace_dir"]
                    if local_ws:
                        local_rag_dir = os.path.join(local_ws, "rag_index")
                if not local_rag_dir:
                    return
                embed_type = rag_cfg["embed_type"]
                embed_api_key = rag_cfg["embed_api_key"]
                if not embed_api_key:
                    embed_api_key = (
                        os.getenv("HUNYUAN_API_KEY", "")
                        if embed_type == "litellm"
                        else os.getenv("ARK_API_KEY", "")
                    )
                rag_store = KnowledgeStore(
                    embed_model_name=rag_cfg["embed_model"],
                    embed_api_key=embed_api_key,
                    embed_api_base=rag_cfg["embed_api_base"],
                    embed_type=embed_type,
                    persist_dir=local_rag_dir,
                    chunk_size=int(rag_cfg["chunk_size"]),
                    chunk_overlap=int(rag_cfg["chunk_overlap"]),
                )
                if os.path.isdir(local_rag_dir):
                    try:
                        rag_store.load(local_rag_dir)
                    except Exception as exc:
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
        round_num = self.state.custom_state["round"]
        polarization = env_data["polarization"]
        prev_polarization = env_data["prev_polarization"]
        polarization_change = env_data["polarization_change"]
        mean_opinion = env_data["mean_opinion"]
        cluster_separation = env_data["cluster_separation"]
        cross_cutting_exposure = env_data["cross_cutting_exposure"]
        num_polarizers = env_data["num_polarizers"]
        num_depolarizers = env_data["num_depolarizers"]
        net_polarization_intensity = env_data["net_polarization_intensity"]
        rag_store: Optional[KnowledgeStore] = self.state.custom_state["rag_store"]
        rag_cfg: Dict[str, Any] = self.state.custom_state["rag_cfg"]
        rag_context = ""
        rag_query_disabled = self.state.custom_state.get("rag_query_disabled", False)
        if not rag_query_disabled and rag_store.is_built():
            top_k = rag_cfg["top_k"]
            query = KnowledgeQuery(
                text=(
                    f"echo chamber polarization: opinion={my_opinion:.2f}, "
                    f"polarization={polarization:.3f}, cluster_separation={cluster_separation:.3f}"
                ),
                top_k=top_k,
                round_num=round_num,
                agent_id=self.config.identity,
            )
            try:
                result = rag_store.query(query)
                rag_context = result.formatted_text
            except RuntimeError as exc:
                # Retrieval enriches the prompt, but it must not take down a
                # long-running simulation when an external embedding endpoint
                # is unavailable (for example an expired Ark endpoint/key).
                self.state.custom_state["rag_query_disabled"] = True
                logger.warning(
                    "[%s] RAG retrieval failed; using fallback context for the "
                    "rest of this actor's run: %s",
                    self.identity,
                    exc,
                )
        if not rag_context:
            rag_context = _RAG_FALLBACK
        self.state.custom_state["last_rag_context"] = rag_context
        template = load_prompt(self.config.extras["llm"]["user_message"])
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
        env_data = self.state.custom_state["env_data"]
        llm_client: LangChainAPIInference = self.state.custom_state["llm_client"]
        strategy_name = self.__class__.__name__
        llm_config = self.config.extras["llm"]
        configured_system_prompt = llm_config["sys_message"]
        if configured_system_prompt != self._system_prompt_path:
            raise ValueError(
                f"[{self.identity}] sys_message does not match the role prompt: "
                f"{configured_system_prompt!r} != {self._system_prompt_path!r}"
            )
        system_prompt = load_prompt(configured_system_prompt)
        user_prompt = self._build_prompt(env_data)
        max_retries = int(llm_config["max_retries"])
        if max_retries < 1:
            raise ValueError("extras.llm.max_retries must be at least 1")
        decision = None
        last_error: Optional[Exception] = None
        for attempt in range(max_retries):
            try:
                infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
                infer_output = llm_client.run([infer_input])
                decision = _parse_echo_chamber_response(infer_output.response)
                break
            except Exception as exc:
                last_error = exc
                parse_error = isinstance(exc, (ValueError, KeyError))
                retryable_api_error = is_retryable_llm_error(exc)
                if not parse_error and not retryable_api_error:
                    raise
                logger.warning(
                    "[%s] LLM attempt %d failed: %s", self.identity, attempt + 1, exc
                )
        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM failed after {max_retries} attempts: {last_error}"
            )
        action_type = decision["action_type"]
        intensity = float(decision["intensity"])
        intensity = self._apply_intensity_constraints(intensity)
        reasoning = str(decision.pop("reasoning"))
        analysis = str(decision.pop("analysis"))
        my_opinion = self.state.custom_state["my_opinion"]
        if action_type == "polarize":
            direction = 1 if my_opinion >= 0 else -1
            polarize_step = float(self.config.extras["polarize_opinion_step"])
            my_opinion += polarize_step * intensity * direction
        elif action_type == "depolarize":
            depolarize_step = float(self.config.extras["depolarize_opinion_step"])
            my_opinion *= 1.0 - depolarize_step * intensity
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
            "reasoning": reasoning,
            "analysis": analysis,
            "rag_context": self.state.custom_state["last_rag_context"],
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
    """RAG-augmented ideologue — in-group amplification with literature context. Theory: simulation-bases.md §4.1."""

    _system_prompt_path = "examples.EchoChamber.Rag.prompts:RAG_IDEOLOGUE_SYS"


class RagLLMConformist(RagLLMSocialAgent):
    """RAG-augmented conformist — group alignment with social conformity literature. Theory: simulation-bases.md §4.2."""

    _system_prompt_path = "examples.EchoChamber.Rag.prompts:RAG_CONFORMIST_SYS"


class RagLLMCriticalThinker(RagLLMSocialAgent):
    """RAG-augmented critical thinker — evidence evaluation with persuasive-arguments literature. Theory: simulation-bases.md §4.3."""

    _system_prompt_path = "examples.EchoChamber.Rag.prompts:RAG_CRITICAL_SYS"


class RagLLMBridgeBuilder(RagLLMSocialAgent):
    """RAG-augmented bridge builder — cross-group engagement with deliberative democracy literature. Theory: simulation-bases.md §4.4."""

    _system_prompt_path = "examples.EchoChamber.Rag.prompts:RAG_BRIDGE_SYS"


class RagLLMPassiveFollower(RagLLMSocialAgent):
    """RAG-augmented passive follower — low-engagement drift with mass communication literature. Theory: simulation-bases.md §4.5."""

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
