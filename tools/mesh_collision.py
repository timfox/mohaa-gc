#!/usr/bin/env python3
"""Per-map brush collision sidecar (.mcol) for xash3d-gc.

Angled MOHAA detail costs too many clipnodes as BSP30 hull geometry, so its player
collision moves to the engine (decision 2026-11-21): the engine sweeps the player box
against these convex brushes the way MOHAA's own Quake 3 collision does, with brush
planes pushed out by the box and axial bevels so corners don't snag.

Terrain (MOHAA LOD terrain patches) is stored as heightfields, the way MOHAA's own
cm_terrain does: 9 x 9 heights per 8 x 8-cell patch, swept as one wedge brush per
triangle that the engine builds on the fly. That is about 1% of the size of storing
the same wedges as brushes.

File layout, little-endian:
  header  char magic[4] "MCOL"; int32 version (3); int32 numplanes, numbrushes,
          numsides, numnodes, numterrain, numtnodes
  planes  numplanes  x { float normal[3]; float dist; }
  brushes numbrushes x { int32 firstside; int32 numsides; float mins[3]; float maxs[3]; }
          A brush is its six axial planes, which are exactly its bounds (a real axial
          face lies on the bounds, a bevel is defined by them), followed by its
          non-axial sides. Axial planes are never stored: that halves the file.
  sides   numsides   x { int32 planenum; }
  nodes   numnodes   x { float mins[3]; float maxs[3]; int32 a; int32 b; }
          b > 0: leaf holding brushes a .. a+b-1; b == 0: inner node, children a, a+1.
          Node 0 is the root. Brushes are stored in leaf order.
  terrain numterrain x { float origin[3]; float cell; float zscale; float zmin; float zmax;
                         uint8 h[81]; uint8 pad[3]; }
          Sample (i, j) is at origin + (i * cell, j * cell, zscale * h[j * 9 + i]). Cell
          (i, j) splits into triangles (p00, p10, p01) and (p11, p01, p10); each is the top
          of a wedge reaching TERRAIN_DEPTH below its lowest corner, with planes: the cell
          bounds (axial, as for brushes), then its top, then its diagonal side.
          zmin/zmax bound the heights.
  tnodes  numtnodes  x node, as above, over terrain patches (stored in leaf order).

trace_box() is the reference sweep that the engine port must match.
"""
from __future__ import annotations

import struct

MAGIC = b"MCOL"
VERSION = 3
TERRAIN_SAMPLES = 9
TERRAIN_DEPTH = 16.0
LEAF_SIZE = 4
DIST_EPSILON = 0.03125  # Quake's SURFACE_CLIP_EPSILON


def _dot(a, b):
	return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _axial(n):
	return sum(1 for c in n if abs(c) > 1e-6) == 1


def bound_planes(mins, maxs):
	"""The six axial planes of a brush, in the order the engine tests them."""
	out = []
	for ax in range(3):
		n = [0.0, 0.0, 0.0]
		n[ax] = -1.0
		out.append((tuple(n), -mins[ax]))
		n = [0.0, 0.0, 0.0]
		n[ax] = 1.0
		out.append((tuple(n), maxs[ax]))
	return out


def _cross(a, b):
	return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _norm(v):
	ln = _dot(v, v) ** 0.5
	return (v[0] / ln, v[1] / ln, v[2] / ln)


def terrain_point(t, i, j):
	origin, cell, zscale, _, _, h = t
	return (origin[0] + i * cell, origin[1] + j * cell, origin[2] + zscale * h[j * TERRAIN_SAMPLES + i])


def terrain_wedges(t, i, j):
	"""The two wedges of terrain cell (i, j): [(mins, maxs, [top, diagonal])]."""
	p00, p10 = terrain_point(t, i, j), terrain_point(t, i + 1, j)
	p01, p11 = terrain_point(t, i, j + 1), terrain_point(t, i + 1, j + 1)
	out = []
	for a, b, c in ((p00, p10, p01), (p11, p01, p10)):
		n = _norm(_cross((b[0] - a[0], b[1] - a[1], b[2] - a[2]), (c[0] - a[0], c[1] - a[1], c[2] - a[2])))
		if n[2] < 0:
			n = (-n[0], -n[1], -n[2])
		# diagonal b -> c, facing away from a
		e = (c[0] - b[0], c[1] - b[1])
		sn = _norm((e[1], -e[0], 0.0))
		if sn[0] * (a[0] - b[0]) + sn[1] * (a[1] - b[1]) > 0:
			sn = (-sn[0], -sn[1], 0.0)
		zs = (a[2], b[2], c[2])
		mins = (p00[0], p00[1], min(zs) - TERRAIN_DEPTH)
		maxs = (p11[0], p11[1], max(zs))
		out.append((mins, maxs, [(n, _dot(n, a)), (sn, _dot(sn, b))]))
	return out


