import chromadb
from chromadb.config import Settings

from hybrid_rag.models.chunk import Chunk
from hybrid_rag.settings import DEFAULT_COLLECTION, VECTORSTORE_DIR


class EmbeddingModelMismatch(RuntimeError):
    pass


class ChromaStore:
    def __init__(self, embedding_model: str, path=VECTORSTORE_DIR,
                 collection_name: str = DEFAULT_COLLECTION):
        path = str(path)
        self.client = chromadb.PersistentClient(
            path=path, settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine", "embedding_model": embedding_model},
        )
        stored = (self.collection.metadata or {}).get("embedding_model")
        if stored and stored != embedding_model:
            raise EmbeddingModelMismatch(
                f"Collection was built with '{stored}', but you are using "
                f"'{embedding_model}'. Reset the vector store or use another collection."
            )

    def upsert(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        self.collection.upsert(
            ids=[c.id for c in chunks],
            embeddings=embeddings,
            documents=[c.text for c in chunks],       # stored text, without the header
            metadatas=[c.metadata for c in chunks],
        )

    def delete_source(self, source: str) -> None:
        self.collection.delete(where={"source": source})

    def count(self) -> int:
        return self.collection.count()

    def query(self, embedding: list[float], k: int = 5, where: dict | None = None) -> list[dict]:
        res = self.collection.query(
            query_embeddings=[embedding],
            n_results=k,
            where=where or None,
            include=["documents", "metadatas", "distances"],
        )
        return [
            {
                "id": res["ids"][0][i],
                "text": res["documents"][0][i],
                "metadata": res["metadatas"][0][i],
                "distance": res["distances"][0][i],
                "score": 1.0 - res["distances"][0][i],     # cosine similarity
            }
            for i in range(len(res["ids"][0]))
        ]