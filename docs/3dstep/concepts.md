---
description: "How 3DStep's pieces fit together: projects and models, parts and ids, how each step's state is built, motion, cameras, styles, themes, and keeping pages small."
---
# Concepts

This page explains how 3DStep's pieces fit together, what a project describes, and how each step's picture is built from it. Understanding these makes everything else in the docs clearer.

## How the pieces fit

3DStep is a renderer with two front ends and an optional publishing step.

- The **project** is the real artifact: a TOML file describing the assembly's steps, beside one GLB file per imported **model**, holding its parts.
- The **renderer** reads them and writes a single HTML file: the viewer, the steps and the models are all inside it.
- The **designer** is a visual way to write the project. It reads STEP files, writes the GLB models, and loads the renderer into your browser to call it, so the preview and the download come from the same code as the command line tool.
- **[md-iframe](../md-iframe/index.md)** is glue for documentation sites, turning the generated HTML into an iframe in a Markdown page that sizes itself and follows the site's light and dark mode. It is a separate tool, and embeds any page.

There is one renderer, not two. A project and its models produce the same bytes whether you press Generate in the browser or run `3dstep` in a terminal.

The STEP converter is the one place where the two front ends differ. `3dstep model.step` reads a STEP file into the same parts, ids, names and colors as the designer's import, but OpenCascade's newer mesher, which the command line uses, splits some curved faces into different triangles, so its GLB is not the designer's byte for byte. The GLB file is what fixes a page's bytes; see [Convert a STEP file](command-line.md#convert-a-step-file).

The same extra splits an assembly too big for the designer's STEP reader, about 45 MB or more, into several STEP files by its top-level components. `3dstep split` keeps each component where the assembly has it and gives each file an assembly of its own, so the designer imports the files as models of one project that line up; see [Split a big assembly](command-line.md#split-a-big-assembly).

Keep the project and its models. A page is derived from them, so when the assembly changes you edit and regenerate rather than starting over. You can write a project by hand; the designer is a convenience, not a requirement, though it is the only way to import a STEP file without the optional extra.

## Models, parts and ids

A **model** is one imported file, stored as one GLB. A project has one or more: a board, the enclosure it goes into, the screws.

Inside a model is the assembly's tree, as the CAD file has it. A **part** is a node with geometry: the unit you show, hide, move and highlight. A **group** is a node with children, and naming a group anywhere in a project means every part in it.

Every node has an **id**, made from its name in the CAD file: accents and other non-ASCII characters are dropped, letters are lowercased, and every run of other characters becomes `_`, so `M3 x 8 Screw` becomes `m3_x_8_screw`. Names that repeat get `_2`, `_3` and so on, in the order the file lists them. Ids never change after the import: renaming a part in the designer changes its display name, not its id, so every step that names it keeps working. Ids are what you write in the [project file](reference/project-toml.md).

Ids are made one model at a time, so two models can have parts with the same names: the screws of an assembly exported as several STEP files, say, or one file imported twice. The page has to tell every part apart, so when you add a model whose ids another model of the project already uses, the designer puts the new model's file name in front of all of its ids: in `tq2_pi4.glb`, `bolt` becomes `tq2_pi4_bolt`. It prefixes every id of that model or none, and the import dialog says so before you add it. Opening a project renames nothing.

**Units and axes** are the CAD file's own: millimeters, and the axes your CAD tool shows, with `up` saying which one points up (Z in most CAD tools, Y in Fusion). Every coordinate you see in the project file, the designer and your CAD tool is the same number. Nothing is scaled or turned to suit a 3D format.

A project has one up axis, which its first model sets. A model you add later from a CAD tool with the other axis up is rotated a quarter turn to the project's axis when the designer imports it, so that it stands upright beside the others; its coordinates are then the project's, not its CAD tool's.

A part's **assembled pose** is where it sits in the CAD file, the place it ends up when the assembly is done.

## Steps

A step is one instruction and the picture that goes with it. Each step is a complete state, built from the steps before it:

- **Visibility carries over.** Before step 1, every part is visible, or every part is hidden with `start = "hidden"`, which suits instructions that add parts as they go. Each step then hides parts and shows parts, in that order, and they stay that way in the steps that follow until a later step changes them.
- **Highlights and ghosts belong to one step.** `highlight` tints the parts this step installs, and the page names them under the step's title. `ghost` draws parts translucent, for context: a board the parts are going around, say. The next step starts with neither.
- **Moves belong to one step.** A move says where parts sit in this step, as an offset and a rotation from their assembled pose. A part with no move in a step is assembled in it.
- **The camera carries over.** A step without a view of its own keeps the previous step's, and step 1 without one starts from the home view.
- **The text, the note, the arrows and the labels belong to one step.**

So the steps of a board going into a case might read:

| Step | Shows | Highlights | Moves |
|---|---|---|---|
| 1. Place the case | the case | the case | |
| 2. Lay the board in | the board | the board | the board, 20 mm above the case |
| 3. Fit the screws | the screws | the screws | the screws, 15 mm above their holes |

In step 3 the case and the board are still visible, the board is back in its place because step 3 does not move it, and only the screws are tinted.

The designer edits steps this way too. Showing a part in one step keeps every other step as it was, and reordering or deleting steps rewrites the project so that every step still shows the same parts.

## Motion

What the reader sees when the step changes:

- **Going to a step**, with Next, Previous, the step list or a key: parts glide from where they are shown to where the new step shows them, parts that appear or disappear fade, and the camera flies to the new step's view. That takes 600 ms in the bundled themes.
- **Play** moves the step's moved parts from their offsets into their assembled places, in 900 ms. Pressing it again, **Reset**, puts them back.
- **Next** first plays the moves the next step does not keep, then goes on. A board pulled out in step 2 slides in when the reader presses Next, then the camera flies to step 3. Reading through with Next shows every part going into place.
- **Play all** steps through from the current step on its own: the moves, a pause, the next step. It stops at the last step, or as soon as the reader changes the step, presses Play or turns the view.
- **An auto arrow** points from a moved part toward its place. It is on for every move unless the move says `arrow = false`, and it shrinks as the part travels and vanishes when the part arrives. It runs along the move in the gap between the part as shown and where it lands, from the side of the part's bounding box that faces its place to the near side of the box it lands in, so it never starts inside the part nor ends buried in what the part goes into. Its length is the move less the part's size along it: a screw 17.5 mm long moved 22 mm along its length gets a short arrow under its tip, moved 30 mm a clear one, and a move shorter than the part plus the arrow's head gets none. A wide part seen from above hides the arrow under it: the 30 mm fan of the ToqueCAN 2 guide, seen from about 30° above, shows its arrow only when lifted more than about 32 mm, so it is lifted 40. An arrow that would run through another part the step moves, a fan's hub above its frame say, is left out.

Themes can change the durations and play each step's moves as soon as it is shown. A reader whose system asks for reduced motion gets no animation at all: steps switch at once.

## Arrows and labels

- A **straight arrow** points from one point to another, for a motion a move cannot show, such as pushing a part along.
- A **rotate arrow** turns around an axis, for screwing and twisting.
- A **label** is a short callout in a box, with a leader line to a point.

An arrow or label can be **attached** to a part. Its points are then measured in that part's frame, so it moves with the part: an arrow attached to a screw travels with the screw as it goes into place. The designer's tools attach what they place to the part you click.

Arrows are sized from the model, within limits, so they suit a small board and a big enclosure alike. A theme can scale them.

## Cameras

The **home view**, `[camera]`, is where the page starts. Each step can have its own view, a position and a point to look at, or a **fit** list: the camera then frames those parts from the previous step's direction, where the step shows them and, for moved parts, where they land as well. Their outline, as seen from there, fills the view's width or height with a margin, below the buttons along the top of the view. A fit frames only the parts the step shows: hidden ones in the list are left out, and a list whose parts are all hidden frames what the step shows instead. A step without either keeps the previous step's camera: the same view, or the same fit list framed again in this step. A project without a home view starts from the front, the right and above, and until a step sets a camera of its own, each step frames what it shows.

The view is **orthographic** by default, without perspective, like the drawings in a printed manual. `fov` sets the framing in both projections, so switching between them keeps the parts the same size on screen.

The reader can always turn, pan and zoom the view; **Reset view** goes back to the step's.

## Line art and shaded

The **line art** style, the default, draws parts flat in the theme's fill color with their outlines and creases as edges, white with dark edges in the default theme's light palette, like the drawings of a printed manual, and tints the parts a step installs. It reads clearly on a phone, and looks the same whatever colors the CAD file has.

The **shaded** style draws the model in its own colors with soft lighting. A project picks one with `style`, a page link can pick one with `?style=`, and a theme can add a button that switches between them.

## Themes

The project says what the page shows; a theme says how the page looks around it: its colors in light and dark mode, its fonts, and how the step panel and buttons behave. The same project renders in any theme.

Four themes ship with 3DStep: `default`, `slate`, `midnight` and `workbench`. A project picks one with `theme`, and `3dstep -t` overrides that for one run. A theme name is looked up in the project's `theme_dir` (default `./themes`, beside the project) first, then in the bundled themes, so a documentation site can keep a theme of its own beside its projects. See [Themes](reference/themes.md).

The designer only sees the bundled themes. It cannot read a theme in a project's own `theme_dir`, since that lives on your disk: it previews such a project with the default look and says so, and its Generate dialog renders it only in a bundled theme, which also sets the project's `theme` until you undo it. Render those projects with the [command line](command-line.md).

## Keeping pages small

The page carries everything it shows, the models included, so its size follows theirs. The viewer takes about 0.9 MB of every page, and each 10,000 triangles of the models add about 0.3 MB more. Keep a page under about **3 MB**, roughly 70,000 triangles, so that it loads quickly on a phone. The example on these pages has 18,537 triangles and makes a 1.4 MB page.

A CAD model of a product is usually far over that. The ways down, roughly in the order they help:

1. **Drop small bodies** at the import. The default of 2 mm leaves out the resistors, capacitors and pins of a board from an EDA tool, often a third or more of its triangles.
2. **Delete** what the instructions never show, in the Parts tab.
3. **Merge** a group into one part when its parts never move apart. A merged part also draws faster.
4. **Simplify** the parts with the most triangles. A board can usually go to a fifth of its triangles before the line art looks any different.
5. **Import at Coarse quality**, for models with many curved surfaces.
6. **Split the instructions** into one page per section, each with only the parts its steps need, rather than one page for the whole product.

The designer shows the page size as you work, in the Parts tab and the status bar.

## What "self-contained" means for the output

`3dstep` writes a single HTML file with its CSS, its JavaScript, the 3D library, the steps and the models inlined, so it works opened directly from disk or served from any static host, with nothing beside it.

Its one external reference is the theme's font, if the theme loads one from Google Fonts, which every bundled theme does (Roboto, Glegoo or Inter). Without a network the page still renders, with a system font. For a page with no external references at all, use a theme with a `bundled` or `system` font; see [Themes](reference/themes.md#font-and-fontlabel).

The page also stays readable without JavaScript or WebGL: the steps' titles and text are in the HTML itself. See [The generated page](reference/page.md#without-webgl).

## Where to go next

- [Getting started](getting-started.md): make a page, end to end.
- [Project TOML](reference/project-toml.md): every key of a project file.
- [Themes](reference/themes.md): restyle the page's colors, fonts and behaviors.
- [The generated page](reference/page.md): what readers can do with it, and how to embed it.
