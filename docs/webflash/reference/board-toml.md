---
description: "Every table and key of a WebFlash board TOML: the board, the firmware and its versions, Katapult, setups, the options a reader may change, flashing and prebuilt files, with every rule, error and warning."
---
# Board TOML reference

A board TOML describes one board: what to build for it (or a ready-made file to flash), which settings the reader of its card may change, and how it is flashed. The site's [Embed step](../site/embed.md) writes this file with **Save TOML**, and `webflash board.toml` renders it into the [generated page](page.md). You can also write or edit it by hand.

A board TOML takes one of two shapes:

- **Built from source:** `[board]`, `[firmware]`, and either one `[config]` table or a `[[setup]]` table for each way to set up the board. `[katapult]`, `[[option]]` and `[flash]` are optional.
- **A file to flash:** `[board]` and `[prebuilt]`, optionally with `[flash]`.

A minimal board built from source:

```toml
[board]
title = "STM32G0B1 over USB"

[firmware]
project = "klipper"

[config]
defconfig = """
CONFIG_MACH_STM32=y
CONFIG_MACH_STM32G0B1=y
"""
```

The defconfig is what `make savedefconfig` writes for the board: everything it leaves out holds its default. This one builds the latest Klipper for an STM32G0B1 with an 8 KiB bootloader, an 8 MHz crystal and USB on PA11/PA12, the defaults for that chip on Klipper `master`.

