import camelot
import pymupdf

from hybrid_rag.ingestion.page_router import PageRoute
from hybrid_rag.models.table import Table
from hybrid_rag.tables.table_cleaner import clean_table
from hybrid_rag.tables.table_to_markdown import to_markdown

MIN_ROWS = 2
MIN_COLS = 2
MIN_STREAM_ACCURACY = 80   # stream mode guesses, so it needs a quality bar


def _to_top_left(bbox, page_height):
    # Camelot uses PDF coordinates (origin bottom-left); Block uses top-left
    x0, y0, x1, y1 = bbox
    return (x0, page_height - y1, x1, page_height - y0)


def extract_tables(pdf_path, routes: list[PageRoute]) -> list[Table]:
    pages = [r.page_number for r in routes if r.use_tables]
    if not pages:
        return []

    with pymupdf.open(pdf_path) as pdf:
        heights = {p: pdf[p].rect.height for p in pages}

    results: list[Table] = []
    covered: set[int] = set()

    for flavor in ("lattice", "stream"):
        remaining = [p for p in pages if p not in covered]
        if not remaining:
            break

        found = camelot.read_pdf(
            str(pdf_path),
            pages=",".join(str(p + 1) for p in remaining),   # Camelot is 1-based
            flavor=flavor,
        )

        for t in found:
            page = t.page - 1
            accuracy = t.parsing_report["accuracy"]
            rows = clean_table(t.df)

            if len(rows) < MIN_ROWS or len(rows[0]) < MIN_COLS:
                continue
            if flavor == "stream" and accuracy < MIN_STREAM_ACCURACY:
                continue

            results.append(
                Table(
                    page_number=page,
                    bbox=_to_top_left(t._bbox, heights[page]),
                    rows=rows,
                    markdown=to_markdown(rows),
                    flavor=flavor,
                    accuracy=accuracy,
                )
            )
            covered.add(page)

    return sorted(results, key=lambda t: (t.page_number, t.bbox[1]))