#!/usr/bin/env python3
"""Resolve bundled design libraries or fetch one pinned, verified resource.

Importing this module has no I/O side effects. Directory lookup never downloads
or creates anything; callers opt into a single-file download via resource_file.
"""

import hashlib
from http.client import HTTPException
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import time
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import HTTPRedirectHandler, ProxyHandler, build_opener


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'https://github.com/junqicheng765-oss/fusion-product-agent'
LIBRARY_IDS = frozenset(('style-presets', 'color-presets', 'component-recipes',
                         'ui-ux-pro-max-data'))
MAX_RESOURCE_BYTES = 32 * 1024 * 1024
MAX_CONFIG_BYTES = 16 * 1024 * 1024
DOWNLOAD_TIMEOUT_SECONDS = 20
DOWNLOAD_DEADLINE_SECONDS = 60


class ResourceError(Exception):
    """A concise error about a library profile, local file, or download."""


def _library_id(value):
    if not isinstance(value, str) or value not in LIBRARY_IDS:
        raise ResourceError('unknown design resource library: ' + str(value))
    return value


def _parts(relative):
    """Validate the original spelling, before Path can normalize dot segments."""
    if (not isinstance(relative, str) or not relative or
            any(ord(character) < 32 or ord(character) == 127 for character in relative) or
            any(character in relative for character in '\\:*?<>|"')):
        raise ResourceError('resource path must be a safe relative file path')
    parts = relative.split('/')
    if any(part in ('', '.', '..') or part.endswith((' ', '.')) for part in parts):
        raise ResourceError('resource path must stay inside its library: ' + relative)
    return parts


def _absolute(path):
    try:
        value = os.fspath(path)
        if not isinstance(value, str) or not value or '\x00' in value:
            raise ResourceError('resource location must be a nonempty filesystem path')
        # Do not resolve symlinks: every original ancestor must be checked below.
        return Path(value).expanduser().absolute()
    except (TypeError, ValueError, RuntimeError, OSError) as exc:
        raise ResourceError('invalid resource location: ' + str(exc)) from None


def _safe_path(path, kind=None, create=False):
    """Reject symlinks and non-directory ancestors, including above a root."""
    path = _absolute(path)
    for item in (*reversed(path.parents), path):
        try:
            mode = item.lstat().st_mode
        except FileNotFoundError:
            if create:
                try:
                    item.mkdir()
                except FileExistsError:
                    pass
                mode = item.lstat().st_mode
            else:
                continue
        if stat.S_ISLNK(mode):
            raise ResourceError('symlink resource location is forbidden: ' + str(item))
        expected_directory = item != path or kind == 'directory' or create
        if expected_directory and not stat.S_ISDIR(mode):
            raise ResourceError('resource directory is not a directory: ' + str(item))
        if item == path and kind == 'file' and not stat.S_ISREG(mode):
            raise ResourceError('resource location is not a regular file: ' + str(item))
    return path


def _existing(path, kind):
    path = _safe_path(path, kind)
    return path if path.exists() else None


