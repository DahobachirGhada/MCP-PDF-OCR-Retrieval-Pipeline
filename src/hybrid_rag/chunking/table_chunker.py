from hybrid_rag.models.table import Table
from hybrid_rag.tables.table_to_markdown import to_markdown


def table_texts(table: Table, max_chars: int) -> list[str]:
    if len(table.markdown) <= max_chars:
        return [table.markdown]                 # normal case: one table, one chunk

    header, *body = table.rows
    pieces, current = [], []
    for row in body:
        if current and len(to_markdown([header] + current + [row])) > max_chars:
            pieces.append(to_markdown([header] + current))
            current = []
        current.append(row)
    if current:
        pieces.append(to_markdown([header] + current))
    return pieces