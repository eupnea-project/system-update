# This file contains all updates for Depthboot. It is called by system-update.py
# The functions are named after the version they update to. For example, the update script for v1.1.0 is named v1_1_0().
# Read the full changelog here: https://github.com/eupnea-linux/depthboot-builder/releases

import contextlib
import json
import os

from functions import *


def v1_1_0():
    # This update was done by the old scripts updater script. It is only here for reference.
    # update-scripts.py can be found here:  https://github.com/eupnea-linux/postinstall-scripts/blob/main/update-scripts
    pass


def v1_1_1():
    # This update adds a fix for auto rotate being flipped on some devices.
    # It has been added to the depthboot script a few weeks prior to this update
    cpfile("/usr/lib/eupnea-system-update/configs/hwdb/61-sensor.hwdb", "/etc/udev/hwdb.d/61-sensor.hwdb")
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
    # PopOS' zram generator only seems to work on new mainline kernels (possibly on new chromeos kernels too)
    # -> might not work until v1.2.0 (kernel package update)
    # if config["distro_name"] in ["arch", "ubuntu"]:
    #     cpfile("/usr/lib/eupnea-system-update/configs/systemd-services/eupnea-system-update-v1.1.3.service",
    #            "/etc/systemd/system/eupnea-system-update-v1.1.3.service")
    #     cpfile("/usr/lib/eupnea-system-update/configs/bash-scripts/update-v1.1.3-postinstall.sh",
    #            "/usr/lib/eupnea/update-v1.1.3-postinstall.sh")
    #     bash("systemctl enable eupnea-system-update-v1.1.3.service")


def v1_1_4():
    # The previous update tried to install a package from inside a postinstall script which does not work as the
    # apt/pacman processes have lock files
    # The v1.1.3 update has now been fixed and this update reruns the v1.1.3 update
    v1_1_3()


def v1_1_5():
    # All previous updates tried installing and uninstalling packages from within this script which did not work due to
    # the package manager processes having lock files

    # v1_1_1 attempted to install iio-sensor-proxy, which did not work due to the package manager processes having lock
    # files
    # v1_1_3 attempted to install zram-generator, which also did not work
    # -> install iio-sensor-proxy and zram-generator via the new systemd service on arch
    with open("/etc/eupnea.json") as f:
        distro_name = json.load(f)["distro_name"]
    match distro_name:
        case "ubuntu":
            with open("/var/tmp/eupnea-updates/v1_1_5.txt", "w") as f:
                f.write("systemd-zram-generator")
        case "arch":
            with open("/var/tmp/eupnea-updates/v1_1_5.txt", "w") as f:
                f.write("iio-sensor-proxy zram-generator")
        case _:
            # Fedora & Pop!_OS already have zram
            pass

    # Completely clean eupnea.json for the last time
    with open("/etc/eupnea.json", "r") as f:
        config = json.load(f)

    # these settings were already removed in previous updates, but the json file on GitHub was not updated, therefore
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
    with contextlib.suppress(KeyError):
        del config["dev_build"]

    with open("/etc/eupnea.json", "w") as file:
        json.dump(config, file)

    # add custom zram config file to fedora as otherwise zram fails to start, presumably due to trying the wrong algo
    if distro_name == "fedora":
        cpfile("/usr/lib/eupnea-system-update/configs/zram/zram-generator.conf", "/etc/systemd/zram-generator.conf")


def v1_1_6():
    # The v1.1.5 update was not applied correctly on some systems
    # -> rerun the v1.1.5 update
    v1_1_5()
    # some older depthboot systems still have cloud-utils installed
    with open("/var/tmp/eupnea-updates/v1_1_6_1.txt", "w") as f:
        f.write("-cloud-utils")  # the package has the same name on all distros

    # Fix the ubuntu version on non-kinetic installs
    with open("/etc/eupnea.json") as f:
        config = json.load(f)

    if config["distro_version"] == "22.04":
        # Fix the repo target on ubuntu 22.04 and popos
        with open("/etc/apt/sources.list.d/eupnea.list", "r") as file:
            repo = file.read()
        repo = repo.replace("kinetic", "jammy")
        with open("/etc/apt/sources.list.d/eupnea.list", "w") as file:
            file.write(repo)

        # update repos to get jammy eupnea packages
        # this will not interfere with the apt lock file
        bash("apt-get update")

        # install the backported libasound2-eupnea package on jammy to support ucm configs v6 syntax
        # PopOS has an updated libasound2-eupnea package in their repo -> no need to install our backport
        if config["distro_name"] == "ubuntu":
            with open("/var/tmp/eupnea-updates/v1_1_6_2.txt", "w") as f:
                f.write("libasound2-eupnea")

#
# def v1_2_0():
#     # This update removes the old kernel scripts/configs and installs the new mainline-only kernel package
#     # and uninstalls the cloud-utils package as it's no longer needed.
#
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
