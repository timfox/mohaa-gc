#!/usr/bin/env python3
"""Extract a MOHAA BSP's brushes into a GoldSrc Valve-220 .map for SDHLT.

First stage of the map pipeline: brushes only. Curved patches, LOD terrain
(unless --terrain-brushes) and static models are left out (they go to the render bake, and their
collision is decided separately). Output compiles with SDHLT
(sdHLCSG/sdHLBSP[/sdHLVIS/sdHLRAD]) into a BSP30 for dod-gc.

What it does:
  * rebuilds every brush from its planes (no texture coordinates exist on
    Q3-family brush sides, so faces get box-projected Valve-220 axes)
  * scales the world uniformly (default 72/94, MOHAA player -> GoldSrc hull)
  * maps MOHAA shaders to <=15-char WAD names; caulk/nodraw -> NULL,
    clip -> CLIP, sky -> sky, water -> !water, triggers -> AAATRIGGER
  * writes brush entities (doors, script objects) and player starts;
    other point entities are counted, not written
  * optionally writes a placeholder WAD3 with one flat texture per name

Usage:
  bsp19_to_map.py SOURCE -o out.map [--wad out.wad] [--scale S]
  SOURCE = file.bsp, or archive.pk3:maps/name.bsp
"""
from __future__ import annotations

import argparse
import hashlib
import math
import re
import struct
import sys
import zipfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mohaa_bsp19 as b19  # noqa: E402
import mesh_collision  # noqa: E402
from budget_report import terrain_cell_size  # noqa: E402

DEFAULT_SCALE = 72.0 / 94.0
GOLDSRC_HULL_HALF_HEIGHT = 36.0  # standing hull is -36..36 around the origin
EPS = 0.01
BIG = 1.0e5
WORLD_LIMIT = 32000.0  # SDHLT rejects brushes past +/-32768; keep a margin
# sdHLCSG plane matching (brush.cpp FindIntPlane): normals within DIR_EPSILON per
# component and distances within DIST_EPSILON share one plane. Two sides of a
# brush that land on the same plane (or its flip) are a fatal "coplanar plane".
# We test with twice those tolerances because sdHLCSG also snaps to planes
# created by earlier brushes.
CSG_DIR_EPS = 2 * 0.0001
CSG_DIST_EPS = 2 * 0.04
# Brushes thinner than this (GoldSrc units, along any of their own side normals)
# are inflated to it: SDHLT turns 1-unit slivers into +/-80000 "outside world"
# brushes, and dropping them instead opens leaks (thin glass and fences seal rooms).
MIN_THICKNESS = 1.1
DROP_THICKNESS = 0.05  # flatter than this is a zero-volume brush; drop it

# ---------------------------------------------------------------- geometry


def _dot(a, b):
	return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _sub(a, b):
	return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a, b):
	return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _norm(v):
	l = math.sqrt(_dot(v, v))
	return (v[0] / l, v[1] / l, v[2] / l) if l > 1e-12 else (0.0, 0.0, 0.0)


def base_winding(n, d):
	"""A huge quad on plane (n, d), wound so cross(p0-p1, p2-p1) points along n."""
	ax = max(range(3), key=lambda i: abs(n[i]))
	up = (0.0, 0.0, 1.0) if ax != 2 else (1.0, 0.0, 0.0)
	v = _sub(up, tuple(n[i] * _dot(up, n) for i in range(3)))
	v = _norm(v)
	r = _cross(v, n)
	org = tuple(n[i] * d for i in range(3))
	v = tuple(c * BIG for c in v)
	r = tuple(c * BIG for c in r)
	w = [
		tuple(org[i] - r[i] + v[i] for i in range(3)),
		tuple(org[i] + r[i] + v[i] for i in range(3)),
		tuple(org[i] + r[i] - v[i] for i in range(3)),
		tuple(org[i] - r[i] - v[i] for i in range(3)),
	]
	return w if _dot(_cross(_sub(w[0], w[1]), _sub(w[2], w[1])), n) > 0 else w[::-1]


def clip_winding(w, n, d):
	"""Keep the part of w behind plane (n, d) (dot(p, n) <= d)."""
	if not w:
		return w
	dists = [_dot(p, n) - d for p in w]
	if all(x <= EPS for x in dists):
		return w
	if all(x >= -EPS for x in dists):
		return []
	out = []
	for i, p in enumerate(w):
		q = w[(i + 1) % len(w)]
		dp, dq = dists[i], dists[(i + 1) % len(w)]
		if dp <= EPS:
			out.append(p)
		if (dp < -EPS and dq > EPS) or (dp > EPS and dq < -EPS):
			t = dp / (dp - dq)
			out.append(tuple(p[k] + t * (q[k] - p[k]) for k in range(3)))
	return out


def winding_area(w):
	if len(w) < 3:
		return 0.0
	total = (0.0, 0.0, 0.0)
	for i in range(1, len(w) - 1):
		c = _cross(_sub(w[i], w[0]), _sub(w[i + 1], w[0]))
		total = (total[0] + c[0], total[1] + c[1], total[2] + c[2])
	return 0.5 * math.sqrt(_dot(total, total))


def brush_faces(planes):
	"""planes: list of (normal, dist, payload). Returns [(normal, dist, winding, payload)]
	for every side that keeps a real face; duplicate planes are dropped."""
	seen = set()
	uniq = []
	for n, d, pay in planes:
		key = (round(n[0], 4), round(n[1], 4), round(n[2], 4), round(d, 2))
		if key in seen:
			continue
		seen.add(key)
		uniq.append((n, d, pay))
	faces = []
	for i, (n, d, pay) in enumerate(uniq):
		w = base_winding(n, d)
		for j, (n2, d2, _) in enumerate(uniq):
			if i != j:
				w = clip_winding(w, n2, d2)
				if not w:
					break
		if len(w) >= 3 and winding_area(w) > 0.1:
			faces.append((n, d, w, pay))
	return faces


def three_points(n, w):
	"""Three well-spread winding points ordered for Valve-220 (cross(p0-p1, p2-p1) along n)."""
	best = None
	m = len(w)
	for a in range(m):
		for b in range(a + 1, m):
			for c in range(b + 1, m):
				area = _dot(_cross(_sub(w[a], w[b]), _sub(w[c], w[b])), n)
				if best is None or abs(area) > abs(best[0]):
					best = (area, w[a], w[b], w[c])
		if m > 12 and best and abs(best[0]) > 1.0:
			break
	area, p0, p1, p2 = best
	return (p0, p1, p2) if area > 0 else (p2, p1, p0)


def texture_axes(n):
	"""Quake-style box projection: pick the axis plane closest to the face."""
	ax = max(range(3), key=lambda i: abs(n[i]))
	if ax == 2:
		return (1.0, 0.0, 0.0), (0.0, -1.0, 0.0)
	if ax == 0:
		return (0.0, 1.0, 0.0), (0.0, 0.0, -1.0)
	return (1.0, 0.0, 0.0), (0.0, 0.0, -1.0)


def _f(v):
	s = f"{v:.3f}".rstrip("0").rstrip(".")
	return "0" if s in ("-0", "") else s


# ---------------------------------------------------------------- textures


class TextureNamer:
	"""MOHAA shader path -> unique <=15-char WAD-safe name."""

	SPECIAL = {"NULL", "CLIP", "sky", "!water", "AAATRIGGER", "ORIGIN"}

	def __init__(self):
		self.by_shader = {}
		self.used = set()
		self.special_used = set()  # sky / !water / AAATRIGGER need WAD entries too

	def name(self, shader: str) -> str:
		if shader in self.by_shader:
			return self.by_shader[shader]
		base = shader.replace("\\", "/").rsplit("/", 1)[-1].lower()
		base = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in base) or "tex"
		cand = base[:15]
		if cand in self.used or cand.upper() in {s.upper() for s in self.SPECIAL}:
			h = hashlib.md5(shader.encode()).hexdigest()[:4]
			cand = base[:10] + "_" + h
		self.used.add(cand)
		self.by_shader[shader] = cand
		return cand


