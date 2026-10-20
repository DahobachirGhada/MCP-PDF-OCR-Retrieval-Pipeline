from dataclasses import dataclass

from hybrid_rag.models.page import Page
from hybrid_rag.models.table import Table


@dataclass
class Document:
    source: str
    pages: list[Page]

    def to_text(self) -> str:
        """Readable dump, mainly for debugging and tests."""
        parts = []
        for page in self.pages:
            parts.append(f"--- page {page.page_number + 1} ({page.label}) ---")
            for el in page.elements:
                parts.append(el.markdown if isinstance(el, Table) else el.text)
        return "\n\n".join(parts)