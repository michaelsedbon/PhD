#!/usr/bin/env python3
"""
Fetch PDFs for papers in the Notion bibliography using Sci-Hub.

Queries the bibliography database, extracts DOIs, and downloads missing
PDFs from Sci-Hub mirrors.

Usage:
    python3 scripts/fetch_papers.py              # Download all missing
    python3 scripts/fetch_papers.py --dry-run    # Preview only
    python3 scripts/fetch_papers.py --filter X   # Only titles matching X
    python3 scripts/fetch_papers.py --force      # Re-download existing
"""

import os
import re
import sys
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from notion_client import (
    CONFIG, query_database, get_title_from_page, get_property_value,
)
import requests
from bs4 import BeautifulSoup

# ─── Config ──────────────────────────────────────────────────────────

PAPERS_DIR = os.path.join(PROJECT_DIR, 'papers')
BIB_DB_ID = CONFIG['notion']['bibliography_db']

# Sci-Hub mirrors to try (in order — working ones first)
# Last checked: 2026-02-27
SCIHUB_MIRRORS = [
    'https://sci-hub.fr',       # from Telegram @scihubot
    'https://sci-hub.al',       # ✅ working
    'https://sci-hub.vg',       # ✅ working
    'https://sci-hub.ren',      # ✅ working
    'https://sci-hub.st',       # ⚠️ redirects
    'https://sci-hub.mksa.top', # ⚠️ redirects
    'https://sci-hub.se',       # ❌ dead as of 2026-02
    'https://sci-hub.red',      # ❌ dead as of 2026-02
    'https://sci-hub.box',      # ❌ dead as of 2026-02
    'https://sci-hub.ru',       # ❌ dead as of 2026-02
]

# Delay between downloads (seconds)
DOWNLOAD_DELAY = 3


# ─── Mirror health check ─────────────────────────────────────────────

def _check_one_mirror(mirror, timeout=8):
    """Check a single mirror. Returns (mirror, status_code, latency_ms)."""
    try:
        start = time.time()
        resp = requests.head(mirror, timeout=timeout, allow_redirects=True)
        latency = int((time.time() - start) * 1000)
        return (mirror, resp.status_code, latency)
    except requests.RequestException:
        return (mirror, 0, None)


def check_mirrors(mirrors=None):
    """
    Test all Sci-Hub mirrors in parallel and print a status report.
    Returns a reordered list: working first, then redirects, then dead.
    """
    if mirrors is None:
        mirrors = SCIHUB_MIRRORS

    print("🔍 Checking Sci-Hub mirrors...\n")
    results = []

    with ThreadPoolExecutor(max_workers=len(mirrors)) as pool:
        futures = {pool.submit(_check_one_mirror, m): m for m in mirrors}
        for future in as_completed(futures):
            results.append(future.result())

    # Sort: 200 first (by latency), then 3xx, then dead
    def sort_key(r):
        mirror, code, latency = r
        if code == 200:
            return (0, latency or 9999)
        elif 300 <= code < 400:
            return (1, latency or 9999)
        else:
            return (2, 9999)

    results.sort(key=sort_key)

    # Print table
    print(f"  {'Mirror':<30} {'Status':>8}  {'Latency':>10}  Verdict")
    print(f"  {'─'*30} {'─'*8}  {'─'*10}  {'─'*10}")
    for mirror, code, latency in results:
        name = mirror.replace('https://', '')
        if code == 200:
            verdict = '✅ Working'
            lat_str = f'{latency} ms'
        elif 300 <= code < 400:
            verdict = '⚠️  Redirect'
            lat_str = f'{latency} ms'
        else:
            verdict = '❌ Dead'
            lat_str = '—'
        print(f"  {name:<30} {f'HTTP {code}':>8}  {lat_str:>10}  {verdict}")

    ordered = [m for m, c, _ in results if c == 200] + \
              [m for m, c, _ in results if 300 <= c < 400] + \
              [m for m, c, _ in results if c == 0 or c >= 400]

    working = sum(1 for _, c, _ in results if c == 200)
    print(f"\n  {working}/{len(results)} mirrors responding\n")
    return ordered

# ─── DOI extraction ──────────────────────────────────────────────────