def _bvh(boxes, leaf_size=LEAF_SIZE):
	"""Median-split BVH over [(mins, maxs)]: returns (nodes, order) in the file's node format."""
	nodes, order = [], []

	def build_into(slot, items):
		mins = tuple(min(boxes[i][0][k] for i in items) for k in range(3))
		maxs = tuple(max(boxes[i][1][k] for i in items) for k in range(3))
		if len(items) <= leaf_size:
			nodes[slot] = (mins, maxs, len(order), len(items))
			order.extend(items)
			return
		ax = max(range(3), key=lambda k: maxs[k] - mins[k])
		items = sorted(items, key=lambda i: boxes[i][0][ax] + boxes[i][1][ax])
		half = len(items) // 2
		first = len(nodes)
		nodes.extend([None, None])  # children stay adjacent
		build_into(first, items[:half])
		build_into(first + 1, items[half:])
		nodes[slot] = (mins, maxs, first, 0)

	if boxes:
		nodes.append(None)
		build_into(0, list(range(len(boxes))))
	return nodes, order


class Collision:
	def __init__(self):
		self.brushes = []  # (planes, mins, maxs)
		self.terrain = []  # (origin, cell, zscale, zmin, zmax, h)

	def add_brush(self, planes, verts):
		mins = tuple(min(v[i] for v in verts) for i in range(3))
		maxs = tuple(max(v[i] for v in verts) for i in range(3))
		self.brushes.append(([p for p in planes if not _axial(p[0])], mins, maxs))

	def add_terrain(self, origin, cell, zscale, h):
		"""One 9 x 9 heightfield patch: sample (i, j) at origin + (i cell, j cell, zscale h[j*9+i])."""
		assert len(h) == TERRAIN_SAMPLES * TERRAIN_SAMPLES and all(0 <= v < 256 for v in h)
		zs = [origin[2] + zscale * v for v in h]
		self.terrain.append((tuple(origin), cell, zscale, min(zs), max(zs), bytes(h)))

	@staticmethod
	def terrain_box(t):
		origin, cell, _, zmin, zmax, _ = t
		span = cell * (TERRAIN_SAMPLES - 1)
		return (origin[0], origin[1], zmin - TERRAIN_DEPTH), (origin[0] + span, origin[1] + span, zmax)

	def build(self):
		"""Returns (planes, brushes, sides, nodes, terrain, tnodes), items in leaf order."""
		plane_ix, planes = {}, []
		nodes, order = _bvh([(b[1], b[2]) for b in self.brushes])
		brushes, sides = [], []
		for i in order:
			bplanes, mins, maxs = self.brushes[i]
			first = len(sides)
			for n, d in bplanes:
				key = (round(n[0], 6), round(n[1], 6), round(n[2], 6), round(d, 3))
				if key not in plane_ix:
					plane_ix[key] = len(planes)
					planes.append((n, d))
				sides.append(plane_ix[key])
			brushes.append((first, len(bplanes), mins, maxs))
		tnodes, torder = _bvh([self.terrain_box(t) for t in self.terrain])
		terrain = [self.terrain[i] for i in torder]
		return planes, brushes, sides, nodes, terrain, tnodes

	def write(self, path):
		planes, brushes, sides, nodes, terrain, tnodes = self.build()
		with open(path, "wb") as f:
			f.write(MAGIC + struct.pack("<7i", VERSION, len(planes), len(brushes), len(sides), len(nodes),
			                            len(terrain), len(tnodes)))
			for n, d in planes:
				f.write(struct.pack("<4f", n[0], n[1], n[2], d))
			for first, num, mins, maxs in brushes:
				f.write(struct.pack("<2i6f", first, num, *mins, *maxs))
			for s in sides:
				f.write(struct.pack("<i", s))
			for mins, maxs, a, b in nodes:
				f.write(struct.pack("<6f2i", *mins, *maxs, a, b))
			for origin, cell, zscale, zmin, zmax, h in terrain:
				f.write(struct.pack("<7f", *origin, cell, zscale, zmin, zmax) + h + b"\0\0\0")
			for mins, maxs, a, b in tnodes:
				f.write(struct.pack("<6f2i", *mins, *maxs, a, b))
		return len(planes), len(brushes), len(sides), len(nodes)


TERRAIN_RECORD = 7 * 4 + 84


