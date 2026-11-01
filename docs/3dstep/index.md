---
description: "3DStep turns a CAD assembly into step-by-step interactive 3D assembly instructions for documentation sites, made in the browser or rendered from a project file on the command line."
hide:
  - toc
---
# 3DStep

3DStep turns a CAD assembly into step-by-step interactive 3D assembly instructions. Each step shows the parts it installs, moves them into place with arrows, and frames them from a good angle, and the reader can turn the model to look closer. The result is a single HTML file you can open in a browser, share, or embed in a documentation site.

![Put the PiCAN 2 in its shell: interactive 3D assembly instructions](../3d/pican2/pican2.3dstep.html){ type=iframe }

There are two ways of making one:

**In the browser.** Open the designer at [3dstep.isiks.tech](https://3dstep.isiks.tech), import your STEP file, build the steps, and press **Generate**. Nothing to install: the designer reads your CAD file in the browser and nothing is uploaded. Start with [Getting started](getting-started.md).

**From the command line.** `3dstep assembly.toml` renders the same file from a saved project, which is what you want for regenerating the page as the assembly changes, or in a CI job that publishes a docs site. See [Command line and CI](command-line.md).

## Contents

### Start here

- [Getting started](getting-started.md): from a STEP file to a finished page, in the browser.
- [The designer](designer.md): a full tour, every tool, keyboard shortcuts, and what to do when something goes wrong.
- [Concepts](concepts.md): models, parts and steps, how a step's state is built, and keeping a page small.

### Going further

- [Command line and CI](command-line.md): install `3dstep`, render projects, convert STEP files on a machine, and run the designer locally.
- [Embedding with md-iframe](../md-iframe/embedding.md): put a page into an MkDocs or Zensical site.
- [Publish on a docs site](../guides/publishing.md): render pages in CI and deploy them with GitHub Pages.

### Reference

- [Project TOML](reference/project-toml.md): every key of a project file.
- [Themes](reference/themes.md): colors, fonts and layout behavior, and writing your own theme.
- [The generated page](reference/page.md): what readers can do with it, and its URL parameters and messages.
