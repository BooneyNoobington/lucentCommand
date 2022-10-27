#!/bin/bash

# Define sources and targets of changed files.
source=/home/grindel/Entwicklung/lucentLIMS/
target=/opt/lucent/
data_source=/home/grindel/Entwicklung/lucentLIMS_data_dir/
data_target=/usr/local/var/lucent/

# Make sure mariadb is running.
sudo systemctl start mariadb.service

# Copy changed data to testing location.
sudo rsync -avu --progress "$source" "$target"
sudo rsync -avu --progress "$data_source" "$data_target"

# Correct owenership.
sudo chown lucent:lucent -R "$target"
sudo chown lucent:lucent -R "$data_target"

# Change into source directory.
cd $source

# Upload to github.
if [[ "$1" != "" ]]; then
    echo "Commiting" $1

    # Add new files.
    git add .

    # Commit with a short comment.
    git commit -m "$1"

    # Upload to github.
    git push origin main
fi

# Change into working direcotry (return with popd?).
pushd /opt/lucent

# If desired launch lucent.
if [[ "$2" = "y" ]]; then
    # Launch lucent.
    sudo -u lucent ./lucent.py
fi
