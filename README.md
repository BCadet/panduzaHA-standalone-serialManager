# PanduzaHA standalone serialManager

This tool help to setup and manage PPP auto start rules to be used with PanduzaHA-standalone device

## Installation

The pip installation is not tested.
For now, udev rules are created in the installation folder and need to be copied manually to the correct location `/etc/udev/rules.d`
The systemd service `host_files/PanduzaHA-ng-pppd@.service`need to be copied to `/etc/systemd/system`

## GUI

The manager GUI is a NiceGUI based gui. Open it with your favorite browser.
