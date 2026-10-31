---
description: "Open-source documentation tools from Isik's Tech: PinConnect turns a board photo into an interactive pinout, and md-iframe embeds pages like it in MkDocs and Zensical sites."
hide:
  - footer
---
# Isik's Tech Doc Tools

Open-source tools for writing better hardware documentation. We built them for the [Isik's Tech docs](https://docs.isiks.tech) and use them there every day.

<div class="grid cards" markdown>

-   **[PinConnect](pinconnect/index.md)**

    ---

    Turns a photo of a circuit board into an interactive pinout: hover or tap a connector and its pin names, colors and description appear. Make one in the browser at [pinconnect.isiks.tech](https://pinconnect.isiks.tech), or render it from a config on the command line.

    [Get started](pinconnect/getting-started.md) · [Live examples](pinconnect/examples/index.md)

-   **[md-iframe](md-iframe/index.md)**

    ---

    A Python-Markdown extension for MkDocs and Zensical sites. It turns an image-style tag into an `<iframe>` that sizes itself to the page inside it and shows a visible error when the file is missing.

    [Embed a page](md-iframe/embedding.md) · [Auto-height protocol](md-iframe/auto-height.md)

</div>

Here is a PinConnect pinout embedded with md-iframe. Hover a connector, or open the connector list:

![OwlFC-Mini interactive pinout](pinouts/owlfc-mini/owlfc-mini.pinout.html){ type=iframe }

## Guides

These topics apply to every tool on this site:

- [Publish on a docs site](guides/publishing.md): generate pages in CI and deploy them with GitHub Pages.
- [Light and dark mode](guides/light-dark.md): how an embedded page follows your site's color scheme.
- [Theming concepts](guides/theming.md): what a theme controls, and where it comes from.

Coming from `pinout-gen` or `pinout-embed`? Nothing breaks; see [Migrating from the old names](migration.md).

## License

PinConnect and md-iframe are licensed under GPL-3.0. Their source is on GitHub: [xbst/PinConnect](https://github.com/xbst/PinConnect) and [xbst/md-iframe](https://github.com/xbst/md-iframe).
