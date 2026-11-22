#!/usr/bin/env python3
"""Search a small visual catalog and fetch selected references on demand.

Commands:
  python3 visual_reference.py list
  python3 visual_reference.py search <keyword> --role <role>
  python3 visual_reference.py show <reference-id>
  python3 visual_reference.py validate
  python3 visual_reference.py validate --resources
"""

import argparse
import hashlib
from http.client import HTTPException
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import HTTPRedirectHandler, build_opener


SKILL_ROOT = Path(__file__).resolve().parents[1]
LIBRARY_ROOT = SKILL_ROOT / 'visual-reference-library'
FAMILIES = (
    'tactile-3d', 'paper-collage', 'illustration-print', 'type-graphics',
    'photo-scene', 'optical-tech', 'cultural-oriental',
)
ROLES = ('composition', 'kv', 'lettering', 'palette', 'material', 'icons')
TAG_FIELDS = ('style', 'composition', 'material', 'lettering', 'color', 'icons')
OBSERVATION_FIELDS = ('composition', 'materials', 'typography', 'colors', 'icons')
MAX_RESOURCE_BYTES = 32 * 1024 * 1024
DOWNLOAD_TIMEOUT_SECONDS = 20
DOWNLOAD_DEADLINE_SECONDS = 60
SEARCH_NOTE = '匹配顺序仅表示检索相关性，不代表审美质量或流行度；原作日期未知时不能以整理日期代替。'


class LibraryError(Exception):
    """A concise, user-facing argument, metadata, or resource error."""


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise LibraryError(message)


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def string_list(value):
    return isinstance(value, list) and all(isinstance(item, str) and item for item in value)


def metadata_errors(catalog):
    """Check the searchable contract without opening or hashing image files."""
    errors = []
    if not isinstance(catalog, dict):
        return ['catalog must be an object']
    if type(catalog.get('schema_version')) is not int or catalog['schema_version'] != 1:
        errors.append('unsupported catalog schema_version')
    if catalog.get('scope') != 'global-visual-reference':
        errors.append('catalog scope must be global-visual-reference')
    if not isinstance(catalog.get('curated_on'), str):
        errors.append('catalog curated_on must be a string')
    for name, allowed in (('families', FAMILIES), ('roles', ROLES)):
        definitions = catalog.get(name)
        if not isinstance(definitions, list) or not all(isinstance(item, dict) for item in definitions):
            errors.append(name + ' must contain definition objects')
            continue
        ids = [item.get('id') for item in definitions]
        if len(ids) != len(set(item for item in ids if isinstance(item, str))) or set(item for item in ids if isinstance(item, str)) != set(allowed):
            errors.append(name + ' definitions must contain each supported enum exactly once')
        if any(not isinstance(item.get('label'), str) or not item['label'] for item in definitions):
            errors.append(name + ' definitions require labels')
        if name == 'families' and any(not isinstance(item.get('description'), str) for item in definitions):
            errors.append('family definitions require descriptions')
    images = catalog.get('images')
    if not isinstance(images, list):
        errors.append('images must be an array')
        return errors
    seen = {'id': set(), 'sha256': set(), 'file': set()}
    for position, record in enumerate(images):
        prefix = 'images[' + str(position) + ']'
        if not isinstance(record, dict):
            errors.append(prefix + ' must be an object')
            continue
        label = record.get('id') if isinstance(record.get('id'), str) else prefix
        for key in ('id', 'sha256', 'file', 'title', 'summary'):
            value = record.get(key)
            if not isinstance(value, str) or not value:
                errors.append(label + ': ' + key + ' must be a nonempty string')
                continue
            if key in seen:
                if value in seen[key]:
                    errors.append(label + ': duplicate ' + key)
                seen[key].add(value)
        if isinstance(record.get('file'), str):
            try:
                image_parts(record['file'])
            except LibraryError as exc:
                errors.append(label + ': ' + str(exc))
        if isinstance(record.get('sha256'), str) and not re.fullmatch(r'[0-9a-f]{64}', record['sha256']):
            errors.append(label + ': invalid sha256')
        for key in ('width', 'height'):
            if type(record.get(key)) is not int or record[key] <= 0:
                errors.append(label + ': ' + key + ' must be a positive integer')
        for key, allowed in (('families', FAMILIES), ('roles', ROLES)):
            values = record.get(key)
            if not string_list(values) or not values or len(values) != len(set(values)) or not set(values).issubset(allowed):
                errors.append(label + ': invalid ' + key + ' enum values')
        for key, fields in (('tags', TAG_FIELDS), ('observations', OBSERVATION_FIELDS)):
            values = record.get(key)
            if not isinstance(values, dict) or set(values) != set(fields) or any(not string_list(values.get(field)) for field in fields):
                errors.append(label + ': invalid ' + key + ' fields')
        review = record.get('review')
        if not isinstance(review, dict) or review.get('decision') != 'include' or review.get('ui_reference') is not False or not isinstance(review.get('reason'), str):
            errors.append(label + ': review must include a non-UI reference')
        source = record.get('source')
        if not isinstance(source, dict):
            errors.append(label + ': source must be an object')
        else:
            if not isinstance(source.get('filename'), str) or not source['filename']:
                errors.append(label + ': source filename is required')
            if source.get('url_hint') is not None and not isinstance(source.get('url_hint'), str):
                errors.append(label + ': invalid source url_hint')
            if type(source.get('url_verified')) is not bool:
                errors.append(label + ': source url_verified must be boolean')
            if 'publication_date' not in source or (source['publication_date'] is not None and not isinstance(source['publication_date'], str)):
                errors.append(label + ': invalid publication_date')
            if not isinstance(source.get('license_status'), str):
                errors.append(label + ': source license_status is required')
        if not string_list(record.get('limitations')):
            errors.append(label + ': limitations must be an array of strings')
    return errors


