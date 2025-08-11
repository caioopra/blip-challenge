import os

from dotenv import load_dotenv

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

load_dotenv()

class _Config:
    def __init__(self):
        self._config = {
            "DATA_DIR": DATA_DIR,
            "INPUT_CSV": os.environ.get(
                "INPUT_CSV",
                os.path.join(DATA_DIR, "tickets_atendimento_sinteticos.csv"),
            ),
            "OUTPUT_CSV": os.environ.get(
                "OUTPUT_CSV", os.path.join(DATA_DIR, "tickets_enriched.csv")
            ),
            "PROVIDER": os.environ.get(
                "LLM_PROVIDER", "mock"
            ).upper(),  # for this example, there is "mock" (offline and no real LLM solution) and "ollama"
            # ollama configuration (only for when PROVIDER is "ollama")
            "LLM_MODEL": os.environ.get("LLM_MODEL", "mistral"),
            "LLM_HOST": os.environ.get("LLM_HOST", "http://localhost:11434"),
        }

    def __getitem__(self, key):
        return self._config.get(key)

    def __repr__(self):
        return f"Config({self._config})"


Config = _Config()
