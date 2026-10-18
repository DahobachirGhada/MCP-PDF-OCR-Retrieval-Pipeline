from abc import ABC, abstractmethod

from PIL import Image

from hybrid_rag.models.block import Block


class OCREngine(ABC):
    @abstractmethod
    def recognize(
        self, image: Image.Image, page_number: int, page_size: tuple[float, float], scale: float
    ) -> list[Block]:
        """Run OCR on a rendered page image and return text blocks.

        scale = pixels per PDF point (dpi / 72), used to map boxes back to PDF coordinates.
        """