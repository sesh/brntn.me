import os
import glob
from pathlib import Path
import shutil
from datetime import datetime

import commonmark


PAGE_TEMPLATE = open('theme/page.html', 'r').read()
POST_TEMPLATE = open('theme/post.html', 'r').read()


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def render_template(output, **kwargs):
    """
    Template renderer that replaces 'handlebars-like' tags with content
    """
    template_tags = ['content', 'published', 'permalink', 'published_formatted']
    for k, v in kwargs.items():
        if k in template_tags:
            output = output.replace('{{ ' + k + ' }}', v)

    return output


def load_post(fn):
    content = open(fn).read()
    headers = {}

    md = ""
    for l in content.splitlines():
        if l.startswith('<!--') and l.endswith('-->'):
            l = l.replace('<!-- ', '').replace(' -->', '')
            k, v = l.split(':', 1)
            headers[k.strip()] = v.strip()
        else:
            md += l + '\n'

    if fn.endswith('.md'):
        # remove comments
        rendered = commonmark.commonmark(md)

    if 'slug' not in headers:
        print(f"Missing slug for {fn}")
        return None

    if 'published' not in headers:
        print(f"Missing published time for {fn}")
        return None

    headers['permalink'] = "/" + headers['slug']
    headers['published_formatted'] = datetime.fromisoformat(headers['published'].replace('Z', '')).strftime('%B %d, %Y')

    print(headers['published_formatted'], headers['published'])
    return (headers, rendered)


def render_post(headers, content, *, build_dir):
    template = headers.get('template', 'post')

    fn = build_dir / headers['slug']  # must be set
    fn.mkdir(parents=True, exist_ok=True)
    fn = fn / 'index.html'

    with open(fn, 'w') as f:
        if template == 'page':
            f.write(render_template(PAGE_TEMPLATE, content=content, **headers))
        else:
            content = render_template(POST_TEMPLATE, content=content, **headers)
            f.write(render_template(PAGE_TEMPLATE, content=content))


def render_post_list(posts, *, build_dir):
    # TODO: Pagination
    fn = build_dir / 'posts'
    fn.mkdir(parents=True, exist_ok=True)

    for i, chunk in enumerate(chunks(posts, 5)):
        output = ""

        for headers, content in chunk:
            output += render_template(POST_TEMPLATE, content=content, **headers) + "\n\n"

        if i == 0:
            out_fn = fn / 'index.html'
        else:
            out_fn = fn / f'page-{i}.html'

        with open(out_fn, 'w') as f:
            f.write(render_template(PAGE_TEMPLATE, content=output))


def blog():
    p = Path('.')

    build_dir = p / '_build'
    content_dir = p / 'content'
    public_dir = p / 'public'
    theme_dir = p / 'theme'


    # remove the build directory
    if build_dir.exists():
        shutil.rmtree(build_dir)

    # public: copy public files to the build directory
    shutil.copytree(public_dir, build_dir)

    # static: copy static files from the theme
    shutil.copytree(theme_dir / 'static', build_dir / 'static', dirs_exist_ok=True)

    # load all posts, filter out pad posts and sort by published date
    posts = [load_post(str(f)) for f in content_dir.rglob('*.md')]
    posts = [p for p in posts if p]
    posts = sorted(posts, key=lambda p: p[0]['published'], reverse=True)

    # render all posts
    for headers, content in posts:
        render_post(headers, content, build_dir=build_dir)

    # remove pages before rendering post list / feed
    posts = [p for p in posts if p[0].get('template') != 'page']
    render_post_list(posts, build_dir=build_dir)


if __name__ == "__main__":
    blog()
