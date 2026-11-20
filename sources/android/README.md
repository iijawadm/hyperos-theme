# Additional Android / HyperOS / MIUI / MTS Icon Packs

Drop extracted Android icon packs (or `.mtz` / `.zip` icon archives) into subdirectories here to include them in the automated conversion pipeline.

## Example Layout

```text
sources/android/
└── my-hyperos-pack/
    ├── com.android.chrome.png
    ├── com.spotify.music.webp
    ├── org.telegram.messenger.png
    └── appfilter.xml          # Optional Android icon pack metadata
```

## Supported Formats

- Raster: `.png`, `.webp`, `.jpg`, `.jpeg`, `.bmp`, `.ico`
- Vector: `.svg`
- Metadata (optional): `appfilter.xml`, `drawable.xml`, `description.xml`, `theme_values.xml`

After adding new icons, run:

```bash
./build.sh
./validate.sh
```

> **Note on Licensing**: Before publishing converted third-party icon packs, record their source, creator, and license in `CREDITS.md` and review `reports/licensing-audit.md`.