DOI_PATTERNS = [
    # Direct DOI URL
    (r'(?:https?://)?(?:dx\.)?doi\.org/(10\.\d{4,}/[^\s?#]+)', None),
    # Science / Science Advances
    (r'science\.org/doi/(10\.\d{4,}/[^\s?#]+)', None),
    # PLoS
    (r'journals\.plos\.org/\w+/article\?id=(10\.\d{4,}/[^\s&#]+)', None),
    # Frontiers
    (r'frontiersin\.org/(?:journals/\w+/)?articles/(10\.\d{4,}/[^\s/?#]+)', None),
    # ACS
    (r'pubs\.acs\.org/doi(?:/abs)?/(10\.\d{4,}/[^\s?#]+)', None),
    # Wiley
    (r'onlinelibrary\.wiley\.com/doi(?:/abs)?/(10\.\d{4,}/[^\s?#]+)', None),
    # Nature — article IDs need 10.1038/ prefix
    (r'nature\.com/articles/([\w\d][\w\d.-]+)', '10.1038/'),
    # PNAS
    (r'pnas\.org/doi(?:/abs)?/(10\.\d{4,}/[^\s?#]+)', None),
    # bioRxiv / medRxiv
    (r'(?:biorxiv|medrxiv)\.org/content/(10\.\d{4,}/[^\s?#]+)', None),
    # Cell Press / Elsevier — extract PII or DOI
    (r'cell\.com/[\w-]+/(?:fulltext|abstract|pdf)/(S[\d-]+)', None),
    (r'linkinghub\.elsevier\.com/retrieve/pii/(S?\d[\d-]+)', None),
    # Oxford Academic — capture the URL path to pass directly to Sci-Hub
    (r'(academic\.oup\.com/[\w/]+/article(?:-abstract)?/[\d/]+)', None),
    # PubMed — PMID works with Sci-Hub
    (r'pubmed\.ncbi\.nlm\.nih\.gov/(\d+)', None),
    # PMC
    (r'pmc\.ncbi\.nlm\.nih\.gov/articles/(PMC\d+)', None),
    # Cambridge
    (r'cambridge\.org/core/[\w/-]+/([A-F0-9]{32})', None),
    # RUPress (JEM, JCB, etc.)
    (r'rupress\.org/\w+/article/[\d/]+', None),
    # Generic DOI anywhere in text
    (r'(10\.\d{4,}/[^\s,;}\]?#]+)', None),
]


def clean_doi(doi):
    """Clean up a DOI string — remove query params, fragments, trailing junk."""
    # Remove query string
    doi = re.split(r'[?#]', doi)[0]
    # Remove trailing punctuation, parentheses, etc.
    doi = doi.rstrip('.,;:)\'"')
    # Remove utm_source etc. that leaked through
    doi = re.sub(r'\?.*$', '', doi)
    return doi


def extract_doi(url):
    """Extract a DOI or identifier from a paper URL."""
    if not url:
        return None

    for pattern, prefix in DOI_PATTERNS:
        match = re.search(pattern, url)
        if match:
            doi = match.group(1) if match.lastindex else match.group(0)
            doi = clean_doi(doi)
            if prefix:
                doi = prefix + doi
            return doi

    # Fallback: if the URL looks like a direct PDF or paper page, pass it directly
    if any(domain in url for domain in ['cell.com', 'elsevier.com', 'rupress.org',
                                         'cambridge.org', 'pmc.ncbi.nlm.nih.gov']):
        return url  # Sci-Hub can handle full URLs

    return None


# ─── Sci-Hub download ────────────────────────────────────────────────

def sanitize_filename(name):
    """Make a string safe for use as a filename."""
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'\s+', '_', name)
    name = name.strip('. _')
    return name[:150]


def download_from_scihub(identifier, output_path, mirrors=None):
    """
    Try to download a PDF from Sci-Hub using a DOI or URL.
    Tries multiple mirrors in order.
    Returns True if successful, False otherwise.
    """
    if mirrors is None:
        mirrors = SCIHUB_MIRRORS

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/120.0.0.0 Safari/537.36',
    }

    for mirror in mirrors:
        try:
            url = f"{mirror}/{identifier}"
            resp = requests.get(url, headers=headers, timeout=30, allow_redirects=True)

            if resp.status_code != 200:
                continue

            # Check if we got a page with a PDF embed
            if 'application/pdf' in resp.headers.get('Content-Type', ''):
                # Direct PDF response
                with open(output_path, 'wb') as f:
                    f.write(resp.content)
                return True

            # Parse the HTML to find the PDF link
            soup = BeautifulSoup(resp.text, 'html.parser')

            # Look for embed or iframe with PDF
            pdf_url = None
            for tag in ['embed', 'iframe']:
                el = soup.find(tag)
                if el and el.get('src'):
                    pdf_url = el['src']
                    break

            # Also try finding direct PDF links
            if not pdf_url:
                for a in soup.find_all('a', href=True):
                    if '.pdf' in a['href']:
                        pdf_url = a['href']
                        break

            # Also look for onclick with PDF URL
            if not pdf_url:
                for btn in soup.find_all(attrs={'onclick': True}):
                    onclick = btn['onclick']
                    pdf_match = re.search(r"location\.href\s*=\s*'([^']+\.pdf[^']*)'", onclick)
                    if pdf_match:
                        pdf_url = pdf_match.group(1)
                        break

            if not pdf_url:
                continue

            # Fix relative URLs
            if pdf_url.startswith('//'):
                pdf_url = 'https:' + pdf_url
            elif pdf_url.startswith('/'):
                pdf_url = mirror + pdf_url

            # Download the PDF
            pdf_resp = requests.get(pdf_url, headers=headers, timeout=60, stream=True)
            if pdf_resp.status_code == 200:
                content_type = pdf_resp.headers.get('Content-Type', '')
                if 'pdf' in content_type or pdf_url.endswith('.pdf') or len(pdf_resp.content) > 10000:
                    with open(output_path, 'wb') as f:
                        for chunk in pdf_resp.iter_content(chunk_size=8192):
                            f.write(chunk)

                    # Verify it's actually a PDF
                    with open(output_path, 'rb') as f:
                        header = f.read(5)
                    if header == b'%PDF-':
                        return True
                    else:
                        os.remove(output_path)

        except (requests.RequestException, Exception) as e:
            continue

    return False


