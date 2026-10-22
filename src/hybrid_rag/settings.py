from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]      # .../MCP-PDF-OCR-Retrieval-Pipeline

VECTORSTORE_DIR = PROJECT_ROOT / "data" / "vectorstore" / "chroma"
MODEL_CACHE_DIR = PROJECT_ROOT / "data" / "model_cache"

DEFAULT_EMBEDDING_MODEL = "intfloat/multilingual-e5-large"
DEFAULT_COLLECTION = "documents"