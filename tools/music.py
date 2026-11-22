#!/usr/bin/env python3
"""Turn MOHAA music (.mus mood tables and triggered cues) into DoD-GC music tables and wavs.

    python3 tools/music.py "/path/to/MOHAA/main" --out build/music [--convert] [--stereo]

MOHAA has two music systems, both driven by scripts:

* Mood music. A level names a soundtrack (`soundtrack music/m1l1.mus`); the .mus file gives a
  folder (`path sound/music`), then for each mood (normal, aux1..aux6) a file and properties
  (`!aux1 volume 0.7`, `!aux1 loop`, `!aux1 fadetime 1.5`). `forcemusic <mood> [fallback]` switches.
* Triggered cues: `$player stufftext "tmstart sound/music/x.mp3"` (once), `tmstartloop` (looped),
  `tmstop`.

For each .mus this writes <out>/music/<name>.mood:

    # mood sample volume loop fadetime
    normal mohaa/music/mus_01a.wav 1.00 1 0.0

Samples are relative to sound/ and move under sound/mohaa/music/, named by their base name. The
game falls back to music/<map>.mood when a level never names its soundtrack.

--convert also writes every referenced track (mood files and tmstart cues) to
<out>/sound/mohaa/music/*.wav as 16-bit PCM at 22050 Hz, mono unless --stereo, using ffmpeg. Each track is
raised by up to --lift-db (8 dB) with its peak kept under -1 dBFS: retail tracks peak near -9 dB and played
too quietly under the GameCube's mixer. The
GameCube streams PCM from disc; decoding mp3 on the Gekko costs too much. Retail installs keep the
music loose in main/sound/music (it is not in the paks), so point the inputs at the installed main
directory. Missing tracks are listed. The `sound/music/null.wav` mood reference is an intentional
no-stream sentinel used to stop the current track; it stays in the mood table but is not treated as a
missing source or converted into a silent audio file.

The output is retail data: write it outside the repository and never commit it.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ubersound import collect, read  # noqa: E402

MOODS = ("normal", "aux1", "aux2", "aux3", "aux4", "aux5", "aux6")
CUE = re.compile(r'\b(tmstart|tmstartloop)\s+([^\s";]+)', re.I)
NO_STREAM_SENTINELS = {"sound/music/null.wav", "sound/amb_stereo/null.wav"}


def parse_mus(text):
    """(folder, {mood: [file, volume, loop, fadetime]}) from .mus text."""
    folder, moods = "sound/music", {}
    for line in text.splitlines():
        line = line.split("//")[0].strip()
        if not line:
            continue
        w = line.split()
        key = w[0].lower()
        if key == "path" and len(w) > 1:
            folder = w[1].strip("/").replace("\\", "/")
        elif key.startswith("!") and len(w) > 1:
            m = moods.setdefault(key[1:], [None, 1.0, 0, 0.0])
            prop = w[1].lower()
            try:
                if prop == "volume" and len(w) > 2:
                    m[1] = float(w[2])
                elif prop == "fadetime" and len(w) > 2:
                    m[3] = float(w[2])
            except ValueError:
                pass
            if prop == "loop":
                m[2] = 1
        elif len(w) > 1:
            moods.setdefault(key, [None, 1.0, 0, 0.0])[0] = w[1].replace("\\", "/")
    return folder, {k: v for k, v in moods.items() if v[0]}


def sample_name(path):
    """sound/music/MUS_01a.mp3 -> mohaa/music/mus_01a.wav (relative to sound/)."""
    base = os.path.splitext(os.path.basename(path.replace("\\", "/")))[0].lower()
    return "mohaa/music/%s.wav" % base


def cues(text):
    """Tracks named by tmstart/tmstartloop in script text: [(path, loop)]."""
    return [(p.lower(), cmd.lower() == "tmstartloop") for cmd, p in CUE.findall(text)]


LIFT_DB = 8.0       # MOHAA's tracks peak around -9 dB: on the GameCube mixer they played under the effects
CEILING_DB = -1.0   # never lifted past this peak, so nothing clips
MAX_VOLUME = re.compile(r"max_volume:\s*(-?[\d.]+|-inf) dB")


def peak_db(data):
    """The track's peak in dBFS (ffmpeg volumedetect), or None if it can't be measured."""
    r = subprocess.run(["ffmpeg", "-v", "info", "-nostats", "-i", "pipe:0", "-af", "volumedetect", "-f", "null", "-"],
                       input=data, capture_output=True)
    m = MAX_VOLUME.search(r.stderr.decode(errors="replace"))
    return None if r.returncode or not m or m.group(1) == "-inf" else float(m.group(1))


def lift_for(peak, lift_db=LIFT_DB, ceiling_db=CEILING_DB):
    """dB to add: up to lift_db, but never past ceiling_db at the peak; never quieter."""
    return 0.0 if peak is None else max(0.0, min(lift_db, ceiling_db - peak))


def convert(data, dest, stereo, lift_db=LIFT_DB):
    """mp3/wav bytes -> 22050 Hz 16-bit wav via ffmpeg, lifted by up to lift_db (peak kept under CEILING_DB).
    Returns an error string or None."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    gain = lift_for(peak_db(data), lift_db) if lift_db > 0 else 0.0
    af = ["-af", "volume=%.2fdB" % gain] if gain >= 0.05 else []
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "pipe:0"] + af + ["-ar", "22050", "-ac",
                        "2" if stereo else "1", "-c:a", "pcm_s16le", "-f", "wav", dest],
                       input=data, capture_output=True)
    return r.stderr.decode(errors="replace").strip() or "ffmpeg failed" if r.returncode else None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="MOHAA main directory, pk3 files or loose directories")
    ap.add_argument("--out", required=True, help="output directory (outside the repository)")
    ap.add_argument("--convert", action="store_true", help="also convert the referenced tracks (needs ffmpeg)")
    ap.add_argument("--stereo", action="store_true", help="keep two channels (twice the disc space)")
    ap.add_argument("--lift-db", type=float, default=LIFT_DB,
                    help="raise each track by up to this many dB, keeping its peak under %.0f dBFS (default %%(default)s; 0 = as is)"
                    % CEILING_DB)
    args = ap.parse_args(argv)

    texts = collect(args.inputs, (".mus", ".scr"))
    wanted = {}  # source path -> sample name
    n_mus = 0
    for path in sorted(p for p in texts if p.endswith(".mus")):
        folder, moods = parse_mus(read(texts[path]).decode("latin-1"))
        rows = []
        for mood in sorted(moods, key=lambda m: (MOODS.index(m) if m in MOODS else 99, m)):
            f, vol, loop, fade = moods[mood]
            src = (folder + "/" + f).lower()
            wanted[src] = sample_name(src)
            rows.append("%s %s %.2f %d %.1f" % (mood, sample_name(src), vol, loop, fade))
        dest = os.path.join(args.out, "music", os.path.splitext(os.path.basename(path))[0] + ".mood")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w") as fh:
            fh.write("# mood sample volume loop fadetime (from MOHAA %s; retail data, do not commit)\n" % path)
            fh.write("\n".join(rows) + ("\n" if rows else ""))
        n_mus += 1
    n_cues = 0
    for path in sorted(p for p in texts if p.endswith(".scr")):
        for src, _ in cues(read(texts[path]).decode("latin-1")):
            if src not in wanted:
                n_cues += 1
            wanted[src] = sample_name(src)
    print("%d mood tables, %d music refs (%d triggered cues)" % (n_mus, len(wanted), n_cues))
    if args.convert:
        if not shutil.which("ffmpeg"):
            print("ffmpeg is needed for --convert")
            return 1
        audio = collect(args.inputs, (".mp3", ".wav"))
        done, missing, failed, sentinels = 0, [], [], []
        for src, rel in sorted(wanted.items()):
            if src in NO_STREAM_SENTINELS:
                sentinels.append(src)
                continue
            if src not in audio:
                missing.append(src)
                continue
            why = convert(read(audio[src]), os.path.join(args.out, "sound", rel), args.stereo, args.lift_db)
            if why:
                failed.append((src, why))
            else:
                done += 1
        print("converted %d tracks, %d missing, %d failed; skipped %d intentional no-stream sentinel(s)"
              % (done, len(missing), len(failed), len(sentinels)))
        for src in missing[:20]:
            print("  missing %s" % src)
        if any(src.startswith("sound/amb_stereo/") for src in missing):
            print("  note: MOHAA stores these in the separate Sound AmbStereo Files CD group; "
                  "supply both install CDs with mohaa_sd.py --cd or add an extracted loose-audio folder "
                  "with --music-source (mohaa_sd.py) / as an input directory (music.py)")
        for src, why in failed[:20]:
            print("  failed %s: %s" % (src, why.splitlines()[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
