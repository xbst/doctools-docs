# 3DStep designer screenshots

Regenerates the thirteen screenshots of the 3DStep designer used in [the designer](../../docs/3dstep/designer.md) and [getting started](../../docs/3dstep/getting-started.md) pages, in `docs/assets/3dstep/`: `designer-overview.png`, `designer-toolbar.png`, `designer-simplify.png`, `designer-about.png`, and `workflow-1..9-*.png`.

The script serves a temporary copy of the installed `3dstep` designer locally on a free port, then Playwright drives the real UI in the system Chrome. It imports a STEP file to capture the import dialog and its review, cancels the import, opens a project (its TOML and GLB models), and captures the panels on the project's second step, the Move gizmo on a part, the Arrow tool halfway through placing an arrow, the Generate dialog, the Simplify dialog and the About box. Shots are dark at 2x, matching the designer's fixed dark chrome.

Run from the repository root after a change to the designer's chrome or tools (fonts, layout, panel markup, toolbar):

```bash
python tools/3dstep-designer-screenshots/generate.py                          # the live example, and the maintainer's STEP file
python tools/3dstep-designer-screenshots/generate.py PROJECT.toml MODEL.step   # your own project and STEP file
```

The project defaults to `docs/3d/pican2/pican2.toml` in this repository. The STEP file defaults to the PiCAN 2 export the example was made from, which lives outside it, in a 3DStep checkout beside this one; without a STEP file, the two import shots (`workflow-1-import.png`, `workflow-2-review.png`) are skipped. The Move shot selects the part `pican2` if the project has it, otherwise the first part; change `SHOW_STEP` and `MOVE_PART` at the top of `generate.py` for another project.

These details keep the images honest and independent of which project you pass:

- It builds the Pyodide payload into the served copy, with the viewer runtime beside it, and waits for the runtime to report ready. Without that the designer shows "Renderer unavailable", and Generate and the status bar's checks would be missing from every shot.
- It strips `theme` and `theme_dir` from a copy of the project before opening it. Opened without its theme file, a project naming a site theme would preview with the default look under a banner asking for that file; the original file is not modified.
- Its HTTP server binds an ephemeral port, serves the designer's files with explicit content types (a Windows registry can map `.js` to plain text), and shuts down after capture, so it does not claim a fixed port or interfere with another development server.

Requires `playwright` (`pip install playwright`); it drives the system Chrome, no download needed. The designer loads Roboto from Google Fonts and Pyodide from a CDN, so this needs network access. Commit the regenerated PNGs whose pixels changed.