# ─── Main ────────────────────────────────────────────────────────────

def get_existing_pdfs():
    """Get set of existing PDF filenames (lowercase, without extension)."""
    if not os.path.isdir(PAPERS_DIR):
        os.makedirs(PAPERS_DIR, exist_ok=True)
        return set()
    return {
        os.path.splitext(f)[0].lower()
        for f in os.listdir(PAPERS_DIR)
        if f.endswith('.pdf')
    }


def pdf_exists_for_title(title, existing_pdfs):
    """Check if we already have a PDF for this paper (fuzzy match)."""
    sanitized = sanitize_filename(title).lower()
    # Check exact match
    if sanitized in existing_pdfs:
        return True
    # Check if any existing PDF contains most of the title words
    title_words = set(sanitized.split('_'))
    for pdf_name in existing_pdfs:
        pdf_words = set(pdf_name.split('_'))
        # If >60% of title words appear in the filename, consider it a match
        if title_words and len(title_words & pdf_words) / len(title_words) > 0.6:
            return True
    return False


def fetch_papers(dry_run=False, filter_text=None, force=False):
    """Fetch PDFs for all papers in the bibliography."""
    os.makedirs(PAPERS_DIR, exist_ok=True)

    print("📚 Querying Notion bibliography...")
    pages = query_database(BIB_DB_ID)
    print(f"  Found {len(pages)} papers\n")

    existing_pdfs = get_existing_pdfs()
    print(f"📁 Existing PDFs: {len(existing_pdfs)}\n")

    downloaded = 0
    skipped_existing = 0
    skipped_no_doi = 0
    failed = 0
    errors = []

    for page in pages:
        title = get_title_from_page(page)
        if not title:
            continue

        # Apply filter
        if filter_text and filter_text.lower() not in title.lower():
            continue

        url = get_property_value(page, 'URL')

        # Extract DOI
        doi = extract_doi(url) if url else None

        if not doi:
            skipped_no_doi += 1
            print(f"  ⏭ No DOI: {title[:70]}")
            if url:
                print(f"       URL: {url}")
            continue

        # Check if PDF exists
        if not force and pdf_exists_for_title(title, existing_pdfs):
            skipped_existing += 1
            print(f"  ✓ Already have: {title[:70]}")
            continue

        # Build output path
        filename = sanitize_filename(title) + '.pdf'
        output_path = os.path.join(PAPERS_DIR, filename)

        if dry_run:
            print(f"  [DRY RUN] Would download: {title[:70]}")
            print(f"            DOI: {doi}")
            downloaded += 1
            continue

        print(f"  ⬇ Downloading: {title[:70]}...")
        print(f"    DOI: {doi}")

        success = download_from_scihub(doi, output_path)
        if success:
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"    ✅ Saved: {filename} ({size_mb:.1f} MB)")
            downloaded += 1
            existing_pdfs.add(sanitize_filename(title).lower())
        else:
            print(f"    ❌ Failed to download")
            failed += 1
            errors.append(f"{title[:60]} (DOI: {doi})")

        # Rate limiting
        time.sleep(DOWNLOAD_DELAY)

    # Summary
    prefix = "[DRY RUN] " if dry_run else ""
    print(f"\n{'='*50}")
    print(f"{prefix}Fetch Complete!")
    print(f"  {'Would download' if dry_run else 'Downloaded'}: {downloaded}")
    print(f"  Already had: {skipped_existing}")
    print(f"  No DOI found: {skipped_no_doi}")
    if failed:
        print(f"  Failed: {failed}")
        for err in errors[:10]:
            print(f"    - {err}")
    print(f"{'='*50}")


# ─── CLI ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch PDFs from Sci-Hub for Notion bibliography')
    parser.add_argument('--dry-run', action='store_true', help='Preview without downloading')
    parser.add_argument('--filter', type=str, help='Only download papers matching this title keyword')
    parser.add_argument('--force', action='store_true', help='Re-download even if PDF exists')
    parser.add_argument('--check-mirrors', action='store_true',
                        help='Test all Sci-Hub mirrors and show which are alive')
    args = parser.parse_args()

    if args.check_mirrors:
        ordered = check_mirrors()
        # If not downloading, just exit after the report
        if not args.dry_run and not args.filter and not args.force:
            sys.exit(0)
        # Otherwise, use the reordered list for downloads
        SCIHUB_MIRRORS[:] = ordered

    fetch_papers(dry_run=args.dry_run, filter_text=args.filter, force=args.force)
