---
description: "WebFlash problems by symptom: devices missing from the picker, drivers and permissions, Katapult and CAN nodes that do not answer, flashes that break off, failed builds, blocked downloads, embedded cards and browsers."
---
# Troubleshooting

When a flash fails, the Flash step shows a title and a sentence, and opens **Trouble connecting?** with the fixes for your operating system and browser. The titles below are the ones the step shows, in quotes; each section says what they mean and what to do. The [Log](site/flash.md#progress) at the bottom of the card has every step; copy it when you ask for help.

## Flashing

### The method says "(not here)"

The browser lacks what the method needs, and picking the method says which: WebUSB for DFU, PICOBOOT and Katapult over CAN, Web Serial for Katapult over USB or UART, the File System Access API for the UF2 drive. A step that needs an API the browser lacks, such as **Restart Klipper into Katapult** without Web Serial, fails with "This browser cannot flash". Use Chrome or Edge on a computer, over HTTPS or from `localhost`, or download the files and flash them with your usual tools. See [Firefox and Safari](#firefox-and-safari), [Brave](#brave) and [Android](#android).

### "No device picked"

The browser's device picker was closed without a choice, or it listed nothing. The picker lists only devices the method can use, so a board that is not in the right mode is not in it.

- Put the board in its bootloader again: BOOT0 and RESET for DFU, BOOTSEL for PICOBOOT and the UF2 drive, a double-tap of RESET (or **Restart Klipper into Katapult**) for Katapult. See [Getting into the bootloader](flashing.md#getting-into-the-bootloader).
- Plug it straight into this computer, not through a hub, with a cable that carries data (a charge-only cable has no data lines).
- For Katapult over UART, the adapter's port is listed whatever the board does; pick it under **Connect**.

### "The browser could not claim the device"

The browser sees the device but cannot open it: a driver is missing, or another program holds it.

- **Windows**: the device has no WinUSB driver. PICOBOOT on an RP2040 always needs it once; the STM32's DFU bootloader usually does not. In Zadig, tick **Options > List All Devices**, pick "DFU in FS Mode" or "STM32 BOOTLOADER" (DFU) or "RP2 Boot (Interface 1)" (PICOBOOT), choose WinUSB and click **Replace Driver**, then replug the board. With STM32CubeProgrammer installed, replace its STTub30 driver with WinUSB the same way. See [Windows](flashing.md#windows).
- **Linux**: add the udev rule for the device and quit `dfu-util` or STM32CubeProgrammer; for a CAN adapter, unbind `gs_usb` first (see [The CAN adapter is busy on Linux](#the-can-adapter-is-busy-on-linux)).
- **macOS** needs no driver: quit the program holding the device (`picotool`, `dfu-util`, STM32CubeProgrammer, Klipper).
- Close the other programs using the board (Klipper, a serial monitor, STM32CubeProgrammer, `dfu-util`, `picotool`), then click **Connect** again.

On Windows, a device without WinUSB can also sit in the connect step: the step gives up after 10 seconds with "The browser did not finish … within 10 s. The device is listed but cannot be used, which on Windows means its interface has no WinUSB driver.", and the same Zadig steps.

### "The device is in use"

Another program, or another tab of this site, has the port or the device open. Close other programs using the board (Klipper, a serial monitor, STM32CubeProgrammer, `dfu-util`, `picotool`) and other tabs of the site, then click **Connect** again. For a serial port the title can read "The port could not be opened". On Linux, the cause may also be the `dialout` group:

```bash
sudo usermod -a -G dialout $USER
```

Log out and back in after it, and stop ModemManager if it holds the port.

### "The browser may not use this device"

The browser refuses the device for this page:

- The page is not on HTTPS or `localhost`. WebUSB, Web Serial and the folder picker exist only there.
- The page is a card embedded in another site without permission to use USB and serial ports: see [A card in another site cannot flash](#a-card-in-another-site-cannot-flash).
- On Linux, the operating system refuses it: add the [udev rule](flashing.md#linux) for USB devices, or join the `dialout` group for serial ports.
- For the UF2 drive: pick the drive's top folder (`RPI-RP2` or `RP2350`) and allow editing, or download the `.uf2` and copy it onto the drive yourself.

### The CAN adapter is busy on Linux

The kernel's `gs_usb` driver owns a candleLight adapter or a Klipper USB to CAN bridge as `can0`, and the browser cannot claim it until you release it:

1. Stop a Klipper host that uses the same adapter.
2. `sudo ip link set can0 down`
3. `echo <name> | sudo tee /sys/bus/usb/drivers/gs_usb/unbind`, with `<name>` the adapter's entry in `/sys/bus/usb/drivers/gs_usb/`, like `1-3:1.0`.
4. Click **Connect** again. Replug the adapter after flashing, so the kernel takes it back.

The udev rule for `1d50:606f` may be needed too; see [Linux](flashing.md#linux).

### "The board did not answer"

The board was connected but did not answer in time: Katapult did not reply to its first command, a CAN node was silent, or a USB request timed out.

- Reset the board into its bootloader and click **Connect** again.
- Still timing out? Try another USB cable or port (a charge-only cable has no data lines).
- **Katapult over UART**: Katapult must use the same baud rate as the firmware. The adapter is opened at the firmware's `CONFIG_SERIAL_BAUD`, else 250000; a Katapult built for another rate does not answer. Build both with the same "Serial baud rate" under the low-level options. Katapult over UART has not been run on a board yet; see [Katapult over UART](flashing.md#katapult-over-uart).

### No node answered on the bus

Katapult over CAN asked the bus who is there and nobody answered. The list says "No node answered on the bus.", and when you go on without a node the step fails with "The board did not answer" and "No node answered on the bus: check the bus speed, the wiring, the termination and the power, or stop Klipper on the host."

- **The bus speed.** The adapter runs at the firmware's CAN bus speed (1 Mbit/s unless the configuration says otherwise), and every node must use the same one.
- **The wiring.** CAN high to CAN high, low to low, a 120 ohm terminator at each end of the bus, and the node powered.
- **A node a running Klipper host holds** does not answer the query. Open **Node not listed? Enter its canbus_uuid**, type its `canbus_uuid` from `printer.cfg` and click **Use this UUID**: WebFlash sends the bootloader request to that UUID. Or stop Klipper on the host (`sudo systemctl stop klipper`) and flash again. A typed UUID is refused unless it has 12 hex digits ("A canbus_uuid is 12 hex digits, like aabbccddeeff.").

See [Katapult over CAN](flashing.md#katapult-over-can).

### "The board did not restart into its bootloader"

WebFlash asked the board to restart into Katapult (over CAN, or from Klipper) and it did not come back as Katapult: "The node … did not come back as Katapult." The node may have no Katapult, or a host may be talking to it.

- Put the board in its bootloader by hand: hold BOOT0 or BOOTSEL and tap RESET, or double-tap RESET for Katapult.
- Click **Connect** and pick it.
- A node without Katapult is flashed over USB (DFU) or SWD first.

After **Restart Klipper into Katapult** or **Restart Klipper into the bootloader**, the step waits 10 seconds for the new device and then asks you to pick it: the browser finds it by itself only when the site was allowed to use it before. A Klipper behind Katapult restarts into Katapult, not into the ROM, so **Restart Klipper into the bootloader** under DFU or PICOBOOT does not reach the ROM there: use BOOT0 or BOOTSEL.

### "The device went away"

The board disappeared in the middle of a step.

- **Just flashed?** Then the restart is expected: check that the board shows up as Klipper (or Katapult).
- Otherwise, put it back in its bootloader and connect again.
- **Keeps dropping?** Try another cable or USB port.

**The UF2 drive.** The BOOTSEL ROM restarts the board as soon as it has every block, and the drive vanishes with it. That counts as success only when it happens on the last part of the file: a drive that goes away earlier fails with "The drive went away after … of …, before the board had the whole file". Hold BOOTSEL while plugging the board back in, pick its drive again and flash again.

### The board is still in Katapult

A Katapult write that broke off on a block ends with "… The board is still in Katapult: connect again and click Flash." Katapult never writes over itself, and WebFlash only tells it to start the firmware once the whole image was written, so the board waits in Katapult. Click **Connect**, pick the Katapult port (or the CAN node) and **Flash** again; no double-tap is needed.

### "The bootloader stayed busy"

A DFU bootloader that stays busy for over 30 seconds fails the flash with a timeout ("The bootloader stayed busy (…) for over 30 s during the …"). Unplug the board, put it back in its bootloader and click **Connect**, then flash again.

### "The chip is read-protected"

The STM32's read-out protection (RDP) is on, so the ROM refuses the read-back and the flash.

1. In STM32CubeProgrammer (over USB to the ROM bootloader, or with an ST-LINK), set RDP to level 0 (AA) under **Option bytes**. This erases the whole chip, Katapult included.
2. Put the board back in its ROM bootloader (hold BOOT0, tap RESET) and flash again.

### "The verification failed"

The read-back differs from what was written, and the message names the address. Flash again. If it fails again, the flash may be worn or write-protected: download the file and use the vendor's flashing tool.

### "Firmware for another micro-controller"

Katapult reports another micro-controller than the firmware was built for ("Katapult MCU: … Firmware MCU: …"), and WebFlash writes nothing. Build the firmware for the micro-controller the board reports, or connect the board this firmware was built for.

### "Firmware for another chip"

An RP2040 firmware on an RP2350 or the other way round, or a `.uf2` for another chip family. Build or pick a firmware for the chip that is connected (RP2040 and RP2350 files differ); an RP2040's drive is `RPI-RP2`, an RP2350's is `RP2350`. A UF2 for another family altogether (a SAMD51's, say) can only be downloaded.

### "The firmware does not fit"

The image does not belong where it would be written:

- **Katapult's application address**: "The firmware starts at 0x08000000 but Katapult's application start is 0x08002000." The file was built without a bootloader offset: build it for Katapult's offset, or flash it with DFU or PICOBOOT instead. A file that starts higher needs the offset Katapult was built for.
- **Outside the flash**: the file is for another chip or is not meant for the flash; build it for the board.
- **Katapult and Klipper together**: "Katapult (…) runs past 0x08002000, where Klipper starts: pick a larger application offset in Katapult."

### "Not in its bootloader"

The device in the picker is not the bootloader the method talks to, for example a board running its application, or a device with no DFU or PICOBOOT interface: "The device has no DFU interface: it is not in its ROM bootloader (hold BOOT0 and tap RESET), or it is a different device." Put it in its bootloader and connect again. For Katapult over CAN the message says the device is not a gs_usb CAN adapter.

### "Not a BOOTSEL drive"

The folder picked for the UF2 drive has no `INFO_UF2.TXT`, or names a board WebFlash does not know. Hold BOOTSEL while plugging the board in and pick the drive named `RPI-RP2` (or `RP2350`), its top folder. The same title also covers a drive the `.uf2` could not be written to.

### "Unexpected answer from the board"

The bootloader answered with something the protocol does not expect (a bad frame, a refused request). Reset the board into its bootloader and try again; copy the **Log** if it happens again.

### The board flashed but does not boot

- **An RP2040 board with an IS25LP flash chip**, such as a KUSBA: Klipper's default stage-2 bootloader is for the W25Q080 chip. Under the low-level options, set "Flash chip" to "GENERIC_03H with CLKDIV 4" (with Katapult, it is under "Katapult only" in Configure, since a Klipper behind Katapult has no stage-2 bootloader of its own). See [Configure](site/configure.md).
- **A firmware at the wrong offset**: a Klipper built for a bootloader offset needs that bootloader in front of it, and a Klipper without one overwrites it. Check the bootloader offset in Configure against what is on the board.
- **The wrong crystal or USB pins**: the board starts but does not enumerate. Check the clock reference and the communication interface in Configure.
- **An RP2350 board**: no RP2350 has been flashed with WebFlash yet; report what happens.

### The printer.cfg hint says `<serial>`

The page cannot know the serial number in Klipper's USB port name: Web Serial gives none, and the serials of the ST ROM and the RP2040's BOOTSEL ROM are not the chip id Klipper reports. Once Klipper runs, find the port on the host with `ls /dev/serial/by-id/`. For a CAN node or a bridge with no UUID from the bus, the hint names `canbus_query.py`.

## Uploaded files

### "The file could not be used"

**Upload firmware** reads the format from the file's content, and refuses what is not a firmware image:

- A text file, such as `klipper.dict`: "… is a text file, not a firmware image (a Klipper dictionary, or an Intel HEX file whose first record cannot be read): upload a .bin, .hex, .uf2 or .elf file."
- A damaged `.hex` (a bad checksum, a line cut short, no end-of-file record), a `.uf2` that is not whole 512-byte blocks, or an `.elf` that is not a 32-bit little-endian executable: the message names the file and what is wrong. Build or download the file again.

A `.bin` asks for its address: type it in hex, with or without `0x`. See [Upload firmware](site/flash.md#upload-firmware).

### The methods do not match my configuration

An uploaded Klipper file carries its own dictionary (the micro-controller, the interface's pins, the CAN bitrate), and that decides its methods rather than the configuration in Configure: a CAN build gets Katapult over CAN even while Configure holds a USB configuration. The reason line says so. A file built for another chip than the configuration's takes its own methods too.

## Building

### "Build failed"

The Build step shows the command that failed and its output. Some causes:

- **Not an Arm chip.** WebFlash builds for Arm only: "Atmega AVR firmware cannot be built in WebFlash: it builds for Arm chips only (STM32, RP2040/RP2350, LPC176x, SAM/SAMD, HC32F460)". The same goes for the Beaglebone PRU, Allwinner AR100, Linux process and Host simulator. Klipper's Kconfig defaults to AVR, so a defconfig that names no architecture lands there; pick the chip under the micro-controller architecture in Configure.
- **An unchecked version.** A version badged **unchecked** "failed the snapshot check" or is "not checked" yet: the snapshot did not build with the reference toolchain, or has not been tried. It may still build in the browser (Klipper v0.12.0 and v0.11.0 do); if it does not, pick a checked version. See [Firmware and versions](site/firmware.md).
- **The configuration.** An option the version's Kconfig accepts can still fail to build for the chip: copy the log and compare with `make` on a Klipper checkout.

See [Build](site/build.md).

### The build stops: "It may have run out of memory"

A compiler worker died, most likely out of memory: "… It may have run out of memory: set fewer compiler workers under Versions and licenses." Each worker holds its own compiler and a copy of the sources. Open **Versions and licenses** (on page 1, or in About), set **Compiler workers** lower, and build again.

## Downloads and the site

### Python does not start: cdn.jsdelivr.net

The site runs its Python engine on Pyodide, which it downloads from `cdn.jsdelivr.net`. If that host is blocked by a network policy, an extension or an offline machine, Python's row in the status chip reads "Python: failed", with the message "Could not download the Python runtime from cdn.jsdelivr.net. Check your network or allowlist that host, or use the webflash command line tool." Allow the host, then click Python's row in the status chip to try again; the next step that needs Python (**Next** on page 1, a Build) tries again too. See [Firmware and versions](site/firmware.md).

A card on a docs page also loads its engine from the WebFlash site; when that site cannot be reached it says "Could not reach the WebFlash site (…). Try again in a moment."

### A download breaks off

The sources and the compiler are downloaded once and kept in the browser's cache. A download that breaks off says which file and how far it got: "Could not download … : the connection broke off after … of … bytes. Check your connection and try again; what did arrive is not kept." Nothing broken is kept, so the next try starts the file again. A file that arrives but does not match its checksum is dropped and fetched again.

## Cards and browsers

### A card in another site cannot flash

A card served from another origin than the docs page (another domain or port) needs permission to use USB and serial ports. Without it, the card says "The page this card is embedded in does not let it use USB or serial ports, so it cannot flash from here", still builds, and offers the files and a link to open the card in a tab of its own. Add `allow="usb; serial"` to the embed:

```markdown
![Flash Klipper to the board](https://firmware.example.org/board.webflash.html){ type=iframe allow="usb; serial" }
```

A frame that allows only one of the two keeps the methods on that one, and its notice says what it withholds. Even with `allow`, browsers open no folder picker in a frame from another site, so the UF2 drive becomes a `.uf2` download there. A page beside the Markdown, on the docs site's own origin, needs nothing. See [Embedding a card](embedding.md).

### Firefox and Safari

Firefox and Safari have no WebUSB and no Web Serial, so they cannot flash. They configure and build, and the Flash step offers the files to download; every method shows **(not here)** with the reason. Flash the files with Chrome or Edge, or with `dfu-util`, `picotool` or Katapult's `flashtool.py`. The site has been tried in Firefox; Safari has not been opened with it yet.

### Brave

Brave has WebUSB and Web Serial, so every method works but the UF2 drive: Brave ships with the File System Access API off. Turn on `brave://flags/#file-system-access-api` and restart Brave, use Chrome or Edge, or download the `.uf2` and copy it onto the drive yourself.

Brave also hands pages made-up USB serial numbers (letters and digits rather than the device's hex serial), most likely as fingerprinting protection, so the device names in the picker and the log show them. The printer.cfg hint does not use them.

### Android

Chrome on Android has WebUSB but no Web Serial and no folder picker: the Flash step offers DFU and PICOBOOT there, with the board on a USB OTG adapter, and accepts the browser's USB permission prompt. Katapult over USB or UART needs a computer. No board has been flashed from Android so far.
