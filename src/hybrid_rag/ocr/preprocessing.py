import pymupdf
from PIL import Image, ImageFilter, ImageOps

DEFAULT_DPI = 300


def render_page(page, dpi: int = DEFAULT_DPI) -> Image.Image:
    pix = page.get_pixmap(dpi=dpi)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def preprocess(image: Image.Image) -> Image.Image:
    image = ImageOps.grayscale(image)
    image = ImageOps.autocontrast(image, cutoff=1)   # fixes faded or uneven scans
    return image.filter(ImageFilter.SHARPEN)