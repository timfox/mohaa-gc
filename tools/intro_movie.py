#!/usr/bin/env python3
"""Convert the player's own MOHAA intro movie into the GameCube intro format, on the SD card.

    python3 tools/intro_movie.py "/path/to/MOHAA" --sd /media/SDCARD
    python3 tools/intro_movie.py "/path/to/MOHAA/main/video/intro.roq" --sd /media/SDCARD

No MOHAA data ships with DoD-GC. The player points this at their own install (or a folder they
unpacked from their CDs, or a single movie file) and it writes, under the SD card root:

    xash3d/dod/media/mohaa_intro.gcvid   video: 320x160 RGB565, 8x8-tile delta frames (engine "GCV2")
    xash3d/dod/media/mohaa_intro.gcpcm   audio: 48 kHz stereo signed 16-bit big-endian ("GCPA")

The disc only carries media/StartupVids.txt naming media/mohaa_intro.avi. The engine finds the
.gcvid/.gcpcm companions through its file system, where sd:/xash3d/<game>/ is searched on top of
the disc, and streams them from the card. A missing movie is skipped and the menu comes up. A, B or
Start skips the movie on the pad (xash3d-gc in_keys.c).

Bandwidth: the SD adapter on a real GameCube reads a few MB/s at best, and the decoder streams the
file when it is too big for ARAM. Keyframes are raw RGB565 (100 KiB at 320x160), so a movie that
changes every pixel every frame costs 1.5 MB/s at 15 fps. The frame keeps the movie's shape (the
engine letterboxes it), so MOHAA's 512x256 intro becomes 320x160, not a stretched 320x240. Two things keep it lower: a tile is only
re-sent when it differs from what the decoder already shows by more than the lowest bit per colour
channel (--exact turns this off), and --fps / --size trade smoothness or detail for rate. The tool
prints the average rate; aim for under about 1.5 MB/s on hardware.

tools/mohaa_sd.py runs this as its "movie" stage (stage_intro); this CLI is for trying other sizes.

Needs ffmpeg on PATH (it reads RoQ, Bink and the other formats MOHAA releases used). The output is
retail data: write it to the SD card or a folder outside the repository, never commit it.
"""
import argparse
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ubersound import collect, read  # noqa: E402

MOVIE_EXTS = (".roq", ".bik", ".avi", ".mpg", ".mpeg", ".smk", ".cin", ".ogv", ".mp4")
# Names tried first, best first. MOHAA's install keeps its movies loose under main/video/.
# Retail main/video/ holds EAlogo.RoQ, 2015intro.RoQ (logo stings), intro.RoQ (the 2:47 cinematic,
# silent, 512x256 at 30 fps) with its soundtrack intro.mp3, and RenSizzlefeb.mpg (a trailer).
PREFERRED = ("video/intro.roq",)
NOT_INTRO = ("logo", "2015", "sizzle", "credits")

GAMEDIR = "dod"
MEDIA_NAME = "mohaa_intro"

GCVID_MAGIC = b"GCV2"
GCVID_TILE = 8
GCVID_KEYFRAME = 0
GCVID_DELTAFRAME = 1
GCVID_MAX_W, GCVID_MAX_H = 320, 240  # engine upload limit (avi_gc.c GC_AVI_UPLOAD_MAX_*)
GCPCM_MAGIC = b"GCPA"
GCPCM_RATE, GCPCM_CHANNELS, GCPCM_WIDTH = 48000, 2, 2

# RGB565 little-endian: low byte gggbbbbb, high byte rrrrrggg. Masks drop the lowest bit of each
# channel when deciding whether a tile changed.
LO_MASK = bytes(b & 0xDE for b in range(256))  # drop b0 and g0
HI_MASK = bytes(b & 0xF7 for b in range(256))  # drop r0


def find_intro(inputs):
    """(game path, entry) of the intro movie among install dirs, pk3s or movie files, or None."""
    files = {}
    dirs = []
    for inp in inputs:
        if os.path.isfile(inp) and inp.lower().endswith(MOVIE_EXTS):
            files[os.path.basename(inp).lower()] = inp
        else:
            dirs.append(inp)
    if dirs:
        files.update(collect(dirs, MOVIE_EXTS))
    if not files:
        return None
    # A main/ folder given one level up shows up as main/video/...; match on the tail.
    for want in PREFERRED:
        for path in sorted(files):
            if path == want or path.endswith("/" + want):
                return path, files[path]
    named = [p for p in files if "intro" in os.path.basename(p) and not any(n in os.path.basename(p) for n in NOT_INTRO)]
    if len(files) == 1:
        named = list(files)
    if not named:
        return None
    # The longest of the candidates is the cinematic, not a logo sting.
    best = max(named, key=lambda p: (_size(files[p]), p))
    return best, files[best]


