"""
Retrieval Layer
---------------
Simulates the RAG retrieval step. In the full production stack (see README),
this is FAISS + sentence-transformers embeddings. For this simulation we use
TF-IDF + cosine similarity so the demo runs instantly with no heavy model
downloads -- same interface, swappable backend.
"""

import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_base", "manuals.json")


class RetrievalLayer:
    def __init__(self, kb_path=KB_PATH):
        with open(kb_path, "r") as f:
            self.knowledge_base = json.load(f)

        self.corpus = [doc["text"] for doc in self.knowledge_base]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.doc_vectors = self.vectorizer.fit_transform(self.corpus)

    def retrieve(self, query: str, top_k: int = 3):
        """Return top_k most relevant knowledge base entries for a query string."""
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.doc_vectors).flatten()
        ranked_idx = scores.argsort()[::-1][:top_k]

        results = []
        for idx in ranked_idx:
            entry = self.knowledge_base[idx]
            results.append({
                "id": entry["id"],
                "title": entry["title"],
                "text": entry["text"],
                "relevance_score": round(float(scores[idx]), 3)
            })
        return results

    def build_query(self, fault_code: str, fault_description: str, sensor_readings: dict) -> str:
        """Turn structured fault input into a natural language query for retrieval."""
        sensor_str = ", ".join(f"{k}={v}" for k, v in sensor_readings.items())
        return f"{fault_code} {fault_description}. Sensor readings: {sensor_str}"
