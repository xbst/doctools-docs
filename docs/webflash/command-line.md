---
description: "Install the webflash command, run the WebFlash site locally, render firmware cards from board TOMLs, publish them from CI, and find the maintainer commands."
---
# Command line and CI

The site is the quickest way to make a board TOML and its card, but it needs a person. `webflash` renders the same card from a saved board TOML with no interaction, which is what you want for regenerating cards as a board changes, keeping them in version control, or publishing a documentation site from CI.

The output is identical either way. The site's **Generate** runs this same renderer in the browser, so a board TOML rendered in both places produces the same bytes.

Rendering a card builds no firmware: the card does that, in the reader's browser, when they ask for it. The command line has three jobs:

- `webflash` with no file serves the WebFlash site on your machine.
- `webflash board.toml` renders a board TOML into an embeddable page.
- A few [maintainer commands](#maintainer-commands) run the build engine natively, for people working on WebFlash itself or checking its output.

## Install

`webflash` needs **Python 3.9 or newer** and has no dependencies beyond the standard library on 3.11 and above. Older versions also pull in `tomli`, a TOML parser.

`pip` installs it straight from GitHub:

```bash
pip install "git+https://github.com/xbst/webflash.git@master"
```

A virtual environment is recommended but optional:

**PowerShell**

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install "git+https://github.com/xbst/webflash.git@master"
```

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
pip install "git+https://github.com/xbst/webflash.git@master"
```

Check it worked:

```bash
webflash --help
```

Installing from `master` means each install picks up the newest renderer, so regenerated cards carry the latest fixes. That is what a CI job wants; see [Publish from CI](#publish-from-ci).

### From a clone

```bash
git clone https://github.com/xbst/webflash.git
cd webflash
pip install .
```

### For development

```bash
pip install -e .
```

An editable install also makes `webflash` serve the site files in your checkout, so edits to them take effect on reload. The same goes for the Python code and the themes: the site's Python payload is built from the package, and a running `webflash` rebuilds it when the reloaded site asks for it. Only a change to the server itself (`serve.py`, `payload.py`) needs a restart.

The maintainer commands are meant to run from a clone: the parity matrix (`tools/parity/matrix.toml`) and the Node runner for the WebAssembly toolchain live in the repository, not in the package.

## Run the site locally

Installing the tool also installs the site. Run `webflash` with no file to open it:

```bash
webflash
```

That builds the Python payload the site needs, starts a local server on a free port, opens a browser, and prints where everything is:

```
Site:      /path/to/webflash/site
Payload:   /path/to/webflash.zip  (118 KB)
Assets:    https://webflash.isiks.tech/
Serving:   http://127.0.0.1:50213
Press Ctrl+C to stop.
```

An installed package keeps its payload in your user cache rather than beside the installed site, and says so on a second line under `Payload:`.

| Option | Meaning |
|---|---|
| `--port N` | Serve on this port. Without it, a free port is chosen; a port in use is reported and another one chosen. |
| `--no-browser` | Do not open a browser window. |
| `--assets URL` | Fetch the compiler and the firmware sources from this site. The default is `https://webflash.isiks.tech/`, so a local site still downloads them from the hosted one. |
| `--assets DIR` | Serve the compiler and the sources from a folder on your machine instead: its `toolchain/` and `sources/` folders, at `/toolchain/` and `/sources/`. |

The local server listens on `127.0.0.1` only, and serves:

- the site at `/`, with a `<meta name="webflash-assets">` tag in `index.html` naming where the compiler and the sources come from (see [Where the downloads come from](reference/site.md#where-the-downloads-come-from));
- the Python payload, `webflash.zip`, rebuilt first whenever the package has changed;
- the card's runtime at `/engine/v1/`, laid out as the hosted site serves it, so a board TOML with `engine_url = "http://127.0.0.1:<port>/engine/v1/"` renders a card that runs against your server;
- with `--assets DIR`, the folder's `toolchain/` and `sources/`, and nothing else of it.

Every response carries `Access-Control-Allow-Origin: *`, as GitHub Pages sends it, so a card served from another local server can load the runtime, and nothing is cached, so an edited file is what the next reload gets.

A local site still loads its Python runtime, Pyodide, from a CDN on first use, and its fonts from Google Fonts. A machine with no network at all cannot run the site; it can still render cards with the command below.

### An assets folder

An `--assets` folder holds the same two folders the hosted site has:

```
local-assets/
├── toolchain/
│   ├── current.json          {"id": "<release id>"}
│   └── <release id>/         an unpacked webflash-toolchain release (manifest.json, llvm.js, llvm.wasm.gz, ...)
└── sources/                  what webflash sources build writes (index.json, blobs/, history/, ...)
```

`sources/` comes from [`webflash sources build`](how-it-builds.md#webflash-sources-build-index-and-check). This is how WebFlash itself is tested before a deploy.

### Serving the site by hand

`webflash` is the easy way. The site must be served over HTTP: opening `index.html` from disk cannot fetch the payload. To serve the site folder with another web server, build the payload into it first. In a clone, this writes it beside the site in `src/webflash/site/`:

```bash
python -m webflash.payload
```

An installed copy keeps its payload in your user cache instead, so name the site folder, or a copy of it, explicitly:

```bash
python -c "from webflash.payload import site_root; print(site_root())"
python -m webflash.payload <site folder>/webflash.zip
```

Rebuild the payload after upgrading `webflash`, or add `--force` to rebuild it regardless. A site served this way has no `webflash-assets` tag, so it fetches `toolchain/` and `sources/` from its own origin, and its Generate preview expects the runtime at `/engine/v1/`: lay the folder out as the repository's Pages workflow (`.github/workflows/pages.yml`) stages it.

## Render a board TOML

```bash
webflash board.toml
```

This writes `board.webflash.html` beside the board TOML, and prints what it did:

```
Generated: /path/to/board.webflash.html  (13 KB)
```

The board TOML is the file the site's **Save TOML** writes, or one you write by hand; see the [board TOML reference](reference/board-toml.md). The page is the card the [generated page reference](reference/page.md) describes.

| Option | Meaning |
|---|---|
| `-o OUT`, `--output OUT` | The file to write. The default is `<stem>.webflash.html` beside the board TOML. The folder must already exist. |
| `-t NAME`, `--theme NAME` | The theme to apply, overriding `[board] theme` for this run. Resolved from the board's `theme_dir` (default `./themes`, beside the TOML) first, then the bundled themes: `default`, `midnight`, `slate` and `workbench`. See [Themes](reference/themes.md). |
| `-i`, `--inline` | Embed the board image and the `[prebuilt]` firmware file in the page as data URLs, so it needs nothing beside it. |

```bash
webflash examples/can-toolhead/can-toolhead.toml -t slate -i -o can.html
```

`webflash` refuses an output path that names a folder, the board TOML itself, its image, its firmware file or its theme file.

### What it needs alongside the board TOML

Three things are resolved relative to the board TOML:

- **The board image**, from `[board] image`: a URL, or a path relative to the TOML. The page references it by the same path, unless you pass `-i`. An image given as a URL stays a URL with `-i`, with a warning.
- **The prebuilt firmware**, from `[prebuilt] file`, for a board that offers a ready-made file rather than a build. The page links it beside itself, unless you pass `-i`.
- **The theme**, from `theme_dir` first, then the bundled themes.

`-i` reads only files below the board TOML's folder: a path with `..`, a drive or a leading `/` is an error. Without `-i`, keep the image and the firmware file next to the page: move one, move the others.

### What the page loads

The page holds the board's configuration, its theme and a static fallback card, and loads the card's code, the runtime, from `[board] engine_url` (`https://webflash.isiks.tech/engine/v1/` by default). The runtime then downloads Python, the firmware sources and the compiler in the reader's browser when they ask for a build (a `[prebuilt]` card needs none of them). So a page rendered once keeps getting the runtime's fixes without being rendered again, and a page opened without network, or without JavaScript, shows the fallback card. The [generated page reference](reference/page.md) has the details.

### Warnings and errors

Problems the page renders with anyway print as `Warning:` lines on stderr, and the page is still written: a label for a value an option does not offer, instructions for a flashing method the board does not offer, a theme's unknown key or malformed color, an image URL that `-i` leaves as it is.

Everything else prints `Error:` on stderr and exits with status 1, without writing anything:

- **`Error: board TOML not found: <path>`**: check the path and your working directory.
- **`Error: <file>: <table>: <message>`**: a problem in the board TOML, such as a TOML syntax error, an unknown key (`bad.toml: [board]: unknown key(s): colour (valid: title, description, image, theme, theme_dir, engine_url)`), a missing required key, a value of the wrong type, or a defconfig line that is not `.config` syntax. See the [board TOML reference](reference/board-toml.md).
- **`Error: Theme '<name>' not found in <folder> or <folder>`**: no `<name>.toml` in either `theme_dir` or the bundled themes, for `-t` or `[board] theme`.
- **`Error: <file>: [board]: image file not found: <path>`** and **`Error: <file>: [prebuilt]: firmware file not found: <path>`**: `-i` could not read a file the TOML names.
- **`Error: <file>: [prebuilt]: file must be a path relative to this TOML, not a URL`**: `-i` cannot embed a firmware file given as a URL.
- **`Error: the output is a folder, not a file`** and **`Error: the output would overwrite <what>: <path>`**: `-o` names a folder or one of the inputs.
- **`Error: cannot write output file: <path>`**: the `-o` folder does not exist, or the file cannot be written there.
- **`Error: port must be between 0 and 65535`**: an out-of-range `--port`.

Mixing the modes is a usage error with status 2: `--port`, `--no-browser` and `--assets` apply only to the site, so they cannot be combined with a board TOML, and `-o`, `-t` and `-i` need a board TOML to render. A file that does not end in `.toml` is a usage error too, and so is an `--assets` value that is neither an `http(s)` URL nor a folder that exists.

## Regenerating as a board changes

The board TOML is the thing worth keeping in version control. A card is derived from it, so a board revision, a new default version or another setup means editing the TOML, in the site or by hand, and running the command again:

```bash
webflash docs/firmware/my-board/my-board.toml -i
```

Because the site and the command produce the same bytes, you can move between them freely: configure a board in the site, save the TOML, and regenerate it from a script afterwards. **Open TOML** in the site takes it back for the next change.

## Publish from CI

A documentation site usually renders its cards on every deploy, from the TOMLs alone. Keep one folder per board, holding its TOML and its photo:

```
docs/
├── my-board.md
└── firmware/
    └── my-board/
        ├── my-board.toml            ← committed
        ├── my-board.webp            ← committed
        └── my-board.webflash.html   ← generated by CI, not committed
```

Embed the generated file with [md-iframe](../md-iframe/embedding.md):

```markdown
![Flash the firmware](firmware/my-board/my-board.webflash.html){ type=iframe }
```

Then add these steps to the workflow, before `zensical build` or `mkdocs build`:

```yaml
      - run: pip install "git+https://github.com/xbst/webflash.git@master"
      - run: pip install "git+https://github.com/xbst/md-iframe.git@master"
      - name: Generate the firmware cards
        run: |
          shopt -s nullglob
          for toml in docs/firmware/*/*.toml; do
            echo "webflash $toml"
            webflash "$toml" -i
          done
```

`-i` embeds the photo and any prebuilt file, so the built site does not depend on their paths resolving. A site-wide theme can live once in `docs/firmware/`, beside the board folders, with each board pointing at it with `theme_dir = ".."`; the loop only renders `docs/firmware/*/*.toml`, so the theme is never rendered as a board. Ignore the generated files:

```gitignore
docs/firmware/**/*.webflash.html
```

[Publish on a docs site](../guides/publishing.md) has the whole workflow, with PinConnect and 3DStep beside it, and [Embedding a card](embedding.md) covers the frame itself, including `allow="usb; serial"` for a card served from another origin.

## Maintainer commands

These run WebFlash's build engine natively, on a Klipper, Kalico or Katapult source tree, with GNU make and a real toolchain. They are for working on WebFlash, checking its output against a GCC build, reproducing a firmware the browser built, and building the source snapshots the site serves. [How it builds](how-it-builds.md) explains each one and what it checks.

| Command | What it does |
|---|---|
| [`webflash build`](how-it-builds.md#webflash-build) | Build one configuration with the engine and GCC, Arm Toolchain for Embedded's clang, or the browser's WebAssembly toolchain under Node. |
| [`webflash make-check`](how-it-builds.md#webflash-make-check) | Compare the engine's make interpreter with GNU make's `make -n V=1`, row by row of the parity matrix. |
| [`webflash parity`](how-it-builds.md#webflash-parity) | Build every row of the parity matrix with several toolchains and compare the results. |
| [`webflash inspect`](how-it-builds.md#webflash-inspect) | Show a firmware file's sections, sizes, segments and vector table. |
| [`webflash sources`](how-it-builds.md#webflash-sources-build-index-and-check) | Build the source snapshots and their index for the site (`build`, `index`, `check`). |

Each prints its options with `--help`:

```
usage: webflash build [-h] --config CONFIG
                      --toolchain {gcc,clang-native,wasm-node}
                      [--toolchain-dir TOOLCHAIN_DIR] [--wasm-mount PATH]
                      [--version VERSION] [-j JOBS] [--out OUT]
                      [--lto {on,off}] [-v]
                      tree
```

```
usage: webflash make-check [-h] [--config CONFIG] [--matrix MATRIX]
                           [--row ROW] [--project {klipper,kalico,katapult}]
                           [--make MAKE] [--gcc-dir GCC_DIR] [--goal GOAL]
                           tree
```

```
usage: webflash parity [-h] [--matrix MATRIX] [--row ROW]
                       [--project {klipper,kalico,katapult}]
                       [--toolchains TOOLCHAINS] [--gcc-dir GCC_DIR]
                       [--clang-dir CLANG_DIR] [--wasm-dir WASM_DIR]
                       [--wasm-mount PATH] [--version VERSION] [-j JOBS]
                       [--out OUT] [--table TABLE] [--append] [--json JSON]
                       tree
```

```
usage: webflash inspect [-h] [--ld LD] [--json] file
```

```
usage: webflash sources build [-h] [--policy FILE] --out DIR --cache DIR
                              [--project P] [--ref R] [--clones DIR]
                              [--no-gate] [--matrix FILE] [--run ID]
                              [--no-history] [--gate-minutes M]
usage: webflash sources index [-h] [--policy FILE] --out DIR --cache DIR
usage: webflash sources check [-h] --out DIR
```

They print `Error:` lines and exit with status 1 on a problem, and `make-check` and `parity` also exit 1 when a comparison fails. `webflash sources build` exits 2 when it wrote everything but a snapshot failed its gate. An installation without the engine says so: `Error: this installation of webflash has no webflash.engine.cli, which runs this command`.
