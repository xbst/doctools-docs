---
description: "Every key of a 3DStep project file: the assembly, the home view, part names and colors, and each step's visibility, moves, camera, arrows and labels, with the checks 3dstep makes."
---
# Project TOML reference

A project file describes one page of assembly instructions: the models it shows, and its steps. The [designer](../designer.md) writes this file as you work, and `3dstep` reads it. You can also write or edit it by hand.

A project has an `[assembly]` table, an optional `[camera]`, any number of `[[part]]` tables, and a `[[step]]` array. Each step can hold a `[step.camera]` table and `[[step.move]]`, `[[step.arrow]]` and `[[step.label]]` arrays. Example:

```toml
[assembly]
title = "Mount the fan"
models = ["board.glb", "fan.glb"]
start = "hidden"

[camera]
position = [160.0, -190.0, 130.0]
target = [30.0, 25.0, 8.0]

[[part]]
id = "fan_30mm"
name = "30 mm fan"

[[step]]
id = "board"
title = "Lay the board down"
text = "Place the board on the bench, components up."
show = ["board"]

[[step]]
id = "fan"
title = "Screw the fan on"
text = "Hold the fan over the board, label down, and drive the **four M3 x 12 mm** screws through it."
show = ["fan_30mm", "fan_screws"]
highlight = ["fan_30mm", "fan_screws"]

  [step.camera]
  fit = ["board", "fan_30mm"]

  [[step.move]]
  parts = ["fan_30mm"]
  offset = [0.0, 0.0, 30.0]

  [[step.move]]
  parts = ["fan_screws"]
  offset = [0.0, 0.0, 45.0]

  [[step.label]]
  text = "Label down"
  at = [30.0, 25.0, 12.0]
  attach = "fan_30mm"
```

Indenting a step's sub-tables is only for reading; TOML does not need it. Every key not listed on this page is an error, so a misspelled key fails loudly instead of being ignored.

## `[assembly]`

| Key | Required | Default | Meaning |
|-----|----------|---------|---------|
| `title` | yes | — | The page's title, at the top of the step panel and in the browser tab. Must not be empty. |
| `models` | yes | — | The GLB files of the models, one per imported file, relative to this file: normally just their names, with the files beside it. Each must end in `.glb` and be listed once. |
| `description` | no | `""` | A line under the title in the panel, and the page's description for search engines. |
| `theme` | no | `"default"` | The [theme](themes.md): the colors, fonts and behavior of the page around the model. |
| `theme_dir` | no | `"./themes"` | Folder holding theme `.toml` files, relative to this file. Names not found here fall back to the themes bundled with the package. |
| `style` | no | `"lineart"` | `"lineart"`: flat parts with dark edges, like a printed manual. `"shaded"`: the model's colors, lit. |
| `up` | no | `"z"` | The model axis that points up: `"z"` (most CAD tools) or `"y"` (Fusion). One axis for every model: the designer rotates a model it adds after the first, if its axis differs. |
| `start` | no | `"visible"` | Every part before step 1: `"visible"`, or `"hidden"` for instructions whose steps add the parts. |

## `[camera]`