def read(path):
	with open(path, "rb") as f:
		data = f.read()
	assert data[:4] == MAGIC
	ver, npl, nbr, nsd, nnd, nte, ntn = struct.unpack_from("<7i", data, 4)
	assert ver == VERSION
	o = 32

	def node_list(o, n):
		return [((a, b, c), (d, e, f), g, h) for a, b, c, d, e, f, g, h in struct.iter_unpack("<6f2i", data[o:o + 32 * n])]

	planes = [((a, b, c), d) for a, b, c, d in struct.iter_unpack("<4f", data[o:o + 16 * npl])]
	o += 16 * npl
	brushes = [(a, b, (c, d, e), (f, g, h)) for a, b, c, d, e, f, g, h in struct.iter_unpack("<2i6f", data[o:o + 32 * nbr])]
	o += 32 * nbr
	sides = [s for (s,) in struct.iter_unpack("<i", data[o:o + 4 * nsd])]
	o += 4 * nsd
	nodes = node_list(o, nnd)
	o += 32 * nnd
	terrain = []
	for k in range(nte):
		x, y, z, cell, zscale, zmin, zmax = struct.unpack_from("<7f", data, o)
		terrain.append(((x, y, z), cell, zscale, zmin, zmax, data[o + 28:o + 28 + 81]))
		o += TERRAIN_RECORD
	tnodes = node_list(o, ntn)
	return planes, brushes, sides, nodes, terrain, tnodes


def _walk(nodes, overlaps):
	"""Leaf ranges (a, b) of the BVH whose boxes overlap."""
	stack = [0] if nodes else []
	while stack:
		lo, hi, a, b = nodes[stack.pop()]
		if not overlaps(lo, hi):
			continue
		if b:
			yield a, b
		else:
			stack.extend((a, a + 1))


def trace_box(mcol, start, end, mins, maxs):
	"""Sweep box (mins, maxs) from start to end. Returns (fraction, normal, startsolid).
	Quake 3 CM_TraceThroughBrush: each plane is pushed out by the box's support
	distance; enter/leave fractions are clipped DIST_EPSILON short of the surface.
	Brushes first, then terrain wedges, in BVH order."""
	planes, brushes, sides, nodes, terrain, tnodes = mcol
	best = [1.0, None, False]
	bmin = [min(start[i], end[i]) + mins[i] for i in range(3)]
	bmax = [max(start[i], end[i]) + maxs[i] for i in range(3)]

	def overlaps(lo, hi):
		return all(lo[i] <= bmax[i] and hi[i] >= bmin[i] for i in range(3))

	def brush(bl, bh, extra):
		enter, leave = -1.0, 1.0
		clipn = None
		startout = getsout = False
		for n, d in bound_planes(bl, bh) + extra:
			off = [maxs[i] if n[i] < 0 else mins[i] for i in range(3)]
			dist = d - _dot(off, n)
			d1 = _dot(start, n) - dist
			d2 = _dot(end, n) - dist
			if d2 > 0:
				getsout = True
			if d1 > 0:
				startout = True
			if d1 > 0 and (d2 >= DIST_EPSILON or d2 >= d1):
				return
			if d1 <= 0 and d2 <= 0:
				continue
			if d1 > d2:
				f = (d1 - DIST_EPSILON) / (d1 - d2)
				if f < 0:
					f = 0.0
				if f > enter:
					enter, clipn = f, n
			else:
				f = (d1 + DIST_EPSILON) / (d1 - d2)
				if f > 1:
					f = 1.0
				if f < leave:
					leave = f
		if not startout:
			best[2] = True
			if not getsout:
				best[0] = 0.0
			return
		if enter < leave and enter > -1 and enter < best[0]:
			best[0], best[1] = max(enter, 0.0), clipn

	for a, b in _walk(nodes, overlaps):
		for first, num, bl, bh in brushes[a:a + b]:
			if overlaps(bl, bh):
				brush(bl, bh, [planes[s] for s in sides[first:first + num]])

	last = TERRAIN_SAMPLES - 2
	for a, b in _walk(tnodes, overlaps):
		for t in terrain[a:a + b]:
			origin, cell = t[0], t[1]
			lo, hi = Collision.terrain_box(t)
			if not overlaps(lo, hi):
				continue
			i0 = max(0, min(last, int((bmin[0] - origin[0]) // cell)))
			i1 = max(0, min(last, int((bmax[0] - origin[0]) // cell)))
			j0 = max(0, min(last, int((bmin[1] - origin[1]) // cell)))
			j1 = max(0, min(last, int((bmax[1] - origin[1]) // cell)))
			for j in range(j0, j1 + 1):
				for i in range(i0, i1 + 1):
					for wl, wh, extra in terrain_wedges(t, i, j):
						if overlaps(wl, wh):
							brush(wl, wh, extra)
	return tuple(best)
