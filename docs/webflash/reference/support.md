---
description: "Which chips WebFlash builds firmware for, which flashing methods each can use, which boards it has run on, what each browser supports, and what WebFlash v1 does not do."
---
# Chips, methods and browsers

WebFlash builds firmware for the Arm chips Klipper, Kalico and Katapult support, and flashes it from Chrome or Edge on a computer. This page lists what each chip family can be flashed with, what has run on real boards, and what each browser can do.

## Chips

WebFlash builds whatever the project's Kconfig offers for an Arm architecture. Which flashing methods the Flash step and a card offer follows from the configuration: its chip, its bootloader offset and its communication interface.

| Family | Kconfig architecture | Methods WebFlash offers |
|---|---|---|
| **STM32** | `MACH_STM32`, every chip the project lists under it (Kalico's AT32F403 and the N32G45x among them) | **Katapult** when there is a bootloader offset; **DFU** when the chip's ROM has a USB DFU bootloader (below); **Download** |
| **RP2040, RP2350** | `MACH_RPXXXX` (`MACH_RP2040` in Klipper before v0.13.0) | **Katapult** with a 16 KiB bootloader offset; **PICOBOOT** and the **UF2 drive**, both through the chip's BOOTSEL ROM; **Download** |
| **LPC176x** | `MACH_LPC176X` (LPC1768, LPC1769) | **Download** (the board's SD card bootloader loads `firmware.bin`); **Katapult** when it is installed in the first 16 KiB |
| **SAM, SAMD** | `MACH_ATSAM` (SAM3, SAM4, SAME70), `MACH_ATSAMD` (SAMC21, SAMD21, SAMD51, SAME5x) | **Download** |
| **HC32F460** | `MACH_HC32F460` | **Download** |

**Download** is always there, last: the firmware files to flash with any other tool (an SD card, ST-LINK, picotool, OpenOCD, bossac). A board TOML's `[flash] methods`, or a setup's own `methods`, narrows and orders the list; see the [board TOML reference](board-toml.md).

### Katapult

Katapult is offered for a configuration that leaves room for a bootloader (an application address after the flash start), over the firmware's own interface:

| Firmware interface | Method | How it is reached |
|---|---|---|
| USB | **Katapult (USB or UART)** | Web Serial, on Katapult's USB port (`1d50:6177`). |
| Serial (UART) | **Katapult (USB or UART)** | Web Serial, through a USB-UART adapter, at the firmware's `CONFIG_SERIAL_BAUD` (250000 unless the configuration says otherwise). Untested on a board so far. |
| CAN | **Katapult over CAN** | WebUSB, through a candleLight (gs_usb) adapter or a Klipper board in USB to CAN bridge mode. |
| USB to CAN bridge | **Katapult (USB or UART)** | The bridge board runs Katapult on its own USB port. |

The CAN adapters WebFlash knows: candleLight and other gs_usb firmware (`1d50:606f`, `1209:2323`), CES CANext FD, ABE CANdebugger FD and Xylanta SAINT3. On Linux the kernel's `gs_usb` driver must let go of the adapter first; [Flashing methods](../flashing.md) has the steps for each OS.

### DFU

An STM32 is flashed with **DFU (STM32 ROM)** when its ROM has a USB DFU bootloader: the STM32F042, F072, the F4 and F7 series, the G0 series except the G070 and G071 (which have no USB), the G4, L4 and H7 series, and Kalico's AT32F403. That holds whatever interface the firmware uses: a CAN or UART toolhead with a USB port is flashed through its ROM like any board. Chips such as the STM32F103 have no DFU in their ROM, and get Katapult or Download instead.

### Katapult itself

A Katapult build (the bootloader, configured alone) is written with the chip's ROM method: **DFU** on an STM32 whose ROM has it, **PICOBOOT** or the **UF2 drive** on an RP2040 or RP2350, else **Download** for another tool.

### Katapult and a firmware together

Configured together, Katapult and Klipper or Kalico are one firmware with two parts. The ROM methods both allow write both in one session (DFU and PICOBOOT write each part; the UF2 drive gets one `.uf2` holding both). Katapult's own methods then write the firmware alone, for a board that has Katapult already. An LPC176x pair has no ROM method, so its Download steps say how to put Katapult on the board first.

## What is refused

The projects also offer architectures that are not Arm. WebFlash configures them but refuses to build them, with one sentence:

> Atmega AVR firmware cannot be built in WebFlash: it builds for Arm chips only (STM32, RP2040/RP2350, LPC176x, SAM/SAMD, HC32F460)

and the same for Beaglebone PRU, Allwinner AR100, Linux process and Host simulator. [How it builds](../how-it-builds.md#arm-only) says why.

## Tested on real boards

Every method was first run against scripted devices, then on these boards, on Windows 10 (the results as of November 2026):

| Board | Methods | Browsers | Result |
|---|---|---|---|
| STM32G0B1 board on USB, with Katapult | Katapult over USB: firmware built on the site and in a card, Kalico built from a host's own version pasted from Mainsail, a cable pulled mid-write and the flash done again | Brave 1.98, Chrome 156 | Pass |
| The same board in its ROM bootloader | DFU: Klipper, Katapult from a `[prebuilt]` card, and Katapult and Klipper together in one session | Brave 1.98, Chrome 156 | Pass |
| STM32F072 board as a USB to CAN bridge | DFU | Chrome 156 | Pass |
| STM32G0B1 CAN toolhead with Katapult (PB0/PB1, 1 Mbit/s) | Katapult over CAN through a CANable (candleLight), from the site and from a card; through the STM32F072 bridge; its own USB port with DFU for a Katapult build | Chrome 156 | Pass |
| RP2040 board (KUSBA, IS25LP flash chip) | PICOBOOT and the UF2 drive, Klipper alone and Katapult and Klipper together | Brave 1.98 (PICOBOOT), Chrome 156 | Pass |
| No board | Configure, build and download | Edge 156, Firefox 159 | Pass |

Not run on a board yet: Katapult in UART mode, a CAN node reached by its typed `canbus_uuid`, an RP2350, and any flashing of LPC176x, SAM, SAMD and HC32F460 builds (their builds pass the parity checks; they are download-only). Every hardware run so far was on Windows: the Linux and macOS steps (udev rules, the `dialout` group, unbinding `gs_usb`) come from those systems' documentation, not from a run.

!!! note "An RP2040 board with an IS25LP flash chip"
    Klipper's default RP2040 build carries the stage-2 bootloader for the W25Q080 flash. A board with an IS25LP chip, such as a KUSBA, boots Klipper only with **Enable extra low-level configuration options** and **Flash chip: GENERIC_03H with CLKDIV 4**. WebFlash cannot tell from the board; the build flashes and verifies either way.

## Browsers

Flashing needs WebUSB (DFU, PICOBOOT, Katapult over CAN), Web Serial (Katapult over USB or UART) or the File System Access API (the UF2 drive), and all three need a page served over HTTPS or from `localhost`. Configuring, building and downloading need none of them.

| Browser | Configure, build, download | WebUSB | Web Serial | UF2 drive |
|---|---|---|---|---|
| Chrome or Edge on a computer | Yes | Yes | Yes | Yes |
| Brave | Yes | Yes | Yes | Off by default |
| Firefox | Yes | No | No | No |
| Safari | Never tried; expected as Firefox | No | No | No |
| Chrome on Android | Expected | Yes | No | No |

- **Chrome and Edge** on Windows, macOS and Linux run everything. Boards have been flashed with Chrome and Brave; Edge has built and downloaded, and has the same APIs as Chrome.
- **Brave** ships with the File System Access API off, so the UF2 drive becomes a `.uf2` download unless `brave://flags/#file-system-access-api` is on. It also hands pages made-up USB serial numbers, so the `printer.cfg` hint after a flash says `<serial>` there.
- **Firefox** configures, builds and offers the files; the Flash step says why it offers nothing else. Flash the files with Chrome or Edge, or your usual tools.
- **Safari** has never been opened on the site. It has no WebUSB, Web Serial or folder picker, so it should behave as Firefox does.
- **Android**: Chrome there has WebUSB, so DFU and PICOBOOT are offered, through a USB OTG adapter; it has no Web Serial, so no Katapult over USB or UART, and no folder picker, so the UF2 drive is a download. Never tried on a phone.
- **In a frame from another origin** (a card embedded from another site), the browser refuses WebUSB and Web Serial unless the iframe has `allow="usb; serial"`, and never opens a folder picker, so the UF2 drive is a `.uf2` download there. The card says what it withholds and links to the card in a tab of its own. See [Embedding a card](../embedding.md).

On Windows, PICOBOOT on an RP2040 needs the WinUSB driver once (Zadig: "RP2 Boot (Interface 1)"); the STM32's DFU bootloader needed no driver on the boards tried so far (if the browser cannot open it, Zadig: "DFU in FS Mode" or "STM32 BOOTLOADER"); Katapult over USB and candleLight adapters need nothing. [Flashing methods](../flashing.md) has the steps for each OS.

## Not supported in v1

- AVR boards and STK500 flashing.
- SAM-BA (bossac) flashing.
- The STM32 HID bootloader and the STM32 UART ROM bootloader (stm32flash).
- Writing to SD cards: an SD card bootloader gets the files to copy yourself.
- AR100, PRU, Linux process and simulator builds.
- `printer.cfg` generation beyond the serial or `canbus_uuid` hint after a flash.
- A board catalog on the site: a board TOML is the preset, and a card is how a board's maker shares one.
- Flashing from Firefox or Safari.
- Web Serial on Android.
- Flashing through the Linux kernel's `gs_usb` driver without unbinding the adapter.
- Translations: the site and the cards are in English.
