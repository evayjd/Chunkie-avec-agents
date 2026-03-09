import requests
import json
import re
from typing import Any, Dict


class OllamaClient:
    """
    Ollama client wrapper.

    Supports:
    - chat(system, user)
    - generate(prompt)
    - chat_json(system, user)
    """

    def __init__(
        self,
        model: str = "llama3.1:8b",
        base_url: str = "http://localhost:11434"
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from model output.
        """

        text = text.strip()

        try:
            return json.loads(text)
        except Exception:
            pass

        match = re.search(r"\{.*\}", text, re.DOTALL)

        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass

        raise ValueError("Model output is not valid JSON")

    def chat(
        self,
        system: str,
        user: str,
        temperature: float = 0.7
    ) -> str:
        """
        Chat-style call with system + user messages
        """

        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "options": {
                "temperature": temperature
            },
            "stream": False
        }

        r = requests.post(url, json=payload, timeout=120)

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
        Chat and parse JSON response
        """

        text = self.chat(system, user, temperature)

        return self._extract_json(text)

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7
    ) -> str:
        """
        Simple generation interface
        """

        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "options": {
                "temperature": temperature
            },
            "stream": False
        }

        r = requests.post(url, json=payload, timeout=120)

        if r.status_code != 200:
            raise RuntimeError(f"Ollama error: {r.text}")

        data = r.json()

        return data["message"]["content"]