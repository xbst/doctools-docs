# Connector gallery

Generates two doc images and the live gallery board from the bundled connector types:

- `docs/assets/pinconnect/connector-gallery.webp` — every type in a labeled grid, shown in [connector types](../../docs/pinconnect/reference/connector-types.md).
- `docs/assets/pinconnect/label-styles.webp` — one header under each `label_style`, shown in the [board TOML reference](../../docs/pinconnect/reference/board-toml.md#label_style).
- `docs/pinouts/connectors/connectors.toml` and `connectors.webp` — the same cards as a board, with a connector box over each card, rendered by CI into the [live connector gallery](../../docs/pinconnect/examples/connector-gallery.md).

Both are drawn with pinconnect's own `render_connector_svg`, so they always match what the generator produces — no hand-drawn art to keep in sync.

Run from the repository root after adding or changing a connector type or a body style:

```bash
python tools/connector-gallery/generate.py
```

Requires `playwright` and `pillow` (`pip install playwright pillow`). Playwright drives the system Chrome, so there is no browser download. Commit the regenerated files.

A new type is picked up automatically once you add it to `GALLERY_ORDER` at the top of `generate.py`. `none` is left out on purpose, because it draws nothing and its card would be blank.
