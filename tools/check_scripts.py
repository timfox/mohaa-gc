#!/usr/bin/env python3
"""Compile every MOHAA .scr script with the DoD-GC script VM and report failures.

    python3 tools/check_scripts.py "/path/to/MOHAA/main"
    python3 tools/check_scripts.py pak0.pk3 pak1.pk3 --verbose

Inputs can be .pk3 archives (later paks override earlier ones, like the game),
directories searched for .pk3 and loose .scr files, or single .scr files.
Scripts are copied to a temporary directory, never into the repository.
"""
import argparse
import os
import subprocess
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MSRUN = os.path.join(ROOT, "out", "msrun")


def build_msrun():
    subprocess.run(["make", "-s", "-C", os.path.join(ROOT, "script")], check=True)


def collect(inputs):
    """Return {game path: bytes}, later inputs overriding earlier ones."""
    scripts = {}

    def add_pk3(path):
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                if name.lower().endswith(".scr"):
                    scripts[name.lower().replace("\\", "/")] = z.read(name)

    for inp in inputs:
        if os.path.isdir(inp):
            paks = []
            for d, _, files in os.walk(inp):
                for f in files:
                    full = os.path.join(d, f)
                    if f.lower().endswith(".pk3"):
                        paks.append(full)
                    elif f.lower().endswith(".scr"):
                        rel = os.path.relpath(full, inp).replace("\\", "/").lower()
                        with open(full, "rb") as fh:
                            scripts[rel] = fh.read()
            for p in sorted(paks, key=lambda s: os.path.basename(s).lower()):
                add_pk3(p)
        elif inp.lower().endswith(".pk3"):
            add_pk3(inp)
        else:
            with open(inp, "rb") as fh:
                scripts[os.path.basename(inp).lower()] = fh.read()
    return scripts


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--verbose", action="store_true", help="print every script checked")
    args = ap.parse_args()

    if not os.path.exists(MSRUN):
        build_msrun()
    scripts = collect(args.inputs)
    if not scripts:
        print("no .scr files found")
        return 1

    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        names = sorted(scripts)
        for n in names:
            dest = os.path.join(tmp, n)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as fh:
                fh.write(scripts[n])
        r = subprocess.run([MSRUN, "-compile"] + names, cwd=tmp, capture_output=True, text=True,
                           errors="replace")
        lines = r.stdout.strip().splitlines()
        for line in lines:
            if "compile error" in line or line.startswith("missing"):
                failures += 1
                print(line.split("] ", 1)[-1])
            elif args.verbose or line.startswith("compiled"):
                print(line)
    print(f"{len(scripts) - failures} of {len(scripts)} scripts compile")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
