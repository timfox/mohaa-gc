#!/usr/bin/env python3
"""Make the SD card for MOHAA on GameCube from your own copy of Medal of Honor: Allied Assault.

    python3 tools/mohaa_sd.py --mohaa "C:/Games/EA GAMES/MOHAA" --sd /media/SDCARD
    python3 tools/mohaa_sd.py --cd /mnt/cd1 /mnt/cd2 --sd /media/SDCARD --maps m1l1,m5l2b
    python3 tools/mohaa_sd.py --mohaa ~/MOHAA --sd ./sdcard --stages music --list
    python3 tools/mohaa_sd.py --mohaa ~/MOHAA --sd ./sdcard --maps m1l1 --xash3d-gc ~/xash3d-gc

The release disc holds no game data. Everything MOHAA brings (the main menu room, loading screens, music, sounds, scripts, maps, collision,
props, terrain and intro movie) is converted here from files you own and written under

    <sd>/xash3d/<gamedir>/          (gamedir: mohaa)

with its own gameinfo.txt and liblist.gam (falling back to dod/ for what MOHAA does not bring),
which the GameCube engine reads at runtime: sd:/ (SD2SP2) or carda:/ cardb:/ (SD Gecko), on top of the disc.

Sources (give one or both):
  --mohaa DIR   an installed game: the folder holding main/ (or main/ itself). Music is loose in
                main/sound/music and main/sound/amb_stereo, the rest in the pak*.pk3 files.
  --cd DIR...   the install CDs, mounted or copied (the folders holding DATA1.HDR and the DATAn.CAB files;
                list both CDs). Needs the `unshield` program; the cabinets are unpacked to a work folder once
                and reused.
  --music-source DIR  an extra folder containing loose sound/ music files; repeat for split extractions.
                      Used by the music stage only. Normally the installed game folder already includes these.
  --sound-source DIR  an extra folder containing loose sound/ effects and dialogue; repeat for split extractions.
                      Used by the sounds stage only.

Stages run in this order (--stages picks some; by default every one whose tools are found):
  menu      the retail main menu: the war room, its lit      needs Pillow and numpy
            spots, sign, Quit and click sounds (resource/gc_menu/; without it the stock menu shows)
  loading   loading screens: the retail ones, per map          needs Pillow and numpy
            (resource/gc_loading/; without them the engine's LOADING plaque shows)
  hud       retail MOHAA HUD artwork as 32-bit Xash3D sprites (sprites/mohaa/; needs Pillow)
  music     soundtracks and tracks                         needs ffmpeg
  sounds    per-map sound tables and samples
  scripts   level scripts and the global/ libraries
  scriptmodels static Studio models for m1l1's scripted actors and trucks (needs Pillow + DoD-GC splitter)
  tags      cutscene model tags and animation durations
  maps      maps/<map>.bsp with MOHAA's textures and skybox (+ .mcol collision, .nodes, media/lg_<map>.gcg light grid)
                                                           needs the patched SDHLT: built once (git, cmake, C++)
  worlddl   media/wd_<map>.gcd GameCube world bake         needs --xash3d-gc DIR (a checkout of xash3d-gc)
  props     media/gp_<map>.gcp static props and terrain    needs --xash3d-gc DIR
The maps stage builds SDHLT with the bsp30ext patch (third_party/sdhlt-bsp30ext, pinned to v1.3.1) the first time
into --tools-dir (default ~/.local/share/mohaa-gc, %LOCALAPPDATA%\\mohaa-gc on Windows) and reuses it; --sdhlt
points at one you built. worlddl and props bake the maps the maps stage compiled (they keep its work folder). Each stage is a function
    stage(sources, game_root, maps, work) -> list of written paths
where sources are MOHAA main folders or pk3 files, game_root is <sd>/xash3d/<gamedir>, maps the map names
("" = every map the stage knows), and work a scratch folder kept between runs.

Needs Python 3.8+, Pillow and numpy (menu, loading, map textures), ffmpeg (audio), and for the map stages SDHLT and an xash3d-gc checkout.
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
    "Sound Amb Files": "sound/amb",
    "Sound Mechanics Files": "sound/mechanics",
    "Sound Vehicle Files": "sound/vehicle",
    "Sound Weapons Files": "sound/weapons",
    "Sound Dialogue Files": "sound/dialogue",
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
    """Unpack the media groups and every pk3 from the CDs' cabinets into <work>/cd/main; returns that folder."""
    out = os.path.join(work, "cd", "main")
    done = os.path.join(work, "cd", ".done")
    # unshield -L lowercases group-directory names and replaces spaces with underscores
    # ("Sound AmbStereo Files" -> "sound_ambstereo_files"). Version the cache
    # so prior extracts without the complete sound groups are unpacked again.
    groups_key = "unshield-lowercase-groups-v3\n" + "\n".join(sorted(CD_GROUPS)) + "\n"
    if os.path.exists(done):
        with open(done) as fh:
            if fh.read() == groups_key:
                return out
        # unpacked by a version that took fewer groups (no video/ before the movie stage): redo it
        log("the CD unpack in %s predates the current file groups; unpacking again" % out)
        shutil.rmtree(os.path.join(work, "cd", "groups"), ignore_errors=True)
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
        group_name = group.lower().replace(" ", "_")
        sub = next((v for k, v in CD_GROUPS.items() if k.lower().replace(" ", "_") == group_name), None)
        for base, _, files in os.walk(gdir):
            for f in files:
                src = os.path.join(base, f)
                if f.lower().endswith(".pk3"):
                    dest = os.path.join(out, f.lower())
                elif sub:
                    rel = os.path.relpath(src, gdir).lower()
                    dest = os.path.join(out, sub, rel)
                else:
                    continue
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                os.replace(src, dest)
    shutil.rmtree(groups_out, ignore_errors=True)
    with open(done, "w") as fh:
        fh.write(groups_key)
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


