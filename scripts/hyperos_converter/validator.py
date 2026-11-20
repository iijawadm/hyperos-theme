"""Automated validator for Freedesktop Linux Icon Theme compliance and image integrity."""

from __future__ import annotations

import configparser
import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image


VALID_ICON_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


@dataclass
class ValidationReport:
    theme_root: Path
    passed: bool = True
    checks_run: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict[str, int] = field(default_factory=dict)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.passed = False

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)


def validate_theme(theme_root: Path) -> ValidationReport:
    report = ValidationReport(theme_root=theme_root)

    if not theme_root.exists() or not theme_root.is_dir():
        report.add_error(f"Theme directory does not exist: {theme_root}")
        return report

    # 1. Validate index.theme existence and Freedesktop syntax
    report.checks_run += 1
    index_path = theme_root / "index.theme"
    if not index_path.is_file():
        report.add_error("Missing index.theme at theme root")
        return report

    parser = configparser.ConfigParser(interpolation=None, strict=True)
    try:
        parser.read(index_path, encoding="utf-8")
    except Exception as exc:
        report.add_error(f"Failed to parse index.theme: {exc}")
        return report

    if "Icon Theme" not in parser:
        report.add_error("index.theme missing [Icon Theme] section")
        return report

    header = parser["Icon Theme"]
    for req_key in ("Name", "Comment", "Directories"):
        if not header.get(req_key, "").strip():
            report.add_error(f"index.theme [Icon Theme] missing required key: {req_key}")

    declared_dirs = [d.strip() for d in header.get("Directories", "").split(",") if d.strip()]
    report.stats["declared_directories"] = len(declared_dirs)
    if not declared_dirs:
        report.add_error("index.theme Directories= list is empty")

    # 2. Validate every declared directory exists and has a matching section with valid Size/Context/Type
    report.checks_run += 1
    declared_set = set(declared_dirs)
    for rel_dir in declared_dirs:
        full_dir = theme_root / rel_dir
        if not full_dir.is_dir():
            report.add_error(f"Declared directory missing on disk: {rel_dir}")
        if rel_dir not in parser:
            report.add_error(f"Declared directory missing section in index.theme: [{rel_dir}]")
            continue
        sec = parser[rel_dir]
        if not sec.get("Size", "").isdigit():
            report.add_error(f"Section [{rel_dir}] missing valid integer Size=")
        if not sec.get("Context", "").strip():
            report.add_error(f"Section [{rel_dir}] missing Context=")
        dir_type = sec.get("Type", "Threshold")
        if dir_type not in ("Fixed", "Scalable", "Threshold"):
            report.add_error(f"Section [{rel_dir}] has invalid Type={dir_type}")

    # 3. Validate all files & symlinks across theme directories
    report.checks_run += 1
    regular_pngs = 0
    regular_svgs = 0
    symlinks = 0
    broken_symlinks = 0
    transparent_pngs = 0
    naming_issues = 0
    dimension_mismatches = 0

    for root_str, _, filenames in os.walk(theme_root):
        cur_dir = Path(root_str)
        rel_dir_path = cur_dir.relative_to(theme_root)
        rel_dir_str = str(rel_dir_path)
        if rel_dir_str == ".":
            continue

        # Check if a directory containing icons is missing from index.theme
        icon_files = [f for f in filenames if f.endswith((".png", ".svg"))]
        if icon_files and rel_dir_str not in declared_set:
            report.add_warning(f"Directory with icons is not listed in index.theme Directories=: {rel_dir_str}")

        expected_size: int | None = None
        top_part = rel_dir_path.parts[0]
        if "x" in top_part:
            a, b = top_part.split("x", 1)
            if a.isdigit() and b.isdigit() and a == b:
                expected_size = int(a)

        for fname in sorted(icon_files):
            fpath = cur_dir / fname
            stem = fpath.stem

            if not VALID_ICON_NAME_RE.match(stem):
                naming_issues += 1
                report.add_error(f"Invalid Linux icon filename: {rel_dir_str}/{fname}")

            if fpath.is_symlink():
                symlinks += 1
                if not fpath.exists():
                    broken_symlinks += 1
                    report.add_error(f"Broken symlink: {rel_dir_str}/{fname} -> {os.readlink(fpath)}")
                continue

            if fname.endswith(".png"):
                regular_pngs += 1
                try:
                    with Image.open(fpath) as img:
                        img.load()
                        w, h = img.size
                        if expected_size is not None and (w != expected_size or h != expected_size):
                            dimension_mismatches += 1
                            report.add_error(
                                f"Dimension mismatch in {rel_dir_str}/{fname}: expected {expected_size}x{expected_size}, got {w}x{h}"
                            )
                        if "A" in img.getbands():
                            transparent_pngs += 1
                        else:
                            report.add_warning(f"PNG without alpha channel: {rel_dir_str}/{fname}")
                except Exception as exc:
                    report.add_error(f"Corrupted/unreadable PNG {rel_dir_str}/{fname}: {exc}")

            elif fname.endswith(".svg"):
                regular_svgs += 1
                try:
                    tree = ET.parse(fpath)
                    if not tree.getroot().tag.lower().endswith("svg"):
                        report.add_error(f"SVG root is not <svg>: {rel_dir_str}/{fname}")
                except Exception as exc:
                    report.add_error(f"Invalid SVG XML {rel_dir_str}/{fname}: {exc}")

    report.stats.update(
        {
            "regular_pngs": regular_pngs,
            "regular_svgs": regular_svgs,
            "symlinks": symlinks,
            "broken_symlinks": broken_symlinks,
            "transparent_pngs": transparent_pngs,
            "dimension_mismatches": dimension_mismatches,
            "naming_issues": naming_issues,
        }
    )

    # 4. Validate with gtk-update-icon-cache --validate or -f -t
    report.checks_run += 1
    cache_tool = shutil.which("gtk-update-icon-cache") or shutil.which("gtk4-update-icon-cache")
    if cache_tool:
        proc = subprocess.run(
            [cache_tool, "-f", "-t", str(theme_root)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            report.add_error(f"{Path(cache_tool).name} failed: {proc.stderr.strip() or proc.stdout.strip()}")
    else:
        report.add_warning("gtk-update-icon-cache / gtk4-update-icon-cache not installed; skipped cache validation")

    # 5. Check GNOME / Freedesktop runtime recognition readiness
    report.checks_run += 1
    example_icon = header.get("Example", "folder").strip()
    if example_icon:
        found_example = any(
            (theme_root / d / f"{example_icon}{ext}").exists()
            for d in declared_dirs
            for ext in (".png", ".svg")
        )
        if not found_example:
            report.add_warning(f"Example icon '{example_icon}' not found directly in theme (will fall back via Inherits=)")

    return report
