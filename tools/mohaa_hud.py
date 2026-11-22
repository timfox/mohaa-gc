#!/usr/bin/env python3
"""Convert the retail MOHAA HUD TGA set to Xash3D 32-bit sprite files.

The GameCube HUD code loads these as ordinary Half-Life sprites. Keeping the
retail RGBA pixels in the version-32 sprite format lets Xash3D upload them to
the GX renderer without palettizing or flattening the alpha edges.
"""
from __future__ import annotations

import io
import os
import struct

from ubersound import collect, read

IDSPRITEHEADER = 0x50534449  # little-endian bytes "IDSP"
SPRITE_VERSION_32 = 32
SPR_FWD_PARALLEL_UPRIGHT = 0
FRAME_SINGLE = 0
HUD_SOURCE_DIR = "textures/hud/"
MAX_IMAGE_SIDE = 512


def encode_sprite_rgba(width: int, height: int, rgba: bytes) -> bytes:
    """Encode one top-left-origin RGBA image as a single-frame Xash v32 .spr."""
    if width < 1 or height < 1 or width > MAX_IMAGE_SIDE or height > MAX_IMAGE_SIDE:
        raise ValueError("unsupported HUD image dimensions %dx%d" % (width, height))
    if width & (width - 1) or height & (height - 1):
        raise ValueError("HUD sprite dimensions must be powers of two: %dx%d" % (width, height))
    if len(rgba) != width * height * 4:
        raise ValueError("RGBA payload is %d bytes, expected %d" % (len(rgba), width * height * 4))

    radius = ((width * width + height * height) ** 0.5) / 2.0
    header = struct.pack(
        "<iiifiiifi",
        IDSPRITEHEADER,
        SPRITE_VERSION_32,
        SPR_FWD_PARALLEL_UPRIGHT,
        radius,
        width,
        height,
        1,
        0.0,
        0,
    )
    frame = struct.pack("<iiiii", FRAME_SINGLE, 0, 0, width, height)
    return header + frame + rgba


def stage_hud(sources, game_root: str) -> list[str]:
    """Convert every ``textures/hud/*.tga`` found in the supplied retail sources."""
    from PIL import Image

    images = {
        path[len(HUD_SOURCE_DIR):]: entry
        for path, entry in collect(sources, (".tga",)).items()
        if path.startswith(HUD_SOURCE_DIR)
    }
    if not images:
        raise ValueError("no retail textures/hud/*.tga files found in the MOHAA sources")

    outdir = os.path.join(game_root, "sprites", "mohaa")
    os.makedirs(outdir, exist_ok=True)
    written = []
    for name, entry in sorted(images.items()):
        stem, ext = os.path.splitext(name)
        if ext.lower() != ".tga" or not stem or "/" in stem or "\\" in stem:
            raise ValueError("unexpected HUD texture path: %s" % name)
        with Image.open(io.BytesIO(read(entry))) as image:
            image = image.convert("RGBA")
            sprite = encode_sprite_rgba(image.width, image.height, image.tobytes())
        path = os.path.join(outdir, stem.lower() + ".spr")
        with open(path, "wb") as fh:
            fh.write(sprite)
        written.append(path)
    return written
