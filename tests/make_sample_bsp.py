#!/usr/bin/env python3
"""Write a small synthetic MOHAA BSP for tests (no game data needed).

Contents: a 2048-unit floor slab and a crate (world), a clip brush, a water
brush, a door brush model, two curved patches (one collidable, one not),
three terrain patches (flat, sloped, bumpy) and two static models.
"""
from __future__ import annotations

import math
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import mohaa_bsp19 as b19  # noqa: E402

SHADERS = [
	# name, surface flags, content flags
	("textures/general/concrete", 0, b19.CONTENTS_SOLID),
	("textures/common/caulk", b19.SURF_NODRAW, b19.CONTENTS_SOLID),
	("textures/common/clip", b19.SURF_NODRAW, b19.CONTENTS_PLAYERCLIP),
	("textures/liquids/water", 0, b19.CONTENTS_WATER),
	("textures/general/archway", 0, b19.CONTENTS_SOLID),
	("textures/general/vines", b19.SURF_NONSOLID, b19.CONTENTS_SOLID),
	("textures/terrain/grass", 0, b19.CONTENTS_SOLID),
]
S_CONCRETE, S_CAULK, S_CLIP, S_WATER, S_ARCH, S_VINES, S_GRASS = range(len(SHADERS))


def box_sides(planes, mins, maxs, shaders):
	"""Append 6 axial planes for a box; return (plane index, shader) pairs."""
	out = []
	for axis in range(3):
		for sign, d in ((1, maxs[axis]), (-1, -mins[axis])):
			n = [0.0, 0.0, 0.0]
			n[axis] = float(sign)
			planes.append((*n, float(d)))
			out.append((len(planes) - 1, shaders[len(out) % len(shaders)]))
	return out