def stage_menu(sources, game_root, maps, work):
    """The main menu background: MOHAA's main menu room (ui/main.urc) baked as the GameCube menu sheet
    (resource/gc_menu/bg_<r>_<c>.cmp/.tga, BackgroundLayout.txt, background.tga/.bmp)."""
    import mohaa_menu
    sheet = mohaa_menu.compose(sources)
    if sheet is None:
        raise SystemExit("no ui/main.urc menu in the sources")
    written = mohaa_menu.write_gc_menu(sheet, game_root)
    menu = mohaa_menu.room_menu(sources)
    if menu:   # the retail menu's hotspots, sign, Quit and click sounds (resource/gc_menu/mohaa_main.txt)
        written += mohaa_menu.write_room_menu(menu, game_root)
    for page in mohaa_menu.PAGES:   # the options desk and the game type cards (resource/gc_menu/mohaa_<page>.txt)
        pm = mohaa_menu.page_menu(sources, page)
        if pm:
            written += mohaa_menu.write_page(pm, game_root, page)
    return written


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


def stage_hud(sources, game_root, maps, work):
    """Convert retail HUD textures to RGBA Xash3D sprites for the GameCube renderer."""
    import mohaa_hud
    written = mohaa_hud.stage_hud(sources, game_root)
    print("   MOHAA HUD: %d retail RGBA sprites" % len(written))
    return written


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


def stage_tags(sources, game_root, maps, work):
    """Cutscene model tags and animation lengths (maps/<map>.tags) for the level scripts' "gettagposition" and
    "waittill animdone": m1l1's opening ride follows its truck path model frame by frame."""
    import mohaa_tags
    maps = maps or sorted(map_sources(sources))
    if not maps:
        return []
    before = _snapshot(game_root)
    if mohaa_tags.main(list(sources) + ["--out", game_root, "--maps", ",".join(maps)]):
        raise SystemExit("tags stage failed")
    return _written(game_root, before)


SCRIPT_TIKI_MODELS = {
    # The visible m1l1 trucks. The gmctruckpath/truck2path TIKIs are tag carriers with helper triangles.
    "m1l1": ("vehicles/gmctruck_opening.tik", "vehicles/opeltruck.tik",
             "human/german_afrika_private.tik"),
}

