#!/usr/bin/env python3
"""Turn MOHAA ubersound aliases into per-map sound tables for DoD-GC.

    python3 tools/ubersound.py "/path/to/MOHAA/main" --out build/sound --maps m1l1,m3l1a [--wav]

MOHAA scripts play aliases ("door_open"), defined in ubersound/*.scr by lines like

    local.master aliascache door_open1 sound/mechanics/door_01.wav soundparms 0.8 0.2 1.0 0.1 160 1600 auto loaded maps "m1 m2"

DoD-GC (GoldSrc) plays precached wav files, and a map can precache only so many. So for each map
this reads maps/<map>.scr and the global/*.scr files it uses, collects every alias named by
playsound/loopsound, and writes <out>/maps/<map>.snd:

    # alias sample volume mindist channel
    door_open mohaa/mechanics/door_01.wav 0.80 160 auto
    door_open mohaa/mechanics/door_02.wav 0.80 160 auto     <- variants: the game picks one at random

An alias with no exact definition resolves to its numbered variants (door_open1, door_open2...),
the way MOHAA does. Samples move under sound/mohaa/ so they cannot clash with DoD's own.

--wav also writes the referenced samples to <out>/sound/mohaa/..., as GoldSrc-friendly 16-bit
mono PCM at 22050 Hz or less. Only PCM sources are converted; others (ADPCM, mp3) are listed.

The output is retail data: write it outside the repository and never commit it.
"""
import argparse
import os
import re
import sys
import wave
import zipfile

SOUND_LIMIT = 96  # samples one map may precache; DoD's own sounds need the rest of the engine's 512


def collect(inputs, exts):
    """Return {game path: bytes} for files with the given extensions, later inputs overriding earlier."""
    files = {}

    def add_pk3(path):
        z = zipfile.ZipFile(path)  # stays open: entries are read later
        for name in z.namelist():
            if name.lower().endswith(exts):
                files[name.lower().replace("\\", "/")] = (z, name)

    for inp in inputs:
        if os.path.isdir(inp):
            paks = []
            for d, _, names in os.walk(inp):
                for f in names:
                    full = os.path.join(d, f)
                    if f.lower().endswith(".pk3"):
                        paks.append(full)
                    elif f.lower().endswith(exts):
                        files[os.path.relpath(full, inp).replace("\\", "/").lower()] = full
            for p in sorted(paks, key=lambda s: os.path.basename(s).lower()):
                add_pk3(p)
        elif inp.lower().endswith(".pk3"):
            add_pk3(inp)
    return files


def read(entry):
    if isinstance(entry, tuple):
        z, name = entry
        return z.read(name)
    with open(entry, "rb") as fh:
        return fh.read()


TOKEN = re.compile(r'"([^"]*)"|(\S+)')


def parse_aliases(text):
    """{alias: [(path, volume, mindist, channel)]} from ubersound script text."""
    out = {}
    for raw in text.splitlines():
        line = raw.split("//", 1)[0]
        toks = [a if a else b for a, b in TOKEN.findall(line)]
        low = [t.lower() for t in toks]
        for kw in ("aliascache", "alias"):
            if kw in low:
                i = low.index(kw)
                break
        else:
            continue
        if i + 2 >= len(toks):
            continue
        name, path = low[i + 1], toks[i + 2].replace("\\", "/")
        vol, mindist, channel = 1.0, 160.0, "auto"
        if "soundparms" in low:
            p = low.index("soundparms")
            try:
                vol = float(toks[p + 1])
                mindist = float(toks[p + 5])
                channel = low[p + 7]
            except (IndexError, ValueError):
                pass
        out.setdefault(name, []).append((path, vol, mindist, channel))
    return out


PLAY = re.compile(r'\b(?:playsound|loopsound)\s+"?([A-Za-z_][\w\-.]*)', re.I)
EXEC = re.compile(r'(global/[\w/\-]+\.scr)', re.I)


def map_aliases(scripts, mapname):
    """Aliases a map's scripts name literally, following the global scripts they use."""
    todo, seen, names = ["maps/%s.scr" % mapname], set(), set()
    while todo:
        path = todo.pop()
        if path in seen or path not in scripts:
            continue
        seen.add(path)
        text = read(scripts[path]).decode("latin-1")
        names.update(n.lower() for n in PLAY.findall(text))
        todo.extend(p.lower() for p in EXEC.findall(text))
    return names, seen


