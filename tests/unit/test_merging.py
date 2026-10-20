from pathlib import Path

from hybrid_rag.ingestion.page_router import route_pages
from hybrid_rag.merging.deduplicator import overlap_ratio
from hybrid_rag.merging.structure_builder import build_document
from hybrid_rag.models.block import Block
from hybrid_rag.models.table import Table
from hybrid_rag.ocr.runner import ocr_document
from hybrid_rag.ocr.tesseract_engine import TesseractEngine
from hybrid_rag.parsing.pymupdf_parser import parse_document
from hybrid_rag.tables.camelot_extractor import extract_tables

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
file_path = FIXTURES / "Actif-du-bilan-rempli.pdf"


def test_merging():
    routes = route_pages(file_path)
    parsed = parse_document(file_path, routes)
    tables = extract_tables(file_path, routes)
    ocr_pages = ocr_document(file_path, routes, TesseractEngine(languages="fra+eng"))

    doc = build_document(file_path, routes, parsed, ocr_pages, tables)
    print(doc.to_text())

    assert len(doc.pages) == len(routes)

    # no text block may remain on top of a table
    for page in doc.pages:
        boxes = [e.bbox for e in page.elements if isinstance(e, Table)]
        for el in page.elements:
            if isinstance(el, Block):
                assert all(overlap_ratio(el.bbox, box) < 0.6 for box in boxes)