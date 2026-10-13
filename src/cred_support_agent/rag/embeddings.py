import hashlib
from functools import lru_cache
from typing import Iterable, List

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - fallback for offline execution
    SentenceTransformer = None


class HashEmbeddingModel:
    def __call__(self, texts: Iterable[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            ints = [int(digest[i : i + 2], 16) for i in range(0, len(digest), 2)]
            vector = [x / 255.0 for x in ints[:384]]
            if len(vector) < 384:
                vector.extend([0.0] * (384 - len(vector)))
            vectors.append(vector)
        return vectors


class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            if SentenceTransformer is None:
                self._model = HashEmbeddingModel()
            else:
                try:
                    self._model = SentenceTransformer(self.model_name)
                except Exception:
                    self._model = HashEmbeddingModel()
        return self._model

    def embed(self, texts: Iterable[str]) -> List[List[float]]:
        texts_list = list(texts)
        if not texts_list:
            return []
        return self._get_model()(texts_list)


@lru_cache(maxsize=8)
def get_embedding_service(model_name: str = "all-MiniLM-L6-v2") -> EmbeddingService:
    return EmbeddingService(model_name=model_name)
