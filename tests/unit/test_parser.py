from pathlib import Path

from hybrid_rag.ingestion.page_router import route_pages
from hybrid_rag.parsing.pymupdf_parser import parse_document

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
file_path = FIXTURES / "Actif-du-bilan-rempli.pdf"


def test_parser():
    routes = route_pages(file_path)
    pages = parse_document(file_path, routes)

    for num, blocks in pages.items():
        print(f"--- page {num}")
        for b in blocks:
            print(b.text[:80].replace("\n", " "))

    assert pages