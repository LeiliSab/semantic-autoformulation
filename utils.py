#%%
import os
import time
import random
from openai import OpenAI

MAX_RETRY = 5

def chat_gpt(
        user_prompt=None, 
        system_prompt=None, 
        n_used=1,
        logprobs=False,      # kept for API compatibility; not used by Azure Chat Completions
        seed=None,
        llm_name=None,       # kept for compatibility
        engine_used='GPT5-mini'
    ):
    """
    Calls OpenAI Chat Completions API with the model selected by `engine_used`.
    API key is read from environment variable.
    """

    # --- Read configuration from environment variables ---
    API_KEY = os.getenv("OPENAI_API_KEY")

    if not API_KEY:
        raise EnvironmentError(
            "Missing OpenAI API key. Please set OPENAI_API_KEY environment variable."
        )

    # Map engine names to actual OpenAI model names
    if engine_used == 'GPT5':
        mdl = "gpt-4o"  # or "gpt-4-turbo" depending on your preference
    elif engine_used == 'GPT5-mini':
        mdl = "gpt-4o-mini"
    else:
        mdl = "gpt-4o"  # default model

    client = OpenAI(
        api_key=API_KEY,
    )

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if user_prompt:
        messages.append({"role": "user", "content": user_prompt})

    # Optional extras
    kwargs = {}
    # If you ever want to toggle JSON mode from the call site, add json_mode=True to the signature.
    # Keeping the behavior identical to your original (json_mode=False by default).
    # if json_mode:
    #     kwargs["response_format"] = {"type": "json_object"}
    if seed is not None:
        kwargs["seed"] = seed

    # --- simple retry with exponential backoff ---
    last_err = None
    for attempt in range(MAX_RETRY):
        try:
            response = client.chat.completions.create(
                model=mdl,
                messages=messages if messages else [{"role": "user", "content": user_prompt or system_prompt}],
                n=n_used,
                **kwargs
            )
            # basic sanity check like your original
            _ = response.choices[0].message.content  # will raise if missing
            return response
        except Exception as e:
            last_err = e
            # jittered backoff
            sleep_time = min(2.5, 1.0 + random.random()) * (1.7 ** attempt)
            time.sleep(sleep_time)

    # If we got here, all retries failed
    raise RuntimeError(f"chat_gpt failed after {MAX_RETRY} attempts. Last error: {last_err}")

# %%
