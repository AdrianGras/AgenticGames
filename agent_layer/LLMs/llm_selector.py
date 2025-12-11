from agent_layer.LLMs.x_llm import GrokLLM
from agent_layer.LLMs.openai_llm import OpenAILLM

MODELS = {
    "gpt-4.1": OpenAILLM,
    "gpt-5": OpenAILLM,
    "grok-4": GrokLLM,
    "grok-4-1-fast": GrokLLM,
    "grok-4-1-fast-non-reasoning": GrokLLM,
}

def get_llm(model_name):
    """
    Given a model name, returns an instance of the corresponding LLM class.
    """
    if model_name not in MODELS:
        raise ValueError(f"Model '{model_name}' is not supported. Available models: {list(MODELS.keys())}")
    
    llm_class = MODELS[model_name]
    return llm_class(model_name=model_name)

def list_available_llms():
    """
    Returns a list of available LLM model names.
    """
    return list(MODELS.keys())
