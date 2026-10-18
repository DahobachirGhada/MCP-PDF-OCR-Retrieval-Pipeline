import os
import shutil
from collections import defaultdict

import pytesseract
from pytesseract import Output

from hybrid_rag.models.block import Block
from hybrid_rag.ocr.base import OCREngine

WINDOWS_DEFAULT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def _configure_binary(tesseract_cmd: str | None):
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    elif not shutil.which("tesseract") and os.path.exists(WINDOWS_DEFAULT):
        pytesseract.pytesseract.tesseract_cmd = WINDOWS_DEFAULT


class TesseractEngine(OCREngine):
    def __init__(self, languages="fra+eng", psm=3, min_word_conf=30, tesseract_cmd=None):
        _configure_binary(tesseract_cmd)
        self.languages = languages
        self.config = f"--psm {psm}"        # 3 = fully automatic page segmentation
        self.min_word_conf = min_word_conf

    def recognize(self, image, page_number, page_size, scale):
        data = pytesseract.image_to_data(
            image, lang=self.languages, config=self.config, output_type=Output.DICT
        )

        # Tesseract groups words as block -> paragraph -> line; we keep paragraphs.
        paragraphs = defaultdict(lambda: defaultdict(list))
        for i, raw in enumerate(data["text"]):
            word = raw.strip()
            conf = float(data["conf"][i])
            if not word or conf < self.min_word_conf:   # conf is -1 for non-words
                continue
            key = (data["block_num"][i], data["par_num"][i])
            x, y = data["left"][i], data["top"][i]
            w, h = data["width"][i], data["height"][i]
            paragraphs[key][data["line_num"][i]].append((word, conf, x, y, x + w, y + h))

        width, height = page_size
        blocks = []
        for lines in paragraphs.values():
            words = [w for line in lines.values() for w in line]
            text = "\n".join(
                " ".join(w[0] for w in lines[n]) for n in sorted(lines)
            )
            bbox = (
                min(w[2] for w in words) / scale,
                min(w[3] for w in words) / scale,
                max(w[4] for w in words) / scale,
                max(w[5] for w in words) / scale,
            )
            confidence = sum(w[1] for w in words) / len(words)
            blocks.append(
                Block(page_number, bbox, text, width, height, "tesseract", confidence)
            )
        return blocks