def _read_file(path, limit, expected=None):
    """Read only a regular file, with a byte limit and optional integrity check."""
    path = _safe_path(path, 'file')
    descriptor = None
    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) |
                             getattr(os, 'O_NONBLOCK', 0))
        with os.fdopen(descriptor, 'rb') as handle:
            descriptor = None
            info = os.fstat(handle.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise ResourceError('resource location is not a regular file: ' + str(path))
            if info.st_size > limit:
                raise ResourceError('resource exceeds size limit: ' + str(path))
            digest = hashlib.sha256()
            content = [] if expected is None else None
            total = 0
            while True:
                chunk = handle.read(min(64 * 1024, limit - total + 1))
                if not chunk:
                    break
                total += len(chunk)
                if total > limit:
                    raise ResourceError('resource exceeds size limit: ' + str(path))
                digest.update(chunk)
                if content is not None:
                    content.append(chunk)
            if expected is not None:
                if total != expected['bytes']:
                    raise ResourceError('resource byte count mismatch: ' + str(path))
                if digest.hexdigest() != expected['sha256']:
                    raise ResourceError('resource sha256 mismatch: ' + str(path))
            _safe_path(path, 'file')
            return b''.join(content) if content is not None else path
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _load_store():
    path = _safe_path(SKILL_ROOT / 'resource-adapters/library-store.json', 'file')
    if not path.exists():
        raise ResourceError('design resource library-store.json is missing; use a bundled library or configure the pinned resource store')
    try:
        store = json.loads(_read_file(path, MAX_CONFIG_BYTES).decode('utf-8'))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ResourceError('cannot read design resource library-store.json: ' + str(exc)) from None
    if not isinstance(store, dict) or type(store.get('schema_version')) is not int or store['schema_version'] != 1:
        raise ResourceError('unsupported design resource store schema_version')
    if store.get('repository') != REPOSITORY:
        raise ResourceError('design resource repository must be ' + REPOSITORY)
    revision = store.get('revision')
    if not isinstance(revision, str) or not re.fullmatch(r'[0-9a-fA-F]{40}', revision):
        raise ResourceError('design resource revision must be a pinned 40-character commit hash')
    libraries = store.get('libraries')
    if not isinstance(libraries, dict) or not libraries:
        raise ResourceError('design resource store libraries must be a nonempty object')
    for library_id, profile in libraries.items():
        _library_id(library_id)
        if not isinstance(profile, dict):
            raise ResourceError('invalid design resource library profile: ' + library_id)
        if profile.get('path') != 'libraries/' + library_id:
            raise ResourceError('design resource library path must be libraries/' + library_id)
        files = profile.get('files')
        if not isinstance(files, dict):
            raise ResourceError('design resource library files must be an object: ' + library_id)
        for relative, record in files.items():
            _parts(relative)
            if not isinstance(record, dict):
                raise ResourceError('invalid resource metadata: ' + relative)
            digest, size = record.get('sha256'), record.get('bytes')
            if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
                raise ResourceError('invalid resource sha256: ' + relative)
            if type(size) is not int or size < 0 or size > MAX_RESOURCE_BYTES:
                raise ResourceError('invalid resource bytes or size limit exceeded: ' + relative)
    return {**store, 'revision': revision.lower()}


def _context(library_id):
    store = _load_store()
    profile = store['libraries'].get(library_id)
    if profile is None:
        raise ResourceError('design resource library profile is missing: ' + library_id)
    explicit_root = os.environ.get('FUSION_DESIGN_RESOURCE_ROOT')
    local = None
    if explicit_root:
        local = _safe_path(_absolute(explicit_root) / profile['path'], 'directory')
    cache_value = os.environ.get('FUSION_DESIGN_RESOURCE_CACHE')
    cache_base = _absolute(cache_value) if cache_value else Path.home() / '.cache/fusion-product-agent/design-resources'
    cache = _absolute(cache_base) / store['revision'] / library_id
    return store, profile, local, cache


def resource_directory(library_id, bundled_root=None):
    """Locate a library directory without fetching, creating, or hashing files.

    The external/cache directory may not exist yet. This is a location lookup,
    not a promise that all manifest resources have been downloaded.
    """
    try:
        library_id = _library_id(library_id)
        if bundled_root is not None:
            bundled = _existing(bundled_root, 'directory')
            if bundled is not None:
                return bundled
        _store, _profile, local, cache = _context(library_id)
        return local if local is not None else _safe_path(cache, 'directory')
    except OSError as exc:
        raise ResourceError('cannot locate design resource directory: ' + str(exc)) from None


class PinnedResourceRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        raise ResourceError('resource download redirect is forbidden; expected the pinned commit URL')


def open_resource(url, timeout):
    # No credential files, authorization headers, or environment proxy credentials.
    return build_opener(ProxyHandler({}), PinnedResourceRedirectHandler()).open(url, timeout=timeout)


def _download(store, profile, relative, record, cache):
    target = _safe_path(cache / relative, 'file')
    parent = _safe_path(target.parent, 'directory', create=True)
    url = ('https://raw.githubusercontent.com/' + REPOSITORY.removeprefix('https://github.com/') +
           '/' + store['revision'] + '/' + quote(profile['path'] + '/' + relative, safe='/'))
    temporary = None
    try:
        started = time.monotonic()
        digest, total = hashlib.sha256(), 0
        with open_resource(url, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
            length = response.headers.get('Content-Length')
            if length is not None:
                try:
                    declared = int(length)
                except (ValueError, TypeError):
                    raise ResourceError('resource server returned an invalid Content-Length') from None
                if declared < 0 or declared > MAX_RESOURCE_BYTES:
                    raise ResourceError('download exceeds resource size limit')
                if declared != record['bytes']:
                    raise ResourceError('downloaded resource byte count mismatch (Content-Length)')
            with tempfile.NamedTemporaryFile(mode='wb', prefix='.download-', suffix='.tmp',
                                             dir=parent, delete=False) as handle:
                temporary = Path(handle.name)
                while True:
                    if time.monotonic() - started > DOWNLOAD_DEADLINE_SECONDS:
                        raise ResourceError('resource download exceeded time limit')
                    chunk = response.read1(min(64 * 1024, record['bytes'] - total + 1))
                    if time.monotonic() - started > DOWNLOAD_DEADLINE_SECONDS:
                        raise ResourceError('resource download exceeded time limit')
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_RESOURCE_BYTES:
                        raise ResourceError('download exceeds resource size limit')
                    if total > record['bytes']:
                        raise ResourceError('downloaded resource byte count mismatch')
                    digest.update(chunk)
                    handle.write(chunk)
                handle.flush()
                os.fsync(handle.fileno())
        if total != record['bytes']:
            raise ResourceError('downloaded resource byte count mismatch')
        if digest.hexdigest() != record['sha256']:
            raise ResourceError('downloaded resource sha256 mismatch')
        _safe_path(target, 'file')
        try:
            # Atomic publication with no replacement, including a concurrent writer.
            os.link(temporary, target, follow_symlinks=False)
        except FileExistsError:
            return _read_file(target, MAX_RESOURCE_BYTES, record)
        return target
    except (URLError, TimeoutError, OSError, HTTPException) as exc:
        raise ResourceError('resource download failed; no verified cached file is available: ' + str(exc)) from None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def resource_file(library_id, relative, bundled_path=None):
    """Return one regular resource file, downloading only if no local copy exists.

    Existing bundled files keep older packages and caller-owned fixtures working
    without a manifest. External mirrors and every cache hit must match the
    pinned manifest; a missing explicit mirror never falls back to the network.
    """
    try:
        library_id = _library_id(library_id)
        _parts(relative)
        if bundled_path is not None:
            bundled = _existing(bundled_path, 'file')
            if bundled is not None:
                if bundled.stat().st_size > MAX_RESOURCE_BYTES:
                    raise ResourceError('bundled resource exceeds size limit: ' + str(bundled))
                return bundled
        store, profile, local, cache = _context(library_id)
        record = profile['files'].get(relative)
        if record is None:
            raise ResourceError('resource file is not listed in library ' + library_id + ': ' + relative)
        if local is not None:
            target = _existing(local / relative, 'file')
            if target is None:
                raise ResourceError('resource file is missing from explicit FUSION_DESIGN_RESOURCE_ROOT: ' + str(local / relative))
            return _read_file(target, MAX_RESOURCE_BYTES, record)
        target = _existing(cache / relative, 'file')
        if target is not None:
            return _read_file(target, MAX_RESOURCE_BYTES, record)
        return _download(store, profile, relative, record, cache)
    except OSError as exc:
        raise ResourceError('cannot read design resource: ' + str(exc)) from None
