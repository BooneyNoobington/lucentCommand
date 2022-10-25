#!/bin/bash

source=/home/grindel/Entwicklung/lucentLIMS/
target=/opt/lucent/

data_source=/home/grindel/Entwicklung/lucentLIMS_data_dir/
data_target=/usr/local/var/lucent/

sudo rsync -avu --progress "$source" "$target"
sudo rsync -avu --progress "$data_source" "$data_target"

sudo chown lucent:lucent -R "$target"
sudo chown lucent:lucent -R "$data_target"

cd $source
git add .

git commit -m "$1"

git push origin main

pushd /opt/lucent

sudo -u lucent ./lucent.py