The home view: where the page starts, and what step 1 looks from. Optional. Without it, the page looks from the front, the right and above, and until a step sets a camera of its own, each step frames what it shows, as a [`fit`](#stepcamera) of those parts would.

| Key | Required | Default | Meaning |
|-----|----------|---------|---------|
| `position` | yes | — | Where the camera is, in millimeters. |
| `target` | yes | — | The point it looks at. Not the same point as `position`. |
| `fov` | no | `35.0` | The vertical field of view, in degrees, between 0 and 180. In the orthographic projection it sets how much the view takes in at the target, so switching projections keeps the framing. |
| `projection` | no | `"orthographic"` | `"orthographic"`, without perspective, like a manual's drawing, or `"perspective"`. |

An empty `[camera]` table counts as none.

## `[[part]]`

Display metadata for a part or a group of the models. Optional, any number.

| Key | Required | Default | Meaning |
|-----|----------|---------|---------|
| `id` | yes | — | The [id](#ids) of a node in one of the models. |
| `name` | no | the node's name in the CAD file, else its id | The display name, which the page lists under a step's title when the step highlights the part. |
| `color` | no | the model's color | A hex color, `"#3b82f6"` or `"#38f"`: the part's color in the shaded style. Line art uses the theme's colors. |

A `[[part]]` whose id no model has is a warning rather than an error, so names survive a model being imported again.

## `[[step]]`

One entry per instruction, in order.

| Key | Required | Default | Meaning |
|-----|----------|---------|---------|
| `id` | no | `"step-N"` | A name for links to the step, as in `?step=push`. Unique among the steps, an [id](#ids), and not only digits: `?step=3` means the third step. |
| `title` | no | `"Step N"` | The step's heading. |
| `text` | no | `""` | The instruction. See [Step text](#step-text). |
| `note` | no | `""` | A callout under the text, for a warning or a tip. |
| `show` | no | `[]` | Ids made visible from this step on. |
| `hide` | no | `[]` | Ids hidden from this step on. |
| `highlight` | no | `[]` | Ids tinted in this step only: the parts it installs. |
| `ghost` | no | `[]` | Ids drawn translucent in this step only, for context. A ghost must be visible to be seen, and a part both highlighted and ghosted is ghosted. |

Visibility carries over from step to step: each step applies its `hide`, then its `show`, to what the previous step displayed. Highlights, ghosts, moves, the text, the note, the arrows and the labels are the step's own, and the camera carries over unless the step sets one. [Concepts](../concepts.md#steps) walks through an example.

An id in any list may be a group's, which means every part under it. One id written in both `show` and `hide` of a step is an error; a group in `hide` with one of its parts in `show` hides the group and shows that part.

### `[step.camera]`

The step's own view. Optional: without it, the step keeps the previous step's camera (a `fit` frames its parts again, where this step shows them), and step 1 starts from `[camera]`.

| Key | Required | Default | Meaning |
|-----|----------|---------|---------|
| `position`, `target` | no | — | The step's own view, as in [`[camera]`](#camera). Give both, or neither. |
| `fit` | no | — | Instead of `position` and `target`: ids to frame, from the previous step's direction. Their outline fills the view's width or height with a 10% margin, below the buttons along the top of the view. The parts are framed where the step shows them, and moved parts where they land as well. Parts the step hides are left out, and when it hides them all, the camera frames what the step shows. |
| `fov` | no | the previous step's | As in `[camera]`. |
| `projection` | no | the previous step's | As in `[camera]`. |

A `fit` in step 1 looks from the `[camera]` direction, or from the default one without it. An empty `[step.camera]` table means the step keeps the previous view.

### `[[step.move]]`

Where parts sit in this step, relative to their assembled pose. A part with no move in a step is assembled in it. The page shows moved parts where the move puts them, and Play, or going to the next step, puts them in place.

| Key | Required | Default | Meaning |
|-----|----------|---------|---------|
| `parts` | yes | — | One or more ids. A group moves as one body. |
| `offset` | no | `[0.0, 0.0, 0.0]` | Millimeters along the model's axes. |
| `rotate` | no | `[0.0, 0.0, 0.0]` | Degrees about the model's X, Y and Z axes (Euler angles in XYZ order), about the center of the part's assembled bounding box, or the group's. |
| `arrow` | no | `true` | Draw an auto arrow from the moved part toward its place. It runs along the move in the gap between the part's bounding box as shown and the box it lands in, and shrinks as the part travels. A gap shorter than the arrow's head gets no arrow, so move a part further than its own size along the move. An arrow that would run through another part moved in the step, a fan's hub above its frame say, is left out. |

A part may be in only one move of a step, also when a group brings it in.

### `[[step.arrow]]`

An arrow of the step's own. Optional, any number.

| Key | Required | Default | Meaning |
|-----|----------|---------|---------|
| `from` | yes | — | The tail. For a rotate arrow, the center of its circle. |
| `to` | yes | — | The head. For a rotate arrow, a point on its axis. Not the same point as `from`. |
| `kind` | no | `"straight"` | `"straight"`, or `"rotate"`: an arc around the axis from `from` to `to`, with a head at its end. |
| `turns` | no | `0.75` | Rotate only: the share of a full turn the arc sweeps. Positive turns sweep clockwise as seen from `from` looking toward `to`, negative turns counterclockwise. Not 0. |
| `radius` | no | `4.0` | Rotate only: the circle's radius in millimeters. Greater than 0. |
| `color` | no | the theme's `arrow` color | Any CSS color. |
| `label` | no | `""` | Short text at the tail. |
| `attach` | no | `""` | An id: `from` and `to` are in that part's frame, and the arrow moves with the part. See [Coordinates](#coordinates). |

To show a screw being tightened, put `from` at the screw's head and `to` further along the screw, into the part: positive turns then sweep clockwise as you look at the head. The designer's Rotate arrow tool places its arrows this way, with `to` inside the part you click; make `turns` negative to show a screw coming out.

Arrows are sized from the models: an arrow's head is 3% of the diagonal of the box around every model, kept between 2 and 20 mm, and a theme scales every arrow with `arrow_scale`. A straight arrow shorter than its head is not drawn, so make `from` and `to` at least that far apart: 2 mm for an assembly up to about 67 mm across, more for a bigger one. `3dstep` and the designer's status bar warn about such an arrow, with its length and the head's:

```
pican2.toml: [[step]] #2 (push): [[step.arrow]] #1 is shorter than its head (1.5 mm < 2.0 mm) and will not be drawn
```

A rotate arrow's arc has the size its `radius` gives it, so this limit does not apply to it.

### `[[step.label]]`

A callout: a short text in a box, with a leader line to a point. Optional, any number.

| Key | Required | Default | Meaning |
|-----|----------|---------|---------|
| `text` | yes | — | The label. Must not be empty. |
| `at` | yes | — | The anchor: the point the leader line ends at. |
| `side` | no | `"auto"` | Where the box sits from the anchor: `"left"`, `"right"`, `"top"`, `"bottom"`, or `"auto"`, away from the middle of the view. |
| `attach` | no | `""` | As for arrows. |

An arrow or label attached to a part that is hidden in its step is hidden with it.

## Ids

An id names a node of a model: a part or a group. Ids are made from the names in the CAD file when a model is imported, as [Concepts](../concepts.md#models-parts-and-ids) describes, and are the node names in the GLB file. The Parts tab of the designer shows each part's id beside its name.

Each id should name one node of the whole project. A model whose ids another model already uses gets its file name in front of all of them when the designer imports it (`tq2_pi4_bolt` in `tq2_pi4.glb`); models that share ids anyway, opened together, get a warning.

In a project file an id is letters, digits, `_`, `.` and `-`, not starting with `.` or `-`. Every id a project names must exist in one of its models; a misspelled one is an error that lists the nearest ids.

## Coordinates

Every point and offset is three numbers, `[x, y, z]`, in millimeters, along the axes of the CAD file. A point in a model is the same number in the project file, the designer and your CAD tool.

The points of an attached arrow or label are measured with their part where the CAD file has it, in its assembled pose. When a step moves the part, the arrow or label moves and turns with it. The designer's tools attach what they place and convert the points for you; the inspector's **Attached** checkbox converts them back to plain model coordinates.

## Step text

The viewer renders a step's `text`:

- A blank line starts a new paragraph, and a single line break stays a line break.
- `**bold**` is bold, and `` `code` `` is code.
- `[a link](https://example.com)` is a link, which opens in a new tab. Links to `http:` and `https:` addresses and relative links work; any other kind shows as plain text.
- Nothing else is markup: HTML in the text shows as text.

A multi-line TOML string (`"""…"""`) keeps paragraphs readable in the file. The `note` takes the same markup, in one paragraph. Without JavaScript, the page shows each step's text and note as plain text.

## Checks

`3dstep` checks a project before rendering it, and the designer runs the same checks as you work: the status bar shows their result.

These are errors, and no page is written:

- Invalid TOML, or a file that is not UTF-8.
- An unknown table or key, anywhere.
- A missing `title` or `models`, or an empty title. A `models` entry that is not a `.glb` file, is an absolute path, is listed twice, or is not found.
- A value of the wrong type, a vector that is not three finite numbers, or a value outside its list, such as `style = "flat"`.
- An id that is not valid, a step id made only of digits, two steps or two `[[part]]` tables with one id, an id listed twice in one list, or one id in both `show` and `hide`.
- An id that no model has.
- One part in two moves of a step, also through a group.
- A camera with only one of `position` and `target`, with both at the same point, with `fit` beside them, or with an `fov` outside 0 to 180. An empty `fit`, a move without `parts`, an arrow whose `from` and `to` are the same point, `turns = 0`, a `radius` of 0 or less, or an empty label text.
- A `[[part]]` color that is not a hex color.

Errors name the file, the table and the key:

```
pican2.toml: [[step]] #2 (push): [[step.arrow]] #1: from and to are the same point, so the arrow has no direction
```

These are warnings: they are printed as `Warning:` lines, and the page is still written:

- A `[[part]]` for an id no model has.
- An id that two models share, so the page cannot tell those parts apart.
- A step that highlights, ghosts or moves a part that is hidden in that step, names one in its own `fit`, or attaches an arrow or label to one.
- A straight arrow shorter than its head, which the page does not draw; see [`[[step.arrow]]`](#steparrow).
- An arrow `color` that is not a CSS color. A hex color missing its `#` gets one.
- A project with no steps.
- A model without 3DStep's metadata, which is then read as millimeters with Z up.
- A problem in the theme; see [Themes](themes.md).

## A complete project

The project behind the live examples on these pages, four steps over one model of three parts:

??? example "`pican2.toml`"

    ```toml
    --8<-- "docs/3d/pican2/pican2.toml"
    ```
