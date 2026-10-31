---
description: "md-iframe is a Python-Markdown extension for MkDocs and Zensical that embeds HTML pages as iframes that size themselves and report missing files."
---
# md-iframe

md-iframe is a Python-Markdown extension for MkDocs and Zensical sites. It turns an image-style tag into an `<iframe>` that sizes itself to the embedded page and shows a visible error when the target file is missing.

```markdown
![Board pinout](pinouts/board.pinout.html){ type=iframe }
```

It was written for [PinConnect](../pinconnect/index.md) pinouts, and embeds any HTML page: an interactive widget, a calculator, a diagram. Every live example on this site is embedded with it.

## Install

md-iframe needs Python 3.9 or newer and Python-Markdown 3.3 or newer, which MkDocs and Zensical already bring.

```bash
pip install "git+https://github.com/xbst/md-iframe.git@master"
```

Install it into the same environment that builds your site.

From a clone of the repository, `pip install .` installs it, and `pip install -e .` installs it for development.

## Enable it

Add it to `markdown_extensions` in your `mkdocs.yml`. It relies on the standard `attr_list` extension to read the tag's attributes, so enable both:

```yaml
markdown_extensions:
  - attr_list
  - md_iframe
```

Zensical reads the same `mkdocs.yml` and uses the same Python-Markdown pipeline, so the same two entries work there.

## Use it

- [Embedding pages](embedding.md): the tag, its attributes, where to put the files, styling, and troubleshooting.
- [Auto-height protocol](auto-height.md): the message an embedded page posts so the iframe fits its content.
- [Publish on a docs site](../guides/publishing.md): generate the pages in CI and deploy the site.

md-iframe replaces PinConnect's `pinout-embed`. Existing sites keep working unchanged: `{ type=application/pinout }` is still recognized, and `- pinout_embed` still loads this extension. See [Migrating from the old names](../migration.md).
