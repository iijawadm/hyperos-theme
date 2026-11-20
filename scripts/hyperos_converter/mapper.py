"""Intelligent Android-to-Linux icon mapping engine with conflict protection."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .metadata import AndroidPackMetadata, DesktopAppInfo
from .scanner import IconAsset

MAPPINGS_FILE = Path(__file__).resolve().parent / "mappings" / "android_to_linux.json"

# Generic tokens that must never trigger automatic desktop-entry fuzzy matches
GENERIC_TOKENS = {
    "android", "app", "apps", "client", "main", "mainactivity", "activity",
    "service", "ui", "pad", "mobile", "lite", "pro", "plus", "free", "hd",
    "home", "shop", "store", "market", "news", "video", "music", "reader",
    "browser", "health", "wallet", "account", "cloud", "chat", "live", "tv",
    "auto", "bbs", "bike", "buyer", "mall", "bank", "pay", "game", "games",
}


@dataclass
class MappingDecision:
    asset: IconAsset
    status: str  # mapped | merged_duplicate | excluded | unresolved | error
    method: str  # original_direct | curated_exact | appfilter_curated | desktop_exact | helper_excluded | redundant_copy | unresolved | unreadable
    confidence: str  # high | medium | low | none
    canonical_name: str | None = None
    context: str | None = None
    app_name: str | None = None
    aliases: list[str] = field(default_factory=list)
    matched_desktop_ids: list[str] = field(default_factory=list)
    reason: str = ""
    output_files: list[str] = field(default_factory=list)
    symlink_files: list[str] = field(default_factory=list)


def normalize_linux_icon_name(raw: str) -> str:
    """Normalize an icon stem to a safe Freedesktop Linux icon filename (preserving reverse-DNS casing if present)."""
    name = raw.strip()
    if "." in name and not name.startswith("."):
        # Preserve standard reverse-DNS desktop IDs like org.gnome.Nautilus
        cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-.")
        return cleaned or "unknown-icon"
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", name).strip("-").lower()
    return cleaned or "unknown-icon"


def load_curated_mappings(path: Path = MAPPINGS_FILE) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_desktop_indexes(
    desktop_apps: dict[str, DesktopAppInfo],
) -> tuple[dict[str, DesktopAppInfo], dict[str, list[DesktopAppInfo]]]:
    by_id_lower: dict[str, DesktopAppInfo] = {}
    by_icon_lower: dict[str, list[DesktopAppInfo]] = {}
    for did, info in desktop_apps.items():
        by_id_lower[did.lower()] = info
        by_icon_lower.setdefault(info.icon.lower(), []).append(info)
    return by_id_lower, by_icon_lower


def map_assets(
    assets: list[IconAsset],
    android_meta: AndroidPackMetadata,
    desktop_apps: dict[str, DesktopAppInfo],
    curated_path: Path = MAPPINGS_FILE,
) -> list[MappingDecision]:
    """Map scanned assets to Freedesktop Linux icon names with strict conflict protection."""
    curated = load_curated_mappings(curated_path)
    exclude_helpers: dict[str, str] = curated.get("exclude_helpers", {})
    curated_apps: dict[str, dict] = curated.get("apps", {})
    curated_status: dict[str, dict] = curated.get("status", {})

    desktop_by_id, desktop_by_icon = build_desktop_indexes(desktop_apps)

    # Track claimed (context, canonical_name) -> MappingDecision to prevent blind overwrites
    claimed_targets: dict[tuple[str, str], MappingDecision] = {}
    # Track already-processed (source_id, stem, sha256) to skip exact redundant copies in subdirs
    seen_exact_stems: set[tuple[str, str, str]] = set()

    decisions: list[MappingDecision] = []

    for asset in assets:
        # 1. Unreadable / corrupted source file
        if asset.error:
            decisions.append(
                MappingDecision(
                    asset=asset,
                    status="error",
                    method="unreadable",
                    confidence="none",
                    reason=f"Source image unreadable: {asset.error}",
                )
            )
            continue

        # 2. Skip exact redundant file copies of the same stem within the same source pack
        # (e.g., hyperos3-icons/apps/128/com.spotify.music.png duplicating hyperos3-icons/com.spotify.music.png)
        dedup_key = (asset.source_id, asset.stem, asset.sha256)
        if dedup_key in seen_exact_stems:
            decisions.append(
                MappingDecision(
                    asset=asset,
                    status="merged_duplicate",
                    method="redundant_copy",
                    confidence="high",
                    reason=f"Exact byte-for-byte duplicate of {asset.duplicate_of or asset.stem} in same source pack",
                )
            )
            continue
        seen_exact_stems.add(dedup_key)

        # 3. Original artwork by Jawad (highest priority, preserved directly)
        if asset.provenance == "original":
            ctx = asset.hint_context or "apps"
            canonical = normalize_linux_icon_name(asset.stem)
            key = (ctx, canonical)
            if key in claimed_targets:
                decisions.append(
                    MappingDecision(
                        asset=asset,
                        status="merged_duplicate",
                        method="original_conflict",
                        confidence="high",
                        canonical_name=canonical,
                        context=ctx,
                        reason=f"Target {ctx}/{canonical} already claimed by {claimed_targets[key].asset.rel_path}",
                    )
                )
                continue
            dec = MappingDecision(
                asset=asset,
                status="mapped",
                method="original_direct",
                confidence="high",
                canonical_name=canonical,
                context=ctx,
                app_name=asset.stem,
                reason="Original HyperOS-inspired artwork preserved directly",
            )
            claimed_targets[key] = dec
            decisions.append(dec)
            continue

        # 4. Excluded Android theme-pack helper templates (masks, patterns, overlays)
        if asset.stem in exclude_helpers:
            decisions.append(
                MappingDecision(
                    asset=asset,
                    status="excluded",
                    method="helper_excluded",
                    confidence="high",
                    reason=exclude_helpers[asset.stem],
                )
            )
            continue

        # 5. Curated exact mapping (apps or status) — directly or via Android appfilter.xml
        entry = curated_apps.get(asset.stem) or curated_status.get(asset.stem)
        method = "curated_exact"
        if entry is None and asset.stem in android_meta.drawable_to_packages:
            for pkg in android_meta.drawable_to_packages[asset.stem]:
                entry = curated_apps.get(pkg) or curated_status.get(pkg)
                if entry is not None:
                    method = "appfilter_curated"
                    break

        if entry is not None:
            canonical = normalize_linux_icon_name(entry["icon"])
            ctx = entry.get("context") or asset.hint_context or "apps"
            aliases = [normalize_linux_icon_name(a) for a in entry.get("aliases", []) if a and a != canonical]
            app_name = entry.get("app_name", canonical)

            # Check installed Linux .desktop entries that match canonical or aliases
            matched_desktops: list[str] = []
            for candidate in [canonical, *aliases]:
                for dinfo in desktop_by_icon.get(candidate.lower(), []):
                    if dinfo.desktop_id not in matched_desktops:
                        matched_desktops.append(dinfo.desktop_id)
                if candidate.lower() in desktop_by_id:
                    dinfo = desktop_by_id[candidate.lower()]
                    if dinfo.desktop_id not in matched_desktops:
                        matched_desktops.append(dinfo.desktop_id)
                    # Add the desktop entry's Icon= as an alias if it's safe and not already listed
                    norm_icon = normalize_linux_icon_name(dinfo.icon)
                    if norm_icon != canonical and norm_icon not in aliases:
                        aliases.append(norm_icon)

            key = (ctx, canonical)
            if key in claimed_targets:
                owner = claimed_targets[key]
                # Merge any extra aliases onto the primary owner without overwriting the primary icon
                for al in aliases:
                    if al != owner.canonical_name and al not in owner.aliases:
                        owner.aliases.append(al)
                for md in matched_desktops:
                    if md not in owner.matched_desktop_ids:
                        owner.matched_desktop_ids.append(md)
                decisions.append(
                    MappingDecision(
                        asset=asset,
                        status="merged_duplicate",
                        method=method,
                        confidence="high",
                        canonical_name=canonical,
                        context=ctx,
                        app_name=app_name,
                        aliases=aliases,
                        matched_desktop_ids=matched_desktops,
                        reason=f"Mapped to {ctx}/{canonical}, which is already provided by {owner.asset.rel_path}",
                    )
                )
                continue

            dec = MappingDecision(
                asset=asset,
                status="mapped",
                method=method,
                confidence="high",
                canonical_name=canonical,
                context=ctx,
                app_name=app_name,
                aliases=aliases,
                matched_desktop_ids=matched_desktops,
                reason=f"Verified Android-to-Linux mapping ({asset.stem} -> {ctx}/{canonical})",
            )
            claimed_targets[key] = dec
            decisions.append(dec)
            continue

        # 6. Direct installed Linux .desktop reverse-DNS or exact icon-name match (strict guard)
        stem_lower = asset.stem.lower()
        desktop_match: DesktopAppInfo | None = None
        if stem_lower in desktop_by_id:
            desktop_match = desktop_by_id[stem_lower]
        elif stem_lower in desktop_by_icon and stem_lower not in GENERIC_TOKENS and "." not in stem_lower:
            desktop_match = desktop_by_icon[stem_lower][0]

        if desktop_match is not None:
            canonical = normalize_linux_icon_name(desktop_match.icon)
            ctx = asset.hint_context or "apps"
            key = (ctx, canonical)
            if key in claimed_targets:
                decisions.append(
                    MappingDecision(
                        asset=asset,
                        status="merged_duplicate",
                        method="desktop_exact",
                        confidence="medium",
                        canonical_name=canonical,
                        context=ctx,
                        app_name=desktop_match.name,
                        matched_desktop_ids=[desktop_match.desktop_id],
                        reason=f"Matched installed .desktop {desktop_match.desktop_id}, already provided by {claimed_targets[key].asset.rel_path}",
                    )
                )
                continue
            dec = MappingDecision(
                asset=asset,
                status="mapped",
                method="desktop_exact",
                confidence="medium",
                canonical_name=canonical,
                context=ctx,
                app_name=desktop_match.name,
                matched_desktop_ids=[desktop_match.desktop_id],
                reason=f"Matched installed Linux desktop entry {desktop_match.desktop_id} (Icon={desktop_match.icon})",
            )
            claimed_targets[key] = dec
            decisions.append(dec)
            continue

        # 7. Unresolved — do NOT guess or blindly rename
        decisions.append(
            MappingDecision(
                asset=asset,
                status="unresolved",
                method="unresolved",
                confidence="none",
                reason="No verified Linux desktop equivalent or installed .desktop match found",
            )
        )

    return decisions
