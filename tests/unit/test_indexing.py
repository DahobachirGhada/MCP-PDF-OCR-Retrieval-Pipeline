import os

import pytest

from hybrid_rag.embeddings.embedder import Embedder
from hybrid_rag.models.chunk import Chunk
from hybrid_rag.vectorstore.chroma_store import ChromaStore, EmbeddingModelMismatch
from hybrid_rag.vectorstore.indexer import index_chunks


class FakeEmbedder:
    """Cheap bag-of-words vectors, so store logic is tested without a model download."""
    model_name = "fake"

    def _vec(self, text):
        v = [0.0] * 64
        for w in text.lower().split():
            v[hash(w) % 64] += 1.0
        norm = sum(x * x for x in v) ** 0.5 or 1.0
        return [x / norm for x in v]

    def embed_documents(self, texts):
        return [self._vec(t) for t in texts]

    def embed_query(self, text):
        return self._vec(text)


def make_chunk(i, text, source="a.pdf", kind="text", page=1):
    return Chunk(
        id=f"{source}-{i}",
        text=text,
        context=f"{source} | page {page}",
        metadata={"source": source, "page": page, "type": kind, "section": ""},
    )


def test_index_search_and_reindex(tmp_path):
    emb = FakeEmbedder()
    store = ChromaStore("fake", path=tmp_path)
    chunks = [
        make_chunk(0, "net revenue grew strongly in the third quarter"),
        make_chunk(1, "the company headquarters moved to a new office"),
        make_chunk(2, "| Quarter | Revenue |", kind="table"),
    ]
    assert index_chunks(chunks, emb, store) == 3
    assert store.count() == 3

    hits = store.query(emb.embed_query("revenue third quarter"), k=1)
    assert hits[0]["id"] == "a.pdf-0"

    tables = store.query(emb.embed_query("revenue"), k=5, where={"type": "table"})
    assert [h["id"] for h in tables] == ["a.pdf-2"]

    index_chunks(chunks[:2], emb, store)         # re-ingest the same source with fewer chunks
    assert store.count() == 2                     # the stale chunk is gone, no duplicates


def test_model_mismatch_is_rejected(tmp_path):
    ChromaStore("model-a", path=tmp_path)
    with pytest.raises(EmbeddingModelMismatch):
        ChromaStore("model-b", path=tmp_path)


@pytest.mark.skipif(not os.getenv("RUN_SLOW"), reason="downloads a ~2 GB model")
def test_cross_language_retrieval(tmp_path):
    emb = Embedder()
    store = ChromaStore(emb.model_name, path=tmp_path)
    chunks = [
        make_chunk(0, "Le chiffre d'affaires net a augmenté de 12 % au troisième trimestre."),
        make_chunk(1, "Le siège social de l'entreprise a déménagé à Oran."),
        make_chunk(2, "الجمهورية الجزائرية الديمقراطية الشعبية، وزارة التربية الوطنية."),
    ]
    index_chunks(chunks, emb, store)

    hits = store.query(emb.embed_query("ما هي وزارة التربية؟"), k=1)    # Arabic question
    assert hits[0]["id"] == "a.pdf-2"
    hits = store.query(emb.embed_query("revenue growth in Q3"), k=1)     # English question
    assert hits[0]["id"] == "a.pdf-0"