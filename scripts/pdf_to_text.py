#!/usr/bin/env python3
"""
Extract text from PDF files using PyMuPDF (fitz).

Usage:
    python3 pdf_to_text.py <pdf_path> [output_dir]

If output_dir is not specified, outputs to papers_txt/ in the project root.
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DEFAULT_OUTPUT_DIR = os.path.join(PROJECT_DIR, 'papers_txt')


def pdf_to_text(pdf_path, output_dir=None):
    """Extract text from a PDF and save as .txt file."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("❌ PyMuPDF not installed. Run: pip3 install pymupdf")
        sys.exit(1)

    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    os.makedirs(output_dir, exist_ok=True)

    basename = os.path.splitext(os.path.basename(pdf_path))[0]
    txt_path = os.path.join(output_dir, f'{basename}.txt')

    doc = fitz.open(pdf_path)
    text_parts = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        if text.strip():
            text_parts.append(f"--- Page {page_num + 1} ---\n{text}")

    doc.close()

    full_text = '\n\n'.join(text_parts)

    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(full_text)

    print(f"✅ Extracted {len(text_parts)} pages → {txt_path}")
    return txt_path


def batch_convert(pdf_dir, output_dir=None):
    """Convert all PDFs in a directory to text."""
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    existing = set(os.listdir(output_dir)) if os.path.exists(output_dir) else set()

    converted = 0
    skipped = 0

    for pdf_file in sorted(pdf_files):
        txt_name = os.path.splitext(pdf_file)[0] + '.txt'
        if txt_name in existing:
            skipped += 1
            continue

        pdf_path = os.path.join(pdf_dir, pdf_file)
        try:
            pdf_to_text(pdf_path, output_dir)
            converted += 1
        except Exception as e:
            print(f"⚠ Failed to extract {pdf_file}: {e}")

    print(f"\nDone! Converted: {converted}, Skipped (already exist): {skipped}")
    return converted


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 pdf_to_text.py <pdf_path> [output_dir]")
        print("  python3 pdf_to_text.py --batch <pdf_dir> [output_dir]")
        sys.exit(1)

    if sys.argv[1] == '--batch':
        pdf_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(PROJECT_DIR, 'papers')
        output_dir = sys.argv[3] if len(sys.argv) > 3 else None
        batch_convert(pdf_dir, output_dir)
    else:
        pdf_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        pdf_to_text(pdf_path, output_dir)
