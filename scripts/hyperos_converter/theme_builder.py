"""Freedesktop icon theme directory builder, alias symlink generator, and index.theme writer."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from .config import (
    CONTEXT_MAP,
    THEME_COMMENT,
    THEME_EXAMPLE,
    THEME_INHERITS,
    THEME_NAME,
)
from .mapper import MappingDecision


def create_alias_symlinks(
    decisions: list[MappingDecision],
    theme_root: Path,
    dry_run: bool = False,
) -> int:
    """Create relative symlinks for all aliases inside each generated size/scalable directory."""
    created_count = 0
    for dec in decisions:
        if dec.status != "mapped" or not dec.canonical_name or not dec.aliases:
            continue
        for rel_out in dec.output_files:
            out_path = theme_root / rel_out
            ext = out_path.suffix
            parent = out_path.parent
            target_filename = out_path.name
            for alias in dec.aliases:
                alias_path = parent / f"{alias}{ext}"
                if alias_path == out_path:
                    continue
                # Never overwrite an existing primary icon or existing symlink
                if alias_path.exists() or alias_path.is_symlink():
                    continue
                if not dry_run:
                    os.symlink(target_filename, alias_path)
                dec.symlink_files.append(str(alias_path.relative_to(theme_root)))
                created_count += 1
    return created_count


def discover_populated_dirs(theme_root: Path) -> list[tuple[str, int, str, str]]:
    """
    Scan theme_root and return sorted list of (rel_dir, size, context_label, dir_type).
    Only includes directories that actually contain icon files or symlinks.
    """
    populated: list[tuple[str, int, str, str]] = []
    if not theme_root.exists():
        return populated

    for size_dir in sorted(theme_root.iterdir()):
        if not size_dir.is_dir():
            continue
        name = size_dir.name
        is_scalable = name == "scalable"
        if is_scalable:
            size_val = 128
        elif "x" in name:
            parts = name.split("x", 1)
            if not (parts[0].isdigit() and parts[1].isdigit() and parts[0] == parts[1]):
                continue
            size_val = int(parts[0])
        else:
            continue

        for ctx_dir in sorted(size_dir.iterdir()):
            if not ctx_dir.is_dir():
                continue
            ctx_key = ctx_dir.name
            if ctx_key not in CONTEXT_MAP:
                continue
            has_entries = any(
                (p.is_file() or p.is_symlink()) and p.suffix.lower() in (".png", ".svg")
                for p in ctx_dir.iterdir()
            )
            if not has_entries:
                continue
            rel = f"{name}/{ctx_key}"
            if is_scalable:
                dir_type = "Scalable"
            elif size_val >= 256:
                dir_type = "Scalable"
            else:
                dir_type = "Fixed"
            populated.append((rel, size_val, CONTEXT_MAP[ctx_key], dir_type))

    # Sort nicely: scalable first, then numeric sizes ascending
    populated.sort(key=lambda item: (0 if item[0].startswith("scalable/") else 1, item[1], item[0]))
    return populated


def generate_index_theme(theme_root: Path, dry_run: bool = False) -> Path:
    """Generate a Freedesktop-compliant index.theme file."""
    dirs = discover_populated_dirs(theme_root)
    dir_list = ",".join(d[0] for d in dirs)

    lines = [
        "[Icon Theme]",
        f"Name={THEME_NAME}",
        f"Comment={THEME_COMMENT}",
        f"Inherits={THEME_INHERITS}",
        f"Example={THEME_EXAMPLE}",
        "FollowsColorScheme=true",
        "",
        f"Directories={dir_list}",
        "",
    ]

    for rel, size_val, ctx_label, dir_type in dirs:
        lines.append(f"[{rel}]")
        lines.append(f"Size={size_val}")
        lines.append(f"Context={ctx_label}")
        lines.append(f"Type={dir_type}")
        if dir_type == "Scalable":
            if rel.startswith("scalable/"):
                lines.append("MinSize=16")
                lines.append("MaxSize=512")
            else:
                lines.append("MinSize=128")
                lines.append("MaxSize=512")
        lines.append("")

    index_path = theme_root / "index.theme"
    if not dry_run:
        index_path.write_text("\n".join(lines), encoding="utf-8")
    return index_path


def update_icon_cache(theme_root: Path) -> tuple[bool, str]:
    """Run gtk-update-icon-cache or gtk4-update-icon-cache if installed."""
    for tool in ("gtk-update-icon-cache", "gtk4-update-icon-cache"):
        exe = shutil.which(tool)
        if exe:
            proc = subprocess.run(
                [exe, "-f", "-t", str(theme_root)],
                capture_output=True,
                text=True,
            )
            if proc.returncode == 0:
                return True, f"Updated icon cache using {tool}"
            return False, f"{tool} failed: {proc.stderr.strip() or proc.stdout.strip()}"
    return True, "gtk-update-icon-cache not found; skipped cache generation"
