import pymupdf

from hybrid_rag.ingestion.page_router import PageRoute
from hybrid_rag.models.block import Block
from hybrid_rag.ocr.base import OCREngine
from hybrid_rag.ocr.postprocessing import clean_blocks
from hybrid_rag.ocr.preprocessing import DEFAULT_DPI, preprocess, render_page
from hybrid_rag.parsing.reading_order import order_blocks


def ocr_document(
    pdf_path, routes: list[PageRoute], engine: OCREngine, dpi: int = DEFAULT_DPI
) -> dict[int, list[Block]]:
    """Return {page_number: ordered blocks} for pages routed to OCR."""
    pages = {}
    scale = dpi / 72
    with pymupdf.open(pdf_path) as pdf:
        for route in routes:
            if not route.use_ocr:
                continue
            page = pdf[route.page_number]
            image = preprocess(render_page(page, dpi))
            blocks = engine.recognize(
                image,
                route.page_number,
                (page.rect.width, page.rect.height),
                scale,
            )
            pages[route.page_number] = order_blocks(clean_blocks(blocks))
    return pages