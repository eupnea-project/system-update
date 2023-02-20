#!/usr/bin/env python3

# This script is used to update Depthboot/EupneaOS between releases.

import json
from functions import *

if __name__ == "__main__":
    # Check if running under Depthboot or EupneaOS
    with open("/etc/eupnea.json", "r") as f:
        config = json.load(f)
    try:
        current_version = config["depthboot_version"]
        os_type = "depthboot_version"
        with open("/usr/lib/eupnea-system-update/configs/depthboot_versions.txt", "r") as f:
            versions_array = f.read().splitlines()
        from depthboot_updates import *  # import the depthboot updates
    except KeyError:
        current_version = config["eupnea_os_version"]
        os_type = "eupnea_os_version"
        # Convert versions.txt into an array
        with open("/usr/lib/eupnea-system-update/configs/eupnea_os_versions.txt", "r") as f:
            versions_array = f.read().splitlines()
        from eupnea_os_updates import *  # import the EupneaOS updates

    # Remove versions older than current version from the array
    try:
        versions_array = versions_array[versions_array.index(current_version) + 1:]
    except ValueError:
        print_error("Your local eupnea version is higher than the package version. This should not happen. Please "
                    "report this issue on the Eupnea GitHub.")
        exit(1)

    if len(versions_array) == 0:  # No updates available.
        exit(0)
    else:
        # Create /var/tmp/eupnea-updates for the modify-packages script
        mkdir("/var/tmp/eupnea-updates", create_parents=True)
        # Execute update scripts for all versions in the array
        for version in versions_array:
            version = version.replace(".", "_")  # Functions cant have dots in their names -> replace with underscores
            globals()[f"v{version}"]()  # This calls the function named after the version

        bash("systemctl daemon-reload")
        # Start eupnea-update service to install package updates if needed
        # systemctl start eupnea-update will wait for the service to finish, but the service is waiting for the package manager to quit -> start service in a subthread
        # bash() uses /bin/sh and not /bin/bash, so it cant use the "&" operator
        # Popen cant use "&" as it tries to pass it as a flag to systemctl
        # -> use external sh file with the "&" operator
        print_status("Starting eupnea-update service to install package updates...")
        bash("sh /usr/lib/eupnea-system-update/configs/start-update-systemd.sh")

        # Update version in config with the latest version in the array
        # reload config from disk
        with open("/etc/eupnea.json", "r") as f:
            config = json.load(f)
        config[os_type] = versions_array[-1]
        with open("/etc/eupnea.json", "w") as file:
            json.dump(config, file)