def require_library():
    if LIBRARY_ROOT.is_symlink():
        raise LibraryError('reference library must not be a symlink')
    if not LIBRARY_ROOT.is_dir():
        raise LibraryError('reference library is missing beside this Skill')
    catalog_path = LIBRARY_ROOT / 'catalog.json'
    if catalog_path.is_symlink():
        raise LibraryError('catalog.json must not be a symlink')
    if not catalog_path.is_file():
        raise LibraryError('reference catalog.json is missing')
    return catalog_path


def load_catalog():
    path = require_library()
    try:
        catalog = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LibraryError('cannot read reference catalog: ' + str(exc)) from None
    errors = metadata_errors(catalog)
    if errors:
        raise LibraryError('; '.join(errors[:6]) + ('; additional metadata errors omitted' if len(errors) > 6 else ''))
    return catalog


def image_parts(relative):
    """Validate catalog paths before any filesystem or URL operation."""
    if not isinstance(relative, str) or not relative or '\\' in relative or '\x00' in relative:
        raise LibraryError('invalid image path')
    parts = relative.split('/')
    pure = PurePosixPath(relative)
    if pure.is_absolute() or re.match(r'^[A-Za-z]:', relative) or len(parts) < 2 or parts[0] != 'images' or any(part in ('', '.', '..') or re.match(r'^[A-Za-z]:', part) for part in parts):
        raise LibraryError('image path must stay relative to images/: ' + relative)
    return parts


def safe_resource_path(root, relative):
    """Return an existing regular file, or None; never follow a resource symlink."""
    parts = image_parts(relative)
    root = Path(root).expanduser().absolute()
    if root.is_symlink():
        raise LibraryError('resource root must not be a symlink: ' + str(root))
    if root.exists() and not root.is_dir():
        raise LibraryError('resource root must be a directory: ' + str(root))
    path = root
    for part in parts:
        path = path / part
        if path.is_symlink():
            raise LibraryError('symlink image path is forbidden: ' + relative)
    if not path.exists():
        return None
    if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise LibraryError('image path is not a file inside the resource root: ' + relative)
    return path.resolve()


def image_path(relative):
    """Compatibility helper for older bundled libraries."""
    path = safe_resource_path(LIBRARY_ROOT, relative)
    if path is None:
        raise LibraryError('image file is missing or inaccessible: ' + relative)
    return path


def load_resource_store():
    path = LIBRARY_ROOT / 'resource-store.json'
    if path.is_symlink():
        raise LibraryError('resource-store.json must not be a symlink')
    if not path.exists():
        return None  # Older packages keep the actual images beside the catalog.
    try:
        store = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LibraryError('cannot read resource-store.json: ' + str(exc)) from None
    if not isinstance(store, dict) or type(store.get('schema_version')) is not int or store['schema_version'] != 1:
        raise LibraryError('unsupported resource-store schema_version')
    repository = store.get('repository')
    match = re.fullmatch(r'https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?', repository) if isinstance(repository, str) else None
    if not match or match.group(1) in ('.', '..') or match.group(2) in ('.', '..'):
        raise LibraryError('resource repository must be an HTTPS GitHub repository URL')
    revision = store.get('revision')
    if not isinstance(revision, str) or not re.fullmatch(r'[0-9a-fA-F]{40}', revision):
        raise LibraryError('resource revision must be a pinned 40-character commit hash')
    resource_path = store.get('path')
    if not isinstance(resource_path, str) or '\\' in resource_path or any(part in ('', '.', '..') for part in resource_path.split('/')) or resource_path.startswith('/') or not re.fullmatch(r'[A-Za-z0-9_./-]+', resource_path):
        raise LibraryError('resource store path must be a safe relative directory')
    return {**store, 'repository': 'https://github.com/' + match.group(1) + '/' + match.group(2),
            'revision': revision.lower(), 'path': resource_path}


