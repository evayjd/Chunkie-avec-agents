from typing import Dict, List

from llm.ollama_client import OllamaClient
from roast_prompts import ROAST_PROMPT

llm = OllamaClient()


def write_roast(
    persona: Dict,
    contradictions: List[str],
    user_data: str,
) -> str:
    """
    Generate roast text using contradictions.
    """

    contradiction_text = "\n".join(f"- {c}" for c in contradictions)

    prompt = f"""
User Persona:
{persona}

Key Contradictions:
{contradiction_text}

User Data:
{user_data}
"""

    roast = llm.chat(
        ROAST_PROMPT,
        prompt,
        temperature=0.9
    )

    return roast.strip()