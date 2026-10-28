"""Make web-sized copies of photos for the gallery.

Usage: python3 tools/build_images.py path/to/photo.jpg [more photos...]

For each photo writes images/thumbs/<name>.webp (grid tile) and
images/fulls/<name>.webp (lightbox), where <name> is the lowercased file
stem. Camera rotation is applied, white padding (as on Instagram exports)
is trimmed, and all metadata (EXIF, GPS) is dropped. Originals live in
originals/, which is gitignored: everything committed here is published.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SIZES = {"thumbs": (1200, 78), "fulls": (2400, 82)}  # long edge px, WebP quality


def trim_box(im: Image.Image) -> tuple:
    """Box of the photo inside Instagram-style padding.

    Padding is centered, so only the white run shared by opposite edges is
    cut; a white studio backdrop touching one edge is left alone.
    """
    white = np.asarray(im.convert("L")) >= 245
    rows, cols = white.mean(axis=1) >= 0.98, white.mean(axis=0) >= 0.98

    def run(edge):
        # Exports often have a 1px gray hairline outside the padding.
        start = next((i for i in range(4) if edge[i]), None)
        if start is None or edge[start:].all():
            return 0
        return start + int(np.argmin(edge[start:]))

    v = min(run(rows), run(rows[::-1]))
    h = min(run(cols), run(cols[::-1]))
    return (h, v, im.width - h, im.height - v)


def build(src: Path) -> None:
    name = src.stem.lower().replace(" ", "-")
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        im = im.crop(trim_box(im))
        for folder, (edge, quality) in SIZES.items():
            out = ROOT / "images" / folder / f"{name}.webp"
            copy = im.copy()
            copy.thumbnail((edge, edge), Image.LANCZOS)
            copy.save(out, "WEBP", quality=quality, method=6)
            print(f"{out.relative_to(ROOT)}  {copy.width}x{copy.height}  {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        build(Path(arg))
