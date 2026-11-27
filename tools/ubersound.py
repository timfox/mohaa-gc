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

MOHAA looks up aliases by prefix: an exact alias and its non-underscore suffix variants
(door_open1, door_open2...) are all candidates, while an underscore suffix starts a separate
family. Samples move under sound/mohaa/ so they cannot clash with DoD's own.

--wav also writes the referenced samples to <out>/sound/mohaa/..., as GoldSrc-friendly 16-bit
mono PCM at 22050 Hz or less, from 8/16-bit PCM or IMA ADPCM WAVs and MP3s decoded by ffmpeg.
FFmpeg's band-limited SWR resampler handles format conversion and downsampling; a pure Python
fallback remains for WAV input when ffmpeg is unavailable. Samples a script plays with loopsound
get a cue point, which makes GoldSrc loop them.

The output is retail data: write it outside the repository and never commit it.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import zipfile

SOUND_LIMIT = 96  # samples one map may precache; DoD's own sounds need the rest of the engine's 512
# The network GameCube profile reserves a 1 MiB ARAM sound ring. Its streaming
# path refuses any one sample larger than half the ring (including its header).
GC_SOUND_PCM_LIMIT = 512 * 1024 - 128

# The map still calls this alias, and its commented legacy definition supplies the
# original source and sound parms. Keep this scoped to that map and use it only if
# no live global alias resolves.
MAP_ALIAS_FALLBACKS = {
    "m6l3a": {
        "gate_large_open": ("sound/mechanics/GateWoodOpen_01.wav", 0.8, 160.0, "item"),
    },
}


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


def strip_comments(text):
    """Remove MOHAA block and line comments before parsing script commands."""
    out, i, state = [], 0, "code"
    while i < len(text):
        ch = text[i]
        if state == "code":
            if text.startswith("//", i):
                out.append(" ")
                i += 2
                state = "line"
            elif text.startswith("/*", i):
                out.append(" ")
                i += 2
                state = "block"
            elif ch == '"':
                out.append(ch)
                i += 1
                state = "string"
            else:
                out.append(ch)
                i += 1
        elif state == "line":
            if ch in "\r\n":
                out.append(ch)
                state = "code"
            i += 1
        elif state == "block":
            if text.startswith("*/", i):
                i += 2
                state = "code"
            elif ch in "\r\n":
                out.append(ch)
                i += 1
            else:
                i += 1
        else:  # quoted string
            out.append(ch)
            if ch == "\\" and i + 1 < len(text):
                out.append(text[i + 1])
                i += 2
            else:
                i += 1
                if ch == '"':
                    state = "code"
    return "".join(out)


def parse_aliases(text):
    """{alias: [(path, volume, mindist, channel)]} from ubersound script text."""
    out = {}
    for line in strip_comments(text).splitlines():
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


PLAY = re.compile(r'\b(playsound|loopsound)\s+"?([A-Za-z_][\w\-.]*)', re.I)
EXEC = re.compile(r'(global/[\w/\-]+\.scr)', re.I)
# what follows playsound when the alias is in a variable ("playsound local.sound"), not a literal
NOT_ALIAS = {"local", "level", "game", "self", "parm", "group", "owner", "sound"}


def map_aliases(scripts, mapname):
    """Aliases a map's scripts name literally, following the global scripts they use.
    Returns (all names, names used by loopsound, scripts read)."""
    todo, seen, names, loops = ["maps/%s.scr" % mapname], set(), set(), set()
    while todo:
        path = todo.pop()
        if path in seen or path not in scripts:
            continue
        seen.add(path)
        text = strip_comments(read(scripts[path]).decode("latin-1"))
        for cmd, n in PLAY.findall(text):
            n = n.lower()
            if "." in n or n in NOT_ALIAS:
                continue
            names.add(n)
            if cmd.lower() == "loopsound":
                loops.add(n)
        todo.extend(p.lower() for p in EXEC.findall(text))
    return names, loops, seen


# Sounds the game plays for map entities rather than for a script line: each class's retail TIKI names the alias
# (models/statweapons/mg42_gun.tik fires "mg42_gun_snd_fire"). A map placing the class gets the alias.
ENTITY_ALIASES = {
    b"turretweapon_german_mg42": ("mg42_gun_snd_fire",),
}


