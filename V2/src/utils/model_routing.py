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

def _extract_reasoning(config, provider):
    """Pops the reasoning block and returns extra kwargs to inject if enabled."""
    reasoning = config.pop("reasoning", None)
    if not reasoning or not reasoning.get("enabled"):
        return {}
    if provider == "anthropic":
        return {"thinking": {"type": "enabled", "budget_tokens": reasoning.get("budget_tokens", 2000)}}
    if provider == "openai":
        return {"reasoning": {"effort": reasoning.get("effort", "low")}}
    if provider == "openrouter":
        # OpenRouter passes thinking via extra_body for supporting models
        return {"extra_body": {"reasoning": {"effort": reasoning.get("effort", "medium")}}}
    return {}


def generate_from_config(config, system_prompt, user_prompt):
    """Returns (text, input_tokens, output_tokens, cache_read_tokens, cache_created_tokens)."""
    provider = config["provider"]
    model = config["model"]
    params = {k: v for k, v in config.items() if k not in ("provider", "model", "input_price_per_1m", "output_price_per_1m")}
    extra = _extract_reasoning(params, provider)
    params.update(extra)
    if provider == "anthropic":
        return generate_claude(model, system_prompt, user_prompt, **params)
    elif provider == "openai":
        text, inp, out = generate_openai(model, system_prompt, user_prompt, **params)
        return text, inp, out, 0, 0
    elif provider == "openrouter":
        text, inp, out = generate_openrouter(model, system_prompt, user_prompt, **params)
        return text, inp, out, 0, 0
    else:
        raise ValueError(f"Unknown provider: {provider}")


def calculate_cost(config, input_tokens, output_tokens):
    """Returns total cost in USD given token counts and per-million pricing from config."""
    input_price = config.get("input_price_per_1m", 0.0)
    output_price = config.get("output_price_per_1m", 0.0)
    return (input_tokens * input_price + output_tokens * output_price) / 1_000_000


def load_routing():
    env = os.environ.get("ENV", "dev")
    with open(ROUTING_PATH) as f:
        routing = yaml.safe_load(f)
    assert env in routing, f"ENV='{env}' not found in model_routing.yaml"
    models = routing["models"]
    tasks = routing[env]
    return {task: _resolve_params(models[alias]) for task, alias in tasks.items()}
