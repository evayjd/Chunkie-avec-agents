import requests


class OllamaClient:

    def __init__(self, model: str, base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def chat(self, system: str, user: str) -> str:

        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "stream": False
        }

        r = requests.post(url, json=payload, timeout=120)

        if r.status_code != 200:
            raise RuntimeError(f"Ollama error: {r.text}")

        data = r.json()

        return data["message"]["content"]