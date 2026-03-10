from typing import Any, Dict, List, Optional

from backend.services.llm.ollama_client import OllamaClient
from backend.services.roast.roast_prompts import ROAST_PROMPT

llm = OllamaClient()


def write_roast(
    persona: Dict[str, Any],
    contradictions: List[str],
    user_data: Any,
    style_preference: Optional[str] = None,
) -> str:
    """
    生成最终 roast 文本。
    - 支持可选 style_preference
    """
    contradiction_text = "\n".join(f"- {c}" for c in contradictions) if contradictions else "无明显矛盾点"

    style_block = ""
    if style_preference:
        style_block = f"\n额外风格偏好：{style_preference}\n"

    prompt = f"""
User Persona:
{persona}

Key Contradictions:
{contradiction_text}

User Data:
{user_data}
{style_block}
"""

    roast = llm.chat(
        system=ROAST_PROMPT,
        user=prompt,
        temperature=0.9
    )

    return roast.strip()