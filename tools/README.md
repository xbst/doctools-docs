# Doc image generators

The images under `docs/assets/pinconnect/` are generated, not hand-made, so they can be refreshed when the thing they show changes. Each generator is a folder here with a `generate.py` and a README saying what it makes and when to rerun it.

They render with the **installed** `pinconnect`, so set up a virtual environment at the repository root first:

```bash
python -m venv venv
```

Activate it (`.\venv\Scripts\activate` in PowerShell, `source venv/bin/activate` elsewhere), then install:

```bash
pip install "git+https://github.com/xbst/PinConnect.git@master" playwright pillow
```

To shoot a change before it reaches PinConnect's `master`, install from your PinConnect clone instead: `pip install -e ../PinConnect`.

Run each one from the repository root, for example `python tools/theme-gallery/generate.py`. Playwright drives the system Chrome, so there is no browser download, and the pages load fonts (and the designer loads Pyodide) from the web, so they need network access.

| Generator | Writes | Rerun after |
|---|---|---|
| [`symbol-icons`](symbol-icons/) | `symbols/*.svg` | a change to `symbols.py` |
| [`connector-gallery`](connector-gallery/) | `connector-gallery.webp`, `label-styles.webp`, and the live gallery board in `docs/pinouts/connectors/` | a new or changed connector type or body style |
| [`theme-gallery`](theme-gallery/) | the 12 `theme-*.webp` | a theme or renderer change that affects appearance |
| [`designer-screenshots`](designer-screenshots/) | the 9 `designer-*` and `workflow-*` PNGs | a change to the designer's chrome |
| [`jumper-gallery`](jumper-gallery/) | `jumper-shapes.webp`, `workflow-jumpers.png`, and the live jumper board image | a change to how jumper settings draw, or to the designer's settings section |

`theme-gallery` and `designer-screenshots` default to the maintainer's sample board, which lives outside this repository; pass your own board TOML and image as arguments.

Regenerated images are often byte-different but pixel-identical, because encoders are not deterministic. Commit only the images whose pixels really changed.