The loader is strict, since a typo here builds the wrong firmware: an unknown key or table, a wrong type or a value outside its list is an error rather than a setting that is quietly ignored. See [errors](#errors).

## `[board]`

What the card shows, and where its parts come from. Required in both shapes.

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `title` | string | required | The card's heading, the page's `<title>` (the browser tab) and the photo's alt text. Must not be empty. Plain text. |
| `description` | string | `""` | Text under the title, in the [text markup](#text-markup). A multi-line string (`"""`) keeps its paragraphs. |
| `image` | string | `""` | The board's photo: a URL, or a path relative to the TOML. See [`image`](#image). |
| `theme` | string | `"default"` | The [theme](themes.md) to apply: colors, fonts and the card's behaviors. Must not be empty; leave it out for the default theme. `webflash -t` overrides it. |
| `theme_dir` | string | `"./themes"` | Folder holding theme `.toml` files, relative to the TOML. Names not found there fall back to the themes bundled with WebFlash. |
| `engine_url` | string | `"https://webflash.isiks.tech/engine/v1/"` | Where the page loads the embed runtime from. Must be an `http://` or `https://` URL; a missing trailing `/` is added. The card's **Open in WebFlash** link goes to the site this URL belongs to: the URL with its `engine/v1/` folder taken off. |

You only change `engine_url` to run cards against your own copy of WebFlash, such as `http://127.0.0.1:8000/engine/v1/` while `webflash --port 8000` runs. See the [command line](../command-line.md).

### Text markup

`description`, an option's `help` and the texts in [`[flash.instructions]`](#flashinstructions) take a small markup, the same as 3DStep's:

| Write | Get |
|-------|-----|
| A blank line | A new paragraph |
| A single line break | A line break |
| `**bold**` | **bold** |
| `` `code` `` | `code`, in the theme's monospace font |
| `[label](https://example.org)` | A link that opens in a new tab. Only `http`, `https` and relative URLs: any other scheme (`javascript:`, `data:`) shows the label alone. |

Everything else is text: HTML in the TOML is shown as written, never run. A setup's `title` and `description`, an option's `label` and `labels`, and `[board] title` are plain text.

```toml
[board]
title = "CAN toolhead (STM32G0B1)"
description = """
Klipper firmware for an STM32G0B1 toolhead board.

Set the CAN bus speed to the one your bus runs at: `canbus_frequency` in the bridge's configuration. See the [Klipper CAN bus guide](https://www.klipper3d.org/CANBUS.html)."""
```

### `image`

The photo is shown beside the title on the card's first step and in the [static fallback](page.md). It is either:

- **A URL:** anything with a scheme of two letters or more (`https://...`, `data:image/webp;base64,...`) or a protocol-relative `//host/...` name. The page loads it as written.
- **A path relative to the TOML:** `board.webp` or `images/board.webp`. A path with `..`, a drive (`C:`) or a leading `/` is an error, since `webflash -i` and the site read only files beside the TOML or below its folder.

The page references the photo by its path, so keep it next to the generated HTML (CI does when it renders in place). `webflash -i` embeds it in the page instead, as a data URL; an image that is a URL stays as it is, with the warning `image is a URL, so -i leaves it as it is`. The site's Generate can embed it too, once the photo was opened with the TOML or attached in the dialog.

## `[firmware]`

The project to build and the versions the reader may pick. Required for a board built from source.

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `project` | string | required | `"klipper"`, `"kalico"` or `"katapult"`: what the card starts with. `"katapult"` builds the Katapult bootloader alone. |
| `projects` | list of strings | `[project]` | The projects the reader may switch between, such as `["klipper", "kalico"]`. Must include `project`, must not list one twice, and cannot mix `katapult` with Klipper or Kalico: the bootloader's configuration is not the firmware's. |
| `version` | string | `"latest"` | The version the card starts with. See [versions](#versions). |
| `versions` | string or list of strings | `"all"` | What the reader may pick from: `"all"`, `"releases"`, or a list of versions. A list must include `version`, unless `version` is `"latest"` or `"release"`. |

With two or more projects, the card's first step shows a switch (**Klipper**, **Kalico**, and **None** when the TOML has [`[katapult]`](#katapult)); with one, it shows the project's name. A project switch keeps the defconfig, so one defconfig serves Klipper and Kalico.

### Versions

`version` (here and in `[katapult]`) is one of:

| Value | Means |
|-------|-------|
| `"latest"` | The project's default branch (`master` for Klipper and Katapult, `main` for Kalico), as the newest snapshot that passed the snapshot check. When the default branch's newest snapshot did not pass, the newest version that did, with a note saying so. |
| `"release"` | The newest release tag that passed the snapshot check. |
| A ref id | A tag or branch the site offers, such as `"v0.13.0"`, `"master"` or Kalico's `"bleeding-edge-v2"`. The card builds that version, even one marked unchecked. |
| An older commit | A commit of the default branch, named by its `git describe` string as Mainsail and Fluidd show it, such as `"v0.13.0-245-g61c0c8d"`. The site keeps a snapshot of every commit from the last year (the last two years for Katapult). |

`versions` limits what the card offers:

| Value | The reader may pick |
|-------|---------------------|
| `"all"` | Any version the site offers: Latest, the releases, the branches and the older commits. |
| `"releases"` | **Newest release** and the release tags. |
| A list | Only those, such as `["v0.13.0", "v0.12.0"]`. A list of one version shows it as text, with no picker. |

`versions` applies to the card only: the site offers every version, and keeps a pinned `version` in the list when you save. The theme's [`show_versions = false`](themes.md#behavior) hides the pickers whatever `versions` says.

```toml
[firmware]
project = "klipper"
projects = ["klipper", "kalico"]
version = "release"
versions = "releases"
```

## `[katapult]`

Offers the Katapult bootloader beside the firmware, built and flashed together with it. Optional.

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `version` | string | `"latest"` | The Katapult version the card starts with. See [versions](#versions). |
| `versions` | string or list of strings | `"all"` | What the reader may pick from, as in `[firmware]`. |
| `default` | bool | `true` | Whether the card's **Katapult** checkbox is ticked when it opens. Set `false` for a board most readers have Katapult on already. |

Rules:

- `[firmware] project` must be `"klipper"` or `"kalico"`. To build Katapult alone, write `project = "katapult"` and leave `[katapult]` out.
- At least one setup must have a `katapult` key: Katapult's own defconfig, in [`[config]`](#config) or a [`[[setup]]`](#setup).
- A `katapult` key in `[config]` or a `[[setup]]` without a `[katapult]` table is an error.

On the card, `[katapult]` adds the **Katapult** checkbox with its own version picker, and **None** to the firmware switch, which builds Katapult alone from each setup's `katapult` defconfig. While Katapult is ticked, a setup without a `katapult` defconfig cannot be picked ("No Katapult in this setup: untick Katapult to use it."), and an option that sets Klipper's bootloader offset is disabled with "Set by Katapult.", since WebFlash sets that offset from Katapult's application offset. The site keeps Katapult ticked when it opens a TOML with `[katapult]`, whatever `default` says: `default` is the card's checkbox.

```toml
[katapult]
version = "latest"
default = false
```

## `[config]`

The defconfig to build, for a board with one way to set it up.

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `defconfig` | string | required | The firmware's defconfig, as `make savedefconfig` writes it. See [defconfigs](#defconfigs). |
| `katapult` | string | none | Katapult's defconfig, built beside the firmware. Needs [`[katapult]`](#katapult). |

A `[config]` table is one setup with the id `default`, which [`[[option]] setups`](#option) can name.

```toml
[config]
defconfig = """
CONFIG_MACH_STM32=y
CONFIG_MACH_STM32G0B1=y
"""
katapult = """
CONFIG_MACH_STM32=y
CONFIG_MACH_STM32G0B1=y
"""
```

## `[[setup]]`

One table for each way to set up the board, such as on a CAN bus with Katapult or on USB with no bootloader. A card with two or more setups adds a Setup step, "How is the board connected?", with one card per setup.

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `id` | string | required | A short name: lowercase letters, digits and `-` (`"can"`, `"usb-katapult"`). Unique among the setups. [`[[option]] setups`](#option) refers to it. |
| `title` | string | required | What the reader picks the setup by. Must not be empty. Plain text. |
| `description` | string | `""` | A line under the title on the Setup step. Plain text. |
| `defconfig` | string | required | The firmware's defconfig for this setup. See [defconfigs](#defconfigs). |
| `katapult` | string | none | Katapult's defconfig for this setup. Needs [`[katapult]`](#katapult); a setup without one cannot be picked while Katapult is ticked. |
| `methods` | list of strings | `[flash] methods` | The flashing methods for this setup, as [`[flash] methods`](#flash). |

The setups are listed in the order they are written, and the card starts on the first one that fits its Katapult checkbox: with Katapult ticked when the card opens, the first setup that has a `katapult` defconfig. The static fallback's "Build the firmware" link names the first setup's title and opens it in the site.

### `[config]` or `[[setup]]`

Write one `[config]` table or one or more `[[setup]]` tables, never both. `[config]` is the short form of a single setup with no title; `[[setup]]` is needed as soon as there are two setups, or one with a title, a description or its own methods. The site's [setups editor](../site/embed.md) switches from one form to the other by itself.

## Defconfigs

A `defconfig` or `katapult` value is the text of a `.config` file, and WebFlash reads it as Kconfig does (with kconfiglib, which Klipper, Kalico and Katapult use). Paste what `make savedefconfig` writes after `make menuconfig`, or copy it from the site's `.config` tab: a defconfig names only what differs from the defaults, so it carries over between versions better than a full `.config`.

Each line is one of:

- `CONFIG_NAME=value`, where the value is `y`, `n`, `m`, a decimal number, a hex number (`0x8000`) or a quoted string (`"PA13"`, with `\"` and `\\` escapes).
- `# CONFIG_NAME is not set`, written exactly so, with one space after the `#`.
- A blank line or any other comment, which is skipped.

The loader refuses what Kconfig would misread without a word:

- **A line that starts with a space or tab.** Kconfig reads only lines that start at column 0, so an indented setting would be ignored. Keep the defconfig's lines at the start of the line inside the `"""` string.
- **An unset line written another way** (`#CONFIG_X is not set`, two spaces): Kconfig takes it for a comment.
- **A symbol set twice.** Kconfig would take the last one.
- **A decimal number with a leading zero** (`CONFIG_SERIAL_BAUD=0250000`): it would reach the C code as an octal number.

Symbols are not checked against a Kconfig here: see [what the loader does not check](#what-the-loader-does-not-check).

## `[[option]]`

A setting the reader of the card may change. Everything else stays as the defconfig sets it. Options are shown on the card's first step for a board with one setup, and under each setup on the Setup step for a board with several.

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `symbol` | string | required | The Kconfig symbol, without `CONFIG_` (`"CANBUS_FREQUENCY"`, `"STM32_FLASH_START_2000"`). Unique among the options. |
| `label` | string | the Kconfig prompt | The option's name on the card. Without it, the card shows the symbol until the configuration loads, then the Kconfig prompt. |
| `values` | list of strings or integers | see below | The values the reader may pick from. Integers are kept as strings, so `1000000` and `"1000000"` are the same. No value may be listed twice. |
| `labels` | table | `{}` | Text for each value in the list, such as `{ 1000000 = "1 Mbit/s" }`. A value without a label shows as itself. |
| `help` | string | the Kconfig help | Text under the option, in the [text markup](#text-markup). Without it, the card offers the Kconfig's own help, folded under **About this option**, once the configuration loads. |
| `setups` | list of strings | every setup | The ids of the setups the option applies to, such as `["can"]`. Each must be a setup's id (`"default"` for a `[config]` table). |

What the card shows depends on the symbol and on `values`:

| Symbol | With `values` | Without `values` |
|--------|---------------|------------------|
| A member of a Kconfig choice (one of the processor, interface or bootloader offset entries) | A list of the members in `values` that the configuration shows | A list of every member the configuration shows |
| A bool | A list of `values` (`y`, `n`) | A checkbox |
| An int, hex or string | A list of `values` | A text field, checked against the symbol's range |

Before the configuration has loaded, an option without `values` shows the defconfig's value (or "as the board's configuration sets it") with a **Change** button, since only the Kconfig knows what fits; **Change** starts the downloads. A list shows the defconfig's value, or **Default** where the defconfig leaves the symbol to its default. A value the configuration has that the list lacks joins the list, so the reader always sees what the board gets. A symbol the version does not have shows "not in this version", and one the other settings hide is disabled with "Not available with the settings above."

For a choice, `symbol` is one of its members, usually the one the defconfig picks, and `values` the members offered. The site's Embed options tab writes it so.

```toml
[[option]]
symbol = "STM32_FLASH_START_2000"
label = "Bootloader"
values = ["STM32_FLASH_START_2000", "STM32_FLASH_START_0000"]
labels = { STM32_FLASH_START_2000 = "Katapult (8 KiB)", STM32_FLASH_START_0000 = "No bootloader (flash with DFU)" }
help = "Katapult must already be on the board for the 8 KiB offset; otherwise pick No bootloader."

[[option]]
symbol = "CANBUS_FREQUENCY"
label = "CAN bus speed"
values = [1000000, 500000, 250000]
labels = { 1000000 = "1 Mbit/s", 500000 = "500 kbit/s", 250000 = "250 kbit/s" }
setups = ["can"]
```

An option that sets Klipper's bootloader offset (a `STM32_FLASH_START_*`, `RPXXXX_FLASH_START_*` or `LPC_FLASH_START_*` member) is disabled while Katapult is ticked, and left out when the reader picks **None** (Katapult alone), since Katapult's Kconfig gives those symbols another meaning.

## `[flash]`

How the board is flashed. Optional in both shapes.

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `methods` | list of strings | inferred | The methods to offer, in order; the first is the one the card picks. Without it, WebFlash infers them from the configuration (or from a prebuilt file). |

`methods` narrows and orders what the configuration allows: a method that does not fit it (DFU for an RP2040, say) is left out, with the card's warning `The board TOML's "dfu" does not fit this configuration, so it is left out.` When none is left, the card offers **Download the files**. A `[[setup]]` with its own `methods` uses those instead. [Flashing methods](../flashing.md) describes each one.

| Id | Shown as | For |
|----|----------|-----|
| `dfu` | DFU (STM32 ROM) | An STM32 whose ROM bootloader has USB DFU |
| `picoboot` | PICOBOOT (RP2 BOOTSEL) | An RP2040 or RP2350 in BOOTSEL mode, over USB |
| `uf2` | UF2 drive (RP2 BOOTSEL) | An RP2040 or RP2350 in BOOTSEL mode, through its drive |
| `katapult` | Katapult (USB or UART) | A board with Katapult on USB, or on a UART through a USB-UART adapter (UART has so far run only against WebFlash's test devices, not on a board) |
| `katapult-can` | Katapult over CAN | A board with Katapult on a CAN bus, through a USB to CAN adapter or bridge |
| `download` | Download the files | Saving the files, for any other tool |

### `[flash.instructions]`

Text for a method, shown in place of WebFlash's own steps when the reader picks it. Each key is a method id, each value a string in the [text markup](#text-markup).

```toml
[flash]
methods = ["katapult", "dfu", "download"]

[flash.instructions]
katapult = "If Klipper is running on the board, WebFlash asks it to restart into Katapult. Otherwise double-tap RESET, then click Connect."
dfu = "Hold BOOT, tap RESET, release BOOT, then click Connect. On Windows, if the browser lists the bootloader but cannot open it, install the WinUSB driver on it with Zadig."
```

Instructions for a method that neither `[flash] methods` nor any setup's `methods` offers are never shown, and the loader warns about them. While a setup infers its methods, any method may come up, so there is no warning.

## `[prebuilt]`

A ready-made firmware file to flash as it is, with nothing to configure or build. The card has two steps, Firmware and Flash, and loads no compiler and no Python.

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `file` | string | required | The file, as a path relative to the TOML (never a URL, `..`, a drive or a leading `/`): a `.bin`, `.hex`, `.uf2` or `.elf`. |
| `address` | integer | none | Where a `.bin` goes in flash, such as `0x08000000`. Required for a `.bin`, which carries no address of its own, and an error for the other formats, which do. Must fit in 32 bits. |
| `mcu` | string | `""` | The chip the file is for, such as `"stm32g0b1xx"` or `"rp2040"`. Decides the methods offered and shows beside the file. Without it, WebFlash goes by the file (a UF2's family, a Klipper file's dictionary, its address). |

The page references the file by its path, so publish it beside the generated HTML; the static fallback links it for download. `webflash -i` embeds it in the page instead.

```toml
[board]
title = "Katapult for STM32G0B1 (prebuilt)"

[prebuilt]
file = "katapult.bin"
address = 0x08000000
mcu = "stm32g0b1xx"

[flash]
methods = ["dfu", "download"]
```

## Which tables go together

| Table | Built from source | `[prebuilt]` |
|-------|-------------------|--------------|
| `[board]` | required | required |
| `[firmware]` | required | not allowed |
| `[config]` or `[[setup]]` | one of them, required | not allowed |
| `[katapult]` | optional, with Klipper or Kalico and a `katapult` defconfig | not allowed |
| `[[option]]` | optional | not allowed: a file has nothing to configure |
| `[flash]` | optional | optional |
| `[prebuilt]` | not allowed | required |

## A full example

A CAN toolhead in two setups: on a CAN bus with Katapult in its first 8 KiB, or on USB with no bootloader. It is [`examples/can-toolhead`](https://github.com/xbst/webflash/tree/master/examples/can-toolhead) in the repository with comments of its own, and runs live in the [CAN toolhead example](../examples/can-toolhead.md).

```toml
[board]
title = "CAN toolhead (STM32G0B1)"
description = """
Klipper firmware for an STM32G0B1 toolhead board.

On a CAN bus, connect a candleLight-compatible USB to CAN adapter, or a board running Klipper in USB to CAN bridge mode, to the same bus. Set the CAN bus speed to the one your bus runs at: `canbus_frequency` in the bridge's configuration."""

[firmware]
project = "klipper"
projects = ["klipper", "kalico"]
version = "latest"

# Katapult is offered with the CAN setup, ticked when the card opens.
[katapult]
version = "latest"

# What `make savedefconfig` writes: low-level options on (so the CAN bus
# speed can be set), CAN on PB0/PB1; the 8 KiB bootloader, the 8 MHz crystal
# and the 1 Mbit/s speed are defaults. Katapult's defconfig relies on the
# same defaults, with its application at 8 KiB.
[[setup]]
id = "can"
title = "CAN bus, with Katapult"
description = "On a CAN bus (PB0/PB1), updated through Katapult in the first 8 KiB."
defconfig = """
CONFIG_LOW_LEVEL_OPTIONS=y
CONFIG_MACH_STM32=y
CONFIG_MACH_STM32G0B1=y
CONFIG_STM32_MMENU_CANBUS_PB0_PB1=y
"""
katapult = """
CONFIG_MACH_STM32=y
CONFIG_MACH_STM32G0B1=y
CONFIG_STM32_MMENU_CANBUS_PB0_PB1=y
"""

# No bootloader and no Katapult; USB on PA11/PA12 is the default.
[[setup]]
id = "usb"
title = "USB, no bootloader"
description = "Plugged into the host over USB, flashed with the chip's DFU bootloader."
defconfig = """
CONFIG_MACH_STM32=y
CONFIG_MACH_STM32G0B1=y
CONFIG_STM32_FLASH_START_0000=y
"""
methods = ["dfu", "download"]

[[option]]
symbol = "CANBUS_FREQUENCY"
label = "CAN bus speed"
values = [1000000, 500000, 250000]
labels = { 1000000 = "1 Mbit/s", 500000 = "500 kbit/s", 250000 = "250 kbit/s" }
setups = ["can"]

[flash]
methods = ["katapult-can", "dfu", "download"]

[flash.instructions]
katapult-can = "Plug in the USB to CAN adapter and click Connect. WebFlash lists the nodes on the bus; pick the toolhead. A node running Klipper is restarted into Katapult first."
dfu = "Plug the toolhead's USB port into this computer, hold BOOT, tap RESET, release BOOT, then click Connect. On Windows, if the browser lists the bootloader but cannot open it, install the WinUSB driver on it with Zadig."
```

While Katapult is ticked, the reader can pick only the `can` setup; unticking it makes `usb` available too. With **None**, the card builds Katapult alone from the `can` setup's `katapult` defconfig.

The repository has one example for each flashing path, each with a live card here: [a board on USB](../examples/usb-board.md) (`[config]` with Katapult unticked), [the CAN toolhead](../examples/can-toolhead.md), [RP2040](../examples/rp2040.md), [Katapult alone](../examples/katapult.md), [LPC1769](../examples/lpc1769.md) and [a prebuilt file](../examples/prebuilt.md).

## Errors

The loader stops at the first problem, with a message that names the file and the table: `<file>: <table>: <message>`. A `[[setup]]` or `[[option]]` is named by its position and, once known, its id or symbol: `board.toml: [[setup]] #2 (usb): ...`, `board.toml: [[option]] #1 (CANBUS_FREQUENCY): ...`. The command line prints it after `Error:`, and the site shows it when it opens the TOML.

| Message | What to change |
|---------|----------------|
| `invalid TOML in board.toml: ...` | A TOML syntax error, with the line and column. |
| `board.toml: unknown top-level key(s) or table(s): configs (valid: [board], [firmware], [katapult], [config], [[setup]], [[option]], [flash], [prebuilt])` | A misspelled table name. |
| `board.toml: [board]: unknown key(s): titel (valid: title, description, image, theme, theme_dir, engine_url)` | A misspelled key; each table lists its valid keys. |
| `board.toml: [board]: missing required key 'title' (the card's heading and the page title)` | Give the board a title. |
| `board.toml: [board]: image must be a URL or a path relative to this TOML, without '..' (got '../board.webp')` | Move the photo beside the TOML or below its folder, or give a URL. |
| `board.toml: [board]: engine_url must be an http:// or https:// URL like https://webflash.isiks.tech/engine/v1/ (got ...)` | Leave `engine_url` out unless you run your own copy of WebFlash. |
| `board.toml: a board TOML needs [firmware] and [config] (or [[setup]] tables) to build from source, or [prebuilt] to flash a file` | Add the tables for one of the two shapes. |
| `board.toml: [firmware]: projects must include 'kalico', the project the card starts with` | Add `project` to `projects`. |
| `board.toml: [firmware]: projects cannot mix katapult with klipper or kalico: the bootloader's configuration is not the firmware's` | Use [`[katapult]`](#katapult) to offer Katapult beside the firmware. |
| `board.toml: [firmware]: version 'v0.12.0' must be one of versions, which the reader picks from` | Add the version to the `versions` list, or start on `"latest"` or `"release"`. |
| `board.toml: [firmware]: versions must be "all", "releases" or a list of ref ids (got 'tags')` | Use one of the three forms. |
| `board.toml: [config] and [[setup]] cannot be used together: write one [config] table, or a [[setup]] table for each way to set up the board` | See [`[config]` or `[[setup]]`](#config-or-setup). |
| `board.toml: [config]: missing required key 'defconfig' (the text make savedefconfig writes)` | Paste the defconfig. |
| `board.toml: [config]: defconfig line 2: 'CONFIG_MACH_STM32G0B1=y' starts with whitespace; Kconfig ignores an indented line, so start each .config line at column 0` | Take the spaces off. |
| `board.toml: [config]: defconfig line 3: '#CONFIG_USB_SERIAL_NUMBER_CHIPID is not set' is not read by Kconfig; write it as # CONFIG_NAME is not set` | One space after the `#`. |
| `board.toml: [config]: defconfig line 4: CONFIG_SERIAL_BAUD=0250000 has a leading zero, which C reads as octal; write it as CONFIG_SERIAL_BAUD=250000` | Drop the leading zero. |
| `board.toml: [config]: defconfig line 5: CONFIG_MACH_STM32 is already set on line 1` | Keep one line per symbol. |
| `board.toml: [config]: katapult is Katapult's defconfig, which needs a [katapult] table (the Katapult version to build beside the firmware)` | Add `[katapult]`, or take the `katapult` key out. |
| `board.toml: [katapult]: offers Katapult beside a firmware, so [firmware] project must be klipper or kalico; to build Katapult alone, leave [katapult] out` | Katapult alone is `project = "katapult"` with no `[katapult]`. |
| `board.toml: [katapult]: no setup can build it: give at least one [[setup]] a katapult key, Katapult's defconfig` | Add Katapult's defconfig to a setup. |
| `board.toml: [[setup]] #1: id must be lowercase letters, digits and '-' like "can-katapult" (got 'CAN')` | Use a lowercase id. |
| `board.toml: [[setup]] #2: id 'can' is already a setup` | Give each setup its own id. |
| `board.toml: [[setup]]: write '[[setup]]' (an array of tables), not '[setup]'` | Double brackets, for `[[setup]]` and `[[option]]` alike. |
| `board.toml: [[option]] #1: symbol is written without CONFIG_: "CANBUS_FREQUENCY" (got 'CONFIG_CANBUS_FREQUENCY')` | Drop the prefix. |
| `board.toml: [[option]] #2: symbol CANBUS_FREQUENCY is already an option` | One option per symbol. |
| `board.toml: [[option]] #1 (CANBUS_FREQUENCY): setups: 'cna' is not the id of a setup (valid: can, usb)` | Name existing setups. |
| `board.toml: [flash]: methods: unknown method 'stlink' (valid: dfu, picoboot, uf2, katapult, katapult-can, download)` | Use the [method ids](#flash). |
| `board.toml: [firmware] cannot be used with [prebuilt]: a board TOML builds from source ([firmware] and [config]) or flashes a file ([prebuilt]), not both` | Pick one shape. |
| `board.toml: [prebuilt]: address is required for a .bin file, which carries no address of its own (for example address = 0x08000000)` | Add the address the file starts at. |
| `board.toml: [prebuilt]: address is only for a .bin file: a .hex file carries its own addresses` | Take `address` out. |
| `board.toml: [prebuilt]: file must be a .bin, .hex, .uf2 or .elf firmware file (got 'klipper.zip')` | Point at the firmware file itself. |

A file that is not UTF-8 is refused with `board.toml is not UTF-8 text: ...`. A byte order mark at the start is dropped, and CRLF line endings read as LF, so a file saved by Notepad renders the same page as one saved anywhere else.

## Warnings

Some problems leave the page usable, so they are warnings: the page is still written. The command line prints each after `Warning:`, and the site's Generate dialog lists them.

| Warning | Why |
|---------|-----|
| `board.toml: [[option]] #1 (CANBUS_FREQUENCY): labels names '125000', which is not one of values, so it is never shown` | A label for a value the option does not offer. |
| `board.toml: [flash.instructions]: 'uf2' is not one of [flash] methods, so its instructions are never shown` | Instructions for a method no table offers. |
| `board.toml: [board]: image is a URL, so -i leaves it as it is` | `-i` embeds only files. |

## What the loader does not check

The loader has neither a Kconfig nor the list of versions, so two things are checked later, by the site and the card once they have them:

- **Symbols and values.** A misspelled symbol in a defconfig or an `[[option]]` passes the loader. When the site configures the board, Configure lists the symbols the version does not have and the values it would not take, and an int or hex option's `values` are checked against the symbol. The card shows an option the version lacks as "not in this version".
- **Versions.** A `version` or `versions` entry the site does not offer passes the loader. The site and the card then say so, naming what there is: `Klipper has no version "v0.99.0" in the sources index. It has: master, v0.13.0, …, and older commits.`

Load the TOML in the site (**Open TOML**) and build it once before you publish its card.

## How the TOML is written

The site's **Save TOML** and the `webflash` package write a board TOML from its tables the same way, byte for byte:

- The tables come in the order of this page: `[board]`, `[firmware]`, `[katapult]`, `[config]` or each `[[setup]]`, `[[option]]`, `[flash]`, `[flash.instructions]`, `[prebuilt]`.
- A key that holds its default is left out, except `[firmware] version` and `[katapult] version`, which are always written. `[katapult] default` is written only as `default = false`.
- A single setup is written back as `[config]` while it is the TOML's form and the setup holds nothing only `[[setup]]` can: no title, no description, no methods. Otherwise every setup is a `[[setup]]` table.
- Defconfigs, and any text with line breaks, are multi-line strings (`"""`).
- `values` are written as strings: `values = ["1000000", "500000"]` loads the same as the integers.
- An option's `labels` follow the order of its `values`, then any other keys sorted.
- A `.bin`'s address is written in hex: `address = 0x08000000`.

Comments are not kept: a TOML opened in the site and saved again comes back without them. Keep a commented copy in your repository if you want the notes, and paste changes into it.

## Tips

- Start from the site: configure the board, add setups and options in the Embed step, and save the TOML. Then add comments and instructions by hand.
- Comments use `#` and are ignored, so you can note in the TOML which defaults a short defconfig relies on, as the examples do.
- An `[[option]]` for a low-level setting, such as `CANBUS_FREQUENCY`, needs `CONFIG_LOW_LEVEL_OPTIONS=y` in the defconfig: without it, Klipper's Kconfig hides the setting, and the card shows it disabled.
- `webflash board.toml` checks the whole file as it renders: run it before you commit.
