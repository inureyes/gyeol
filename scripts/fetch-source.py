#!/usr/bin/env python3
"""Fetch web page content and save as markdown in .memory/semantics/source/.

Usage:
    python3 scripts/fetch-source.py <id> <url>
    python3 scripts/fetch-source.py <id>          # reads URL from semantics/summary/{id}-*.md frontmatter
    python3 scripts/fetch-source.py --all          # fetch all references missing source files
    python3 scripts/fetch-source.py --list-missing # print refs with no source (for manual capture)

PDF URLs are downloaded and converted via pymupdf4llm.
HTML fetches fall back to Wayback Machine when blocked.
If a manual capture is placed at .memory/semantics/source/manual/{id}-*.pdf, it is used
as-is instead of a network fetch.

Examples:
    python3 scripts/fetch-source.py 42 https://example.com/article
    python3 scripts/fetch-source.py 42
    python3 scripts/fetch-source.py --all
    python3 scripts/fetch-source.py --list-missing
"""

import glob
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

import trafilatura
from trafilatura.settings import use_config

SEMANTICS_DIR = os.path.join(os.path.dirname(__file__), '..', '.memory', 'semantics')
SOURCE_DIR = os.path.join(SEMANTICS_DIR, 'source')
MANUAL_DIR = os.path.join(SOURCE_DIR, 'manual')

USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
)


def get_config():
    config = use_config()
    config.set('DEFAULT', 'USER_AGENTS', USER_AGENT)
    return config


SUMMARY_DIR = os.path.join(SEMANTICS_DIR, 'summary')


def get_ref_file(ref_id: int) -> str | None:
    candidates: list[str] = []
    for name in (f'{ref_id}', f'{ref_id:03d}'):
        candidates += [
            m for m in glob.glob(os.path.join(SUMMARY_DIR, f'{name}-*.md'))
            if not m.endswith('.source.md')
        ]
    return candidates[0] if candidates else None


def get_ref_slug(ref_file: str) -> str | None:
    basename = os.path.basename(ref_file)
    match = re.match(r'^\d+-(.+)\.md$', basename)
    return match.group(1) if match else None


def extract_url_from_ref(ref_file: str) -> str | None:
    with open(ref_file, 'r') as f:
        content = f.read()
    match = re.search(r'^url:\s*"(.+?)"', content, re.MULTILINE)
    return match.group(1) if match else None


def extract_title_from_ref(ref_file: str) -> str | None:
    with open(ref_file, 'r') as f:
        content = f.read()
    match = re.search(r'^title:\s*"(.+?)"', content, re.MULTILINE)
    return match.group(1) if match else None


def is_pdf_url(url: str) -> bool:
    path = urllib.parse.urlsplit(url).path.lower()
    return path.endswith('.pdf')


def download_binary(url: str) -> bytes | None:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()
    except Exception:
        return None


def extract_pdf_markdown(pdf_bytes: bytes) -> str | None:
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name
    try:
        try:
            import pymupdf4llm
            md = pymupdf4llm.to_markdown(tmp_path)
            if md and md.strip():
                return md.strip()
        except Exception:
            pass
        try:
            import pymupdf
            doc = pymupdf.open(tmp_path)
            parts = []
            for page in doc:
                parts.append(page.get_text())
            doc.close()
            text = '\n\n'.join(p for p in parts if p.strip())
            return text.strip() or None
        except Exception:
            return None
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def fetch_pdf_as_markdown(url: str) -> str | None:
    data = download_binary(url)
    if not data:
        return None
    if not data[:4] == b'%PDF':
        return None
    return extract_pdf_markdown(data)


def fetch_html(url: str) -> str | None:
    config = get_config()
    downloaded = trafilatura.fetch_url(url, config=config)
    if downloaded:
        return downloaded
    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception:
        pass
    return fetch_from_wayback(url)


