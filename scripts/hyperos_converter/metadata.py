"""Readers for Android icon pack XML metadata and installed Linux .desktop entries."""

from __future__ import annotations

import configparser
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from .config import LINUX_DESKTOP_DIRS


@dataclass
class DesktopAppInfo:
    desktop_id: str
    name: str
    icon: str
    wm_class: str
    categories: list[str] = field(default_factory=list)
    path: str = ""


@dataclass
class AndroidPackMetadata:
    # drawable_name -> list of package names from appfilter.xml
    drawable_to_packages: dict[str, list[str]] = field(default_factory=dict)
    # package_name -> drawable_name
    package_to_drawable: dict[str, str] = field(default_factory=dict)
    # Theme metadata discovered in description.xml / manifest.xml
    theme_credits: list[dict[str, str]] = field(default_factory=list)


def scan_android_metadata(source_paths: Iterable[Path]) -> AndroidPackMetadata:
    """Parse appfilter.xml, description.xml, and manifest.xml if present in source directories."""
    meta = AndroidPackMetadata()
    comp_re = re.compile(r"ComponentInfo\{([^/\s}]+)/")

    for root in source_paths:
        if not root.exists():
            continue
        for xml_file in sorted(root.rglob("*.xml")):
            fname = xml_file.name.lower()
            try:
                tree = ET.parse(xml_file)
                xml_root = tree.getroot()
            except Exception:
                continue

            if fname == "appfilter.xml":
                for elem in xml_root.iter("item"):
                    comp = elem.attrib.get("component", "")
                    drawable = elem.attrib.get("drawable", "").strip()
                    m = comp_re.search(comp)
                    if m and drawable:
                        pkg = m.group(1).strip()
                        meta.drawable_to_packages.setdefault(drawable, []).append(pkg)
                        meta.package_to_drawable[pkg] = drawable

            elif fname in ("description.xml", "theme_values.xml"):
                info = {"file": str(xml_file)}
                for tag in ("title", "author", "designer", "version", "uiVersion", "description"):
                    node = xml_root.find(tag)
                    if node is not None and node.text and node.text.strip():
                        info[tag] = node.text.strip()
                if len(info) > 1:
                    meta.theme_credits.append(info)

    return meta


def scan_linux_desktop_entries(
    desktop_dirs: Iterable[Path] = LINUX_DESKTOP_DIRS,
) -> dict[str, DesktopAppInfo]:
    """Scan installed Linux .desktop files and index them by desktop ID, icon name, and normalized name."""
    apps: dict[str, DesktopAppInfo] = {}
    for ddir in desktop_dirs:
        if not ddir.exists():
            continue
        for desktop_file in sorted(ddir.glob("*.desktop")):
            parser = configparser.ConfigParser(interpolation=None, strict=False)
            try:
                parser.read(desktop_file, encoding="utf-8")
            except Exception:
                continue
            if "Desktop Entry" not in parser:
                continue
            entry = parser["Desktop Entry"]
            if entry.get("NoDisplay", "").lower() == "true":
                continue
            icon = entry.get("Icon", "").strip()
            name = entry.get("Name", "").strip()
            if not icon or "/" in icon:
                continue
            desktop_id = desktop_file.stem
            wm_class = entry.get("StartupWMClass", "").strip()
            cats = [c for c in entry.get("Categories", "").split(";") if c]
            apps[desktop_id] = DesktopAppInfo(
                desktop_id=desktop_id,
                name=name,
                icon=icon,
                wm_class=wm_class,
                categories=cats,
                path=str(desktop_file),
            )
    return apps
