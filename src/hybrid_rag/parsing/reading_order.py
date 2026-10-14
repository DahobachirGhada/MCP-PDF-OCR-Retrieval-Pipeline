#Reading order handles one or two columns, with full-width blocks (titles) splitting the page into bands.

FULL_WIDTH = 0.6   # a block this wide (fraction of page) spans all columns


def _is_full_width(b) -> bool:
    return (b.bbox[2] - b.bbox[0]) >= FULL_WIDTH * b.page_width


def _center_x(b) -> float:
    return (b.bbox[0] + b.bbox[2]) / 2


def _flush(band: list, mid: float) -> list:
    left = [b for b in band if _center_x(b) < mid]
    right = [b for b in band if _center_x(b) >= mid]
    by_y = lambda b: (b.bbox[1], b.bbox[0])
    if left and right:                       # two columns: left first, then right
        return sorted(left, key=by_y) + sorted(right, key=by_y)
    return sorted(band, key=by_y)


def order_blocks(blocks: list) -> list:
    if not blocks:
        return []
    mid = blocks[0].page_width / 2
    ordered, band = [], []
    for b in sorted(blocks, key=lambda b: (b.bbox[1], b.bbox[0])):
        if _is_full_width(b):                # titles split the page into bands
            ordered += _flush(band, mid)
            band = []
            ordered.append(b)
        else:
            band.append(b)
    ordered += _flush(band, mid)
    return ordered