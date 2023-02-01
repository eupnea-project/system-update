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

    # these settings were already removed in v1.1.0, but the json file on GitHub was not updated, therefore
    # some newer installs still have them
    with contextlib.suppress(KeyError):
        del config["kernel_type"]
    with contextlib.suppress(KeyError):
        del config["kernel_version"]
    with contextlib.suppress(KeyError):
        del config["kernel_dev"]
    with contextlib.suppress(KeyError):
        del config["postinstall_version"]
    with contextlib.suppress(KeyError):
        del config["audio_version"]

    with open("/etc/eupnea.json", "w") as file:
        json.dump(config, file)

    # if config["distro_name"] == "arch" and config["de_name"] != "cli":
    # the auto-rotate service is not installed by default on Arch
    # bash("pacman -Syyu --noconfirm")  # update the package database
    # bash("pacman -S --noconfirm iio-sensor-proxy")
    # after a reboot the auto-rotate service will automatically be "integrated" into the DE


def v1_1_2():
    # the depthboot_updates.py file was missing some imports and therefore the v1.1.1 update was not applied
    # There were also a few other minor fixes
    v1_1_1()


def v1_1_3():
    # This update installs zram on systems that were not installed with zram
    with open("/etc/eupnea.json", "r") as f:
        config = json.load(f)
    # fedora and pop os already have zram installed and setup ootb
    # PopOS' zram generator only seems to work on new mainline kernels (possible on new chromeos kernels too)
    # -> might not work until v1.2.0 (kernel package update)
    # Debian has no systemd-zram-generator package
    if config["distro_name"] in ["arch", "ubuntu"]:
        cpfile("/tmp/eupnea-system-update/configs/systemd-services/eupnea-system-update-v1.1.3.service",
               "/etc/systemd/system/eupnea-system-update-v1.1.3.service")
        cpfile("/tmp/eupnea-system-update/configs/bash-scripts/update-v1.1.3-postinstall.sh",
               "/usr/lib/eupnea/update-v1.1.3-postinstall.sh")
        bash("systemctl enable eupnea-system-update-v1.1.3.service")


def v1_1_4():
    # The previous update tried to install a package from inside a postinstall script which does not work as the
    # apt/pacman processes have lock files
    # The v1.1.3 update has now been fixed and this update reruns the v1.1.3 update
    v1_1_3()

#
# def v1_2_0():
#     # This update removes the old kernel scripts/configs and installs the new mainline-only kernel package
#     # and uninstalls the cloud-utils package as it's no longer needed.
#
#     # some older installs might still have this option in eupnea.json
#     with open("/etc/eupnea.json", "r") as f:
#         config = json.load(f)
#     with contextlib.suppress(KeyError):
#         del config["dev_build"]
#     with open("/etc/eupnea.json", "w") as file:
#         json.dump(config, file)
#
#     # Force stop and disable the old kernel update script
#     with contextlib.suppress(KeyError):  # services might be deleted already, if the install is a bit newer
#         bash("systemctl stop eupnea-update.timer eupnea-update.service")
#         bash("systemctl disable eupnea-update.timer eupnea-update.service")
#     # Remove the old kernel update script
#     rmfile("/etc/systemd/system/eupnea-update.timer")
#     rmfile("/etc/systemd/system/eupnea-update.service")
#     # Remove old kernel modules load config
#     rmfile("/etc/modules-load.d/eupnea-modules.conf")
#
#     # Download and install the new kernel package with the system package manager + uninstall cloud-utils
#     if path_exists("/usr/bin/apt"):
#         bash("apt-get update -y")
#         bash("apt-get install -y eupnea-kernel")
#         bash("apt-get purge -y cloud-utils")
#     elif path_exists("/usr/bin/pacman"):
#         bash("pacman -Syyu --noconfirm")
#         bash("pacman -S --noconfirm eupnea-kernel")
#         bash("pacman -R --noconfirm cloud-utils")
#     elif path_exists("/usr/bin/dnf"):
#         bash("dnf update --refresh -y")
#         bash("dnf install -y eupnea-kernel")
#         bash("dnf remove -y cloud-utils")