# The retail German private is a composite TIKI: its body, head and equipment use
# separate SKDs. The mission's default KAR 98K loadout is baked into one Studio rig.
SCRIPT_TIKI_COMPONENTS = {
    "human/german_afrika_private.tik": (
        {"mesh": "models/human/heads/dakhead.skd", "surfaces": {"head": "facewrap"}},
        {"mesh": "models/human/hands/hand.skd", "surfaces": {"hand": "handsnew"}},
        {"mesh": "models/gear/g_headgear/germanhelmet.skd",
         "surfaces": {"outside": "dak_helmet", "inside": "german-helmet_inside"}},
        {"mesh": "models/gear/dak/dakloadout.skd", "surfaces": {"dakloadout": "german_gear"}},
        {"mesh": "models/gear/dak/dakkarclip.skd", "surfaces": {"dakkarclip": "german_riflebelt"}},
    ),
}

SCRIPT_TIKI_ANIMATIONS = {
    "human/german_afrika_private.tik": (
        "opel_driver",
        "driver_killvisa", "passenger_killvisa", "guard_killvisa",
        "driver_getvisa", "passenger_getvisa", "guard_getvisa",
        "driver_idlevisa", "passenger_idlevisa", "guard_idlevisa",
    ),
}

# Keep the complete retail actor animation set, but move it out of the core
# Studio MDL. Xash3D-GC streams these native packs from ARAM one sequence at a
# time, which keeps the model header/mesh below the lean per-file MEM1 limit.
SCRIPT_TIKI_ANIMATION_PACKS = {
    "human/german_afrika_private.tik": "models/human/german_afrika_private_%s.gca",
}


def stage_script_models(sources, game_root, maps, work):
    """Bake the supported scripted TIKI meshes and a map-local precache manifest."""
    from pathlib import Path
    import importlib.util
    import mohaa_tiki_model

    split_tool = os.path.join(HERE, "..", "dod-gc", "tools", "split_studio_mdl.py")
    split_spec = importlib.util.spec_from_file_location("mohaa_split_studio_mdl", split_tool)
    if split_spec is None or split_spec.loader is None:
        raise RuntimeError("could not load dod-gc/tools/split_studio_mdl.py")
    split_studio_mdl = importlib.util.module_from_spec(split_spec)
    split_spec.loader.exec_module(split_studio_mdl)

    selected = maps or sorted(map_sources(sources))
    before = _snapshot(game_root)
    for mapname in selected:
        tikis = SCRIPT_TIKI_MODELS.get(mapname.lower(), ())
        if not tikis:
            continue
        model_paths = []
        for tiki in tikis:
            rel = "models/" + tiki[:-4] + ".mdl"
            output = os.path.join(game_root, rel)
            parts, verts, tris, textures, scale, idle = mohaa_tiki_model.convert(
                sources, tiki, Path(output),
                animation_names=SCRIPT_TIKI_ANIMATIONS.get(tiki, None),
                components=SCRIPT_TIKI_COMPONENTS.get(tiki, ()))
            print("MOHAA script model %s: %d bodygroups, %d triangles, %d bodygroup verts, scale %.5f, idle %s" %
                  (tiki, parts, tris, verts, scale, idle or "-"))
            pack_path = SCRIPT_TIKI_ANIMATION_PACKS.get(tiki)
            if pack_path:
                model_name = os.path.splitext(os.path.basename(output))[0]
                split_files, _ = split_studio_mdl.split(
                    Path(output).read_bytes(), model_name, pack_path=pack_path)
                model_dir = os.path.dirname(output)
                for filename, data in split_files.items():
                    with open(os.path.join(model_dir, filename), "wb") as fh:
                        fh.write(data)
                pack_name, pack_data = next(
                    (name, data) for name, data in split_files.items() if name.endswith(".gca"))
                print("  streamed %d sequences to %s (%d bytes); core %d bytes, external skin %d bytes" % (
                    len(SCRIPT_TIKI_ANIMATIONS[tiki]), pack_name, len(pack_data),
                    len(split_files[model_name + ".mdl"]),
                    len(split_files[model_name + "T.mdl"])))
            model_paths.append(rel)
        manifest = os.path.join(game_root, "maps", mapname.lower() + ".models")
        os.makedirs(os.path.dirname(manifest), exist_ok=True)
        with open(manifest, "w", newline="\n") as fh:
            fh.write("# Baked MOHAA script models; retail assets stay on the user's SD card.\n")
            fh.writelines(path + "\n" for path in model_paths)
    return _written(game_root, before)


