from sentence_transformers import SentenceTransformer
from typing import List
from functools import lru_cache


class EmbeddingModel:
    """
    Wraps the embedding model. Not instantiated at import time —
    the model only loads when first used, and tests can swap in a fake
    implementation instead of ever touching this class.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self._model_name = model_name
        self._model = None  # lazy-loaded on first use

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self._model_name)
        return self._model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self._get_model().encode(texts, show_progress_bar=False).tolist()

    def embed_query(self, query: str) -> List[float]:
        return self.embed_texts([query])[0]


@lru_cache
def get_embedding_model() -> EmbeddingModel:
    """
    Shared instance for production/app use (cached so the model only loads once).
    Tests do NOT use this — they construct a fake EmbeddingModel directly.
    """
    return EmbeddingModel()