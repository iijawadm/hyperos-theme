# Asset Provenance & Licensing Audit

> **Important**: Publicly downloadable Android / HyperOS / MIUI / MTS theme assets are **not** automatically free to redistribute. Review the flagged collections below before publishing or redistributing derived icon themes.

## Summary by License Status

| License / Provenance Status | Scanned Files | Action Required |
| --- | ---: | --- |
| `original_author` (Jawad's original artwork in `sources/original/`) | 0 | Safe under repository license chosen by author |
| `unverified_third_party` (`hyperos3-icons/` & `sources/android/`) | 302 | **Flagged**: Verify original creator & redistribution permission before public release |

## Embedded Android XML Theme Metadata Found

No `description.xml` or `theme_values.xml` metadata files were present in the current Android icon directories. Original theme pack authorship for `hyperos3-icons/` cannot be automatically verified from file metadata alone and is flagged in `CREDITS.md`.

## Additional Repository Components Requiring Attribution Review

- `hyperos icons/`: Based on **Reversal Icon Theme** (GPL-3.0, `AUTHORS` & `COPYING` present) by `yeyushengfan258` / `vinceliuice`, derived from `OSX_ONE` (`unc926`), plus custom modifications by Jawad.
- `hyperos3-icons/`: Android HyperOS 3 / MIUI / MTS-sourced PNG icons — **no license file or embedded metadata included**. Flagged for copyright/redistribution review.
- `font/MiSans_Arabic/` & `font/MiSans_Latin/`: Xiaomi MiSans fonts — verify Xiaomi MiSans license terms before redistribution.
- `hyperos sounds/`: MIUI sound theme (`Name=MIUI`) — no license file present; verify redistribution rights.
- `backgrounds/`: Mixed community/OS wallpapers (including macOS/Xiaomi/anime wallpapers) — no per-file license recorded; verify before redistribution.
- `extenstions/`: 8 third-party GNOME Shell extensions, each retaining its own `LICENSE`/`COPYING` and `metadata.json` (documented in `CREDITS.md`).
