import requests

from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL

SYSTEM_PROMPT = (
    "You are a Senior Portfolio Manager. Look at the 4H trend and the 15M entry data. "
    "Decide the best action. You must reply with EXACTLY one word: BUY, SELL, or HOLD. "
    "No other text."
)


def get_ai_decision(market_data_string):
    response = requests.post(
        f"{OPENROUTER_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": market_data_string},
            ],
        },
        timeout=60,
    )

    if response.status_code != 200:
        raise RuntimeError(f"OpenRouter request failed with HTTP {response.status_code}.")

    return response.json()["choices"][0]["message"]["content"].strip()
