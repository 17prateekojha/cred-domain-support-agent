from __future__ import annotations

from typing import Any, Dict, List, Sequence

import chromadb

from src.cred_support_agent.config import BASE_DIR
from src.cred_support_agent.rag.embeddings import get_embedding_service


class InMemoryVectorStore:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.documents: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.ids: List[str] = []
        self.embeddings: List[List[float]] = []

    def upsert(self, ids: Sequence[str], documents: Sequence[str], metadatas: Sequence[Dict[str, Any]], embeddings: Sequence[List[float]] | None = None):
        for idx, item_id in enumerate(ids):
            if item_id in self.ids:
                existing_index = self.ids.index(item_id)
                self.documents[existing_index] = documents[idx]
                self.metadatas[existing_index] = metadatas[idx]
                self.embeddings[existing_index] = list(embeddings[idx]) if embeddings is not None else []
            else:
                self.ids.append(item_id)
                self.documents.append(documents[idx])
                self.metadatas.append(metadatas[idx])
                self.embeddings.append(list(embeddings[idx]) if embeddings is not None else [])

    def query(self, query_embedding: Sequence[float], n_results: int = 5):
        results = []
        if not self.documents:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        for idx, stored in enumerate(self.documents):
            dot = sum(a * b for a, b in zip(query_embedding, self.embeddings[idx])) if self.embeddings[idx] else 0.0
            magnitude = (sum(v * v for v in query_embedding) ** 0.5) * (sum(v * v for v in self.embeddings[idx]) ** 0.5 or 1.0)
            score = dot / magnitude if magnitude else 0.0
            results.append((score, idx))
        results.sort(key=lambda item: item[0], reverse=True)
        selected = results[:n_results]
        return {
            "documents": [[self.documents[idx] for _, idx in selected]],
            "metadatas": [[self.metadatas[idx] for _, idx in selected]],
            "distances": [[1.0 - score for score, _ in selected]],
        }


class ChromaCollectionAdapter:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self._client = None
        self._collection = None
        self._fallback = InMemoryVectorStore(collection_name)

    def _ensure_collection(self):
        if self._collection is not None:
            return self._collection
        try:
            self._client = chromadb.PersistentClient(path=str(BASE_DIR / "chroma_store"))
            self._collection = self._client.get_or_create_collection(name=self.collection_name)
        except Exception:
            self._collection = None
        return self._collection

    def upsert(self, ids: Sequence[str], documents: Sequence[str], metadatas: Sequence[Dict[str, Any]], embeddings: Sequence[List[float]]):
        collection = self._ensure_collection()
        if collection is not None:
            collection.upsert(
                ids=list(ids),
                documents=list(documents),
                metadatas=list(metadatas),
                embeddings=list(embeddings),
            )
            return
        self._fallback.upsert(list(ids), list(documents), list(metadatas), list(embeddings))

    def query(self, query_embedding: Sequence[float], n_results: int = 5):
        collection = self._ensure_collection()
        if collection is not None:
            return collection.query(query_embeddings=[list(query_embedding)], n_results=n_results)
        return self._fallback.query(list(query_embedding), n_results=n_results)


def build_collection(collection_name: str, chunks: Sequence[Dict[str, Any]]):
    service = get_embedding_service()
    adapter = ChromaCollectionAdapter(collection_name)
    texts = [c["text"] for c in chunks]
    embeddings = service.embed(texts)
    ids = [c["chunk_id"] for c in chunks]
    metadatas = [{"doc_id": c["doc_id"], "strategy": c["strategy"]} for c in chunks]
    adapter.upsert(ids, texts, metadatas, embeddings)
    return adapter
