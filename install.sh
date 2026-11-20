#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME_NAME="HyperOS-Icons"
SRC_DIR="$REPO_ROOT/$THEME_NAME"
MODE="user"
APPLY_GNOME=0
CUSTOM_PREFIX=""

usage() {
  cat <<EOF
Usage: ./install.sh [OPTIONS]

Install the HyperOS Linux Icon Theme on Fedora / Ultramarine Linux and other Freedesktop desktops.

Options:
  --user            Install for the current user in ~/.local/share/icons/$THEME_NAME (default)
  --system          Install system-wide in /usr/share/icons/$THEME_NAME (uses sudo if needed)
  --prefix <dir>    Install into a custom icons directory (useful for staging/testing)
  --apply           Set '$THEME_NAME' as the active GNOME icon theme via gsettings (Wayland-safe)
  -h, --help        Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user) MODE="user"; shift ;;
    --system) MODE="system"; shift ;;
    --prefix) CUSTOM_PREFIX="${2:?Missing directory for --prefix}"; MODE="custom"; shift 2 ;;
    --apply) APPLY_GNOME=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ ! -d "$SRC_DIR" || ! -f "$SRC_DIR/index.theme" ]]; then
  echo "Theme build directory '$SRC_DIR' not found. Running ./build.sh first..."
  "$REPO_ROOT/build.sh"
fi

case "$MODE" in
  user)
    DEST_BASE="${XDG_DATA_HOME:-$HOME/.local/share}/icons"
    USE_SUDO=0
    ;;
  system)
    DEST_BASE="/usr/share/icons"
    USE_SUDO=1
    [[ $EUID -eq 0 ]] && USE_SUDO=0
    ;;
  custom)
    DEST_BASE="$CUSTOM_PREFIX"
    USE_SUDO=0
    ;;
esac

DEST_DIR="$DEST_BASE/$THEME_NAME"

run_priv() {
  if [[ "$USE_SUDO" -eq 1 ]]; then
    sudo "$@"
  else
    "$@"
  fi
}

echo "Installing $THEME_NAME -> $DEST_DIR"
run_priv mkdir -p "$DEST_BASE"

# Safely replace only the dedicated HyperOS-Icons theme folder (never unrelated files)
if [[ -e "$DEST_DIR" || -L "$DEST_DIR" ]]; then
  run_priv rm -rf "$DEST_DIR"
fi

run_priv cp -a "$SRC_DIR" "$DEST_DIR"

if [[ "$MODE" == "system" ]]; then
  run_priv chmod -R a+rX "$DEST_DIR"
fi

# Update GTK icon cache if available
for cache_bin in gtk-update-icon-cache gtk4-update-icon-cache; do
  if command -v "$cache_bin" >/dev/null 2>&1; then
    run_priv "$cache_bin" -f -t "$DEST_DIR" >/dev/null 2>&1 || true
    echo "Updated icon cache with $cache_bin."
    break
  fi
done

if [[ "$APPLY_GNOME" -eq 1 ]]; then
  if command -v gsettings >/dev/null 2>&1; then
    gsettings set org.gnome.desktop.interface icon-theme "$THEME_NAME"
    echo "Applied GNOME icon theme: $THEME_NAME"
  else
    echo "Warning: gsettings not found; select '$THEME_NAME' manually in your desktop settings." >&2
  fi
fi

echo "Done. Select 'HyperOS' ($THEME_NAME) in GNOME Tweaks, KDE System Settings, XFCE Appearance, Cinnamon Themes, or MATE Appearance."
