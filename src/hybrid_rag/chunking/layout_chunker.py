#text is split into parapgraph sized chunks
import re
from dataclasses import dataclass

from hybrid_rag.chunking.metadata_enricher import make_chunk
from hybrid_rag.chunking.semantic_chunker import normalize, split_text
from hybrid_rag.chunking.table_chunker import table_texts
from hybrid_rag.models.chunk import Chunk
from hybrid_rag.models.document import Document
from hybrid_rag.models.table import Table

NUMBERED = re.compile(r"^(\d+(\.\d+)*[.)]?|[IVXLC]+[.)]|[A-Z][.)])\s+[^\W\d_]")
KEYWORDS = re.compile(
    r"^(article|chapter|section|part|annex|chapitre|titre|annexe|المادة|الفصل|الباب|ملحق)\b",
    re.IGNORECASE,
)
MAX_HEADING_CHARS = 100


@dataclass
class ChunkingConfig:
    max_chars: int = 1000
    overlap_chars: int = 150
    max_table_chars: int = 3000


def is_heading(block) -> bool:
    text = " ".join(block.text.split())
    if not text or len(text) > MAX_HEADING_CHARS or block.text.strip().count("\n") > 1:
        return False
    if text.endswith((".", ",", ";", "،")):
        return False
    letters = [c for c in text if c.isalpha()]
    if len(letters) < 3:
        return False
    if NUMBERED.match(text) or KEYWORDS.match(text):
        return True
    return sum(c.isupper() for c in letters) / len(letters) >= 0.8


class LayoutChunker:
    def __init__(self, config: ChunkingConfig | None = None):
        self.cfg = config or ChunkingConfig()

    def chunk(self, doc: Document) -> list[Chunk]:
        self.doc, self.chunks, self.buffer, self.section, self.index = doc, [], [], "", 0

        for page in doc.pages:
            for el in page.elements:
                if isinstance(el, Table):
                    self._flush()
                    self._add_table(el)
                elif is_heading(el):
                    self._flush()
                    self.section = " ".join(el.text.split())[:120]
                    self.buffer.append(el)      # keep the heading text in the body too
                else:
                    self.buffer.append(el)
            self._flush()                       # chunks never cross a page boundary
        return self.chunks

    def _flush(self):
        if not self.buffer:
            return
        text = "\n".join(t for t in (normalize(b.text) for b in self.buffer) if t)
        page = self.buffer[0].page_number
        kind = "ocr" if any(b.source == "tesseract" for b in self.buffer) else "text"
        confs = [b.confidence for b in self.buffer if b.confidence is not None]
        conf = sum(confs) / len(confs) if confs else None

        for piece in split_text(text, self.cfg.max_chars, self.cfg.overlap_chars):
            self._append(page, kind, piece, conf)
        self.buffer = []

    def _add_table(self, table: Table):
        for piece in table_texts(table, self.cfg.max_table_chars):
            self._append(table.page_number, "table", piece, None)

    def _append(self, page, kind, text, confidence):
        self.chunks.append(
            make_chunk(self.doc.source, page, kind, self.section, text, self.index, confidence)
        )
        self.index += 1


def chunk_document(doc: Document, config: ChunkingConfig | None = None) -> list[Chunk]:
    return LayoutChunker(config).chunk(doc)