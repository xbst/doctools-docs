# 3DStep theme gallery

Regenerates the eight bundled-theme screenshots in [the 3DStep themes reference](../../docs/3dstep/reference/themes.md), in `docs/assets/3dstep/`: `theme-<name>-{light,dark}.webp` for `default`, `slate`, `midnight` and `workbench`. The reference for [the generated page](../../docs/3dstep/reference/page.md) uses `theme-default-light.webp` too.

For each theme it runs `3dstep` on a sample project with that theme, opens the result in the system Chrome (light and dark) on the project's second step, releases the viewer as Escape does, so the shot shows the resting state an embedded page starts in, and captures the page's root element. The example's second step has a highlighted part, an arrow and a label, so one frame shows nearly every theme token. `midnight` puts its panel below the view and `workbench` over it, so their images are taller.

Run from the repository root after a theme or viewer change that affects appearance:

```bash
python tools/3dstep-theme-gallery/generate.py                 # the live example in docs/3d/pican2/
python tools/3dstep-theme-gallery/generate.py PROJECT.toml    # your own project
```

Change `STEP` in `generate.py` for a project whose second step shows less.

Requires `playwright` and `pillow` (`pip install playwright pillow`); Playwright drives the system Chrome, no download needed, and the pages load their fonts from Google Fonts, so this needs network access. Output is resized to 1600px wide and saved as WebP (60 to 100 KB each) to keep the repository small. Commit the regenerated `.webp` files whose pixels changed.
