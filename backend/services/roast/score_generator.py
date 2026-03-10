from typing import Any, Dict

from backend.services.llm.ollama_client import chat_json
from backend.services.roast.roast_prompts import SCORE_PROMPT


def generate_scores(persona: Dict[str, Any], user_data: Any) -> Dict[str, Any]:
    """
    生成 roast 评分结果。
    """
    prompt = f"""
用户画像：
{persona}

用户资料：
{user_data}
"""

    result = chat_json(SCORE_PROMPT, prompt)

    if not isinstance(result, dict):
        return {"scores": {}, "diagnosis_rate": 0}

    scores = result.get("scores", {})
    diagnosis_rate = result.get("diagnosis_rate", 0)

    if not isinstance(scores, dict):
        scores = {}

    return {
        "scores": scores,
        "diagnosis_rate": diagnosis_rate
    }