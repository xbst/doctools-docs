---
description: "pinout-gen became pinconnect and pinout-embed became md-iframe. Every old install line, command and extension name keeps working; here is what changed and how to move to the new names."
---
# Migrating from the old names

PinConnect used to be two tools, `pinout-gen` (the command line) and `pinout-design` (the designer), with a Markdown extension called `pinout-embed`. They are now:

- **`pinconnect`**: one tool, one install, one command. `pinconnect` opens the designer, and `pinconnect board.toml` renders a board.
- **`md-iframe`**: the Markdown extension, in a repository of its own, [xbst/md-iframe](https://github.com/xbst/md-iframe). It embeds any page, not only pinouts.

**Nothing you have today breaks, and nothing will.** The old install lines, the old command, the old extension name and the old tag all keep working, for good, so a CI job or a site that installs from `master` keeps building with no changes. Move to the new names when it suits you.

## What keeps working

| You have | It still works because |
|---|---|
| `pip install "git+https://github.com/xbst/PinConnect.git@master#subdirectory=pinout_gen"` | `pinout_gen/` is now a small compatibility package that installs `pinconnect` |
| `pip install "git+https://github.com/xbst/PinConnect.git@master#subdirectory=pinout_embed"` | `pinout_embed/` is likewise a compatibility package that installs `md-iframe` |
| `pinout-gen @ git+...` and `pinout-embed @ git+...` in a requirements file | The same compatibility packages, under the same names |
| `pinout-gen board.toml -i`, `-o`, `-t` | `pinout-gen` is still installed by its package, with the same options, output and messages |
| `pinout-gen --serve 8000`, `--no-browser` | Unchanged, and opens the same designer |
| `- pinout_embed` in `markdown_extensions` | md-iframe registers itself under that name too |
| `pinout_embed:PinoutExtension` | The compatibility package still provides it |
| `{ type=application/pinout }` | md-iframe treats it exactly like `{ type=iframe }` |
| CSS for `iframe.pinconnect-embed` and `.pinconnect-embed-error` | Every embed still carries those classes |
| Pinouts that post `{pinconnectHeight}`, and `{pinconnectTheme}` messages | md-iframe still reads the old height key, and pinouts still post it; the theme message is unchanged |
| Links to `pinconnect.isiks.tech` and `<board>.pinout.html` files | Unchanged |

Upgrading a long-lived virtual environment in place, with `pip install --upgrade` on the old lines, is safe: it replaces the old packages with the compatibility ones and installs the new tools beside them.

## The one thing that does not

**An editable install of the old layout** (`pip install -e ./pinout_gen` or `pip install -e ./pinout_embed` from a clone) stops working after you pull the new code, because the files it points at have moved. Reinstall from the clone:

```bash
pip uninstall -y pinout-gen pinout-embed
pip install -e .
```

and install md-iframe from its own repository if you need it. This only affects people working on PinConnect itself.

## Moving to the new names

When you are ready, these are the replacements:

| Old | New |
|---|---|
| `pip install "git+https://github.com/xbst/PinConnect.git@master#subdirectory=pinout_gen"` | `pip install "git+https://github.com/xbst/PinConnect.git@master"` |
| `pip install "git+https://github.com/xbst/PinConnect.git@master#subdirectory=pinout_embed"` | `pip install "git+https://github.com/xbst/md-iframe.git@master"` |
| `pip install ./pinout_gen` (from a clone) | `pip install .` |
| `pinout-gen board.toml` | `pinconnect board.toml` |
| `pinout-gen --serve` | `pinconnect` |
| `pinout-gen --serve 8000` | `pinconnect --port 8000` |
| `python pinout_design/tools/build-payload.py` (build the designer's payload) | `python -m pinconnect.payload` |
| `- pinout_embed` | `- md_iframe` |
| `{ type=application/pinout }` | `{ type=iframe }` |
| `iframe.pinconnect-embed` in your CSS | `iframe.md-iframe` |

The rendering options, `-o`, `-i` and `-t`, and the output file name, `<board>.pinout.html`, are the same as before.

For a docs site built in CI, the whole change is usually three lines of the workflow and one of `mkdocs.yml`. [Publish on a docs site](guides/publishing.md) has the new workflow.

## Where the documentation went

The documentation that used to be in the PinConnect repository's `docs/` folder is now this site. The pages map like this:

| Old page | New page |
|---|---|
| `docs/README.md` | [PinConnect](pinconnect/index.md) |
| `docs/getting-started.md` | [Getting started](pinconnect/getting-started.md) |
| `docs/designer.md` | [The designer](pinconnect/designer.md) |
| `docs/concepts.md` | [Concepts](pinconnect/concepts.md) |
| `docs/automating.md` | [Command line and CI](pinconnect/command-line.md) |
| `docs/embedding.md` | [Embedding pages](md-iframe/embedding.md) and [Publish on a docs site](guides/publishing.md) |
| `docs/reference/board-toml.md` | [Board TOML](pinconnect/reference/board-toml.md) |
| `docs/reference/connector-types.md` | [Connector types](pinconnect/reference/connector-types.md) |
| `docs/reference/themes.md` | [Themes](pinconnect/reference/themes.md) and [Light and dark mode](guides/light-dark.md) |
