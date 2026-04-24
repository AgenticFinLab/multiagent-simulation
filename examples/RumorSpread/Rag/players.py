"""RumorSpreadRag — RAG-augmented Rule+LLM Rumor Propagation Simulation

Design:
    - InformationEnvironment coordinator: identical rule-based dynamics as RumorSpread.
    - Social agents: LLM-powered with two layers of augmentation:
        1. System prompt embeds explicit quantitative rules (from rule-based)
           alongside a rich persona/profile description (same as RuleLLM).
        2. At initialization, each agent builds a personal RAG library by
           loading reference documents and indexing them with the configured
           embedding API.
        3. At every decision round, the agent retrieves the top-k most
           relevant text chunks from its RAG library and injects them into
           the user prompt before calling the LLM.

This extends the three-variant comparison:
    RumorSpread        — pure rule-based
    RumorSpreadRuleLLM — LLM with rules in prompt (no external knowledge)
    RumorSpreadRag     — LLM with rules in prompt + RAG knowledge retrieval

All parameters are configured via players.yml config file.

Usage
-----
1. **Via Streamlit Web UI (Recommended):**

   ```bash
   cd /path/to/multiagent-simulation
   streamlit run masim/interface/app.py
   ```
   Then select "RumorSpreadRag" from the scenario dropdown.

2. **Command Line:**

   ```bash
   python examples/RumorSpread/Rag/run_rumor_rag.py \
       -c configs/RumorSpread/Rag/simulation.yml
   ```

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required for LLM calls)
"""

from __future__ import annotations

import json
import logging
import os
import random
import shutil
from typing import Any, Dict, List, Optional

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.knowledge import (
    KnowledgeLoader,
    KnowledgeQuery,
    KnowledgeStore,
    ResourceManager,
)
from masim.knowledge.manager import KnowledgeManager
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer
from masim.utils.llm_utils import parse_llm_response_with_thinking

from .prompts import (
    RAG_GULLIBLE_SYS,
    RAG_DISTORTING_SYS,
    RAG_SKEPTICAL_SYS,
    RAG_FACTCHECKER_SYS,
    RAG_BYSTANDER_SYS,
)

logger = logging.getLogger("RumorSpreadRag")


# =============================================================================
# InformationEnvironment — Rule-Based Coordinator (identical to Rule variant)
# =============================================================================


