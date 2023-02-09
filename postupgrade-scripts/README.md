# postupgrade-scripts

Sometimes the system update script needs to install/remove a package from the depthboot system. This is not possible
from within a postinstall script of a package. Therefor a systemd updater script is run, which will wait for the
packagemanager to finish and then install/remove the necessary packages.