def build(version: int = 19) -> bytes:
	planes = []
	brushsides = []
	brushes = []

	def add_brush(mins, maxs, side_shaders, brush_shader):
		first = len(brushsides)
		for pi, sh in box_sides(planes, mins, maxs, side_shaders):
			brushsides.append((pi, sh, -1))
		brushes.append((first, 6, brush_shader))

	# world brushes: floor (top face concrete, rest caulk), crate, clip, water
	add_brush((-1024, -1024, -64), (1024, 1024, 0), [S_CAULK, S_CAULK, S_CAULK, S_CAULK, S_CONCRETE, S_CAULK], S_CONCRETE)
	add_brush((0, 0, 0), (64, 64, 64), [S_CONCRETE], S_CONCRETE)
	add_brush((200, 200, 0), (264, 264, 128), [S_CLIP], S_CLIP)
	add_brush((-512, -512, -64), (-256, -256, -8), [S_WATER], S_WATER)
	n_world = len(brushes)
	# brush model 1: a door
	add_brush((400, 0, 0), (408, 96, 120), [S_CONCRETE], S_CONCRETE)

	surfaces = []

	def surf(shader, stype, pw=0, ph=0):
		v = [shader, -1, stype, 0, 0, 0, 0, -1, 0, 0, 0, 0] + [0.0] * 12 + [pw, ph, 4.0]
		surfaces.append(struct.pack("<12i3f9f2if", *v))

	surf(S_CONCRETE, b19.MST_PLANAR)
	surf(S_ARCH, b19.MST_PATCH, 5, 3)  # 2 bezier pieces, collidable
	surf(S_VINES, b19.MST_PATCH, 3, 3)  # 1 piece, non-solid
	surf(S_GRASS, b19.MST_TERRAIN)

	def terrain(x, y, base, fn):
		heights = bytes(max(0, min(255, int(fn(i, j)))) for j in range(9) for i in range(9))
		rec = bytearray(b19.SZ_TERRAPATCH)
		struct.pack_into("<2b", rec, 36, x, y)
		struct.pack_into("<hH", rec, 38, base, S_GRASS)
		rec[304:304 + 81] = heights
		return bytes(rec)

	terrain_recs = [
		terrain(-16, -16, 0, lambda i, j: 0),  # flat -> one 512 cell
		terrain(-8, -16, 0, lambda i, j: i * 4),  # planar slope -> one 512 cell
		terrain(0, -16, 0, lambda i, j: 40 + 30 * math.sin(i * 1.3) * math.cos(j * 1.1)),  # bumpy -> 64 cells
	]

	def static_model(path, origin):
		rec = bytearray(b19.SZ_STATICMODEL)
		rec[:len(path)] = path.encode()
		struct.pack_into("<3f3ff", rec, 128, *origin, 0, 90, 0, 1.0)
		return bytes(rec)

	statics = [static_model("static/barrel.tik", (10, 20, 0)), static_model("static/barrel.tik", (50, 20, 0))]

	models = [
		struct.pack("<6f4i", -1024, -1024, -64, 1024, 1024, 256, 0, 4, 0, n_world),
		struct.pack("<6f4i", 400, 0, 0, 408, 96, 120, 0, 0, n_world, 1),
	]
	entities = (
		'{\n"classname" "worldspawn"\n}\n'
		'{\n"classname" "info_player_allied"\n"origin" "0 0 16"\n}\n'
		'{\n"classname" "func_door"\n"model" "*1"\n"targetname" "door1"\n}\n'
		'{\n"classname" "actor"\n"origin" "128 0 16"\n}\n'
		'{\n"classname" "info_pathnode"\n"origin" "64 64 16"\n}\n'
		'{\n"classname" "info_pathnode"\n"origin" "128 64 16"\n}\n'
		'{\n"classname" "light"\n"origin" "0 0 128"\n}\n'
	).encode() + b"\0"

	lumps = {i: b"" for i in range(b19.HEADER_LUMPS)}
	lumps[b19.LUMP_SHADERS] = b"".join(
		struct.pack("<64s3i64s", n.encode(), sf, cf, 0, b"") for n, sf, cf in SHADERS)
	lumps[b19.LUMP_PLANES] = b"".join(struct.pack("<4f", *p) for p in planes)
	lumps[b19.LUMP_LIGHTMAPS] = bytes(b19.LIGHTMAP_BYTES * 2)
	lumps[b19.LUMP_SURFACES] = b"".join(surfaces)
	lumps[b19.LUMP_BRUSHSIDES] = b"".join(struct.pack("<3i", *s) for s in brushsides)
	lumps[b19.LUMP_BRUSHES] = b"".join(struct.pack("<3i", *b) for b in brushes)
	lumps[b19.LUMP_MODELS] = b"".join(models)
	lumps[b19.LUMP_ENTITIES] = entities
	lumps[b19.LUMP_LEAFS] = bytes((b19.SZ_LEAF_V19 if version >= 19 else b19.SZ_LEAF_V17) * 3)
	lumps[b19.LUMP_TERRAIN] = b"".join(terrain_recs)
	if version >= 19:
		lumps[b19.LUMP_STATICMODELDEF] = b"".join(statics)

	# Directory order on disk; v17/18 have an extra lump after LUMP_BRUSHES.
	order = list(range(b19.HEADER_LUMPS))
	ondisk = []
	for i in order:
		ondisk.append(lumps[i])
		if version <= 18 and i == b19.LUMP_BRUSHES:
			ondisk.append(b"")  # extra (fog) lump
	ondisk = ondisk[: b19.HEADER_LUMPS + (1 if version <= 18 else 0)]

	header_size = 12 + 8 * len(ondisk)
	body = bytearray()
	dirents = []
	for blob in ondisk:
		ofs = header_size + len(body)
		dirents.append((ofs, len(blob)))
		body += blob
		body += bytes((-len(body)) % 4)
	head = b19.BSP_IDENT + struct.pack("<ii", version, 0x1234)
	head += b"".join(struct.pack("<ii", *d) for d in dirents)
	return head + bytes(body)


def main():
	out = Path(sys.argv[1] if len(sys.argv) > 1 else "sample.bsp")
	out.write_bytes(build(int(sys.argv[2]) if len(sys.argv) > 2 else 19))
	print(out)


if __name__ == "__main__":
	main()
