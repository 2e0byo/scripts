#!/bin/sh

function wofi_theme() {
    rm ~/.config/wofi/style.css
    ln -rs ~/.config/wofi/style-$1.css ~/.config/wofi/style.css
}

function replace_between() {
    START="$1"
    END="$2"
    DATAF="$3"
    FILE="$4"
    sed "/$START/q" $FILE > $FILE.tmp
    cat $DATAF >> $FILE.tmp
    sed -n "/$END/,\$p" $FILE >> $FILE.tmp
    mv $FILE.tmp $FILE
}

function alacritty_theme() {
    pushd ~/.config/alacritty > /dev/null
    replace_between "## BEGIN COLORS ##" "## END COLORS ##" "$1.yml" alacritty.yml
    popd > /dev/null
}


case $1 in
    dark)
        wofi_theme dark
        alacritty_theme dark
        ;;
    light)
        wofi_theme light
        alacritty_theme light
        ;;
    *)
        echo "Unknown theme: $1, should be one of 'dark' or 'light'"
        ;;
esac
