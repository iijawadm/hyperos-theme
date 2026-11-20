# Original HyperOS-Inspired Icons

Place independently created or modified HyperOS-inspired icons by Jawad (`iijawadm`) in this directory.

## Directory Layout

You can organize icons by Freedesktop context:

```text
sources/original/
├── apps/       # Application icons (e.g., firefox.svg, org.gnome.Nautilus.svg)
├── actions/    # Action icons
├── devices/    # Device icons
├── places/     # Folder and place icons
└── status/     # Status/panel icons
```

## Rules

- **Highest priority**: Icons placed here take precedence over any Android/HyperOS/MTS pack icons during `./build.sh`.
- **Supported formats**: `.svg` (preferred for crisp scaling), `.png`, `.webp`.
- **Never overwritten**: The conversion pipeline will never replace original artwork placed here with third-party Android assets.