def find_soundtrack(inputs, movie_path):
    """The separate soundtrack MOHAA keeps beside a silent movie (video/intro.mp3), or None."""
    stem = os.path.splitext(movie_path)[0]
    files = {}
    for inp in inputs:
        if os.path.isfile(inp) and inp.lower().endswith(MOVIE_EXTS):
            d = os.path.dirname(inp) or "."
            for f in os.listdir(d):
                files[f.lower()] = os.path.join(d, f)
        elif os.path.isdir(inp) or inp.lower().endswith(".pk3"):
            files.update(collect([inp], (".mp3", ".wav")))
    for ext in (".mp3", ".wav"):
        if stem + ext in files:
            return files[stem + ext]
    return None


def _size(entry):
    if isinstance(entry, tuple):
        z, name = entry
        return z.getinfo(name).file_size
    return os.path.getsize(entry)


def _materialize(entry, tmpdir, name):
    """A real file path for ffmpeg: the file itself, or a copy out of a pk3."""
    if not isinstance(entry, tuple):
        return entry
    path = os.path.join(tmpdir, os.path.basename(name))
    with open(path, "wb") as fh:
        fh.write(read(entry))
    return path


def encode_gcvid(source, dest, width=320, height=240, fps=15, exact=False, ffmpeg="ffmpeg"):
    """Write a GCV2 stream from any movie ffmpeg reads. Returns (frames, keyframes, bytes)."""
    if width % GCVID_TILE or height % GCVID_TILE or width > GCVID_MAX_W or height > GCVID_MAX_H:
        raise ValueError("size must be a multiple of 8, at most %dx%d" % (GCVID_MAX_W, GCVID_MAX_H))
    frame_size = width * height * 2
    tiles_x, tiles_y = width // GCVID_TILE, height // GCVID_TILE
    row = GCVID_TILE * 2
    proc = subprocess.Popen(
        [ffmpeg, "-v", "error", "-i", source, "-an",
         "-vf", "fps=%d,scale=%d:%d:flags=lanczos" % (fps, width, height),
         "-pix_fmt", "rgb565le", "-f", "rawvideo", "-"],
        stdout=subprocess.PIPE)
    offsets, keyframes = [], 0
    shown = None  # tile bytes the decoder currently shows, per tile index
    shown_key = None
    os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
    body_path = dest + ".body"
    pos = 0
    try:
        with open(body_path, "wb") as body:
            while True:
                frame = proc.stdout.read(frame_size)
                if len(frame) < frame_size:
                    break
                tiles = []
                for ty in range(tiles_y):
                    base = ty * GCVID_TILE * width * 2
                    for tx in range(tiles_x):
                        start = base + tx * row
                        tiles.append(b"".join(frame[start + r * width * 2:start + r * width * 2 + row]
                                              for r in range(GCVID_TILE)))
                if exact:
                    keys = tiles
                else:
                    keys = [t[0::2].translate(LO_MASK) + t[1::2].translate(HI_MASK) for t in tiles]
                changed = [] if shown is not None else None
                if shown is not None:
                    for i, k in enumerate(keys):
                        if k != shown_key[i]:
                            changed.append(i)
                offsets.append(pos)
                if changed is None or len(changed) * (2 + len(tiles[0])) + 3 >= frame_size + 1:
                    packet = bytes([GCVID_KEYFRAME]) + frame
                    shown, shown_key = list(tiles), list(keys)
                    keyframes += 1
                else:
                    parts = [bytes([GCVID_DELTAFRAME]), struct.pack("<H", len(changed))]
                    for i in changed:
                        parts.append(struct.pack("<H", i))
                        parts.append(tiles[i])
                        shown[i], shown_key[i] = tiles[i], keys[i]
                    packet = b"".join(parts)
                body.write(packet)
                pos += len(packet)
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg could not decode %s" % source)
        if not offsets:
            raise RuntimeError("ffmpeg produced no frames for %s" % source)
        header = GCVID_MAGIC + struct.pack("<6I", width, height, fps, 1, len(offsets), GCVID_TILE)
        header += struct.pack("<%dI" % len(offsets), *offsets)
        with open(dest, "wb") as out, open(body_path, "rb") as body:
            out.write(header)
            shutil.copyfileobj(body, out)
    finally:
        if proc.poll() is None:
            proc.kill()
        if os.path.exists(body_path):
            os.remove(body_path)
    return len(offsets), keyframes, os.path.getsize(dest)


def encode_gcpcm(source, dest, ffmpeg="ffmpeg"):
    """Write the movie's audio as GCPA (48 kHz stereo s16 big-endian). False when it has none."""
    run = subprocess.run(
        [ffmpeg, "-v", "error", "-i", source, "-map", "0:a:0", "-ar", str(GCPCM_RATE),
         "-ac", str(GCPCM_CHANNELS), "-f", "s16be", "-acodec", "pcm_s16be", "-"],
        capture_output=True)
    if run.returncode != 0 and b"matches no streams" in run.stderr:
        return False
    if run.returncode != 0 or not run.stdout:
        raise RuntimeError("ffmpeg could not decode the audio of %s: %s" % (source, run.stderr.decode(errors="replace")[:200]))
    pcm = run.stdout[:len(run.stdout) - len(run.stdout) % (GCPCM_CHANNELS * GCPCM_WIDTH)]
    with open(dest, "wb") as fh:
        fh.write(GCPCM_MAGIC + struct.pack("<IHHI", GCPCM_RATE, GCPCM_CHANNELS, GCPCM_WIDTH, len(pcm)))
        fh.write(pcm)
    return True


