---
description: "Put a WebFlash card on a docs page: make the board TOML, render it with webflash, embed it with md-iframe, allow USB and serial from another origin, and publish from CI."
---
# Embedding a card

A card puts one board's firmware on a documentation page: the reader picks the firmware, the version and how the board is connected, builds it in the browser and flashes it, without leaving the page. This page takes you from a board to a card on an MkDocs or Zensical site.

![Flash Klipper to a CAN toolhead](../firmware/can-toolhead/can-toolhead.webflash.html){ type=iframe }

The card above is rendered from [`can-toolhead.toml`](examples/can-toolhead.md) on every deploy of this site. It has two setups, so it asks how the board is connected before it builds.

The path has four steps:

1. Make the board's [board TOML](reference/board-toml.md), on the site or by hand.
2. Put the photo, and a prebuilt firmware file if there is one, beside it.
3. Render it with `webflash board.toml`, which writes `board.webflash.html`.
4. Embed the HTML in a page with [md-iframe](../md-iframe/embedding.md).

## Make the board TOML

### On the site

The site writes the TOML as you work:

1. Configure the board as a reader would get it: open <https://webflash.isiks.tech>, pick the firmware and the versions on page 1, and set the configuration on Configure. [Getting started](getting-started.md) walks through it. You need not build or flash it, though doing so once is the best check that the configuration works.
2. Go to the **Embed** step: the step bar links to it from every step. In **Embed options**, give the card its title, description and photo, add a setup for each way the board is connected, and choose what the reader may change. [Embed](site/embed.md) describes every field.
3. Click **Save TOML**.

**Generate** in the same footer shows the card as it will look and runs it, and its **Download HTML** gives the same file as step 3 below. For a docs site that renders its pages in CI, the TOML is all you keep.

To change a TOML later, open it with **Open TOML** in the site's top bar, with its photo (the file picker takes both), change it, and save it again. The site keeps every value but writes the text fresh, so comments in the file are lost.

### By hand

