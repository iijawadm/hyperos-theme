"""High-quality image conversion preserving transparency, aspect ratio, and crisp scaling."""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image

from .config import RASTER_SIZES, STATUS_RASTER_SIZES, SUPPORTED_VECTOR_EXTS
from .mapper import MappingDecision


def resize_preserve_aspect_rgba(img: Image.Image, target_size: int) -> Image.Image:
    """
    Convert to RGBA, scale down with Lanczos preserving aspect ratio,
    and center onto a transparent square canvas of target_size x target_size.
    """
    rgba = img.convert("RGBA")
    w, h = rgba.size
    if w == target_size and h == target_size:
        return rgba

    # Compute aspect-ratio-preserving dimensions
    scale = min(target_size / w, target_size / h)
    new_w = max(1, round(w * scale))
    new_h = max(1, round(h * scale))
    resized = rgba.resize((new_w, new_h), Image.Resampling.LANCZOS)

    if new_w == target_size and new_h == target_size:
        return resized

    canvas = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
    offset_x = (target_size - new_w) // 2
    offset_y = (target_size - new_h) // 2
    canvas.paste(resized, (offset_x, offset_y))
    return canvas


def convert_decision(
    decision: MappingDecision,
    theme_root: Path,
    dry_run: bool = False,
) -> list[Path]:
    """
    Convert a single mapped icon decision into Freedesktop Linux icon theme outputs.
    Returns list of created output file paths.
    """
    if decision.status != "mapped" or not decision.canonical_name or not decision.context:
        return []

    src = decision.asset.path
    ctx = decision.context
    canonical = decision.canonical_name
    created: list[Path] = []

    if src.suffix.lower() in SUPPORTED_VECTOR_EXTS:
        out_dir = theme_root / "scalable" / ctx
        out_file = out_dir / f"{canonical}.svg"
        if not dry_run:
            out_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, out_file)
        created.append(out_file)
        decision.output_files.append(str(out_file.relative_to(theme_root)))
        return created

    sizes = STATUS_RASTER_SIZES if ctx == "status" else RASTER_SIZES

    with Image.open(src) as img:
        img.load()
        src_max = max(img.size)
        # Never upscale blurry pixels beyond source resolution;
        # always generate at least the smallest standard size if source is tiny.
        applicable_sizes = [s for s in sizes if s <= src_max]
        if not applicable_sizes:
            applicable_sizes = [sizes[0]]

        for size in applicable_sizes:
            out_dir = theme_root / f"{size}x{size}" / ctx
            out_file = out_dir / f"{canonical}.png"
            if not dry_run:
                out_dir.mkdir(parents=True, exist_ok=True)
                rendered = resize_preserve_aspect_rgba(img, size)
                rendered.save(out_file, format="PNG", optimize=False, compress_level=6)
            created.append(out_file)
            decision.output_files.append(str(out_file.relative_to(theme_root)))

    return created
