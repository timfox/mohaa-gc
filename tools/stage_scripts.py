#!/usr/bin/env python3
"""Copy the scripts a MOHAA level needs onto a DoD-GC disc tree.

    python3 tools/stage_scripts.py "/path/to/MOHAA/main" --out <disc root> --maps m1l1,m3l1a

DoD-GC runs maps/<map>.scr, which pulls in global/*.scr libraries with exec, thread, waitthread and
waitexec (global/spawner.scr, global/disable_ai.scr, global/entsound.scr ...), and those pull in
more. This follows every global/<name>.scr a script mentions, from the map script outward, and
copies the whole set (plus maps/<map>_precache.scr when there is one) under <out>/maps and
<out>/global. Scripts the paks do not have are listed, so a missing library shows up before the
disc is burnt rather than as a script error in Dolphin.

The output is retail data: write it outside the repository and never commit it.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ubersound import collect, read  # noqa: E402

GLOBAL = re.compile(r'(global/[\w/\-]+\.scr)', re.I)


def gc_script_overrides(mapname, path, data):
    """Apply small GameCube parity hooks to copied retail mission scripts."""
    if mapname.lower() != "m1l2a" or path.lower() != "maps/m1l2a.scr":
        return data
    text = data.decode("latin-1").replace("\r\n", "\n").replace("\r", "\n")
    if "gc_door_hint_watch:" in text:
        return data
    anchor = "\texec global/door_locked.scr"
    if anchor not in text:
        raise ValueError("m1l2a script has no door_locked bootstrap to attach the door hint")
    text = text.replace(anchor, anchor + "\n\t$door_locked thread gc_door_hint_watch", 1)
    anchor = "hint_door:\n"
    if anchor not in text:
        raise ValueError("m1l2a script has no retail hint_door label")
    watcher = (
        "gc_door_hint_watch:\n"
        "\tself waittill trigger\n"
        "\tthread hint_door\n"
        "\tgoto gc_door_hint_watch\n"
        "end\n\n"
    )
    text = text.replace(anchor, watcher + anchor, 1)
    return text.encode("latin-1")


def closure(scripts, mapname):
    """(scripts the level needs, in the order found; global scripts named but missing)."""
    start = ["maps/%s.scr" % mapname]
    if "maps/%s_precache.scr" % mapname in scripts:
        start.append("maps/%s_precache.scr" % mapname)
    todo, seen, missing = list(start), [], []
    while todo:
        path = todo.pop(0)
        if path in seen or path in missing:
            continue
        if path not in scripts:
            missing.append(path)
            continue
        seen.append(path)
        for ref in GLOBAL.findall(read(scripts[path]).decode("latin-1")):
            todo.append(ref.lower())
    return seen, missing


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="MOHAA main directory, pk3 files or loose directories")
    ap.add_argument("--out", required=True, help="disc root to copy into (outside the repository)")
    ap.add_argument("--maps", required=True, help="comma-separated map names")
    args = ap.parse_args(argv)
    scripts = collect(args.inputs, (".scr",))
    bad = 0
    for m in args.maps.split(","):
        need, missing = closure(scripts, m)
        if "maps/%s.scr" % m in missing:
            print("%s: no maps/%s.scr" % (m, m))
            bad += 1
            continue
        size = 0
        for path in need:
            data = read(scripts[path])
            data = gc_script_overrides(m, path, data)
            dest = os.path.join(args.out, path)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as fh:
                fh.write(data)
            size += len(data)
        print("%s: %d scripts, %d KB%s" % (m, len(need), size // 1024,
              (", missing: " + " ".join(missing)) if missing else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
