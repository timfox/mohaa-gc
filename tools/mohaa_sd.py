#!/usr/bin/env python3
"""Make a DoD-GC SD card from your own copy of Medal of Honor: Allied Assault.

    python3 tools/mohaa_sd.py --mohaa "C:/Games/EA GAMES/MOHAA" --sd /media/SDCARD
    python3 tools/mohaa_sd.py --cd /mnt/cd1 /mnt/cd2 --sd /media/SDCARD --maps m1l1,m5l2b
    python3 tools/mohaa_sd.py --mohaa ~/MOHAA --sd ./sdcard --stages music --list

The release disc holds no game data. Everything MOHAA brings (music, sounds, scripts, and later maps, props,
collision and the intro movie) is converted here from files you own and written under

    <sd>/xash3d/<gamedir>/          (gamedir: dod)

which the GameCube engine reads at runtime: sd:/ (SD2SP2) or carda:/ cardb:/ (SD Gecko), on top of the disc.

Sources (give one or both):
  --mohaa DIR   an installed game: the folder holding main/ (or main/ itself). Music is loose in
                main/sound/music and main/sound/amb_stereo, the rest in the pak*.pk3 files.
  --cd DIR...   the install CDs, mounted or copied (the folders holding DATA1.HDR and the DATAn.CAB files;
                list both CDs). Needs the `unshield` program; the cabinets are unpacked to a work folder once
                and reused.

Stages (--stages, default all that are ready): see STAGES below. Each is a function
    stage(sources, game_root, maps, work) -> list of written paths
where sources are MOHAA main folders or pk3 files, game_root is <sd>/xash3d/<gamedir>, maps the map names
("" = every map the stage knows), and work a scratch folder kept between runs.

Needs Python 3.8+ and ffmpeg (for audio). Nothing it writes may be shared: it is your game's data.
"""
import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# InstallShield file groups on the retail CDs, and where their files go under main/ (the cabinets store
# each group's files flat). pk3 files from any group go to main/.
CD_GROUPS = {
    "Music Files": "sound/music",
    "Sound AmbStereo Files": "sound/amb_stereo",
    "Video Files": "video",          # intro.RoQ + intro.mp3 for the movie stage
}


def find_main(root):
    """The MOHAA main folder in or at root (any letter case), or None."""
    if not os.path.isdir(root):
        return None
    names = {n.lower(): n for n in os.listdir(root)}
    if "main" in names and os.path.isdir(os.path.join(root, names["main"])):
        return os.path.join(root, names["main"])
    if any(n.startswith("pak") and n.endswith(".pk3") for n in names):
        return root
    return None


def find_cab_set(dirs):
    """{lower name: path} of DATA*.HDR / DATA*.CAB across the CD folders (searched two levels deep)."""
    found = {}
    for d in dirs:
        for base, subdirs, files in os.walk(d):
            if base[len(d):].count(os.sep) > 2:
                subdirs[:] = []
                continue
            for f in files:
                lf = f.lower()
                if lf.startswith("data") and lf.endswith((".cab", ".hdr")):
                    found.setdefault(lf, os.path.join(base, f))
    return found


def unpack_cds(dirs, work, log=print):
    """Unpack the music groups and every pk3 from the CDs' cabinets into <work>/cd/main; returns that folder."""
    out = os.path.join(work, "cd", "main")
    done = os.path.join(work, "cd", ".done")
    if os.path.exists(done):
        return out
    unshield = shutil.which("unshield")
    if not unshield:
        raise SystemExit("--cd needs the unshield program (Debian/Ubuntu: apt install unshield; macOS: brew install unshield)")
    cabs = find_cab_set(dirs)
    if "data1.hdr" not in cabs or "data1.cab" not in cabs:
        raise SystemExit("no DATA1.HDR/DATA1.CAB under %s" % ", ".join(dirs))
    # unshield wants the whole set in one folder: link (or copy) them side by side
    cabdir = os.path.join(work, "cd", "cabs")
    os.makedirs(cabdir, exist_ok=True)
    for name, path in cabs.items():
        dest = os.path.join(cabdir, name.upper())
        if not os.path.exists(dest):
            try:
                os.symlink(os.path.abspath(path), dest)
            except OSError:
                shutil.copy(path, dest)
    groups_out = os.path.join(work, "cd", "groups")
    log("unpacking the install cabinets (once) ...")
    subprocess.run([unshield, "-L", "-d", groups_out, "x", os.path.join(cabdir, "DATA1.CAB")],
                   check=True, stdout=subprocess.DEVNULL)
    os.makedirs(out, exist_ok=True)
    for group in sorted(os.listdir(groups_out)):
        gdir = os.path.join(groups_out, group)
        if not os.path.isdir(gdir):
            continue
        sub = next((v for k, v in CD_GROUPS.items() if k.lower() == group.lower()), None)
        for base, _, files in os.walk(gdir):
            for f in files:
                src = os.path.join(base, f)
                if f.lower().endswith(".pk3"):
                    dest = os.path.join(out, f.lower())
                elif sub:
                    dest = os.path.join(out, sub, f.lower())
                else:
                    continue
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                os.replace(src, dest)
    shutil.rmtree(groups_out, ignore_errors=True)
    open(done, "w").close()
    return out


