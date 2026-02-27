#!/usr/bin/env python3
import base64, csv, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / 'hyperos3-icons' / 'apps' / '128'
STATUS_SOURCE_DIR = ROOT / 'hyperos3-icons' / 'status' / '24'
TARGET_SCALABLE_DIRS = [
    ROOT / 'hyperos icons' / 'apps' / 'scalable',
    ROOT / 'hyperos icons' / 'apps@2x' / 'scalable',
]
TARGET_ACTION_24_DIRS = [
    ROOT / 'hyperos icons' / 'actions' / '24',
    ROOT / 'hyperos icons' / 'actions@2x' / '24',
]
LOG_DIR = ROOT / 'hyperos3-icons' / 'mapping'
LOG_DIR.mkdir(parents=True, exist_ok=True)

KNOWN_MAP = {
    'com.android.calculator2': 'calculator',
    'com.miui.calculator': 'calculator',
    'com.android.settings': 'preferences-system',
    'com.android.camera': 'camera-photo',
    'com.android.contacts': 'x-office-address-book',
    'com.android.providers.contacts': 'x-office-address-book',
    'com.android.providers.contacts.CallLogProvider': 'call-start',
    'com.android.contacts.activities.TwelveKeyDialer': 'call-start',
    'com.android.deskclock': 'alarm',
    'com.android.fileexplorer': 'system-file-manager',
    'com.mi.android.globalFileexplorer': 'system-file-manager',
    'com.miui.gallery': 'org.gnome.Photos',
    'com.android.email': 'internet-mail',
    'com.android.music': 'multimedia-player',
    'com.miui.player': 'multimedia-player',
    'com.apple.android.music': 'multimedia-player',
    'com.spotify.music': 'spotify-client',
    'org.telegram.messenger': 'telegram',
    'com.whatsapp': 'whatsapp',
    'com.twitter.android': 'twitter',
    'com.instagram.android': 'instagram',
    'com.facebook.katana': 'facebook',
    'com.facebook.orca': 'messenger',
    'com.tencent.mm': 'wechat',
    'com.tencent.mobileqq': 'qq',
    'com.tencent.tim': 'tim',
    'com.tencent.qqmusic': 'qqmusic',
    'com.netease.cloudmusic': 'netease-cloud-music',
    'com.miui.weather2': 'weather-severe-alert',
    'com.miui.screenrecorder': 'media-record',
    'com.android.soundrecorder': 'audio-input-microphone',
    'com.android.mms': 'mail-message-new',
    'com.android.thememanager': 'preferences-desktop-theme',
    'com.android.voicedialer': 'audio-headset',
    'com.miui.compass': 'compass',
    'com.miui.fmradio': 'radio',
    'com.miui.fm': 'radio',
    'com.miui.video': 'video-display',
    'com.miui.videoplayer': 'video-display',
    'com.miui.notes': 'notes',
    'com.xiaomi.calendar': 'x-office-calendar',
    'com.android.providers.downloads.ui': 'folder-download',
    'com.android.providers.downloads': 'folder-download',
}

STATUS_MAP = {
    'status_bar_toggle_flight_mode_on': 'airplane-mode-on',
    'status_bar_toggle_flight_mode_off': 'airplane-mode-off',
    'status_bar_toggle_wifi_on': 'network-wireless-on',
    'status_bar_toggle_wifi_off': 'network-wireless-off',
    'status_bar_toggle_wifi_ap_on': 'network-wireless-hotspot',
    'status_bar_toggle_wifi_ap_off': 'network-wireless-hotspot-disabled',
    'status_bar_toggle_data_on': 'network-cellular-on',
    'status_bar_toggle_data_off': 'network-cellular-off',
    'status_bar_toggle_bluetooth_on': 'bluetooth-active',
    'status_bar_toggle_bluetooth_off': 'bluetooth-disabled',
    'status_bar_toggle_torch_on': 'flashlight-on',
    'status_bar_toggle_torch_off': 'flashlight-off',
    'status_bar_toggle_lock': 'changes-prevent',
}

