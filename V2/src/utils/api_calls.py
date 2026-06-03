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
        return response.output_text
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
):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    kwargs = {}
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
        return response.content[0].text

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
        return response.text

    except Exception as e:
        raise RuntimeError(f"Gemini API Error: {e}") from e
