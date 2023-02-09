#!/usr/bin/env python3

import argparse
import sys
from typing import Tuple

sys.path.insert(0, "/usr/lib/eupnea")
from functions import *


# parse arguments from the cli.
def process_args():
    parser = argparse.ArgumentParser()
    # list of packages to be installed
    parser.add_argument("package_list", nargs="+", help="List of packages to be installed. Packages that need to be "
                                                        "deleted should be prefixed with '-'")
    return parser.parse_args()


def parse_package_list(packages_raw: list) -> Tuple[list, list]:
    packages_remove = []
    packages_install = []
    for package in packages_raw:
        if package.startswith("-"):
            packages_remove.append(package[1:])
        else:
            packages_install.append(package)
    return packages_install, packages_remove


if __name__ == "__main__":
    args = process_args()
    temp_output = parse_package_list(args.package_list)

    if len(temp_output[0]) == 0 and len(temp_output[1]) == 0:
        exit(0)

    # Wait for pacman to be ready
    while True:
        try:
            bash("sudo pacman -Syy")
        except subprocess.CalledProcessError:
            sleep(5)
            continue
        break

    # force-update all repos
    bash("pacman --noconfirm -Syy")

    # install packages
    if len(temp_output[0]) > 0:
        print("pacman -S --noconfirm " + " ".join(temp_output[0]))

    # remove packages
    if len(temp_output[1]) > 0:
        print("pacman -R --noconfirm " + " ".join(temp_output[1]))
