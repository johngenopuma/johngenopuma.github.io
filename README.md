# gracegilhool.com

Grace Gilhool's photography and architecture site, served by GitHub Pages
from this repo (`main` branch, custom domain in `CNAME`).

## Updating

1. Put new originals in `originals/` (gitignored, never published).
2. Make web copies: `python3 tools/build_images.py originals/<folder>/<photo>.jpg`
   (writes `images/thumbs/` and `images/fulls/`, trims Instagram padding, strips GPS).
3. Edit `content.json`: photo order, titles, captions, categories, architecture
   projects, bio and services.
4. Rebuild the pages: `python3 tools/build_site.py`
5. Commit and push; GitHub Pages deploys in about a minute.

Preview locally with `python3 -m http.server 8765` and open http://localhost:8765.

The contact form posts through FormSubmit (`FORM_ACTION` in `tools/build_site.py`).
