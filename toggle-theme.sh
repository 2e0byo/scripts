#!/bin/sh

case $1 in
    dark)
        rm ~/.config/wofi/style.css
        ln -rs ~/.config/wofi/style-dark.css ~/.config/wofi/style.css 
        ;;
    light)
        rm ~/.config/wofi/style.css
        ln -rs ~/.config/wofi/style-light.css ~/.config/wofi/style.css 
        ;;
    *)
        echo "Unknown theme: $1, should be one of 'dark' or 'light'"
        ;;
esac
