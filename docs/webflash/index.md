---
description: "WebFlash configures, builds and flashes Klipper, Kalico and Katapult firmware for 3D printer boards in a web browser, and turns a board's settings into a flashing card for its docs."
hide:
  - toc
---
# WebFlash

WebFlash configures, builds and flashes Klipper, Kalico and Katapult firmware for 3D printer boards in a web browser. It shows the project's own `make menuconfig` options, compiles the firmware on your computer with clang running in the browser, and writes it to the board over USB: the STM32 DFU bootloader, RP2040 and RP2350 PICOBOOT and UF2, and Katapult over USB, UART and CAN. There is nothing to install and no printer host involved, and your configuration never leaves the browser.

It also turns one board's firmware settings into a card for that board's documentation. This is one, for the [Birds' Nest](https://docs.isiks.tech/birds-nest/usb/manual/), an STM32G0B1 board on USB:

![Flash Klipper to the Birds' Nest](../firmware/stm32g0b1-usb/stm32g0b1-usb.webflash.html){ type=iframe }

The reader picks Klipper or Kalico, a version and whether to flash Katapult with it, and the card builds the firmware with the settings the board needs and flashes it. Flashing needs Chrome or Edge on a computer; other browsers build the firmware and download it.

There are three ways of using it:

**The site.** Open [webflash.isiks.tech](https://webflash.isiks.tech) and follow its five steps: Firmware, Configure, Build, Flash and Embed. Start with [Getting started](getting-started.md).

**A card in a docs page.** Save a board's settings as a board TOML on the site, then render it into a page with **Generate** or the `webflash` command, and embed it with [md-iframe](../md-iframe/index.md). See [Embedding a card](embedding.md).

**The command line.** `webflash board.toml` renders the same page from a saved board TOML, for regenerating cards in the CI job that publishes a docs site. `webflash` with no file serves the site on your own computer. See [Command line and CI](command-line.md).

## Contents

### Start here

- [Getting started](getting-started.md): build and flash Klipper for a board on the site, from picking a version to the `printer.cfg` line.
- [The site](site/firmware.md), step by step: [Firmware and versions](site/firmware.md), [Configure](site/configure.md), [Build](site/build.md), [Flash](site/flash.md) and [Embed](site/embed.md).
- [Flashing methods](flashing.md): DFU, PICOBOOT, the UF2 drive, Katapult over USB, UART and CAN, the drivers each needs, and how to put a board in its bootloader.
- [Troubleshooting](troubleshooting.md): what each error means and how to fix it.

### Going further

- [Embedding a card](embedding.md): a flashing card for your board in an MkDocs or Zensical site.
- [Command line and CI](command-line.md): install `webflash`, render cards, and run the site locally.
- [Publish on a docs site](../guides/publishing.md): generate the cards in CI and deploy them with GitHub Pages.
- [How it builds](how-it-builds.md): what runs in the browser, why the firmware is larger than a GCC build, and how to reproduce a build on your own machine.

### Reference

- [Board TOML](reference/board-toml.md): every table and key of a board TOML, its rules and its errors.
- [Themes](reference/themes.md): colors, fonts and the card's behavior, and writing your own theme.
- [The generated page](reference/page.md): the card's steps, its fallback, and the messages it exchanges with the page around it.
- [Chips, methods and browsers](reference/support.md): what WebFlash builds and flashes, and in which browsers.
- [Site URLs and storage](reference/site.md): the site's URL parameters and what it keeps in your browser.

### Live examples

One card per way of flashing a board: [a board on USB](examples/usb-board.md), [a CAN toolhead](examples/can-toolhead.md), [RP2040](examples/rp2040.md), [Katapult alone](examples/katapult.md), [LPC1769](examples/lpc1769.md), [a prebuilt file](examples/prebuilt.md), and [light and dark](examples/light-dark.md).

## License

WebFlash is licensed under GPL-3.0. Its source is on GitHub: [xbst/webflash](https://github.com/xbst/webflash). Klipper, Kalico and Katapult are licensed under GPL-3.0 by their own authors; the site lists the version and license of everything it runs under **Versions and licenses**.
