# Doc image generators

The images under `docs/assets/pinconnect/` and `docs/assets/3dstep/` are generated, not hand-made, so they can be refreshed when the thing they show changes. Each generator is a folder here with a `generate.py` and a README saying what it makes and when to rerun it.

They render with the **installed** `pinconnect` and `3dstep`, so set up a virtual environment at the repository root first:

```bash
python -m venv venv
```

Activate it (`.\venv\Scripts\activate` in PowerShell, `source venv/bin/activate` elsewhere), then install:

```bash
pip install "git+https://github.com/xbst/PinConnect.git@master" "git+https://github.com/xbst/3DStep.git@master" playwright pillow
```

To shoot a change before it reaches a tool's `master`, install from your clone instead: `pip install -e ../PinConnect` or `pip install -e ../3DStep`.

Run each one from the repository root, for example `python tools/theme-gallery/generate.py`. Playwright drives the system Chrome, so there is no browser download, and the pages load fonts (and the designers load Pyodide) from the web, so they need network access.

| Generator | Writes | Rerun after |
|---|---|---|
| [`symbol-icons`](symbol-icons/) | `symbols/*.svg` | a change to `symbols.py` |
| [`connector-gallery`](connector-gallery/) | `connector-gallery.webp`, `label-styles.webp`, and the live gallery board in `docs/pinouts/connectors/` | a new or changed connector type or body style |
| [`theme-gallery`](theme-gallery/) | the 12 `theme-*.webp` | a theme or renderer change that affects appearance |
| [`designer-screenshots`](designer-screenshots/) | the 9 `designer-*` and `workflow-*` PNGs | a change to the designer's chrome |
| [`jumper-gallery`](jumper-gallery/) | `jumper-shapes.webp`, `workflow-jumpers.png`, and the live jumper board image | a change to how jumper settings draw, or to the designer's settings section |
| [`3dstep-theme-gallery`](3dstep-theme-gallery/) | the 8 `3dstep/theme-*.webp` | a 3DStep theme or viewer change that affects appearance |
| [`3dstep-designer-screenshots`](3dstep-designer-screenshots/) | the 13 `3dstep/designer-*` and `3dstep/workflow-*` PNGs | a change to the 3DStep designer's chrome or tools |

`theme-gallery` and `designer-screenshots` default to the maintainer's sample board, which lives outside this repository; pass your own board TOML and image as arguments. The 3DStep generators default to the live example in `docs/3d/pican2/`; only their two import-dialog shots need a STEP file from outside the repository, and are skipped without one.

`docs/assets/3dstep/3dstep-demo.gif` is the one image not made here: it is the animation at the top of the 3DStep repository's README, copied in for the home page.

Regenerated images are often byte-different but pixel-identical, because encoders are not deterministic. Commit only the images whose pixels really changed.
