from typing import Any, Dict, List

from backend.services.llm.ollama_client import chat_json
from backend.services.roast.roast_prompts import TAG_PROMPT


def generate_tags(persona: Dict[str, Any], user_data: Any) -> List[str]:
    """
    生成 roast 标签。

    安全策略：
    1. 捕获 LLM 调用异常
    2. 校验 JSON 结构
    3. 清洗标签数据
    4. 保证函数永远返回 List[str]
    """

    prompt = f"""
用户画像：
{persona}

用户资料：
{user_data}
"""

    # -------------------------------------------------
    # 调用 LLM
    # -------------------------------------------------
    try:
        result = chat_json(TAG_PROMPT, prompt)
    except Exception as e:
        print("⚠️ TAG GENERATION FAILED:", e)
        return []

    # -------------------------------------------------
    # JSON结构校验
    # -------------------------------------------------
    if not isinstance(result, dict):
        return []

    tags = result.get("tags", [])

    if not isinstance(tags, list):
        return []

    # -------------------------------------------------
    # 标签清洗
    # -------------------------------------------------
    cleaned: List[str] = []

    for tag in tags:

        # 只接受字符串
        if not isinstance(tag, str):
            continue

        tag = tag.strip()

        if not tag:
            continue

        # 去掉多余符号
        tag = tag.replace("\n", " ").replace("  ", " ")

        # 避免过长
        if len(tag) > 40:
            tag = tag[:40]

        cleaned.append(tag)

    # -------------------------------------------------
    # 去重
    # -------------------------------------------------
    unique_tags: List[str] = []
    seen = set()

    for tag in cleaned:
        if tag not in seen:
            unique_tags.append(tag)
            seen.add(tag)

    # 最多返回6个
    return unique_tags[:6]