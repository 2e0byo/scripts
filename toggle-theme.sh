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

function bat_theme() {
    sed -i "s/--theme=.*/--theme=\"Solarized ($1)\"/" ~/.config/bat/config
}

function emacs_theme() {
    emacsclient -e "(spacemacs/load-theme 'solarized-$1)"
}

CACHEF=~/.cache/system-theme/theme

case $1 in
    dark)
        MODE=dark
        ;;
    light)
        MODE=light
        ;;
    "")
        MODE=$(cat $CACHEF 2>/dev/null || echo "dark")
        case $MODE in
            dark) MODE=light;;
            light) MODE=dark;;
        esac
        ;;
    *)
        echo "Unknown theme: $1, should be one of 'dark' or 'light'"
        exit 1
        ;;
esac

mkdir -p $(dirname $CACHEF)
echo $MODE > $CACHEF
wofi_theme $MODE
alacritty_theme $MODE
bat_theme $MODE
emacs_theme $MODE