def resolve(aliases, name):
    if name in aliases:
        return aliases[name]
    variants = sorted(k for k in aliases if k.startswith(name) and k[len(name):].isdigit())
    return [v for k in variants for v in aliases[k]]


def sample_name(path):
    """sound/mechanics/door_01.wav -> mohaa/mechanics/door_01.wav (relative to GoldSrc's sound/)."""
    p = path.lower()
    if p.startswith("sound/"):
        p = p[6:]
    return "mohaa/" + p


def convert_wav(data, dest):
    """16-bit mono PCM at <= 22050 Hz. Returns None on success, or why it was skipped."""
    import io
    try:
        w = wave.open(io.BytesIO(data))
    except (wave.Error, EOFError) as e:
        return "not PCM wav (%s)" % e
    ch, width, rate, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
    frames = w.readframes(n)
    if width not in (1, 2):
        return "%d-bit samples" % (width * 8)
    step = 1
    while rate // step > 22050:
        step += 1
    out = bytearray()
    stride = ch * width
    for f in range(0, n, step):
        acc = 0
        for c in range(ch):
            o = f * stride + c * width
            s = frames[o] - 128 << 8 if width == 1 else int.from_bytes(frames[o:o + 2], "little", signed=True)
            acc += s
        out += int(acc / ch).to_bytes(2, "little", signed=True)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with wave.open(dest, "wb") as o:
        o.setnchannels(1)
        o.setsampwidth(2)
        o.setframerate(rate // step)
        o.writeframes(bytes(out))
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="MOHAA main directory, pk3 files or loose directories")
    ap.add_argument("--out", required=True, help="output directory (outside the repository)")
    ap.add_argument("--maps", help="comma-separated map names (default: every maps/*.scr)")
    ap.add_argument("--wav", action="store_true", help="also convert the referenced samples")
    args = ap.parse_args()

    scripts = collect(args.inputs, (".scr",))
    aliases = {}
    for path in sorted(p for p in scripts if p.startswith("ubersound/")):
        for k, v in parse_aliases(read(scripts[path]).decode("latin-1")).items():
            aliases.setdefault(k, []).extend(v)
    if not aliases:
        print("no ubersound aliases found")
        return 1
    maps = args.maps.split(",") if args.maps else sorted(
        os.path.basename(p)[:-4] for p in scripts if p.startswith("maps/") and p.count("/") == 1)
    sounds = collect(args.inputs, (".wav", ".mp3")) if args.wav else {}
    wanted = {}
    print("%d aliases defined" % len(aliases))
    for m in maps:
        names, used = map_aliases(scripts, m)
        if "maps/%s.scr" % m not in scripts:
            print("%s: no script" % m)
            continue
        rows, missing, samples = [], [], set()
        for name in sorted(names):
            r = resolve(aliases, name)
            if not r:
                missing.append(name)
            for path, vol, mindist, channel in r:
                rows.append("%s %s %.2f %d %s" % (name, sample_name(path), vol, mindist, channel))
                samples.add(path.lower())
                wanted[path.lower()] = sample_name(path)
        dest = os.path.join(args.out, "maps", m + ".snd")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w") as fh:
            fh.write("# alias sample volume mindist channel (from MOHAA ubersound; retail data, do not commit)\n")
            fh.write("\n".join(rows) + ("\n" if rows else ""))
        over = " OVER the %d-sample budget" % SOUND_LIMIT if len(samples) > SOUND_LIMIT else ""
        print("%s: %d aliases, %d samples%s, %d scripts read, %d unresolved%s" % (
            m, len(names), len(samples), over, len(used), len(missing),
            (": " + " ".join(missing[:10]) + (" ..." if len(missing) > 10 else "")) if missing else ""))
    if args.wav:
        done, skipped = 0, []
        for src, rel in sorted(wanted.items()):
            if src not in sounds:
                skipped.append((src, "missing"))
                continue
            why = convert_wav(read(sounds[src]), os.path.join(args.out, "sound", rel))
            if why:
                skipped.append((src, why))
            else:
                done += 1
        print("converted %d samples, skipped %d" % (done, len(skipped)))
        for src, why in skipped[:20]:
            print("  skipped %s: %s" % (src, why))
    return 0


if __name__ == "__main__":
    sys.exit(main())