def side_texture(sh: b19.Shader, namer: TextureNamer, brush_class: str) -> str:
	tex = _side_texture(sh, namer, brush_class)
	if tex in ("sky", "!water", "AAATRIGGER"):  # ORIGIN is added where origin brushes are written
		namer.special_used.add(tex)
	return tex


def _side_texture(sh: b19.Shader, namer: TextureNamer, brush_class: str) -> str:
	low = sh.name.lower()
	if brush_class == "clip":
		return "CLIP"
	if brush_class == "trigger":
		return "AAATRIGGER"
	if brush_class == "water":
		return "!water"
	if sh.surface_flags & b19.SURF_SKY or "/sky" in low:
		return "sky"
	if sh.surface_flags & b19.SURF_NODRAW or "caulk" in low or "nodraw" in low:
		return "NULL"
	return namer.name(sh.name)


def classify(contents: int) -> str:
	if contents & b19.CONTENTS_ORIGIN:
		return "origin"
	if contents & (b19.CONTENTS_AREAPORTAL | b19.CONTENTS_FOG) and not contents & b19.CONTENTS_SOLID:
		return "skip"
	if contents & b19.CONTENTS_TRIGGER:
		return "trigger"
	if contents & b19.CONTENTS_FLUID:
		return "water"
	if contents & (b19.CONTENTS_SOLID | b19.CONTENTS_FENCE):
		return "detail" if contents & b19.CONTENTS_DETAIL else "solid"
	if contents & b19.CONTENTS_ANYCLIP:
		return "clip"
	return "nonsolid"


# ---------------------------------------------------------------- entities

PLAYER_STARTS = {
	"info_player_start": ["info_player_start", "info_player_allies"],
	"info_player_allied": ["info_player_allies"],
	"info_player_axis": ["info_player_axis"],
	"info_player_deathmatch": ["info_player_allies", "info_player_axis"],
	"info_player_intermission": ["info_intermission"],
}

BRUSH_CLASS_MAP = {
	"func_door": "func_door",
	"func_rotatingdoor": "func_door_rotating",
	"func_door_rotating": "func_door_rotating",
	"func_explodingwall": "func_breakable",
	"func_window": "func_breakable",
}
ROTATING = {"func_door_rotating"}
# MOHAA triggers. GoldSrc's trigger_multiple fires on touch like MOHAA's trigger_multiple; a use-trigger
# (trigger_use) has no GoldSrc twin and also fires on touch here. The script hears every firing ("waittill
# trigger"); MOHAA's "setthread" (a level-script label to run) rides in netname for dod-gc to start.
TRIGGER_CLASS_MAP = {
	"trigger_once": "trigger_once",
	"trigger_hurt": "trigger_hurt",
	"trigger_push": "trigger_push",
	"trigger_pushany": "trigger_push",
}
TRIGGER_KEYS = ("targetname", "target", "wait", "delay", "dmg", "speed", "angle", "angles")
# MOHAA brush entities that are volumes, not walls: no player/bullet collision.
NONSOLID_BRUSH = {"func_rain": "func_illusionary"}


def parse_vec(s, default=(0.0, 0.0, 0.0)):
	try:
		v = [float(x) for x in s.split()]
		return tuple(v[:3]) if len(v) >= 3 else default
	except (ValueError, AttributeError):
		return default


# ---------------------------------------------------------------- convert


def csg_plane(p0, p1, p2):
	"""The plane sdHLCSG derives from three written points (PlaneFromPoints)."""
	n = _norm(_cross(_sub(p0, p1), _sub(p2, p1)))
	return n, _dot(n, p0)


def _same_plane(a, b):
	"""a, b: (normal, dist, point). sdHLCSG matches normals per component and tests
	the new side's first point against the old plane, so check both directions."""
	(n1, d1, p1), (n2, d2, p2) = a, b
	if not all(abs(n1[k] - n2[k]) < CSG_DIR_EPS for k in range(3)):
		return False
	return abs(_dot(p1, n2) - d2) < CSG_DIST_EPS or abs(_dot(p2, n1) - d1) < CSG_DIST_EPS


def csg_safe_sides(sides, stats):
	"""sides: [(points, rest_of_line)]. Drops later sides that sdHLCSG would read as the
	same plane as an earlier one; returns None when two sides are flips of one plane
	(a brush thinner than DIST_EPSILON) or a side has no normal."""
	kept, planes = [], []
	for pts, rest in sides:
		rp = tuple(tuple(float(_f(c)) for c in p) for p in pts)
		n, d = csg_plane(*rp)
		if n == (0.0, 0.0, 0.0):
			stats["brushes_degenerate"] += 1
			return None
		flip = ((-n[0], -n[1], -n[2]), -d, rp[0])
		if any(_same_plane(flip, q) for q in planes):
			stats["brushes_too_thin"] += 1
			return None
		if any(_same_plane((n, d, rp[0]), q) for q in planes):
			stats["sides_coplanar_dropped"] += 1
			continue
		planes.append((n, d, rp[0]))
		kept.append((pts, rest))
	if len(kept) < 4:
		stats["brushes_degenerate"] += 1
		return None
	return kept


def brush_thickness(faces):
	"""Smallest extent of a convex brush measured along its own side normals."""
	verts = [p for _, _, w, _ in faces for p in w]
	return min(d - min(_dot(p, n) for p in verts) for n, d, _, _ in faces)


def brush_text(bsp, brush, scale, offset, namer, stats, cls, entity=False, geom=None, flags=None):
	planes = []
	for si in range(brush.first_side, brush.first_side + brush.num_sides):
		if si >= len(bsp.brushsides):
			break
		pi, shi = bsp.brushsides[si]
		if not 0 <= pi < len(bsp.planes):
			continue
		nx, ny, nz, dist = bsp.planes[pi]
		n = (nx, ny, nz)
		d = (dist + _dot(n, offset)) * scale
		sh = bsp.shaders[shi] if 0 <= shi < len(bsp.shaders) else b19.Shader("", 0, 0, 0)
		planes.append((n, d, sh))
	faces = brush_faces(planes)
	if len(faces) < 4:
		stats["brushes_degenerate"] += 1
		return None
	if any(abs(c) > WORLD_LIMIT for _, _, w, _ in faces for p in w for c in p):
		# Unbounded or runaway brush (MOHAA keeps a few); SDHLT would abort on it.
		stats["brushes_outside_world"] += 1
		return None
	t = brush_thickness(faces)
	if t < DROP_THICKNESS:
		stats["brushes_too_thin"] += 1
		return None
	if t < MIN_THICKNESS:
		# Push every side out by the same amount: the brush stays convex and keeps its shape.
		# Grow all source planes, not just the ones with faces: a sliver's end caps can be
		# under the area cutoff, and growing only the long sides leaves an open prism.
		grow = (MIN_THICKNESS - t) / 2 + 0.05
		faces = brush_faces([(n, d + grow, sh) for n, d, sh in planes])
		if len(faces) < 4 or brush_thickness(faces) < MIN_THICKNESS:
			stats["brushes_too_thin"] += 1
			return None
		if any(abs(c) > WORLD_LIMIT for _, _, w, _ in faces for p in w for c in p):
			stats["brushes_outside_world"] += 1
			return None
		stats["brushes_thickened"] += 1
		if flags is not None:
			flags["thickened"] = True
	sides = []
	for n, d, w, sh in faces:
		tex = side_texture(sh, namer, cls)
		if entity and tex == "sky":
			tex = "NULL"  # SDHLT: "SKY brushes not allowed in entity"
		u, v = texture_axes(n)
		rest = f"{tex} [ {_f(u[0])} {_f(u[1])} {_f(u[2])} 0 ] [ {_f(v[0])} {_f(v[1])} {_f(v[2])} 0 ] 0 1 1"
		sides.append((three_points(n, w), rest))
	sides = csg_safe_sides(sides, stats)
	if sides is None:
		return None
	if geom is not None:
		geom.extend(faces)
	lines = ["{"]
	for pts, rest in sides:
		lines.append(" ".join("( %s %s %s )" % tuple(_f(c) for c in p) for p in pts) + " " + rest)
		stats["faces"] += 1
	lines.append("}")
	return "\n".join(lines)


