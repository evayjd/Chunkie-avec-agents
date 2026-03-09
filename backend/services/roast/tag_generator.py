from .roast_prompts import TAG_PROMPT
from llm.ollama_client import chat_json


def generate_tags(persona):

    prompt = f"""
用户画像：

{persona}
"""

    result = chat_json(TAG_PROMPT, prompt)

    return result.get("tags", [])