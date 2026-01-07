# Open Source Support for the Mountain DisplayPad
[![Build Packages](https://github.com/AnnikenYT/oss-mountain-displaypad/workflows/Build%20Packages/badge.svg)](https://github.com/AnnikenYT/oss-mountain-displaypad/actions?query=workflow:"Build+Packages")
[![GitHub tag](https://img.shields.io/github/tag/AnnikenYT/oss-mountain-displaypad?include_prereleases=&sort=semver&color=blue)](https://github.com/AnnikenYT/oss-mountain-displaypad/releases/)
[![License](https://img.shields.io/badge/License-MIT-blue)](#license)
[![issues - oss-mountain-displaypad](https://img.shields.io/github/issues/AnnikenYT/oss-mountain-displaypad)](https://github.com/AnnikenYT/oss-mountain-displaypad/issues)

![Example Image](./docs/img/render.png)

This repository provides a Python driver for the Mountain DisplayPad, enabling users to control and customize their DisplayPad devices on linux.

**:window: Windows or :apple: Mac user?** Please see the [FAQ](#faq) for more information on the current state of support for these operating systems.

This was built on the amazing work of [ReversingForFun in their DisplayPad project](https://github.com/ReversingForFun/MountainDisplayPadPy/tree/main). Specifically how keys are decoded was learned from [LeLuF's mountain-displaypad](https://github.com/JeLuF/mountain-displaypad/tree/main).

## Repo Structure

```
(oss-mountain-displaypad)
├── packages/
│   ├── driver/   - low-ish level driver to communicate with the device
│   └── library/  - library for actually productively working with the driver
├── examples/     - examples
├── scripts/      - useful scripts to get up and running
└── ...
```

## Installation

## Dependencies

_OS Support_

![linux - full](https://img.shields.io/badge/linux-full-2ea44f?logo=linux&logoColor=ffffff)
![windows - partial](https://img.shields.io/badge/windows-partial-EBAF00?logo=gitforwindows&logoColor=ffffff)[^1](#faq)
![macos - untested](https://img.shields.io/badge/macos-untested-EBAF00?logo=apple&logoColor=ffffff)


_System Dependencies_

[![Go to Python website](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2FAnnikenYT%2Foss-mountain-displaypad%2Frefs%2Fheads%2Fmain%2Fpackages%2Flibrary%2Fpyproject.toml&query=project.requires-python&label=lib&logo=python&logoColor=white)](https://python.org)
[![Go to Python website](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2FAnnikenYT%2Foss-mountain-displaypad%2Frefs%2Fheads%2Fmain%2Fpackages%2Fdriver%2Fpyproject.toml&query=project.requires-python&label=driver&logo=python&logoColor=white)](https://python.org)

The package is not yet published to PyPI, but build artifacts can be found in the [Releases](https://github.com/AnnikenYT/oss-mountain-displaypad/releases). The latest builds can be found in the [Action Artifacts](https://github.com/AnnikenYT/oss-mountain-displaypad/actions).

## Usage

See the [Project Wiki](https://github.com/AnnikenYT/oss-mountain-displaypad/wiki/Quick-Start) for detailed documentation on how to use the library and driver.

Please refer to the [examples](./examples) directory for usage examples of the library and driver. More information can be found in the respective `README.md` files within the `packages/driver` and `packages/library` directories.

## FAQ

### Why is Windows support marked as partial?

I primarily developed this project on Linux. While technically the library should work just fine since `pyusb` supports Windows, there are some major errors when trying to communicate with the device on Windows. I did get the keypresses working, but writing to the DisplayPad does not work reliably at all.
If you want to use windows, please check out the [feat/windows-support branch](https://github.com/AnnikenYT/oss-mountain-displaypad/tree/feat/windows-support) and install the package from there. Please note that this branch is experimental and may not be stable.

### What about MacOS support?

I do not have access to a MacOS device, so I cannot test or guarantee that the library works on MacOS. However, since `pyusb` supports MacOS, it is possible that the library may work on MacOS as well. If you have a MacOS device and are willing to test the library, please let me know!

### I keep getting a Timeout error!
Unfortunately, the Timeout errors are thrown at pretty much any USB communication failure.
Make sure that:
- You have the correct permissions to access USB devices on your OS. On Linux, this may involve setting up udev rules. Run the script in [scripts/check_udev_perms.py](./scripts/check_udev_perms.py) to verify.
:warning: PLEASE validate that the suggested commands are correct for your distro! All I did was post what worked for me on Fedora.
- The DisplayPad is properly connected to your computer.
- No other application is currently using the DisplayPad.
- Restarting your computer can sometimes resolve USB communication issues.