import os
import random
from pathlib import Path

import anthropic
import openai
import yaml

ROUTING_PATH = Path(__file__).resolve().parent.parent / "model_routing.yaml"

with open(ROUTING_PATH) as f:
    _ROUTING = yaml.safe_load(f)

MODELS = _ROUTING["models"]
DEFAULTS = _ROUTING["defaults"]

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


# Calls the given model alias with a system/user prompt pair, dispatching to
# the Anthropic SDK directly for provider: anthropic entries and to
# OpenRouter for everything else (including entries with no provider key, for
# backward compatibility with the original OpenRouter-only routing file).
# reasoning=True asks for extended thinking on models that support it.
# max_tokens overrides the model's own configured cap (see
# MODELS[alias]["max_tokens"]) — pass this when a specific pipeline step's
# expected output is larger than what the model's default budget covers (e.g.
# init_outline, whose beats can add up to far more tokens than a
# single-object step like init_novel).
def call_model(
    alias: str,
    system_prompt: str,
    user_prompt: str,
    reasoning: bool = False,
    max_tokens: int | None = None,
    json_mode: bool = True,
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

    if config.get("provider") == "anthropic":
        return _call_anthropic(alias, config, system_prompt, user_prompt, token_budget, ceiling, reasoning)
    return _call_openrouter(alias, config, system_prompt, user_prompt, token_budget, ceiling, reasoning, json_mode)


# Calls the given model alias via OpenRouter with a system/user prompt pair.
# reasoning=True asks OpenRouter to enable extended thinking for models that
# support it (ignored by OpenRouter for models that don't).
def _call_openrouter(
    alias: str,
    config: dict,
    system_prompt: str,
    user_prompt: str,
    token_budget: int,
    ceiling: int,
    reasoning: bool,
    json_mode: bool,
) -> str:
    client = openai.OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
    )

    # Every model in model_routing.yaml supports OpenRouter's JSON mode
    # (verified against the /models endpoint's supported_parameters), and
    # every structured pipeline step wants a JSON object back — so ask for
    # one by default. Without it a model is free to wrap the object in prose
    # or append a sign-off, which _extract_json then has to guess its way
    # through. json_mode=False opts out for calls that want plain prose back
    # (chapter generation/editing) — forcing free-text creative writing
    # through the JSON-object constraint measurably hurts long prose output,
    # since the model starts treating the wrapper as a structural limit on
    # the writing itself (escaped quotes/newlines inside a string field).
    kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}
    if reasoning:
        kwargs["extra_body"] = {"reasoning": {"effort": "medium"}}

    # Prompt caching. Most providers (grok, qwen, deepseek) cache automatically
    # on an exact prefix match and need nothing sent; Anthropic-style models
    # require an explicit cache_control breakpoint instead. `cache: true` in
    # model_routing.yaml opts a model into the explicit form. Either way what
    # actually earns the discount is prefix stability — SYSTEM_PROMPT keeps all
    # its fixed text above {intro_prompt}, and every step serializes shared
    # context identically (see generation._worldbuilding_json).
    system_content = system_prompt
    if config.get("cache"):
        system_content = [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ]

    # A step's max_tokens is an estimate, and some novels genuinely produce
    # more (a bigger cast, a denser outline) than that estimate covers. Rather
    # than fail the whole pipeline the first time a response gets cut off
    # mid-JSON, keep doubling the budget and retrying — capped at the model's
    # ceiling — before giving up. This used to stop after a single doubling
    # regardless of how far below the ceiling that landed (e.g. a 16000
    # default doubling to 32000 against a 450000 ceiling), which failed
    # permanently on any step whose real output sat above the second attempt.
    attempt_budget = token_budget
    while True:
        try:
            response = client.chat.completions.create(
                model=config["model"],
                max_tokens=attempt_budget,
                temperature=config["temperature"],
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_prompt},
                ],
                **kwargs,
            )
        except Exception as e:
            raise RuntimeError(f"OpenRouter API error ({alias}): {e}") from e

        # Cached-token count, logged so cache effectiveness is observable — a
        # run where this stays 0 after the first call means the prefix is
        # being broken somewhere (usually key ordering or whitespace in a
        # serialized block).
        usage = getattr(response, "usage", None)
        details = getattr(usage, "prompt_tokens_details", None)
        cached = getattr(details, "cached_tokens", None) if details else None
        if usage is not None:
            print(
                f"[{alias}] prompt_tokens={getattr(usage, 'prompt_tokens', '?')} "
                f"cached_tokens={cached if cached is not None else 0}",
                flush=True,
            )

        choice = response.choices[0]
        if choice.finish_reason != "length":
            content = choice.message.content
            if not content:
                raise RuntimeError(
                    f"{alias} returned an empty response (finish_reason="
                    f"{choice.finish_reason!r}) — the provider gave back no usable text"
                )
            return content

        if attempt_budget >= ceiling:
            break
        next_budget = min(attempt_budget * 2, ceiling)
        print(
            f"[{alias}] response truncated at max_tokens={attempt_budget}, "
            f"retrying with max_tokens={next_budget}",
            flush=True,
        )
        attempt_budget = next_budget

    raise RuntimeError(
        f"{alias} response was truncated (finish_reason='length') even after "
        f"doubling the token budget toward its ceiling of {ceiling}"
    )


