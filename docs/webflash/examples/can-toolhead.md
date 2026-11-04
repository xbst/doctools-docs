---
description: "A live WebFlash card for a CAN toolhead with two setups: on a CAN bus with Katapult, or on USB with no bootloader."
hide:
  - toc
---
# A CAN toolhead

An STM32G0B1 toolhead board that runs two ways: on a CAN bus with Katapult in its first 8 KiB, updated through a USB to CAN adapter, or on USB with no bootloader. The TOML describes each as a setup, and the card asks which one the reader has:

![Flash Klipper to a CAN toolhead](../../firmware/can-toolhead/can-toolhead.webflash.html){ type=iframe }

Things to try:

- **Press Next, then pick a setup.** With two or more `[[setup]]` tables the card has a **Setup** step between Firmware and Build, one card per setup with its own options.
- **Keep Katapult ticked and pick USB, no bootloader.** That setup has no Katapult configuration, so it is disabled while Katapult is ticked. Untick Katapult to use it.
- **Change the CAN bus speed.** The option applies to the CAN setup only (`setups = ["can"]`), and with Katapult ticked it sets the speed of both, since Klipper and Katapult share it.
- **Pick None** to build Katapult alone for the CAN setup.

On the Flash step the CAN setup offers Katapult over CAN first: plug in a candleLight adapter, or a board running Klipper in USB to CAN bridge mode, and pick the toolhead from the list of nodes on the bus. The USB setup names its own methods (`methods = ["dfu", "download"]`). See [Flashing methods](../flashing.md#katapult-over-can).

## The sources

Download [`can-toolhead.toml`](../../firmware/can-toolhead/can-toolhead.toml) and open it on the site with **Open TOML**: Configure then has a **Setup** select, and Embed options lists both setups under **Setups the reader picks from**.

??? example "`can-toolhead.toml`"

    ```toml
    --8<-- "docs/firmware/can-toolhead/can-toolhead.toml"
    ```
