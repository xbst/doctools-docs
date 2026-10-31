---
description: "Install the pinconnect command, render pinouts from a board config, run the designer locally, and serve it by hand."
---
# Command line and CI

The designer is the quickest way to make a pinout, but it needs a person. `pinconnect` renders the same file from a saved config with no interaction, which is what you want for regenerating pinouts as a board changes, keeping them in version control, or publishing a documentation site from CI.

The output is identical either way. The designer runs this same generator in the browser, so a config rendered in both places produces the same bytes.

## Install

`pinconnect` needs **Python 3.9 or newer** and has no dependencies beyond the standard library on 3.11 and above. Older versions also pull in `tomli`, a TOML parser.

`pip` installs it straight from GitHub:

```bash
pip install "git+https://github.com/xbst/PinConnect.git@master"
```

A virtual environment is recommended but optional:

**PowerShell**

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install "git+https://github.com/xbst/PinConnect.git@master"
```

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
pip install "git+https://github.com/xbst/PinConnect.git@master"
```

Check it worked:

```bash
pinconnect --help
```

Installing from `master` means each install picks up the newest generator, so regenerated pinouts carry the latest fixes. That is what a CI job wants; see [Publish on a docs site](../guides/publishing.md).

### From a clone

```bash
git clone https://github.com/xbst/PinConnect.git
cd PinConnect
pip install .
```

### For development

```bash
pip install -e .
```

An editable install also makes `pinconnect` serve the designer files in your checkout, so edits to them take effect on reload.

## Run the designer locally

Installing the tool also installs the designer. Run `pinconnect` with no config to open it:

```bash
pinconnect
```

That builds what the designer needs, starts a local server on a free port, and opens a browser. `--port 8000` picks the port; `--no-browser` skips opening one.

Use this when you want the designer offline from the hosted site, or when you are working on the designer itself. It still downloads its Python runtime from a CDN on first load, so a fully offline machine should use the command line instead.

### Serving the designer by hand

`pinconnect` is the easy way. To serve the designer folder with another web server instead, it needs the payload it fetches at startup, `pinconnect.zip`, beside its `index.html`. Without it, the designer boots into "Renderer unavailable".

In a clone of the repository, the designer is `src/pinconnect/designer/`, and this builds the payload there:

```bash
python -m pinconnect.payload
```

An installed copy keeps its payload in your user cache instead, so name the designer folder explicitly. This prints where the installed designer is:

```bash
python -c "from pinconnect.payload import designer_root; print(designer_root())"
```

Then build the payload into it, or into a copy of that folder, which keeps your site-packages clean:

```bash
python -m pinconnect.payload <designer folder>/pinconnect.zip
```

The designer must be served over HTTP: opening `index.html` from disk cannot fetch the payload. Rebuild the payload after upgrading `pinconnect`, or add `--force` to rebuild it regardless.

## Render a config

```bash
pinconnect board.toml
```

This writes `board.pinout.html` beside the config, and prints what it did:

```
Generated: /path/to/board.pinout.html  (14 connectors)
```

Write somewhere else with `-o` / `--output`. The directory must already exist.

```bash
pinconnect board.toml -o docs/my-board.html
```

## What it needs alongside the config

Three things are resolved relative to the board config:

- **The board image**, from `image` in `[board]`. Referenced by the output rather than embedded, unless you pass `-i`.
- **The connector types**, from `connector_dir` (default `./connectors`, beside the config) first, then the types bundled with the package. Putting a `<type>.toml` in your `connector_dir` overrides a bundled type of the same name. See [connector types](reference/connector-types.md).
- **The theme**, from `theme_dir` (default `./themes`) first, then the bundled themes. See [Themes](reference/themes.md).

A board using its own `connector_dir` or `theme_dir` is one the designer cannot render faithfully, since those files are on your disk. Render those with this command.

## Keep the image beside the output

By default the generated HTML links the board image by the same relative path the config uses. If `board.toml` says `image = "board.png"`, then `board.png` must sit next to `board.pinout.html`. Move one, move the other.

To avoid that, embed the image instead.

## Embed the board image

`-i` / `--image-embed` base64-encodes the image into the HTML, giving one file that carries everything:

```bash
pinconnect board.toml -i
```

That reads `image` from the config. To embed a different file:

```bash
pinconnect board.toml -i other.png
```

`-i` covers the image only. A theme whose font comes from Google Fonts, including the default, still loads it from the web, so an offline page falls back to a system font. For output with no external references at all, pair `-i` with a theme using a `bundled` or `system` font. See [Themes](reference/themes.md).

## Choose a theme

`-t` / `--theme` overrides the board's `[board] theme` for one run:

```bash
pinconnect board.toml --theme midnight
```

The bundled themes are `default`, `midnight`, `ocean`, `slate`, `terminal` and `workbench`.

## Regenerating as a board changes

The config is the thing worth keeping in version control. A pinout is derived from it, so a board revision means editing the config and running the command again rather than starting over:

```bash
pinconnect boards/rev-c.toml -o site/rev-c.pinout.html -i
```

Because the designer and the command produce the same bytes, you can move between them freely: design a board visually, save the config, and regenerate it from a script afterwards.

To regenerate every pinout of a docs site on each deploy, see [Publish on a docs site](../guides/publishing.md).

## Common errors

All of these print to stderr and exit with status 1.

- **`Error: config file not found`**: check the path and your working directory.
- **`Error: Connector type '<name>' not found`**: no `<name>.toml` in either `connector_dir` or the bundled types. The message names both folders. Fix the `type` value or add the type; see [connector types](reference/connector-types.md).
- **`Error: Theme '<name>' not found`**: same lookup, for `-t` or `[board] theme`. See [Themes](reference/themes.md).
- **`Error: image file not found`**: `-i` could not read the board image.
- **`Error: cannot write output file`**: the `-o` folder does not exist, or the file cannot be written there.
- **`Error: port must be between 0 and 65535`**: an out-of-range `--port`.

A malformed config reports the specific problem, such as a TOML syntax error, a missing required key, an unknown `[geometry]` key, or a duplicate connector `id`, rather than a traceback.

Mixing the two modes is a usage error with status 2: `--port` and `--no-browser` apply only to the designer, so they cannot be combined with a config, and `-o`, `-i` and `-t` need a config to render.
