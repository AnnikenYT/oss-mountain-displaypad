# Open Source Support for the Mountain DisplayPad

This repository provides a Python driver for the Mountain DisplayPad, enabling users to control and customize their DisplayPad devices on various operating systems.

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

The package is not yet published to PyPI, but build artifacts can be found in the [Releases](https://github.com/AnnikenYT/oss-mountain-displaypad/releases). The latest release can be found in the [Action Artifacts](https://github.com/AnnikenYT/oss-mountain-displaypad/actions).

## Usage

Please refer to the [examples](./examples) directory for usage examples of the library and driver. More information can be found in the respective `README.md` files within the `packages/driver` and `packages/library` directories.

## FAQ

### I keep getting a Timeout error!
Unfortunately, the Timeout errors are thrown at pretty much any USB communication failure.
Make sure that:
- You have the correct permissions to access USB devices on your OS. On Linux, this may involve setting up udev rules. Run the script in [scripts/check_udev_perms.py](./scripts/check_udev_perms.py) to verify.
:warning: PLEASE validate that the suggested commands are correct for your distro! All I did was post what worked for me on Fedora.
- The DisplayPad is properly connected to your computer.
- No other application is currently using the DisplayPad.
- Restarting your computer can sometimes resolve USB communication issues.