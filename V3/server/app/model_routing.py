import os
import random
from pathlib import Path

import openai
import yaml

ROUTING_PATH = Path(__file__).resolve().parent.parent / "model_routing.yaml"

with open(ROUTING_PATH) as f:
    _ROUTING = yaml.safe_load(f)

MODELS = _ROUTING["models"]
DEFAULTS = _ROUTING["defaults"]

# Model aliases that support OpenRouter's JSON mode (response_format:
# json_object) — forces the response to be a valid JSON object instead of
# relying on regex-extracting the first {...} block from free-form text.
JSON_MODE_MODELS = {"mistral-medium", "mistral-small"}


# List of selectable model aliases, for populating dropdowns client-side.
def list_models() -> list[str]:
    return list(MODELS.keys())


# Resolve a temperature range (e.g. [0.8, 1.0]) to a single sampled value.
def _resolve_params(config: dict) -> dict:
    resolved = {}
    for k, v in config.items():
        if isinstance(v, list) and len(v) == 2:
            resolved[k] = random.uniform(v[0], v[1])
        else:
            resolved[k] = v
    return resolved


# Calls the given model alias via OpenRouter with a system/user prompt pair.
# reasoning=True asks OpenRouter to enable extended thinking for models that
# support it (ignored by OpenRouter for models that don't). max_tokens
# overrides the model's own configured cap (see MODELS[alias]["max_tokens"])
# — pass this when a specific pipeline step's expected output is larger than
# what the model's default budget covers (e.g. init_outline, whose beats can
# add up to far more tokens than a single-object step like init_novel).
def call_model(
    alias: str,
    system_prompt: str,
    user_prompt: str,
    reasoning: bool = False,
    max_tokens: int | None = None,
) -> str:
    if alias not in MODELS:
        raise ValueError(f"Unknown model alias: {alias}")
    config = _resolve_params(MODELS[alias])
    # max_tokens is the step's request; the model's own max_tokens_ceiling (or
    # max_tokens when no ceiling is configured) is the hard limit. A step may
    # raise the budget above the everyday default for steps that genuinely
    # emit more (init_outline), but never above what the model can actually
    # produce — asking for more than that doesn't buy headroom, it just lets
    # the response run until the provider cuts it off mid-JSON.
    ceiling = config.get("max_tokens_ceiling", config["max_tokens"])
    token_budget = min(max_tokens, ceiling) if max_tokens else config["max_tokens"]

    client = openai.OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
    )

    kwargs = {}
    if alias in JSON_MODE_MODELS:
        kwargs["response_format"] = {"type": "json_object"}
    if reasoning:
        kwargs["extra_body"] = {"reasoning": {"effort": "medium"}}

    try:
        response = client.chat.completions.create(
            model=config["model"],
            max_tokens=token_budget,
            temperature=config["temperature"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            **kwargs,
        )
    except Exception as e:
        raise RuntimeError(f"OpenRouter API error ({alias}): {e}") from e

    choice = response.choices[0]
    if choice.finish_reason == "length":
        raise RuntimeError(
            f"{alias} response was truncated (finish_reason='length', max_tokens={token_budget})"
        )
    return choice.message.content
