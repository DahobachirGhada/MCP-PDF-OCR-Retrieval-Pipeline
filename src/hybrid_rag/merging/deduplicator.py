#Remove duplicates (example text that both PyMuPDF and OCR captured).
def overlap_ratio(a, b) -> float:
    """Fraction of box a's area that is covered by box b."""
    ix0, iy0 = max(a[0], b[0]), max(a[1], b[1])
    ix1, iy1 = min(a[2], b[2]), min(a[3], b[3])
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    inter = (ix1 - ix0) * (iy1 - iy0)
    area = (a[2] - a[0]) * (a[3] - a[1])
    return inter / area if area > 0 else 0.0


def remove_covered(blocks: list, boxes: list, threshold: float) -> list:
    """Drop blocks that are mostly inside any of the given boxes."""
    return [
        b for b in blocks
        if not any(overlap_ratio(b.bbox, box) >= threshold for box in boxes)
    ]