PREFIXES = [
    'com.android.', 'com.miui.', 'com.xiaomi.', 'com.mi.', 'com.tencent.',
    'com.facebook.', 'com.ss.android.', 'com.', 'org.', 'net.', 'me.', 'xyz.'
]

def probable_name(package: str) -> str:
    token = package.split('.')[-1]
    token = re.sub(r'([a-z])([A-Z])', r'\1 \2', token)
    token = token.replace('_', ' ').replace('-', ' ')
    return token.title()

def fallback_name(package: str) -> str:
    p = package
    for pref in PREFIXES:
        if p.startswith(pref):
            p = p[len(pref):]
            break
    p = p.replace('.', '-')
    p = re.sub(r'[^a-zA-Z0-9-]+', '-', p).strip('-').lower()
    return p or 'android-app'

def png_dimensions(data: bytes):
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('not png')
    import struct
    w,h = struct.unpack('>II', data[16:24])
    return w,h

def png_to_embedded_svg(src: Path, dst: Path):
    data = src.read_bytes()
    w, h = png_dimensions(data)
    b64 = base64.b64encode(data).decode('ascii')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <image width="{w}" height="{h}" href="data:image/png;base64,{b64}"/>
</svg>\n'''
    dst.write_text(svg)

rows = []
added = 0
skipped_existing = 0
for src in sorted(SOURCE_DIR.glob('*.png')):
    package = src.stem
    canonical = KNOWN_MAP.get(package) or fallback_name(package)
    purpose = 'application icon'
    app_name = probable_name(package)
    status = 'mapped' if package in KNOWN_MAP else 'fallback'

    for target_dir in TARGET_SCALABLE_DIRS:
        target = target_dir / f'{canonical}.svg'
        package_alias = target_dir / f'{package}.svg'
        if target.exists():
            skipped_existing += 1
            target_action = 'exists-skip'
        else:
            png_to_embedded_svg(src, target)
            added += 1
            target_action = 'created'

        if not package_alias.exists() and package_alias != target:
            rel = target.name
            package_alias.symlink_to(rel)
            alias_action = 'alias-created'
        else:
            alias_action = 'alias-exists-skip'

        rows.append({
            'source': str(src.relative_to(ROOT)),
            'package': package,
            'probable_app_name': app_name,
            'purpose': purpose,
            'transformation': f'{package} -> {canonical}',
            'target': str(target.relative_to(ROOT)),
            'status': status,
            'target_action': target_action,
            'alias_action': alias_action,
        })

for src in sorted(STATUS_SOURCE_DIR.glob('*.png')):
    stem = src.stem
    canonical = STATUS_MAP.get(stem, stem.replace('_', '-'))
    for target_dir in TARGET_ACTION_24_DIRS:
        target = target_dir / f'{canonical}.svg'
        if target.exists():
            action = 'exists-skip'
        else:
            png_to_embedded_svg(src, target)
            action = 'created'
            added += 1
        rows.append({
            'source': str(src.relative_to(ROOT)),
            'package': stem,
            'probable_app_name': stem,
            'purpose': 'status toggle icon',
            'transformation': f'{stem} -> {canonical}',
            'target': str(target.relative_to(ROOT)),
            'status': 'mapped',
            'target_action': action,
            'alias_action': '',
        })

csv_path = LOG_DIR / 'conversion-mapping-log.csv'
with csv_path.open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

summary_path = LOG_DIR / 'summary.txt'
fallbacks = sum(1 for r in rows if r['status'] == 'fallback')
known = sum(1 for r in rows if r['status'] == 'mapped')
unique_targets = len({r['target'] for r in rows})
summary_path.write_text(
    f'total_entries={len(rows)}\n'
    f'known_mappings={known}\n'
    f'fallback_mappings={fallbacks}\n'
    f'unique_target_paths={unique_targets}\n'
    f'created_this_run={added}\n'
    f'skipped_existing={skipped_existing}\n'
)
print(f'Wrote {csv_path} and {summary_path}')
