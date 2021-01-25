A simple static-site generator powering my personal site.

## Usage

1. Install `commonmark` with `pip`
2. Populate the `content` directory with Markdown files
3. Run `python3 site.py`
4. Host the `_build` directory somewhere


## Metadata

The files in the `content` directory can have the following metadata:

- `slug`: represents the URL path that this file should be served from
- `title`: the title of the post to be used on the Posts page
- `published`: an ISO formatted date time representing when this post was published
