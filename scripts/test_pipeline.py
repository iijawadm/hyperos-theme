#!/usr/bin/env python3
"""Automated tests for the HyperOS Android-to-Linux icon conversion pipeline."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from hyperos_converter.converter import convert_decision
from hyperos_converter.mapper import map_assets
from hyperos_converter.metadata import scan_android_metadata
from hyperos_converter.scanner import scan_sources
from hyperos_converter.theme_builder import create_alias_symlinks, generate_index_theme
from hyperos_converter.validator import validate_gnome_shell_css, validate_theme


def run_tests() -> None:
    with tempfile.TemporaryDirectory(prefix="hyperos_test_") as tmp:
        tmp_path = Path(tmp)
        orig_dir = tmp_path / "sources" / "original" / "apps"
        android_dir = tmp_path / "sources" / "android" / "pack1"
        out_theme = tmp_path / "HyperOS-Icons"
        orig_dir.mkdir(parents=True)
        android_dir.mkdir(parents=True)

        # 1. Original SVG icon (must take priority over Android pack for spotify)
        (orig_dir / "spotify.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">'
            '<circle cx="32" cy="32" r="30" fill="#1db954"/></svg>\n',
            encoding="utf-8",
        )

        # 2. Android WebP icon (non-square 200x100 with transparency -> must pad to square, never upscale to 256)
        webp_img = Image.new("RGBA", (200, 100), (0, 120, 255, 200))
        webp_img.save(android_dir / "com.android.chrome.webp", format="WEBP", lossless=True)

        # 3. Android PNG competing for spotify (must NOT overwrite original SVG)
        png_img = Image.new("RGBA", (128, 128), (255, 0, 0, 255))
        png_img.save(android_dir / "com.spotify.music.png", format="PNG")

        # 4. Android appfilter.xml mapping a custom drawable name -> org.telegram.messenger
        tg_img = Image.new("RGBA", (256, 256), (34, 158, 217, 255))
        tg_img.save(android_dir / "ic_my_tg.png", format="PNG")
        (android_dir / "appfilter.xml").write_text(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            "<resources>\n"
            '  <item component="ComponentInfo{org.telegram.messenger/org.telegram.ui.LaunchActivity}" drawable="ic_my_tg" />\n'
            "</resources>\n",
            encoding="utf-8",
        )

        # 5. Unresolved icon (must stay unresolved, never blindly renamed)
        unres_img = Image.new("RGBA", (128, 128), (100, 100, 100, 255))
        unres_img.save(android_dir / "com.example.unknownmobileapp.png", format="PNG")

        specs = [
            {
                "id": "original",
                "label": "Original",
                "path": tmp_path / "sources" / "original",
                "priority": 1,
                "provenance": "original",
                "license_status": "original_author",
            },
            {
                "id": "android",
                "label": "Android Pack",
                "path": tmp_path / "sources" / "android",
                "priority": 2,
                "provenance": "android_mts_pack",
                "license_status": "unverified_third_party",
            },
        ]

        assets, _, _, _ = scan_sources(tmp_path, specs)
        meta = scan_android_metadata([android_dir])
        decisions = map_assets(assets, meta, desktop_apps={})

        by_stem = {d.asset.stem: d for d in decisions}
        assert by_stem["spotify"].status == "mapped"
        assert by_stem["spotify"].method == "original_direct"
        assert by_stem["com.spotify.music"].status == "merged_duplicate", "Android icon must not overwrite original!"
        assert by_stem["com.android.chrome"].canonical_name == "google-chrome"
        assert by_stem["ic_my_tg"].canonical_name == "telegram"
        assert by_stem["ic_my_tg"].method == "appfilter_curated"
        assert by_stem["com.example.unknownmobileapp"].status == "unresolved"

        out_theme.mkdir(parents=True)
        for d in decisions:
            convert_decision(d, out_theme)
        create_alias_symlinks(decisions, out_theme)
        generate_index_theme(out_theme)

        # Verify SVG preserved in scalable/apps
        assert (out_theme / "scalable/apps/spotify.svg").is_file()
        # Verify WebP 200x100 converted up to 128x128 (NOT upscaled to 256x256) with RGBA preserved
        assert (out_theme / "128x128/apps/google-chrome.png").is_file()
        assert not (out_theme / "256x256/apps/google-chrome.png").exists()
        with Image.open(out_theme / "128x128/apps/google-chrome.png") as im:
            assert im.size == (128, 128)
            assert im.mode == "RGBA"
            # Top row should be transparent padding because 200x100 was centered in 128x128
            assert im.getpixel((64, 0))[3] == 0
            assert im.getpixel((64, 64))[3] == 200

        # Verify alias symlinks created
        assert (out_theme / "128x128/apps/org.telegram.desktop.png").is_symlink()

        # Run full Freedesktop validator
        val = validate_theme(out_theme)
        assert val.passed, f"Validation failed: {val.errors}"

        # Verify GNOME Shell CSS passes St CSS transparency/shorthand checks
        css_ok, css_errors = validate_gnome_shell_css(REPO_ROOT / "Hyperos-Dark" / "gnome-shell" / "gnome-shell.css")
        assert css_ok, f"GNOME Shell CSS validation failed: {css_errors}"

        # Verify built theme has HyperOS 3/4 vector folder + inode-directory alias (not broken blank squircle)
        built_folder = REPO_ROOT / "HyperOS-Icons" / "scalable" / "places" / "folder.svg"
        built_dir_alias = REPO_ROOT / "HyperOS-Icons" / "scalable" / "places" / "inode-directory.svg"
        assert built_folder.is_file(), "Missing HyperOS 3/4 scalable/places/folder.svg"
        assert built_dir_alias.is_symlink(), "Missing scalable/places/inode-directory.svg alias"
        assert not (REPO_ROOT / "HyperOS-Icons" / "128x128" / "places" / "folder.png").exists(), "Broken Android squircle folder.png must not exist"

        # Test install.sh and uninstall.sh with --prefix
        install_stage = tmp_path / "stage_icons"
        subprocess.check_call([str(REPO_ROOT / "install.sh"), "--prefix", str(install_stage)])
        assert (install_stage / "HyperOS-Icons" / "index.theme").is_file()
        subprocess.check_call([str(REPO_ROOT / "uninstall.sh"), "--prefix", str(install_stage)])
        assert not (install_stage / "HyperOS-Icons").exists()

    print("ALL PIPELINE & INSTALLER TESTS PASSED!")


if __name__ == "__main__":
    run_tests()
