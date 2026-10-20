from dataclasses import dataclass, field

from hybrid_rag.models.block import Block
from hybrid_rag.models.table import Table

Element = Block | Table


@dataclass
class Page:
    page_number: int          # 0-based
    label: str                # digital | scanned | mixed | blank
    width: float
    height: float
    elements: list[Element] = field(default_factory=list)   # in reading order