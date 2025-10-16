## HyperOS 3 Icons (WIP)

Drop your extracted icons into the standard freedesktop icon theme layout below.

Suggested structure:

```
hyperos3-icons/
  index.theme
  apps/
    16/
    22/
    24/
    32/
    48/
    64/
    128/
    scalable/   # for SVG
  actions/
    16/ 22/ 24/ 32/ 48/ 64/ 128/ scalable/
  categories/
  devices/
  emblems/
  mimes/
  places/
  status/
```

Tips:
- Prefer SVG in `scalable/` where possible. Use PNG for raster sizes.
- Filenames should match freedesktop icon names (e.g., `org.gnome.Terminal.svg`).
- After adding icons system-wide, run `sudo gtk-update-icon-cache -f /usr/share/icons/hyperos3-icons`.
- For user install, place the folder in `~/.icons/` or `~/.local/share/icons/` and run `gtk-update-icon-cache` accordingly.


