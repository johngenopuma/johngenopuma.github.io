"""Make web-sized copies of photos for the gallery.

Usage: python3 tools/build_images.py path/to/photo.jpg [more photos...]

For each photo writes images/thumbs/<name>.webp (grid tile) and
images/fulls/<name>.webp (lightbox), where <name> is the lowercased file
stem. Camera rotation is applied and all metadata (EXIF, GPS) is dropped.
Keep originals outside this repo: everything here is published.
"""
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SIZES = {"thumbs": (1200, 78), "fulls": (2400, 82)}  # long edge px, WebP quality


def build(src: Path) -> None:
    name = src.stem.lower().replace(" ", "-")
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        for folder, (edge, quality) in SIZES.items():
            out = ROOT / "images" / folder / f"{name}.webp"
            copy = im.copy()
            copy.thumbnail((edge, edge), Image.LANCZOS)
            copy.save(out, "WEBP", quality=quality, method=6)
            print(f"{out.relative_to(ROOT)}  {copy.width}x{copy.height}  {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        build(Path(arg))