def fetch_from_wayback(url: str) -> str | None:
    try:
        import json
        cdx = (
            'http://web.archive.org/cdx/search/cdx'
            f'?url={urllib.parse.quote(url, safe="")}'
            '&output=json&filter=statuscode:200&filter=mimetype:text/html&limit=-5'
        )
        req = urllib.request.Request(cdx, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            rows = json.loads(resp.read().decode('utf-8', errors='replace'))
        if not rows or len(rows) < 2:
            return None
        timestamp = rows[-1][1]
        original = rows[-1][2]
        snap_url = f'https://web.archive.org/web/{timestamp}id_/{original}'
        req2 = urllib.request.Request(snap_url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req2, timeout=60) as resp:
            html = resp.read().decode('utf-8', errors='replace')
        return html or None
    except Exception:
        return None


def extract_markdown(html: str) -> str | None:
    config = get_config()
    result = trafilatura.extract(
        html,
        output_format='markdown',
        include_links=True,
        include_images=True,
        include_tables=True,
        config=config,
    )
    if result:
        return result
    result = trafilatura.extract(
        html,
        output_format='markdown',
        include_links=True,
        include_images=True,
        include_tables=True,
        favor_recall=True,
        config=config,
    )
    if result:
        return result
    try:
        proc = subprocess.run(
            ['pandoc', '-f', 'html', '-t', 'markdown', '--wrap=none'],
            input=html, capture_output=True, text=True, timeout=30,
        )
        if proc.returncode == 0 and len(proc.stdout.strip()) > 100:
            return proc.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def get_source_path(ref_id: int) -> str:
    ref_file = get_ref_file(ref_id)
    if ref_file:
        slug = get_ref_slug(ref_file)
        if slug:
            return os.path.join(SOURCE_DIR, f'{ref_id}-{slug}.source.md')
    return os.path.join(SOURCE_DIR, f'{ref_id}.source.md')


def find_manual_pdf(ref_id: int) -> str | None:
    if not os.path.isdir(MANUAL_DIR):
        return None
    patterns = [
        os.path.join(MANUAL_DIR, f'{ref_id}.pdf'),
        os.path.join(MANUAL_DIR, f'{ref_id:03d}.pdf'),
    ]
    patterns += glob.glob(os.path.join(MANUAL_DIR, f'{ref_id}-*.pdf'))
    patterns += glob.glob(os.path.join(MANUAL_DIR, f'{ref_id:03d}-*.pdf'))
    for p in patterns:
        if os.path.isfile(p):
            return p
    return None


def fetch_and_save(ref_id: int, url: str) -> bool:
    manual_pdf = find_manual_pdf(ref_id)
    if manual_pdf:
        with open(manual_pdf, 'rb') as f:
            data = f.read()
        result = extract_pdf_markdown(data)
        if result:
            os.makedirs(SOURCE_DIR, exist_ok=True)
            out_path = get_source_path(ref_id)
            with open(out_path, 'w') as f:
                f.write(f'<!-- source: {url} -->\n')
                f.write(f'<!-- manual-pdf: {os.path.relpath(manual_pdf)} -->\n\n')
                f.write(result)
                f.write('\n')
            size = os.path.getsize(out_path)
            print(f'  [{ref_id}] OK (manual-pdf): {size:,} bytes -> {os.path.relpath(out_path)}')
            return True
        print(f'  [{ref_id}] WARN: manual PDF extraction failed, falling back to network')

    if is_pdf_url(url):
        result = fetch_pdf_as_markdown(url)
        if not result:
            print(f'  [{ref_id}] FAIL: could not fetch or extract PDF {url}')
            return False
    else:
        html = fetch_html(url)
        if not html:
            print(f'  [{ref_id}] FAIL: could not fetch {url}')
            return False

        result = extract_markdown(html)
        if not result:
            print(f'  [{ref_id}] FAIL: no content extracted from {url}')
            return False

    os.makedirs(SOURCE_DIR, exist_ok=True)
    out_path = get_source_path(ref_id)
    with open(out_path, 'w') as f:
        f.write(f'<!-- source: {url} -->\n\n')
        f.write(result)
        f.write('\n')

    size = os.path.getsize(out_path)
    print(f'  [{ref_id}] OK: {size:,} bytes -> {os.path.relpath(out_path)}')
    return True


def fetch_all():
    ref_files = sorted(glob.glob(os.path.join(SUMMARY_DIR, '[0-9]*-*.md')))
    total = len(ref_files)
    skipped = 0
    fetched = 0
    failed = 0

    for ref_file in ref_files:
        basename = os.path.basename(ref_file)
        match = re.match(r'^(\d+)-', basename)
        if not match:
            continue
        ref_id = int(match.group(1))

        source_path = get_source_path(ref_id)
        legacy_path = os.path.join(SOURCE_DIR, f'{ref_id}.source.md')
        if os.path.exists(source_path) or os.path.exists(legacy_path):
            skipped += 1
            continue

        url = extract_url_from_ref(ref_file)
        if not url:
            print(f'  [{ref_id}] SKIP: no URL in frontmatter')
            skipped += 1
            continue

        if fetch_and_save(ref_id, url):
            fetched += 1
        else:
            failed += 1

    print(f'\nDone: {fetched} fetched, {failed} failed, {skipped} skipped (of {total} total)')


def list_missing():
    ref_files = sorted(glob.glob(os.path.join(SUMMARY_DIR, '[0-9]*-*.md')))
    missing = []
    for ref_file in ref_files:
        basename = os.path.basename(ref_file)
        m = re.match(r'^(\d+)-(.+)\.md$', basename)
        if not m:
            continue
        ref_id = int(m.group(1))
        source_path = get_source_path(ref_id)
        legacy_path = os.path.join(SOURCE_DIR, f'{ref_id}.source.md')
        if os.path.exists(source_path) or os.path.exists(legacy_path):
            continue
        url = extract_url_from_ref(ref_file) or ''
        title = extract_title_from_ref(ref_file) or ''
        missing.append((ref_id, title, url))

    print(f'# Missing sources ({len(missing)} refs)\n')
    print('Put manual captures in `.memory/semantics/source/manual/{id}-{slug}.pdf`')
    print('and re-run `python3 scripts/fetch-source.py --all`.\n')
    for rid, title, url in missing:
        print(f'- [{rid}] {title}')
        print(f'  {url}')


def ensure_dirs():
    """Create required directories if they don't exist."""
    os.makedirs(SUMMARY_DIR, exist_ok=True)
    os.makedirs(SOURCE_DIR, exist_ok=True)
    os.makedirs(MANUAL_DIR, exist_ok=True)


def main():
    ensure_dirs()

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == '--all':
        fetch_all()
        return

    if sys.argv[1] == '--list-missing':
        list_missing()
        return

    ref_id = int(sys.argv[1])

    if len(sys.argv) >= 3:
        url = sys.argv[2]
    else:
        ref_file = get_ref_file(ref_id)
        if not ref_file:
            print(f'Error: no reference file found for id {ref_id}')
            sys.exit(1)
        url = extract_url_from_ref(ref_file)
        if not url:
            print(f'Error: no URL found in {ref_file}')
            sys.exit(1)

    fetch_and_save(ref_id, url)


if __name__ == '__main__':
    main()
