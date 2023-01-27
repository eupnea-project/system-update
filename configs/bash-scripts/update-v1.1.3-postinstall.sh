#!/bin/bash

# due to the apt/pacman lock file its not possible to install additional packages from inside an apt/pacman
# hook/postinstall script

# Check if apt is installed
if command -v apt-get >/dev/null 2>&1; then
  apt-get install -y systemd-zram-generator
else
  # Check if pacman is installed
  if command -v pacman >/dev/null 2>&1; then
    sudo pacman -S --noconfirm zram-generator iio-sensor-proxy
  fi
fi

# Delete systemd service and this script
rm -rf /etc/systemd/system/eupnea-system-update-v1.1.3.service
rm -rf /usr/lib/eupnea/update-v1.1.3-postinstall.sh