# Tools the map stages run that are not Python in this repo. main() fills these from the command line.
CONFIG = {"sdhlt": None, "xash3d_gc": None, "fast_vis": False, "tools_dir": None, "build_sdhlt": True,
          "texture_size": None, "texture_budget": None}
SDHLT = ("sdHLCSG", "sdHLBSP", "sdHLVIS")
SDHLT_BUILD = os.path.join(os.path.dirname(HERE), "third_party", "sdhlt-bsp30ext", "build.sh")
_found = {}


def tools_dir():
    """Where the converter keeps tools it builds (the patched SDHLT): --tools-dir, else a per-user data folder."""
    if CONFIG["tools_dir"]:
        return CONFIG["tools_dir"]
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(base, "mohaa-gc")


def sdhlt_patched(folder):
    """True if folder holds all three SDHLT programs and its sdHLBSP is the bsp30ext build (it knows -hull2alias:
    a stock SDHLT compiles maps the GameCube can't hold)."""
    tools = [shutil.which(t, path=folder) for t in SDHLT]
    if not all(tools):
        return False
    with open(tools[1], "rb") as fh:
        return b"hull2alias" in fh.read()


def sdhlt_dir():
    """The patched SDHLT's folder: --sdhlt (only), else the one the converter built, else PATH. None if none."""
    if "sdhlt" not in _found:
        if CONFIG["sdhlt"]:   # the one asked for, or none
            cands = [CONFIG["sdhlt"]]
        else:
            cands = [os.path.join(tools_dir(), "sdhlt", "SDHLT", "tools")]
            p = shutil.which(SDHLT[1])
            if p:
                cands.append(os.path.dirname(p))
        _found["sdhlt"] = next((c for c in cands if os.path.isdir(c) and sdhlt_patched(c)), None)
    return _found["sdhlt"]


def sdhlt_buildable():
    """Why the patched SDHLT can't be built here, or None."""
    if not CONFIG["build_sdhlt"]:
        return "--no-build-sdhlt"
    lack = [t for t in ("bash", "git", "cmake") if not shutil.which(t)]
    if not any(shutil.which(c) for c in ("c++", "g++", "clang++")):
        lack.append("a C++ compiler")
    return ("building it needs " + ", ".join(lack)) if lack else None


def ensure_sdhlt(log=print):
    """The patched SDHLT's folder, building it once into tools_dir() (pinned SDHLT v1.3.1 plus
    third_party/sdhlt-bsp30ext) when there is none."""
    found = sdhlt_dir()
    if found:
        return found
    if CONFIG["sdhlt"]:
        raise SystemExit("--sdhlt %s: no sdHLCSG/sdHLBSP/sdHLVIS with the bsp30ext patch (-hull2alias) there"
                         % CONFIG["sdhlt"])
    why = sdhlt_buildable()
    if why:
        raise SystemExit("needs the patched SDHLT (%s): %s; or build it with %s and pass --sdhlt <dir>/SDHLT/tools"
                         % (", ".join(SDHLT), why, os.path.relpath(SDHLT_BUILD)))
    work = os.path.join(tools_dir(), "sdhlt")
    os.makedirs(work, exist_ok=True)
    blog = os.path.join(work, "build.log")
    log("   building the patched SDHLT once into %s (a few minutes; log: %s)" % (work, blog))
    _run(["bash", SDHLT_BUILD, work], work, blog)
    _found.pop("sdhlt", None)
    found = sdhlt_dir()
    if not found:
        raise SystemExit("SDHLT built, but no patched sdHLBSP in %s; see %s" % (work, blog))
    return found


def engine_script(name):
    """Path of an xash3d-gc script (from --xash3d-gc), or None."""
    root = CONFIG["xash3d_gc"]
    # Stage commands change cwd before invoking the baker, so a relative
    # --xash3d-gc path would otherwise be resolved from the output directory.
    path = os.path.abspath(os.path.join(root, "scripts", name)) if root else None
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


