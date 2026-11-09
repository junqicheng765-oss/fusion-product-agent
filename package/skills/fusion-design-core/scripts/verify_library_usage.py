#!/usr/bin/env python3
"""Check requested local asset/stylesheet evidence, not design quality or tool execution.

The optional --manifest is the machine-readable form of the existing asset record:
entrypoints: [relative HTML paths]
stylesheets: [{file, role: recipes|theme, required: true}]
assets: [{file, provider, source: URL or tool ID, role, required: true}]
Rows describe adopted files by default; required:false excludes candidate rows.
Paths resolve inside task_dir. Without entrypoints, root index.html is used if present.
Source/role declarations are checked for presence, never authenticated by this script.
"""
import argparse
import base64
import binascii
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import struct
import sys
from urllib.parse import unquote, unquote_to_bytes, urlsplit
import xml.etree.ElementTree as ET
import zlib


CSS_URL = re.compile(r"url\(\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s)]*))\s*\)", re.I)
CSS_IMPORT = re.compile(r"@import\s+(?:url\(\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s)]*))\s*\)|\"([^\"]*)\"|'([^']*)')", re.I)


def local_path(root, value, relative_to=None):
    """Resolve a declared path without reading outside the task (including symlinks)."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("file/path must be a non-empty string")
    p = Path(value)
    p = (p if p.is_absolute() else (relative_to or root) / p).resolve()
    try:
        p.relative_to(root)
    except ValueError:
        raise ValueError("path leaves task directory")
    return p


def lottie_valid(data):
    return (isinstance(data, dict) and isinstance(data.get('v'), str)
            and all(isinstance(data.get(k), (int, float)) and not isinstance(data.get(k), bool)
                    for k in ('fr', 'ip', 'op', 'w', 'h'))
            and data['fr'] > 0 and data['op'] > data['ip'] and data['w'] > 0 and data['h'] > 0
            and isinstance(data.get('layers'), list) and bool(data['layers'])
            and all(isinstance(layer, dict) and type(layer.get('ty')) is int
                    for layer in data['layers']))


def media_format(path):
    """Conservative structural checks; not a complete decoder or renderer."""
    b = path.read_bytes()
    ext = path.suffix.lower()
    if ext == '.svg':
        svg = ET.fromstring(b)
        draw = {'path', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'text', 'image', 'use'}
        if svg.tag.split('}')[-1] == 'svg' and any(n.tag.split('}')[-1] in draw for n in svg.iter()):
            return 'svg'
    elif ext == '.png' and b.startswith(b'\x89PNG\r\n\x1a\n'):
        pos, chunks = 8, []
        while pos + 12 <= len(b):
            n = struct.unpack('>I', b[pos:pos + 4])[0]
            kind, payload = b[pos + 4:pos + 8], b[pos + 8:pos + 8 + n]
            end = pos + 12 + n
            if end > len(b) or zlib.crc32(kind + payload) & 0xffffffff != struct.unpack('>I', b[end - 4:end])[0]:
                break
            chunks.append((kind, payload)); pos = end
            if kind == b'IEND':
                if (pos == len(b) and chunks[0][0] == b'IHDR' and len(chunks[0][1]) == 13
                        and all(struct.unpack('>II', chunks[0][1][:8]))
                        and any(k == b'IDAT' and p for k, p in chunks)):
                    zlib.decompress(b''.join(p for k, p in chunks if k == b'IDAT'))
                    return 'png'
                break
    elif ext in ('.jpg', '.jpeg') and len(b) > 16 and b[:2] == b'\xff\xd8' and b[-2:] == b'\xff\xd9':
        # A frame header and scan distinguish JPEG data from a renamed metadata file.
        if re.search(b'\xff[\xc0-\xc3\xc5-\xc7\xc9-\xcb\xcd-\xcf]', b) and b'\xff\xda' in b:
            return 'jpeg'
    elif ext == '.gif' and len(b) > 14 and b[:6] in (b'GIF87a', b'GIF89a'):
        if all(struct.unpack('<HH', b[6:10])) and b'\x2c' in b[13:] and b.endswith(b';'):
            return 'gif'
    elif ext == '.webp' and len(b) > 20 and b[:4] == b'RIFF' and b[8:12] == b'WEBP':
        if struct.unpack('<I', b[4:8])[0] + 8 == len(b) and b[12:16] in (b'VP8 ', b'VP8L', b'VP8X'):
            return 'webp'
    elif ext == '.json':
        if lottie_valid(json.loads(b)):
            return 'lottie-json'
    elif ext == '.glb' and len(b) >= 20 and b[:4] == b'glTF':
        version, size, n = struct.unpack('<III', b[4:16])
        if version == 2 and size == len(b) and b[16:20] == b'JSON' and 20 + n <= len(b):
            gltf = json.loads(b[20:20 + n].rstrip(b'\x00 '))
            if (isinstance(gltf, dict) and isinstance(gltf.get('asset'), dict)
                    and gltf['asset'].get('version') == '2.0'
                    and isinstance(gltf.get('meshes'), list) and bool(gltf['meshes'])):
                return 'glb'
    elif ext == '.mp4' and len(b) > 24 and b[4:8] == b'ftyp' and b'mdat' in b and (b'moov' in b or b'moof' in b):
        return 'mp4'
    elif ext == '.webm' and b.startswith(b'\x1aE\xdf\xa3') and b'webm' in b[:4096] and len(b) > 32:
        return 'webm'
    raise ValueError("unsupported, empty or structurally invalid media file")


class References(HTMLParser):
    def __init__(self):
        super().__init__(); self.urls = []; self.stylesheets = []; self.css = []; self.style_blocks = []; self.in_style = False
        self.base_href = None; self.template_depth = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'template': self.template_depth += 1
        if self.template_depth: return
        if tag == 'base' and 'href' in a and self.base_href is None: self.base_href = a['href'] or ''
        if tag == 'style': self.in_style = True
        if a.get('style'): self.css.append(a['style'])
        for key in ('src', 'poster', 'data'):
            if a.get(key) and (key != 'data' or tag == 'object'):
                self.urls.append((a[key], 'document' if tag in ('iframe', 'object') else 'asset'))
        if tag == 'link':
            rel = set(a.get('rel', '').lower().split())
            if a.get('href') and rel & {'stylesheet', 'icon', 'preload', 'modulepreload'}:
                self.urls.append((a['href'], 'asset'))
                if 'stylesheet' in rel and 'alternate' not in rel and 'disabled' not in a:
                    self.stylesheets.append(a['href'])
        if tag in ('use', 'image'):
            if a.get('href') or a.get('xlink:href'): self.urls.append((a.get('href') or a['xlink:href'], 'asset'))
        if a.get('srcset') and 'data:' not in a['srcset']:
            self.urls.extend((part.strip().split()[0], 'asset') for part in a['srcset'].split(',') if part.strip())

    def handle_endtag(self, tag):
        if tag == 'template' and self.template_depth: self.template_depth -= 1
        if self.template_depth: return
        if tag == 'style': self.in_style = False

    def handle_data(self, data):
        if self.in_style and not self.template_depth:
            self.css.append(data); self.style_blocks.append(data)


def css_references(text):
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    return [v for m in CSS_URL.findall(text) for v in [next((v for v in m if v), '')] if v] + css_imports(text)


def css_imports(text):
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    return [v for m in CSS_IMPORT.findall(text) for v in [next((v for v in m if v), '')] if v]


def stylesheet_valid(path):
    css = re.sub(r'/\*.*?\*/', '', path.read_text(encoding='utf-8'), flags=re.S)
    return bool(re.search(r'[^{}]+\{[^{}]*:[^{}]+\}', css)
                or (re.search(r'@import\s', css, re.I) and css_references(css)))


def reachable_files(root, entries):
    seen, visited_modes, loaded_styles, embedded, errors = set(), set(), set(), set(), []

    def visit(p, mode):
        if (p, mode) in visited_modes: return
        visited_modes.add((p, mode))
        if not p.is_file():
            errors.append({'file': str(p.relative_to(root)), 'reason': 'local resource does not exist'}); return
        seen.add(p)
        refs = []
        if (mode == 'document' and p.suffix.lower() in ('.html', '.htm')) or p.suffix.lower() == '.svg':
            parser = References(); parser.feed(p.read_text(encoding='utf-8'))
            if parser.base_href:
                raise ValueError('base href URL resolution is not supported; references remain unverified')
            refs = (parser.urls + [(u, 'stylesheet') for u in parser.stylesheets]
                    + [(u, 'asset') for c in parser.css for u in css_references(c)]
                    + [(u, 'stylesheet') for c in parser.style_blocks for u in css_imports(c)])
        elif mode == 'stylesheet' and p.suffix.lower() == '.css':
            loaded_styles.add(p)
            css = p.read_text(encoding='utf-8'); imports = set(css_imports(css))
            refs = [(u, 'stylesheet' if u in imports else 'asset') for u in css_references(css)]
        for ref, edge in refs:
            if ref.startswith('data:'):
                try:
                    header, payload = ref.split(',', 1)
                    raw = base64.b64decode(payload, validate=True) if ';base64' in header else unquote_to_bytes(payload)
                    embedded.add(hashlib.sha256(raw).hexdigest())
                except (ValueError, binascii.Error):
                    errors.append({'file': str(p.relative_to(root)), 'reason': 'malformed embedded data URL'})
                continue
            parsed = urlsplit(ref)
            if parsed.scheme or parsed.netloc or not parsed.path: continue
            try:
                target = local_path(root, unquote(parsed.path).lstrip('/') if parsed.path.startswith('/') else unquote(parsed.path),
                                    root if parsed.path.startswith('/') else p.parent)
                visit(target, edge)
            except (ValueError, UnicodeError, OSError) as e:
                errors.append({'file': str(p.relative_to(root)), 'reason': str(e)})

    for p in entries: visit(p, 'document')
    return seen, loaded_styles, embedded, errors


def verify(task_dir: Path, require_avatars: int = 0, require_photos: bool = False, *,
           manifest=None, entrypoints=None, require_stylesheets=None,
           require_recipes=False, require_theme=False, require_iconscout=False) -> dict:
    root = Path(task_dir).resolve(); issues = []; data = {}; manifest_given = manifest is not None

    def issue(code, message):
        issues.append({'code': code, 'severity': 'FAIL', 'message': message})

    if not root.is_dir():
        issue('TASK_DIR_MISSING', '任务目录不存在或不是目录。')
    if require_avatars < 0:
        issue('INVALID_REQUIREMENT', '头像数量不能为负。')
    if manifest_given and root.is_dir():
        try:
            mp = local_path(root, str(manifest)); data = json.loads(mp.read_text(encoding='utf-8'))
            if not isinstance(data, dict) or not any(k in data for k in ('entrypoints', 'assets', 'stylesheets')):
                raise ValueError('manifest needs entrypoints, assets or stylesheets fields')
            for key in ('entrypoints', 'assets', 'stylesheets'):
                if key in data and not isinstance(data[key], list): raise ValueError(key + ' must be a list')
        except (ValueError, OSError) as e:
            issue('MANIFEST_INVALID', str(e)); data = {}

    entry_values = list(entrypoints or data.get('entrypoints', []))
    if not entry_values and (root / 'index.html').is_file(): entry_values = ['index.html']
    entries = []
    for value in entry_values:
        try:
            p = local_path(root, value)
            if p.suffix.lower() not in ('.html', '.htm'): raise ValueError('entrypoint must be HTML')
            entries.append(p)
        except ValueError as e: issue('ENTRYPOINT_INVALID', str(e))
    try:
        reachable, loaded_styles, embedded, ref_errors = reachable_files(root, entries)
    except (ValueError, OSError, UnicodeError) as e:
        reachable, loaded_styles, embedded, ref_errors = set(), set(), set(), [{'reason': str(e)}]
    for error in ref_errors: issue('LOCAL_REFERENCE_INVALID', json.dumps(error, ensure_ascii=False))

    stylesheet_rows = list(data.get('stylesheets', [])) + [{'file': x} for x in require_stylesheets or []]
    asset_rows = list(data.get('assets', []))
    requested = bool(manifest_given or stylesheet_rows or require_recipes or require_theme or require_iconscout
                     or require_avatars or require_photos)
    if requested and not entries: issue('ENTRYPOINTS_UNVERIFIED', '需提供实际 HTML 入口，才能核对资产与样式的静态引用。')
    checked_styles = []
    for row in stylesheet_rows:
        if not isinstance(row, dict): issue('STYLESHEET_RECORD_INVALID', '样式记录必须包含 file。'); continue
        if row.get('required') is False: continue
        try:
            p = local_path(root, row.get('file'))
            if p.suffix.lower() != '.css' or not p.is_file(): raise ValueError('stylesheet missing or not CSS')
            if not stylesheet_valid(p):
                raise ValueError('no stylesheet rule or import found')
            if p not in loaded_styles: raise ValueError('stylesheet has no actual stylesheet link/import from entrypoints')
            checked_styles.append({'file': str(p.relative_to(root)), 'role': row.get('role'), 'reference_checked': True})
        except (ValueError, OSError, UnicodeError) as e:
            issue('STYLESHEET_UNVERIFIED', '{}: {}'.format(row.get('file'), e))
    for role, required in (('recipes', require_recipes), ('theme', require_theme)):
        if not required: continue
        candidates = [p for p in loaded_styles if p.name == role + '.css']
        candidates += [root / x['file'] for x in checked_styles if x['role'] == role]
        if not candidates: issue(role.upper() + '_NOT_LOADED', '要求的 {} 样式没有实际入口引用证据。'.format(role))
        for p in set(candidates):
            if not stylesheet_valid(p): issue('STYLESHEET_UNVERIFIED', '{} contains no stylesheet rule or import'.format(p.name))

    checked_assets = []; assets_by_path = {}
    for row in asset_rows:
        if not isinstance(row, dict): issue('ASSET_RECORD_INVALID', '资产记录必须包含 file。'); continue
        if row.get('required') is False: continue
        try:
            p = local_path(root, row.get('file'))
            if not p.is_file(): raise ValueError('asset does not exist')
            fmt = media_format(p)
            embedded_match = hashlib.sha256(p.read_bytes()).hexdigest() in embedded
            if p not in reachable and not embedded_match: raise ValueError('asset is not referenced by entrypoints/loaded CSS')
            provider, source, role = row.get('provider'), row.get('source'), row.get('role')
            if any(not isinstance(v, str) or not v.strip() for v in (provider, source, role)):
                raise ValueError('provider, source URL/tool ID and role must be declared; filenames are not provenance')
            identity = (provider.strip().lower(), source.strip(), role.strip().lower())
            if p in assets_by_path:
                if assets_by_path[p] != identity:
                    issue('ASSET_RECORD_CONFLICT', '{} has conflicting provider/source/role declarations'.format(p.relative_to(root)))
                continue
            assets_by_path[p] = identity
            checked_assets.append({'file': str(p.relative_to(root)), 'format': fmt, 'provider': provider.strip(),
                                   'role': role.strip().lower(), 'source': source.strip(), 'source_declared': True,
                                   'source_authenticity_verified': False, 'reference_checked': True,
                                   'embedded_content_match': embedded_match})
        except (ValueError, OSError, ET.ParseError, UnicodeError, struct.error, zlib.error) as e:
            issue('ASSET_UNVERIFIED', '{}: {}'.format(row.get('file'), e))
    iconscout = [x for x in checked_assets if x['provider'].strip().lower() == 'iconscout']
    avatars = [x for x in checked_assets if x['role'] == 'avatar']
    photos = [x for x in checked_assets if x['role'] == 'photo']
    if require_iconscout and not iconscout: issue('ICONSCOUT_EVIDENCE_MISSING', '没有有效、已引用且声明 IconScout 来源的资产；登记文件或文件名不构成证据。')
    if len(avatars) < require_avatars: issue('AVATAR_EVIDENCE_MISSING', '有效且已引用的头像资产少于要求；头像含义与质量仍需看图。')
    if require_photos and not photos: issue('PHOTO_EVIDENCE_MISSING', '没有有效、已引用并声明摄影角色与来源的资产；真实摄影身份仍需核验。')

    passed = not issues
    return {'passed': passed, 'status': ('FAILED' if not passed else 'CHECKED' if requested else 'NO_REQUIREMENTS_REQUESTED'),
            'task_dir': str(root), 'issue_count': len(issues), 'issues': issues,
            'found': {'recipes_css': [str(p) for p in loaded_styles if p.name == 'recipes.css'],
                      'theme_css': [str(p) for p in loaded_styles if p.name == 'theme.css'],
                      'iconscout_files_count': len(iconscout)},
            'coverage': {'entrypoints': [str(p.relative_to(root)) for p in entries],
                         'stylesheets': 'checked' if stylesheet_rows or require_recipes or require_theme else 'not_requested',
                         'assets': 'checked' if asset_rows else 'unverified' if require_iconscout or require_avatars or require_photos else 'not_requested'},
            'stylesheets': checked_styles, 'assets': checked_assets,
            'execution_verified': False, 'license_verified': False, 'visual_quality_verified': False,
            'limits': 'Local structural file checks and literal HTML/CSS references only; stylesheet evidence needs stylesheet link/import edges. Exact embedded content matches are supported; base href resolution is unverified. Does not prove acquisition execution, source authenticity, license rights, live CSS effects, runtime JS loading, semantic fit or visual quality.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('task_dir')
    ap.add_argument('--manifest', help='Existing asset record JSON; file paths relative to task_dir')
    ap.add_argument('--entrypoint', action='append', dest='entrypoints', help='Actual relative HTML entry; repeatable')
    ap.add_argument('--require-stylesheet', action='append', dest='require_stylesheets', help='Relative CSS file; repeatable')
    ap.add_argument('--require-recipes', action='store_true', help='Require reachable recipes stylesheet evidence')
    ap.add_argument('--require-theme', action='store_true', help='Require reachable theme stylesheet evidence')
    ap.add_argument('--require-iconscout', action='store_true', help='Require referenced valid asset with declared IconScout source')
    ap.add_argument('--require-avatars', type=int, default=0)
    ap.add_argument('--require-photos', action='store_true')
    args = vars(ap.parse_args()); args['task_dir'] = Path(args['task_dir'])
    rep = verify(**args)
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0 if rep['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
