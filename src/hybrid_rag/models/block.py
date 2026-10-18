from dataclasses import dataclass


@dataclass
class Block:
    page_number: int
    bbox: tuple[float, float, float, float]   # x0, y0, x1, y1
    text: str
    page_width: float
    page_height: float
    source: str = "pymupdf"
    confidence: float | None = None 