TEXTURE_SIZE = 128            # map textures' largest side by default
TEXTURE_FALLBACK = 64         # a map over its budget at TEXTURE_SIZE is built again at this
BSP_UNLIT_MAX = 3 * 1048576   # xash3d-gc's compact load: the BSP without its lighting lump (README, map_flags.txt)
LUMP_LIGHTING = 8


def bsp_unlit_size(path):
    """The BSP30's size without its lighting lump (the part the GameCube's map budget counts)."""
    import struct
    with open(path, "rb") as fh:
        head = fh.read(4 + 15 * 8)
    _, ln = struct.unpack_from("<ii", head, 4 + LUMP_LIGHTING * 8)
    return os.path.getsize(path) - ln


def stage_maps(sources, game_root, maps, work):
    """Each map compiled for the GameCube: maps/<map>.bsp lit with MOHAA's own light, plus its .mcol collision
    and .nodes path nodes. Needs SDHLT (third_party/sdhlt-bsp30ext/build.sh builds the patched one)."""
    import bsp19_lightgrid
    import bsp19_lightmaps
    import bsp19_to_map
    import mohaa_sky
    from ubersound import read
    known, names = _map_names(sources, maps)
    folder = ensure_sdhlt()
    csg, bsp, vis = (shutil.which(t, path=folder) for t in SDHLT)
    flags = map_flags()
    out_maps = os.path.join(game_root, "maps")
    os.makedirs(out_maps, exist_ok=True)
    written = []
    for m in names:
        d = os.path.join(work, "maps", m)
        os.makedirs(d, exist_ok=True)
        log = os.path.join(d, "compile.log")
        open(log, "w").close()
        # Keep the retail BSP in its own directory: SDHLT writes <map>.bsp in
        # d, while the converter derives the script name from the source stem.
        src_dir = os.path.join(d, "source")
        os.makedirs(src_dir, exist_ok=True)
        src = os.path.join(src_dir, m + ".bsp")
        source_bsp = read(known[m])
        with open(src, "wb") as fh:
            fh.write(source_bsp)
        skyname, sky_files = mohaa_sky.stage_map_sky(sources, m, source_bsp, game_root)
        if skyname:
            print("   %s: skybox %s (%d new CMPR faces)" % (m, skyname, len(sky_files)))
        else:
            print("   %s: no stageable retail skybox; leaving skyname unset" % m)
        dest = os.path.join(out_maps, m + ".bsp")
        size = CONFIG["texture_size"]
        sizes = [size] if size is not None else [TEXTURE_SIZE, TEXTURE_FALLBACK]
        for k, size in enumerate(sizes):
            textures = [] if size == 0 else [a for s in sources for a in ("--textures", s)] + ["--texture-size", str(size)]
            if textures and CONFIG["texture_budget"]:
                textures += ["--texture-budget", str(CONFIG["texture_budget"])]
            print("   %s: converting" % m)
            convert_args = [src, "-o", os.path.join(d, m + ".map"), "--wad", os.path.join(d, m + ".wad")]
            if skyname:
                convert_args += ["--skyname", skyname]
            _quiet(bsp19_to_map.main, convert_args
                   + flags.get(m, []) + [a for s in sources for a in ("--scripts", s)] + textures, log)
            print("   %s: compiling (SDHLT)" % m)
            # the textures go inside the BSP, so nothing on the card points back at this work folder
            _run([csg, "-wadinclude", m + ".wad", m], d, log)
            _run([bsp, "-hull2alias", m], d, log)
            _run([vis] + (["-fast"] if CONFIG["fast_vis"] else []) + [m], d, log)
            print("   %s: lighting" % m)
            _quiet(bsp19_lightmaps.main, [src, os.path.join(d, m + ".bsp"), "-o", dest], log)
            over = bsp_unlit_size(dest) - BSP_UNLIT_MAX
            if over <= 0:
                break
            if k + 1 < len(sizes):
                print("   %s: %d KB over the GameCube's %d KB map budget with %d-texel textures; again at %d"
                      % (m, over // 1024 + 1, BSP_UNLIT_MAX // 1024, size, sizes[k + 1]))
            else:
                print("   %s: warning: %d KB over the GameCube's %d KB map budget (without its light)"
                      % (m, over // 1024 + 1, BSP_UNLIT_MAX // 1024))
        written.append(dest)
        # MOHAA's light grid: how retail lights soldiers and other models
        grid = os.path.join(game_root, "media", "lg_%s.gcg" % m)
        try:
            _quiet(bsp19_lightgrid.main, [src, "-o", grid], log)
            written.append(grid)
        except (ValueError, SystemExit) as e:
            print("   %s: no light grid (%s); models light from the floor" % (m, e))
        for ext in (".mcol", ".nodes"):
            side = os.path.join(d, m + ext)
            if os.path.isfile(side):
                shutil.copy(side, os.path.join(out_maps, m + ext))
                written.append(os.path.join(out_maps, m + ext))
    lst = write_maps_lst(game_root)
    if lst:
        written.append(lst)
    return written


def write_maps_lst(game_root):
    """maps.lst, the list the menu's Create Game offers: every compiled map in the game folder, as
    `name "title"`. The engine can't write it on the GameCube's read-only card path, so without it Create Game
    has no map. Returns its path, or None when there is no map."""
    folder = os.path.join(game_root, "maps")
    names = sorted(f[:-4] for f in os.listdir(folder) if f.lower().endswith(".bsp")) if os.path.isdir(folder) else []
    if not names:
        return None
    # m1l1 first: the campaign's opening map, and the one Create Game selects
    names.sort(key=lambda n: (n != "m1l1", n))
    path = os.path.join(game_root, "maps.lst")
    with open(path, "w") as fh:
        fh.writelines('%s "%s"\n' % (n, n) for n in names)
    return path


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
                                                       "--bsp", os.path.join(d, "source", m + ".bsp")], log)
        except SystemExit:
            if not os.path.isfile(mprop):
                raise
            print("   %s: some prop models or textures are missing (see %s)" % (m, log))
        _run([sys.executable, script, "--map", os.path.join(game_root, "maps", m + ".bsp"), "--mprop", mprop,
              "--out", media], media, log)
        written += [p for p in (os.path.join(media, "gp_%s.gcp" % m), os.path.join(media, "pt_%s.gct" % m))
                    if os.path.isfile(p)]
    return written


# name -> function, in the order they run (maps before the bakes that read the compiled map). movie is
# tools/intro_movie.py: media/mohaa_intro.gcvid + .gcpcm, which the boot playlist plays and A/B/Start skips.
STAGES = {
    "menu": stage_menu,
    "loading": stage_loading,
    "hud": stage_hud,
    "music": stage_music,
    "sounds": stage_sounds,
    "scripts": stage_scripts,
    "tags": stage_tags,
    "scriptmodels": stage_script_models,
    "maps": stage_maps,
    "worlddl": stage_worlddl,
    "props": stage_props,
    "movie": stage_intro,
}


def missing_tools(stage):
    """Why a stage can't run here (a tool it needs is missing), or None."""
    if stage in ("menu", "loading"):
        try:
            import numpy  # noqa: F401
            import PIL  # noqa: F401
        except ImportError:
            return "needs Pillow and numpy (pip install pillow numpy)"
    if stage == "hud":
        try:
            import PIL  # noqa: F401
        except ImportError:
            return "needs Pillow (pip install pillow)"
    if stage == "scriptmodels":
        try:
            import PIL  # noqa: F401
        except ImportError:
            return "needs Pillow (pip install pillow)"
    if stage in ("maps", "props"):
        try:
            import PIL  # noqa: F401
        except ImportError:
            return "needs Pillow (pip install pillow)"
    if stage in ("music", "movie", "sounds") and not shutil.which("ffmpeg"):
        return "needs ffmpeg (MP3/audio conversion)"
    if stage == "maps" and not sdhlt_dir():
        why = "--sdhlt %s is not the patched SDHLT" % CONFIG["sdhlt"] if CONFIG["sdhlt"] else sdhlt_buildable()
        if why:
            return "needs the patched SDHLT (%s)" % why
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
    ap.add_argument("--music-source", action="append", default=[], metavar="DIR",
                    help="extra folder containing loose sound/ music files; repeat for split extractions")
    ap.add_argument("--sound-source", action="append", default=[], metavar="DIR",
                    help="extra folder containing loose sound/ effects or dialogue; repeat for split extractions")
    ap.add_argument("--movie-source", action="append", default=[], metavar="DIR",
                    help="extra folder containing the loose intro movie and soundtrack; repeat for split extractions")
    ap.add_argument("--sd", required=True, help="SD card root (or a folder to copy onto one later)")
    ap.add_argument("--gamedir", default="mohaa", help="game folder under xash3d/ (default mohaa)")
    ap.add_argument("--maps", default="", help="comma-separated maps (default: all the stage knows)")
    ap.add_argument("--stages", help="comma-separated stages (default: every one whose tools are here; have: %s)"
                    % ", ".join(STAGES))
    ap.add_argument("--sdhlt", help="folder holding the patched sdHLCSG, sdHLBSP, sdHLVIS (default: the one built "
                    "into --tools-dir, else PATH; built from third_party/sdhlt-bsp30ext when there is none)")
    ap.add_argument("--tools-dir", help="where built tools are kept between runs (default: %s)" % tools_dir())
    ap.add_argument("--no-build-sdhlt", dest="build_sdhlt", action="store_false",
                    help="never build SDHLT (the maps stage is skipped without one)")
    ap.add_argument("--xash3d-gc", dest="xash3d_gc", help="xash3d-gc checkout, for the GameCube bakes (worlddl, props)")
    ap.add_argument("--fast-vis", action="store_true", help="sdHLVIS -fast (quicker compiles, more overdraw)")
    ap.add_argument("--texture-size", type=int, default=None,
                    help="largest map texture side (default: 128, or 64 for a map that would go over the "
                         "GameCube's 3 MB map budget; 0 = placeholder checkers)")
    ap.add_argument("--texture-budget", type=int, default=None, metavar="KB",
                    help="most texture bytes a map carries; the biggest textures shrink first (default: "
                         "bsp19_to_map's)")
    ap.add_argument("--work", help="scratch folder kept between runs (default <sd>/.mohaa-work)")
    ap.add_argument("--list", action="store_true", help="list every file written")
    a = ap.parse_args(argv)
    if not a.mohaa and not a.cd:
        ap.error("give --mohaa or --cd (or both)")
    # Stages change cwd for native tools and the Xash bakers. Resolve every
    # user-supplied path at the CLI boundary so relative paths keep working.
    a.sd = os.path.abspath(a.sd)
    if a.mohaa:
        a.mohaa = os.path.abspath(a.mohaa)
    if a.cd:
        a.cd = [os.path.abspath(path) for path in a.cd]
    a.music_source = [os.path.abspath(path) for path in a.music_source]
    for path in a.music_source:
        if not os.path.isdir(path):
            ap.error("music source folder does not exist: %s" % path)
    a.sound_source = [os.path.abspath(path) for path in a.sound_source]
    for path in a.sound_source:
        if not os.path.isdir(path):
            ap.error("sound source folder does not exist: %s" % path)
    a.movie_source = [os.path.abspath(path) for path in a.movie_source]
    for path in a.movie_source:
        if not os.path.isdir(path):
            ap.error("movie source folder does not exist: %s" % path)
    for name in ("sdhlt", "tools_dir", "xash3d_gc", "work"):
        value = getattr(a, name)
        if value:
            setattr(a, name, os.path.abspath(value))
    CONFIG.update(sdhlt=a.sdhlt, xash3d_gc=a.xash3d_gc, fast_vis=a.fast_vis, tools_dir=a.tools_dir,
                  build_sdhlt=a.build_sdhlt, texture_size=a.texture_size,
                  texture_budget=a.texture_budget)
    _found.clear()
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
            extra_sources = []
            if s == "music":
                extra_sources = a.music_source
            elif s == "sounds":
                extra_sources = a.sound_source
            elif s == "movie":
                extra_sources = a.movie_source
            stage_sources = sources + extra_sources
            if extra_sources:
                print("%s sources: %s" % (s, ", ".join(extra_sources)))
            files = STAGES[s](stage_sources, game_root, maps, work)
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