def entity_aliases(bsp_bytes):
    """Aliases the classes a map places need, from its BSP's entity text."""
    out = set()
    for cls, names in ENTITY_ALIASES.items():
        if b'"' + cls + b'"' in bsp_bytes:
            out.update(names)
    return out


def resolve(aliases, name):
    """The alias's samples (or its numbered variants'), each path once, silent placeholders dropped."""
    rows = _alias_rows(aliases, name)
    out, seen = [], set()
    for row in rows:
        key = row[0].lower()
        if key in seen or key.endswith("/null.wav") or key == "null.wav":
            continue
        seen.add(key)
        out.append(row)
    return out


def _alias_rows(aliases, name):
    # Match Alias_ListFindRandom: every name sharing this prefix participates unless the
    # next character is '_'. This includes both the exact alias and suffix variants.
    keys = (key for key in sorted(aliases)
            if key.startswith(name) and (len(key) == len(name) or key[len(name)] != "_"))
    return [row for key in keys for row in aliases[key]]


def intentionally_silent(aliases, name):
    """True when the alias is explicitly defined only with MOHAA's null.wav sentinel."""
    rows = _alias_rows(aliases, name)
    return bool(rows) and all(row[0].lower().replace("\\", "/").endswith("/null.wav") or
                              row[0].lower().replace("\\", "/") == "null.wav" for row in rows)


def sample_name(path):
    """sound/mechanics/door_01.wav -> mohaa/mechanics/door_01.wav (relative to GoldSrc's sound/)."""
    p = path.lower()
    if p.startswith("sound/"):
        p = p[6:]
    if p.endswith(".mp3"):
        p = p[:-4] + ".wav"
    return "mohaa/" + p


IMA_STEP = [7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31, 34, 37, 41, 45, 50, 55, 60, 66, 73, 80, 88, 97,
            107, 118, 130, 143, 157, 173, 190, 209, 230, 253, 279, 307, 337, 371, 408, 449, 494, 544, 598, 658, 724,
            796, 876, 963, 1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024, 3327, 3660, 4026,
            4428, 4871, 5358, 5894, 6484, 7132, 7845, 8630, 9493, 10442, 11487, 12635, 13899, 15289, 16818, 18500,
            20350, 22385, 24623, 27086, 29794, 32767]
IMA_INDEX = [-1, -1, -1, -1, 2, 4, 6, 8]


def ima_nibble(n, pred, idx):
    step = IMA_STEP[idx]
    diff = step >> 3
    if n & 1:
        diff += step >> 2
    if n & 2:
        diff += step >> 1
    if n & 4:
        diff += step
    pred = pred - diff if n & 8 else pred + diff
    pred = -32768 if pred < -32768 else (32767 if pred > 32767 else pred)
    idx = min(88, max(0, idx + IMA_INDEX[n & 7]))
    return pred, idx


def decode_ima(data, ch, block_align):
    """IMA ADPCM (WAVE format 0x11) blocks -> interleaved 16-bit samples."""
    out = []
    for b in range(0, len(data) - 4 * ch + 1, block_align):
        block = data[b:b + block_align]
        pred, idx = [], []
        for c in range(ch):
            pred.append(int.from_bytes(block[4 * c:4 * c + 2], "little", signed=True))
            idx.append(min(88, block[4 * c + 2]))
        chans = [[p] for p in pred]
        pos = 4 * ch
        # after the headers, each channel in turn gives 4 bytes = 8 samples, low nibble first
        while pos + 4 * ch <= len(block):
            for c in range(ch):
                for byte in block[pos + 4 * c:pos + 4 * c + 4]:
                    for n in (byte & 15, byte >> 4):
                        pred[c], idx[c] = ima_nibble(n, pred[c], idx[c])
                        chans[c].append(pred[c])
            pos += 4 * ch
        for i in range(len(chans[0])):
            for c in range(ch):
                out.append(chans[c][i])
    return out