class InformationEnvironment(GeneralPlayer):
    """
    Central information environment tracking rumor spread dynamics.

    Rumor Belief Model:
        B(t+1) = B(t) + alpha * NetSpread + beta * (Truth - B(t)) + epsilon

    Parameters from config extras:
        - rumor_truth_value, initial_belief, spread_impact, truth_correction
        - leveling_rate, sharpening_rate, noise_std, custom_state_hot_limit
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "belief" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["belief"] = extras["initial_belief"]
            self.state.custom_state["distortion"] = 0.0
            self.state.custom_state["truth_value"] = extras["rumor_truth_value"]

            hot_limit = extras["custom_state_hot_limit"]
            self.state.custom_state["belief_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "belief"),
                entry_limit=hot_limit,
            )
            self.state.custom_state["distortion_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "distortion"),
                entry_limit=hot_limit,
            )
            self.state.custom_state["spread_count_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "spread_count"),
                entry_limit=hot_limit,
            )
            self.state.custom_state["correction_count_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "correction_count"),
                entry_limit=hot_limit,
            )

        actions = []
        if observation.inbounds:
            for inb in observation.inbounds:
                action = inb.payload
                actions.append(
                    {
                        "agent_id": inb.sender_id,
                        "action_type": action["action_type"],
                        "intensity": action["intensity"],
                        "agent_role": action["agent_role"],
                    }
                )
        self.state.custom_state["actions"] = actions

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_belief = self.state.custom_state["belief"]
        current_distortion = self.state.custom_state["distortion"]
        truth_value = self.state.custom_state["truth_value"]
        actions = self.state.custom_state["actions"]

        spread_actions = [a for a in actions if a["action_type"] == "spread"]
        correct_actions = [a for a in actions if a["action_type"] == "correct"]

        total_spread = sum(a["intensity"] for a in spread_actions)
        total_correction = sum(a["intensity"] for a in correct_actions)
        net_spread = total_spread - total_correction

        spread_impact = extras["spread_impact"]
        truth_correction = extras["truth_correction"]
        leveling_rate = extras["leveling_rate"]
        sharpening_rate = extras["sharpening_rate"]
        noise_std = extras["noise_std"]

        spread_effect = spread_impact * net_spread
        truth_effect = truth_correction * (truth_value - current_belief)
        noise = random.gauss(0, noise_std)

        new_belief = max(
            0.0, min(1.0, current_belief + spread_effect + truth_effect + noise)
        )

        leveling = leveling_rate * current_distortion
        sharpening = sharpening_rate * len(spread_actions) * (1.0 - truth_value)
        new_distortion = max(0.0, min(1.0, current_distortion - leveling + sharpening))

        self.state.custom_state["belief"] = new_belief
        self.state.custom_state["distortion"] = new_distortion
        self.state.custom_state["belief_history"].append(new_belief)
        self.state.custom_state["distortion_history"].append(new_distortion)
        self.state.custom_state["spread_count_history"].append(len(spread_actions))
        self.state.custom_state["correction_count_history"].append(len(correct_actions))

        logger.debug(
            "[InfoEnv] R%d  Belief=%.3f→%.3f  Distortion=%.3f→%.3f",
            round_num,
            current_belief,
            new_belief,
            current_distortion,
            new_distortion,
        )

        env_data = {
            "belief": new_belief,
            "prev_belief": current_belief,
            "belief_change": new_belief - current_belief,
            "distortion": new_distortion,
            "truth_value": truth_value,
            "num_spreaders": len(spread_actions),
            "num_correctors": len(correct_actions),
            "net_spread_intensity": net_spread,
            "round": round_num,
        }

        return {
            "env_data": env_data,
            "outbound_messages": [
                {"payload": env_data, "content_type": "environment_update"}
            ],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="environment_broadcast",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# Base RagLLM Social Agent
# =============================================================================


class RagLLMSocialAgent(GeneralPlayer):
    """Base class for RAG-augmented Rule+LLM social agents in RumorSpread."""

    _system_prompt: str = ""

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

    def _get_llm(self) -> LangChainAPIInference:
        """Lazy-initialize LLM client."""
        llm_cfg = self.config.extras["llm"]
        self._llm = LangChainAPIInference(
            lm_name=llm_cfg["lm_name"],
            generation_config=llm_cfg["generation_config"],
        )
        return self._llm

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "my_belief" not in self.state.custom_state:
            await self._initialize_agent()

        if observation.inbounds:
            for inb in observation.inbounds:
                env_data = inb.payload
                self.state.custom_state["env_data"] = env_data
                self.state.custom_state["belief_history"].append(env_data["belief"])

    async def _initialize_agent(self) -> None:
        """One-time initialization: belief state + LLM client + RAG index."""
        extras = self.config.extras
        record_path = extras["record_path"]
        base_path = os.path.join(record_path, self.config.identity)
        hot_limit = extras["custom_state_hot_limit"]

        self.state.custom_state["my_belief"] = extras["initial_belief"]
        self.state.custom_state["credibility"] = extras["initial_credibility"]
        self.state.custom_state["belief_history"] = HistoryBuffer(
            folder=os.path.join(base_path, "belief"),
            entry_limit=hot_limit,
        )

        # LLM client for RAG initialization
        llm_client = self._get_llm()

        private_knowledge = extras["private_knowledge"]
        rag_cfg = private_knowledge.get("rag", extras.get("rag", {}))
        await self._initialize_rag(rag_cfg, llm_client, extras["llm"])

    async def _initialize_rag(
        self, rag_cfg: Dict[str, Any], llm_client: Any, llm_config: Dict[str, Any]
    ) -> None:
        """Build or load the agent's RAG index using the unified knowledge architecture."""
        extras = self.config.extras
        record_path = extras["record_path"]

        knowledge_config = extras["knowledge"]
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
                    "output_position": rag_cfg.get("shared_rag_index_dir", "rag_index"),
                },
            }

        resource_manager = ResourceManager(knowledge_config)

        private_knowledge = extras["private_knowledge"]
        if not private_knowledge:
            private_knowledge = {
                "from_global_resources": ["MinerU_processed"],
                "local_resources": {
                    "local_uri": "",
                    "local_resources": [],
                },
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

        logger.info(
            "[%s] Knowledge: processed=%s shared_rag=%s local_rag=%s",
            self.identity,
            processed_dir,
            shared_rag_dir,
            local_rag_dir,
        )

        embed_type = resolved_rag.get("embed_type", "litellm")
        embed_model = resolved_rag.get("embed_model", "openai/hunyuan-embedding")
        embed_api_base = resolved_rag.get("embed_api_base", "")
        embed_api_key = resolved_rag.get("embed_api_key", "")
        chunk_size = int(resolved_rag.get("chunk_size", 512))
        chunk_overlap = int(resolved_rag.get("chunk_overlap", 64))

        if not embed_api_key:
            if embed_type == "litellm":
                embed_api_key = os.getenv("HUNYUAN_API_KEY", "")
            elif embed_type == "openai":
                embed_api_key = os.getenv("ARK_API_KEY", "")

        rag_store = KnowledgeStore(
            embed_model_name=embed_model,
            embed_api_key=embed_api_key,
            embed_api_base=embed_api_base,
            embed_type=embed_type,
            persist_dir=local_rag_dir,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        # Try loading existing local RAG index
        if os.path.isdir(local_rag_dir):
            index_files = [
                f for f in os.listdir(local_rag_dir) if not f.startswith(".")
            ]
            if index_files:
                logger.info(
                    "[%s] Loading local RAG index from %s", self.identity, local_rag_dir
                )
                try:
                    rag_store.load(local_rag_dir)
                    self.state.custom_state["rag_store"] = rag_store
                    self.state.custom_state["rag_cfg"] = resolved_rag
                    return
                except Exception as exc:
                    logger.warning(
                        "[%s] Local index load failed (%s)", self.identity, exc
                    )

        # Try copying shared RAG index
        shared_rag_dirs = resolved_rag.get("shared_rag_index_dirs", [])
        if not shared_rag_dirs and os.path.isdir(shared_rag_dir):
            shared_rag_dirs = [shared_rag_dir]

        for s_dir in shared_rag_dirs:
            if os.path.isdir(s_dir):
                shared_files = [f for f in os.listdir(s_dir) if not f.startswith(".")]
                if shared_files:
                    logger.info(
                        "[%s] Copying shared RAG index from %s", self.identity, s_dir
                    )
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
                            "[%s] Shared index copy failed (%s)", self.identity, exc
                        )

        # Build from scratch
        loader = KnowledgeLoader()
        docs: List[Any] = []

        if os.path.isdir(processed_dir) and os.listdir(processed_dir):
            logger.info("[%s] Loading docs from %s", self.identity, processed_dir)
            docs = loader.load_from_dir(processed_dir)
        else:
            logger.error(
                "[%s] No processed documents in %s", self.identity, processed_dir
            )
            raise RuntimeError(
                f"[{self.identity}] No processed documents for RAG. "
                f"Check {processed_dir}"
            )

        logger.info("[%s] Building RAG index over %d docs", self.identity, len(docs))
        rag_store.build(docs)

        # Copy to shared location
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
            logger.warning("[%s] Failed to copy to shared: %s", self.identity, exc)

        self.state.custom_state["rag_store"] = rag_store
        self.state.custom_state["rag_cfg"] = resolved_rag

    def __getstate__(self):
        state = self.__dict__.copy()
        if "state" in state and hasattr(state["state"], "custom_state"):
            custom = dict(state["state"].custom_state)
            for key in ("llm_client", "rag_store"):
                custom.pop(key, None)
            state["state"].custom_state = custom
        return state

    def __setstate__(self, state):
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
                    local_workspace_dir = rag_cfg.get("local_workspace_dir", "")
                    if local_workspace_dir:
                        local_rag_dir = os.path.join(local_workspace_dir, "rag_index")

                if not local_rag_dir:
                    logger.warning(
                        "[%s] Cannot reconstruct RAG store: no path", self.identity
                    )
                    return

                embed_type = rag_cfg.get("embed_type", "litellm")
                embed_api_key = rag_cfg.get("embed_api_key", "")
                if not embed_api_key:
                    if embed_type == "litellm":
                        embed_api_key = os.getenv("HUNYUAN_API_KEY", "")
                    elif embed_type == "openai":
                        embed_api_key = os.getenv("ARK_API_KEY", "")

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
                    except Exception as exc:
                        logger.warning("[%s] RAG reload failed: %s", self.identity, exc)
                custom["rag_store"] = rag_store

    def _build_prompt(self, env_data: Dict[str, Any]) -> str:
        """Build user prompt with RAG context + environment state."""
        my_belief = self.state.custom_state["my_belief"]
        round_num = self.state.custom_state["round"]
        rag_store: KnowledgeStore = self.state.custom_state.get("rag_store")
        rag_cfg: Dict[str, Any] = self.state.custom_state.get("rag_cfg", {})

        # Retrieve relevant context from RAG library
        rag_context = ""
        if rag_store and rag_store.is_built():
            top_k = rag_cfg.get("top_k", 3)
            belief_level = env_data["belief"]
            distortion_level = env_data["distortion"]
            truth_value = env_data["truth_value"]

            if belief_level > 0.6:
                belief_desc = "high and rising"
            elif belief_level < 0.3:
                belief_desc = "low and contained"
            else:
                belief_desc = "moderate and contested"

            query = KnowledgeQuery(
                text=(
                    f"rumor spread strategy when: "
                    f"population_belief={belief_desc}, "
                    f"distortion={distortion_level:.2f}, "
                    f"truth={truth_value:.2f}, "
                    f"spreaders={env_data['num_spreaders']}, "
                    f"correctors={env_data['num_correctors']}"
                ),
                top_k=top_k,
                round_num=round_num,
                agent_id=self.config.identity,
            )
            result = rag_store.query(query)
            rag_context = result.formatted_text

        if not rag_context:
            rag_context = "(No relevant knowledge retrieved this round.)"

        return (
            f"Round {round_num}\n"
            f"RAG Context:\n{rag_context}\n\n"
            f"Population Belief: {env_data['belief']:.3f}  prev={env_data['prev_belief']:.3f}"
            f"  change={env_data['belief_change']:.3f}  distortion={env_data['distortion']:.3f}\n"
            f"Truth Value: {env_data['truth_value']:.3f}\n"
            f"Spreaders: {env_data['num_spreaders']}  Correctors: {env_data['num_correctors']}"
            f"  net_spread={env_data['net_spread_intensity']:.3f}\n"
            f"Your Personal Belief: {my_belief:.3f}\n"
            "Respond with <analysis>...</analysis> then "
            '<decision>{"action_type":"spread"|"ignore"|"correct","intensity":<0-1>,"reasoning":"..."}'
            "</decision>"
        )

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response with analysis and decision sections."""
        return parse_llm_response_with_thinking(response_text)

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        env_data = self.state.custom_state["env_data"]
        strategy_name = self.__class__.__name__

        user_prompt = self._build_prompt(env_data)
        system_prompt = self._system_prompt
        llm_client = self._get_llm()

        max_retries = 3
        decision = None
        last_error = None
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            infer_output = llm_client.run([infer_input])
            try:
                decision = self._parse_llm_response(infer_output.outputs[0].response)
                break
            except ValueError as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.debug("[%s] LLM parse failed, retrying...", self.identity)

        if decision is None:
            logger.warning(
                "[%s] LLM failed after %d attempts: %s",
                self.identity,
                max_retries,
                last_error,
            )
            action = {
                "action_type": "ignore",
                "intensity": 0.0,
                "agent_role": strategy_name,
                "agent_id": self.identity,
                "reasoning": "LLM parse failed",
                "analysis": "",
            }
            return {
                **action,
                "outbound_messages": [
                    {"payload": action, "content_type": "social_action"}
                ],
            }

        action_type = decision.get("action_type", "ignore")
        intensity = float(decision.get("intensity", 0.0))
        intensity = max(0.0, min(1.0, intensity))

        # Update personal belief based on action
        my_belief = self.state.custom_state["my_belief"]
        if action_type == "spread":
            my_belief = max(my_belief, env_data["belief"] * 0.5 + my_belief * 0.5)
        elif action_type == "correct":
            my_belief = min(my_belief, env_data["truth_value"] * 0.5 + my_belief * 0.5)
        my_belief = max(0.0, min(1.0, my_belief))
        self.state.custom_state["my_belief"] = my_belief

        logger.debug(
            "[%s] R%d (%s): A=%s I=%.3f belief=%.3f",
            self.identity,
            round_num,
            strategy_name,
            action_type,
            intensity,
            my_belief,
        )

        action = {
            "action_type": action_type,
            "intensity": intensity,
            "agent_role": strategy_name,
            "agent_id": self.identity,
            "reasoning": decision.get("reasoning", "")[:120],
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


# =============================================================================
# Concrete RAG+LLM Social Agent Types
# =============================================================================


class RagLLMGullibleSpreader(RagLLMSocialAgent):
    """RAG-augmented gullible spreader."""

    _system_prompt = RAG_GULLIBLE_SYS


class RagLLMDistortingRelayer(RagLLMSocialAgent):
    """RAG-augmented distorting relayer."""

    _system_prompt = RAG_DISTORTING_SYS


class RagLLMSkepticalEvaluator(RagLLMSocialAgent):
    """RAG-augmented skeptical evaluator."""

    _system_prompt = RAG_SKEPTICAL_SYS


class RagLLMFactChecker(RagLLMSocialAgent):
    """RAG-augmented fact checker."""

    _system_prompt = RAG_FACTCHECKER_SYS


class RagLLMUninformedBystander(RagLLMSocialAgent):
    """RAG-augmented uninformed bystander."""

    _system_prompt = RAG_BYSTANDER_SYS


__all__ = [
    "InformationEnvironment",
    "RagLLMSocialAgent",
    "RagLLMGullibleSpreader",
    "RagLLMDistortingRelayer",
    "RagLLMSkepticalEvaluator",
    "RagLLMFactChecker",
    "RagLLMUninformedBystander",
]
