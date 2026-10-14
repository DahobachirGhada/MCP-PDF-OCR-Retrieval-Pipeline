#The parser only handles pages with use_parser=True. Scanned pages are left for OCR, and mixed pages go through both, so the duplicate text is removed later in merging/

import pymupdf

from hybrid_rag.ingestion.page_router import PageRoute
from hybrid_rag.models.block import Block
from hybrid_rag.parsing.header_footer_remover import remove_headers_footers
from hybrid_rag.parsing.reading_order import order_blocks


def extract_blocks(page, page_number: int) -> list[Block]:
    width, height = page.rect.width, page.rect.height
    blocks = []
    for x0, y0, x1, y1, text, _no, block_type in page.get_text("blocks"):
        if block_type != 0:          # 0 = text, 1 = image
            continue
        text = text.strip()
        if not text:
            continue
        blocks.append(Block(page_number, (x0, y0, x1, y1), text, width, height))
    return blocks


def parse_document(pdf_path, routes: list[PageRoute]) -> dict[int, list[Block]]:
    """Return {page_number: ordered blocks} for pages routed to the parser."""
    pages = {}
    with pymupdf.open(pdf_path) as pdf:
        for route in routes:
            if route.use_parser:
                pages[route.page_number] = extract_blocks(
                    pdf[route.page_number], route.page_number
                )

    pages = remove_headers_footers(pages)
    return {num: order_blocks(blocks) for num, blocks in pages.items()}