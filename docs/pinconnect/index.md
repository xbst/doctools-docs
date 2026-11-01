---
description: "PinConnect turns a photo of a circuit board into an interactive pinout diagram, made in the browser or rendered from a config on the command line."
hide:
  - toc
---
# PinConnect

PinConnect turns a photo of a circuit board into an interactive pinout diagram: hover or tap a connector and its pin names, colors, and description appear. The result is a single HTML file you can open in a browser, share, or embed in a documentation site.

![OwlFC-Mini interactive pinout](../pinouts/owlfc-mini/owlfc-mini.pinout.html){ type=iframe style="height:80vh;min-height:500px;width:100%" }

There are two ways of generating pinouts with it:

**In the browser.** Open the designer at [pinconnect.isiks.tech](https://pinconnect.isiks.tech), load a board image, draw a box over each connector, label the pins, and press **Generate**. Nothing to install. Start with [Getting started](getting-started.md).

**From the command line.** `pinconnect board.toml` renders the same file from a saved config, which is what you want for regenerating pinouts as a board changes, or in a CI job that publishes a docs site. See [Command line and CI](command-line.md).

## Contents

### Start here

- [Getting started](getting-started.md): from a board image to a finished pinout, in the browser.
- [The designer](designer.md): a full tour, keyboard shortcuts, and what to do when something goes wrong.
- [Concepts](concepts.md): how the pieces fit together, and the three kinds of TOML file.

### Going further

- [Command line and CI](command-line.md): install `pinconnect`, regenerate pinouts, and run the designer locally.
- [Embedding with md-iframe](../md-iframe/embedding.md): put a pinout into an MkDocs or Zensical page.
- [Publish on a docs site](../guides/publishing.md): generate pinouts in CI and deploy them with GitHub Pages.

### Reference

- [Board TOML](reference/board-toml.md): every field in a board config, including jumper settings for pin headers.
- [Connector types](reference/connector-types.md): the built-in library, and adding your own.
- [Themes](reference/themes.md): colors, fonts, and layout behavior, and writing your own theme.

### Live examples

- [Live examples](examples/index.md): a real board, every connector type, jumper settings, and light and dark mode, all generated from TOMLs on every deploy of this site.
