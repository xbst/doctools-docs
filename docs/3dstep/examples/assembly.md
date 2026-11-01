---
description: "Live 3DStep assembly instructions: a PiCAN 2 USB to CAN adapter going into its printed shell, in a theme that matches this docs site."
hide:
  - toc
---
# A real assembly

A PiCAN 2 USB to CAN adapter going into its printed two-part shell, in four steps: the board into the upturned top shell, pushed toward the USB end, the bottom shell snapped on, and done. Press **Next** to step through, **Play** to watch a step's moves, or drag the view to look closer:

![Put the PiCAN 2 in its shell: interactive 3D assembly instructions](../../3d/pican2/pican2.3dstep.html){ type=iframe }

Things to try:

- **Scroll past it.** The page scrolls over the viewer until you click it, and over its step panel always; once you click the view, the wheel zooms it, and `Esc` lets go. See [Scrolling past an embedded page](../reference/page.md#scrolling-past-an-embedded-page).
- **Press Play all** to watch the whole assembly.
- **Narrow the window.** Once the frame is 760 pixels wide or less, the step panel moves under the view, and the frame grows to fit it, with no scrollbar inside. That is the [auto-height protocol](../../md-iframe/auto-height.md) at work.
- **Flip the site's light/dark toggle.** The page follows it; see [Light and dark mode](../../guides/light-dark.md).
- **Press the fullscreen button** in the corner of the view.

The page uses `isikstech`, a theme kept beside the project folders rather than bundled with 3DStep. Its page and its 3D view are transparent, so the viewer sits on this site's own background, with the site's amber for the highlights and arrows, and Roboto.

The model came from the adapter's 18 MB STEP export through the designer. The board alone had 304 bodies, of which the 2 mm size filter dropped 248, and simplifying the board to half its triangles did the rest: 3 parts and 18,537 triangles, in a 1.4 MB page.

## The sources

Download [`pican2.toml`](../../3d/pican2/pican2.toml), [`pican2.glb`](../../3d/pican2/pican2.glb) and the theme, [`isikstech.toml`](../../3d/isikstech.toml), and open the three together in the [designer](https://3dstep.isiks.tech) with **Open project**. The designer then previews the project in the site's theme, and its Generate gives this page. Opened without the theme, the project previews with the default look, and a banner offers to open `isikstech.toml`.

??? example "The theme, `isikstech.toml`"

    ```toml
    --8<-- "docs/3d/isikstech.toml"
    ```

??? example "The second step of `pican2.toml`: a move, an arrow and a label"

    ```toml
    --8<-- "docs/3d/pican2/pican2.toml:54:74"
    ```
