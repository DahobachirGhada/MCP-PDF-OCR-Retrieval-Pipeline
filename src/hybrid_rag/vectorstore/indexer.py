from hybrid_rag.embeddings.embedder import Embedder
from hybrid_rag.models.chunk import Chunk
from hybrid_rag.vectorstore.chroma_store import ChromaStore


def index_chunks(chunks: list[Chunk], embedder: Embedder, store: ChromaStore,
                 batch_size: int = 64) -> int:
    if not chunks:
        return 0

    # re-ingesting a document replaces its old chunks instead of leaving stale ones
    for source in {c.metadata["source"] for c in chunks}:
        store.delete_source(source)

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        vectors = embedder.embed_documents([c.embedding_text for c in batch])
        store.upsert(batch, vectors)

    return len(chunks)