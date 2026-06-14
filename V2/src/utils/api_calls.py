import os
import openai
import anthropic
from google import genai
from google.genai import types


def generate_openai(
    model,
    system_prompt,
    user_prompt,
    seed=None,
    reasoning=None,
    text=None,
):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    kwargs = {}
    if reasoning is not None:
        kwargs["reasoning"] = reasoning
    if text is not None:
        kwargs["text"] = text
    if seed is not None:
        kwargs["seed"] = seed
    try:
        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            **kwargs,
        )
        if response.output_text is None:
            raise RuntimeError(f"OpenAI API returned None output_text for model {model}")
        usage = response.usage
        return response.output_text, usage.input_tokens, usage.output_tokens
    except Exception as e:
        raise RuntimeError(f"OpenAI API Error: {e}") from e

def generate_claude(
    model,
    system_prompt,
    user_prompt,
    max_tokens=8192,
    temperature=None,
    top_p=None,
    top_k=None,
    stop_sequences=None,
    thinking=None,
):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    kwargs = {}
    if thinking is not None:
        # thinking and temperature are mutually exclusive
        kwargs["thinking"] = thinking
    else:
        if temperature is not None:
            kwargs["temperature"] = temperature
    if top_p is not None:
        kwargs["top_p"] = top_p
    if top_k is not None:
        kwargs["top_k"] = top_k
    if stop_sequences is not None:
        kwargs["stop_sequences"] = stop_sequences

    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            **kwargs,
        )
        usage = response.usage
        text = next(b.text for b in response.content if b.type == "text")
        return text, usage.input_tokens, usage.output_tokens

    except Exception as e:
        raise RuntimeError(f"Anthropic API Error: {e}") from e


def generate_gemini(
    model,
    system_prompt,
    user_prompt,
    max_output_tokens=8192,
    temperature=None,
    top_p=None,
    top_k=None,
    stop_sequences=None,
    seed=None,
    candidate_count=None,
):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        stop_sequences=stop_sequences,
        seed=seed,
        candidate_count=candidate_count,
    )
    try:
        response = client.models.generate_content(
            model=model,
            contents=user_prompt,
            config=config,
        )
        usage = response.usage_metadata
        return response.text, usage.prompt_token_count, usage.candidates_token_count

    except Exception as e:
        raise RuntimeError(f"Gemini API Error: {e}") from e


def generate_openrouter(
    model,
    system_prompt,
    user_prompt,
    max_tokens=8192,
    temperature=None,
    top_p=None,
    extra_body=None,
):
    client = openai.OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
    )
    kwargs = {}
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if temperature is not None:
        kwargs["temperature"] = temperature
    if top_p is not None:
        kwargs["top_p"] = top_p
    if extra_body is not None:
        # extra_body is merged into the raw JSON request — used to pass reasoning params
        # for models that support it (e.g. {"reasoning": {"effort": "medium"}})
        kwargs["extra_body"] = extra_body
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            **kwargs,
        )
        choice = response.choices[0]
        content = choice.message.content
        if content is None:
            finish_reason = choice.finish_reason
            refusal = getattr(choice.message, "refusal", None)
            raise RuntimeError(
                f"OpenRouter API returned None content for model {model} "
                f"(finish_reason={finish_reason!r}, refusal={refusal!r})"
            )
        usage = response.usage
        return content, usage.prompt_tokens, usage.completion_tokens
    except Exception as e:
        raise RuntimeError(f"OpenRouter API Error: {e}") from e
