#!/usr/bin/env python3
"""Rebuild semantics indices from reference frontmatter.

Generates:
  - .memory/semantics/_index.md    (master reference list)
  - .memory/semantics/_tags.md     (tag → reference ID inverted index)

Usage:
    python3 scripts/build-index.py
"""

import glob
import os
import re
import sys
from collections import defaultdict
from datetime import date

SEMANTICS_DIR = os.path.join(os.path.dirname(__file__), '..', '.memory', 'semantics')


def parse_frontmatter(filepath: str) -> dict | None:
    """Parse YAML frontmatter from a markdown file."""
    with open(filepath, 'r') as f:
        content = f.read()

    match = re.match(r'^---\s*\n(.+?)\n---', content, re.DOTALL)
    if not match:
        return None

    fm = {}
    for line in match.group(1).split('\n'):
        # Simple key: value parsing
        kv = re.match(r'^(\w+):\s*(.+)$', line)
        if not kv:
            continue
        key = kv.group(1)
        value = kv.group(2).strip()

        # Parse arrays: ["a", "b"]
        array_match = re.match(r'^\[(.+)\]$', value)
        if array_match:
            items = re.findall(r'"([^"]*)"', array_match.group(1))
            fm[key] = items
        # Parse quoted strings
        elif value.startswith('"') and value.endswith('"'):
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
        if fm and 'id' in fm:
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

    for filename, fm in sorted(refs, key=lambda x: int(x[1].get('id', 0))):
        ref_id = fm.get('id', '')
        title = fm.get('title', '')
        ref_type = fm.get('type', '')
        year = fm.get('year', '')
        topics = ', '.join(fm.get('topics', []))
        lines.append(
            f'| {ref_id} | {title} | {ref_type} | {year} | {topics} | [{filename}](./summary/{filename}) |'
        )

    lines.append('')
    return '\n'.join(lines)


def build_tag_index(refs: list[tuple[str, dict]]) -> str:
    """Generate _tags.md content (inverted index: tag → reference IDs)."""
    tag_map: dict[str, list[int]] = defaultdict(list)

    for _, fm in refs:
        ref_id = int(fm.get('id', 0))
        for tag in fm.get('tags', []):
            tag_map[tag].append(ref_id)

    lines = [
        '# Tag Index',
        '',
        f'> {len(tag_map)}개의 태그, {len(refs)}건의 레퍼런스 ({date.today().isoformat()} 기준)',
        '',
    ]

    for tag in sorted(tag_map.keys()):
        ids = sorted(tag_map[tag])
        id_str = ', '.join(str(i) for i in ids)
        lines.append(f'## {tag}')
        lines.append(f'{id_str}')
        lines.append('')

    return '\n'.join(lines)


def ensure_dirs():
    """Create required directories if they don't exist."""
    os.makedirs(os.path.join(SEMANTICS_DIR, 'summary'), exist_ok=True)
    os.makedirs(os.path.join(SEMANTICS_DIR, '_topics'), exist_ok=True)


def main():
    ensure_dirs()

    refs = collect_references()

    # Write _index.md
    index_path = os.path.join(SEMANTICS_DIR, '_index.md')
    with open(index_path, 'w') as f:
        f.write(build_master_index(refs))
    print(f'  _index.md: {len(refs)} references')

    # Write _tags.md
    tags_path = os.path.join(SEMANTICS_DIR, '_tags.md')
    with open(tags_path, 'w') as f:
        f.write(build_tag_index(refs))

    tag_count = len(set(
        tag
        for _, fm in refs
        for tag in fm.get('tags', [])
    ))
    print(f'  _tags.md: {tag_count} tags')

    print(f'\nDone. {len(refs)} references indexed.')


if __name__ == '__main__':
    main()
