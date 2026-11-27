#!/usr/bin/env python3
"""Stage MOHAA skyParms cubemaps as native GameCube CMPR sky sides.

The map converter uses the ``skyParms`` environment name as GoldSrc's
``skyname``. The GameCube runtime then reads ``media/sky_<name><side>.cmp``
instead of falling back to the clear colour.
"""
from __future__ import annotations

import os
import re
from collections import Counter
from io import BytesIO

import mohaa_bsp19 as b19
from ubersound import collect, read, strip_comments

SIDES = ("rt", "bk", "lf", "ft", "up", "dn")
SKY_SIZE = 128
_FILE_CACHE = {}


def _files(sources, extensions):
    key = (tuple(os.path.abspath(s) for s in sources), tuple(extensions))
    if key not in _FILE_CACHE:
        _FILE_CACHE[key] = collect(sources, extensions)
    return _FILE_CACHE[key]


def _shader_sky_roots(sources):
    roots = {}
    for path, entry in _files(sources, (".shader",)).items():
        if not path.startswith("scripts/"):
            continue
        text = strip_comments(read(entry).decode("latin1", "replace"))
        for match in re.finditer(r"(?m)^\s*([^\s{}]+)\s*\{", text):
            start = match.end()
            depth = 1
            end = start
            while end < len(text) and depth:
                if text[end] == "{":
                    depth += 1
                elif text[end] == "}":
                    depth -= 1
                end += 1
            if depth:
                continue
            body = text[start:end - 1]
            sky = re.search(r"(?im)^\s*skyParms\s+([^\s]+)", body)
            if sky:
                root = sky.group(1)
                if root != "-":
                    roots[match.group(1).lower()] = root.replace("\\", "/").rsplit("/", 1)[-1]
    return roots


def sky_root_from_bsp(data: bytes, name: str, sources) -> str | None:
    """Return the most-used skyParms cubemap root referenced by a MOHAA BSP."""
    bsp = b19.load_bytes(data, name)
    roots = _shader_sky_roots(sources)
    uses = Counter()
    for surface in bsp.surfaces:
        if not (0 <= surface.shader < len(bsp.shaders)):
            continue
        shader = bsp.shaders[surface.shader]
        if shader.surface_flags & b19.SURF_SKY:
            root = roots.get(shader.name.lower())
            if root:
                uses[root] += max(1, surface.num_indexes // 3)
    if not uses:
        return None
    return uses.most_common(1)[0][0]


def write_skybox(sources, root: str, game_root: str) -> list[str]:
    """Write one six-sided 128x128 CMPR skybox; source paths are read-only."""
    from PIL import Image
    import numpy as np
    import mohaa_menu

    files = _files(sources, (".jpg", ".jpeg", ".tga", ".bmp", ".png"))
    outdir = os.path.join(game_root, "media")
    os.makedirs(outdir, exist_ok=True)
    written = []
    for side in SIDES:
        key = "env/%s_%s.jpg" % (root, side)
        entry = files.get(key)
        if entry is None:
            key = "env/%s_%s.tga" % (root, side)
            entry = files.get(key)
        if entry is None:
            raise ValueError("no retail sky face %s (looked for env/%s_%s.jpg/.tga)" % (root, root, side))
        with Image.open(BytesIO(read(entry))) as image:
            rgb = image.convert("RGB").resize((SKY_SIZE, SKY_SIZE), Image.Resampling.LANCZOS)
            data = mohaa_menu.cmpr_encode(np.asarray(rgb, dtype=np.uint8))
        if len(data) != SKY_SIZE * SKY_SIZE // 2:
            raise ValueError("CMPR encoder returned %d bytes for %s" % (len(data), key))
        path = os.path.join(outdir, "sky_%s%s.cmp" % (root, side))
        with open(path, "wb") as fh:
            fh.write(data)
        written.append(path)
    return written


def stage_map_sky(sources, map_name: str, bsp_data: bytes, game_root: str) -> tuple[str | None, list[str]]:
    """Find and stage one map's cubemap, returning its GoldSrc skyname."""
    root = sky_root_from_bsp(bsp_data, "maps/%s.bsp" % map_name, sources)
    if not root:
        return None, []
    faces = [os.path.join(game_root, "media", "sky_%s%s.cmp" % (root, side)) for side in SIDES]
    expected_size = SKY_SIZE * SKY_SIZE // 2
    if all(os.path.isfile(path) and os.path.getsize(path) == expected_size for path in faces):
        return root, []
    try:
        return root, write_skybox(sources, root, game_root)
    except ValueError as exc:
        if str(exc).startswith("no retail sky face "):
            # Some retail shader entries deliberately name a nonexistent env
            # root (for example idontexist). Keep those maps' skyname unset so
            # the converter does not advertise a cubemap that cannot load.
            return None, []
        raise
