import json
import os

from openai import OpenAI


class LLMClient:
    def __init__(self, provider: str | None = None):
        self.provider = provider or os.getenv("LLM_PROVIDER", "openai")
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.client = None

        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)

    def generate(self, prompt: str) -> str:
        if self.provider != "openai":
            raise Exception(f"Unsupported provider: {self.provider}")

        if self.client is None:
            raise Exception("OPENAI_API_KEY is not configured.")

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text

    def generate_json(self, prompt: str) -> dict:
        output = self.generate(prompt)

        try:
            return json.loads(output)
        except json.JSONDecodeError:
            cleaned = output.strip()

            if cleaned.startswith("```json"):
                cleaned = cleaned.removeprefix("```json").removesuffix("```").strip()
            elif cleaned.startswith("```"):
                cleaned = cleaned.removeprefix("```").removesuffix("```").strip()

            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                return {
                    "root_cause": "UNKNOWN",
                    "confidence": "LOW",
                    "reason": cleaned or "Model returned an empty response."
                }
