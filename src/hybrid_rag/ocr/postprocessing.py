#removes blocks Tesseract wasn’t confident about, 
#blocks made mostly of symbols (borders, stamps, scanner noise), and fixes hyphenation and spacing.

import re

MIN_BLOCK_CONF = 50
MIN_ALNUM_RATIO = 0.4


def _fix_text(text: str) -> str:
    # join words split by a line-end hyphen: "exam-\nple" -> "example"
    text = re.sub(r"([a-zà-öø-ÿ])-\n([a-zà-öø-ÿ])", r"\1\2", text)
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def _is_noise(text: str) -> bool:
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return True
    return sum(c.isalnum() for c in chars) / len(chars) < MIN_ALNUM_RATIO


def clean_blocks(blocks: list) -> list:
    cleaned = []
    for b in blocks:
        if b.confidence is not None and b.confidence < MIN_BLOCK_CONF:
            continue
        b.text = _fix_text(b.text)
        if not b.text or _is_noise(b.text):
            continue
        cleaned.append(b)
    return cleaned
