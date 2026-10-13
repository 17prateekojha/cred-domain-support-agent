import re
from typing import Iterable, List, Dict, Any


def split_fixed_size(text: str, chunk_size: int = 350, overlap: int = 60) -> List[str]:
    if not text:
        return []
    text = text.strip()
    if len(text) <= chunk_size:
        return [text]
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end]
        chunks.append(chunk.strip())
        if end == len(text):
            break
        start += max(1, chunk_size - overlap)
    return [c for c in chunks if c]


def split_sentences(text: str) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def build_document_chunks(documents: Iterable[Dict[str, Any]], strategy: str = "fixed") -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []
    for doc in documents:
        body = doc.get("text", "")
        parent_id = doc.get("doc_id", doc.get("id", "unknown"))
        if strategy == "sentence":
            pieces = split_sentences(body)
        else:
            pieces = split_fixed_size(body)
        for idx, piece in enumerate(pieces):
            chunks.append(
                {
                    "doc_id": parent_id,
                    "chunk_id": f"{parent_id}-chunk-{idx}",
                    "text": piece,
                    "strategy": strategy,
                }
            )
    return chunks
