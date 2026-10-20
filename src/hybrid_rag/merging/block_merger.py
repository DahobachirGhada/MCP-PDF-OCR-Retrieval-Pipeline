#merge Text Blocks + Tables + OCR output
from hybrid_rag.merging.deduplicator import remove_covered
from hybrid_rag.models.block import Block
from hybrid_rag.parsing.reading_order import order_blocks

TABLE_OVERLAP = 0.6    # text this covered by a table is a duplicate of it
PARSER_OVERLAP = 0.5   # OCR this covered by parser text is a duplicate


def merge_page(page_number, size, parsed, ocr, tables) -> list:
    width, height = size
    table_boxes = [t.bbox for t in tables]

    # 1. text inside a table would duplicate its content
    parsed = remove_covered(parsed, table_boxes, TABLE_OVERLAP)
    ocr = remove_covered(ocr, table_boxes, TABLE_OVERLAP)

    # 2. parser text is exact; OCR only keeps what the parser did not see
    ocr = remove_covered(ocr, [b.bbox for b in parsed], PARSER_OVERLAP)

    # 3. order everything together; tables are wrapped as placeholder blocks
    items = parsed + ocr
    placeholders = {}
    for t in tables:
        ph = Block(page_number, t.bbox, t.markdown, width, height, "table")
        placeholders[id(ph)] = t
        items.append(ph)

    ordered = order_blocks(items)
    return [placeholders.get(id(b), b) for b in ordered]