def origin_brush(o, half=8.0):
	x, y, z = o
	lo = (x - half, y - half, z - half)
	hi = (x + half, y + half, z + half)
	faces = []
	for ax in range(3):
		for sign in (1, -1):
			n = [0.0, 0.0, 0.0]
			n[ax] = float(sign)
			d = hi[ax] if sign > 0 else -lo[ax]
			faces.append((tuple(n), d, None))
	out = ["{"]
	for n, d, w, _ in brush_faces(faces):
		p0, p1, p2 = three_points(n, w)
		u, v = texture_axes(n)
		pts = " ".join("( %s %s %s )" % tuple(_f(c) for c in p) for p in (p0, p1, p2))
		out.append(f"{pts} ORIGIN [ {_f(u[0])} {_f(u[1])} {_f(u[2])} 0 ] [ {_f(v[0])} {_f(v[1])} {_f(v[2])} 0 ] 0 1 1")
	out.append("}")
	return "\n".join(out)


def model_brushes(bsp, model_index, scale, offset, namer, stats):
	entity = model_index != 0
	m = bsp.models[model_index]
	out = []
	for bi in range(m.first_brush, m.first_brush + m.num_brushes):
		br = bsp.brushes[bi]
		sh = bsp.shaders[br.shader] if 0 <= br.shader < len(bsp.shaders) else b19.Shader("", 0, 0, 0)
		cls = classify(sh.content_flags)
		stats["brush_class_" + cls] += 1
		if cls in ("origin", "skip", "nonsolid"):
			continue
		faces = []
		flags = {}
		txt = brush_text(bsp, br, scale, offset, namer, stats, cls, entity, faces, flags)
		if txt:
			if cls == "detail" and flags.get("thickened"):
				cls = "thin_detail"
			out.append((cls, txt, faces))
	return out


THIN_WALL_CELL = 1024.0  # group thin detail into func_walls per cell so bbox culling still works


def thin_wall_blocks(thin, stats, cell=THIN_WALL_CELL):
	"""thin: [(txt, faces)]. One func_wall per THIN_WALL_CELL^3 cell (by brush centre).
	As separate brush models they don't split the world's hull-0 tree (each kept sliver
	cost 6-13 world leaves in func_detail) but still block players and traces."""
	cells = {}
	for txt, faces in thin:
		texs = _SIDE_TEXNAME_RE.findall(txt)
		if texs and all(t == "NULL" for t in texs):
			# Nothing to draw: as a wall it only adds hull-0 nodes/leaves (BSP size).
			# Players still collide with its CLIP copy / voxel boxes in the world.
			stats["nodraw_wall_brushes_dropped"] += 1
			continue
		verts = [p for _, _, w, _ in faces for p in w]
		c = tuple(int(math.floor((min(v[i] for v in verts) + max(v[i] for v in verts)) * 0.5 / cell))
		          for i in range(3))
		cells.setdefault(c, []).append(txt)
	stats["thin_detail_walls"] += len(cells)
	# zhlt_noclip: no hull 1-3 trees per wall (each sliver cost ~40 clipnodes as its own
	# model). Players collide with a CLIP copy in the world instead, see clip_copy().
	return [kv_block({"classname": "func_wall", "mohaa_classname": "thin_detail", "zhlt_noclip": "1"}, cells[c])
	        for c in sorted(cells)]


_SIDE_TEXNAME_RE = re.compile(r"^\(.*?\) \(.*?\) \(.*?\) (\S+) \[", re.M)
_SIDE_TEXNAME_SUB = re.compile(r"^(\(.*?\) \(.*?\) \(.*?\) )\S+ \[", re.M)
_SIDE_TEX_RE = re.compile(r"^(\(.*?\) \(.*?\) \(.*?\) )\S+ \[", re.M)


def clip_copy(txt):
	"""The same brush with every side textured CLIP (player hulls only, no hull-0 leaves)."""
	return _SIDE_TEX_RE.sub(lambda m: m.group(1) + "CLIP [", txt)


def _face_line(n, w, tex):
	p0, p1, p2 = three_points(n, w)
	u, v = texture_axes(n)
	pts = " ".join("( %s %s %s )" % tuple(_f(c) for c in p) for p in (p0, p1, p2))
	return f"{pts} {tex} [ {_f(u[0])} {_f(u[1])} {_f(u[2])} 0 ] [ {_f(v[0])} {_f(v[1])} {_f(v[2])} 0 ] 0 1 1"


def wedge_planes(a, b, c, depth):
	"""Planes of the convex wedge under triangle abc: sloped top, flat bottom, then three
	vertical sides. None for a triangle seen edge-on from above."""
	n = _norm(_cross(_sub(b, a), _sub(c, a)))
	if n[2] < 0:
		n = (-n[0], -n[1], -n[2])
	if n[2] < 1e-3:
		return None
	planes = [(n, _dot(n, a))]
	zb = min(a[2], b[2], c[2]) - depth
	planes.append(((0.0, 0.0, -1.0), -zb))
	for p, q, r in ((a, b, c), (b, c, a), (c, a, b)):
		e = _sub(q, p)
		sn = _norm((e[1], -e[0], 0.0))
		if _dot(sn, _sub(r, p)) > 0:
			sn = (-sn[0], -sn[1], 0.0)
		planes.append((sn, _dot(sn, p)))
	return planes


def wedge_brush(a, b, c, depth, top_tex, side_tex):
	"""Convex brush under triangle abc: sloped top, three vertical sides, flat bottom."""
	wp = wedge_planes(a, b, c, depth)
	if wp is None:
		return None
	planes = [(n, d, top_tex if i == 0 else side_tex) for i, (n, d) in enumerate(wp)]
	faces = brush_faces(planes)
	if len(faces) < 5:
		return None
	return "\n".join(["{"] + [_face_line(fn, w, t) for fn, _, w, t in faces] + ["}"])


def _terrain_triangles(tp, scale, tol):
	"""Triangles of one LOD terrain patch, merged into cells as coarse as tol (GoldSrc units)."""
	n = b19.TERRAIN_SAMPLES
	tol_mohaa = tol / scale if scale > 0 else tol
	cell = terrain_cell_size(tp.heights, tol_mohaa)
	step = cell // b19.TERRAIN_CELL
	x0, y0 = tp.origin
	cells = (n - 1) // step

	def pt(i, j):
		return ((x0 + i * b19.TERRAIN_CELL) * scale, (y0 + j * b19.TERRAIN_CELL) * scale, tp.heights[j * n + i] * scale)

	tris = []
	for cj in range(cells):
		for ci in range(cells):
			i0, j0, i1, j1 = ci * step, cj * step, (ci + 1) * step, (cj + 1) * step
			p00, p10, p01, p11 = pt(i0, j0), pt(i1, j0), pt(i0, j1), pt(i1, j1)
			# same diagonal as budget_report.terrain_cell_size
			tris.extend(((p00, p10, p01), (p11, p01, p10)))
	return cell, tris


