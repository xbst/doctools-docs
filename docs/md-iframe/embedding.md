---
description: "Embed an HTML page, such as a PinConnect pinout, in an MkDocs or Zensical page with an image-style md-iframe tag."
---
# Embedding pages

md-iframe lets you drop an HTML page into a Markdown page with an image-style tag, which it replaces at build time with an `<iframe>`. It only handles embedding: produce the page first, for example a pinout with [PinConnect](../pinconnect/getting-started.md).

[Install and enable it](index.md#install) first.

## The tag

Use image syntax pointing at the HTML file, with `type=iframe`:

```markdown
![Board pinout](../path/to/board.pinout.html){ type=iframe style="min-height:60vh;width:100%" }
```

At build time the extension turns that into an `<iframe>` that loads the page. Details:

- The **path** is resolved like any other asset in your docs, relative to the page.
- The **alt text** (`Board pinout` above) becomes the iframe's `title` for tooltips and screen readers. An explicit Markdown title wins if you give one: `![alt](board.pinout.html "Board pinout")` uses `Board pinout`, and the alt text is only the fallback.
- The **`style`** attribute is passed straight through. If you omit it, the default is `min-height:60vh;width:100%`.
- A **`class`** you add is kept, beside md-iframe's own.
- The iframe is set to `loading="lazy"` and `allowfullscreen`.

Only images tagged `type=iframe` are affected; ordinary images pass through untouched.

!!! note "`type=application/pinout` still works"
    Pages written for md-iframe's predecessor, pinout-embed, use `{ type=application/pinout }`. md-iframe treats it exactly like `type=iframe`, and always will, so there is no need to change existing pages. See [Migrating from the old names](../migration.md).

## Place the files so the site serves them

MkDocs and Zensical copy non-Markdown files under `docs/` into the built site. Put the HTML, **and anything it loads by relative path**, inside your docs tree and reference the HTML by a path relative to the page.

A PinConnect pinout links its board image by relative path unless it was generated with `pinconnect -i`, so keep the two together. For example:

```
docs/
├── boards.md
└── pinouts/
    ├── board.pinout.html
    └── board.png
```

Referenced from `docs/boards.md`:

```markdown
![Board pinout](pinouts/board.pinout.html){ type=iframe }
```

You can also set the size of the iframe. md-iframe overrides it while the page inside [reports its own height](auto-height.md):

```markdown
![Board pinout](pinouts/board.pinout.html){ type=iframe style="height:60vh;min-height:500px;width:100%" }
```

A convenient way to keep a pinout in step is to point `pinconnect -o` straight at your docs tree:

```bash
pinconnect board.toml -o docs/pinouts/board.pinout.html
```

Remember to copy the board image next to it, or use `-i` to embed the image into the HTML. To generate every page on each deploy instead of committing them, see [Publish on a docs site](../guides/publishing.md).

## Height

Most embedded pages render at a fixed height (your `style`, or the `min-height:60vh` default), which is what you want for a diagram that fills its frame.

A page can also report its content height, and md-iframe then grows or shrinks the iframe to fit, with no scrollbar inside it. PinConnect pinouts do this when their theme stacks the connector list below the board on narrow screens. md-iframe adds one small listener per page that has an embed; there is nothing to configure. A page that never reports a height keeps the authored `(min-)height`.

[Auto-height protocol](auto-height.md) describes the message, so other tools and hand-written pages can use it too.

## Light and dark mode

md-iframe does not change the embedded page's colors. A page that supports both schemes, like a PinConnect pinout, follows your site's toggle on its own when it is served from the same origin. [Light and dark mode](../guides/light-dark.md) explains how, and what to do across origins.

## Styling

Every embedded iframe has the class `md-iframe`, and also `pinconnect-embed`, so CSS written for pinout-embed keeps applying:

```css
iframe.md-iframe {
  border-radius: 8px;
}
```

A missing page is replaced by a box with the classes `md-iframe-error` and `pinconnect-embed-error`.

## When the file is missing

md-iframe checks each embed when the page loads. If the file returns 404, a typo or a page that was never generated, the iframe is replaced with a red box reading "Embed failed to load — file not found:" and the path, rather than a blank frame. A `type=application/pinout` embed says "Pinout failed to load" instead.

MkDocs also reports the missing file at build time; Zensical currently doesn't, which is why the check runs in the browser. Cross-origin embeds cannot be checked, so they are left alone. The check runs again after Material's and Zensical's instant navigation, so pages reached without a reload are checked too.

## Troubleshooting

- **The tag renders as a plain image or a broken image.** The extension is not active. Confirm both `attr_list` and `md_iframe` are in `markdown_extensions`, and that `md-iframe` is installed in the environment running MkDocs or Zensical.
- **A red box says the embed failed to load.** The HTML is not at that path in the built site. Check the path relative to the page, and that the file was generated before the build.
- **A pinout loads but shows a broken image inside.** The board image is not next to the HTML in the built site. Copy it along with the HTML, or regenerate with `pinconnect -i` to embed the image.
- **The iframe has a scrollbar inside it.** The page inside does not report its height. Give the tag a taller `style`, or have the page post its height as the [auto-height protocol](auto-height.md) describes.
