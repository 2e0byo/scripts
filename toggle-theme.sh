#!/bin/sh

function wofi_theme() {
    rm ~/.config/wofi/style.css
    ln -rs ~/.config/wofi/style-$1.css ~/.config/wofi/style.css
}
}


case $1 in
    dark)
        wofi_theme dark
        ;;
    light)
        wofi_theme light
        ;;
    *)
        echo "Unknown theme: $1, should be one of 'dark' or 'light'"
        ;;
esac
