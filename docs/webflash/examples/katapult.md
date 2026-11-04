---
description: "A live WebFlash card that builds the Katapult bootloader alone for an STM32G0B1 board and installs it with DFU."
hide:
  - toc
---
# Katapult alone

A card for the bootloader itself: Katapult for an STM32G0B1 board on USB, in the first 8 KiB of flash, installed once with the chip's DFU bootloader. After that, Klipper updates go through Katapult:

![Flash Katapult to an STM32G0B1 board](../../firmware/katapult-stm32g0b1/katapult-stm32g0b1.webflash.html){ type=iframe }

The TOML's project is `katapult`. The build also makes `deployer.bin`, which a board already running a bootloader can use to install Katapult without DFU: the Build step lists it with the other files.

To flash Katapult and Klipper together instead, use a firmware TOML with a `[katapult]` table, like [the board on USB](usb-board.md): the reader ticks Katapult and gets both in one DFU session.

## The sources

??? example "`katapult-stm32g0b1.toml`"

    ```toml
    --8<-- "docs/firmware/katapult-stm32g0b1/katapult-stm32g0b1.toml"
    ```
