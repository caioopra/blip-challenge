import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Tuple

import requests

from Config import Config


# Enum for LLM providers
class LLMProvider(Enum):
    MOCK = "mock"
    OLLAMA = "ollama"

    @staticmethod
    def from_string(provider: str) -> "LLMProvider":
        """Converts a string to an LLMProvider enum."""
        try:
            return LLMProvider[provider.upper()]
        except KeyError:
            raise ValueError(f"Unknown LLM provider: {provider}")


def get_llm_client(provider: LLMProvider) -> "LLM":
    """
    Factory function to get the appropriate LLM client based on the provider.
    """
    print(f"Using LLM provider: {provider.value}")
    if provider == LLMProvider.MOCK:
        return MockLLM()

    return LLMClient(
        model=Config["LLM_MODEL"],
        host=Config["LLM_HOST"],
    )


# Abstract base class for LLM client
class LLM(ABC):
    @abstractmethod
    def summarize(self, text: str) -> str:
        """Generates a summary of the given text."""
        pass

    @abstractmethod
    def classify(self, text: str, categories: List[str]) -> Tuple[str, float]:
        """Classifies the given text into one of the provided categories."""
        pass


# mock llm for offline testing
class MockLLM(LLM):
    def summarize(self, text: str) -> str:
        """Applies a simple heuristic summarizer, taking first sentence/part of text"""
        if not text or text.strip() == "":
            return ""

        sentences = text.split(".")
        candidate = sentences[0].strip() if sentences else ""

        if len(candidate) < 180 and len(sentences) > 1:
            return (
                sentences[0].strip()
                + (". " + sentences[1].strip() if sentences[1].strip() else "").strip()
            )

        return (candidate[:200] + "..." if len(candidate) > 200 else "").strip()

    def classify(self, text: str, categories: List[str]) -> Tuple[str, float]:
        """
        Mock classification based on key-words classification for the customer support domain.
        """
        ...
        txt = text.lower()

        scores = {c: 0.0 for c in categories}

        mapping = {
            "reclam": "Reclamação",
            "fatura": "Reclamação",
            "erro": "Suporte técnico",
            "falha": "Suporte técnico",
            "login": "Suporte técnico",
            "dúvid": "Dúvida",
            "como": "Dúvida",
            "solicit": "Solicitação de serviço",
            "pedido": "Solicitação de serviço",
            "feedback": "Feedback",
            "sugest": "Feedback",
        }

        # increase score when keywords appear
        for k, v in mapping.items():
            if k in txt:
                scores[v] += 1.0

        best = max(scores.items(), key=lambda x: x[1])

        if best[1] == 0.0:
            # fallback if nothing matches
            return ("Dúvida", 0.35)

        total = sum(scores.values())
        confidence = best[1] / (total if total > 0 else 1)

        return (best[0], min(max(confidence, 0.35), 0.99))


# for ollama
class LLMClient(LLM):
    def __init__(
        self,
        model: Optional[str] = Config["LLM_MODEL"],
        host: Optional[str] = Config["LLM_HOST"],
    ):
        self.model = model
        self.host = host

    def summarize(self, text: str) -> str:
        prompt = f"Resuma o seguinte chamado em até 3 frases (ou menos) relatando o que o cliente enviou, em português claro:\n\n{text}\n\nResumo:"

        return self._generate(prompt).strip()

    def classify(self, text: str, categories: List[str]) -> Tuple[str, float]:
        categories_str = "\n - ".join(categories)

        prompt = (
            f"Classifique o chamado abaixo em somente **UMA** das categorias a seguir:\n"
            f"{categories_str}\n\n"
            f"Chamado: {text}\n\n"
            "Responda apenas com o nome exato da categoria: "
        )

        label = self._generate(prompt).strip()

        if label not in categories:
            return ("Dúvida", 0.35)

        return (label, 0.85)  # fixed confidence for MVP

    def _generate(self, prompt: str) -> str:
        """Generates text using the LLM API."""
        url = f"{self.host}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        try:
            response = requests.post(url, json=payload)

            response.raise_for_status()

            data = response.json()

            return data.get("response", "").strip()
        except requests.RequestException as e:
            print(f"Error communicating with LLM API: {e}")
            return ""
        except Exception as e:
            print(f"Unexpected LLM error: {e}")
            return ""
