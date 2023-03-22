#!/bin/sh
paru -Syu
case $? in
    0)
        notify-send "System updated"
        ;;
    *)
        read -p "Update failed, press enter to exit..."
        notify-send "Update failed"
        exit 1
esac
