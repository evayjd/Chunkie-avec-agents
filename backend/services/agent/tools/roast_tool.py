import requests


class RoastTool:
    name = "roast_tool"
    description = "Generate a roast based on one or more documents."
    input_schema = {
        "document_ids": "list[string] | null"
    }

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def run(self, document_ids=None):
        response = requests.post(
            f"{self.base_url}/roast",
            json={
                "document_ids": document_ids
            },
            timeout=180
        )
        response.raise_for_status()
        return response.json()