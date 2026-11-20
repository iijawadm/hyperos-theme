"""Generate a self-contained, searchable HTML icon preview & comparison gallery."""

from __future__ import annotations

import html
import json
import os
from pathlib import Path

from .mapper import MappingDecision


def _rel_href(from_dir: Path, target: Path) -> str:
    return Path(os.path.relpath(target, from_dir)).as_posix()


def generate_preview_gallery(
    decisions: list[MappingDecision],
    theme_root: Path,
    gallery_path: Path,
) -> Path:
    """Build an interactive HTML preview gallery with side-by-side Original vs Linux icon comparison."""
    gallery_path.parent.mkdir(parents=True, exist_ok=True)
    gallery_dir = gallery_path.parent

    # Only include non-redundant decisions (show mapped, unresolved, excluded, error; skip exact redundant copies)
    records = []
    for d in decisions:
        if d.status == "merged_duplicate" and d.method == "redundant_copy":
            continue

        orig_href = _rel_href(gallery_dir, d.asset.path)
        converted_href = ""
        converted_label = "—"
        if d.status == "mapped" and d.output_files:
            # Prefer 128x128 or 256x256 or scalable SVG for crisp gallery preview
            preferred = None
            for cand in d.output_files:
                if cand.startswith(("scalable/", "128x128/", "256x256/", "64x64/")):
                    preferred = cand
                    break
            chosen = preferred or d.output_files[-1]
            converted_href = _rel_href(gallery_dir, theme_root / chosen)
            converted_label = chosen

        dims = f"{d.asset.width}x{d.asset.height}" if d.asset.width else "Vector (SVG)"
        records.append(
            {
                "stem": d.asset.stem,
                "sourcePath": d.asset.rel_path,
                "sourceId": d.asset.source_id,
                "provenance": d.asset.provenance,
                "licenseStatus": d.asset.license_status,
                "format": d.asset.detected_format,
                "resolution": dims,
                "hasAlpha": bool(d.asset.has_alpha),
                "status": d.status,
                "method": d.method,
                "context": d.context or "unassigned",
                "canonical": d.canonical_name or "",
                "appName": d.app_name or d.asset.stem,
                "aliases": d.aliases,
                "desktopIds": d.matched_desktop_ids,
                "reason": d.reason,
                "origHref": orig_href,
                "convertedHref": converted_href,
                "convertedLabel": converted_label,
                "sizesCount": len(d.output_files),
            }
        )

    data_json = json.dumps(records, ensure_ascii=False).replace("</", "<\\/")

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>HyperOS Linux Icon Theme — Preview &amp; QA Gallery</title>
  <style>
    :root {{
      --bg: #0f1117;
      --surface: #171a23;
      --surface-2: #1f2430;
      --border: #2a3142;
      --text: #eef1f7;
      --muted: #98a2b8;
      --accent: #3b82f6;
      --ok: #22c55e;
      --warn: #f59e0b;
      --err: #ef4444;
      --purple: #a855f7;
      --checker-a: #252b38;
      --checker-b: #1b202b;
    }}
    body.light-preview {{
      --checker-a: #e9edf5;
      --checker-b: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.45;
    }}
    header {{
      position: sticky;
      top: 0;
      z-index: 20;
      background: rgba(15, 17, 23, 0.92);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
      padding: 16px 24px;
    }}
    .header-top {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }}
    h1 {{
      margin: 0;
      font-size: 1.25rem;
      font-weight: 700;
    }}
    .stats {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      font-size: 0.82rem;
    }}
    .pill {{
      padding: 4px 10px;
      border-radius: 999px;
      background: var(--surface-2);
      border: 1px solid var(--border);
      color: var(--muted);
    }}
    .pill strong {{ color: var(--text); }}
    .controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }}
    input[type="search"], select, button {{
      background: var(--surface);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 8px 12px;
      font-size: 0.9rem;
    }}
    input[type="search"] {{
      flex: 1 1 260px;
      min-width: 200px;
    }}
    button {{
      cursor: pointer;
    }}
    button:hover {{
      border-color: var(--accent);
    }}
    main {{
      padding: 20px 24px 48px;
      max-width: 1600px;
      margin: 0 auto;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
      gap: 16px;
    }}
    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}
    .compare {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      border-bottom: 1px solid var(--border);
    }}
    .pane {{
      padding: 14px 10px 10px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
      background-image:
        linear-gradient(45deg, var(--checker-a) 25%, transparent 25%),
        linear-gradient(-45deg, var(--checker-a) 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, var(--checker-a) 75%),
        linear-gradient(-45deg, transparent 75%, var(--checker-a) 75%);
      background-size: 14px 14px;
      background-position: 0 0, 0 7px, 7px -7px, -7px 0;
      background-color: var(--checker-b);
    }}
    .pane + .pane {{
      border-left: 1px solid var(--border);
    }}
    .pane img {{
      width: 64px;
      height: 64px;
      object-fit: contain;
      image-rendering: auto;
    }}
    .pane .placeholder {{
      width: 64px;
      height: 64px;
      display: grid;
      place-items: center;
      border: 1px dashed var(--border);
      border-radius: 12px;
      color: var(--muted);
      font-size: 0.72rem;
      text-align: center;
      padding: 4px;
    }}
    .pane-label {{
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--muted);
      background: rgba(15, 17, 23, 0.75);
      padding: 2px 7px;
      border-radius: 6px;
    }}
    .meta {{
      padding: 12px 14px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      font-size: 0.83rem;
    }}
    .title-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }}
    .name {{
      font-weight: 600;
      word-break: break-word;
    }}
    .badge {{
      font-size: 0.72rem;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 999px;
      white-space: nowrap;
    }}
    .badge-mapped {{ background: rgba(34, 197, 94, 0.16); color: var(--ok); }}
    .badge-unresolved {{ background: rgba(245, 158, 11, 0.16); color: var(--warn); }}
    .badge-excluded {{ background: rgba(168, 85, 247, 0.16); color: var(--purple); }}
    .badge-merged_duplicate {{ background: rgba(59, 130, 246, 0.16); color: var(--accent); }}
    .badge-error {{ background: rgba(239, 68, 68, 0.16); color: var(--err); }}
    .kv {{
      color: var(--muted);
      font-size: 0.78rem;
      word-break: break-word;
    }}
    .kv code {{
      color: var(--text);
      background: var(--surface-2);
      padding: 1px 5px;
      border-radius: 4px;
      font-size: 0.75rem;
    }}
    .empty {{
      text-align: center;
      padding: 48px;
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <header>
    <div class="header-top">
      <h1>HyperOS Linux Icon Theme — Preview &amp; Comparison Gallery</h1>
      <div class="stats" id="stats"></div>
    </div>
    <div class="controls">
      <input type="search" id="search" placeholder="Search filename, Android package, Linux icon name, or alias..." />
      <select id="statusFilter">
        <option value="all">All Statuses</option>
        <option value="mapped">Mapped</option>
        <option value="unresolved">Unresolved</option>
        <option value="merged_duplicate">Merged Alias / Duplicate</option>
        <option value="excluded">Excluded Helpers</option>
        <option value="error">Errors</option>
      </select>
      <select id="contextFilter">
        <option value="all">All Categories</option>
        <option value="apps">apps</option>
        <option value="places">places</option>
        <option value="status">status</option>
        <option value="devices">devices</option>
        <option value="actions">actions</option>
        <option value="unassigned">unassigned</option>
      </select>
      <button id="toggleSurface" type="button">Toggle Light/Dark Checkerboard</button>
    </div>
  </header>
  <main>
    <div class="grid" id="grid"></div>
    <div class="empty" id="empty" hidden>No icons match your filter criteria.</div>
  </main>
  <script>
    const RECORDS = {data_json};
    const grid = document.getElementById('grid');
    const empty = document.getElementById('empty');
    const stats = document.getElementById('stats');
    const searchEl = document.getElementById('search');
    const statusEl = document.getElementById('statusFilter');
    const contextEl = document.getElementById('contextFilter');

    function esc(str) {{
      return String(str).replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
    }}

    function renderStats(list) {{
      const counts = {{ mapped: 0, unresolved: 0, excluded: 0, merged_duplicate: 0, error: 0 }};
      for (const r of RECORDS) counts[r.status] = (counts[r.status] || 0) + 1;
      stats.innerHTML = `
        <span class="pill">Showing <strong>${{list.length}}</strong> / ${{RECORDS.length}}</span>
        <span class="pill">Mapped: <strong>${{counts.mapped}}</strong></span>
        <span class="pill">Unresolved: <strong>${{counts.unresolved}}</strong></span>
        <span class="pill">Merged: <strong>${{counts.merged_duplicate}}</strong></span>
        <span class="pill">Excluded: <strong>${{counts.excluded}}</strong></span>
      `;
    }}

    function render() {{
      const q = searchEl.value.trim().toLowerCase();
      const st = statusEl.value;
      const ctx = contextEl.value;

      const filtered = RECORDS.filter(r => {{
        if (st !== 'all' && r.status !== st) return false;
        if (ctx !== 'all' && r.context !== ctx) return false;
        if (!q) return true;
        const hay = [r.stem, r.sourcePath, r.canonical, r.appName, r.context, ...(r.aliases || []), ...(r.desktopIds || [])]
          .join(' ').toLowerCase();
        return hay.includes(q);
      }});

      renderStats(filtered);
      empty.hidden = filtered.length > 0;
      grid.innerHTML = filtered.map(r => {{
        const rightPane = r.convertedHref
          ? `<img src="${{esc(r.convertedHref)}}" alt="${{esc(r.canonical)}}" loading="lazy" />`
          : `<div class="placeholder">${{esc(r.status)}}</div>`;
        const linuxMapping = r.canonical ? `<code>${{esc(r.context)}}/${{esc(r.canonical)}}</code>` : '—';
        const aliases = r.aliases.length ? r.aliases.slice(0, 4).map(a => `<code>${{esc(a)}}</code>`).join(' ') + (r.aliases.length > 4 ? ` +${{r.aliases.length - 4}}` : '') : '—';
        return `
          <article class="card">
            <div class="compare">
              <div class="pane">
                <img src="${{esc(r.origHref)}}" alt="${{esc(r.stem)}}" loading="lazy" />
                <span class="pane-label">Original Android</span>
              </div>
              <div class="pane">
                ${{rightPane}}
                <span class="pane-label">Linux Theme</span>
              </div>
            </div>
            <div class="meta">
              <div class="title-row">
                <span class="name">${{esc(r.appName)}}</span>
                <span class="badge badge-${{esc(r.status)}}">${{esc(r.status)}}</span>
              </div>
              <div class="kv"><strong>File:</strong> <code>${{esc(r.stem)}}</code></div>
              <div class="kv"><strong>Source:</strong> <code>${{esc(r.sourcePath)}}</code> (${{esc(r.resolution)}}, ${{esc(r.format)}}${{r.hasAlpha ? ', RGBA' : ''}})</div>
              <div class="kv"><strong>Linux Mapping:</strong> ${{linuxMapping}} ${{r.sizesCount ? `(${{r.sizesCount}} sizes)` : ''}}</div>
              <div class="kv"><strong>Aliases:</strong> ${{aliases}}</div>
              <div class="kv"><strong>License:</strong> <code>${{esc(r.licenseStatus)}}</code></div>
            </div>
          </article>
        `;
      }}).join('');
    }}

    searchEl.addEventListener('input', render);
    statusEl.addEventListener('change', render);
    contextEl.addEventListener('change', render);
    document.getElementById('toggleSurface').addEventListener('click', () => {{
      document.body.classList.toggle('light-preview');
    }});

    render();
  </script>
</body>
</html>
"""
    gallery_path.write_text(page, encoding="utf-8")
    return gallery_path
