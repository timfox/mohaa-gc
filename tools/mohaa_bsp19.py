#!/usr/bin/env python3
"""Read Medal of Honor: Allied Assault BSP files ("2015" ident, versions 17-21).

Pure standard library. Written from the on-disk struct layouts (as documented
in OpenMoHAA's code/qcommon/qfiles.h); no code is copied from GPL projects.

Only the lumps the budget report needs are decoded: shaders, planes, surfaces,
brush sides, brushes, models, entities, leafs, terrain patches and static
model definitions. Everything else is exposed as raw lump sizes.
"""
from __future__ import annotations

import re
import struct
from dataclasses import dataclass, field

BSP_IDENT = b"2015"
BSP_MIN_VERSION = 17  # beta Allied Assault
BSP_VERSION_AA = 19  # Allied Assault retail
BSP_MAX_VERSION = 21  # Breakthrough

HEADER_LUMPS = 28

# Lump numbers for version 19+. Versions 17-18 carry an extra lump after
# LUMP_BRUSHES, so every lump after it is shifted up by one.
LUMP_SHADERS = 0
LUMP_PLANES = 1
LUMP_LIGHTMAPS = 2
LUMP_SURFACES = 3
LUMP_DRAWVERTS = 4
LUMP_DRAWINDEXES = 5
LUMP_LEAFBRUSHES = 6
LUMP_LEAFSURFACES = 7
LUMP_LEAFS = 8
LUMP_NODES = 9
LUMP_SIDEEQUATIONS = 10
LUMP_BRUSHSIDES = 11
LUMP_BRUSHES = 12
LUMP_MODELS = 13
LUMP_ENTITIES = 14
LUMP_VISIBILITY = 15
LUMP_LIGHTGRIDPALETTE = 16
LUMP_LIGHTGRIDOFFSETS = 17
LUMP_LIGHTGRIDDATA = 18
LUMP_SPHERELIGHTS = 19
LUMP_SPHERELIGHTVIS = 20
LUMP_LIGHTDEFS = 21
LUMP_TERRAIN = 22
LUMP_TERRAININDEXES = 23
LUMP_STATICMODELDATA = 24
LUMP_STATICMODELDEF = 25
LUMP_STATICMODELINDEXES = 26
LUMP_DUMMY10 = 27

LUMP_NAMES = [
	"shaders", "planes", "lightmaps", "surfaces", "drawverts", "drawindexes",
	"leafbrushes", "leafsurfaces", "leafs", "nodes", "sideequations",
	"brushsides", "brushes", "models", "entities", "visibility",
	"lightgridpalette", "lightgridoffsets", "lightgriddata", "spherelights",
	"spherelightvis", "lightdefs", "terrain", "terrainindexes",
	"staticmodeldata", "staticmodeldef", "staticmodelindexes", "dummy10",
]

# Record sizes (bytes).
SZ_SHADER = 140  # char[64] name, int surf, int contents, int subdiv, char[64] fence
SZ_PLANE = 16
SZ_SURFACE = 108
SZ_DRAWVERT = 44
SZ_BRUSHSIDE = 12  # plane, shader, equation
SZ_BRUSH = 12  # firstSide, numSides, shader
SZ_MODEL = 40
SZ_LEAF_V19 = 64
SZ_LEAF_V17 = 56
SZ_TERRAPATCH = 388
SZ_STATICMODEL = 164
LIGHTMAP_BYTES = 128 * 128 * 3

# Surface types.
MST_BAD, MST_PLANAR, MST_PATCH, MST_TRIANGLE_SOUP, MST_FLARE, MST_TERRAIN = range(6)
SURFACE_TYPE_NAMES = {0: "bad", 1: "planar", 2: "patch", 3: "soup", 4: "flare", 5: "terrain"}