def fit_height(source, width, ffmpeg="ffmpeg"):
    """Frame height for width that keeps the movie's shape, a multiple of 8, at most 240.

    The engine letterboxes by the frame's aspect, so MOHAA's 512x256 intro becomes 320x160 rather
    than being stretched to 4:3 (and costs a third less to stream)."""
    info = subprocess.run([ffmpeg, "-hide_banner", "-i", source], capture_output=True, text=True).stderr
    m = re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", info)
    if not m:
        return GCVID_MAX_H
    w, h = int(m.group(1)), int(m.group(2))
    return max(8, min(GCVID_MAX_H, int(round(width * h / float(w) / 8.0)) * 8))


def convert_intro(inputs, game_root, width=320, height=None, fps=15, exact=False, log=print):
    """Find the intro in the player's data and write media/mohaa_intro.* under game_root.

    Returns the files written (empty when no intro was found, which is not an error: the game then
    boots straight to the menu). Raises SystemExit when the conversion fails."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg is needed to convert the intro movie")
    found = find_intro(list(inputs))
    if not found:
        log("intro movie: none found (the game will boot straight to the menu)")
        return []
    name, entry = found
    media = os.path.join(game_root, "media")
    os.makedirs(media, exist_ok=True)
    gcvid = os.path.join(media, MEDIA_NAME + ".gcvid")
    gcpcm = os.path.join(media, MEDIA_NAME + ".gcpcm")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            src = _materialize(entry, tmp, name)
            if height is None:
                height = fit_height(src, width, ffmpeg)
            frames, keys, size = encode_gcvid(src, gcvid, width, height, fps, exact, ffmpeg)
            written = [gcvid]
            # MOHAA's intro.RoQ is silent; its music is video/intro.mp3 beside it.
            track = find_soundtrack(inputs, name)
            audio = _materialize(track, tmp, name[:-4] + ".snd") if track else src
            if encode_gcpcm(audio, gcpcm, ffmpeg):
                written.append(gcpcm)
            elif os.path.exists(gcpcm):
                os.remove(gcpcm)
    except (RuntimeError, ValueError, OSError) as e:
        raise SystemExit("intro movie: %s" % e)
    seconds = frames / float(fps)
    rate = size / seconds / 1e6 if seconds else 0.0
    log("intro movie: %s -> media/%s.gcvid (%d frames, %.1f s, %d keyframes, %.1f MB, %.2f MB/s video)"
        % (name, MEDIA_NAME, frames, seconds, keys, size / 1e6, rate))
    if rate > 1.5:
        log("  warning: over 1.5 MB/s may stutter on a real SD adapter; try --fps 12 or --size 256x192")
    return written


def stage_intro(sources, game_root, maps, work):
    """tools/mohaa_sd.py stage: the intro cinematic as media/mohaa_intro.gcvid + .gcpcm."""
    return convert_intro(sources, game_root)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="MOHAA install or main/ folder, pk3 files, or the movie file")
    ap.add_argument("--sd", required=True, help="SD card root (or a staging folder laid out like one)")
    ap.add_argument("--game", default=GAMEDIR, help="engine game folder on the card (default dod)")
    ap.add_argument("--size", default="320", help="frame width, or WIDTHxHEIGHT; multiples of 8, at most 320x240 (default 320 wide, height from the movie's shape)")
    ap.add_argument("--fps", type=int, default=15)
    ap.add_argument("--exact", action="store_true", help="re-send every tile that changes at all (bigger)")
    args = ap.parse_args(argv)
    try:
        dims = [int(v) for v in args.size.lower().split("x")]
        w, h = dims[0], (dims[1] if len(dims) > 1 else None)
    except (ValueError, IndexError):
        ap.error("--size takes WIDTH or WIDTHxHEIGHT")
    if w % 8 or not 0 < w <= GCVID_MAX_W or (h is not None and (h % 8 or not 0 < h <= GCVID_MAX_H)):
        ap.error("--size must be multiples of 8, at most %dx%d" % (GCVID_MAX_W, GCVID_MAX_H))
    try:
        written = convert_intro(args.inputs, os.path.join(args.sd, "xash3d", args.game), w, h, args.fps, args.exact)
    except SystemExit as e:
        print("error: %s" % e)
        return 1
    return 0 if written else 2


if __name__ == "__main__":
    sys.exit(main())
