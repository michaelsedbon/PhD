#!/usr/bin/env python3
import sys
import os
import subprocess

def read_summary(title_query):
    index_path = "/Users/michaelsedbon/Documents/SYNTHETIC_PERSONAL_LAB/papers_txt/INDEX.md"
    if not os.path.exists(index_path):
        print("Index not found.")
        return

    with open(index_path, 'r') as f:
        content = f.read()

    sections = content.split("---")
    for section in sections:
        if title_query.lower() in section.lower():
            # Extract just the summary part (skip the header and metadata)
            lines = section.strip().split('\n')
            summary_lines = [l for l in lines if l and not l.startswith('#') and not l.startswith('**') and not l.startswith('URL:')]
            summary_text = " ".join(summary_lines)
            
            print(f"Reading summary for: {lines[0]}")
            subprocess.run(["say", summary_text])
            return

    print(f"No summary found matching: {title_query}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 read_index.py 'Paper Title Keywords'")
    else:
        read_summary(" ".join(sys.argv[1:]))