# Content flags (MOHAA surfaceflags.h).
CONTENTS_SOLID = 0x1
CONTENTS_LADDER = 0x2
CONTENTS_LAVA = 0x8
CONTENTS_SLIME = 0x10
CONTENTS_WATER = 0x20
CONTENTS_FOG = 0x40
CONTENTS_FENCE = 0x2000
CONTENTS_AREAPORTAL = 0x8000
CONTENTS_PLAYERCLIP = 0x10000
CONTENTS_MONSTERCLIP = 0x20000
CONTENTS_WEAPONCLIP = 0x40000
CONTENTS_VEHICLECLIP = 0x80000
CONTENTS_ORIGIN = 0x1000000
CONTENTS_DETAIL = 0x8000000
CONTENTS_TRIGGER = 0x40000000
CONTENTS_FLUID = CONTENTS_WATER | CONTENTS_SLIME | CONTENTS_LAVA
CONTENTS_ANYCLIP = CONTENTS_PLAYERCLIP | CONTENTS_MONSTERCLIP | CONTENTS_WEAPONCLIP | CONTENTS_VEHICLECLIP

# Surface flags.
SURF_SKY = 0x4
SURF_NODRAW = 0x80
SURF_NONSOLID = 0x800

# Terrain: a patch is 8x8 cells of 64 units; heights are base + 2 * byte.
TERRAIN_CELL = 64
TERRAIN_PATCH_SIZE = 512
TERRAIN_SAMPLES = 9


class BspError(ValueError):
	pass


@dataclass
class Shader:
	name: str
	surface_flags: int
	content_flags: int
	subdivisions: int


@dataclass
class Surface:
	shader: int
	surface_type: int
	num_verts: int
	num_indexes: int
	patch_width: int
	patch_height: int
	subdivisions: float
	first_vert: int = 0
	first_index: int = 0
	lightmap: int = -1  # lightmap page, -1 = lit by its vertex colours


@dataclass
class Brush:
	first_side: int
	num_sides: int
	shader: int


@dataclass
class Model:
	mins: tuple
	maxs: tuple
	first_surface: int
	num_surfaces: int
	first_brush: int
	num_brushes: int


@dataclass
class TerrainPatch:
	x: int  # in 64-unit cells
	y: int
	base_z: int
	shader: int
	heights: list  # 81 world-space heights, row-major (index = j * 9 + i, i along x)
	tex: tuple = ()  # texCoord[2][2][2]: (s, t) at the corners (x0 y0, x0 y1, x1 y0, x1 y1), as read
	lm_page: int = -1  # its lightmap page
	lm_s: int = 0  # the lightmap texel of sample (0, 0)
	lm_t: int = 0
	lm_scale: int = 1  # lightmap texels per 64-unit cell

	@property
	def origin(self):
		return (self.x * TERRAIN_CELL, self.y * TERRAIN_CELL)


@dataclass
class StaticModel:
	model: str
	origin: tuple
	angles: tuple
	scale: float


@dataclass
class Bsp:
	name: str
	version: int
	checksum: int
	file_size: int
	lump_sizes: dict
	shaders: list = field(default_factory=list)
	num_planes: int = 0
	planes: list = field(default_factory=list)  # (nx, ny, nz, dist)
	brushsides: list = field(default_factory=list)  # (plane, shader)
	surfaces: list = field(default_factory=list)
	brushsides_shader: list = field(default_factory=list)
	brushes: list = field(default_factory=list)
	models: list = field(default_factory=list)
	entities: list = field(default_factory=list)
	num_leafs: int = 0
	num_nodes: int = 0
	num_lightmaps: int = 0
	num_drawverts: int = 0
	drawverts: list = field(default_factory=list)  # xyz of each draw vertex (patch control points)
	drawvert_st: list = field(default_factory=list)  # (s, t) of each draw vertex
	drawvert_normals: list = field(default_factory=list)  # normal of each draw vertex
	drawindexes: list = field(default_factory=list)  # triangle indexes, relative to a surface's first_vert
	drawvert_lmst: list = field(default_factory=list)  # lightmap (s, t) of each draw vertex, 0..1 over a page
	drawvert_color: list = field(default_factory=list)  # RGBA of each draw vertex (vertex-lit light)
	lightmaps: bytes = b""  # 128 x 128 RGB pages, one overbright bit down
	terrain: list = field(default_factory=list)
	static_models: list = field(default_factory=list)


def _cstr(b: bytes) -> str:
	return b.split(b"\0", 1)[0].decode("latin-1", "replace")


def _lump_index(version: int, lump: int) -> int:
	if version <= 18 and lump > LUMP_BRUSHES:
		return lump + 1
	return lump


