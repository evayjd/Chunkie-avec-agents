from .roast_prompts import SCORE_PROMPT
from llm.ollama_client import chat_json


def generate_scores(persona):

    prompt = f"""
用户画像：

{persona}
"""

    return chat_json(SCORE_PROMPT, prompt)