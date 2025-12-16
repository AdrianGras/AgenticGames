from typing import List, Type
from agent_layer.llm_agents.LLMs.general_llm import GeneralLLM
from agent_layer.llm_agents.LLMs.grok_llm import GrokLLM
from agent_layer.llm_agents.LLMs.openai_llm import OpenAILLM

# Registry mapping model identifiers to their implementation classes.
# This acts as the configuration center for supported models.
MODELS: dict[str, Type[GeneralLLM]] = {
    # OpenAI Models
    "gpt-4.1": OpenAILLM,
    "gpt-5": OpenAILLM,
    
    # xAI (Grok) Models
    "grok-4": GrokLLM,
    "grok-4-1-fast": GrokLLM,
    "grok-4-1-fast-non-reasoning": GrokLLM,
}

def get_llm(model_name: str) -> GeneralLLM:
    """
    Factory function: Returns an instantiated LLM client based on the model name.
    
    Args:
        model_name (str): The specific model identifier (e.g., 'gpt-4'). 
                          It is case-insensitive.

    Returns:
        GeneralLLM: An instance of the LLM class configured for the requested model.

    Raises:
        ValueError: If the model name is not in the supported list.
    """
    # Normalize input to ensure case-insensitivity
    normalized_name = model_name.lower().strip()

    if normalized_name not in MODELS:
        available = ", ".join(list_available_llms())
        raise ValueError(
            f"Model '{model_name}' is not supported. "
            f"Available models: {available}"
        )
    
    llm_class = MODELS[normalized_name]
    
    return llm_class(model_name=normalized_name)

def list_available_llms() -> List[str]:
    """
    Returns a list of all supported LLM model identifiers.
    """
    return list(MODELS.keys())