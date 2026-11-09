#!/usr/bin/env python3
"""Find packaged visual references; validate integrity only when requested.

Commands:
  python3 visual_reference.py list
  python3 visual_reference.py search <keyword> --role <role>
  python3 visual_reference.py show <reference-id>
  python3 visual_reference.py validate
"""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys


SKILL_ROOT = Path(__file__).resolve().parents[1]
LIBRARY_ROOT = SKILL_ROOT / 'visual-reference-library'
FAMILIES = (
    'tactile-3d', 'paper-collage', 'illustration-print', 'type-graphics',
    'photo-scene', 'optical-tech', 'cultural-oriental',
)
ROLES = ('composition', 'kv', 'lettering', 'palette', 'material', 'icons')
TAG_FIELDS = ('style', 'composition', 'material', 'lettering', 'color', 'icons')
OBSERVATION_FIELDS = ('composition', 'materials', 'typography', 'colors', 'icons')
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


def image_path(relative):
    """Reject traversal, absolute paths, and symlinks before opening an asset."""
    if not isinstance(relative, str) or not relative or '\\' in relative or '\x00' in relative:
        raise LibraryError('invalid image path')
    parts = relative.split('/')
    pure = PurePosixPath(relative)
    if pure.is_absolute() or re.match(r'^[A-Za-z]:', relative) or len(parts) < 2 or parts[0] != 'images' or any(part in ('', '.', '..') for part in parts):
        raise LibraryError('image path must stay relative to images/: ' + relative)
    path = LIBRARY_ROOT
    for part in parts:
        path = path / part
        if path.is_symlink():
            raise LibraryError('symlink image path is forbidden: ' + relative)
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError):
        raise LibraryError('image file is missing or inaccessible: ' + relative) from None
    if not resolved.is_relative_to(LIBRARY_ROOT.resolve()) or not resolved.is_file():
        raise LibraryError('image path is not a file inside the library: ' + relative)
    return resolved


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
    for _rank, record, matches in ranked[:args.limit]:
        date = record['source']['publication_date']
        results.append({'id': record['id'], 'title': record['title'], 'summary': record['summary'],
                        'image_path': str(image_path(record['file'])), 'families': record['families'],
                        'roles': record['roles'], 'tags': {key: values[:3] for key, values in record['tags'].items() if values},
                        'matched_fields': matches, 'publication_date': date,
                        'date_note': '原作日期未知' if date is None else '原作日期：' + date})
    return {'ok': True, 'command': 'search', 'query': terms,
            'filters': {'role': args.role, 'family': args.family}, 'limit': args.limit,
            'total_matches': len(ranked), 'returned': len(results), 'results': results, 'note': SEARCH_NOTE}


def cmd_show(catalog, args):
    for record in catalog['images']:
        if record['id'] == args.id:
            return {**record, 'ok': True, 'command': 'show', 'image_path': str(image_path(record['file']))}
    raise LibraryError('unknown reference id: ' + args.id)


def digest_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def cmd_validate(catalog, _args):
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
    listed = set()
    for record in catalog['images']:
        listed.add(record['file'])
        try:
            path = image_path(record['file'])
            if digest_file(path) != record['sha256']:
                errors.append(record['id'] + ': sha256 mismatch')
            else:
                verified_hashes += 1
        except (LibraryError, OSError) as exc:
            errors.append(record['id'] + ': ' + str(exc))
    images_root = LIBRARY_ROOT / 'images'
    actual = set()
    if images_root.is_symlink():
        errors.append('images directory must not be a symlink')
    elif not images_root.is_dir():
        errors.append('images directory is missing')
    else:
        for path in images_root.rglob('*'):
            relative = path.relative_to(LIBRARY_ROOT).as_posix()
            if path.is_symlink():
                errors.append('symlink resource is forbidden: ' + relative)
            elif path.is_file():
                actual.add(relative)
    for relative in sorted(listed - actual):
        errors.append('catalog image absent from resource set: ' + relative)
    for relative in sorted(actual - listed):
        errors.append('unlisted image resource: ' + relative)
    return {'ok': not errors, 'command': 'validate', 'image_count': len(catalog['images']),
            'verified_hashes': verified_hashes,
            'error_count': len(errors), 'errors': errors[:20],
            'additional_error_count': max(0, len(errors) - 20)}


def parser():
    root = JsonArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest='command', required=True, parser_class=JsonArgumentParser)
    sub.add_parser('list', help='List family and role counts without listing every image').set_defaults(run=cmd_list)
    search = sub.add_parser('search', help='Match every whitespace-separated keyword; exact tags rank first')
    search.add_argument('keywords', nargs='+')
    search.add_argument('--role', choices=ROLES)
    search.add_argument('--family', choices=FAMILIES)
    search.add_argument('--limit', type=int, default=6)
    search.set_defaults(run=cmd_search)
    show = sub.add_parser('show', help='Show complete metadata and an absolute installed image path')
    show.add_argument('id')
    show.set_defaults(run=cmd_show)
    sub.add_parser('validate', help='Check metadata, paths, all hashes, resource sets, and indexes').set_defaults(run=cmd_validate)
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
