#Header/footer removal works across the whole document, which is why it runs after all pages are extracted. 
#Normalizing digits means “Page 4” and “Page 5” count as the same footer.

import re
from collections import Counter

EDGE_RATIO = 0.08     # top/bottom 8% of the page counts as margin
MIN_PAGES = 3         # too few pages to detect repetition
REPEAT_RATIO = 0.5    # repeated on at least half the pages


def _normalize(text: str) -> str:
    # digits -> '#', so "Page 4" and "Page 5" match
    return re.sub(r"\d+", "#", " ".join(text.lower().split()))


def _in_margin(block) -> bool:
    top = block.bbox[1] < block.page_height * EDGE_RATIO
    bottom = block.bbox[3] > block.page_height * (1 - EDGE_RATIO)
    return top or bottom


def remove_headers_footers(pages: dict) -> dict:
    if len(pages) < MIN_PAGES:
        return pages

    counts = Counter()
    for blocks in pages.values():
        counts.update({_normalize(b.text) for b in blocks if _in_margin(b)})

    threshold = len(pages) * REPEAT_RATIO
    repeated = {text for text, n in counts.items() if n >= threshold}

    return {
        num: [
            b for b in blocks
            if not (_in_margin(b) and _normalize(b.text) in repeated)
        ]
        for num, blocks in pages.items()
    }