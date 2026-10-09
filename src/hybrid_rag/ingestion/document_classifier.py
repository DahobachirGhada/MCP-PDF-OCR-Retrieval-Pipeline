import pymupdf

MIN_CHARS = 50          # below this, a page has no real text layer
IMAGE_COVERAGE = 0.5    # fraction of the page covered by images

def classifier(pdf_path):
    """Return one label per page: digital, scanned, mixed or blank."""
    labels = []
    with pymupdf.open(pdf_path) as pdf:
        for page in pdf:
            chars = len(page.get_text().strip())
            image_area = sum(
                abs(rect)
                for img in page.get_images(full=True)
                for rect in page.get_image_rects(img[0])
            )
            coverage = min(image_area / abs(page.rect), 1.0)

            if chars < MIN_CHARS:
                labels.append("scanned" if coverage >= IMAGE_COVERAGE else "blank")
            else:
                labels.append("digital" if coverage < IMAGE_COVERAGE else "mixed")
    return labels