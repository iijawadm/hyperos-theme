"""Merge legacy `hyperos icons/` assets as a clean Priority-3 fallback layer for gaps."""

from __future__ import annotations

import os
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from .config import CONTEXT_MAP
from .mapper import MappingDecision

VALID_ICON_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]*$")

# Map legacy Reversal/`hyperos icons` subdirs (<context>/<subdir>) -> Freedesktop <size_dir>
LEGACY_SIZE_MAP = {
    "16": "16x16",
    "22": "22x22",
    "24": "24x24",
    "32": "32x32",
    "48": "scalable",
    "scalable": "scalable",
    "symbolic": "symbolic",
}


def _is_legacy_base64_wrapper(path: Path) -> bool:
    """Detect old 3-line base64-PNG-in-SVG wrappers created by scripts/import_hyperos3_icons.py."""
    try:
        head = path.read_text(encoding="utf-8", errors="ignore")
        return "data:image/png;base64," in head and len(head.splitlines()) <= 5
    except Exception:
        return False


def _is_valid_svg(path: Path) -> bool:
    try:
        tree = ET.parse(path)
        return tree.getroot().tag.lower().endswith("svg")
    except Exception:
        return False


def merge_legacy_fallback(
    legacy_root: Path,
    theme_root: Path,
    decisions: list[MappingDecision],
    dry_run: bool = False,
) -> dict[str, int]:
    """
    Copy non-conflicting icons & valid relative symlinks from `hyperos icons/` into `theme_root`
    so every missing icon falls back to the classic HyperOS/Reversal collection while all newly
    built HyperOS 3/4 icons always take priority.
    """
    stats = {
        "files_merged": 0,
        "symlinks_merged": 0,
        "skipped_protected": 0,
        "skipped_invalid": 0,
    }
    if not legacy_root.is_dir():
        return stats

    # Build set of (context, stem_lower) protected by Priority 1 (original) and Priority 2 (HyperOS 3 Android)
    protected: set[tuple[str, str]] = set()
    for d in decisions:
        if d.status == "mapped" and d.context and d.canonical_name:
            protected.add((d.context, d.canonical_name.lower()))
            for alias in d.aliases:
                protected.add((d.context, alias.lower()))

    # Two-pass per directory: regular files first, then relative symlinks whose target exists
    for ctx_dir in sorted(legacy_root.iterdir()):
        if not ctx_dir.is_dir() or ctx_dir.is_symlink():
            continue
        ctx = ctx_dir.name
        if ctx not in CONTEXT_MAP:
            continue

        for size_dir in sorted(ctx_dir.iterdir()):
            if not size_dir.is_dir() or size_dir.is_symlink():
                continue
            target_size_name = LEGACY_SIZE_MAP.get(size_dir.name)
            if not target_size_name:
                continue

            is_symbolic = target_size_name == "symbolic"
            dest_dir = theme_root / target_size_name / ctx

            regular_files: list[Path] = []
            symlink_files: list[Path] = []
            for entry in sorted(size_dir.iterdir()):
                if entry.suffix.lower() not in (".svg", ".png"):
                    continue
                if entry.is_symlink():
                    symlink_files.append(entry)
                elif entry.is_file():
                    regular_files.append(entry)

            # Pass 1: Regular files
            for src in regular_files:
                stem = src.stem
                if not VALID_ICON_NAME_RE.match(stem):
                    stats["skipped_invalid"] += 1
                    continue
                if not is_symbolic and (ctx, stem.lower()) in protected:
                    stats["skipped_protected"] += 1
                    continue
                dest = dest_dir / src.name
                if dest.exists() or dest.is_symlink():
                    stats["skipped_protected"] += 1
                    continue
                if src.suffix.lower() == ".svg":
                    if _is_legacy_base64_wrapper(src) or not _is_valid_svg(src):
                        stats["skipped_invalid"] += 1
                        continue
                if not dry_run:
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dest)
                stats["files_merged"] += 1

            # Pass 2: Symlinks (only within-directory relative symlinks whose target exists)
            for src in symlink_files:
                stem = src.stem
                if not VALID_ICON_NAME_RE.match(stem):
                    stats["skipped_invalid"] += 1
                    continue
                if not is_symbolic and (ctx, stem.lower()) in protected:
                    stats["skipped_protected"] += 1
                    continue
                dest = dest_dir / src.name
                if dest.exists() or dest.is_symlink():
                    stats["skipped_protected"] += 1
                    continue
                try:
                    raw_target = os.readlink(src)
                except OSError:
                    stats["skipped_invalid"] += 1
                    continue
                # Resolve symlink chains safely; if pointing to another file in same dir, link to its filename
                resolved = src.resolve()
                if not resolved.is_file():
                    stats["skipped_invalid"] += 1
                    continue
                # Ensure target exists in dest_dir (or copy resolved file if target was outside same dir)
                if "/" not in raw_target and (dest_dir / raw_target).exists():
                    if not dry_run:
                        dest_dir.mkdir(parents=True, exist_ok=True)
                        os.symlink(raw_target, dest)
                    stats["symlinks_merged"] += 1
                elif (dest_dir / resolved.name).exists():
                    if not dry_run:
                        dest_dir.mkdir(parents=True, exist_ok=True)
                        os.symlink(resolved.name, dest)
                    stats["symlinks_merged"] += 1
                else:
                    # Cross-directory valid symlink (e.g. places/16 -> actions/16) — materialize if valid SVG/PNG
                    if resolved.suffix.lower() == ".svg" and (
                        _is_legacy_base64_wrapper(resolved) or not _is_valid_svg(resolved)
                    ):
                        stats["skipped_invalid"] += 1
                        continue
                    if not dry_run:
                        dest_dir.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(resolved, dest)
                    stats["files_merged"] += 1

    return stats
