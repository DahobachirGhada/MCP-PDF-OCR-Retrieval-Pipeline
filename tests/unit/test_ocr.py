from pathlib import Path

from hybrid_rag.ingestion.page_router import route_pages
from hybrid_rag.ocr.runner import ocr_document
from hybrid_rag.ocr.tesseract_engine import TesseractEngine

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
file_path = FIXTURES / "Convocation_scolaire_arabe.pdf"   # use a scanned fixture


def test_ocr():
    routes = route_pages(file_path)
    engine = TesseractEngine(languages="ara+fra")
    pages = ocr_document(file_path, routes, engine)

    for num, blocks in pages.items():
        print(f"--- page {num}")
        for b in blocks:
            print(f"[{b.confidence:.0f}] {b.text[:80]!r}")

    assert isinstance(pages, dict)