"""Recursive asset scanner with format detection, SHA-256 deduplication, and perceptual hashing."""

from __future__ import annotations

import hashlib
import shutil
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from PIL import Image

from .config import ARCHIVE_EXTS, DHASH_SIMILARITY_THRESHOLD, SUPPORTED_EXTS, SUPPORTED_VECTOR_EXTS


@dataclass
class IconAsset:
    path: Path
    rel_path: str
    source_id: str
    source_label: str
    priority: int
    provenance: str
    license_status: str
    stem: str
    ext: str
    detected_format: str
    width: int | None
    height: int | None
    has_alpha: bool | None
    sha256: str
    dhash: int | None = None
    hint_context: str | None = None
    duplicate_of: str | None = None
    similar_to: list[str] = field(default_factory=list)
    error: str | None = None


def compute_dhash(img: Image.Image, hash_size: int = 8) -> int:
    """Compute a 64-bit difference hash (dHash) using Pillow only."""
    # Composite onto white background so transparency doesn't produce false noise
    rgba = img.convert("RGBA")
    bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(bg, rgba).convert("L")
    resized = composited.resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = list(resized.getdata())
    bits = 0
    for row in range(hash_size):
        row_start = row * (hash_size + 1)
        for col in range(hash_size):
            left = pixels[row_start + col]
            right = pixels[row_start + col + 1]
            bits = (bits << 1) | (1 if left > right else 0)
    return bits