def default_cache_dir():
    configured = os.environ.get('FUSION_VISUAL_CACHE_DIR')
    if configured:
        return Path(configured).expanduser()
    if os.environ.get('XDG_CACHE_HOME'):
        return Path(os.environ['XDG_CACHE_HOME']).expanduser() / 'fusion-product-agent'
    if sys.platform == 'darwin':
        return Path.home() / 'Library/Caches/fusion-product-agent'
    if os.name == 'nt' and os.environ.get('LOCALAPPDATA'):
        return Path(os.environ['LOCALAPPDATA']) / 'fusion-product-agent/cache'
    return Path.home() / '.cache/fusion-product-agent'


def resource_context(args):
    store = load_resource_store()
    local = getattr(args, 'resource_root', None) or os.environ.get('FUSION_VISUAL_RESOURCE_ROOT')
    cache_base = Path(getattr(args, 'cache_dir', None) or default_cache_dir()).expanduser().absolute()
    cache_root = None
    if store:
        namespace = hashlib.sha256((store['repository'] + '/' + store['path']).encode('utf-8')).hexdigest()[:20]
        cache_root = cache_base / 'visual-references' / namespace / store['revision']
    return {'store': store, 'local_root': Path(local).expanduser().absolute() if local else None,
            'cache_base': cache_base, 'cache_root': cache_root}


def check_cache_directories(context, create=False):
    """Only create namespaced cache directories; reject pre-existing symlinks."""
    base, root = context['cache_base'], context['cache_root']
    if root is None:
        return
    paths = [base]
    paths.extend(base / Path(*root.relative_to(base).parts[:length])
                 for length in range(1, len(root.relative_to(base).parts) + 1))
    for path in paths:
        if path.is_symlink():
            raise LibraryError('cache directory must not be a symlink: ' + str(path))
        if path.exists() and not path.is_dir():
            raise LibraryError('cache directory is not a directory: ' + str(path))
        if create:
            path.mkdir(parents=True, exist_ok=True)


def find_local_resource(record, context):
    for status, root in (('bundled', LIBRARY_ROOT), ('local', context['local_root']),
                         ('cached', context['cache_root'])):
        if root is None:
            continue
        if status == 'cached':
            check_cache_directories(context)
        path = safe_resource_path(root, record['file'])
        if path is not None:
            return path, status
    return None, 'missing'


def verified_resource(path, record):
    if path.stat().st_size > MAX_RESOURCE_BYTES:
        raise LibraryError(record['id'] + ': image exceeds resource size limit')
    if digest_file(path) != record['sha256']:
        raise LibraryError(record['id'] + ': sha256 mismatch')
    return path


def resource_url(store, relative):
    image_parts(relative)
    repository = store['repository'].removeprefix('https://github.com/')
    return 'https://raw.githubusercontent.com/' + repository + '/' + store['revision'] + '/' + quote(store['path'] + '/' + relative, safe='/')


class PinnedResourceRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        raise LibraryError('resource download redirect is forbidden; expected the pinned commit URL')


def open_resource(url, timeout):
    return build_opener(PinnedResourceRedirectHandler()).open(url, timeout=timeout)


