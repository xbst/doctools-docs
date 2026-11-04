---
description: "A live WebFlash card for the Birds' Nest, an STM32G0B1 board on USB: Klipper or Kalico, with Katapult flashed beside it or already on the board."
hide:
  - toc
---
# A board on USB

The [Birds' Nest](https://docs.isiks.tech/birds-nest/usb/manual/), a USB hub for toolchangers with an STM32G0B1 on USB and an 8 MHz crystal. The card builds Klipper or Kalico for it and flashes it over the chip's DFU bootloader, or through Katapult once Katapult is on the board:

![Flash Klipper to the Birds' Nest](../../firmware/stm32g0b1-usb/stm32g0b1-usb.webflash.html){ type=iframe }

Things to try:

- **Tick Katapult.** The card then builds Katapult and Klipper together and flashes both in one DFU session, Katapult in the first 8 KiB and Klipper after it. The **Bootloader** option is set by Katapult while it is ticked.
- **Leave Katapult unticked and keep Katapult (8 KiB).** That is a Klipper update for a board that has Katapult already: the card restarts Klipper into Katapult over USB and writes Klipper alone, with no buttons to press.
- **Pick No bootloader (flash with DFU)** for a board without Katapult, as the Birds' Nest's own manual flashes it.
- **Switch to Kalico**, or open the version list and paste the version Mainsail shows for your MCU.

The TOML offers both projects (`projects = ["klipper", "kalico"]`), opens with Katapult unticked (`[katapult] default = false`), and lets the reader pick the bootloader offset with an `[[option]]`. Everything else, such as the crystal and the USB pins, holds the defaults of `make savedefconfig`, so the defconfig is two lines.

## The sources

Download [`stm32g0b1-usb.toml`](../../firmware/stm32g0b1-usb/stm32g0b1-usb.toml) and open it on the site with **Open TOML** to change it. The photo beside it, `birds-nest.webp`, is inlined into the page by `webflash -i`.

??? example "`stm32g0b1-usb.toml`"

    ```toml
    --8<-- "docs/firmware/stm32g0b1-usb/stm32g0b1-usb.toml"
    ```
