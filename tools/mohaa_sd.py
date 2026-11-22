#!/usr/bin/env python3
"""Make the SD card for MOHAA on GameCube from your own copy of Medal of Honor: Allied Assault.

    python3 tools/mohaa_sd.py --mohaa "C:/Games/EA GAMES/MOHAA" --sd /media/SDCARD
    python3 tools/mohaa_sd.py --cd /mnt/cd1 /mnt/cd2 --sd /media/SDCARD --maps m1l1,m5l2b
    python3 tools/mohaa_sd.py --mohaa ~/MOHAA --sd ./sdcard --stages music --list
    python3 tools/mohaa_sd.py --mohaa ~/MOHAA --sd ./sdcard --maps m1l1 --sdhlt ~/SDHLT/tools --xash3d-gc ~/xash3d-gc

The release disc holds no game data. Everything MOHAA brings (the main menu room, loading screens, music, sounds, scripts, maps, collision,
props and terrain; the intro movie is still to come) is converted here from files you own and written under

    <sd>/xash3d/<gamedir>/          (gamedir: mohaa)

with its own gameinfo.txt and liblist.gam (falling back to dod/ for what MOHAA does not bring),
which the GameCube engine reads at runtime: sd:/ (SD2SP2) or carda:/ cardb:/ (SD Gecko), on top of the disc.

Sources (give one or both):
  --mohaa DIR   an installed game: the folder holding main/ (or main/ itself). Music is loose in
                main/sound/music and main/sound/amb_stereo, the rest in the pak*.pk3 files.
  --cd DIR...   the install CDs, mounted or copied (the folders holding DATA1.HDR and the DATAn.CAB files;
                list both CDs). Needs the `unshield` program; the cabinets are unpacked to a work folder once
                and reused.

Stages run in this order (--stages picks some; by default every one whose tools are found):
  menu      main menu background: MOHAA's war room         needs Pillow and numpy
            (resource/gc_menu/; without it the disc's DoD background shows)
  loading   loading screens: the retail ones, per map          needs Pillow and numpy
            (resource/gc_loading/; without them the engine's LOADING plaque shows)
  music     soundtracks and tracks                         needs ffmpeg
  sounds    per-map sound tables and samples
  scripts   level scripts and the global/ libraries
  maps      maps/<map>.bsp (+ .mcol collision, .nodes)     needs SDHLT: --sdhlt DIR (third_party/sdhlt-bsp30ext)
  worlddl   media/wd_<map>.gcd GameCube world bake         needs --xash3d-gc DIR (a checkout of xash3d-gc)
  props     media/gp_<map>.gcp static props and terrain    needs --xash3d-gc DIR
worlddl and props bake the maps the maps stage compiled (they keep its work folder). Each stage is a function
    stage(sources, game_root, maps, work) -> list of written paths
where sources are MOHAA main folders or pk3 files, game_root is <sd>/xash3d/<gamedir>, maps the map names
("" = every map the stage knows), and work a scratch folder kept between runs.

Needs Python 3.8+, Pillow and numpy (menu, loading), ffmpeg (audio), and for the map stages SDHLT and an xash3d-gc checkout.
Nothing it writes may be shared: it is your game's data.
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


def stage_menu(sources, game_root, maps, work):
    """The main menu background: MOHAA's main menu room (ui/main.urc) baked as the GameCube menu sheet
    (resource/gc_menu/bg_<r>_<c>.cmp/.tga, BackgroundLayout.txt, background.tga/.bmp)."""
    import mohaa_menu
    sheet = mohaa_menu.compose(sources)
    if sheet is None:
        raise SystemExit("no ui/main.urc menu in the sources")
    return mohaa_menu.write_gc_menu(sheet, game_root)


def stage_loading(sources, game_root, maps, work):
    """The loading screens: MOHAA's own (ui/loading_*.urc), one per map that has one plus the default, baked for the
    GameCube engine (resource/gc_loading/<map>.cmp, default.cmp). With --maps, the default and those maps only."""
    import mohaa_loading
    items = mohaa_loading.screens(sources)
    if not items:
        raise SystemExit("no ui/loading_*.urc screens in the sources")
    if maps:
        want = set(m.lower() for m in maps) | {"default"}
        items = [it for it in items if it[0] in want]
    return mohaa_loading.write_loading(items, game_root)


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
    maps = maps or sorted(map_sources(sources))
    if not maps:
        return []
    before = _snapshot(game_root)
    if ss.main(list(sources) + ["--out", game_root, "--maps", ",".join(maps)]):
        raise SystemExit("scripts stage failed")
    return _written(game_root, before)


# Tools the map stages run that are not Python in this repo. main() fills these from --sdhlt and --xash3d-gc.
CONFIG = {"sdhlt": None, "xash3d_gc": None, "fast_vis": False}
SDHLT = ("sdHLCSG", "sdHLBSP", "sdHLVIS")


def sdhlt_tool(name):
    """Path of an SDHLT program (from --sdhlt, else PATH), or None."""
    return shutil.which(name, path=CONFIG["sdhlt"]) if CONFIG["sdhlt"] else shutil.which(name)


def engine_script(name):
    """Path of an xash3d-gc script (from --xash3d-gc), or None."""
    root = CONFIG["xash3d_gc"]
    path = os.path.join(root, "scripts", name) if root else None
    return path if path and os.path.isfile(path) else None


def map_flags(path=os.path.join(HERE, "map_flags.txt")):
    """{map: [bsp19_to_map flags]} from tools/map_flags.txt (the GameCube fit for each retail map)."""
    flags = {}
    if os.path.isfile(path):
        for line in open(path):
            words = line.split("#", 1)[0].split()
            if words:
                flags[words[0].lower()] = words[1:]
    return flags


def map_sources(sources):
    """{map name: the MOHAA .bsp's game entry} across the sources (later ones win)."""
    from ubersound import collect
    found = {}
    for path, entry in collect(sources, (".bsp",)).items():
        if path.startswith("maps/") and path.count("/") == 1:
            found[path[5:-4]] = entry
    return found


def _map_names(sources, maps):
    known = map_sources(sources)
    names = maps or sorted(known)
    missing = [m for m in names if m not in known]
    if missing:
        raise SystemExit("no maps/%s.bsp in the sources" % ".bsp, maps/".join(missing))
    return known, names


def _run(cmd, cwd, log):
    """Run one compile tool, keeping its output in log; a failure ends the stage with the log's tail."""
    with open(log, "a") as fh:
        fh.write("$ %s\n" % " ".join(cmd))
        fh.flush()
        r = subprocess.run(cmd, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT)
    if r.returncode:
        tail = open(log, errors="replace").read().splitlines()[-8:]
        raise SystemExit("%s failed (exit %d), see %s:\n      %s" % (os.path.basename(cmd[0]), r.returncode, log,
                                                                   "\n      ".join(tail)))


def _quiet(fn, argv, log):
    """Call a tool's main(argv) with its prints sent to log; nonzero is a failure."""
    import contextlib
    with open(log, "a") as fh, contextlib.redirect_stdout(fh):
        fh.write("$ %s %s\n" % (fn.__module__, " ".join(argv)))
        rc = fn(argv)
    if rc:
        raise SystemExit("%s failed, see %s" % (fn.__module__, log))


def stage_maps(sources, game_root, maps, work):
    """Each map compiled for the GameCube: maps/<map>.bsp lit with MOHAA's own light, plus its .mcol collision
    and .nodes path nodes. Needs SDHLT (third_party/sdhlt-bsp30ext/build.sh builds the patched one)."""
    import bsp19_lightmaps
    import bsp19_to_map
    from ubersound import read
    known, names = _map_names(sources, maps)
    tools = [sdhlt_tool(t) for t in SDHLT]
    if not all(tools):
        raise SystemExit("needs SDHLT (%s): build it with third_party/sdhlt-bsp30ext/build.sh and pass --sdhlt "
                         "<dir>/SDHLT/tools" % ", ".join(SDHLT))
    csg, bsp, vis = tools
    flags = map_flags()
    out_maps = os.path.join(game_root, "maps")
    os.makedirs(out_maps, exist_ok=True)
    written = []
    for m in names:
        d = os.path.join(work, "maps", m)
        os.makedirs(d, exist_ok=True)
        log = os.path.join(d, "compile.log")
        open(log, "w").close()
        src = os.path.join(d, m + "_mohaa.bsp")   # the retail map, kept for the props stage
        with open(src, "wb") as fh:
            fh.write(read(known[m]))
        print("   %s: converting" % m)
        _quiet(bsp19_to_map.main, [src, "-o", os.path.join(d, m + ".map"), "--wad", os.path.join(d, m + ".wad")]
               + flags.get(m, []) + [a for s in sources for a in ("--scripts", s)], log)
        print("   %s: compiling (SDHLT)" % m)
        # the textures go inside the BSP, so nothing on the card points back at this work folder
        _run([csg, "-wadinclude", m + ".wad", m], d, log)
        _run([bsp, "-hull2alias", m], d, log)
        _run([vis] + (["-fast"] if CONFIG["fast_vis"] else []) + [m], d, log)
        print("   %s: lighting" % m)
        dest = os.path.join(out_maps, m + ".bsp")
        _quiet(bsp19_lightmaps.main, [src, os.path.join(d, m + ".bsp"), "-o", dest], log)
        written.append(dest)
        for ext in (".mcol", ".nodes"):
            side = os.path.join(d, m + ext)
            if os.path.isfile(side):
                shutil.copy(side, os.path.join(out_maps, m + ext))
                written.append(os.path.join(out_maps, m + ext))
    return written


def _compiled(game_root, work, maps, need):
    """The maps the maps stage has compiled (and that have work file `need`), limited to maps if given."""
    root = os.path.join(work, "maps")
    have = sorted(m for m in (os.listdir(root) if os.path.isdir(root) else [])
                  if os.path.isfile(os.path.join(game_root, "maps", m + ".bsp"))
                  and (not need or os.path.isfile(os.path.join(root, m, m + need))))
    return [m for m in have if not maps or m in maps]


def stage_worlddl(sources, game_root, maps, work):
    """The GameCube world bake of each compiled map (media/wd_<map>.gcd, _lf.gcd), with xash3d-gc's baker."""
    script = engine_script("bake_worlddl_goldsrc.py")
    if not script:
        raise SystemExit("needs --xash3d-gc <checkout> (scripts/bake_worlddl_goldsrc.py)")
    media = os.path.join(game_root, "media")
    os.makedirs(media, exist_ok=True)
    written = []
    for m in _compiled(game_root, work, maps, None):
        out = os.path.join(media, "wd_%s.gcd" % m)
        _run([sys.executable, script, "--map", os.path.join(game_root, "maps", m + ".bsp"), "--out", out],
             media, os.path.join(work, "maps", m, "bake.log"))
        written += [p for p in (out, out[:-4] + "_lf.gcd", out[:-4] + "_sb.gcd") if os.path.isfile(p)]
    return written


def stage_props(sources, game_root, maps, work):
    """Each compiled map's static props, terrain and curved surfaces (media/gp_<map>.gcp, pt_<map>.gct):
    props_models.py packs them from your paks, then xash3d-gc's baker lights them from the compiled map."""
    import props_models
    script = engine_script("bake_props_goldsrc.py")
    if not script:
        raise SystemExit("needs --xash3d-gc <checkout> (scripts/bake_props_goldsrc.py)")
    media = os.path.join(game_root, "media")
    os.makedirs(media, exist_ok=True)
    written = []
    for m in _compiled(game_root, work, maps, ".props"):
        d = os.path.join(work, "maps", m)
        log = os.path.join(d, "props.log")
        open(log, "w").close()
        mprop = os.path.join(d, m + ".mprop")
        try:
            _quiet(props_models.main, list(sources) + [os.path.join(d, m + ".props"), "-o", mprop,
                                                       "--bsp", os.path.join(d, m + "_mohaa.bsp")], log)
        except SystemExit:
            if not os.path.isfile(mprop):
                raise
            print("   %s: some prop models or textures are missing (see %s)" % (m, log))
        _run([sys.executable, script, "--map", os.path.join(game_root, "maps", m + ".bsp"), "--mprop", mprop,
              "--out", media], media, log)
        written += [p for p in (os.path.join(media, "gp_%s.gcp" % m), os.path.join(media, "pt_%s.gct" % m))
                    if os.path.isfile(p)]
    return written


# name -> function, in the order they run (maps before the bakes that read the compiled map). The intro movie
# (tools/intro_movie.py stage_intro) plugs in here with the same signature.
STAGES = {
    "menu": stage_menu,
    "loading": stage_loading,
    "music": stage_music,
    "sounds": stage_sounds,
    "scripts": stage_scripts,
    "maps": stage_maps,
    "worlddl": stage_worlddl,
    "props": stage_props,
}


def missing_tools(stage):
    """Why a stage can't run here (a tool it needs is missing), or None."""
    if stage in ("menu", "loading"):
        try:
            import numpy  # noqa: F401
            import PIL  # noqa: F401
        except ImportError:
            return "needs Pillow and numpy (pip install pillow numpy)"
    if stage == "music" and not shutil.which("ffmpeg"):
        return "needs ffmpeg"
    if stage == "maps" and not all(sdhlt_tool(t) for t in SDHLT):
        return "needs SDHLT (--sdhlt)"
    if stage in ("worlddl", "props") and not CONFIG["xash3d_gc"]:
        return "needs --xash3d-gc"
    return None


TITLE = "Medal of Honor: Allied Assault"
MARK = "written by mohaa-gc tools/mohaa_sd.py"


def write_gameinfo(game_root, gamedir, fallback="dod"):
    """The game folder's gameinfo.txt and liblist.gam: our own text, not game data. The game runs DoD-GC's game
    code with this folder on top of dod/ (fallback_dir), so whatever MOHAA does not bring comes from DoD.
    A file someone else wrote is left alone."""
    files = {
        "gameinfo.txt": ("// MOHAA on GameCube, %s\n" % MARK
                         + "basedir\t\t\"valve\"\ngamedir\t\t\"%s\"\nfallback_dir\t\"%s\"\n" % (gamedir, fallback)
                         + "title\t\t\"%s\"\nstartmap\t\"m1l1\"\n" % TITLE),
        "liblist.gam": ("// MOHAA on GameCube, %s\n" % MARK
                        + "game \"%s\"\nfallback_dir \"%s\"\nstartmap \"m1l1\"\n" % (TITLE, fallback)),
    }
    written = []
    for name, text in files.items():
        path = os.path.join(game_root, name)
        if os.path.isfile(path) and MARK not in open(path, errors="replace").read():
            print("keeping %s (not ours)" % path)
            continue
        with open(path, "w", newline="\n") as fh:
            fh.write(text)
        written.append(path)
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mohaa", help="installed MOHAA folder (holding main/)")
    ap.add_argument("--cd", nargs="+", help="install CD folders (holding DATA1.HDR / DATAn.CAB)")
    ap.add_argument("--sd", required=True, help="SD card root (or a folder to copy onto one later)")
    ap.add_argument("--gamedir", default="mohaa", help="game folder under xash3d/ (default mohaa)")
    ap.add_argument("--maps", default="", help="comma-separated maps (default: all the stage knows)")
    ap.add_argument("--stages", help="comma-separated stages (default: every one whose tools are here; have: %s)"
                    % ", ".join(STAGES))
    ap.add_argument("--sdhlt", help="folder holding sdHLCSG, sdHLBSP, sdHLVIS (default: PATH)")
    ap.add_argument("--xash3d-gc", dest="xash3d_gc", help="xash3d-gc checkout, for the GameCube bakes (worlddl, props)")
    ap.add_argument("--fast-vis", action="store_true", help="sdHLVIS -fast (quicker compiles, more overdraw)")
    ap.add_argument("--work", help="scratch folder kept between runs (default <sd>/.mohaa-work)")
    ap.add_argument("--list", action="store_true", help="list every file written")
    a = ap.parse_args(argv)
    if not a.mohaa and not a.cd:
        ap.error("give --mohaa or --cd (or both)")
    CONFIG.update(sdhlt=a.sdhlt, xash3d_gc=a.xash3d_gc, fast_vis=a.fast_vis)
    if a.stages:
        stages = [s.strip() for s in a.stages.split(",") if s.strip()]
        for s in stages:
            if s not in STAGES:
                ap.error("unknown stage %r (have: %s)" % (s, ", ".join(STAGES)))
        stages = [s for s in STAGES if s in stages]   # always in pipeline order
    else:
        stages = []
        for s in STAGES:
            why = missing_tools(s)
            if why:
                print("skipping %s: %s" % (s, why))
            else:
                stages.append(s)
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
    if a.gamedir.lower() != "dod":   # never over DoD's own folder
        write_gameinfo(game_root, a.gamedir)
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