def download_resource(record, context):
    store, root = context['store'], context['cache_root']
    if store is None:
        raise LibraryError('image resource is missing; no pinned resource-store.json is configured')
    check_cache_directories(context, create=True)
    target = root / record['file']
    # Reuse path validation for each existing descendant before creating directories.
    safe_resource_path(root, record['file'])
    parent = root
    for part in image_parts(record['file'])[:-1]:
        parent = parent / part
        if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
            raise LibraryError('unsafe cache image directory: ' + str(parent))
        parent.mkdir(exist_ok=True)
    temporary = None
    try:
        url = resource_url(store, record['file'])
        started = time.monotonic()
        digest = hashlib.sha256()
        total = 0
        with open_resource(url, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
            length = response.headers.get('Content-Length')
            if length is not None:
                try:
                    declared_size = int(length)
                except (TypeError, ValueError):
                    raise LibraryError('resource server returned an invalid Content-Length') from None
                if declared_size < 0 or declared_size > MAX_RESOURCE_BYTES:
                    raise LibraryError('download exceeds resource size limit')
            with tempfile.NamedTemporaryFile(mode='wb', prefix='.download-', suffix='.tmp', dir=parent, delete=False) as handle:
                temporary = Path(handle.name)
                while True:
                    if time.monotonic() - started > DOWNLOAD_DEADLINE_SECONDS:
                        raise LibraryError('resource download exceeded time limit')
                    chunk = response.read1(64 * 1024)
                    if time.monotonic() - started > DOWNLOAD_DEADLINE_SECONDS:
                        raise LibraryError('resource download exceeded time limit')
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_RESOURCE_BYTES:
                        raise LibraryError('download exceeds resource size limit')
                    digest.update(chunk)
                    handle.write(chunk)
                handle.flush()
                os.fsync(handle.fileno())
        if digest.hexdigest() != record['sha256']:
            raise LibraryError(record['id'] + ': downloaded sha256 mismatch')
        # Check again before the atomic rename so a symlink cannot be overwritten.
        check_cache_directories(context)
        existing = safe_resource_path(root, record['file'])
        if existing is not None:
            return verified_resource(existing, record)
        os.replace(temporary, target)
        temporary = None
        return target.resolve()
    except (URLError, TimeoutError, OSError, HTTPException) as exc:
        raise LibraryError('resource download failed; no verified cached image is available: ' + str(exc)) from None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def expected_indexes(catalog):
    indexes = {'family': {key: [] for key in FAMILIES}, 'role': {key: [] for key in ROLES}, 'tag': {}}
    for record in catalog['images']:
        for key in record['families']:
            indexes['family'][key].append(record['id'])
        for key in record['roles']:
            indexes['role'][key].append(record['id'])
        tags = dict.fromkeys(tag for values in record['tags'].values() for tag in values)
        for tag in tags:
            indexes['tag'].setdefault(tag, []).append(record['id'])
    return indexes


def cmd_list(catalog, _args):
    result = {'ok': True, 'command': 'list', 'scope': catalog['scope'],
              'curated_on': catalog['curated_on'], 'image_count': len(catalog['images'])}
    for field in ('families', 'roles'):
        result[field] = [{**definition, 'count': sum(definition['id'] in item[field] for item in catalog['images'])}
                         for definition in catalog[field]]
    result['note'] = SEARCH_NOTE
    return result


def searchable_fields(record, catalog):
    fields = {key: [record[key]] for key in ('id', 'title', 'summary')}
    for section in ('tags', 'observations'):
        fields.update({section + '.' + key: values for key, values in record[section].items()})
    for section in ('families', 'roles'):
        definitions = {item['id']: item for item in catalog[section]}
        fields[section] = [value for key in record[section]
                           for value in (key, definitions[key]['label'], definitions[key].get('description', '')) if value]
    fields['limitations'] = record['limitations']
    return fields


def cmd_search(catalog, args):
    terms = list(dict.fromkeys(term.casefold() for query in args.keywords for term in query.split() if term))
    if not terms:
        raise LibraryError('search requires at least one nonempty keyword')
    if not 1 <= args.limit <= 12:
        raise LibraryError('--limit must be between 1 and 12')
    ranked = []
    for position, record in enumerate(catalog['images']):
        if args.role and args.role not in record['roles']:
            continue
        if args.family and args.family not in record['families']:
            continue
        fields = searchable_fields(record, catalog)
        matches = []
        exact_count = tag_count = title_count = 0
        for term in terms:
            matched = [name for name, values in fields.items() if any(term in value.casefold() for value in values)]
            if not matched:
                break
            exact_tags = [name for name, values in fields.items() if name.startswith('tags.') and any(term == value.casefold() for value in values)]
            exact_count += bool(exact_tags)
            tag_count += any(name.startswith('tags.') for name in matched)
            title_count += 'title' in matched
            matches.append({'term': term, 'fields': matched, 'exact_tag_fields': exact_tags})
        if len(matches) != len(terms):
            continue
        # Scores are private retrieval mechanics, never a quality or popularity rating.
        ranked.append(((exact_count, tag_count, title_count, -position), record, matches))
    ranked.sort(key=lambda item: item[0], reverse=True)
    results = []
    context = resource_context(args)
    for _rank, record, matches in ranked[:args.limit]:
        date = record['source']['publication_date']
        path, status = find_local_resource(record, context)
        result = {'id': record['id'], 'title': record['title'], 'summary': record['summary'],
                        'file': record['file'], 'resource_status': status, 'families': record['families'],
                        'roles': record['roles'], 'tags': {key: values[:3] for key, values in record['tags'].items() if values},
                        'matched_fields': matches, 'publication_date': date,
                        'date_note': '原作日期未知' if date is None else '原作日期：' + date}
        if path is not None:
            result['image_path'] = str(path)
        results.append(result)
    return {'ok': True, 'command': 'search', 'query': terms,
            'filters': {'role': args.role, 'family': args.family}, 'limit': args.limit,
            'total_matches': len(ranked), 'returned': len(results), 'results': results, 'note': SEARCH_NOTE}


def cmd_show(catalog, args):
    for record in catalog['images']:
        if record['id'] == args.id:
            context = resource_context(args)
            path, status = find_local_resource(record, context)
            if path is None:
                path = download_resource(record, context)
                status = 'downloaded'
            else:
                verified_resource(path, record)
            return {**record, 'ok': True, 'command': 'show', 'image_path': str(path),
                    'resource_status': status}
    raise LibraryError('unknown reference id: ' + args.id)


def digest_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def cmd_validate(catalog, args):
    errors = []
    verified_hashes = 0
    expected = expected_indexes(catalog)
    indexes = catalog.get('indexes')
    if not isinstance(indexes, dict) or set(indexes) != set(expected):
        errors.append('indexes must contain exactly family, role, and tag')
    else:
        for key, values in expected.items():
            if indexes[key] != values:
                errors.append('index mismatch: ' + key)
    context = resource_context(args)
    counts = {'bundled': 0, 'local': 0, 'cached': 0, 'downloaded': 0, 'missing': 0, 'invalid': 0}
    listed = {record['file'] for record in catalog['images']}
    for record in catalog['images']:
        try:
            path, status = find_local_resource(record, context)
            if args.resources:
                if path is None:
                    errors.append(record['id'] + ': image resource is missing locally (validation does not download)')
                else:
                    verified_resource(path, record)
                    verified_hashes += 1
            counts[status] += 1
        except (LibraryError, OSError) as exc:
            counts['invalid'] += 1
            errors.append(record['id'] + ': ' + str(exc))
    if args.resources:
        for resource_root in dict.fromkeys(root for root in (LIBRARY_ROOT, context['local_root']) if root is not None):
            images_root = resource_root / 'images'
            if images_root.is_symlink():
                errors.append('images directory must not be a symlink')
            elif images_root.is_dir():
                for path in images_root.rglob('*'):
                    relative = path.relative_to(resource_root).as_posix()
                    if path.is_symlink():
                        errors.append('symlink resource is forbidden: ' + relative)
                    elif path.is_file() and relative not in listed:
                        errors.append('unlisted image resource: ' + relative)
    return {'ok': not errors, 'command': 'validate', 'mode': 'resources' if args.resources else 'catalog',
            'image_count': len(catalog['images']), 'verified_hashes': verified_hashes,
            'resources': counts, 'resource_revision': context['store']['revision'] if context['store'] else None,
            'error_count': len(errors), 'errors': errors[:20],
            'additional_error_count': max(0, len(errors) - 20)}


def add_resource_options(command):
    command.add_argument('--resource-root', help='Local resource library containing images/ (or FUSION_VISUAL_RESOURCE_ROOT)')
    command.add_argument('--cache-dir', help='Cache base directory (or FUSION_VISUAL_CACHE_DIR)')


def parser():
    root = JsonArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest='command', required=True, parser_class=JsonArgumentParser)
    sub.add_parser('list', help='List family and role counts without listing every image').set_defaults(run=cmd_list)
    search = sub.add_parser('search', help='Match every whitespace-separated keyword; exact tags rank first')
    search.add_argument('keywords', nargs='+')
    search.add_argument('--role', choices=ROLES)
    search.add_argument('--family', choices=FAMILIES)
    search.add_argument('--limit', type=int, default=6)
    add_resource_options(search)
    search.set_defaults(run=cmd_search)
    show = sub.add_parser('show', help='Fetch one verified image if needed and show its complete metadata')
    show.add_argument('id')
    add_resource_options(show)
    show.set_defaults(run=cmd_show)
    validate = sub.add_parser('validate', help='Check catalog and indexes without downloading images')
    validate.add_argument('--resources', action='store_true', help='Also hash all locally available images; never download')
    add_resource_options(validate)
    validate.set_defaults(run=cmd_validate)
    return root


def main(argv=None):
    command = None
    try:
        args = parser().parse_args(argv)
        command = args.command
        result = args.run(load_catalog(), args)
    except (LibraryError, OSError, ValueError) as exc:
        emit({'ok': False, 'command': command, 'error': str(exc)})
        return 2
    emit(result)
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
