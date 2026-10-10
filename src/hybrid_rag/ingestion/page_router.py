#Digital -> PyMuPDFparser
#Scanned -> OCR path
#Table/Grid -> Table path
from dataclasses import dataclass
from pathlib import Path

import pymupdf

from hybrid_rag.ingestion.document_classifier import classifier


@dataclass
class PageRoute:
    page_number: int   # 0-based
    label: str         # digital | scanned | mixed | blank
    use_parser: bool   # PyMuPDF text extraction
    use_ocr: bool      # DocTR / PaddleOCR
    use_tables: bool   # Camelot


def _has_tables(page) -> bool:
    try:
        return len(page.find_tables().tables) > 0
    except Exception:
        return False


def route_pages(pdf_path) -> list[PageRoute]:
    pdf_path = Path(pdf_path)
    labels = classifier(pdf_path)

    routes = []
    with pymupdf.open(pdf_path) as pdf:
        for i, (page, label) in enumerate(zip(pdf, labels)):
            has_text_layer = label in ("digital", "mixed")
            routes.append(
                PageRoute(
                    page_number=i,
                    label=label,
                    use_parser=has_text_layer,
                    use_ocr=label in ("scanned", "mixed"),
                    use_tables=has_text_layer and _has_tables(page),
                )
            )
    return routes