#!/usr/bin/env python3
"""Rebuild semantics indices from reference frontmatter.

Generates:
  - memory/semantics/_index.md    (master reference list)
  - memory/semantics/_tags.md     (tag → reference ID inverted index)

Usage:
    python3 scripts/build-index.py
"""

from __future__ import annotations

import glob
import os
import re
import sys
import tempfile
from collections import defaultdict
from datetime import date

# Resolve the semantics directory. The installed layout ($GYEOL_HOME) uses
# memory/semantics, while the repo's own gitignored dev memory uses
# .memory/semantics. Prefer the installed layout and fall back to the dev
# layout when only that one is present.
_GYEOL_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEMANTICS_DIR = os.path.join(_GYEOL_HOME, 'memory', 'semantics')
if not os.path.isdir(SEMANTICS_DIR) and os.path.isdir(
        os.path.join(_GYEOL_HOME, '.memory', 'semantics')):
    SEMANTICS_DIR = os.path.join(_GYEOL_HOME, '.memory', 'semantics')

_ARRAY_TOKEN_RE = re.compile(
    r'\s*(?:"([^"]*)"|\'([^\']*)\'|([^,]+?))\s*(?:,|$)'
)


def parse_yaml_array(inner: str) -> list[str]:
    """Parse inline YAML array items (double-quoted, single-quoted, or unquoted)."""
    inner = inner.strip()
    if not inner:
        return []
    items: list[str] = []
    for match in _ARRAY_TOKEN_RE.finditer(inner):
        if match.group(0).strip() == '':
            continue
        val = (
            match.group(1)
            if match.group(1) is not None
            else match.group(2)
            if match.group(2) is not None
            else (match.group(3) or '').strip()
        )
        if val != '':
            items.append(val)
    return items


def ref_id_sort_key(ref_id: int | str) -> tuple[int, int, str]:
    """Sort numeric IDs first by integer value, then string IDs lexicographically."""
    if isinstance(ref_id, int):
        return (0, ref_id, '')
    s = str(ref_id).strip()
    if s.isdigit():
        return (0, int(s), '')
    return (1, 0, s)


def parse_frontmatter(filepath: str) -> dict | None:
    """Parse YAML frontmatter from a markdown file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.match(r'^---\s*\n(.+?)\n---', content, re.DOTALL)
    if not match:
        return None

    fm = {}
    for line in match.group(1).split('\n'):
        # Simple key: value parsing
        kv = re.match(r'^(\w+):\s*(.*)$', line)
        if not kv:
            continue
        key = kv.group(1)
        value = kv.group(2).strip()

        # Parse arrays: ["a", "b"], ['a', 'b'], [a, b], or []
        array_match = re.match(r'^\[(.*)\]$', value)
        if array_match is not None:
            fm[key] = parse_yaml_array(array_match.group(1))
        # Parse double-quoted strings
        elif len(value) >= 2 and value.startswith('"') and value.endswith('"'):
            fm[key] = value[1:-1]
        # Parse single-quoted strings
        elif len(value) >= 2 and value.startswith("'") and value.endswith("'"):
            fm[key] = value[1:-1]
        # Parse numbers
        elif re.match(r'^\d+$', value):
            fm[key] = int(value)
        else:
            fm[key] = value

    return fm


def collect_references() -> list[tuple[str, dict]]:
    """Collect all reference files and their frontmatter."""
    summary_dir = os.path.join(SEMANTICS_DIR, 'summary')
    pattern = os.path.join(summary_dir, '[0-9]*-*.md')
    files = sorted(glob.glob(pattern))
    refs = []
    for f in files:
        basename = os.path.basename(f)
        fm = parse_frontmatter(f)
        if fm and 'id' in fm and fm['id'] != '':
            refs.append((basename, fm))
    return refs


def build_master_index(refs: list[tuple[str, dict]]) -> str:
    """Generate _index.md content."""
    lines = [
        '# Semantics Index',
        '',
        f'> {len(refs)}건의 레퍼런스 ({date.today().isoformat()} 기준)',
        '',
        '| ID | Title | Type | Year | Topics | File |',
        '|-----|-------|------|------|--------|------|',
    ]

    for filename, fm in sorted(
        refs, key=lambda x: (ref_id_sort_key(x[1].get('id', '')), x[0])
    ):
        ref_id = fm.get('id', '')
        title = fm.get('title', '')
        ref_type = fm.get('type', '')
        year = fm.get('year', '')
        raw_topics = fm.get('topics', [])
        topics = (
            ', '.join(str(t) for t in raw_topics)
            if isinstance(raw_topics, list)
            else str(raw_topics)
        )
        lines.append(
            f'| {ref_id} | {title} | {ref_type} | {year} | {topics} | [{filename}](./summary/{filename}) |'
        )

    lines.append('')
    return '\n'.join(lines)


def build_tag_index(refs: list[tuple[str, dict]]) -> str:
    """Generate _tags.md content (inverted index: tag → reference IDs)."""
    tag_map: dict[str, list[int | str]] = defaultdict(list)

    for _, fm in refs:
        ref_id = fm.get('id', '')
        if ref_id == '':
            continue
        raw_tags = fm.get('tags', [])
        tags = raw_tags if isinstance(raw_tags, list) else ([raw_tags] if raw_tags else [])
        for tag in tags:
            tag_map[str(tag)].append(ref_id)

    lines = [
        '# Tag Index',
        '',
        f'> {len(tag_map)}개의 태그, {len(refs)}건의 레퍼런스 ({date.today().isoformat()} 기준)',
        '',
    ]

    for tag in sorted(tag_map.keys()):
        ids = sorted(tag_map[tag], key=ref_id_sort_key)
        id_str = ', '.join(str(i) for i in ids)
        lines.append(f'## {tag}')
        lines.append(f'{id_str}')
        lines.append('')

    return '\n'.join(lines)


def atomic_write_text(target_path: str, content: str) -> None:
    """Write content to target_path atomically via a same-directory temp file."""
    target_dir = os.path.dirname(os.path.abspath(target_path))
    os.makedirs(target_dir, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        prefix='.tmp-', dir=target_dir, text=True
    )
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
        os.replace(tmp_path, target_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def ensure_dirs():
    """Create required directories if they don't exist."""
    os.makedirs(os.path.join(SEMANTICS_DIR, 'summary'), exist_ok=True)
    os.makedirs(os.path.join(SEMANTICS_DIR, '_topics'), exist_ok=True)


def main():
    ensure_dirs()

    refs = collect_references()
    master_index = build_master_index(refs)
    tag_index = build_tag_index(refs)

    # Write _index.md atomically after generation succeeds
    index_path = os.path.join(SEMANTICS_DIR, '_index.md')
    atomic_write_text(index_path, master_index)
    print(f'  _index.md: {len(refs)} references')

    # Write _tags.md atomically after generation succeeds
    tags_path = os.path.join(SEMANTICS_DIR, '_tags.md')
    atomic_write_text(tags_path, tag_index)

    tag_count = len(set(
        str(tag)
        for _, fm in refs
        for tag in (fm.get('tags', []) if isinstance(fm.get('tags', []), list) else [])
    ))
    print(f'  _tags.md: {tag_count} tags')

    print(f'\nDone. {len(refs)} references indexed.')


if __name__ == '__main__':
    main()