A board TOML is a short text file, and starting from one of the [examples](https://github.com/xbst/webflash/tree/master/examples) is the quickest way. The smallest one names the board, the firmware and its configuration:

```toml
[board]
title = "My Board"
image = "my-board.webp"

[firmware]
project = "klipper"

[config]
defconfig = """
CONFIG_MACH_STM32=y
CONFIG_MACH_STM32G0B1=y
"""
```

`defconfig` is what `make savedefconfig` writes in a Klipper checkout, or what the site's **.config** tab shows with **Minimal (defconfig)** ticked: only the lines that differ from the defaults. The [board TOML reference](reference/board-toml.md) has every key, and `webflash board.toml` reports a mistake with the file and the table it is in.

## What goes beside it

Keep one folder per board, with the TOML and the files it names:

```
docs/
├── my-board.md
└── firmware/
    └── my-board/
        ├── my-board.toml            ← committed
        ├── my-board.webp            ← committed
        └── my-board.webflash.html   ← generated, not committed
```

- **The photo**, `[board] image`: a path relative to the TOML, inside its folder (no `..`, no drive, no leading `/`), or a URL.
- **A prebuilt firmware file**, `[prebuilt] file`, for a [prebuilt board](#a-prebuilt-board): a path relative to the TOML, never a URL.

## Render it

```bash
pip install "git+https://github.com/xbst/webflash.git@master"
webflash docs/firmware/my-board/my-board.toml
```

That writes `my-board.webflash.html` beside the TOML and prints its size. Warnings, such as instructions for a method the TOML does not offer, go to the terminal and do not stop it; an error names the file, the table and the problem.

| Option | Effect |
|---|---|
| `-i`, `--inline` | Put the photo and the prebuilt file inside the page as data URLs, so it is one self-contained file. A photo given as a URL stays a URL, with a warning; a file that is missing is an error. |
| `-t NAME`, `--theme NAME` | Use another theme than `[board] theme`: one in the board's `theme_dir`, or a bundled one. |
| `-o OUT`, `--output OUT` | Write the page somewhere else. Without `-i`, copy the photo and the prebuilt file beside it too. |

Without `-i`, the page loads the photo and the prebuilt file from beside it, by the paths the TOML gives. [Command line and CI](command-line.md) has the rest of the command.

The same TOML and files give the same bytes on every machine, and the same as the site's Generate, so a page only changes when its inputs or the WebFlash version do.

## Embed it with md-iframe

[Install and enable md-iframe](../md-iframe/index.md#install), then point an image-style tag at the page:

```markdown
![Flash Klipper to My Board](firmware/my-board/my-board.webflash.html){ type=iframe }
```

The alt text becomes the frame's title, for screen readers and tooltips. The card sizes its frame itself: it reports its height whenever it changes, as the reader moves between steps and opens the log, and md-iframe follows it, so the frame never has a scrollbar. See [Height](../md-iframe/embedding.md#height).

A page beside the Markdown, on the docs site's own origin, follows the site's light and dark toggle live, with nothing to configure, and needs nothing more to flash: WebUSB and Web Serial are allowed in a frame from the page's own origin. [Light and dark mode](../guides/light-dark.md) explains how the scheme is picked; `?theme=dark` or `?theme=light` on the path pins one.

## From another origin

A frame from another origin needs `allow="usb; serial"`, which md-iframe keeps on the iframe:

```markdown
![Flash](https://example.org/board.webflash.html){ type=iframe allow="usb; serial" }
```

Without it, the browser refuses both device pickers ("disallowed by permissions policy"). The card says so, still builds and offers the files for download, and links to the card in a tab of its own, where it can flash. A frame that allows only one of the two APIs keeps the methods on that one: `allow="usb"` keeps DFU, PICOBOOT and Katapult over CAN, `allow="serial"` keeps Katapult over a USB or UART serial port, and the card names what it cannot offer.

Even with `allow="usb; serial"`, a browser opens no folder picker in a frame from another origin, so the RP2040 and RP2350 UF2 drive method becomes a `.uf2` download there, to copy onto the drive by hand.

A page from another origin cannot read the docs site's toggle either: the host has to send it the scheme, as [Light and dark mode](../guides/light-dark.md#across-origins) shows.

## Publish from CI

Rather than committing generated pages, render them on every deploy: keep the TOMLs and their files in the repository, and let the workflow write the HTML. Add these steps before `zensical build` or `mkdocs build`:

```yaml
      - run: pip install "git+https://github.com/xbst/webflash.git@master"
      - name: Generate the firmware cards
        run: |
          shopt -s nullglob
          for toml in docs/firmware/*/*.toml; do
            echo "webflash $toml"
            webflash "$toml" -i
          done
```

and ignore the output:

```gitignore
docs/firmware/**/*.webflash.html
```

A theme of your own can sit beside the board folders, in `docs/firmware/mysite.toml`, with `theme = "mysite"` and `theme_dir = ".."` in each board's `[board]` table; the loop renders only `docs/firmware/*/*.toml`, so it never renders the theme as a board. This site's cards use one, `isikstech.toml`. [Publish on a docs site](../guides/publishing.md) has a complete workflow, and the themes reference [a theme for a docs site](reference/themes.md#a-theme-for-a-docs-site).

## A board that runs two ways

A board that is used in more than one way, on a CAN bus with Katapult or on USB without a bootloader, say, gets one setup per way: repeated `[[setup]]` tables, each with a title, a description, its configuration, optionally Katapult's beside it, and its own flashing methods. The card then has a Setup step, where the reader picks one, and each `[[option]]` can apply to some setups only. With `[katapult]`, the card offers Katapult beside the firmware with a checkbox, ticked at the start or not (`[katapult] default`), and a setup without Katapult is disabled while it is ticked.

On the site, **+ Add the current configuration** in Embed options makes a setup from what Configure holds; see [Setups the reader picks from](site/embed.md#setups-the-reader-picks-from). The board TOML reference has the keys: [`[[setup]]`](reference/board-toml.md#setup), [`[katapult]`](reference/board-toml.md#katapult) and [`[[option]]`](reference/board-toml.md#option). The [CAN toolhead example](examples/can-toolhead.md) is the card at the top of this page.

## A prebuilt board

A board that needs one known firmware file, such as a Katapult build to install once, can skip the build: a `[prebuilt]` table names the file, its address for a `.bin`, and the chip it is for. The card then has two steps, the board and its file, then Flash, and loads no Python, no sources and no compiler. With `-i` the file is inside the page; without it, it sits beside the page. The fallback without JavaScript offers it as a download. See [`[prebuilt]`](reference/board-toml.md#prebuilt) and the [prebuilt example](examples/prebuilt.md).

## Open in WebFlash

Every card built from source links to the WebFlash site: the fallback's sentence, and **Open in WebFlash** in the card's Flash step. The link is the site with `#toml=` and the board TOML after it, base64url-encoded, so the site opens the board with every option of `make menuconfig` for a reader who needs more than the card offers. Until the reader changes something, it carries the page's own TOML; once they have, it carries a TOML with their picks: their setup first, their option choices in its configuration, their firmware and versions, and Katapult as they left it. [The generated page](reference/page.md#open-in-webflash) has the details.

The site's **Copy link**, on the TOML tab and in Generate, gives the same link for the TOML you are editing.

## The runtime and `engine_url`

A generated page holds the card's configuration and a static fallback, not the card's code: it loads the WebFlash runtime from `[board] engine_url`, by default `https://webflash.isiks.tech/engine/v1/`. The runtime then downloads the Python payload, the sources and the compiler from the same site, and Python itself from jsDelivr, once the reader clicks Next. The `v1` is the version of the runtime the page is rendered against, so you leave `engine_url` alone unless you host a WebFlash site of your own; the site's Embed options have no field for it, so set it in the TOML by hand.

The "Open in WebFlash" link goes to the site that `engine_url` belongs to: `engine_url` without its `engine/v1/` folder.

## Test a card locally

To try a card against a local copy of WebFlash before you publish it, run the site on a fixed port and point the TOML at it:

```bash
webflash --port 8000 --no-browser
```

```toml
[board]
title = "My Board"
engine_url = "http://127.0.0.1:8000/engine/v1/"
```

Render the TOML, then open the page over HTTP, from a folder that holds it and its photo:

```bash
webflash my-board.toml
python -m http.server 8001
```

and browse to `http://127.0.0.1:8001/my-board.webflash.html`. The local server allows every origin, as the hosted site does, so the page on another port can load the runtime; by default it still takes the compiler and the sources from <https://webflash.isiks.tech> (`--assets` names another URL, or a folder holding `toolchain/` and `sources/`). Add `?mock=dfu` (or `katapult`, `uart`, `can`, `picoboot`, `uf2`) to the page's address to run the Flash step against scripted devices instead of a board. Put `engine_url` back, or remove it, before you publish.
