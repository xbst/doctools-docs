---
description: "Install the 3dstep command, render pages from a project, convert STEP files to GLB on a machine, split assemblies too big for the designer, run the designer locally, and serve it by hand."
---
# Command line and CI

The designer is the quickest way to make a page, but it needs a person. `3dstep` renders the same file from a saved project with no interaction, which is what you want for regenerating pages as an assembly changes, keeping them in version control, or publishing a documentation site from CI.

The output is identical either way. The designer runs this same renderer in the browser, so a project rendered in both places produces the same bytes.

## Install

`3dstep` needs **Python 3.9 or newer** and has no dependencies beyond the standard library on 3.11 and above. Older versions also pull in `tomli`, a TOML parser.

`pip` installs it straight from GitHub:

```bash
pip install "git+https://github.com/xbst/3DStep.git@master"
```

A virtual environment is recommended but optional:

**PowerShell**

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install "git+https://github.com/xbst/3DStep.git@master"
```

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
pip install "git+https://github.com/xbst/3DStep.git@master"
```

Check it worked:

```bash
3dstep --help
```

Installing from `master` means each install picks up the newest renderer, so regenerated pages carry the latest fixes. That is what a CI job wants; see [Publish on a docs site](../guides/publishing.md).

Converting and splitting STEP files on a machine need an optional extra; see [Convert a STEP file](#convert-a-step-file).

### From a clone

```bash
git clone https://github.com/xbst/3DStep.git
cd 3DStep
pip install .
```

### For development

```bash
pip install -e .
```

An editable install also makes `3dstep` serve the designer files in your checkout, so edits to them take effect on reload. The same goes for the Python code, the viewer and the themes: the designer's renderer is built from the package, and a running `3dstep` rebuilds it when the reloaded designer asks for it. Only a change to the server itself (`serve.py`, `payload.py`) needs a restart.

## Run the designer locally

Installing the tool also installs the designer. Run `3dstep` with no file to open it:

```bash
3dstep
```

That builds what the designer needs, starts a local server on a free port, opens a browser, and prints where everything is:

```
Designer:  /path/to/threedstep/designer
Payload:   /path/to/threedstep.zip  (270 KB)
Serving:   http://127.0.0.1:50213
Press Ctrl+C to stop.
```

`--port 8000` picks the port; `--no-browser` skips opening one.

Use this when you want the designer offline from the hosted site, or when you are working on the designer itself. The STEP reader is served from your machine, but the designer still downloads its Python runtime from a CDN on first load, which Generate needs. A fully offline machine should render with the command line instead.

### Serving the designer by hand

`3dstep` is the easy way. To serve the designer with another web server instead, put three things in one folder: the designer's files, the viewer runtime it loads from `viewer/`, and the payload it fetches at startup, `threedstep.zip`. Without the payload, the designer boots into "Renderer unavailable".

This prints where the installed designer and viewer are:

```bash
python -c "from threedstep.payload import designer_root, viewer_root; print(designer_root()); print(viewer_root())"
```

Copy the designer folder, copy the viewer folder into the copy as `viewer`, then build the payload into it:

```bash
python -m threedstep.payload <your copy>/threedstep.zip
```

In a clone of the repository the two folders are `src/threedstep/designer/` and `src/threedstep/viewer/`. The hosted designer is published this way by the repository's GitHub Pages workflow.

The designer must be served over HTTP, with `.js` files as JavaScript: opening `index.html` from disk cannot fetch the payload. Rebuild the payload after upgrading `3dstep`, or add `--force` to rebuild it regardless.

## Render a project

```bash
3dstep assembly.toml
```

This writes `assembly.3dstep.html` beside the project, and prints what it did:

```
Generated: /path/to/assembly.3dstep.html  (4 steps, 3 parts, 1.40 MB)
```

Write somewhere else with `-o` / `--output`. The directory must already exist, and `3dstep` refuses an output path that names a folder, the project, one of its models or its theme.

```bash
3dstep assembly.toml -o docs/3d/assembly.3dstep.html
```

## What it needs alongside the project

Two things are resolved relative to the project file:

- **The models**, from `models` in `[assembly]`: the GLB files the designer saved, beside the project. They are written into the page, so it needs nothing beside it.
- **The theme**, from `theme_dir` (default `./themes`, beside the project) first, then the themes bundled with the package. See [Themes](reference/themes.md).

The designer cannot read a project's own `theme_dir`, which is on your disk: open the theme's file there together with the project, and its Generate gives this command's page. See [a site's own theme](designer.md#a-sites-own-theme).

## Choose a theme

`-t` / `--theme` overrides the project's `[assembly] theme` for one run:

```bash
3dstep assembly.toml --theme midnight
```

The bundled themes are `default`, `midnight`, `slate` and `workbench`.

## Convert a STEP file

`3dstep model.step` turns a STEP file into a GLB on your machine, the same model the designer's import makes. It is for pipelines that keep only the STEP file in the repository, and for files too big for the designer: the browser's STEP reader stops at 2 GB of memory, which a STEP file of about 45 MB fills, and the command line has no such limit. To import such a file in the designer instead, [split it](#split-a-big-assembly).

It needs an optional extra, the Python bindings of OpenCascade, which have wheels for Python 3.11 and newer on Windows, Linux and macOS (about 50 to 70 MB to download):

```bash
pip install "3dstep[step] @ git+https://github.com/xbst/3DStep.git@master"
```

From a clone, `pip install ".[step]"`. On Python 3.9 and 3.10 the extra installs nothing, and the convert mode says the dependency is missing.

```bash
3dstep "PiCAN2-in-Shell.step" --min-size 2
```

This writes the GLB beside the STEP file, under the name the designer gives the same import, so a project made in the designer finds the file this regenerates:

```
Wrote /path/to/pican2_in_shell.glb  (3 parts, 35011 triangles, 0.67 MB)
```

The options are the import dialog's:

| Option | Default | Meaning |
|---|---|---|
| `-o OUT` | `<name>.glb` beside the STEP file | The GLB to write. |
| `--quality fine\|normal\|coarse` | `normal` | The tessellation preset: how finely curved surfaces become triangles. The same presets as the designer. |
| `--deflection MM`, `--angle DEG` | | Instead of a preset: the largest distance between a surface and its triangles, in millimeters, and the largest angle between neighboring triangles, in degrees. |
| `--min-size MM` | `0` | Drop bodies whose bounding-box diagonal is smaller. Parts keep the same ids whatever the filter. |
| `--merge-bodies` / `--no-merge-bodies` | merged | One part per component, its bodies merged, or one part per body. |
| `--id-prefix PREFIX` | | Put `PREFIX` in front of every id: `--id-prefix tq2_pi4_` makes `bolt` `tq2_pi4_bolt`. It must start with a letter, a digit or `_`, and hold only letters, digits, `_`, `.` and `-`. |

The designer prefixes the ids of a model whose ids another model of the project already uses, with the model's file name and `_` (see [Import a model](designer.md#1-import-a-model)). To regenerate such a model's GLB, pass the same prefix:

```bash
3dstep tq2-pi4.step --id-prefix tq2_pi4_
```

The command line and the designer read a STEP file the same way: the same tree of groups and parts, the same ids, names and colors, so a project written in the designer works with either GLB. The triangles differ, though. The designer's reader is built on OpenCascade 7.6 and the extra on 8.0, whose meshers do not always split a curved face the same way: the example above has 34,691 triangles imported in the designer and 35,011 converted here. The same converter on Linux and on Windows can split a few faces differently too. Commit the GLB the designer wrote where you want the same file every time, and convert in pipelines that regenerate GLBs from STEP files.

The converter does not simplify. To get a big model under the [size guidance](concepts.md#keeping-pages-small), open its GLB in the designer, simplify there, and save.

The converter keeps the STEP file's axes, and the GLB always records Z as its up axis: it cannot know which axis the CAD tool had up. A model from a Y-up CAD tool such as Fusion needs `up = "y"` in its project's `[assembly]`, and when you add its GLB to a project in the designer, choose **Y** as its up axis in the import dialog. The designer rotates a model added to a project with the other up axis (see [Import a model](designer.md#1-import-a-model)); the converter never does, so it cannot regenerate such a model's GLB: commit the GLB the designer wrote for it.

## Split a big assembly

The designer's STEP reader stops at 2 GB of memory, which a STEP file of about 45 MB fills while reading. `3dstep split` cuts such an assembly into several smaller STEP files by its top-level components. Each file is one assembly that holds some of the components, each where the original assembly has it and with its names and colors, so the designer imports the files one after another as models of one project that line up. It needs the same extra as [converting](#convert-a-step-file).

Start by listing the top-level components, to see what there is to split:

```bash
3dstep split "TQ2-on-Pi.step" --list
```

```
TQ2-on-Pi.step: assembly 'TQ2 on Pi', 20 top-level components of 8 products
instances  bodies  product
        1     650  Assembly Raspberry Pi 4 Model B step
        4       8  M3x20 Standoff v1
        1     803  TQ2-T5
        1       4  3010 Axial Fan
        4       4  M2.5 Threaded Insert
        4       4  M2.5x6 BHCS
        4       4  M2.5x16 BHCS
        1      53  TQ2-USB
```

A product is a part or a sub-assembly of the CAD file, and each place the assembly uses it is an instance. The body counts show where the size is: in this ToqueCAN 2 on a Raspberry Pi, a 71.5 MB file, the Pi and the TQ2-T5 board hold most of the 1,530 bodies. A file of several top-level shapes with no assembly around them lists the shapes instead.

The split cuts the assembly at its top level only: a sub-assembly among the components goes into a file whole, and `take` cannot name a product inside one. The designer and `3dstep model.step` read a STEP file the same way, keeping the top-level components and flattening everything below them into bodies, so a board exported with its heatsink is one part on every path. For a part inside a sub-assembly that the instructions move on its own, export the sub-assembly from your CAD tool as a STEP file of its own, in its assembled position, or make the part a top-level component of the assembly; in the designer, Split and Merge group can separate one body from the rest, see [Import a model](designer.md#1-import-a-model).

Without a spec, `3dstep split` writes one file per product, named after it (`tq2_t5.step`, `m2_5_threaded_insert.step`, …), beside the assembly. A spec groups the components into the files you want instead. It is TOML, with one `[[file]]` table per file:

```toml
[[file]]
name = "tq2-pi4.step"
assembly = "TQ2 Pi 4"
take = ["Assembly Raspberry Pi 4 Model B step"]

[[file]]
name = "tq2-board.step"
assembly = "TQ2 board"
take = ["TQ2-T5"]

[[file]]
name = "tq2-hardware.step"
assembly = "TQ2 hardware"
take = ["*"]
```

```bash
3dstep split "TQ2-on-Pi.step" --spec tq2-split.toml
```

```
Wrote /path/to/tq2-pi4.step  (TQ2 Pi 4: 1 component, 20.57 MB)
Wrote /path/to/tq2-board.step  (TQ2 board: 1 component, 43.59 MB)
Wrote /path/to/tq2-hardware.step  (TQ2 hardware: 18 components, 7.62 MB)
```

| Key | Required | Meaning |
|---|---|---|
| `name` | yes | The STEP file to write: a file name ending in `.step` or `.stp`, without a folder. Two files cannot have the same name. |
| `assembly` | yes | The name of the assembly in the file. The designer names the model's top group, and that group's id, after it, so each file needs its own: a model with an id that another model already uses gets all of its ids prefixed. |
| `take` | yes | The products the file holds, as `--list` names them: every instance of each. `"*"` takes every product no other file names, in one file at most. A product goes in one file only. |

A product that no file takes is left out of the split, with a warning. The spec's mistakes are errors named like the project file's, such as `tq2-split.toml: [[file]] #2: take: 'TQ2 T5' is not a top-level component (nearest: TQ2-T5)`, and nothing is written.

| Option | Default | Meaning |
|---|---|---|
| `--list` | | Print the top-level components, in the file's order, and write nothing. |
| `--spec SPLIT.toml` | a file per product | Which components go into which file. |
| `-o OUT_DIR` | the assembly's folder | The folder to write the files in, made if it is missing. A file that would replace the assembly itself is refused. |

The ToqueCAN 2 split takes about 30 seconds, and the designer then reads the three files in a minute or two. Import them one after another: each becomes a model of the project, and they sit together as in the assembly. The edges are written without their 2D curves, which OpenCascade computes again when it reads a file, so together the files are about the size of the original. One product too big on its own, such as a board with every component modeled, stays too big after the split: drop detail from it in your CAD tool, or convert it with [`3dstep model.step`](#convert-a-step-file) and import the GLB.

## Regenerating as an assembly changes

The project and its models are the things worth keeping in version control. A page is derived from them, so an assembly revision means editing the project, or importing the new STEP file over the old model, and running the command again rather than starting over:

```bash
3dstep docs/3d/fan/fan.toml
```

Because the designer and the command produce the same bytes, you can move between them freely: build the steps visually, save the project, and regenerate it from a script afterwards.

To render every page of a docs site on each deploy, see [Publish on a docs site](../guides/publishing.md).

## Common errors

All of these print to stderr and exit with status 1.

- **`Error: project file not found`**: check the path and your working directory.
- **`Error: model file not found`**: a GLB the project names in `[assembly] models` is not beside it. The message says which project names it.
- **`Error: … unknown id '<id>' (nearest: …)`**: a step names a part no model has, usually after a model was imported again with other names. The message says where, and lists the nearest ids.
- **`Error: Theme '<name>' not found`**: no `<name>.toml` in either `theme_dir` or the bundled themes. The message names both folders. See [Themes](reference/themes.md).
- **`Error: the output would overwrite …`** and **`Error: the output is a folder, not a file`**: `-o` names one of the inputs, or a folder. For `3dstep split`, **`Error: the output is a file, not a folder`**: its `-o` names a file.
- **`Error: cannot write output file`**: the `-o` folder does not exist, or the file cannot be written there.
- **`Error: STEP conversion needs the optional dependency`** and **`Error: Splitting a STEP file needs the optional dependency`**: install the `step` extra, as above.
- **`Error: … could not be read as a STEP file`**: OpenCascade could not read it. The message quotes its last messages.
- **`Error: … has no bodies of N mm or larger; lower the size filter`**: `--min-size` dropped everything.
- **`Error: out of memory while converting …`**: use `--quality coarse`, or split the assembly into smaller STEP files with [`3dstep split`](#split-a-big-assembly).
- **`Error: <spec>: [[file]] #N: …`**: a problem in a split spec, such as an unknown or missing key, a product that is not a top-level component, a product two files take, or two files with one name or one assembly name. The message lists the nearest product names.
- **`Error: … has no components to split: it holds one part`**: the STEP file is a single part.
- **`Error: port must be between 0 and 65535`**: an out-of-range `--port`.

A malformed project reports the specific problem with the file, the table and the key, such as a TOML syntax error, an unknown key, a missing required key or a value of the wrong type, rather than a traceback. See [Project TOML](reference/project-toml.md#checks). Problems the page renders with anyway, such as a highlight on a part hidden in that step, print as `Warning:` lines, and the page is still written.

Mixing the modes is a usage error with status 2: `--port` and `--no-browser` apply only to the designer, `-t` only to rendering a project, and the convert options only to converting a STEP file. `--quality` is a preset for `--deflection` and `--angle`, so give one or the other. `3dstep split` takes only its own options, and `--list` writes nothing, so it takes neither `-o` nor `--spec`.