def read_wav(data):
    """(channels, rate, interleaved 16-bit samples) from PCM 8/16-bit or IMA ADPCM, or a reason string."""
    if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        return "not a wav file"
    fmt, body, pos = None, None, 12
    while pos + 8 <= len(data):
        cid, size = data[pos:pos + 4], int.from_bytes(data[pos + 4:pos + 8], "little")
        chunk = data[pos + 8:pos + 8 + size]
        if cid == b"fmt ":
            fmt = chunk
        elif cid == b"data":
            body = chunk
        pos += 8 + size + (size & 1)
    if not fmt or body is None:
        return "no fmt/data chunk"
    tag, ch, rate = int.from_bytes(fmt[0:2], "little"), int.from_bytes(fmt[2:4], "little"), int.from_bytes(fmt[4:8], "little")
    align, bits = int.from_bytes(fmt[12:14], "little"), int.from_bytes(fmt[14:16], "little")
    if ch < 1:
        return "no channels"
    if tag == 0x11:
        return ch, rate, decode_ima(body, ch, align)
    if tag != 1:
        return "format %d" % tag
    if bits == 8:
        return ch, rate, [(v - 128) << 8 for v in body]
    if bits == 16:
        return ch, rate, [int.from_bytes(body[i:i + 2], "little", signed=True) for i in range(0, len(body) - 1, 2)]
    return "%d-bit samples" % bits


def write_wav(dest, rate, samples, loop):
    """16-bit mono PCM; loop adds a cue point at 0, which makes GoldSrc repeat the sample."""
    pcm = b"".join(int(v).to_bytes(2, "little", signed=True) for v in samples)
    write_pcm_wav(dest, rate, pcm, loop)


def write_pcm_wav(dest, rate, pcm, loop):
    """Write little-endian 16-bit mono PCM, adding a cue point for looping samples."""
    fmt = (1).to_bytes(2, "little") + (1).to_bytes(2, "little") + rate.to_bytes(4, "little") + \
        (rate * 2).to_bytes(4, "little") + (2).to_bytes(2, "little") + (16).to_bytes(2, "little")
    chunks = b"fmt " + len(fmt).to_bytes(4, "little") + fmt + b"data" + len(pcm).to_bytes(4, "little") + pcm
    if len(pcm) & 1:
        chunks += b"\0"
    if loop:
        cue = (1).to_bytes(4, "little") + (0).to_bytes(4, "little") * 2 + b"data" + (0).to_bytes(4, "little") * 3
        chunks += b"cue " + len(cue).to_bytes(4, "little") + cue
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as fh:
        fh.write(b"RIFF" + (4 + len(chunks)).to_bytes(4, "little") + b"WAVE" + chunks)


