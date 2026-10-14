from pathlib import Path

from hybrid_rag.ingestion.page_router import route_pages
from hybrid_rag.tables.camelot_extractor import extract_tables

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
file_path = FIXTURES / "Actif-du-bilan-rempli.pdf"


def test_tables():
    routes = route_pages(file_path)
    tables = extract_tables(file_path, routes)

    for t in tables:
        print(f"--- page {t.page_number} ({t.flavor}, accuracy {t.accuracy:.0f})")
        print(t.markdown)

    assert isinstance(tables, list)