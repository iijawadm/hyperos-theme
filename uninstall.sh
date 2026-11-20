#!/usr/bin/env bash
set -euo pipefail

THEME_NAME="HyperOS-Icons"
MODE="user"
CUSTOM_PREFIX=""

usage() {
  cat <<EOF
Usage: ./uninstall.sh [OPTIONS]

Remove the installed HyperOS Linux Icon Theme cleanly.

Options:
  --user            Remove from ~/.local/share/icons/$THEME_NAME (default)
  --system          Remove from /usr/share/icons/$THEME_NAME (uses sudo if needed)
  --all             Remove from both user and system icon directories
  --prefix <dir>    Remove from a custom icons directory
  -h, --help        Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user) MODE="user"; shift ;;
    --system) MODE="system"; shift ;;
    --all) MODE="all"; shift ;;
    --prefix) CUSTOM_PREFIX="${2:?Missing directory for --prefix}"; MODE="custom"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

remove_target() {
  local base="$1"
  local use_sudo="$2"
  local target="$base/$THEME_NAME"
  if [[ -e "$target" || -L "$target" ]]; then
    echo "Removing $target"
    if [[ "$use_sudo" -eq 1 && $EUID -ne 0 ]]; then
      sudo rm -rf "$target"
    else
      rm -rf "$target"
    fi
  else
    echo "Not installed at $target (skipping)"
  fi
}

case "$MODE" in
  user)
    remove_target "${XDG_DATA_HOME:-$HOME/.local/share}/icons" 0
    ;;
  system)
    remove_target "/usr/share/icons" 1
    ;;
  all)
    remove_target "${XDG_DATA_HOME:-$HOME/.local/share}/icons" 0
    remove_target "/usr/share/icons" 1
    ;;
  custom)
    remove_target "$CUSTOM_PREFIX" 0
    ;;
esac

# If GNOME is currently using HyperOS-Icons, safely reset to Adwaita (skip for --prefix staging tests)
if [[ "$MODE" != "custom" ]] && command -v gsettings >/dev/null 2>&1; then
  current="$(gsettings get org.gnome.desktop.interface icon-theme 2>/dev/null || true)"
  if [[ "$current" == "'$THEME_NAME'" ]]; then
    gsettings set org.gnome.desktop.interface icon-theme "Adwaita"
    echo "Reset GNOME icon-theme from '$THEME_NAME' back to 'Adwaita'."
  fi
fi

echo "Uninstall complete."
