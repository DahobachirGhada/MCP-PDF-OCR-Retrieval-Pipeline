import re
from pathlib import Path

from hybrid_rag.chunking.layout_chunker import chunk_document
from hybrid_rag.chunking.semantic_chunker import split_text
from hybrid_rag.chunking.table_chunker import table_texts
from hybrid_rag.ingestion.page_router import route_pages
from hybrid_rag.merging.structure_builder import build_document
from hybrid_rag.models.table import Table
from hybrid_rag.parsing.pymupdf_parser import parse_document
from hybrid_rag.tables.camelot_extractor import extract_tables
from hybrid_rag.tables.table_to_markdown import to_markdown

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
file_path = FIXTURES / "Actif-du-bilan-rempli.pdf"


def test_split_text_size_and_overlap():
    text = " ".join(f"Sentence number {i} ends here." for i in range(60))
    chunks = split_text(text, max_chars=200, overlap=60)

    assert len(chunks) > 1
    assert all(len(c) <= 200 for c in chunks)
    last = re.findall(r"Sentence number \d+ ends here\.", chunks[0])[-1]
    assert last in chunks[1]                      # overlap carried forward


def test_table_split_repeats_header():
    rows = [["Quarter", "Revenue"]] + [[f"Q{i}", str(i * 100)] for i in range(40)]
    table = Table(0, (0, 0, 1, 1), rows, to_markdown(rows), "lattice", 99.0)

    pieces = table_texts(table, max_chars=300)
    assert len(pieces) > 1
    assert all(p.startswith("| Quarter | Revenue |") for p in pieces)


def test_chunk_document():
    routes = route_pages(file_path)
    parsed = parse_document(file_path, routes)
    tables = extract_tables(file_path, routes)
    doc = build_document(file_path, routes, parsed, {}, tables)   # no OCR: fast

    chunks = chunk_document(doc)
    for c in chunks:
        print(f"[p{c.metadata['page']}] {c.metadata['type']:5} | {c.context}")
        print(c.text[:120].replace("\n", " "), "\n")

    assert chunks
    assert len({c.id for c in chunks}) == len(chunks)
    for c in chunks:
        assert all(isinstance(v, (str, int, float, bool)) for v in c.metadata.values())