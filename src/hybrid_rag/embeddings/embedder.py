from fastembed import TextEmbedding

from hybrid_rag.settings import DEFAULT_EMBEDDING_MODEL, MODEL_CACHE_DIR


class Embedder:
    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL, batch_size: int = 16):
        self.model_name = model_name
        self.batch_size = batch_size
        self._model = None
        # E5 models were trained with these prefixes; other models don't use them
        self._e5 = "e5" in model_name.lower()

    @property
    def model(self) -> TextEmbedding:
        if self._model is None:                          # lazy: loading takes seconds
            MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
            self._model = TextEmbedding(
                model_name=self.model_name, cache_dir=str(MODEL_CACHE_DIR)
            )
        return self._model

    def _embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.embed(texts, batch_size=self.batch_size)
        return [v.tolist() for v in vectors]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if self._e5:
            texts = [f"passage: {t}" for t in texts]
        return self._embed(texts)

    def embed_query(self, text: str) -> list[float]:
        if self._e5:
            text = f"query: {text}"
        return self._embed([text])[0]