def hamming_distance(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def inspect_image(path: Path) -> tuple[str, int | None, int | None, bool | None, int | None, str | None]:
    """Inspect an image file and return (format, width, height, has_alpha, dhash, error)."""
    ext = path.suffix.lower()
    if ext in SUPPORTED_VECTOR_EXTS:
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            if not root.tag.lower().endswith("svg"):
                return ("SVG_INVALID", None, None, None, None, "Root XML element is not <svg>")
            return ("SVG", None, None, True, None, None)
        except Exception as exc:
            return ("SVG_INVALID", None, None, None, None, f"Invalid SVG XML: {exc}")

    try:
        with Image.open(path) as img:
            img.load()
            fmt = (img.format or ext.lstrip(".").upper()).upper()
            width, height = img.size
            has_alpha = (
                "A" in img.getbands()
                or img.mode in ("RGBA", "LA", "PA")
                or (img.mode == "P" and "transparency" in img.info)
            )
            dhash = compute_dhash(img)
            return (fmt, width, height, has_alpha, dhash, None)
    except Exception as exc:
        return ("UNREADABLE", None, None, None, None, str(exc))


def infer_context_from_path(rel_path: Path) -> str | None:
    parts = [p.lower() for p in rel_path.parts[:-1]]
    for ctx in ("apps", "actions", "devices", "places", "status", "mimes", "categories", "emblems"):
        if ctx in parts:
            return ctx
    return None


def extract_archives(source_dir: Path, extract_root: Path) -> list[Path]:
    """Safely extract any .mtz or .zip archives found in source_dir into extract_root."""
    extracted_dirs: list[Path] = []
    if not source_dir.exists():
        return extracted_dirs
    for archive in sorted(source_dir.rglob("*")):
        if archive.is_file() and archive.suffix.lower() in ARCHIVE_EXTS:
            target = extract_root / archive.stem
            target.mkdir(parents=True, exist_ok=True)
            try:
                with zipfile.ZipFile(archive, "r") as zf:
                    for member in zf.infolist():
                        # Guard against Zip Slip path traversal
                        member_path = (target / member.filename).resolve()
                        if not str(member_path).startswith(str(target.resolve())):
                            continue
                        zf.extract(member, target)
                # MIUI .mtz archives often contain an inner `icons` zip archive
                inner_icons = target / "icons"
                if inner_icons.is_file() and zipfile.is_zipfile(inner_icons):
                    inner_dir = target / "icons_extracted"
                    inner_dir.mkdir(parents=True, exist_ok=True)
                    with zipfile.ZipFile(inner_icons, "r") as izf:
                        for member in izf.infolist():
                            mpath = (inner_dir / member.filename).resolve()
                            if not str(mpath).startswith(str(inner_dir.resolve())):
                                continue
                            izf.extract(member, inner_dir)
                extracted_dirs.append(target)
            except Exception:
                continue
    return extracted_dirs


def scan_sources(
    repo_root: Path,
    source_specs: Iterable[dict],
) -> tuple[list[IconAsset], dict[str, list[IconAsset]], list[tuple[IconAsset, IconAsset, int]], Path | None]:
    """
    Recursively scan all configured source directories.

    Returns:
      - assets: all discovered IconAsset objects (including duplicates tagged with duplicate_of)
      - exact_duplicates: sha256 -> list of IconAsset with identical bytes (len > 1)
      - visual_duplicates: list of (asset_a, asset_b, hamming_dist) for distinct-byte visually similar icons
      - temp_extract_dir: temporary directory used for archive extraction (caller cleans up), or None
    """
    assets: list[IconAsset] = []
    temp_dir: Path | None = None

    for spec in source_specs:
        src_path: Path = spec["path"]
        if not src_path.exists():
            continue

        scan_roots = [src_path]
        if any(p.is_file() and p.suffix.lower() in ARCHIVE_EXTS for p in src_path.rglob("*")):
            if temp_dir is None:
                temp_dir = Path(tempfile.mkdtemp(prefix="hyperos_mtz_"))
            scan_roots.extend(extract_archives(src_path, temp_dir / spec["id"]))

        for root in scan_roots:
            for file_path in sorted(root.rglob("*")):
                if not file_path.is_file() or file_path.is_symlink():
                    continue
                if file_path.suffix.lower() not in SUPPORTED_EXTS:
                    continue
                # Skip generated mapping / report / preview folders inside source trees
                if any(part in ("mapping", "reports", "__pycache__") for part in file_path.parts):
                    continue

                data = file_path.read_bytes()
                sha256 = hashlib.sha256(data).hexdigest()
                fmt, w, h, has_alpha, dhash, err = inspect_image(file_path)

                try:
                    rel_path = str(file_path.relative_to(repo_root))
                except ValueError:
                    rel_path = f"{spec['id']}/{file_path.relative_to(root)}"

                rel_within_source = file_path.relative_to(root)
                hint_context = infer_context_from_path(rel_within_source)

                assets.append(
                    IconAsset(
                        path=file_path,
                        rel_path=rel_path,
                        source_id=spec["id"],
                        source_label=spec["label"],
                        priority=spec["priority"],
                        provenance=spec["provenance"],
                        license_status=spec["license_status"],
                        stem=file_path.stem,
                        ext=file_path.suffix.lower(),
                        detected_format=fmt,
                        width=w,
                        height=h,
                        has_alpha=has_alpha,
                        sha256=sha256,
                        dhash=dhash,
                        hint_context=hint_context,
                        error=err,
                    )
                )

    # Sort deterministically: priority asc, higher resolution first, shorter path first (prefer root over duplicate subdirs)
    assets.sort(
        key=lambda a: (
            a.priority,
            -(a.width or 0) * (a.height or 0),
            len(Path(a.rel_path).parts),
            a.rel_path.lower(),
        )
    )

    # Exact duplicate detection (by SHA-256)
    by_hash: dict[str, list[IconAsset]] = {}
    for asset in assets:
        by_hash.setdefault(asset.sha256, []).append(asset)

    exact_duplicates: dict[str, list[IconAsset]] = {}
    unique_representatives: list[IconAsset] = []
    for sha, group in by_hash.items():
        primary = group[0]
        unique_representatives.append(primary)
        if len(group) > 1:
            exact_duplicates[sha] = group
            for dup in group[1:]:
                # Only mark as redundant file duplicate if same stem or same source;
                # distinct Android package names sharing identical artwork are still tracked!
                dup.duplicate_of = primary.rel_path

    # Visual similarity detection (dHash) across distinct-byte raster representatives
    visual_duplicates: list[tuple[IconAsset, IconAsset, int]] = []
    raster_reps = [a for a in unique_representatives if a.dhash is not None and a.error is None]
    for i in range(len(raster_reps)):
        a = raster_reps[i]
        for j in range(i + 1, len(raster_reps)):
            b = raster_reps[j]
            dist = hamming_distance(a.dhash, b.dhash)  # type: ignore[arg-type]
            if dist <= DHASH_SIMILARITY_THRESHOLD:
                visual_duplicates.append((a, b, dist))
                a.similar_to.append(b.rel_path)
                b.similar_to.append(a.rel_path)

    return assets, exact_duplicates, visual_duplicates, temp_dir


def cleanup_temp_dir(temp_dir: Path | None) -> None:
    if temp_dir and temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)