def convert_wav(data, dest, loop=False):
    """Mono PCM at 22.05 or 11.025 kHz, small enough for the GameCube ARAM ring."""
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        rate = wav_rate(data)
        if isinstance(rate, str):
            return rate
        rate = min(rate, 22050)
        why = convert_ffmpeg(data, dest, rate, loop, ffmpeg)
        if why:
            return why
        if os.path.getsize(dest) - 44 > GC_SOUND_PCM_LIMIT and rate > 11025:
            why = convert_ffmpeg(data, dest, 11025, loop, ffmpeg)
            if why:
                os.unlink(dest)
                return why
        if os.path.getsize(dest) - 44 > GC_SOUND_PCM_LIMIT:
            os.unlink(dest)
            return "exceeds the GameCube 1 MiB ARAM sound ring"
        return None

    got = read_wav(data)
    if isinstance(got, str):
        return got
    ch, rate, samples = got
    step = 1
    while rate // step > 22050:
        step += 1
    frames = len(samples) // ch
    if frames // step * 2 > GC_SOUND_PCM_LIMIT:
        while rate // step > 11025:
            step += 1
    if frames // step * 2 > GC_SOUND_PCM_LIMIT:
        return "exceeds the GameCube 1 MiB ARAM sound ring"
    mono = [sum(samples[f * ch:f * ch + ch]) // ch for f in range(0, frames, step)]
    write_wav(dest, rate // step, mono, loop)
    return None


def wav_rate(data):
    """Return the source WAV rate without decoding its full sample payload."""
    if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        return "not a wav file"
    pos = 12
    while pos + 8 <= len(data):
        cid = data[pos:pos + 4]
        size = int.from_bytes(data[pos + 4:pos + 8], "little")
        chunk = data[pos + 8:pos + 8 + size]
        if cid == b"fmt ":
            if len(chunk) < 8:
                return "short fmt chunk"
            rate = int.from_bytes(chunk[4:8], "little")
            return rate if rate > 0 else "invalid sample rate"
        pos += 8 + size + (size & 1)
    return "no fmt chunk"


def convert_ffmpeg(data, dest, rate, loop=False, ffmpeg=None):
    """Decode/resample audio with FFmpeg's band-limited SWR filter, then write PCM WAV."""
    ffmpeg = ffmpeg or shutil.which("ffmpeg")
    if not ffmpeg:
        return "ffmpeg needed for band-limited audio conversion"
    run = subprocess.run(
        [ffmpeg, "-v", "error", "-i", "pipe:0", "-map", "0:a:0",
         "-af", "aresample=%d:resampler=swr:filter_size=64:cutoff=0.95" % rate,
         "-ar", str(rate), "-ac", "1", "-f", "s16le", "-acodec", "pcm_s16le", "pipe:1"],
        input=data, capture_output=True)
    if run.returncode or not run.stdout:
        return "ffmpeg could not decode/resample sound sample"
    pcm = run.stdout[:len(run.stdout) - len(run.stdout) % 2]
    write_pcm_wav(dest, rate, pcm, loop)
    return None


def convert_mp3(data, dest, loop=False):
    """Decode an MP3 alias to GameCube-friendly 22.05 kHz mono PCM WAV."""
    return convert_ffmpeg(data, dest, 22050, loop)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="MOHAA main directory, pk3 files or loose directories")
    ap.add_argument("--out", required=True, help="output directory (outside the repository)")
    ap.add_argument("--maps", help="comma-separated map names (default: every maps/*.scr)")
    ap.add_argument("--wav", action="store_true", help="also convert the referenced samples")
    args = ap.parse_args(argv)

    scripts = collect(args.inputs, (".scr",))
    aliases = {}
    for path in sorted(p for p in scripts if p.startswith("ubersound/")):
        for k, v in parse_aliases(read(scripts[path]).decode("latin-1")).items():
            aliases.setdefault(k, []).extend(v)
    if not aliases:
        print("no ubersound aliases found")
        return 1
    maps = args.maps.split(",") if args.maps else sorted(
        os.path.basename(p)[:-4] for p in scripts if p.startswith("maps/") and p.count("/") == 1
        and not p.endswith(("_precache.scr", "soundcache.scr")))
    sounds = collect(args.inputs, (".wav", ".mp3")) if args.wav else {}
    bsps = collect(args.inputs, (".bsp",))
    wanted, looped = {}, set()
    print("%d aliases defined" % len(aliases))
    for m in maps:
        names, loops, used = map_aliases(scripts, m)
        if "maps/%s.bsp" % m in bsps:
            names |= entity_aliases(read(bsps["maps/%s.bsp" % m]))
        if "maps/%s.scr" % m not in scripts:
            print("%s: no script" % m)
            continue
        effective_aliases = dict(aliases)
        for name, row in MAP_ALIAS_FALLBACKS.get(m.lower(), {}).items():
            if name in names and not resolve(effective_aliases, name) and not intentionally_silent(effective_aliases, name):
                effective_aliases.setdefault(name, []).append(row)
        rows, missing, samples = [], [], set()
        for name in sorted(names):
            r = resolve(effective_aliases, name)
            if not r and not intentionally_silent(effective_aliases, name):
                missing.append(name)
            for path, vol, mindist, channel in r:
                rows.append("%s %s %.2f %d %s" % (name, sample_name(path), vol, mindist, channel))
                samples.add(path.lower())
                wanted[path.lower()] = sample_name(path)
                if name in loops:
                    looped.add(path.lower())
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
            data = read(sounds[src])
            if src.endswith(".mp3"):
                why = convert_mp3(data, os.path.join(args.out, "sound", rel), src in looped)
            else:
                why = convert_wav(data, os.path.join(args.out, "sound", rel), src in looped)
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
