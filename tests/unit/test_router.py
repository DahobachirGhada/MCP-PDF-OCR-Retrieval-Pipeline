from pathlib import Path

from hybrid_rag.ingestion.page_router import route_pages

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
file_path = FIXTURES / "Convocation_scolaire_arabe.pdf"


def test_router():
    routes = route_pages(file_path)
    for r in routes:
        print(r)

    assert len(routes) > 0