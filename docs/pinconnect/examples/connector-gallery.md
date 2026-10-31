---
description: "Every connector type bundled with PinConnect as a live pinout: hover a card to see the connector drawn with sample pins."
---
# Connector gallery

Every connector type bundled with PinConnect, one card each. Hover or tap a card to see the type drawn with sample pins and labels, exactly as it appears in a generated pinout:

![Live gallery of every bundled PinConnect connector type](../../pinouts/connectors/connectors.pinout.html){ type=iframe style="min-height:80vh;width:100%" }

The pin names are only samples. The [connector types reference](../reference/connector-types.md) lists each type's pitch, rows and style, and explains how to add your own.

## How it is made

This page is a pinout like any other. The board image is a picture of the cards, and each card is a connector box of its own type. Both are written by the [connector gallery generator](https://github.com/xbst/doctools-docs/tree/master/tools/connector-gallery) in this site's repository, which draws the cards with PinConnect's own renderer, so the gallery always matches what PinConnect produces. When a connector type is added, rerunning it adds the card.

Source: [`connectors.toml`](../../pinouts/connectors/connectors.toml).
