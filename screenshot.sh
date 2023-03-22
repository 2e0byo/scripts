#!/bin/sh
grim -g "$(slurp)" ~/screenshots/$(date +%Y-%m-%d-%T)-screenshot.png
find ~/screenshots -maxdepth 1 -type f -mtime +180 -exec rm {} \;
