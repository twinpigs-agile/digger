#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from pathlib import Path
from PIL import Image, ImageFile

# Allow Pillow to load truncated PNGs if needed
ImageFile.LOAD_TRUNCATED_IMAGES = True

TARGET_IN = (1024, 1024)
TARGET_OUT = (512, 512)

def is_png(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() == ".png"

def resize_png(src: Path, dst: Path, optimize=True, compress_level=9) -> None:
    with Image.open(src) as im:
        # Skip files that are not exactly 1024×1024
        if im.size != TARGET_IN:
            return

        # Resize with high-quality LANCZOS filter
        im_resized = im.resize(TARGET_OUT, resample=Image.Resampling.LANCZOS)

        # Preserve ICC profile if present
        save_kwargs = {
            "optimize": optimize,
            "compress_level": compress_level,
        }
        if "icc_profile" in im.info:
            save_kwargs["icc_profile"] = im.info["icc_profile"]

        # Save resized image as PNG (alpha channel preserved automatically)
        dst.parent.mkdir(parents=True, exist_ok=True)
        im_resized.save(dst, format="PNG", **save_kwargs)

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Recursively find 1024×1024 PNG images and resize them to 512×512 (transparency preserved)."
    )
    parser.add_argument("root", type=Path, help="Root directory to scan")
    parser.add_argument(
        "--inplace",
        action="store_true",
        help="Overwrite original files in place (default: create files with -512 suffix).",
    )
    parser.add_argument(
        "--suffix",
        default="-512",
        help="Suffix for resized file names (ignored with --inplace). Default: -512",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without writing files.",
    )

    args = parser.parse_args()

    if not args.root.exists() or not args.root.is_dir():
        print(f"Error: '{args.root}' does not exist or is not a directory.", file=sys.stderr)
        return 1

    total_found = 0
    total_done = 0

    for path in args.root.rglob("*.png"):
        if not is_png(path):
            continue

        # Check image size before processing
        try:
            with Image.open(path) as im:
                if im.size != TARGET_IN:
                    continue
        except Exception as e:
            print(f"[Skip] Cannot open: {path} ({e})", file=sys.stderr)
            continue

        total_found += 1

        if args.inplace:
            dst = path
        else:
            dst = path.with_name(path.stem + args.suffix + path.suffix)

        print(("DRY-RUN " if args.dry_run else "") + f"[{total_found}] {path} -> {dst}")

        if args.dry_run:
            continue

        try:
            resize_png(path, dst)
            total_done += 1
        except Exception as e:
            print(f"[Error] {path} -> {dst}: {e}", file=sys.stderr)

    print(f"\nFound 1024×1024 PNGs: {total_found}")
    if not args.dry_run:
        print(f"Successfully resized to 512×512: {total_done}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
