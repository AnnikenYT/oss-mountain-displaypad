# MountainDisplayPad for Linux

This is a python USB driver for linux to support the DisplayPad hardware manufactured by Mountain.gg. It was born from the result of reverse engineering the basecamp software for windows so there will be plenty of missing features.

The python module consists of the `mountain_displaypad.py` python file that implements the USB protocol along with the user configurable background DisplayPadWorker service. The background service is configurable through .json files stored under `~/.config/displaypad/panels/`

If you would like to simply interact with the device you can use `from mountain_displaypad import DisplayPad` and call the required gg* methods from your own respective python code. Otherwise, copy and configure any example .json files found under `/panels` and then launch the service

## Features

 - Hardware control
 	- Updating display
 		- write to full display
	 	- Set display timeout
	 	- Set brightness
	- listening for button presses
 		- emulate keystrokes
	 	- launch applications
 - Background service
	- Control OBS
		- start/stop recording
		- change scene
		- toggle sources
		- toggle input
	- on-the-fly panel config switching
	- icon and image handling

## Installing

### Requirements

System packages:
```
python3
python-venv
```

External modules:
```
pyusb
evdev
obs-websocket-py
pillow
```

### Configure virtual environment and install the required modules:

```
mkdir displaypad
cd displaypad
python3 -m venv ./venv
source ./venv/bin/activate
git clone {giturl}
cd ./mountain-displaypad-python/
pip3 install -r requirements.txt
```

### Optionally install and start the systemd unit file:

```
cp DisplayPadWorker.service /usr/lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start DisplayPadWorker
```

### Add a udev rule for access

Some linux distros will require a udev rule for user access to the USB device

```
SUBSYSTEMS=="usb", ATTRS{idVendor}=="3282", ATTRS{idProduct}=="0009", MODE="0666", TAG+="uaccess"
```

## Configuring

Example .json config files are located under `/panels` and per-user configs can be placed in `/home/{username}/.config/displaypad/panels/`

### Panel .json settings

The panel configs consist of basic options and a keymapping dictionary that corresponds to each key

 - `name` - a unique name for this panel
 - `background` - a filepath to an 800x240 resolution image to use as a background
 - `color` - an array containing the RGB value you would like to use as a background color
 - `order` - a number value used to order this panel by

Each key has a dictionary item within the keymapping dict that consists of an action, value, and icon value

 - `action` - can be one of `keybind`, `switch`, `obscmd`, `execute`
 - `value` - a string that will be translated into action parameters depending on the action
 - `icon` - a filepath to an image that will be placed underneath the corresponding key

### Actions

`keybind` - `+` delimited keys to send. For example, to send the Windows key and D keystroke you can specify: `meta+d`

`switch` - Change panels on-the-fly by including a string of either `'prev'`, `'next'`, or a precise panel #

`obscmd` - change OBS via the obs websocket server by providing a string value of `"command parameters"`

`execute` - launch or run another program with subprocess by providing a string containing a path to the binary and any arguments: `"path arg1 arg2 arg3"`

### obscmd

The obscmd action will perform an action through the configured OBS websocket server

`toggle_input name` - used to toggle an audio input by providing the case-sensitive input name

`toggle_source name` - toggle a source by specifying the case-sensitive source item name

`toggle_record` - start and stop the recording

`switch_scene name` - switch to the specified case-sensitive scene name
