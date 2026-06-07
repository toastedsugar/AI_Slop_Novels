import os
import random
import yaml
from utils.api_calls import generate_openai, generate_claude, generate_openrouter

ROUTING_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "model_routing.yaml")

def _resolve_params(config):
    resolved = {}
    for k, v in config.items():
        if isinstance(v, list) and len(v) == 2:
            resolved[k] = random.uniform(v[0], v[1])
        else:
            resolved[k] = v
    return resolved

def generate_from_config(config, system_prompt, user_prompt):
    provider = config["provider"]
    model = config["model"]
    params = {k: v for k, v in config.items() if k not in ("provider", "model")}
    if provider == "anthropic":
        return generate_claude(model, system_prompt, user_prompt, **params)
    elif provider == "openai":
        return generate_openai(model, system_prompt, user_prompt, **params)
    elif provider == "openrouter":
        return generate_openrouter(model, system_prompt, user_prompt, **params)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def load_routing():
    env = os.environ.get("ENV", "dev")
    with open(ROUTING_PATH) as f:
        routing = yaml.safe_load(f)
    assert env in routing, f"ENV='{env}' not found in model_routing.yaml"
    models = routing["models"]
    tasks = routing[env]
    return {task: _resolve_params(models[alias]) for task, alias in tasks.items()}
