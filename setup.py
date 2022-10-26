#!/bin/env python3

# Setup lucentLIMS.

import csv  # For guessing package manager.

distroInfo = {}  # Initialize empty dictianory.

# Open os-release file and read contents.
with open("/etc/os-release") as f:
    # Interpret it like a csv file.
    reader = csv.reader(f, delimiter="=")
    # Loop over all rows / lines and get key value pairs of them.
    for row in reader:
        if row:
            distroInfo[row[0]] = row[1]

# Create a class defining your package manager.
class PackageManager():

    # Constructor.
    def __init__(self, commands):
        try:
            self.repoUpdateCmd = commands["repoUpdate"]
        except KeyError:  # Some package managers don't do this.
            self.repoUpdateCmd = ""
        self.distUpgradeCmd = commands["distUpgrade"]
        self.installCmd = commands["install"]

    ## Methods ##
    def repoUpdate(self):
        import os  # For giving the os commands.
        if self.repoUpdateCmd == "":
            print("Your' package manager doesn't do that.")
        else:
            os.system(f"sudo {self.repoUpdateCmd}")

    def distUpgrade(self):
        import os  # For giving the os commands.
        os.system(f"sudo {self.distUpgradeCmd}")

    def install(self, packagesList):
        import os  # For giving the os commands.
        # Turn packages list into string.
        packagesStr = " ".join(packagesList)
        os.system(f"sudo {self.installCmd} {packagesStr}")

# Depending on which distro there is, set the package manager.
if distroInfo["ID"].lower() == "ubuntu":
    commands = {
        "repoUpdate": "apt update"
      , "distUpgrade": "apt dist-upgrade -y"
      , "install": "install -y"
    }
elif distroInfo["ID"].lower() == "manjaro":
    commands = {
        "distUpgrade": "pamac upgrade --aur"
      , "install": "pamac install"
    }

pm = PackageManager(commands)

pm.repoUpdate()
pm.distUpgrade()
pm.install(["htop", "kate"])
