# This file contains all updates for Depthboot. It is called by system-update.py
# The functions are named after the version they update to. For example, the update script for v1.1.0 is named v1_1_0().
# Read the full changelog here: https://github.com/eupnea-linux/depthboot-builder/releases

import contextlib
from functions import *
import json


def v1_1_0():
    # This update was done by the old scripts updater script. It is only here for reference.
    # update-scripts.py can be found here:  https://github.com/eupnea-linux/postinstall-scripts/blob/main/update-scripts
    pass


def v1_1_1():
    # This update adds a fix for auto rotate being flipped on some devices.
    # It has been added to the depthboot script a few weeks prior to this update
    cpfile("/tmp/eupnea-system-update/configs/hwdb/61-sensor.hwdb", "/etc/udev/hwdb.d/61-sensor.hwdb")
    bash("systemd-hwdb update")

    # Remove old eupnea-utils scripts
    rmfile("/usr/lib/eupnea/eupnea-postinstall")  # has been renamed to just postinstall
    rmfile("/usr/lib/eupnea/eupnea-update")  # has been included accidentally in the package

    # Remove unneeded settings from /etc/eupnea.json
    with open("/etc/eupnea.json", "r") as f:
        config = json.load(f)
    with contextlib.suppress(KeyError):
        # these settings were already removed in v1.1.0, but the json file on GitHub was not updated, therefore
        # some newer installs still have them
        del config["kernel_type"]
        del config["kernel_version"]
        del config["kernel_dev"]
        del config["postinstall_version"]
        del config["audio_version"]
    with open("/etc/eupnea.json", "w") as file:
        json.dump(config, file)

    if config["distro_name"] == "arch" and config["de_name"] != "cli":
        # the auto-rotate service is not installed by default on Arch
        bash("pacman -Syyu --noconfirm")  # update the package database
        bash("pacman -S --noconfirm iio-sensor-proxy")
        # after a reboot the auto-rotate service will automatically be "integrated" into the DE


def v1_1_2():
    # the depthboot_updates.py file was missing some imports and therefore the v1.1.1 update was not applied
    v1_1_1()
