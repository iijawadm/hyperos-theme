"""Configuration constants and Freedesktop specification definitions."""

from pathlib import Path

THEME_NAME = "HyperOS"
THEME_DIR_NAME = "HyperOS-Icons"
THEME_COMMENT = "HyperOS-inspired Freedesktop Linux icon theme converted from Android HyperOS assets and original artwork."
THEME_INHERITS = "Adwaita,hicolor"
THEME_EXAMPLE = "folder"

# Standard Freedesktop raster sizes
RASTER_SIZES = (16, 24, 32, 48, 64, 96, 128, 256)
STATUS_RASTER_SIZES = (16, 24, 32, 48, 64)

# Context directory names -> Freedesktop Context field values
CONTEXT_MAP = {
    "apps": "Applications",
    "actions": "Actions",
    "animations": "Animations",
    "devices": "Devices",
    "places": "Places",
    "status": "Status",
    "mimes": "MimeTypes",
    "categories": "Categories",
    "emblems": "Emblems",
}

SUPPORTED_RASTER_EXTS = {".png", ".webp", ".jpg", ".jpeg", ".bmp", ".ico"}
SUPPORTED_VECTOR_EXTS = {".svg"}
SUPPORTED_EXTS = SUPPORTED_RASTER_EXTS | SUPPORTED_VECTOR_EXTS
ARCHIVE_EXTS = {".mtz", ".zip"}

# Visual similarity threshold (Hamming distance out of 64-bit dHash; <= 4 is visually near-identical)
DHASH_SIMILARITY_THRESHOLD = 4

# Default Linux desktop entry directories
LINUX_DESKTOP_DIRS = (
    Path("/usr/share/applications"),
    Path("/usr/local/share/applications"),
    Path.home() / ".local/share/applications",
    Path("/var/lib/flatpak/exports/share/applications"),
    Path.home() / ".local/share/flatpak/exports/share/applications",
    Path("/var/lib/snapd/desktop/applications"),
)

# Default source definitions (ordered by priority: lower number = higher priority)
def default_source_specs(repo_root: Path) -> list[dict]:
    return [
        {
            "id": "original",
            "label": "Original HyperOS-Inspired Artwork (Jawad)",
            "path": repo_root / "sources" / "original",
            "priority": 1,
            "provenance": "original",
            "license_status": "original_author",
        },
        {
            "id": "hyperos3-icons",
            "label": "HyperOS 3 Android Icon Pack (hyperos3-icons/)",
            "path": repo_root / "hyperos3-icons",
            "priority": 2,
            "provenance": "android_hyperos_pack",
            "license_status": "unverified_third_party",
        },
        {
            "id": "android-packs",
            "label": "Additional Android / MTS Icon Packs (sources/android/)",
            "path": repo_root / "sources" / "android",
            "priority": 3,
            "provenance": "android_mts_pack",
            "license_status": "unverified_third_party",
        },
    ]
