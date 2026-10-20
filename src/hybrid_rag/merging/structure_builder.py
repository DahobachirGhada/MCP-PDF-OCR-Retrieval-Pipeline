from collections import defaultdict
from pathlib import Path

import pymupdf

from hybrid_rag.merging.block_merger import merge_page
from hybrid_rag.models.document import Document
from hybrid_rag.models.page import Page


def build_document(pdf_path, routes, parsed, ocr_pages, tables) -> Document:
    tables_by_page = defaultdict(list)
    for t in tables:
        tables_by_page[t.page_number].append(t)

    pages = []
    with pymupdf.open(pdf_path) as pdf:
        for route in routes:
            n = route.page_number
            rect = pdf[n].rect
            elements = merge_page(
                n,
                (rect.width, rect.height),
                parsed.get(n, []),
                ocr_pages.get(n, []),
                tables_by_page.get(n, []),
            )
            pages.append(Page(n, route.label, rect.width, rect.height, elements))

    return Document(source=Path(pdf_path).name, pages=pages)