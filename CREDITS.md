# Credits, Attribution, and Licensing

This repository combines original desktop theming work, independently modified components, and third-party open-source or external assets. We strive to credit every original creator accurately and **do not claim ownership of third-party assets**.

> **Important Notice on Redistribution**: Publicly downloadable Android / HyperOS / MIUI / MTS theme assets, proprietary fonts, system sounds, and community wallpapers are **not** automatically free to redistribute. Items with unverified ownership or licensing are explicitly flagged below and in [`reports/licensing-audit.md`](reports/licensing-audit.md).

---

## 1. Original Work Created by Jawad (`iijawadm`)

| Component | Path | License / Terms | Notes |
| --- | --- | --- | --- |
| Repository curation, layout scripts, and banner | `README.md`, `banner.png`, `gnome-layout-manager/`, `screenshots/` | Maintained by `iijawadm` | Project curation, GNOME layout integration, and documentation |
| Original HyperOS-inspired icons (drop-in directory) | `sources/original/` | Author-owned (`iijawadm`) | Dedicated directory for Jawad's original/independently created HyperOS-inspired artwork (takes highest priority in `./build.sh`) |
| Automated Android-to-Linux icon theme pipeline | `scripts/hyperos_converter/`, `build.sh`, `validate.sh`, `install.sh`, `uninstall.sh`, `scripts/test_pipeline.py` | Open-source tooling in this repository | Freedesktop icon conversion, mapping, validation, and HTML preview gallery |

---

## 2. HyperOS / MIUI / MTS Android Theme Sources

| Asset Collection | Path | Original Creator / Source | License / Usage Terms | Redistribution Status |
| --- | --- | --- | --- | --- |
| HyperOS 3 Android Icon Pack (151 unique PNGs + duplicates) | `hyperos3-icons/` | Originating from Android HyperOS / MIUI / MTS theme packs (no embedded `description.xml` or license metadata found in files) | **Unverified** — Xiaomi HyperOS / MIUI and third-party MTS theme pack artwork may be subject to proprietary copyright and trademark restrictions | **FLAGGED — Verify permission before redistributing** |
| Generated Linux Icon Theme (from `hyperos3-icons/`) | `HyperOS-Icons/` | Converted derivative of `hyperos3-icons/` (plus any original artwork placed in `sources/original/`) | Inherits licensing constraints of its source assets | **FLAGGED** for assets derived from `hyperos3-icons/` |
| MIUI Sound Theme | `hyperos sounds/` | `index.theme` identifies `Name=MIUI`; original creator Xiaomi / MIUI | **Unverified** — no license file included in directory | **FLAGGED — Verify permission before redistributing** |
| MiSans Fonts (Arabic & Latin) | `font/MiSans_Arabic/`, `font/MiSans_Latin/` | Xiaomi Inc. (`MiSans`) | Subject to Xiaomi MiSans Font License Agreement (verify current terms from Xiaomi before redistributing) | **Review required** — verify license terms before redistributing |

---

## 3. Third-Party Icon Creators & Desktop Components

### Base Icon Theme (`hyperos icons/`)

Per [`hyperos icons/AUTHORS`](hyperos%20icons/AUTHORS) and [`hyperos icons/COPYING`](hyperos%20icons/COPYING):

- **Theme**: Reversal Icon Theme
- **Customizer / Maintainer**: `yeyushengfan258` (`yeyushengfan258@outlook.com`) — <https://github.com/yeyushengfan258/Reversal-icon-theme> (listed in `AUTHORS` as `https://github.com//vinceliuice/Reversal-icon-theme`)
- **Upstream Source**: `OSX_ONE` — <https://github.com/unc926/OSX_ONE>
- **License**: GNU General Public License v3.0 (`GPL-3.0`, see `hyperos icons/COPYING`)
- **Redistribution**: Permitted under the terms of GPL-3.0, with attribution and license preserved.

### Bundled GNOME Shell Extensions (`extenstions/`)

Each bundled extension preserves its upstream `metadata.json` and `LICENSE`/`COPYING` file:

| Extension | Directory | Upstream URL | License File |
| --- | --- | --- | --- |
| Compiz alike magic lamp effect | `extenstions/compiz-alike-magic-lamp-effect@hermes83.github.com` | <https://github.com/hermes83/compiz-alike-magic-lamp-effect> | `LICENSE` |
| Custom OSD | `extenstions/custom-osd@neuromorph` | <https://github.com/neuromorph/custom-osd> | `LICENSE` |
| Dash to Dock | `extenstions/dash-to-dock@micxgx.gmail.com` | <https://micheleg.github.io/dash-to-dock/> | `COPYING` |
| Gnome 4x UI Improvements | `extenstions/gnome-ui-tune@itstime.tech` | <https://github.com/axxapy/gnome-ui-tune> | `LICENSE` |
| Just Perfection | `extenstions/just-perfection-desktop@just-perfection` | <https://gitlab.gnome.org/jrahmatzadeh/just-perfection> | `LICENSE` |
| Open Bar | `extenstions/openbar@neuromorph` | <https://github.com/neuromorph/openbar> | `LICENSE` |
| Quick Setting Tweaker (`[QSTweak]`) | `extenstions/quick-settings-tweaks@qwreey` | <https://github.com/qwreey75/quick-settings-tweaks> | `LICENSE`, `LICENSE-gnome-volume-mixer` |
| User Themes | `extenstions/user-theme@gnome-shell-extensions.gcampax.github.com` | <https://gitlab.gnome.org/GNOME/gnome-shell-extensions> | `COPYING` |

---

## 4. Independently Modified or Adapted Icons & Themes

| Component | Path | Base / Inspiration | Notes |
| --- | --- | --- | --- |
| `Hyperos-Dark` GTK & GNOME Shell Theme | `Hyperos-Dark/` | Adapted from community themes on GnomeLook (`index.theme` notes `"based on Elegant Design"`) | Modified by Jawad for HyperOS-style GNOME Shell & GTK aesthetics; verify upstream base theme license if redistributing |
| Modified SVGs in legacy `hyperos icons/` | `hyperos icons/apps/scalable/` (modified in commit `838a588`) | Adapted on top of Reversal Icon Theme (GPL-3.0) | Includes repaired SVG files (`Blender.svg`, `GitKraken.svg`, `Notion.svg`, `Stacer.svg`, `TeamViewer.svg`, `Terminal.svg`, `text-x-R.svg`) and GNOME app icon tweaks |

---

## 5. Unknown or Unverified Ownership

The following assets currently lack verifiable author metadata or explicit license files in the repository and **must be reviewed before public redistribution**:

- **`hyperos3-icons/*.png`** — Android HyperOS 3 / MIUI / MTS theme icons without embedded author/license XML metadata.
- **`backgrounds/*`** — Wallpapers from mixed sources (including Xiaomi, macOS, anime, and digital art wallpapers) without per-file creator attribution or license files.
- **`hyperos sounds/*`** — MIUI-branded system sound files without a license file.
- **Legacy embedded-PNG SVGs in `hyperos icons/`** (imported in commit `c79c9cb` from `hyperos3-icons/`) — inherit the unverified licensing status of `hyperos3-icons/`.

If you are an original creator of any asset in this repository and would like attribution updated or an asset removed, please open an issue or pull request on <https://github.com/iijawadm/hyperos-theme>.