# Calls the given model alias via the Anthropic API directly (ANTHROPIC_API_KEY).
# reasoning=True enables adaptive thinking, which every current Claude model
# (5-family and 4.6+) supports via the same {"type": "adaptive"} config —
# there's no fixed budget_tokens to tune per model. Streamed unconditionally
# since max_tokens here can reach the 128K ceiling, which risks the SDK's
# 10-minute non-streaming request timeout.
def _call_anthropic(
    alias: str,
    config: dict,
    system_prompt: str,
    user_prompt: str,
    token_budget: int,
    ceiling: int,
    reasoning: bool,
) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    kwargs = {}
    if reasoning:
        kwargs["thinking"] = {"type": "adaptive"}
    # temperature/top_p/top_k are no longer accepted as direct messages.create()
    # kwargs on anthropic>=1.0 (Opus 5/4.7+ and Sonnet 5 400 on them regardless
    # of how they're sent). Sonnet 4.6 and Haiku 4.5 still honor the setting,
    # so pass it via extra_body — the one form the 1.x SDK still forwards —
    # only for models that actually accept it.
    elif config["model"] in ("claude-sonnet-4-6", "claude-haiku-4-5"):
        kwargs["extra_body"] = {"temperature": config["temperature"]}

    # Explicit cache_control breakpoint — same prefix-stability contract as
    # the OpenRouter `cache: true` path (see _call_openrouter above): the
    # SYSTEM_PROMPT's fixed text must stay above {intro_prompt} for this to
    # actually earn a cache hit.
    system_content = [
        {"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}
    ]

    attempt_budget = token_budget
    while True:
        try:
            with client.messages.stream(
                model=config["model"],
                max_tokens=attempt_budget,
                system=system_content,
                messages=[{"role": "user", "content": user_prompt}],
                **kwargs,
            ) as stream:
                response = stream.get_final_message()
        except Exception as e:
            raise RuntimeError(f"Anthropic API error ({alias}): {e}") from e

        usage = response.usage
        cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
        print(
            f"[{alias}] prompt_tokens={usage.input_tokens} cached_tokens={cache_read}",
            flush=True,
        )

        if response.stop_reason != "max_tokens":
            text = next((b.text for b in response.content if b.type == "text"), None)
            if not text:
                raise RuntimeError(
                    f"{alias} returned an empty response (stop_reason="
                    f"{response.stop_reason!r}) — the provider gave back no usable text"
                )
            return text

        if attempt_budget >= ceiling:
            break
        next_budget = min(attempt_budget * 2, ceiling)
        print(
            f"[{alias}] response truncated at max_tokens={attempt_budget}, "
            f"retrying with max_tokens={next_budget}",
            flush=True,
        )
        attempt_budget = next_budget

    raise RuntimeError(
        f"{alias} response was truncated (stop_reason='max_tokens') even after "
        f"doubling the token budget toward its ceiling of {ceiling}"
    )
