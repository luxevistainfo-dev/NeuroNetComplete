#!/usr/bin/env python3
"""
copy_abi.py

Searches common build/artifact directories for compiled contract JSON files
and writes ABI-only JSON files into the project's `abi/` directory.

This is a small convenience script for local tooling and CI pipelines.
"""
import os
import sys
import json
import glob
import argparse
from pathlib import Path

SEARCH_PATTERNS = [
    "artifacts/**/*.json",
    "build/contracts/*.json",
    "build/**/*.json",
    "out/**/*.json",
]


def find_json_files():
    files = set()
    for pattern in SEARCH_PATTERNS:
        for f in glob.glob(pattern, recursive=True):
            files.add(f)
    return sorted(files)


def extract_and_dump_abi(src_path, out_dir):
    with open(src_path, "r", encoding="utf-8") as fh:
        try:
            data = json.load(fh)
        except Exception:
            return
    # Expect ABI to be under 'abi' key (standard for many toolchains)
    abi = data.get("abi")
    if not abi:
        return
    name = Path(src_path).stem
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{name}.abi.json"
    with open(out_path, "w", encoding="utf-8") as out_fh:
        json.dump(abi, out_fh, indent=2)
    print(f"Wrote ABI for {name} to {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Copy ABIs from build artifacts into abi/")
    parser.add_argument("--out", default="abi", help="Output directory for ABIs")
    args = parser.parse_args()

    files = find_json_files()
    if not files:
        print("No artifact JSON files found. Make sure you compiled contracts first.")
        sys.exit(0)

    for f in files:
        extract_and_dump_abi(f, args.out)

if __name__ == "__main__":
    main()