def add_mesh_terrain(bsp, scale, mesh, stats):
	"""LOD terrain as heightfields in the engine collision mesh (.mcol): exact, and no
	clipnodes. MOHAA terrain is not a brush, so without this it has no collision."""
	for tp in bsp.terrain:
		x0, y0 = tp.origin
		h = [(z - tp.base_z) // 2 for z in tp.heights]
		mesh.add_terrain((x0 * scale, y0 * scale, tp.base_z * scale), b19.TERRAIN_CELL * scale, 2 * scale, h)
		stats["mesh_terrain_patches"] += 1


def _bezier(p0, p1, p2, t):
	u = 1.0 - t
	return tuple(u * u * p0[k] + 2 * u * t * p1[k] + t * t * p2[k] for k in range(3))


def _quad_steps(p0, p1, p2, tol):
	"""Segments that keep a quadratic curve within tol of its polyline (error ~ dev / n^2)."""
	mid = tuple((p0[k] + p2[k]) * 0.5 for k in range(3))
	dev = math.sqrt(sum((p1[k] - mid[k]) ** 2 for k in range(3))) * 0.5
	return max(1, min(16, math.ceil(math.sqrt(dev / tol)) if tol > 0 else 16))


def patch_triangles(ctrl, w, h, tol):
	"""Tessellate a Quake 3 biquadratic patch (w x h control points, row-major, both odd)
	into triangles within about tol of the surface. Strips share their step counts so
	neighbouring 3x3 pieces meet without cracks."""
	if w < 3 or h < 3 or not (w & 1) or not (h & 1) or len(ctrl) < w * h:
		return []
	cp = lambda i, j: ctrl[j * w + i]  # noqa: E731
	su = [max(_quad_steps(cp(2 * i, j), cp(2 * i + 1, j), cp(2 * i + 2, j), tol) for j in range(h))
	      for i in range((w - 1) // 2)]
	sv = [max(_quad_steps(cp(i, 2 * j), cp(i, 2 * j + 1), cp(i, 2 * j + 2), tol) for i in range(w))
	      for j in range((h - 1) // 2)]
	# parameter samples along each axis: (strip, t)
	us = [(i, k / n) for i, n in enumerate(su) for k in range(n)] + [(len(su) - 1, 1.0)]
	vs = [(j, k / n) for j, n in enumerate(sv) for k in range(n)] + [(len(sv) - 1, 1.0)]

	def point(ui, vj):
		i, tu = ui
		j, tv = vj
		cols = [_bezier(cp(2 * i, 2 * j + r), cp(2 * i + 1, 2 * j + r), cp(2 * i + 2, 2 * j + r), tu) for r in range(3)]
		return _bezier(cols[0], cols[1], cols[2], tv)

	grid = [[point(u, v) for u in us] for v in vs]
	tris = []
	for y in range(len(vs) - 1):
		for x in range(len(us) - 1):
			p00, p10, p01, p11 = grid[y][x], grid[y][x + 1], grid[y + 1][x], grid[y + 1][x + 1]
			tris.extend(((p00, p10, p11), (p00, p11, p01)))
	return tris


def mesh_patches(bsp, scale, tol, mesh, stats):
	"""Solid curved patches of the world as triangles in the engine collision mesh (each
	swept as a thin prism, the way Quake 3 collides with patch facets). Brush-model patches are left to their entities."""
	if not bsp.models or not bsp.drawverts:
		return
	m = bsp.models[0]
	for si in range(m.first_surface, m.first_surface + m.num_surfaces):
		if si >= len(bsp.surfaces):
			break
		sf = bsp.surfaces[si]
		if sf.surface_type != b19.MST_PATCH:
			continue
		sh = bsp.shaders[sf.shader] if 0 <= sf.shader < len(bsp.shaders) else None
		if sh is None or not sh.content_flags & (b19.CONTENTS_SOLID | b19.CONTENTS_PLAYERCLIP) \
				or sh.surface_flags & (b19.SURF_NONSOLID | b19.SURF_SKY):
			stats["mesh_patches_nonsolid"] += 1
			continue
		ctrl = [tuple(c * scale for c in v) for v in bsp.drawverts[sf.first_vert:sf.first_vert + sf.num_verts]]
		tris = patch_triangles(ctrl, sf.patch_width, sf.patch_height, tol)
		if not tris:
			stats["mesh_patches_bad"] += 1
			continue
		for a, b, c in tris:
			if mesh.add_triangle(a, b, c):
				stats["mesh_patch_triangles"] += 1
		stats["mesh_patches"] += 1


def terrain_brushes(bsp, scale, tol, tex, stats, depth=16.0):
	"""Wedge brushes for every LOD terrain patch, as coarse as tol (GoldSrc units) allows."""
	out = []
	for tp in bsp.terrain:
		cell, tris = _terrain_triangles(tp, scale, tol)
		for tri in tris:
			txt = wedge_brush(*tri, depth, tex, tex if tex == "CLIP" else "NULL")
			if txt:
				out.append(txt)
				stats["terrain_brushes_written"] += 1
			else:
				stats["terrain_brushes_degenerate"] += 1
		stats["terrain_patches_cell_" + str(cell)] += 1
	return out


def _box_brush(lo, hi, tex):
	return "\n".join(["{"] + [_face_line(n, w, tex) for n, _, w, _ in brush_faces(
		[((1.0, 0.0, 0.0), hi[0], None), ((-1.0, 0.0, 0.0), -lo[0], None),
		 ((0.0, 1.0, 0.0), hi[1], None), ((0.0, -1.0, 0.0), -lo[1], None),
		 ((0.0, 0.0, 1.0), hi[2], None), ((0.0, 0.0, -1.0), -lo[2], None)])] + ["}"])


def terrain_seal_brushes(bsp, scale, stats, gap=8.0, base=16.0):
	"""One NULL column under each terrain patch, from a common floor up to just below the
	patch's lowest point. MOHAA terrain is not a brush, so without these the map leaks
	through the ground; the columns abut, so neighbouring patches at different heights
	leave no gap. The walkable surface itself comes from mesh collision (or
	--terrain-brushes)."""
	if not bsp.terrain:
		return []
	floor = (min(min(tp.heights) for tp in bsp.terrain) - gap - base) * scale
	out = []
	for tp in bsp.terrain:
		x0, y0 = tp.origin
		top = (min(tp.heights) - gap) * scale
		lo = (x0 * scale, y0 * scale, floor)
		hi = ((x0 + b19.TERRAIN_PATCH_SIZE) * scale, (y0 + b19.TERRAIN_PATCH_SIZE) * scale, top)
		out.append(_box_brush(lo, hi, "NULL"))
		stats["terrain_seal_brushes"] += 1
	return out


def seal_box_brushes(bsp, scale, stats, margin=256.0, wall=16.0):
	"""Six NULL slabs enclosing the whole map. A last resort for maps that leak through
	gaps we can't find: the space between the map and the box counts as inside, so
	outward faces are kept and VIS has more to chew on, but hull 0 seals."""
	m = bsp.models[0]
	lo = [max(-WORLD_LIMIT + wall, m.mins[i] * scale - margin) for i in range(3)]
	hi = [min(WORLD_LIMIT - wall, m.maxs[i] * scale + margin) for i in range(3)]
	out = []
	for ax in range(3):
		for side in (0, 1):
			blo, bhi = [c - wall for c in lo], [c + wall for c in hi]
			if side == 0:
				bhi[ax] = lo[ax]
			else:
				blo[ax] = hi[ax]
			out.append(_box_brush(blo, bhi, "NULL"))
	stats["seal_box_brushes"] += len(out)
	return out


def is_axial_brush(faces):
	return all(sum(1 for c in n if abs(c) > 1e-6) == 1 for n, _, _, _ in faces)


def brush_volume(faces):
	verts = [p for _, _, w, _ in faces for p in w]
	c = tuple(sum(p[i] for p in verts) / len(verts) for i in range(3))
	return sum(winding_area(w) * (d - _dot(n, c)) for n, d, w, _ in faces) / 3.0


def brush_aabb(faces):
	verts = [p for _, _, w, _ in faces for p in w]
	return (tuple(min(p[i] for p in verts) for i in range(3)),
	        tuple(max(p[i] for p in verts) for i in range(3)))


class ReachIndex:
	"""Where players can be: MOHAA path nodes and player starts. Angled detail far from
	all of them never touches a player hull, so it needs no player collision (bullets
	still hit its hull-0 copy). up/down bound how far above/below a point counts."""

	def __init__(self, points, radius, up=256.0, down=512.0):
		self.r, self.up, self.down = radius, up, down
		self.cells = {}
		for p in points:
			self.cells.setdefault((int(math.floor(p[0] / radius)), int(math.floor(p[1] / radius))), []).append(p)

	def reaches(self, lo, hi):
		r = self.r
		for cx in range(int(math.floor((lo[0] - r) / r)), int(math.floor((hi[0] + r) / r)) + 1):
			for cy in range(int(math.floor((lo[1] - r) / r)), int(math.floor((hi[1] + r) / r)) + 1):
				for p in self.cells.get((cx, cy), ()):
					dx = max(lo[0] - p[0], 0.0, p[0] - hi[0])
					dy = max(lo[1] - p[1], 0.0, p[1] - hi[1])
					if dx * dx + dy * dy <= r * r and p[2] + self.up >= lo[2] and p[2] - self.down <= hi[2]:
						return True
		return False


PATH_NODES = ("info_pathnode", "info_grav_pathnode")
ACTOR_KEYS = ("targetname", "target", "angle", "angles", "model", "health", "spawnflags")


def is_actor(cn, model):
	"""MOHAA soldiers: classname "actor", or a human/ tiki as the classname or model."""
	cn, model = cn.lower(), model.lower()
	return cn == "actor" or cn.startswith("human/") or "human/" in model


def path_nodes(bsp, scale):
	"""Path nodes for the <map>.nodes sidecar: one line per node, feet origin scaled.
	They stay out of the .map so they cost no edicts; dod-gc links them at load."""
	lines = ["# mohaa path nodes: x y z grav spawnflags targetname"]
	for e in bsp.entities[1:]:
		cn = e.get("classname", "").lower()
		if cn not in PATH_NODES:
			continue
		x, y, z = (c * scale for c in parse_vec(e.get("origin", "")))
		try:
			flags = int(e.get("spawnflags", "0"))
		except ValueError:
			flags = 0
		name = e.get("targetname", "").strip().lstrip("$") or "-"
		lines.append(f"{_f(x)} {_f(y)} {_f(z)} {int(cn == 'info_grav_pathnode')} {flags} {name.split()[0]}")
	return "\n".join(lines) + "\n", len(lines) - 1


def reach_points(bsp, scale):
	pts = []
	for e in bsp.entities[1:]:
		cn = e.get("classname", "").lower()
		if cn in PATH_NODES or cn in PLAYER_STARTS:
			pts.append(tuple(c * scale for c in parse_vec(e.get("origin", ""))))
	return pts


def angled_collision(faces, voxels, grid, stats, aabb_fill=0.0, reach=None, exact_size=0.0, txt=None, mesh=None):
	"""Player collision for an angled brush: nothing if no player can reach it, its own
	axial bounding box if that box is nearly as tight as the brush (or the brush is
	smaller than a cell), else grid voxels. Returns a CLIP brush or None."""
	lo, hi = brush_aabb(faces)
	if reach is not None and not reach.reaches(lo, hi):
		stats["collision_unreachable"] += 1
		return None
	if mesh is not None:
		# Exact: the engine sweeps the player box against this brush (.mcol sidecar).
		mesh.add_brush([(n, d) for n, d, _, _ in faces], [p for _, _, w, _ in faces for p in w])
		stats["collision_mesh"] += 1
		return None
	if exact_size > 0 and txt is not None and max(hi[i] - lo[i] for i in range(3)) >= exact_size:
		# A big ramp or roof as voxels is a staircase of hundreds of steps; as one exact
		# CLIP brush it is a handful of planes. Voxels only pay off for the many small ones.
		stats["collision_exact"] += 1
		return clip_copy(txt)
	if aabb_fill > 0:
		g = _grid3(grid)
		ext = [hi[i] - lo[i] for i in range(3)]
		box_vol = ext[0] * ext[1] * ext[2]
		if all(ext[i] <= g[i] for i in range(3)) or (box_vol > 0 and brush_volume(faces) / box_vol >= aabb_fill):
			stats["collision_aabb"] += 1
			return _box_brush(tuple(math.floor(c) for c in lo), tuple(math.ceil(c) for c in hi), "CLIP")
	voxelize_brush(faces, voxels, grid)
	return None


def _grid3(grid):
	"""A grid is one cell size or (xy, z) / (x, y, z)."""
	if isinstance(grid, (int, float)):
		return (float(grid),) * 3
	g = tuple(float(v) for v in grid)
	return (g[0], g[0], g[1]) if len(g) == 2 else g


def voxelize_brush(faces, voxels, grid):
	"""Add every grid cell the convex brush may overlap (plane test against the cell's
	nearest corner, so thin beams are never missed; it can over-include a little)."""
	g = _grid3(grid)
	verts = [p for _, _, w, _ in faces for p in w]
	lo = [math.floor(min(p[i] for p in verts) / g[i]) for i in range(3)]
	hi = [math.ceil(max(p[i] for p in verts) / g[i]) for i in range(3)]
	planes = [(n, d) for n, d, _, _ in faces]
	for x in range(lo[0], hi[0]):
		for y in range(lo[1], hi[1]):
			for z in range(lo[2], hi[2]):
				c0 = (x * g[0], y * g[1], z * g[2])
				for n, d in planes:
					# the cell corner furthest behind the plane
					m = sum((c0[k] if n[k] > 0 else c0[k] + g[k]) * n[k] for k in range(3))
					if m >= d - 1e-6:
						break
				else:
					voxels.add((x, y, z))


def voxel_boxes(voxels, grid, stats):
	"""Greedy-merge occupied cells into axial CLIP boxes (x runs, then y, then z).

	Player-hull expansion of thousands of arbitrarily angled brushes is what blows
	the plane and clipnode limits on m6l1a/b and m6l2b. Axial boxes on a shared
	grid need no bevels and reuse the same few planes, and a slope becomes steps of
	one grid cell, which players climb as long as the grid is under the 18-unit
	step height. Only the z cell size matters for stepping, so a coarser xy cell
	(--collision-grid-z) cuts the box count without making slopes unclimbable."""
	g = _grid3(grid)
	left = set(voxels)
	out = []
	for cell in sorted(voxels, key=lambda c: (c[2], c[1], c[0])):
		if cell not in left:
			continue
		x0, y0, z0 = cell
		x1 = x0
		while (x1 + 1, y0, z0) in left:
			x1 += 1
		y1 = y0
		while all((x, y1 + 1, z0) in left for x in range(x0, x1 + 1)):
			y1 += 1
		z1 = z0
		while all((x, y, z1 + 1) in left for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)):
			z1 += 1
		for x in range(x0, x1 + 1):
			for y in range(y0, y1 + 1):
				for z in range(z0, z1 + 1):
					left.discard((x, y, z))
		out.append(_box_brush((x0 * g[0], y0 * g[1], z0 * g[2]),
		                      ((x1 + 1) * g[0], (y1 + 1) * g[1], (z1 + 1) * g[2]), "CLIP"))
	stats["collision_voxels"] += len(voxels)
	stats["collision_boxes"] += len(out)
	return out


def kv_block(keys, brushes=()):
	lines = ["{"]
	for k, v in keys.items():
		lines.append(f'"{k}" "{v}"')
	lines.extend(brushes)
	lines.append("}")
	return "\n".join(lines)


def convert(bsp: b19.Bsp, scale: float = DEFAULT_SCALE, wad_name: str | None = None,
            terrain: bool = False, terrain_tol: float = 8.0, terrain_tex: str = "CLIP",
            terrain_seal: bool = True, detail_world: bool = False, seal_box: bool = False,
            simplify_collision: bool = False, collision_grid: float = 16.0, thin_walls: bool = True,
            detail_walls: bool = False, wall_cell: float = THIN_WALL_CELL,
            collision_aabb: float = 0.0, collision_reach: float = 0.0, collision_exact: float = 0.0,
            mesh=None, mesh_terrain: bool = False, mesh_patch_tol: float = 0.0, mesh_angled: bool = True,
            merge_static_models: bool = False, script_words: set | None = None):
	"""mesh: a mesh_collision.Collision that angled detail (mesh_angled, under
	simplify_collision), terrain heightfields (mesh_terrain) and solid world patches
	(mesh_patch_tol > 0) are added to.

	merge_static_models also merges triggers with the same keys into one entity each.
	script_words: every word of the level's scripts (script_names()). A targetname that no
	script word and no entity target names is dropped, so that entity can merge too; None
	keeps every targetname."""
	angled_mesh = mesh if mesh_angled else None
	namer = TextureNamer()
	stats = Counter()
	world = bsp.entities[0] if bsp.entities else {"classname": "worldspawn"}
	ws_keys = {"classname": "worldspawn", "mapversion": "220"}
	if wad_name:
		ws_keys["wad"] = wad_name
	if "message" in world:
		ws_keys["message"] = world["message"]
	ws_keys["mohaa_source"] = bsp.name.replace('"', "'")

	world_brushes = []
	detail = []
	noclip_detail = []
	voxels = set()
	thin = []
	reach = None
	if simplify_collision and collision_reach > 0:
		pts = reach_points(bsp, scale)
		if len(pts) >= 8:  # too few points (some MP maps): keep collision everywhere
			reach = ReachIndex(pts, collision_reach)
		stats["collision_reach_points"] += len(pts)
	for cls, txt, faces in model_brushes(bsp, 0, scale, (0.0, 0.0, 0.0), namer, stats):
		if cls == "thin_detail":
			if " sky [" in txt or not thin_walls:
				cls = "detail"  # sky must go to the world below; otherwise keep the old path
			else:
				thin.append((txt, faces))
				stats["thin_detail_to_wall"] += 1
				if simplify_collision and not is_axial_brush(faces):
					box = angled_collision(faces, voxels, collision_grid, stats, collision_aabb, reach, collision_exact, txt, angled_mesh)
					if box:
						world_brushes.append(box)
				else:
					world_brushes.append(clip_copy(txt))
					namer.special_used.add("CLIP")
				stats["world_brushes_written"] += 1
				continue
		sky_detail = cls == "detail" and " sky [" in txt  # SDHLT: no sky in any entity, so world
		if simplify_collision and cls in ("detail", "clip") and not sky_detail and not is_axial_brush(faces):
			box = angled_collision(faces, voxels, collision_grid, stats, collision_aabb, reach, collision_exact, txt, angled_mesh)
			if box:
				world_brushes.append(box)
			if cls == "detail" and detail_walls:
				thin.append((txt, faces))  # drawn and shot, no world leaves, no player hulls
				stats["detail_to_wall"] += 1
			elif cls == "detail":
				noclip_detail.append(txt)  # still drawn, no player hulls
				stats["detail_noclip"] += 1
			else:
				stats["clip_replaced"] += 1
			stats["world_brushes_written"] += 1
			continue
		if cls == "detail" and detail_walls and not detail_world and " sky [" not in txt:
			thin.append((txt, faces))
			world_brushes.append(clip_copy(txt))  # players collide in the world's hulls 1/3
			namer.special_used.add("CLIP")
			stats["detail_to_wall"] += 1
			stats["world_brushes_written"] += 1
			continue
		if cls == "detail" and detail_world:
			cls = "solid"  # MOHAA detail can be part of the shell; func_detail never seals in SDHLT
		if cls == "detail" and " sky [" in txt:
			cls = "solid"  # SDHLT rejects sky inside func_detail too
			stats["detail_sky_to_world"] += 1
		(detail if cls == "detail" else world_brushes).append(txt)
		stats["world_brushes_written"] += 1
	if voxels:
		world_brushes.extend(voxel_boxes(voxels, collision_grid, stats))
	if terrain_seal:
		world_brushes.extend(terrain_seal_brushes(bsp, scale, stats))
	if seal_box:
		world_brushes.extend(seal_box_brushes(bsp, scale, stats))
	if terrain:
		detail.extend(terrain_brushes(bsp, scale, terrain_tol, terrain_tex, stats))
	if mesh is not None and mesh_terrain and not terrain:
		add_mesh_terrain(bsp, scale, mesh, stats)
	if mesh is not None and mesh_patch_tol > 0:
		mesh_patches(bsp, scale, mesh_patch_tol, mesh, stats)
	blocks = [kv_block(ws_keys, world_brushes)]
	if detail:
		# SDHLT func_detail keeps MOHAA's detail brushes out of the vis tree.
		blocks.append(kv_block({"classname": "func_detail", "zhlt_detaillevel": "1"}, detail))
	if noclip_detail:
		blocks.append(kv_block({"classname": "func_detail", "zhlt_detaillevel": "1", "zhlt_noclip": "1"}, noclip_detail))
	if thin:
		blocks.extend(thin_wall_blocks(thin, stats, wall_cell))

	mesh_built = []

	def spawn_clear_z(x, y, z, stats):
		"""Centre height for a standing player at (x, y, z) that the engine mesh (terrain,
		patches, slopes) doesn't hold inside: MOHAA spawns sit on terrain at the feet, and a
		box whose corners dip into rising ground is stuck, so DoD never spawns anyone there."""
		if mesh is None or not (mesh.brushes or mesh.terrain or mesh.tris):
			return z
		if not mesh_built:
			mesh_built.append(mesh.build())
		m = mesh_built[0]
		lo, hi = (-16.0, -16.0, -GOLDSRC_HULL_HALF_HEIGHT), (16.0, 16.0, GOLDSRC_HULL_HALF_HEIGHT)
		if not mesh_collision.trace_box(m, (x, y, z), (x, y, z), lo, hi)[2]:
			return z
		top = z + 128.0
		frac, _, solid = mesh_collision.trace_box(m, (x, y, top), (x, y, z), lo, hi)
		if solid:
			stats["player_starts_stuck"] += 1
			return z
		stats["player_starts_lifted"] += 1
		return top + (z - top) * frac + 1.0

	skipped = Counter()
	static_cells = {}  # cell -> brush texts of unnamed static brush models, merged per cell
	trigger_groups = {}  # trigger keys -> brush texts, for triggers that merge
	targeted = {e["target"] for e in bsp.entities if e.get("target")}

	def unused_name(e):
		"""e's targetname, when nothing can ever look it up."""
		name = e.get("targetname")
		if not name or script_words is None or name in script_words or name in targeted:
			return False
		# scripts build numbered names: $("bunker_" + local.i) reaches bunker_1, bunker_2 ...
		stem = name.rstrip("0123456789")
		return not (stem != name and len(stem) >= 3 and stem in script_words)

	for e in bsp.entities[1:]:
		cn = e.get("classname", "")
		model = e.get("model", "")
		if merge_static_models and unused_name(e):
			e = {k: v for k, v in e.items() if k != "targetname"}
			stats["targetnames_unused"] += 1
		if model.startswith("*"):
			try:
				mi = int(model[1:])
			except ValueError:
				mi = -1
			if not 0 < mi < len(bsp.models):
				skipped[cn + " (bad model)"] += 1
				continue
			if cn.startswith("trigger_"):
				o = parse_vec(e.get("origin", ""))
				brushes = [_SIDE_TEXNAME_SUB.sub(r"\1AAATRIGGER [", t) for _, t, _ in model_brushes(bsp, mi, scale, o, namer, stats)]
				if not brushes:
					skipped[cn + " (no brushes)"] += 1
					continue
				namer.special_used.add("AAATRIGGER")
				keys = {"classname": TRIGGER_CLASS_MAP.get(cn, "trigger_multiple"), "mohaa_classname": cn}
				for k in TRIGGER_KEYS:
					if k in e:
						keys[k] = e[k]
				if e.get("setthread"):
					keys["netname"] = e["setthread"].strip()
				if keys["classname"] == "trigger_multiple" and "wait" not in keys:
					keys["wait"] = "0.2"  # MOHAA re-arms a multiple trigger quickly; GoldSrc's default is 0.2 too
				if merge_static_models and "targetname" not in keys and keys["classname"] != "trigger_once":
					# nothing names it, so the same keys on one entity act the same: touching any brush
					# fires it (a trigger_once stays apart, since each MOHAA one fires once on its own)
					trigger_groups.setdefault(tuple(keys.items()), []).extend(brushes)
					stats["triggers_merged"] += 1
					continue
				blocks.append(kv_block(keys, brushes))
				stats["triggers_written"] += 1
				continue
			gcn = NONSOLID_BRUSH.get(cn) or BRUSH_CLASS_MAP.get(cn, "func_wall")
			o = parse_vec(e.get("origin", ""))
			brushes = [t for _, t, _ in model_brushes(bsp, mi, scale, o, namer, stats)]
			if not brushes:
				skipped[cn + " (no brushes)"] += 1
				continue
			if merge_static_models and gcn == "func_wall" and cn not in NONSOLID_BRUSH \
					and not any(k in e for k in ("targetname", "target", "angle", "angles")):
				# nothing can name, target or move it: one model per cell instead of one each
				# (m5l2b's 375 script_objects overflowed the 512-model limit)
				m = bsp.models[mi]
				cell = tuple(int(((m.mins[k] + m.maxs[k]) * 0.5 * scale) // wall_cell) for k in range(2))
				static_cells.setdefault(cell, []).extend(brushes)
				stats["static_brush_models_merged"] += 1
				continue
			keys = {"classname": gcn, "mohaa_classname": cn}
			if cn in NONSOLID_BRUSH:
				keys["zhlt_noclip"] = "1"  # no hull 1-3 trees for a volume nobody collides with
			for k in ("targetname", "target", "angle", "angles", "speed", "wait", "lip"):
				if k in e:
					keys[k] = e[k]
			if gcn in ROTATING:
				brushes.append(origin_brush(tuple(c * scale for c in o)))
				namer.special_used.add("ORIGIN")
			blocks.append(kv_block(keys, brushes))
			stats["brush_entities_written"] += 1
			continue
		if cn in PLAYER_STARTS:
			ox, oy, oz = parse_vec(e.get("origin", ""))
			cz = spawn_clear_z(ox * scale, oy * scale, oz * scale + GOLDSRC_HULL_HALF_HEIGHT + 1, stats)
			org = f"{_f(ox * scale)} {_f(oy * scale)} {_f(cz)}"
			for gcn in PLAYER_STARTS[cn]:
				keys = {"classname": gcn, "origin": org}
				if "angle" in e:
					keys["angle"] = e["angle"]
				blocks.append(kv_block(keys))
				stats["player_starts_written"] += 1
			continue
		if is_actor(cn, e.get("model", "")):
			# dod-gc spawns this as a script grunt; the origin stays at the feet.
			ox, oy, oz = parse_vec(e.get("origin", ""))
			keys = {"classname": "mohaa_actor", "origin": f"{_f(ox * scale)} {_f(oy * scale)} {_f(oz * scale)}"}
			for k in ACTOR_KEYS:
				if k in e:
					keys[k] = e[k]
			if "model" not in keys and cn.lower() != "actor":
				keys["model"] = cn
			blocks.append(kv_block(keys))
			stats["actors_written"] += 1
			continue
		if cn.lower() in PATH_NODES:
			stats["path_nodes_to_sidecar"] += 1
			continue
		if e.get("targetname") and not unused_name(e) and not cn.lower().startswith("light"):
			# a named script_origin / script_model / script_object ...: scripts move it, hide it, read its
			# origin or thread on it, so it needs to exist. A point entity holds its place (one edict).
			ox, oy, oz = parse_vec(e.get("origin", ""))
			keys = {"classname": "info_target", "mohaa_classname": cn, "targetname": e["targetname"],
			        "origin": f"{_f(ox * scale)} {_f(oy * scale)} {_f(oz * scale)}"}
			for k in ("target", "angle", "angles"):
				if k in e:
					keys[k] = e[k]
			blocks.append(kv_block(keys))
			stats["named_points_written"] += 1
			continue
		skipped[cn] += 1

	if not stats["player_starts_written"]:
		# A map with no start can't be walked; drop one above the world centre.
		m = bsp.models[0]
		c = [(m.mins[i] + m.maxs[i]) * 0.5 * scale for i in range(3)]
		c[2] = m.maxs[2] * scale - 64
		for gcn in ("info_player_start", "info_player_allies", "info_player_axis"):
			blocks.append(kv_block({"classname": gcn, "origin": " ".join(_f(v) for v in c)}))
		stats["player_starts_fallback"] += 1

	for keys, brushes in trigger_groups.items():
		blocks.append(kv_block(dict(keys), brushes))
		stats["triggers_written"] += 1
	for cell in sorted(static_cells):
		blocks.append(kv_block({"classname": "func_wall", "mohaa_classname": "static_brush_models"}, static_cells[cell]))
		stats["static_brush_model_walls"] += 1
	text = "// generated by mohaa-gc tools/bsp19_to_map.py from " + bsp.name + "\n" + "\n".join(blocks) + "\n"
	return text, namer, stats, skipped


# ---------------------------------------------------------------- WAD3


def _placeholder_mips(name: str, size: int = 64):
	"""Two-tone checker in a colour derived from the name, all 4 mip levels."""
	h = hashlib.md5(name.encode()).digest()
	base = (64 + h[0] % 160, 64 + h[1] % 160, 64 + h[2] % 160)
	palette = bytearray(768)
	palette[0:3] = bytes(base)
	palette[3:6] = bytes(max(0, c - 40) for c in base)
	palette[765:768] = b"\x00\x00\xff"  # index 255 blue (transparent key in GoldSrc)
	mips = []
	for level in range(4):
		s = size >> level
		cell = max(1, 16 >> level)
		mips.append(bytes(((x // cell + y // cell) & 1) for y in range(s) for x in range(s)))
	return mips, bytes(palette)


def write_wad(path: Path, names):
	size = 64
	lumps = []
	for name in sorted(set(names)):
		mips, palette = _placeholder_mips(name, size)
		header_len = 16 + 4 + 4 + 16
		offsets = []
		pos = header_len
		for m in mips:
			offsets.append(pos)
			pos += len(m)
		body = struct.pack("<16sII4I", name.encode()[:15], size, size, *offsets)
		body += b"".join(mips) + struct.pack("<H", 256) + palette + b"\x00\x00"
		lumps.append((name, body))
	out = bytearray(b"WAD3" + struct.pack("<ii", len(lumps), 0))
	entries = []
	for name, body in lumps:
		entries.append((len(out), len(body), name))
		out += body
	dir_ofs = len(out)
	for ofs, ln, name in entries:
		out += struct.pack("<iiibbh16s", ofs, ln, ln, 0x43, 0, 0, name.encode()[:15])
	struct.pack_into("<i", out, 8, dir_ofs)
	path.write_bytes(bytes(out))


# ---------------------------------------------------------------- CLI


def read_source(src: str) -> tuple[str, bytes]:
	if ".pk3:" in src.lower():
		i = src.lower().index(".pk3:") + 4
		pak, inner = src[:i], src[i + 1:]
		with zipfile.ZipFile(pak) as z:
			names = {n.lower(): n for n in z.namelist()}
			real = names.get(inner.lower())
			if not real:
				raise SystemExit(f"{inner} not found in {pak}")
			return f"{Path(pak).name}:{real}", z.read(real)
	return src, Path(src).read_bytes()


SCRIPT_WORD = re.compile(r"[A-Za-z0-9_]+")


def script_names(inputs, mapname):
	"""Every word in the scripts the level runs (maps/<map>.scr and the global scripts it pulls in),
	read from MOHAA pk3s or directories, or None when the map has no script. A targetname missing
	from this set can't be what a script asks for with $name, so the converter may drop it."""
	from stage_scripts import closure
	from ubersound import collect, read
	scripts = collect(inputs, (".scr",))
	need, _ = closure(scripts, mapname)
	if not need:
		return None
	words = set()
	for path in need:
		words.update(SCRIPT_WORD.findall(read(scripts[path]).decode("latin-1")))
	return words


def main(argv=None) -> int:
	ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
	ap.add_argument("source")
	ap.add_argument("-o", "--out", type=Path, required=True, help="output .map")
	ap.add_argument("--wad", type=Path, help="also write a placeholder WAD3 with every used texture")
	ap.add_argument("--scale", type=float, default=DEFAULT_SCALE)
	ap.add_argument("--terrain-brushes", action="store_true",
	                help="also write LOD terrain as wedge brushes (GoldSrc-native terrain collision)")
	ap.add_argument("--terrain-tol", type=float, default=8.0,
	                help="max terrain height error for --terrain-brushes, GoldSrc units (default 8)")
	ap.add_argument("--terrain-tex", default="CLIP",
	                help="texture for terrain brushes: CLIP (player hulls only; default, keeps hull 0 small) or NULL")
	ap.add_argument("--no-terrain-seal", action="store_true",
	                help="don't write the NULL columns under terrain that stop it leaking")
	ap.add_argument("--detail-world", action="store_true",
	                help="write MOHAA detail brushes into worldspawn (they seal; func_detail does not)")
	ap.add_argument("--simplify-collision", action="store_true",
	                help="angled detail/clip brushes collide as merged CLIP boxes on a grid (detail still drawn)")
	ap.add_argument("--collision-grid-z", type=float,
	                help="vertical cell for --simplify-collision (default: same as --collision-grid); "
	                     "keep it under 18 so voxel slopes stay climbable while xy is coarser")
	ap.add_argument("--collision-aabb", type=float, default=0.0, metavar="FILL",
	                help="under --simplify-collision, an angled brush collides as its own bounding box when it "
	                     "fills at least FILL of it (e.g. 0.4) or is smaller than a cell; others are voxelized")
	ap.add_argument("--mesh-collision", action="store_true",
	                help="under --simplify-collision, angled brushes collide exactly through the engine instead of "
	                     "voxels: written to <out>.mcol (needs xash3d-gc mesh collision)")
	ap.add_argument("--no-mesh-terrain", action="store_true",
	                help="don't give LOD terrain collision through the engine mesh (by default it goes to "
	                     "<out>.mcol as exact heightfields)")
	ap.add_argument("--mesh-patch-tol", type=float, default=2.0, metavar="UNITS",
	                help="solid curved patches collide through the engine mesh, tessellated within about UNITS "
	                     "(default 2; 0 = no patch collision, as before)")
	ap.add_argument("--collision-exact", type=float, default=0.0, metavar="UNITS",
	                help="under --simplify-collision, angled brushes at least UNITS long keep exact CLIP "
	                     "collision (a big slope is a few planes exact, hundreds of voxel steps)")
	ap.add_argument("--collision-reach", type=float, default=0.0, metavar="UNITS",
	                help="under --simplify-collision, angled brushes further than UNITS (xy) from every path "
	                     "node and player start get no player collision (needs >= 8 such points)")
	ap.add_argument("--collision-grid", type=float, default=16.0,
	                help="grid for --simplify-collision, GoldSrc units (default 16, under the 18-unit step)")
	ap.add_argument("--seal-box", action="store_true",
	                help="enclose the map in a NULL box so hull 0 can't leak (last resort)")
	ap.add_argument("--detail-walls", action="store_true",
	                help="put all MOHAA detail into per-cell zhlt_noclip func_walls (no world hull-0 leaves); "
	                     "players collide with CLIP copies, or voxel boxes for angled detail under --simplify-collision")
	ap.add_argument("--wall-cell", type=float, default=THIN_WALL_CELL,
	                help="cell size for detail/thin func_walls (default 1024); larger means fewer brush "
	                     "models (SDHLT allows 512) and smaller BSP trees, coarser culling")
	ap.add_argument("--keep-brush-models", action="store_true",
	                help="write every MOHAA brush model as its own entity (default: unnamed, untargeted static "
	                     "ones such as script_object are merged into one func_wall per --wall-cell cell, which "
	                     "keeps maps under the 512-model limit)")
	ap.add_argument("--thin-detail-in-world", action="store_true",
	                help="keep thickened detail slivers in func_detail (default: per-cell func_walls, "
	                     "which keeps them out of the world's hull-0 leaves)")
	ap.add_argument("--scripts", action="append", metavar="PATH",
	                help="MOHAA main directory or pk3 (repeatable): targetnames the level's scripts never use "
	                     "are dropped, so those brush models and triggers merge too")
	args = ap.parse_args(argv)

	mesh = mesh_collision.Collision()
	name, data = read_source(args.source)
	bsp = b19.load_bytes(data, name)
	words = None
	if args.scripts:
		mapname = re.sub(r"\.bsp$", "", re.split(r"[/:\\]", name)[-1], flags=re.I).lower()
		words = script_names(args.scripts, mapname)
		if words is None:
			print(f"{name}: no maps/{mapname}.scr, keeping every targetname")
	wad_key = str(args.wad.resolve()) if args.wad else None
	text, namer, stats, skipped = convert(bsp, args.scale, wad_key, args.terrain_brushes, args.terrain_tol, args.terrain_tex,
	                                         not args.no_terrain_seal, args.detail_world, args.seal_box,
	                                         args.simplify_collision,
	                                         (args.collision_grid, args.collision_grid_z or args.collision_grid),
	                                         not args.thin_detail_in_world, args.detail_walls, args.wall_cell,
	                                         args.collision_aabb, args.collision_reach, args.collision_exact,
	                                         mesh, not args.no_mesh_terrain, args.mesh_patch_tol, args.mesh_collision,
	                                         not args.keep_brush_models, words)
	args.out.write_text(text)
	ntext, nnodes = path_nodes(bsp, args.scale)
	if nnodes:
		npath = args.out.with_suffix(".nodes")
		npath.write_text(ntext)
		print(f"{name}: wrote {npath} ({nnodes} path nodes)")
	if mesh.brushes or mesh.terrain or mesh.tris:
		mpath = args.out.with_suffix(".mcol")
		npl, nbr, nsd, nnd = mesh.write(mpath)
		print(f"{name}: wrote {mpath} ({nbr} brushes, {npl} planes, {nnd} nodes, {mpath.stat().st_size} bytes)")
	if args.wad:
		write_wad(args.wad, list(namer.by_shader.values()) + sorted(namer.special_used))
	print(f"{name}: wrote {args.out}")
	for k in sorted(stats):
		print(f"  {k:<28} {stats[k]}")
	print(f"  textures                     {len(namer.by_shader)}")
	if skipped:
		print("  point/brush entities not written: " + ", ".join(f"{k} x{v}" for k, v in skipped.most_common(15)))
	return 0


if __name__ == "__main__":
	sys.exit(main())
