import os
import json
from typing import List
from app_layer.registries.generic_registry import EntityManifest
from app_layer.registries.specs import ChoiceParamSpec
from .basic_agent import BasicAgent
from agent_layer.llm_agents.LLMs.llm_selector import list_available_llms

def _get_available_prompt_ids() -> List[str]:
    """
    Helper function to dynamically extract prompt IDs from the local JSON file.
    
    Returns:
        List[str]: A list of keys found in system_prompts.json.
    """
    try:
        current_dir = os.path.dirname(__file__)
        prompt_path = os.path.join(current_dir, "system_prompts.json")
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return list(data.keys())
    except Exception:
        pass
    return ["check_hypothesis"]

# The discovery system will find this instance and register it automatically
llms_list = list_available_llms()
prompt_ids = _get_available_prompt_ids()
manifest = EntityManifest(
    id="basic_agent",
    display_name="Basic LLM Agent",
    cls=BasicAgent,
    description=(
        "A simple LLM Agent that uses a message history and "
        "a predefined system prompt to guide its reasoning."
    ),
    params=[
        ChoiceParamSpec(
            id="model_name",
            label="LLM Model",
            description="The backend model providing the reasoning capabilities.",
            choices=llms_list,
            default=llms_list[0]
        ),
        ChoiceParamSpec(
            id="system_prompt_id",
            label="Reasoning Strategy",
            description="The system prompt identity defined in system_prompts.json.",
            choices=prompt_ids,
            default=prompt_ids[0]
        )
    ]
)