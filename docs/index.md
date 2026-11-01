---
description: "Open-source documentation tools from Isik's Tech: PinConnect turns a board photo into an interactive pinout, 3DStep turns a CAD assembly into interactive 3D assembly instructions, and md-iframe embeds pages like them in MkDocs and Zensical sites."
hide:
  - footer
  - toc
---
# Isik's Tech Documentation Tools

Open-source tools for writing better hardware documentation. Initially built for [Isik's Tech docs](https://docs.isiks.tech), open-sourced so others can use them too.

<div class="grid cards" markdown>

-    ## PinConnect
    ---
    
    PinConnect turns a photo of a circuit board into an interactive pinout: hover or tap a connector to see its pinout. Make one in the browser at [pinconnect.isiks.tech](https://pinconnect.isiks.tech), or render it from a config on the command line.
    
    === "Animated demo"
        ![A generated PinConnect pinout: hovering connectors on the board, then opening the connector list and picking connectors from it](assets/pinconnect/pinout-demo.gif)
         
        *A generated pinout for the [Birds' Nest CAN](https://store.isiks.tech/products/birds-nest-CAN) board — hover a connector on the board for its pinout, or open the connector list to browse every connector at once.*
    
    === "Interactive pinout"
        ![OwlFC-Mini interactive pinout](pinouts/owlfc-mini/owlfc-mini.pinout.html){ type=iframe }
        
        *Above pinout was generated for [OwlFC-Mini docs](https://docs.isiks.tech/owlfc-mini/manual/#pinout) using PinConnect with a custom theme, embedded with [md-iframe](#md-iframe).*

    ---
    
    [Documentation](pinconnect){ .md-button .md-button--primary } [Repo](https://github.com/xbst/PinConnect){ .md-button }

-    ## 3DStep
    ---

    3DStep turns a CAD assembly into step-by-step interactive 3D assembly instructions: each step shows the parts it installs, moves them into place with arrows, and frames them from a good angle, and the reader can turn the model to look closer. Build them in the browser from a STEP file at [3dstep.isiks.tech](https://3dstep.isiks.tech), or render them from a project file on the command line.

    === "Animated demo"
        ![A generated 3DStep page: stepping through the PiCAN 2 going into its shell, each part moving into place, and the view turned to look closer](assets/3dstep/3dstep-demo.gif)

        *Assembly instructions for a PiCAN 2 USB to CAN adapter going into its printed shell — press Next and each part moves into place, or turn the model to look closer.*

    === "Interactive viewer"
        ![Put the PiCAN 2 in its shell: interactive 3D assembly instructions](3d/pican2/pican2.3dstep.html){ type=iframe }

        *Above page was generated with 3DStep using a custom theme that matches this site, embedded with [md-iframe](#md-iframe).*

    ---

    [Documentation](3dstep){ .md-button .md-button--primary } [Repo](https://github.com/xbst/3DStep){ .md-button }

-     ##md-iframe
    ---
    A Python-Markdown extension for MkDocs and Zensical sites. It turns an image-style tag into an `<iframe>` that sizes itself to the page inside it and shows a visible error when the file is missing. Supports syncing dark/light mode and automatic resizing.
     
     ---
     
    [Documentation](md-iframe){ .md-button .md-button--primary } [Repo](https://github.com/xbst/md-iframe){ .md-button }

</div>

!!! info "Coming from `pinout-gen` or `pinout-embed`? Nothing breaks; see [Migrating from the old names](migration.md)."

## License

PinConnect, 3DStep and md-iframe are licensed under GPL-3.0. Their source is on GitHub: [xbst/PinConnect](https://github.com/xbst/PinConnect), [xbst/3DStep](https://github.com/xbst/3DStep) and [xbst/md-iframe](https://github.com/xbst/md-iframe).
