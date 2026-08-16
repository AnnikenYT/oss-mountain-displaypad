<center>
  <img src="./docs/img/brand/oss-mountain-displaypad-horizontal.svg" alt="Project Logo" width="600">

  <h1>Open Source Support for the Mountain DisplayPad</h1>
</center>

[![Build Packages](https://github.com/AnnikenYT/oss-mountain-displaypad/workflows/Build%20Packages/badge.svg)](https://github.com/AnnikenYT/oss-mountain-displaypad/actions?query=workflow:"Build+Packages")
[![GitHub tag](https://img.shields.io/github/tag/AnnikenYT/oss-mountain-displaypad?include_prereleases=&sort=semver&color=blue)](https://github.com/AnnikenYT/oss-mountain-displaypad/releases/)
[![License](https://img.shields.io/badge/License-MIT-blue)](#license)
[![issues - oss-mountain-displaypad](https://img.shields.io/github/issues/AnnikenYT/oss-mountain-displaypad)](https://github.com/AnnikenYT/oss-mountain-displaypad/issues)

<center>
<figure>
  <img src="./docs/img/render.png" width="600" alt="Descriptive alt text">
  <figcaption>Example: My personal dashboard created with this library.</figcaption>
</figure>
</center>

This repository provides a Python driver and library for the Mountain DisplayPad, enabling users to control, automate, and customize their DisplayPad devices on Linux (and possibly other platforms).

> [!NOTE]
> This is **not** meant to replace the Mountain BaseCamp software, but instead to make it possible to integrate the DisplayPad into your own projects. If you're looking for a replacement for BaseCamp, please check out [ramisotti13-eng/BaseCamp-Linux](https://github.com/ramisotti13-eng/BaseCamp-Linux)!

**:window: Windows or :apple: Mac user?** Please see the [FAQ](#faq) for more information on the current state of support for these operating systems.

Disclaimer: This Project is not affiliated with or endorsed by the Mountain Brand or 360 Service Agency GmbH. The Mountain Logo is a registered trademark of 360 Service Agency GmbH.

## Contents
- [Dependencies & OS Support](#dependencies--os-support)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Repo Structure](#repo-structure)
- [FAQ](#faq)
- [Acknowledgments & Credits](#acknowledgments--credits)

## Dependencies & OS Support

![linux - full](https://img.shields.io/badge/linux-full-2ea44f?logo=linux&logoColor=ffffff)
![windows - partial](https://img.shields.io/badge/windows-partial-EBAF00?logo=gitforwindows&logoColor=ffffff)[^1](#faq)
![macos - untested](https://img.shields.io/badge/macos-untested-EBAF00?logo=apple&logoColor=ffffff)

[![Go to Python website](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2FAnnikenYT%2Foss-mountain-displaypad%2Frefs%2Fheads%2Fmain%2Fpackages%2Flibrary%2Fpyproject.toml&query=project.requires-python&label=lib&logo=python&logoColor=white)](https://python.org)
[![Go to Python website](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2FAnnikenYT%2Foss-mountain-displaypad%2Frefs%2Fheads%2Fmain%2Fpackages%2Fdriver%2Fpyproject.toml&query=project.requires-python&label=driver&logo=python&logoColor=white)](https://python.org)

## Installation

### From PyPi

Both packages are available on PyPi.

#### Library (you want this one)

[![PyPI Version](https://img.shields.io/pypi/v/displaypad-lib)](https://pypi.org/project/displaypad-lib/)

```bash
pip install displaypad-lib
```

#### Driver

[![PyPI Version](https://img.shields.io/pypi/v/displaypad-driver)](https://pypi.org/project/displaypad-driver/)


```bash
pip install displaypad-driver
```

### Dev / Source

Install editable packages for development:
```bash
pip install -e packages/driver -e packages/library
```

## Usage

For documentation, see the [project wiki](https://github.com/AnnikenYT/oss-mountain-displaypad/wiki).

See the [examples](./examples) directory for complete working examples:
- [driver_example.py](./examples/driver_example.py) - Direct driver communication & key event polling.
- [lib_example.py](./examples/lib_example.py) - High-level library usage with custom buttons & icons.
- [page_example.py](./examples/page_example.py) - Multi-page navigation & auto-timeout screens.
- [clock.py](./examples/clock.py) - Live digital clock implementation.

## Features

- **USB Driver (`displaypad-driver`)**:
  - Dual-interface transport (`hidapi` for commands/events on Interface 3, `PyUSB` for fast pixel streaming on Interface 1).
  - Per-button 102×102 BGR tile uploads (`upload_button`) and full-panel updates (`upload_panel`).
  - Thread-safe USB queue with input interleaving and report deduplication so keypresses are never lost during screen updates.
  - Backlight brightness control (`set_brightness`), hardware `SET_IDLE` traffic suppression, and initialization handshakes.
  - Image manipulation & animation helpers (`split_image_to_tiles`, `split_gif_to_tiles`, `load_gif_frames`, rotation, text label/folder icon generation).

- **Rich Feature Library (`displaypad-lib`)**:
  - Multi-page layout engine (`Page`, `PageManager`) with auto-timeout navigation (`mode: "after" | "idle"`).
  - Specialized Key types: `GifKey` (animated GIF playback), `IconKey`, `LabelKey`, `FramerateLimitedKey`, `LoggerKey`.
  - Comprehensive interaction lifecycle hooks: `on_press`, `on_release`, `on_double_press`, `on_long_press`, `on_tick`, `on_mount`.
  - Hybrid rendering: fast per-button tile updates for single key repaints, automatic full-panel batching for page switches.
  - Automatic unassigned key tile clearing (blank black hardware rendering).

## Repo Structure

```
(oss-mountain-displaypad)
├── packages/
│   ├── driver/   - Low-level, thread-safe PyUSB + hidapi driver & protocol helpers
│   └── library/  - High-level multi-page library, key abstractions & rendering engine
├── examples/     - Working example scripts (driver, lib, clock, custom keys)
├── tests/        - Automated unit test suite
├── scripts/      - Permissions & setup helper scripts
└── ...
```

## FAQ

### Why is Windows support marked as partial?
Primary development takes place on Linux. While `pyusb` and `hidapi` support Windows, USB claim permissions differ. ~~For Windows experimental work, see the `feat/windows-support` branch.~~ <small>(That branch is currently outdated. I'll do some more windows dev eventually when I need it, but I haven't gotten around to it. Feel free to contribute!)</small>

### What about MacOS support?
`pyusb` and `hidapi` support macOS, but hardware verification on macOS has not been tested yet. If you own a Mac and have a DisplayPad, feel free to test and open an issue with the results!

### I keep getting a Timeout error!
USB communication timeouts typically indicate udev permission restrictions or endpoint conflicts.
- Run `python3 scripts/check_udev_perms.py` to set up proper udev rules on Linux.
- Ensure no other application (e.g. BaseCamp) is actively holding the USB interfaces.

### DisplayPad not detected / keys not rendered

Quote [ramisotti13-eng/BaseCamp-Linux](https://github.com/ramisotti13-eng/BaseCamp-Linux/tree/main#displaypad-not-detected--keys-not-rendered-usb-interface-quirk):

> On some systems (seen on Ubuntu 24.04 / Linux Mint 22) the DisplayPad enumerates
> but its command interface never appears, so the app shows it as *not connected*,
> the startup logo is missing, and key images don't render. The kernel log shows:
> 
> ```
> usb 3-3: config 1 has an invalid interface number: 3 but max is 2
> usb 3-3: config 1 has no interface number 2
> usbhid 3-3:1.1: couldn't find an input interrupt endpoint
> ```
> 
> **Cause:** the DisplayPad reports its USB interfaces out of order and `usbhid`
> rejects interface 3 (which BaseCamp needs for commands and key events).
> 
> **Fix** (thanks @FransM): tell `usbhid` to skip the broken input sync for this
> device:
> 
> ```bash
> echo 'options usbhid quirks=0x3282:0x0009:0x4000' | \
>   sudo tee /etc/modprobe.d/mountain-displaypad.conf
> sudo update-initramfs -u   # Debian/Ubuntu/Mint
> # Fedora/Nobora: sudo dracut --force
> ```
> 
> Then reboot. `0x4000` is `HID_QUIRK_NO_INPUT_SYNC`. After this the command
> interface appears and the DisplayPad works normally.

## Acknowledgments & Credits

This project builds upon the fantastic work of the open-source community:
- [ReversingForFun/MountainDisplayPadPy](https://github.com/ReversingForFun/MountainDisplayPadPy/tree/main) for original reverse-engineered DisplayPad Python driver concepts.
- [JeLuF/mountain-displaypad](https://github.com/JeLuF/mountain-displaypad/tree/main) for initial key event decoding.
- [ramisotti13-eng/BaseCamp-Linux](https://github.com/ramisotti13-eng/BaseCamp-Linux) for critical device performance optimizations, dual-transport (PyUSB + hidapi) architecture, protocol handshakes, input report interleaving during display uploads, and multi-page layout engine inspiration.