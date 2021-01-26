import os
import glob
from pathlib import Path
import shutil
from datetime import datetime
import subprocess

import commonmark


PAGE_TEMPLATE = open("theme/page.html", "r").read()
POST_TEMPLATE = open("theme/post.html", "r").read()

STATIC_SITES = [
    ("/calendar/", "https://github.com/sesh/calendar.git"),
    ("/runcalc/", "https://api.glitch.com/git/runcalc"),
    ("/scratchpad/", "https://github.com/sesh/scratchpad.git")
]


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def render_template(output, **kwargs):
    """
    Template renderer that replaces 'handlebars-like' tags with content
    """
    template_tags = ["content", "published", "permalink", "published_formatted"]
    for k, v in kwargs.items():
        if k in template_tags:
            output = output.replace("{{ " + k + " }}", v)

    return output


def load_post(fn):
    content = open(fn).read()
    headers = {}

    md = ""
    for l in content.splitlines():
        if l.startswith("<!--") and l.endswith("-->"):
            l = l.replace("<!-- ", "").replace(" -->", "")
            k, v = l.split(":", 1)
            headers[k.strip()] = v.strip()
        else:
            md += l + "\n"

    if fn.endswith(".md"):
        # remove comments
        rendered = commonmark.commonmark(md)

    if "slug" not in headers:
        print(f"Missing slug for {fn}")
        return None

    if "published" not in headers:
        print(f"Missing published time for {fn}")
        return None

    if headers["slug"].startswith("/"):
        headers["slug"] = headers["slug"][1:]

    headers["permalink"] = "/" + headers["slug"]
    headers["published_formatted"] = datetime.fromisoformat(
        headers["published"].replace("Z", "")
    ).strftime("%B %d, %Y")

    return (headers, rendered)


def render_post(headers, content, *, build_dir):
    template = headers.get("template", "post")

    fn = build_dir / headers["slug"]  # must be set
    fn.mkdir(parents=True, exist_ok=True)
    fn = fn / "index.html"

    with open(fn, "w") as f:
        if template == "page":
            f.write(render_template(PAGE_TEMPLATE, content=content, **headers))
        else:
            content = render_template(POST_TEMPLATE, content=content, **headers)
            f.write(render_template(PAGE_TEMPLATE, content=content))


def render_post_list(posts, *, build_dir):
    fn = build_dir / "posts"
    fn.mkdir(parents=True, exist_ok=True)

    next_url = ""
    previous_url = ""

    for i, chunk in enumerate(chunks(posts, 5)):
        output = ""

        for headers, content in chunk:
            output += (
                render_template(POST_TEMPLATE, content=content, **headers) + "\n\n"
            )

        if i == 0:
            out_fn = fn / "index.html"
        else:
            out_fn = fn / f"page-{i}.html"

        next_url = str(fn / f"page-{i + 1}.html").replace(str(build_dir), "")

        output += "<div class='pagination'>"
        if previous_url:
            output += f"<a href='{previous_url}'>&larr; Previous</a>"

        if next_url:
            output += f"<a href='{next_url}'>Next &rarr;</a>"
        output += "</div>"

        with open(out_fn, "w") as f:
            f.write(render_template(PAGE_TEMPLATE, content=output))


        previous_url = str(out_fn).replace(str(build_dir), "")


def clone_repo(repo, path):
    output = subprocess.run(["git", "clone", repo, path], check=True)
    shutil.rmtree(path / '.git')


def blog():
    p = Path(".")

    build_dir = p / "_build"
    content_dir = p / "content"
    public_dir = p / "public"
    theme_dir = p / "theme"

    # remove the build directory
    if build_dir.exists():
        shutil.rmtree(build_dir)

    # public: copy public files to the build directory
    shutil.copytree(public_dir, build_dir)

    with open(build_dir / "CNAME", "w") as f:
        f.write("brntn.me")

    # static: copy static files from the theme
    shutil.copytree(theme_dir / "static", build_dir / "static", dirs_exist_ok=True)

    # clone static sites
    for slug, repo in STATIC_SITES:
        if slug.startswith("/"):
            slug = slug[1:]

        clone_repo(repo, build_dir / slug)

    # load all posts, filter out pad posts and sort by published date
    posts = [load_post(str(f)) for f in content_dir.rglob("*.md")]
    posts = [p for p in posts if p]
    posts = sorted(posts, key=lambda p: p[0]["published"], reverse=True)

    # render all posts
    for headers, content in posts:
        render_post(headers, content, build_dir=build_dir)

    # remove pages before rendering post list / feed
    posts = [p for p in posts if p[0].get("template") != "page"]
    render_post_list(posts, build_dir=build_dir)


if __name__ == "__main__":
    blog()