def parse_entities(text: str) -> list[dict]:
	"""Parse a Q3-style entity string into a list of key/value dicts."""
	ents = []
	for block in re.finditer(r"\{(.*?)\}", text, re.S):
		kv = {}
		for k, v in re.findall(r'"([^"]*)"\s+"([^"]*)"', block.group(1)):
			kv[k] = v
		# Radiant writes many MOHAA names as "$targetname" (flak88_1 on m5l2b, the exploders);
		# the game reads them as targetname. A plain key, when both are there, wins.
		for k in [k for k in kv if k.startswith("$") and len(k) > 1]:
			kv.setdefault(k[1:], kv.pop(k))
		ents.append(kv)
	return ents


def _records(data: bytes, size: int):
	n = len(data) // size
	return [data[i * size:(i + 1) * size] for i in range(n)]


def load_bytes(data: bytes, name: str = "<memory>") -> Bsp:
	if len(data) < 12:
		raise BspError(f"{name}: too small to be a BSP")
	ident = data[:4]
	if ident != BSP_IDENT:
		raise BspError(f"{name}: ident {ident!r} is not MOHAA '2015'")
	version, checksum = struct.unpack_from("<ii", data, 4)
	if not BSP_MIN_VERSION <= version <= BSP_MAX_VERSION:
		raise BspError(f"{name}: unsupported MOHAA BSP version {version}")
	num_dir = HEADER_LUMPS + (1 if version <= 18 else 0)
	if len(data) < 12 + 8 * num_dir:
		raise BspError(f"{name}: truncated lump directory")
	directory = [struct.unpack_from("<ii", data, 12 + 8 * i) for i in range(num_dir)]

	def lump(n: int) -> bytes:
		ofs, length = directory[_lump_index(version, n)]
		if length == 0:
			return b""
		if ofs < 0 or length < 0 or ofs + length > len(data):
			raise BspError(f"{name}: lump {LUMP_NAMES[n]} lies outside the file")
		return data[ofs:ofs + length]

	bsp = Bsp(
		name=name,
		version=version,
		checksum=checksum,
		file_size=len(data),
		lump_sizes={LUMP_NAMES[i]: directory[_lump_index(version, i)][1] for i in range(HEADER_LUMPS)},
	)

	for rec in _records(lump(LUMP_SHADERS), SZ_SHADER):
		surf, cont, sub = struct.unpack_from("<3i", rec, 64)
		bsp.shaders.append(Shader(_cstr(rec[:64]), surf, cont, sub))

	pl = lump(LUMP_PLANES)
	bsp.planes = list(struct.iter_unpack("<4f", pl[: len(pl) // SZ_PLANE * SZ_PLANE]))
	bsp.num_planes = len(bsp.planes)

	for rec in _records(lump(LUMP_SURFACES), SZ_SURFACE):
		v = struct.unpack_from("<12i3f9f2if", rec)
		bsp.surfaces.append(Surface(
			shader=v[0], surface_type=v[2], num_verts=v[4], num_indexes=v[6],
			patch_width=v[24], patch_height=v[25], subdivisions=v[26], first_vert=v[3], first_index=v[5],
			lightmap=v[7],
		))

	sides = lump(LUMP_BRUSHSIDES)
	sides = sides[: len(sides) // SZ_BRUSHSIDE * SZ_BRUSHSIDE]
	bsp.brushsides = [(p, s) for p, s, _ in struct.iter_unpack("<3i", sides)]
	bsp.brushsides_shader = [s for _, s in bsp.brushsides]

	for rec in _records(lump(LUMP_BRUSHES), SZ_BRUSH):
		bsp.brushes.append(Brush(*struct.unpack("<3i", rec)))

	for rec in _records(lump(LUMP_MODELS), SZ_MODEL):
		v = struct.unpack("<6f4i", rec)
		bsp.models.append(Model(tuple(v[0:3]), tuple(v[3:6]), *v[6:10]))

	bsp.entities = parse_entities(_cstr(lump(LUMP_ENTITIES)))

	leaf_size = SZ_LEAF_V19 if version >= 19 else SZ_LEAF_V17
	bsp.num_leafs = len(lump(LUMP_LEAFS)) // leaf_size
	bsp.num_nodes = len(lump(LUMP_NODES)) // 36
	bsp.lightmaps = lump(LUMP_LIGHTMAPS)
	bsp.num_lightmaps = len(bsp.lightmaps) // LIGHTMAP_BYTES
	dv = lump(LUMP_DRAWVERTS)
	bsp.num_drawverts = len(dv) // SZ_DRAWVERT
	bsp.drawverts = [struct.unpack_from("<3f", dv, i * SZ_DRAWVERT) for i in range(bsp.num_drawverts)]
	bsp.drawvert_st = [struct.unpack_from("<2f", dv, i * SZ_DRAWVERT + 12) for i in range(bsp.num_drawverts)]
	bsp.drawvert_normals = [struct.unpack_from("<3f", dv, i * SZ_DRAWVERT + 28) for i in range(bsp.num_drawverts)]
	bsp.drawvert_lmst = [struct.unpack_from("<2f", dv, i * SZ_DRAWVERT + 20) for i in range(bsp.num_drawverts)]
	bsp.drawvert_color = [struct.unpack_from("<4B", dv, i * SZ_DRAWVERT + 40) for i in range(bsp.num_drawverts)]
	di = lump(LUMP_DRAWINDEXES)
	bsp.drawindexes = list(struct.unpack_from("<%di" % (len(di) // 4), di))

	for rec in _records(lump(LUMP_TERRAIN), SZ_TERRAPATCH):
		x, y = struct.unpack_from("<2b", rec, 36)
		base, shader = struct.unpack_from("<hH", rec, 38)
		raw = struct.unpack_from("<81B", rec, 304)
		tex = struct.unpack_from("<8f", rec, 4)
		lm_scale, lm_s, lm_t = struct.unpack_from("<3B", rec, 1)
		lm_page = struct.unpack_from("<H", rec, 42)[0]
		bsp.terrain.append(TerrainPatch(x, y, base, shader, [base + 2 * h for h in raw], tex,
			lm_page, lm_s, lm_t, max(1, lm_scale)))

	if version >= 19:
		for rec in _records(lump(LUMP_STATICMODELDEF), SZ_STATICMODEL):
			origin = struct.unpack_from("<3f", rec, 128)
			angles = struct.unpack_from("<3f", rec, 140)
			scale = struct.unpack_from("<f", rec, 152)[0]
			bsp.static_models.append(StaticModel(_cstr(rec[:128]), origin, angles, scale))

	return bsp


def lightmap_rgb(bsp: Bsp, page: int, s: float, t: float) -> tuple | None:
	"""Bilinear light (0..255 floats, as stored: one overbright bit down) at lightmap (s, t) of a page."""
	if page < 0 or (page + 1) * LIGHTMAP_BYTES > len(bsp.lightmaps):
		return None
	x = min(max(s * 128.0 - 0.5, 0.0), 127.0)
	y = min(max(t * 128.0 - 0.5, 0.0), 127.0)
	x0, y0 = int(x), int(y)
	x1, y1 = min(x0 + 1, 127), min(y0 + 1, 127)
	fx, fy = x - x0, y - y0
	lm, base = bsp.lightmaps, page * LIGHTMAP_BYTES
	acc = [0.0, 0.0, 0.0]
	for xx, yy, w in ((x0, y0, (1 - fx) * (1 - fy)), (x1, y0, fx * (1 - fy)), (x0, y1, (1 - fx) * fy), (x1, y1, fx * fy)):
		o = base + (yy * 128 + xx) * 3
		acc[0] += lm[o] * w
		acc[1] += lm[o + 1] * w
		acc[2] += lm[o + 2] * w
	return tuple(acc)


def terrain_light(bsp: Bsp, tp: TerrainPatch, i: int, j: int) -> tuple | None:
	"""The light at height sample (i, j) of a terrain patch: lm_scale lightmap texels per 64-unit cell,
	texel (lm_s, lm_t) at sample (0, 0), s along x."""
	if tp.lm_page < 0 or tp.lm_s + 8 * tp.lm_scale > 127 + 1 or tp.lm_t + 8 * tp.lm_scale > 127 + 1:
		return None
	return lightmap_rgb(bsp, tp.lm_page, (tp.lm_s + i * tp.lm_scale + 0.5) / 128.0, (tp.lm_t + j * tp.lm_scale + 0.5) / 128.0)


def load(path) -> Bsp:
	with open(path, "rb") as f:
		return load_bytes(f.read(), str(path))
