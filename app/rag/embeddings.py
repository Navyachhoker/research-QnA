from functools import lru_cache

from sentence_transformers import SentenceTransformer


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

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return self._get_model().encode(texts, show_progress_bar=False).tolist()

    def embed_query(self, query: str) -> list[float]:
        return self.embed_texts([query])[0]


@lru_cache
def get_embedding_model() -> EmbeddingModel:
    """
    Shared instance for production/app use (cached so the model only loads once).
    Tests do NOT use this — they construct a fake EmbeddingModel directly.
    """
    from app.config import settings

    return EmbeddingModel(model_name=settings.embedding_model)
