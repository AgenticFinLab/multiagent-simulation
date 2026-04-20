"""DispositionEffect Rag prompts - reuses RuleLLM prompts with RAG augmentation."""

from examples.DispositionEffect.RuleLLM.prompts import (
    RULELLM_DISPOSITION_BIASED_SYS,
    RULELLM_RATIONAL_SYS,
    RULELLM_TAX_AWARE_SYS,
    RULELLM_INSTITUTIONAL_SYS,
    RULELLM_LOSS_AVERSE_SYS,
    LLM_USER_TEMPLATE,
)

# RAG agents use the same prompts as RuleLLM, but with additional
# knowledge context injected at runtime from the RAG retrieval
