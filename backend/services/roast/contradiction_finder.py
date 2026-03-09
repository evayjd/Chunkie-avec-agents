from typing import Dict, List

from llm.ollama_client import OllamaClient
from .roast_prompts import CONTRADICTION_PROMPT

llm = OllamaClient()


def find_contradictions(persona: Dict, user_data: str) -> List[str]:
    """
    Extract contradictions / tensions from persona + user data.

    Returns
    -------
    List[str]
        3–5 concise contradiction statements used to guide roast writing.
    """

    prompt = f"""
User Persona:
{persona}

User Data:
{user_data}
"""

    result = llm.chat_json(CONTRADICTION_PROMPT, prompt)

    contradictions = result.get("contradictions", [])

    # basic cleanup
    cleaned = []
    for c in contradictions:
        if isinstance(c, str) and c.strip():
            cleaned.append(c.strip())

    return cleaned[:5]