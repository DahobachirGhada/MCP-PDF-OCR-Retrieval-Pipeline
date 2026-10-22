#Each chunk gets metadata: page: 12, type: table, source: annual_report.pdf, section: Financial Results.
import hashlib

from hybrid_rag.models.chunk import Chunk


def make_chunk(source, page, kind, section, text, index, ocr_confidence=None) -> Chunk:
    # page is 0-based inside the pipeline; metadata stores it 1-based for humans
    parts = [source, section, f"page {page + 1}"]
    if kind == "table":
        parts.append("table")
    context = " | ".join(p for p in parts if p)

    digest = hashlib.sha1(f"{source}|{index}|{text}".encode("utf-8")).hexdigest()[:16]

    metadata = {
        "source": source,
        "page": page + 1,
        "type": kind,             # text | ocr | table
        "section": section,       # "" when unknown: Chroma rejects None
        "chunk_index": index,
        "n_chars": len(text),
    }
    if ocr_confidence is not None:
        metadata["ocr_confidence"] = round(ocr_confidence, 1)

    return Chunk(id=digest, text=text, context=context, metadata=metadata)