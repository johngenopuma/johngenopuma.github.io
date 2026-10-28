"""Generate index.html and architecture.html from content.json.

Usage: python3 tools/build_site.py

Edit content.json (order, titles, captions, bio), run this, commit the
result. Photo dimensions are read from images/thumbs so the gallery can lay
every photo out at its real shape. Asset URLs carry a content hash so a
deploy is never served a stale stylesheet or script.
"""
import hashlib
import json
from html import escape
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://gracegilhool.com"
FORM_ACTION = "https://formsubmit.co/johnpuma@stanford.edu"
INSTAGRAM = "https://www.instagram.com/gracegilhoolpictures/"
EAGER = 6  # gallery photos fetched immediately; the rest load as they scroll in


def asset(name: str) -> str:
    digest = hashlib.sha1((ROOT / name).read_bytes()).hexdigest()[:8]
    return f"{name}?v={digest}"


def dims(slug: str) -> tuple:
    with Image.open(ROOT / "images" / "thumbs" / f"{slug}.webp") as im:
        return im.size


def photo(slug: str, alt: str, title: str, caption: str, eager: bool) -> str:
    w, h = dims(slug)
    loading = "" if eager else ' loading="lazy"'
    return (
        f'<a href="images/fulls/{slug}.webp" data-title="{escape(title)}" data-caption="{escape(caption)}">'
        f'<img src="images/thumbs/{slug}.webp" width="{w}" height="{h}" alt="{escape(alt)}"{loading} decoding="async"></a>'
    )


def page(title: str, description: str, current: str, body: str) -> str:
    nav = [("./", "Photography"), ("architecture.html", "Architecture<span class=\"nav-long\"> &amp; Design</span>"),
           ("./#about", "About"), ("./#contact", "Contact")]
    links = "".join(
        f'<a href="{href}"{" aria-current=\"page\"" if label.startswith(current) else ""}>{label}</a>'
        for href, label in nav)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{SITE}/images/fulls/beret-portrait.webp">
<link rel="icon" href="favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,400&amp;family=Inter:wght@400;500&amp;display=swap">
<link rel="stylesheet" href="{asset("styles.css")}">
</head>
<body>
<header class="site-header">
  <a class="wordmark" href="./">Grace Gilhool</a>
  <nav>{links}</nav>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <p>&copy; Grace Gilhool &middot; <a href="{INSTAGRAM}">Instagram</a> &middot; <a href="mailto:gracegilhool@gmail.com">gracegilhool@gmail.com</a></p>
  <p class="credit">Site by <a href="https://www.linkedin.com/in/johnpumayalli/">John Pumayalli</a></p>
</footer>
<dialog class="lightbox" aria-label="Photo viewer">
  <button class="lb-close" type="button" aria-label="Close">&times;</button>
  <button class="lb-prev" type="button" aria-label="Previous photo">&#8249;</button>
  <figure><img alt=""><figcaption><strong></strong><span></span></figcaption></figure>
  <button class="lb-next" type="button" aria-label="Next photo">&#8250;</button>
</dialog>
<script src="{asset("site.js")}" defer></script>
</body>
</html>
"""


def index(c: dict) -> str:
    filters = '<button type="button" data-filter="all" aria-pressed="true">All</button>' + "".join(
        f'<button type="button" data-filter="{k}" aria-pressed="false">{escape(v)}</button>'
        for k, v in c["categories"].items())
    figures = "\n".join(
        f'  <figure data-tag="{p["tag"]}" style="--r:{dims(p["slug"])[0] / dims(p["slug"])[1]:.3f}">'
        f'{photo(p["slug"], p["alt"], p["title"], p["caption"], i < EAGER)}</figure>'
        for i, p in enumerate(c["photography"]))
    about = "\n".join(f"    <p>{escape(p)}</p>" for p in c["about"])
    services = "".join(f'<li><a href="#contact" data-shoot="{escape(s)}">{escape(s)}</a></li>' for s in c["services"])
    options = "".join(f"<option>{escape(s)}</option>" for s in c["services"])
    body = f"""<section class="intro">
  <h1>Portraits, events, sports, and food. Based in Telluride and Boulder, Colorado.</h1>
  <p>Now booking senior portraits, headshots, and events. <a href="#contact">Get in touch</a></p>
</section>
<section id="work" class="work" aria-label="Photography">
  <div class="filters" role="group" aria-label="Filter photos">{filters}</div>
  <div class="gallery" data-lightbox>
{figures}
  </div>
</section>
<section id="about" class="about">
  <h2>About</h2>
  <div class="about-body">
{about}
  </div>
  <div class="services">
    <h3>Book a shoot</h3>
    <ul>{services}</ul>
  </div>
</section>
<section id="contact" class="contact">
  <h2>Get in touch</h2>
  <form id="contact-form" method="post" action="{FORM_ACTION}">
    <input type="hidden" name="_subject" value="New message from gracegilhool.com">
    <input type="hidden" name="_template" value="table">
    <input type="text" name="_honey" class="honey" tabindex="-1" autocomplete="off" aria-hidden="true">
    <label>Name<input type="text" name="name" autocomplete="name" required></label>
    <label>Email<input type="email" name="email" autocomplete="email" required></label>
    <label>What are you looking for?<select name="shoot"><option value="">Choose one (optional)</option>{options}<option>Something else</option></select></label>
    <label class="wide">Message<textarea name="message" rows="5" required></textarea></label>
    <div class="wide actions"><button type="submit">Send</button><p class="status" role="status"></p></div>
  </form>
</section>"""
    return page("Grace Gilhool | Photography",
                "Grace Gilhool photographs portraits, events, sports, and food. Based in Telluride and Boulder, Colorado.",
                "Photography", body)


def architecture(c: dict) -> str:
    projects = []
    for i, p in enumerate(c["architecture"]):
        imgs = "".join(photo(im["slug"], im["alt"], p["title"], "", i < 2) for im in p["images"])
        projects.append(f"""  <article class="project">
    <div class="project-images" data-count="{len(p["images"])}">{imgs}</div>
    <div class="project-text">
      <p class="kind">{escape(p["kind"])}</p>
      <h2>{escape(p["title"])}</h2>
      <p>{escape(p["text"])}</p>
    </div>
  </article>""")
    body = f"""<section class="intro">
  <h1>Architecture and design work from CU Boulder and Copenhagen.</h1>
</section>
<section class="projects" data-lightbox>
{chr(10).join(projects)}
</section>"""
    return page("Architecture & Design | Grace Gilhool",
                "Architecture models and furniture by Grace Gilhool, from CU Boulder and a study abroad in Copenhagen.",
                "Architecture", body)


if __name__ == "__main__":
    content = json.loads((ROOT / "content.json").read_text())
    for name, render in [("index.html", index), ("architecture.html", architecture)]:
        (ROOT / name).write_text(render(content))
        print("wrote", name)
