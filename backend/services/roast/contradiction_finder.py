from typing import Any, Dict, List

from backend.services.llm.ollama_client import chat_json
from backend.services.roast.roast_prompts import CONTRADICTION_PROMPT


def find_contradictions(persona: Dict[str, Any], user_data: Any) -> List[str]:
    """
    从 persona + user_data 中抽取矛盾点。

    返回：
    - 最多 5 条可用于 roast 的矛盾表述
    """
    prompt = f"""
User Persona:
{persona}

User Data:
{user_data}
"""

    result = chat_json(CONTRADICTION_PROMPT, prompt)

    contradictions = result.get("contradictions", [])
    cleaned: List[str] = []

    if isinstance(contradictions, list):
        for c in contradictions:
            if isinstance(c, str):
                c = c.strip()
                if c:
                    cleaned.append(c)

    return cleaned[:5]