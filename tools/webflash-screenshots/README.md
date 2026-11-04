# WebFlash screenshots

Regenerates the 31 WebFlash images in `docs/assets/webflash/`, used across the [WebFlash docs](../../docs/webflash/) and the home page:

- the site (`site-*.webp`, 16): page 1 with Klipper and Katapult picked, a version picker open, a pasted Mainsail version with its "Closest kept" note, the status chip's popover, Configure for an STM32G0B1 pair and an RP2040 pair, the Build step done (and with Memory open), the Flash step for a pair over DFU, a finished flash, the Katapult method, the CAN node list, a failed flash with its fixes, Embed options, the Generate dialog and About;
- the cards (`card-*.webp`, 7): the Firmware step in dark and light, the Setup step, the Build step done, the Flash step, the card at phone width and the static fallback;
- the theme gallery (`theme-<name>-<scheme>.webp`, 8): the `stm32g0b1-usb` card's first step in each bundled theme (`default`, `midnight`, `slate`, `workbench`), dark and light.

The script starts the installed `webflash` site (`python -m webflash --port <free port> --no-browser --assets <assets>`) as a subprocess, renders the cards of the live examples in `docs/firmware/` with the command line into a temporary folder, their `engine_url` pointing at that server's embed runtime, and serves them on another free port. Playwright then drives the real site and the real cards in the system Chrome, headless. The builds really run: Pyodide comes from jsDelivr, the compiler and the source snapshots from the assets. Flashing runs against the site's scripted devices (`?mock=dfu`, `?mock=can`, `?mock=dfu&fail=claim`), so no board is needed. Both servers are stopped at the end.

Run from the repository root after a change to the site's or the card's look or texts (layout, CSS, a step's wording, the flash panel, a bundled theme):

```bash
python tools/webflash-screenshots/generate.py --assets ASSETS
python tools/webflash-screenshots/generate.py --assets ASSETS --only site-build card-*   # some of them
```

`--assets` is required and takes what `webflash --assets` takes: a folder holding `toolchain/` (an unpacked toolchain release under `toolchain/<id>/`, with `current.json`) and `sources/` (the output of `webflash sources build`, with the older commits for the version picker), or a URL serving them, such as `https://webflash.isiks.tech/` once the site is deployed. `--only` takes image names without `.webp`; `*` and `?` match. A full run takes about a minute.

These details keep the images honest and the same from run to run:

- Every scene starts in a fresh browser context, so the download hints ("Next downloads Python, the sources and the compiler…") and the caches read the same each time.
- The site's copies of the example TOMLs leave out `theme` and `theme_dir`: the site does not bundle the docs site's `isikstech` theme, and Generate would list it as not bundled. The originals are not modified.
- The cards keep the `isikstech` theme, whose page is transparent, so they are shot on the docs site's background (`#131313` dark, `#F8F8F8` light). The fallback is rendered with the default `engine_url`, so its link names the hosted site rather than a local port, and shot in a host page with JavaScript off.
- Every page sees 8 cores, 8 GB of memory and a 10 GB storage quota, so About and the compiler pool show no detail of the machine taking the shots; the failed flash pretends to be Windows (`&os=windows`), so its fixes are the same everywhere.
- The open version picker shows Kalico's list, which has every group (Latest, Releases, Branches, Older commits), drawn without its usual height limit so the groups fit in one shot.

The one text that changes from run to run is the build time ("Built in 4.9 s") in `site-build`, `site-build-memory` and `card-build`. Regenerated images are otherwise pixel-identical, though rarely byte-identical: commit only the images whose pixels really changed.

Requires `webflash`, `playwright` and `pillow` (see [the tools README](../README.md)); Playwright drives the system Chrome, no download needed. The pages load Roboto from Google Fonts and Pyodide from a CDN, so this needs network access.
