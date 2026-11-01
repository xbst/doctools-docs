---
description: "Install the 3dstep command, render pages from a project, convert STEP files to GLB on a machine, run the designer locally, and serve it by hand."
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

Converting STEP files on a machine needs an optional extra; see [Convert a STEP file](#convert-a-step-file).

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

A project using its own `theme_dir` is one the designer cannot render faithfully, since that theme is on your disk. Render those with this command.

## Choose a theme

`-t` / `--theme` overrides the project's `[assembly] theme` for one run:

```bash
3dstep assembly.toml --theme midnight
```

The bundled themes are `default`, `midnight`, `slate` and `workbench`.

## Convert a STEP file

`3dstep model.step` turns a STEP file into a GLB on your machine, the same model the designer's import makes. It is for pipelines that keep only the STEP file in the repository, and for files too big for the designer: the browser's STEP reader stops at 2 GB of memory, which a STEP file of about 45 MB fills, and the command line has no such limit.

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

The converter does not simplify. To get a big model under the [size guidance](concepts.md#keeping-pages-small), open its GLB in the designer, simplify there, and save. The GLB always records Z as its up axis; a model from a Y-up CAD tool such as Fusion needs `up = "y"` in its project's `[assembly]`.

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
- **`Error: the output would overwrite …`** and **`Error: the output is a folder, not a file`**: `-o` names one of the inputs, or a folder.
- **`Error: cannot write output file`**: the `-o` folder does not exist, or the file cannot be written there.
- **`Error: STEP conversion needs the optional dependency`**: install the `step` extra, as above.
- **`Error: … could not be read as a STEP file`**: OpenCascade could not read it. The message quotes its last messages.
- **`Error: … has no bodies of N mm or larger; lower the size filter`**: `--min-size` dropped everything.
- **`Error: out of memory while converting …`**: use `--quality coarse`, or split the assembly into smaller STEP files.
- **`Error: port must be between 0 and 65535`**: an out-of-range `--port`.

A malformed project reports the specific problem with the file, the table and the key, such as a TOML syntax error, an unknown key, a missing required key or a value of the wrong type, rather than a traceback. See [Project TOML](reference/project-toml.md#checks). Problems the page renders with anyway, such as a highlight on a part hidden in that step, print as `Warning:` lines, and the page is still written.

Mixing the modes is a usage error with status 2: `--port` and `--no-browser` apply only to the designer, `-t` only to rendering a project, and the convert options only to converting a STEP file. `--quality` is a preset for `--deflection` and `--angle`, so give one or the other.
