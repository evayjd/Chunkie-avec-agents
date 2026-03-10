import json
import re
from typing import Any, Dict, Optional

import requests

from backend.core.config import settings


class OllamaClient:
    """
    Ollama client wrapper.

    提供：
    - chat()
    - generate()
    - chat_json()

    chat_json 具有 JSON 自动修复能力
    """

    def __init__(
        self,
        model: Optional[str] = None,
        base_url: str = "http://localhost:11434"
    ):
        self.model = model or settings.CHAT_MODEL
        self.base_url = base_url.rstrip("/")

    # -------------------------------------------------
    # JSON解析工具
    # -------------------------------------------------

    def _extract_json_block(self, text: str) -> Optional[str]:
        """
        从文本中提取第一个 JSON 对象 {...}
        """
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return match.group()
        return None

    def _repair_json(self, text: str) -> Optional[Dict[str, Any]]:
        """
        尝试修复 JSON
        """
        json_text = self._extract_json_block(text)

        if not json_text:
            return None

        # 修复常见错误
        json_text = json_text.replace("\n", " ")
        json_text = re.sub(r",\s*}", "}", json_text)
        json_text = re.sub(r",\s*]", "]", json_text)

        try:
            return json.loads(json_text)
        except Exception:
            return None

    def _parse_json(self, text: str) -> Dict[str, Any]:
        """
        JSON解析流程：
        1 尝试直接解析
        2 尝试提取 {...}
        3 尝试修复
        """

        text = text.strip()

        # 1 直接解析
        try:
            return json.loads(text)
        except Exception:
            pass

        # 2 提取 {...}
        json_block = self._extract_json_block(text)
        if json_block:
            try:
                return json.loads(json_block)
            except Exception:
                pass

        # 3 JSON修复
        repaired = self._repair_json(text)
        if repaired:
            return repaired

        # 调试输出
        print("\n⚠️ LLM JSON PARSE FAILED")
        print("RAW MODEL OUTPUT:\n")
        print(text)
        print("\n")

        raise ValueError("Model output is not valid JSON")

    # -------------------------------------------------
    # LLM调用
    # -------------------------------------------------

    def chat(
        self,
        system: str,
        user: str,
        temperature: float = 0.7
    ) -> str:
        """
        标准 chat 调用
        """
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "options": {"temperature": temperature},
            "stream": False
        }

        try:
            r = requests.post(url, json=payload, timeout=120)
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "Cannot connect to Ollama. Did you run 'ollama serve'?"
            )

        if r.status_code != 200:
            raise RuntimeError(f"Ollama error: {r.text}")

        data = r.json()
        return data["message"]["content"]

    def chat_json(
        self,
        system: str,
        user: str,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        JSON安全调用
        """
        text = self.chat(system, user, temperature)
        return self._parse_json(text)

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7
    ) -> str:

        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "options": {"temperature": temperature},
            "stream": False
        }

        r = requests.post(url, json=payload, timeout=120)

        if r.status_code != 200:
            raise RuntimeError(f"Ollama error: {r.text}")

        data = r.json()
        return data["message"]["content"]


# -------------------------------------------------
# 全局 helper
# -------------------------------------------------

_default_client = OllamaClient()


def chat(system: str, user: str, temperature: float = 0.7) -> str:
    return _default_client.chat(system, user, temperature)


def chat_json(system: str, user: str, temperature: float = 0.7):
    return _default_client.chat_json(system, user, temperature)


def chat_text(system: str, user: str, temperature: float = 0.9):
    return _default_client.chat(system, user, temperature)