#!/usr/bin/env python3
"""
Build the blog: convert markdown posts in blog/posts/ to HTML, generate a blog
index page, and update the home page's blog preview block in place.

Usage:
    python3 build_blog.py
"""
from __future__ import annotations

import datetime as dt
import re
from html import escape
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
POSTS_DIR = ROOT / "blog" / "posts"
BLOG_DIR = ROOT / "blog"
TEMPLATE_POST = BLOG_DIR / "template_post.html"
HOME_INDEX = ROOT / "index.html"
BLOG_INDEX = BLOG_DIR / "index.html"

HOME_MARKER_START = "<!-- BLOG:POSTS:START -->"
HOME_MARKER_END = "<!-- BLOG:POSTS:END -->"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def parse_post(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(raw)
    if not m:
        raise ValueError(f"{path.name}: missing frontmatter (--- ... ---)")
    fm_text, body = m.groups()

    fm = {}
    for line in fm_text.splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip()

    for required in ("title", "date", "excerpt"):
        if required not in fm:
            raise ValueError(f"{path.name}: missing frontmatter field '{required}'")

    try:
        date = dt.date.fromisoformat(fm["date"])
    except ValueError as e:
        raise ValueError(f"{path.name}: bad date '{fm['date']}', expected YYYY-MM-DD") from e

    slug = path.stem
    if re.match(r"^\d{4}-\d{2}-\d{2}-", slug):
        slug = slug[11:]

    html_body = markdown.markdown(body, extensions=["fenced_code", "tables"])

    return {
        "slug": slug,
        "filename": path.name,
        "title": fm["title"],
        "date": date,
        "excerpt": fm["excerpt"],
        "body_html": html_body,
        "out_path": BLOG_DIR / f"{slug}.html",
    }


def render_post(post: dict, template: str) -> str:
    return (
        template
        .replace("{{TITLE}}", escape(post["title"]))
        .replace("{{EXCERPT}}", escape(post["excerpt"]))
        .replace("{{DATE_DISPLAY}}", post["date"].strftime("%B %d, %Y").upper())
        .replace("{{CONTENT}}", post["body_html"])
    )


def render_blog_index(posts: list[dict]) -> str:
    cards = []
    for p in posts:
        cards.append(f"""
        <a href="{escape(p['slug'])}.html" class="block p-8 md:p-12 border-b grid-border hover:bg-[var(--hover-bg)] transition-colors group">
            <span class="text-[10px] font-doto tracking-[0.2em] uppercase opacity-50 font-bold">{p['date'].strftime('%B %d, %Y')}</span>
            <h2 class="text-3xl md:text-4xl font-heading font-bold uppercase tracking-tight mt-3 mb-3 group-hover:text-accent transition-colors">{escape(p['title'])}</h2>
            <p class="text-base opacity-70 leading-relaxed">{escape(p['excerpt'])}</p>
            <span class="inline-block mt-4 text-[10px] font-doto tracking-[0.2em] uppercase font-bold text-accent">Read →</span>
        </a>""")

    return f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog · Abhiram Yenugadhati</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Doto:wght@100..900&family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {{ darkMode: 'class', theme: {{ extend: {{ fontFamily: {{
            sans: ['Inter', 'sans-serif'],
            heading: ['Space Grotesk', 'sans-serif'],
            doto: ['Doto', 'sans-serif'],
        }}}}}}}}
    </script>
    <style>
        :root {{ --bg-color: #F8F8F8; --text-color: #0A0A0A; --accent-primary: #00FF88; --border-color: rgba(0,0,0,0.2); --hover-bg: rgba(0,0,0,0.05); }}
        html.dark {{ --bg-color: #0A0A0A; --text-color: #F4F4F0; --border-color: rgba(255,255,255,0.2); --hover-bg: rgba(255,255,255,0.05); }}
        body {{ background: var(--bg-color); color: var(--text-color); font-family: 'Inter', sans-serif; }}
        .text-accent {{ color: var(--accent-primary); }}
        .grid-border {{ border-color: var(--border-color); }}
    </style>
</head>
<body class="font-sans antialiased">
    <nav class="border-b grid-border" style="background-color: var(--bg-color);">
        <div class="max-w-[1800px] mx-auto px-5 md:px-8 py-5 flex items-center justify-between border-x grid-border">
            <a href="../index.html" class="text-2xl font-doto font-bold tracking-tight hover:text-accent transition-colors">AY</a>
            <a href="../index.html" class="font-doto text-[10px] tracking-[0.2em] uppercase font-bold hover:text-accent">← Home</a>
        </div>
    </nav>
    <header class="border-b grid-border p-8 md:p-16">
        <div class="max-w-5xl mx-auto">
            <p class="text-[10px] tracking-[0.4em] uppercase opacity-50 font-bold font-doto mb-4">// FIELD NOTES</p>
            <h1 class="text-5xl md:text-7xl font-heading font-bold uppercase tracking-tighter">Blog</h1>
        </div>
    </header>
    <main class="max-w-5xl mx-auto">
        {''.join(cards) if cards else '<p class="p-16 text-center opacity-50">No posts yet.</p>'}
    </main>
    <footer class="border-t grid-border py-12 px-8 text-center mt-16">
        <p class="text-[10px] font-doto tracking-[0.2em] uppercase opacity-50">© 2026 Abhiram Yenugadhati</p>
    </footer>
    <script>
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.classList.toggle('dark', savedTheme === 'dark');
    </script>
</body>
</html>
"""


def render_home_preview(posts: list[dict]) -> str:
    if not posts:
        return """
            <div class="grid grid-cols-1 md:grid-cols-3">
                <div class="p-8 md:p-12 border-b md:border-b-0 md:border-r grid-border reveal">
                    <span class="text-[10px] font-doto opacity-50 tracking-[0.2em] uppercase">No posts yet</span>
                    <h4 class="text-2xl font-heading font-bold uppercase mt-4 mb-3">Coming Soon</h4>
                </div>
            </div>"""

    cards = []
    for i, p in enumerate(posts[:3]):
        # alternate border on right side for the first two cards on desktop
        border_classes = "border-b md:border-b-0 md:border-r grid-border" if i < 2 else "border-b md:border-b-0 grid-border"
        delay = f' style="transition-delay: {i * 0.1}s;"' if i else ""
        cards.append(f"""
                <a href="blog/{escape(p['slug'])}.html" class="block p-8 md:p-12 {border_classes} hover:bg-[var(--hover-bg)] transition-colors reveal group"{delay}>
                    <span class="text-[10px] font-doto tracking-[0.2em] uppercase opacity-50 font-bold">{p['date'].strftime('%b %d, %Y')}</span>
                    <h4 class="text-2xl font-heading font-bold uppercase tracking-tight mt-3 mb-3 group-hover:text-accent transition-colors">{escape(p['title'])}</h4>
                    <p class="text-sm opacity-70 leading-relaxed">{escape(p['excerpt'])}</p>
                    <span class="inline-block mt-4 text-[10px] font-doto tracking-[0.2em] uppercase font-bold text-accent">Read →</span>
                </a>""")

    # Add "view all" link if more than 3 posts
    view_all = ""
    if len(posts) > 3:
        view_all = '\n            <div class="p-8 md:p-12 text-center border-b grid-border reveal">\n                <a href="blog/index.html" class="font-doto text-xs tracking-[0.2em] uppercase font-bold hover:text-accent">View all posts →</a>\n            </div>'

    return f"""
            <div class="grid grid-cols-1 md:grid-cols-3">{''.join(cards)}
            </div>{view_all}"""


def update_home_index(preview_html: str) -> None:
    home = HOME_INDEX.read_text(encoding="utf-8")
    pattern = re.compile(
        re.escape(HOME_MARKER_START) + r".*?" + re.escape(HOME_MARKER_END),
        re.DOTALL,
    )
    replacement = f"{HOME_MARKER_START}{preview_html}\n            {HOME_MARKER_END}"
    new_home, n = pattern.subn(replacement, home, count=1)
    if n != 1:
        raise SystemExit(
            f"could not find blog markers in {HOME_INDEX} — expected "
            f"{HOME_MARKER_START} ... {HOME_MARKER_END}"
        )
    HOME_INDEX.write_text(new_home, encoding="utf-8")


def main() -> None:
    if not TEMPLATE_POST.exists():
        raise SystemExit(f"missing template: {TEMPLATE_POST}")

    template = TEMPLATE_POST.read_text(encoding="utf-8")

    md_files = sorted(POSTS_DIR.glob("*.md"))
    if not md_files:
        print("no posts found in", POSTS_DIR)
        update_home_index(render_home_preview([]))
        BLOG_INDEX.write_text(render_blog_index([]), encoding="utf-8")
        return

    posts = [parse_post(p) for p in md_files]
    posts.sort(key=lambda p: p["date"], reverse=True)

    for post in posts:
        post["out_path"].write_text(render_post(post, template), encoding="utf-8")
        print(f"  wrote {post['out_path'].relative_to(ROOT)}")

    BLOG_INDEX.write_text(render_blog_index(posts), encoding="utf-8")
    print(f"  wrote {BLOG_INDEX.relative_to(ROOT)}")

    update_home_index(render_home_preview(posts))
    print(f"  updated {HOME_INDEX.relative_to(ROOT)} blog preview block")

    print(f"\nbuilt {len(posts)} post(s).")


if __name__ == "__main__":
    main()
