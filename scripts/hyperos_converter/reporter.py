"""Generate structured conversion, unresolved, duplicate, and licensing audit reports."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .mapper import MappingDecision
from .metadata import AndroidPackMetadata, DesktopAppInfo
from .scanner import IconAsset


def write_reports(
    reports_dir: Path,
    decisions: list[MappingDecision],
    exact_duplicates: dict[str, list[IconAsset]],
    visual_duplicates: list[tuple[IconAsset, IconAsset, int]],
    android_meta: AndroidPackMetadata,
    desktop_apps: dict[str, DesktopAppInfo],
) -> dict[str, Path]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    generated: dict[str, Path] = {}

    status_counts = Counter(d.status for d in decisions)
    context_counts = Counter(d.context for d in decisions if d.status == "mapped" and d.context)
    source_counts = Counter(d.asset.source_id for d in decisions)
    license_counts = Counter(d.asset.license_status for d in decisions)

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. Machine-readable conversion-report.json
    json_path = reports_dir / "conversion-report.json"
    payload = {
        "generated_at": now_iso,
        "summary": {
            "total_scanned_files": len(decisions),
            "mapped_primary_icons": status_counts["mapped"],
            "merged_duplicates": status_counts["merged_duplicate"],
            "excluded_helpers": status_counts["excluded"],
            "unresolved": status_counts["unresolved"],
            "errors": status_counts["error"],
            "total_output_files": sum(len(d.output_files) for d in decisions),
            "total_alias_symlinks": sum(len(d.symlink_files) for d in decisions),
            "exact_duplicate_groups": len(exact_duplicates),
            "visual_similar_pairs": len(visual_duplicates),
            "installed_linux_desktop_entries_scanned": len(desktop_apps),
            "by_context": dict(context_counts),
            "by_source": dict(source_counts),
            "by_license_status": dict(license_counts),
        },
        "items": [
            {
                "source_path": d.asset.rel_path,
                "source_id": d.asset.source_id,
                "provenance": d.asset.provenance,
                "license_status": d.asset.license_status,
                "stem": d.asset.stem,
                "format": d.asset.detected_format,
                "dimensions": f"{d.asset.width}x{d.asset.height}" if d.asset.width else "vector",
                "has_alpha": d.asset.has_alpha,
                "sha256": d.asset.sha256[:16],
                "status": d.status,
                "method": d.method,
                "confidence": d.confidence,
                "canonical_name": d.canonical_name,
                "context": d.context,
                "app_name": d.app_name,
                "aliases": d.aliases,
                "matched_desktop_ids": d.matched_desktop_ids,
                "output_files": d.output_files,
                "symlink_count": len(d.symlink_files),
                "reason": d.reason,
            }
            for d in decisions
        ],
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    generated["conversion_json"] = json_path

    # 2. Human-readable conversion-report.md
    md_path = reports_dir / "conversion-report.md"
    mapped_items = [d for d in decisions if d.status == "mapped"]
    md_lines = [
        "# Android-to-Linux Icon Conversion Report",
        "",
        f"Generated: `{now_iso}`",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Total source icon files scanned | {len(decisions)} |",
        f"| Mapped primary Linux icons | {status_counts['mapped']} |",
        f"| Generated icon image files (all sizes) | {sum(len(d.output_files) for d in decisions)} |",
        f"| Generated alias symlinks | {sum(len(d.symlink_files) for d in decisions)} |",
        f"| Merged exact/canonical duplicates | {status_counts['merged_duplicate']} |",
        f"| Excluded theme-pack helper templates | {status_counts['excluded']} |",
        f"| Unresolved icons (not guessed) | {status_counts['unresolved']} |",
        f"| Unreadable / failed files | {status_counts['error']} |",
        f"| Host Linux `.desktop` entries scanned | {len(desktop_apps)} |",
        "",
        "## Mapped Icons by Context",
        "",
        "| Context | Primary Icons |",
        "| --- | ---: |",
    ]
    for ctx, cnt in sorted(context_counts.items()):
        md_lines.append(f"| `{ctx}` | {cnt} |")

    md_lines.extend(
        [
            "",
            "## Mapped Icons Detail",
            "",
            "| Source Asset | Linux Context / Name | Aliases | Resolution | Method | Host `.desktop` Matches |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for d in sorted(mapped_items, key=lambda x: (x.context or "", x.canonical_name or "")):
        dims = f"{d.asset.width}x{d.asset.height}" if d.asset.width else "SVG"
        aliases_str = ", ".join(f"`{a}`" for a in d.aliases[:5])
        if len(d.aliases) > 5:
            aliases_str += f" (+{len(d.aliases) - 5})"
        desktop_str = ", ".join(f"`{x}`" for x in d.matched_desktop_ids[:3]) or "—"
        md_lines.append(
            f"| `{d.asset.rel_path}` | `{d.context}/{d.canonical_name}` | {aliases_str or '—'} | {dims} | `{d.method}` | {desktop_str} |"
        )
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    generated["conversion_md"] = md_path

    # 3. Unresolved icons report (Markdown + CSV)
    unresolved_items = [d for d in decisions if d.status == "unresolved"]
    excluded_items = [d for d in decisions if d.status == "excluded"]

    unres_md = reports_dir / "unresolved-icons.md"
    ulines = [
        "# Unresolved & Excluded Android Icons Report",
        "",
        "Icons listed below were **intentionally not guessed or blindly renamed** because they either lack a verified Linux desktop application equivalent (e.g., regional mobile-only banking, shopping, or carrier apps) or are MIUI/HyperOS launcher template assets.",
        "",
        "To map any icon below in the future, add an entry to `scripts/hyperos_converter/mappings/android_to_linux.json` and re-run `./build.sh`.",
        "",
        f"## Excluded Theme-Pack Helper Templates ({len(excluded_items)})",
        "",
        "| File | Source | Reason |",
        "| --- | --- | --- |",
    ]
    for d in sorted(excluded_items, key=lambda x: x.asset.rel_path):
        ulines.append(f"| `{d.asset.rel_path}` | `{d.asset.source_id}` | {d.reason} |")

    ulines.extend(
        [
            "",
            f"## Unresolved Android Packages ({len(unresolved_items)})",
            "",
            "| Android Package / Stem | Source Path | Format & Size | Reason |",
            "| --- | --- | --- | --- |",
        ]
    )
    for d in sorted(unresolved_items, key=lambda x: x.asset.stem.lower()):
        dims = f"{d.asset.detected_format} {d.asset.width}x{d.asset.height}" if d.asset.width else d.asset.detected_format
        ulines.append(f"| `{d.asset.stem}` | `{d.asset.rel_path}` | {dims} | {d.reason} |")

    unres_md.write_text("\n".join(ulines) + "\n", encoding="utf-8")
    generated["unresolved_md"] = unres_md

    unres_csv = reports_dir / "unresolved-icons.csv"
    with unres_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["stem", "source_path", "source_id", "format", "dimensions", "status", "reason"],
        )
        writer.writeheader()
        for d in sorted(unresolved_items + excluded_items, key=lambda x: (x.status, x.asset.stem.lower())):
            dims = f"{d.asset.width}x{d.asset.height}" if d.asset.width else "vector"
            writer.writerow(
                {
                    "stem": d.asset.stem,
                    "source_path": d.asset.rel_path,
                    "source_id": d.asset.source_id,
                    "format": d.asset.detected_format,
                    "dimensions": dims,
                    "status": d.status,
                    "reason": d.reason,
                }
            )
    generated["unresolved_csv"] = unres_csv

    # 4. Duplicates & visual similarity report
    dup_md = reports_dir / "duplicates-report.md"
    dlines = [
        "# Duplicate & Visually Similar Icons Report",
        "",
        f"- **Exact byte-for-byte duplicate groups (SHA-256)**: {len(exact_duplicates)}",
        f"- **Distinct-byte visually similar pairs (dHash <= 4)**: {len(visual_duplicates)}",
        "",
        "## Visually Similar Pairs (Distinct Bytes)",
        "",
    ]
    if visual_duplicates:
        dlines.extend(["| Icon A | Icon B | Hamming Distance |", "| --- | --- | ---: |"])
        for a, b, dist in sorted(visual_duplicates, key=lambda t: (t[2], t[0].rel_path)):
            dlines.append(f"| `{a.rel_path}` | `{b.rel_path}` | {dist} |")
    else:
        dlines.append("No distinct-byte visually similar pairs detected.")

    dlines.extend(
        [
            "",
            "## Exact Duplicate Groups (SHA-256)",
            "",
            "| SHA-256 (prefix) | Count | Primary Kept | Duplicate Paths |",
            "| --- | ---: | --- | --- |",
        ]
    )
    for sha, group in sorted(exact_duplicates.items(), key=lambda kv: (-len(kv[1]), kv[1][0].rel_path)):
        dups = ", ".join(f"`{a.rel_path}`" for a in group[1:])
        dlines.append(f"| `{sha[:12]}` | {len(group)} | `{group[0].rel_path}` | {dups} |")

    dup_md.write_text("\n".join(dlines) + "\n", encoding="utf-8")
    generated["duplicates_md"] = dup_md

    # 5. Licensing & ownership audit report
    lic_md = reports_dir / "licensing-audit.md"
    llines = [
        "# Asset Provenance & Licensing Audit",
        "",
        "> **Important**: Publicly downloadable Android / HyperOS / MIUI / MTS theme assets are **not** automatically free to redistribute. Review the flagged collections below before publishing or redistributing derived icon themes.",
        "",
        "## Summary by License Status",
        "",
        "| License / Provenance Status | Scanned Files | Action Required |",
        "| --- | ---: | --- |",
        f"| `original_author` (Jawad's original artwork in `sources/original/`) | {license_counts['original_author']} | Safe under repository license chosen by author |",
        f"| `unverified_third_party` (`hyperos3-icons/` & `sources/android/`) | {license_counts['unverified_third_party']} | **Flagged**: Verify original creator & redistribution permission before public release |",
        "",
        "## Embedded Android XML Theme Metadata Found",
        "",
    ]
    if android_meta.theme_credits:
        for info in android_meta.theme_credits:
            llines.append(f"- `{info.get('file')}`: " + ", ".join(f"{k}=`{v}`" for k, v in info.items() if k != "file"))
    else:
        llines.append(
            "No `description.xml` or `theme_values.xml` metadata files were present in the current Android icon directories. "
            "Original theme pack authorship for `hyperos3-icons/` cannot be automatically verified from file metadata alone and is flagged in `CREDITS.md`."
        )

    llines.extend(
        [
            "",
            "## Additional Repository Components Requiring Attribution Review",
            "",
            "- `hyperos icons/`: Based on **Reversal Icon Theme** (GPL-3.0, `AUTHORS` & `COPYING` present) by `yeyushengfan258` / `vinceliuice`, derived from `OSX_ONE` (`unc926`), plus custom modifications by Jawad.",
            "- `hyperos3-icons/`: Android HyperOS 3 / MIUI / MTS-sourced PNG icons — **no license file or embedded metadata included**. Flagged for copyright/redistribution review.",
            "- `font/MiSans_Arabic/` & `font/MiSans_Latin/`: Xiaomi MiSans fonts — verify Xiaomi MiSans license terms before redistribution.",
            "- `hyperos sounds/`: MIUI sound theme (`Name=MIUI`) — no license file present; verify redistribution rights.",
            "- `backgrounds/`: Mixed community/OS wallpapers (including macOS/Xiaomi/anime wallpapers) — no per-file license recorded; verify before redistribution.",
            "- `extenstions/`: 8 third-party GNOME Shell extensions, each retaining its own `LICENSE`/`COPYING` and `metadata.json` (documented in `CREDITS.md`).",
        ]
    )
    lic_md.write_text("\n".join(llines) + "\n", encoding="utf-8")
    generated["licensing_md"] = lic_md

    return generated
