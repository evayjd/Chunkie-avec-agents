import json
import re
from typing import Dict, Any, List

import requests


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.1:8b"


class RoastLLMError(Exception):
    pass


def _extract_json(text: str) -> Dict:
    """
    尝试从模型输出中提取 JSON
    """

    text = text.strip()

    try:
        return json.loads(text)
    except:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group())
        except:
            pass

    raise RoastLLMError("LLM output is not valid JSON")


def chat(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "options": {
            "temperature": temperature
        },
        "stream": False
    }

    res = requests.post(OLLAMA_URL, json=payload)

    if res.status_code != 200:
        raise RoastLLMError(res.text)

    return res.json()["message"]["content"]


def chat_json(system_prompt: str, user_prompt: str) -> Dict:

    text = chat(system_prompt, user_prompt)

    return _extract_json(text)


def chat_text(system_prompt: str, user_prompt: str) -> str:

    return chat(system_prompt, user_prompt, temperature=0.9)


def safe_list(items: List[Any], max_len: int = 6) -> List[str]:

    if not isinstance(items, list):
        return []

    cleaned = []

    for i in items:
        if isinstance(i, str):
            i = i.strip()
            if i:
                cleaned.append(i)

    return cleaned[:max_len]


def clamp_score(x: Any) -> int:

    try:
        x = int(float(x))
    except:
        return 50

    return max(0, min(100, x))


def clamp_rate(x: Any) -> float:

    try:
        x = round(float(x), 1)
    except:
        return 90.0

    return max(80.0, min(99.0, x))