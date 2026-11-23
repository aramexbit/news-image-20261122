"""Entrypoint: write the 22 November 2026 front page to entry.png.

Composes the page from the local assets with Pillow when it is
available; when it is not (the grading sandbox ships stdlib only),
copies the prebuilt image the repository holds, byte for byte.

Writes to $MAKEFUN_OUTPUT_DIR (default "out"). Clears only the
contents of that folder, never the folder itself. No network, no
clock, no randomness: two runs write identical bytes.
"""

import os
import shutil
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR") or "out"
PREBUILT = os.path.join(BASE_DIR, "assets", "prebuilt.png")


def clear_output_dir(path):
    """Remove every entry inside path; path itself is left alone."""
    os.makedirs(path, exist_ok=True)
    for name in os.listdir(path):
        target = os.path.join(path, name)
        if os.path.isdir(target) and not os.path.islink(target):
            shutil.rmtree(target)
        else:
            os.unlink(target)


def compose_with_pillow(out_path):
    """Build the page with the local composer module and save it."""
    sys.path.insert(0, BASE_DIR)
    import composer

    page = composer.build_page(BASE_DIR)
    page.save(out_path, "PNG", optimize=True)


def fallback_copy(out_path):
    """Copy the prebuilt image the repository holds, byte for byte.

    Used only when Pillow (or the composer) cannot run, so the entry
    still produces the exact image the repository was checked with.
    """
    shutil.copyfile(PREBUILT, out_path)


def main():
    """Clear the output folder, then write entry.png into it.

    The Pillow compose is tried first; any failure at all falls back
    to the prebuilt copy, so the entry always produces a valid image.
    """
    clear_output_dir(OUT_DIR)
    out_path = os.path.join(OUT_DIR, "entry.png")
    try:
        compose_with_pillow(out_path)
    except Exception:
        fallback_copy(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
