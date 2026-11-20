#!/usr/bin/env python3
"""Generate clean, original Xiaomi HyperOS 3/4 style SVG place & MIME icons into sources/original/."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PLACES_DIR = REPO_ROOT / "sources" / "original" / "places"
MIMES_DIR = REPO_ROOT / "sources" / "original" / "mimes"


def make_folder_svg(
    glyph_markup: str = "",
    back_top: str = "#FFB938",
    back_bot: str = "#E67E17",
    front_top: str = "#FFD05B",
    front_mid: str = "#FFA229",
    front_bot: str = "#F07B16",
    tab_color: str = "#F39C1F",
    open_flap: bool = False,
) -> str:
    """Create a crisp 64x64 Xiaomi HyperOS 3/4 squircle-rounded frosted glass folder SVG."""
    front_y = 24.5 if open_flap else 20.5
    front_h = 31.5 if open_flap else 35.5
    front_path = (
        f"M 11.5,{front_y} H 52.5 C 56.6,{front_y} 59.5,{front_y + 2.9} 59.5,{front_y + 7.0} "
        f"L 58.2,49.0 C 58.0,53.2 54.8,56.0 50.6,56.0 H 13.4 C 9.2,56.0 6.0,53.2 5.8,49.0 "
        f"L 4.5,{front_y + 7.0} C 4.5,{front_y + 2.9} 7.4,{front_y} 11.5,{front_y} Z"
        if open_flap
        else f"M 11.5,{front_y} H 52.5 C 56.4,{front_y} 59.0,{front_y + 2.6} 59.0,{front_y + 6.5} "
        f"V 48.5 C 59.0,52.8 55.8,56.0 51.5,56.0 H 12.5 C 8.2,56.0 5.0,52.8 5.0,48.5 "
        f"V {front_y + 6.5} C 5.0,{front_y + 2.6} 7.6,{front_y} 11.5,{front_y} Z"
    )
    paper_peek = (
        '<rect x="11" y="16" width="42" height="14" rx="4" fill="#FFFFFF" fill-opacity="0.82"/>'
        if open_flap
        else '<rect x="10.5" y="17.5" width="43" height="6" rx="3" fill="#FFF8E7" fill-opacity="0.42"/>'
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
  <defs>
    <linearGradient id="backGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{back_top}"/>
      <stop offset="100%" stop-color="{back_bot}"/>
    </linearGradient>
    <linearGradient id="frontGrad" x1="15%" y1="0%" x2="85%" y2="100%">
      <stop offset="0%" stop-color="{front_top}"/>
      <stop offset="52%" stop-color="{front_mid}"/>
      <stop offset="100%" stop-color="{front_bot}"/>
    </linearGradient>
    <linearGradient id="glassSheen" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.34"/>
      <stop offset="42%" stop-color="#FFFFFF" stop-opacity="0.06"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0.06"/>
    </linearGradient>
    <filter id="dropShadow" x="-10%" y="-10%" width="120%" height="125%">
      <feDropShadow dx="0" dy="2" stdDeviation="1.8" flood-color="#000000" flood-opacity="0.24"/>
    </filter>
  </defs>
  <g filter="url(#dropShadow)">
    <!-- Back plate with rounded HyperOS tab -->
    <path d="M 11.5,10.5 H 24.8 C 27.2,10.5 29.0,11.6 30.6,13.6 L 32.2,15.5 H 52.5 C 56.2,15.5 58.8,18.1 58.8,21.8 V 48.0 C 58.8,52.4 55.6,55.5 51.2,55.5 H 12.8 C 8.4,55.5 5.2,52.4 5.2,48.0 V 16.8 C 5.2,13.1 7.8,10.5 11.5,10.5 Z" fill="url(#backGrad)"/>
    <!-- Subtle inner sheet / HyperOS depth layer -->
    {paper_peek}
    <!-- Front rounded squircle flap -->
    <path d="{front_path}" fill="url(#frontGrad)"/>
    <!-- Frosted specular sheen -->
    <path d="{front_path}" fill="url(#glassSheen)"/>
    <!-- Crisp top rim highlight -->
    <path d="M 11.5,{front_y + 0.6} H 52.5" stroke="#FFFFFF" stroke-opacity="0.45" stroke-width="1.1" stroke-linecap="round" fill="none"/>
  </g>
  {glyph_markup}
</svg>
'''


def make_trash_svg(full: bool = False) -> str:
    accent = "#3B9EFF" if full else "#9CA8BA"
    lid_top = "#4DA6FF" if full else "#C9D3E0"
    body_top = "#334054" if full else "#3A4250"
    body_bot = "#1F2633" if full else "#252B36"
    papers = (
        '''
  <path d="M 21,21 L 27,13 L 36,19 L 30,23 Z" fill="#FFFFFF" fill-opacity="0.9"/>
  <path d="M 33,19 L 41,14 L 46,21 L 36,23 Z" fill="#CFE6FF" fill-opacity="0.92"/>'''
        if full
        else ""
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{body_top}"/>
      <stop offset="100%" stop-color="{body_bot}"/>
    </linearGradient>
    <linearGradient id="rim" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0.02"/>
    </linearGradient>
  </defs>
  <rect x="6" y="6" width="52" height="52" rx="14" fill="url(#bg)" stroke="#FFFFFF" stroke-opacity="0.14" stroke-width="1.2"/>
  <rect x="6" y="6" width="52" height="52" rx="14" fill="url(#rim)"/>
  {papers}
  <!-- Trash bin body -->
  <path d="M 20,24 H 44 L 41.6,47.2 C 41.4,49.4 39.6,51 37.4,51 H 26.6 C 24.4,51 22.6,49.4 22.4,47.2 Z" fill="#FFFFFF" fill-opacity="0.14" stroke="{lid_top}" stroke-width="2" stroke-linejoin="round"/>
  <path d="M 17,22.5 H 47" stroke="{lid_top}" stroke-width="2.6" stroke-linecap="round"/>
  <path d="M 27,18.5 C 27,16.8 28.4,15.5 30,15.5 H 34 C 35.6,15.5 37,16.8 37,18.5" fill="none" stroke="{lid_top}" stroke-width="2.2" stroke-linecap="round"/>
  <line x1="27.5" y1="30" x2="28.3" y2="45" stroke="{accent}" stroke-width="2.2" stroke-linecap="round"/>
  <line x1="32" y1="30" x2="32" y2="45" stroke="{accent}" stroke-width="2.2" stroke-linecap="round"/>
  <line x1="36.5" y1="30" x2="35.7" y2="45" stroke="{accent}" stroke-width="2.2" stroke-linecap="round"/>
</svg>
'''


def make_mime_svg(badge_text: str, accent_top: str, accent_bot: str, inner_icon: str = "") -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
  <defs>
    <linearGradient id="cardBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2D3442"/>
      <stop offset="100%" stop-color="#1E232E"/>
    </linearGradient>
    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{accent_top}"/>
      <stop offset="100%" stop-color="{accent_bot}"/>
    </linearGradient>
    <filter id="sh" x="-10%" y="-10%" width="120%" height="125%">
      <feDropShadow dx="0" dy="2" stdDeviation="1.6" flood-color="#000000" flood-opacity="0.28"/>
    </filter>
  </defs>
  <g filter="url(#sh)">
    <path d="M 16,6 H 39 L 52,19 V 51 C 52,54.9 48.9,58 45,58 H 16 C 12.1,58 9,54.9 9,51 V 13 C 9,9.1 12.1,6 16,6 Z" fill="url(#cardBg)" stroke="#FFFFFF" stroke-opacity="0.14" stroke-width="1.2"/>
    <path d="M 39,6 V 15 C 39,17.2 40.8,19 43,19 H 52 Z" fill="#FFFFFF" fill-opacity="0.14"/>
  </g>
  {inner_icon}
  <rect x="14" y="40" width="33" height="12" rx="6" fill="url(#accentGrad)"/>
  <text x="30.5" y="48.8" text-anchor="middle" font-family="Inter, MiSans, sans-serif" font-size="8.2" font-weight="700" fill="#FFFFFF" letter-spacing="0.4">{badge_text}</text>
</svg>
'''


def main() -> None:
    PLACES_DIR.mkdir(parents=True, exist_ok=True)
    MIMES_DIR.mkdir(parents=True, exist_ok=True)

    # Subtle centered frosted-white glyph styling on HyperOS golden-amber folders
    def glyph_group(body: str) -> str:
        return f'<g fill="none" stroke="#FFFFFF" stroke-opacity="0.90" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">{body}</g>'

    folders = {
        "folder.svg": make_folder_svg(),
        "folder-open.svg": make_folder_svg(open_flap=True),
        "folder-drag-accept.svg": make_folder_svg(
            open_flap=True,
            back_top="#4CA8FF",
            back_bot="#1E6BF0",
            front_top="#67B8FF",
            front_mid="#2B85FF",
            front_bot="#1A65E6",
        ),
        "folder-home.svg": make_folder_svg(
            glyph_group(
                '<path d="M 23,38.5 L 32,30.5 L 41,38.5"/>'
                '<path d="M 25.5,36.8 V 45.5 H 38.5 V 36.8"/>'
            )
        ),
        "folder-desktop.svg": make_folder_svg(
            glyph_group(
                '<rect x="22" y="30.5" width="20" height="13.5" rx="2.5"/>'
                '<line x1="28" y1="47.5" x2="36" y2="47.5"/>'
                '<line x1="32" y1="44" x2="32" y2="47.5"/>'
            )
        ),
        "folder-download.svg": make_folder_svg(
            glyph_group(
                '<line x1="32" y1="29.5" x2="32" y2="42.5"/>'
                '<polyline points="26.5,37.5 32,43 37.5,37.5"/>'
                '<line x1="24.5" y1="46.5" x2="39.5" y2="46.5"/>'
            )
        ),
        "folder-documents.svg": make_folder_svg(
            glyph_group(
                '<rect x="24" y="29.5" width="16" height="18" rx="2.5"/>'
                '<line x1="28" y1="35" x2="36" y2="35"/>'
                '<line x1="28" y1="39.5" x2="36" y2="39.5"/>'
                '<line x1="28" y1="43.5" x2="33" y2="43.5"/>'
            )
        ),
        "folder-music.svg": make_folder_svg(
            glyph_group(
                '<path d="M 28,43.5 V 32 L 39,29.8 V 41.5"/>'
                '<circle cx="25.5" cy="44" r="2.6" fill="#FFFFFF" fill-opacity="0.9" stroke="none"/>'
                '<circle cx="36.5" cy="42" r="2.6" fill="#FFFFFF" fill-opacity="0.9" stroke="none"/>'
            )
        ),
        "folder-pictures.svg": make_folder_svg(
            glyph_group(
                '<rect x="22.5" y="30.5" width="19" height="15.5" rx="2.8"/>'
                '<circle cx="28" cy="35.5" r="1.6" fill="#FFFFFF" fill-opacity="0.9" stroke="none"/>'
                '<polyline points="23.5,44 29.5,38.5 33.5,42 36.8,39 40.8,44"/>'
            )
        ),
        "folder-videos.svg": make_folder_svg(
            glyph_group(
                '<rect x="22" y="31" width="20" height="15" rx="3"/>'
                '<polygon points="30,35.2 36.2,38.5 30,41.8" fill="#FFFFFF" fill-opacity="0.92" stroke="none"/>'
            )
        ),
        "folder-publicshare.svg": make_folder_svg(
            glyph_group(
                '<circle cx="32" cy="34.5" r="3.2"/>'
                '<path d="M 25,46 C 25.6,42.2 28.4,40.5 32,40.5 C 35.6,40.5 38.4,42.2 39,46"/>'
            )
        ),
        "folder-templates.svg": make_folder_svg(
            glyph_group(
                '<rect x="24" y="30" width="16" height="17" rx="2.5" stroke-dasharray="3.5 2.5"/>'
            )
        ),
        "folder-recent.svg": make_folder_svg(
            glyph_group(
                '<circle cx="32" cy="38.5" r="7.5"/>'
                '<polyline points="32,34.5 32,38.8 35.5,40.8"/>'
            )
        ),
        "folder-remote.svg": make_folder_svg(
            glyph_group(
                '<circle cx="32" cy="38.5" r="7.5"/>'
                '<ellipse cx="32" cy="38.5" rx="3.4" ry="7.5"/>'
                '<line x1="24.8" y1="38.5" x2="39.2" y2="38.5"/>'
            ),
            back_top="#4CA8FF",
            back_bot="#1E6BF0",
            front_top="#67B8FF",
            front_mid="#2B85FF",
            front_bot="#1A65E6",
        ),
        "folder-bookmarks.svg": make_folder_svg(
            glyph_group(
                '<polygon points="32,30.5 34.4,35.4 39.8,36.2 35.9,40 36.8,45.3 32,42.8 27.2,45.3 28.1,40 24.2,36.2 29.6,35.4" fill="#FFFFFF" fill-opacity="0.9" stroke="none"/>'
            )
        ),
    }

    for fname, content in folders.items():
        (PLACES_DIR / fname).write_text(content, encoding="utf-8")

    mimes = {
        "text-x-generic.svg": make_mime_svg(
            "TXT",
            "#4CA8FF",
            "#2B7BFF",
            '<g stroke="#9EB0C9" stroke-width="2.2" stroke-linecap="round">'
            '<line x1="16" y1="22" x2="34" y2="22"/>'
            '<line x1="16" y1="28" x2="43" y2="28"/>'
            '<line x1="16" y1="34" x2="38" y2="34"/>'
            "</g>",
        ),
        "application-pdf.svg": make_mime_svg(
            "PDF",
            "#FF6B6B",
            "#E03131",
            '<path d="M 18,32 C 22,22 28,22 31,32 C 34,26 40,26 42,32" fill="none" stroke="#FF8787" stroke-width="2.4" stroke-linecap="round"/>',
        ),
        "image-x-generic.svg": make_mime_svg(
            "IMG",
            "#38D9A9",
            "#0CA678",
            '<circle cx="22" cy="24" r="3" fill="#63E6BE"/>'
            '<polyline points="15,35 23,27 29,32 35,26 44,35" fill="none" stroke="#63E6BE" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>',
        ),
        "audio-x-generic.svg": make_mime_svg(
            "AUDIO",
            "#B197FC",
            "#7950F2",
            '<path d="M 25,34 V 22 L 37,19.5 V 32" fill="none" stroke="#D0BFFF" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"/>'
            '<circle cx="22.5" cy="34" r="2.6" fill="#D0BFFF"/>'
            '<circle cx="34.5" cy="32" r="2.6" fill="#D0BFFF"/>',
        ),
        "video-x-generic.svg": make_mime_svg(
            "VIDEO",
            "#FF922B",
            "#F76707",
            '<polygon points="26,21 38,28 26,35" fill="#FFC078"/>',
        ),
        "package-x-generic.svg": make_mime_svg(
            "ZIP",
            "#FCC419",
            "#F08C00",
            '<g stroke="#FFE066" stroke-width="2.2" stroke-linecap="round">'
            '<line x1="30.5" y1="16" x2="30.5" y2="35" stroke-dasharray="2.5 3.5"/>'
            '<rect x="26.5" y="25" width="8" height="6" rx="1.8" fill="#FFE066" stroke="none"/>'
            "</g>",
        ),
        "text-x-script.svg": make_mime_svg(
            "CODE",
            "#22B8CF",
            "#1098AD",
            '<g fill="none" stroke="#66D9E8" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">'
            '<polyline points="23,23 17,28 23,33"/>'
            '<polyline points="38,23 44,28 38,33"/>'
            '<line x1="33" y1="21" x2="28" y2="35"/>'
            "</g>",
        ),
        "application-x-executable.svg": make_mime_svg(
            "APP",
            "#5C7CFA",
            "#3B5BDB",
            '<rect x="21" y="19" width="19" height="16" rx="4" fill="none" stroke="#91A7FF" stroke-width="2.2"/>'
            '<circle cx="30.5" cy="27" r="3" fill="#91A7FF"/>',
        ),
    }

    for fname, content in mimes.items():
        (MIMES_DIR / fname).write_text(content, encoding="utf-8")

    print(f"Generated {len(folders)} HyperOS 3/4 place SVGs and {len(mimes)} MIME SVGs in sources/original/.")


if __name__ == "__main__":
    main()
