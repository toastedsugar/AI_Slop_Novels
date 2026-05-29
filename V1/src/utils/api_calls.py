import os
import openai
import ollama
import anthropic
from google import genai
from google.genai import types
from xai_sdk import Client
from xai_sdk.chat import user, system


def generate_openai(
    model,
    system_prompt,
    user_prompt,
    temperature=1,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    seed=None,
):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            seed=seed,
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return None


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
        print(f"Anthropic API Error: {e}")
        return None


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
        print(f"Gemini API Error: {e}")
        return None



def generate_xai(
    model,
    system_prompt,
    user_prompt,
    temperature=None,
    top_p=None,
    seed=None,
):
    client = Client(api_key=os.getenv("XAI_API_KEY"))
    kwargs = {}
    if temperature is not None:
        kwargs["temperature"] = temperature
    if top_p is not None:
        kwargs["top_p"] = top_p
    if seed is not None:
        kwargs["seed"] = seed

    try:
        chat = client.chat.create(model=model, **kwargs)
        chat.append(system(system_prompt))
        chat.append(user(user_prompt))
        response = chat.sample()
        return response.content

    except Exception as e:
        print(f"xAI API Error: {e}")
        return None



def generate_ollama(model, prompt):
    host = os.getenv("OLLAMA_HOST") or "http://localhost:11434"
    client = ollama.Client(host=host)
    model = os.getenv("OLLAMA_MODEL", "llama3")
    print(prompt)

    try:
        response = client.generate(model=model, prompt=prompt, stream=False)
        return response['response']
    except Exception as e:
        if "model" in str(e).lower() and "not found" in str(e).lower():
            print(f"Error: Model '{model}' is not downloaded.")
            print(f"Run: docker exec ollama ollama pull {model}")
        else:
            raise



