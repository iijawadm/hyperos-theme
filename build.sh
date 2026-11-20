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
exec "$PYTHON" -m hyperos_converter.cli build --repo-root "$REPO_ROOT" --clean "$@"
