from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import uuid

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class MemoryRecord:
    id: str
    text: str
    metadata: Dict[str, Any]


class VectorMemory:
    """Lightweight vector store backed by TF-IDF + cosine similarity."""

    def __init__(self) -> None:
        self.records: List[MemoryRecord] = []
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=2048)
        self.embeddings = np.empty((0, 0))

    def _rebuild_index(self) -> None:
        if not self.records:
            self.embeddings = np.empty((0, 0))
            return
        corpus = [record.text for record in self.records]
        self.embeddings = self.vectorizer.fit_transform(corpus)

    def upsert(self, text: str, metadata: Optional[Dict[str, Any]] = None, record_id: Optional[str] = None) -> MemoryRecord:
        metadata = metadata or {}
        record_id = record_id or metadata.get("id") or str(uuid.uuid4())
        # Replace if the id already exists
        existing = [r for r in self.records if r.id == record_id]
        if existing:
            self.records = [r for r in self.records if r.id != record_id]
        record = MemoryRecord(id=record_id, text=text, metadata=metadata)
        self.records.append(record)
        self._rebuild_index()
        return record

    def bulk_load(self, items: List[Dict[str, Any]]) -> List[MemoryRecord]:
        loaded = []
        for item in items:
            loaded.append(
                self.upsert(
                    text=item["text"],
                    metadata=item.get("metadata") or {},
                    record_id=item.get("id"),
                )
            )
        return loaded

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.records:
            return []
        if self.embeddings.shape[0] == 0:
            return []
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.embeddings).flatten()
        idxs = scores.argsort()[::-1][:top_k]
        results = []
        for idx in idxs:
            record = self.records[int(idx)]
            results.append(
                {
                    "id": record.id,
                    "text": record.text,
                    "score": float(scores[int(idx)]),
                    "metadata": record.metadata,
                }
            )
        return results

    def clear(self) -> None:
        self.records = []
        self.embeddings = np.empty((0, 0))
