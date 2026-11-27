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
COMPASS_SPRITE_SIDE = 32
COMPASS_STATIC_SIDE = 64
COMPASS_FRAMES = 16
ROTATING_HUD_IMAGES = {"compassface.tga": 1, "compassobjarrow.tga": -1}
COMPACT_COMPASS_IMAGES = {
    "compassback.tga", "compassface.tga", "compassneedle.tga",
    "compassobjarrow.tga", "compassobjball.tga",
}
REQUIRED_HUD_IMAGES = frozenset({
    "healthback.tga",
    "healthmeter.tga",
    "healthneedle.tga",
    "ammotoparm.tga",
    "ammobotmarm.tga",
    "ammotoparmbar.tga",
    "crosshair.tga",
})


def encode_sprite_rgba(width: int, height: int, rgba: bytes) -> bytes:
    """Encode one top-left-origin RGBA image as a single-frame Xash v32 .spr."""
    return encode_sprite_frames(width, height, (rgba,))


def encode_sprite_frames(width: int, height: int, frames) -> bytes:
    """Encode equally-sized RGBA frames as a native Xash v32 animated sprite."""
    if width < 1 or height < 1 or width > MAX_IMAGE_SIDE or height > MAX_IMAGE_SIDE:
        raise ValueError("unsupported HUD image dimensions %dx%d" % (width, height))
    if width & (width - 1) or height & (height - 1):
        raise ValueError("HUD sprite dimensions must be powers of two: %dx%d" % (width, height))
    frames = tuple(frames)
    if not frames or len(frames) > 32:
        raise ValueError("sprite frame count must be between 1 and 32")
    expected = width * height * 4
    if any(len(rgba) != expected for rgba in frames):
        raise ValueError("RGBA frame payload does not match %dx%d" % (width, height))

    radius = ((width * width + height * height) ** 0.5) / 2.0
    header = struct.pack(
        "<iiifiiifi",
        IDSPRITEHEADER,
        SPRITE_VERSION_32,
        SPR_FWD_PARALLEL_UPRIGHT,
        radius,
        width,
        height,
        len(frames),
        0.0,
        0,
    )
    frame_header = struct.pack("<iiiii", FRAME_SINGLE, 0, 0, width, height)
    return header + b"".join(frame_header + rgba for rgba in frames)


def encode_rotating_compass(image, direction: int) -> bytes:
    """Bake compact compass orientations so the GC HUD can select a frame without runtime rotation."""
    from PIL import Image

    image = image.convert("RGBA").resize(
        (COMPASS_SPRITE_SIDE, COMPASS_SPRITE_SIDE), Image.Resampling.LANCZOS
    )
    frames = []
    for i in range(COMPASS_FRAMES):
        angle = direction * 360.0 * i / COMPASS_FRAMES
        rotated = image.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False,
                               fillcolor=(0, 0, 0, 0))
        frames.append(rotated.tobytes())
    return encode_sprite_frames(COMPASS_SPRITE_SIDE, COMPASS_SPRITE_SIDE, frames)


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
    missing = sorted(REQUIRED_HUD_IMAGES - set(images))
    if missing:
        missing_paths = ", ".join("textures/hud/" + name for name in missing)
        raise ValueError("retail HUD source is incomplete; missing " + missing_paths)

    outdir = os.path.join(game_root, "sprites", "mohaa")
    os.makedirs(outdir, exist_ok=True)
    written = []
    for name, entry in sorted(images.items()):
        stem, ext = os.path.splitext(name)
        if ext.lower() != ".tga" or not stem or "/" in stem or "\\" in stem:
            raise ValueError("unexpected HUD texture path: %s" % name)
        with Image.open(io.BytesIO(read(entry))) as image:
            image = image.convert("RGBA")
            if name.lower() in ROTATING_HUD_IMAGES:
                sprite = encode_rotating_compass(image, ROTATING_HUD_IMAGES[name.lower()])
            else:
                # The stationary bronze housing and needle contain fine ring
                # marks that disappear at 32 px. Keep those at 64 px; the
                # 16-frame rotating layers stay 32 px to bound MEM1 usage.
                if name.lower() in {"compassback.tga", "compassneedle.tga"}:
                    image = image.resize((COMPASS_STATIC_SIDE, COMPASS_STATIC_SIDE), Image.Resampling.LANCZOS)
                elif name.lower() in COMPACT_COMPASS_IMAGES:
                    image = image.resize((COMPASS_SPRITE_SIDE, COMPASS_SPRITE_SIDE), Image.Resampling.LANCZOS)
                sprite = encode_sprite_rgba(image.width, image.height, image.tobytes())
        path = os.path.join(outdir, stem.lower() + ".spr")
        with open(path, "wb") as fh:
            fh.write(sprite)
        written.append(path)
    return written