def _written(root, before):
    after = set()
    for base, _, files in os.walk(root):
        for f in files:
            after.add(os.path.join(base, f))
    return sorted(after - before)


def _snapshot(root):
    s = set()
    for base, _, files in os.walk(root):
        for f in files:
            s.add(os.path.join(base, f))
    return s


from intro_movie import stage_intro  # noqa: E402


def stage_music(sources, game_root, maps, work):
    """Every soundtrack (music/<name>.mood) and track (sound/mohaa/music/*.wav, 22 kHz mono PCM)."""
    import music
    before = _snapshot(game_root)
    if music.main(list(sources) + ["--out", game_root, "--convert"]):
        raise SystemExit("music stage failed")
    return _written(game_root, before)


def stage_sounds(sources, game_root, maps, work):
    """Per-map sound tables (maps/<map>.snd) and their samples (sound/mohaa/...)."""
    import ubersound
    before = _snapshot(game_root)
    argv = list(sources) + ["--out", game_root, "--wav"]
    if maps:
        argv += ["--maps", ",".join(maps)]
    if ubersound.main(argv):
        raise SystemExit("sounds stage failed")
    return _written(game_root, before)


def stage_scripts(sources, game_root, maps, work):
    """The level scripts and the global/ libraries they use."""
    import stage_scripts as ss
    if not maps:
        return []   # stage_scripts needs names; with none given the maps stage decides (not ready yet)
    before = _snapshot(game_root)
    if ss.main(list(sources) + ["--out", game_root, "--maps", ",".join(maps)]):
        raise SystemExit("scripts stage failed")
    return _written(game_root, before)


# name -> (function, ready). Stages still to come plug in here with the same signature: maps (bsp19_to_map +
# SDHLT), collision (.mcol), props (props_models --bsp, then xash3d-gc's bake_props_goldsrc.py), movie
# (tools/intro_movie.py stage_intro).
STAGES = {
    "music": stage_music,
    "sounds": stage_sounds,
    "scripts": stage_scripts,
    "movie": stage_intro,
}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mohaa", help="installed MOHAA folder (holding main/)")
    ap.add_argument("--cd", nargs="+", help="install CD folders (holding DATA1.HDR / DATAn.CAB)")
    ap.add_argument("--sd", required=True, help="SD card root (or a folder to copy onto one later)")
    ap.add_argument("--gamedir", default="dod", help="game folder under xash3d/ (default dod)")
    ap.add_argument("--maps", default="", help="comma-separated maps (default: all the stage knows)")
    ap.add_argument("--stages", default=",".join(STAGES), help="comma-separated stages (default: %(default)s)")
    ap.add_argument("--work", help="scratch folder kept between runs (default <sd>/.mohaa-work)")
    ap.add_argument("--list", action="store_true", help="list every file written")
    a = ap.parse_args(argv)
    if not a.mohaa and not a.cd:
        ap.error("give --mohaa or --cd (or both)")
    stages = [s.strip() for s in a.stages.split(",") if s.strip()]
    for s in stages:
        if s not in STAGES:
            ap.error("unknown stage %r (have: %s)" % (s, ", ".join(STAGES)))
    maps = [m.strip().lower() for m in a.maps.split(",") if m.strip()]
    work = a.work or os.path.join(a.sd, ".mohaa-work")
    os.makedirs(work, exist_ok=True)

    sources = []
    if a.cd:
        sources.append(unpack_cds(a.cd, work))
    if a.mohaa:
        m = find_main(a.mohaa)
        if not m:
            ap.error("no main/ folder with pak*.pk3 in %s" % a.mohaa)
        sources.append(m)   # later inputs win: an installed (patched) game over the CDs
    game_root = os.path.join(a.sd, "xash3d", a.gamedir)
    os.makedirs(game_root, exist_ok=True)
    print("sources: %s" % ", ".join(sources))
    print("writing: %s" % game_root)
    total, failed = 0, []
    for s in stages:
        print("== %s" % s)
        try:
            files = STAGES[s](sources, game_root, maps, work)
        except SystemExit as e:   # one stage's failure does not stop the others
            print("== %s: FAILED (%s)" % (s, e))
            failed.append(s)
            continue
        size = sum(os.path.getsize(f) for f in files)
        total += size
        print("== %s: %d files, %.1f MB" % (s, len(files), size / 1048576.0))
        if a.list:
            for f in files:
                print("   " + os.path.relpath(f, a.sd))
    print("done: %.1f MB new under %s" % (total / 1048576.0, game_root))
    if failed:
        print("failed stages: %s" % ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
