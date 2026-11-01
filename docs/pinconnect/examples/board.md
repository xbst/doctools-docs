---
description: "A live PinConnect pinout of the OwlFC-Mini filament changer controller, in a custom theme that matches this docs site."
hide:
  - toc
---
# A real board

The [OwlFC-Mini](https://docs.isiks.tech/owlfc-mini/manual/), a filament changer controller, with 18 connectors. Hover a connector on the board for its pinout, or open the connector list with the ☰ button to browse them all:

![OwlFC-Mini interactive pinout](../../pinouts/owlfc-mini/owlfc-mini.pinout.html){ type=iframe }

Things to try:

- **Narrow the window.** Below 1080 pixels the connector list moves under the board, and the frame grows to fit it, with no scrollbar inside. That is the [auto-height protocol](../../md-iframe/auto-height.md) at work.
- **Flip the site's light/dark toggle.** The pinout follows it; see [Light and dark mode](../../guides/light-dark.md).
- **Press the fullscreen button** beside the list toggle.

The pinout uses `isikstech`, a theme kept beside the board folders rather than bundled with PinConnect. It has a transparent background, amber highlights, Roboto, and `tooltip_placement = "panel"`, which shows the selected connector in a panel under the board instead of a floating tooltip.

## The sources

Download [`owlfc-mini.toml`](../../pinouts/owlfc-mini/owlfc-mini.toml) and [`owlfc-mini.png`](../../pinouts/owlfc-mini/owlfc-mini.png) to open the board in the [designer](https://pinconnect.isiks.tech). The designer cannot read the board's own theme, so it renders the board with the default theme and says so.

??? example "The theme, `isikstech.toml`"

    ```toml
    --8<-- "docs/pinouts/isikstech.toml"
    ```

??? example "The first connector of `owlfc-mini.toml`"

    ```toml
    --8<-- "docs/pinouts/owlfc-mini/owlfc-mini.toml:1:36"
    ```
