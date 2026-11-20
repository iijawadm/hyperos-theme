#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

find_python_with_pillow() {
  for py in "${PYTHON_BIN:-}" "$REPO_ROOT/.venv/bin/python3" /usr/bin/python3 "$(command -v python3 || true)"; do
    if [[ -n "$py" && -x "$py" ]]; then
      if "$py" -c "import PIL" >/dev/null 2>&1; then
        echo "$py"
        return 0
      fi
    fi
  done
  return 1
}

PYTHON="$(find_python_with_pillow || true)"
if [[ -z "$PYTHON" ]]; then
  echo "Error: Python 3 with Pillow (PIL) is required." >&2
  echo "On Fedora / Ultramarine Linux, install it with:" >&2
  echo "  sudo dnf install python3-pillow" >&2
  exit 1
fi

export PYTHONPATH="$REPO_ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}"
"$PYTHON" -m hyperos_converter.cli validate --repo-root "$REPO_ROOT" "$@"

echo ""
echo "=== Desktop Environment Recognition Check ==="
if [[ -n "${XDG_CURRENT_DESKTOP:-}" ]]; then
  echo "Detected desktop: ${XDG_CURRENT_DESKTOP} (session: ${XDG_SESSION_TYPE:-unknown})"
else
  echo "No active graphical session detected (automated validation only)."
fi

if command -v gsettings >/dev/null 2>&1; then
  current_theme="$(gsettings get org.gnome.desktop.interface icon-theme 2>/dev/null || echo 'unavailable')"
  echo "Current GNOME icon-theme setting: ${current_theme}"
fi
