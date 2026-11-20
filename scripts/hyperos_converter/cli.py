"""Command-line interface for the HyperOS Android-to-Linux icon theme converter."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from .config import THEME_DIR_NAME, default_source_specs
from .converter import convert_decision
from .gallery import generate_preview_gallery
from .mapper import map_assets
from .metadata import scan_android_metadata, scan_linux_desktop_entries
from .reporter import write_reports
from .scanner import cleanup_temp_dir, scan_sources
from .theme_builder import create_alias_symlinks, generate_index_theme, update_icon_cache
from .validator import validate_theme


def cmd_build(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    theme_root = Path(args.output).resolve() if args.output else (repo_root / THEME_DIR_NAME)
    reports_dir = repo_root / "reports"

    source_specs = default_source_specs(repo_root)
    if args.extra_source:
        for idx, extra in enumerate(args.extra_source, start=10):
            p = Path(extra).resolve()
            source_specs.append(
                {
                    "id": f"extra-{idx}",
                    "label": f"Extra Source ({p.name})",
                    "path": p,
                    "priority": idx,
                    "provenance": "android_extra_pack",
                    "license_status": "unverified_third_party",
                }
            )

    print(f"[1/7] Scanning icon sources in {repo_root}...")
    assets, exact_dups, visual_dups, temp_dir = scan_sources(repo_root, source_specs)
    try:
        print(
            f"      Found {len(assets)} icon files "
            f"({len(exact_dups)} exact duplicate groups, {len(visual_dups)} visually similar pairs)."
        )

        print("[2/7] Reading Android pack metadata & installed Linux .desktop entries...")
        scan_paths = [s["path"] for s in source_specs if s["path"].exists()]
        if temp_dir and temp_dir.exists():
            scan_paths.append(temp_dir)
        android_meta = scan_android_metadata(scan_paths)
        desktop_apps = {} if args.no_system_desktops else scan_linux_desktop_entries()
        print(
            f"      Parsed {len(android_meta.package_to_drawable)} appfilter entries, "
            f"{len(desktop_apps)} installed Linux .desktop entries."
        )

        print("[3/7] Mapping Android packages to Freedesktop Linux icon names...")
        decisions = map_assets(assets, android_meta, desktop_apps)
        mapped = [d for d in decisions if d.status == "mapped"]
        unresolved = [d for d in decisions if d.status == "unresolved"]
        excluded = [d for d in decisions if d.status == "excluded"]
        merged = [d for d in decisions if d.status == "merged_duplicate"]
        errors = [d for d in decisions if d.status == "error"]
        print(
            f"      Mapped: {len(mapped)} | Merged duplicates: {len(merged)} | "
            f"Excluded helpers: {len(excluded)} | Unresolved: {len(unresolved)} | Errors: {len(errors)}"
        )

        if not args.dry_run and args.clean and theme_root.exists():
            shutil.rmtree(theme_root)
        if not args.dry_run:
            theme_root.mkdir(parents=True, exist_ok=True)

        print(f"[4/7] Converting {len(mapped)} primary icons into {theme_root}...")
        total_out = 0
        for idx, dec in enumerate(mapped, start=1):
            created = convert_decision(dec, theme_root, dry_run=args.dry_run)
            total_out += len(created)
            if idx % 20 == 0 or idx == len(mapped):
                print(f"      Progress: {idx}/{len(mapped)} icons ({total_out} output files)")

        print("[5/7] Creating alias symlinks & generating Freedesktop index.theme...")
        symlink_count = create_alias_symlinks(decisions, theme_root, dry_run=args.dry_run)
        index_path = generate_index_theme(theme_root, dry_run=args.dry_run)
        print(f"      Created {symlink_count} alias symlinks and {index_path.name}.")

        if not args.dry_run:
            cache_ok, cache_msg = update_icon_cache(theme_root)
            print(f"      Cache: {cache_msg}")
            if not cache_ok:
                return 1

        print("[6/7] Generating reports (conversion, unresolved, duplicates, licensing)...")
        if not args.dry_run:
            report_paths = write_reports(
                reports_dir, decisions, exact_dups, visual_dups, android_meta, desktop_apps
            )
            for name, path in report_paths.items():
                print(f"      Wrote {path.relative_to(repo_root)}")

        if not args.skip_gallery and not args.dry_run:
            print("[7/7] Generating searchable HTML preview & comparison gallery...")
            gallery_path = generate_preview_gallery(
                decisions, theme_root, reports_dir / "preview-gallery.html"
            )
            print(f"      Wrote {gallery_path.relative_to(repo_root)}")
        else:
            print("[7/7] Skipped HTML preview gallery.")

        print("\nBuild complete.")
        return 0
    finally:
        cleanup_temp_dir(temp_dir)


def cmd_validate(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    theme_root = Path(args.target).resolve() if args.target else (repo_root / THEME_DIR_NAME)

    print(f"Validating Freedesktop icon theme at: {theme_root}")
    report = validate_theme(theme_root)

    print(f"Checks run: {report.checks_run}")
    for k, v in sorted(report.stats.items()):
        print(f"  - {k}: {v}")

    if report.warnings:
        print(f"\nWarnings ({len(report.warnings)}):")
        for w in report.warnings:
            print(f"  [WARN] {w}")

    if report.errors:
        print(f"\nErrors ({len(report.errors)}):")
        for e in report.errors:
            print(f"  [FAIL] {e}")
        print("\nValidation FAILED.")
        return 1

    print("\nValidation PASSED with 0 errors.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hyperos_converter",
        description="Automated Android HyperOS to Freedesktop Linux Icon Theme Converter",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="Scan, map, convert, build index.theme, and generate reports/gallery")
    p_build.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    p_build.add_argument("--output", help="Output icon theme directory (default: <repo>/HyperOS-Icons)")
    p_build.add_argument("--extra-source", action="append", help="Additional Android icon pack directory or archive root")
    p_build.add_argument("--clean", action="store_true", help="Clean output directory before building")
    p_build.add_argument("--dry-run", action="store_true", help="Simulate conversion without writing files")
    p_build.add_argument("--skip-gallery", action="store_true", help="Skip generating HTML preview gallery")
    p_build.add_argument("--no-system-desktops", action="store_true", help="Do not scan host Linux .desktop entries")
    p_build.set_defaults(func=cmd_build)

    p_val = sub.add_parser("validate", help="Validate generated Linux icon theme")
    p_val.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    p_val.add_argument("--target", help="Icon theme directory to validate (default: <repo>/HyperOS-Icons)")
    p_val.set_defaults(func=cmd_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
