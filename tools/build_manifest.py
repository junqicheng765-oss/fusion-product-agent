#!/usr/bin/env python3
"""Refresh the package byte inventory after an intentional source change."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / 'package'
path = root / 'manifest.json'
data = json.loads(path.read_text(encoding='utf-8'))
data['files'] = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(root.rglob('*')) if p.is_file() and p != path
                 and '__pycache__' not in p.parts and not p.name.endswith('.pyc')}
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
