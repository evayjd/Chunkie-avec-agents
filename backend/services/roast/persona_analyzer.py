from .roast_prompts import PERSONA_PROMPT
from backend.services.roast.roast import chat_json


def analyze_persona(user_data):

    prompt = f"""
用户资料：
{user_data}
"""

    result = chat_json(PERSONA_PROMPT, prompt)

    return result