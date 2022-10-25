#!/bin/bash

source=/home/grindel/Entwicklung/lucentLIMS/
target=/opt/lucent/

sudo rsync -avu --progress "$source" "$target"

sudo chown lucent:lucent -R "$target"
