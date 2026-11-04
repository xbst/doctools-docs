---
description: "A live WebFlash card that flashes a ready-made firmware file: nothing to configure, build or download besides the file itself."
hide:
  - toc
---
# A prebuilt file

A card for a firmware file that is flashed as it is: here a Katapult build for the STM32G0B1, installed with the chip's DFU bootloader. A `[prebuilt]` board has two steps, Firmware and Flash, and loads no Python and no compiler:

![Flash a prebuilt Katapult to an STM32G0B1 board](../../firmware/prebuilt/prebuilt.webflash.html){ type=iframe }

`webflash -i` inlines the file into the page, so the card works on its own. Without `-i` the card loads the file from beside the page, and the fallback card links to it for download.

A `.bin` file has no load address of its own, so the TOML gives it: `address = 0x08000000`. The `mcu` key names the chip it is for, and the card shows it on the Firmware step.

## The sources

Download [`prebuilt.toml`](../../firmware/prebuilt/prebuilt.toml) and [`katapult.bin`](../../firmware/prebuilt/katapult.bin) (the site's own build of [Katapult alone](katapult.md), flashed and checked on a board).

??? example "`prebuilt.toml`"

    ```toml
    --8<-- "docs/firmware/prebuilt/prebuilt.toml"
    ```
