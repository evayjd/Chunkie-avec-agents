import json
import random

from sqlalchemy import text

from backend.core.database import SessionLocal
from backend.services.llm.ollama_client import OllamaClient


OUTPUT_FILE = "evaluation/dataset.json"

SAMPLE_SIZE = 30


class DatasetGenerator:

    def __init__(self):

        self.db = SessionLocal()

        self.llm = OllamaClient(model="llama3")

    # --------------------------------------------------
    # 获取随机chunks
    # --------------------------------------------------

    def sample_chunks(self):

        sql = """
        SELECT content
        FROM chunks
        ORDER BY random()
        LIMIT :n
        """

        rows = self.db.execute(text(sql), {"n": SAMPLE_SIZE}).fetchall()

        return [r.content for r in rows]

    # --------------------------------------------------
    # 生成问题
    # --------------------------------------------------

    def generate_question(self, chunk):

        prompt = f"""
Given the following document excerpt, generate ONE clear question
that can be answered using the text.

Text:
{chunk}

Rules:
- Question must be answerable from the text
- Question should be concise
- Do not include explanation

Return only the question.
"""

        question = self.llm.chat(
            system="You generate questions from documents.",
            user=prompt
        )

        return question.strip()

    # --------------------------------------------------
    # 生成keywords
    # --------------------------------------------------

    def generate_keywords(self, chunk):

        prompt = f"""
Extract 3 important keywords from the text.

Text:
{chunk}

Return JSON list like:
["keyword1", "keyword2"]
"""

        result = self.llm.chat(
            system="Extract keywords.",
            user=prompt
        )

        try:
            keywords = json.loads(result)
        except:
            keywords = []

        return keywords

    # --------------------------------------------------
    # 主生成函数
    # --------------------------------------------------

    def generate_dataset(self):

        chunks = self.sample_chunks()

        dataset = []

        for chunk in chunks:

            try:

                question = self.generate_question(chunk)

                keywords = self.generate_keywords(chunk)

                if not question:
                    continue

                item = {
                    "question": question,
                    "expected_keywords": keywords
                }

                dataset.append(item)

                print("Generated:", question)

            except Exception as e:

                print("Error:", e)

        return dataset

    # --------------------------------------------------
    # 保存dataset
    # --------------------------------------------------

    def save(self, dataset):

        with open(OUTPUT_FILE, "w") as f:

            json.dump(dataset, f, indent=2)

        print("Dataset saved:", OUTPUT_FILE)


if __name__ == "__main__":

    generator = DatasetGenerator()

    dataset = generator.generate_dataset()

    generator.save(dataset)