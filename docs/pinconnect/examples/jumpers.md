---
description: "A live PinConnect pinout of pin headers with jumper settings: on/off, one of several, combinations, and groups."
hide:
  - toc
---
# Jumper settings

Pin headers often carry jumpers that select a mode. PinConnect draws each setting as jumper caps over the pins, and the pinout's tooltip gets a button per setting. Hover a header, then press its buttons:

![Live pinout of six jumper headers with switchable settings](../../pinouts/jumpers/jumpers.pinout.html){ type=iframe }

The six headers are the common shapes, from simplest to most involved:

| Header | Shape |
|---|---|
| CAN termination | An on/off jumper: one setting fits it, the other leaves it open. |
| Boot mode | A selector with a shared middle pin: the two positions overlap on one pin. |
| Fan voltage | An N-way selector: one row is shared, and one jumper picks a pin in the other. |
| Microstepping (A4988) | Combinations: each setting lists every jumper it fits, or none at all. |
| Data routing | A multi-pole switch: two jumpers that always move together. |
| Config header | Groups: unrelated jumpers on one header, each chosen on its own. |

The [board TOML reference](../reference/board-toml.md#connectorsetting) explains how to write each one, and [the designer](../designer.md) has an editor for them.

## The source

Download [`jumpers.toml`](../../pinouts/jumpers/jumpers.toml) and open it in the [designer](https://pinconnect.isiks.tech) to see each header's settings. The board image, [`jumpers.png`](../../pinouts/jumpers/jumpers.png), is a plain board with a header drawn in each connector's box.

??? example "The fan voltage selector in `jumpers.toml`"

    ```toml
    --8<-- "docs/pinouts/jumpers/jumpers.toml:78:127"
    ```
