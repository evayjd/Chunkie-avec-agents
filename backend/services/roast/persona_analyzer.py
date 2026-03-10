from typing import Any, Dict

from backend.services.llm.ollama_client import chat_json
from backend.services.roast.roast_prompts import PERSONA_PROMPT


def analyze_persona(user_data: Any) -> Dict[str, Any]:
    """
    基于统一的 user_data payload 生成人物画像。
    """
    prompt = f"""
用户资料：
{user_data}
"""

    result = chat_json(PERSONA_PROMPT, prompt)

    if not isinstance(result, dict):
        return {}

    return result