#!/usr/bin/env python3
"""Per-map brush collision sidecar (.mcol) for xash3d-gc.

Angled MOHAA detail costs too many clipnodes as BSP30 hull geometry, so its player
collision moves to the engine (decision 2026-11-21): the engine sweeps the player box
against these convex brushes the way MOHAA's own Quake 3 collision does, with brush
planes pushed out by the box and axial bevels so corners don't snag.

File layout, little-endian:
  header  char magic[4] "MCOL"; int32 version (1); int32 numplanes, numbrushes,
          numsides, numnodes
  planes  numplanes  x { float normal[3]; float dist; }
  brushes numbrushes x { int32 firstside; int32 numsides; float mins[3]; float maxs[3]; }
  sides   numsides   x { int32 planenum; }
  nodes   numnodes   x { float mins[3]; float maxs[3]; int32 a; int32 b; }
          b > 0: leaf holding brushes a .. a+b-1; b == 0: inner node, children a, a+1.
          Node 0 is the root. Brushes are stored in leaf order.

trace_box() is the reference sweep that the engine port must match.
"""
from __future__ import annotations

import struct

MAGIC = b"MCOL"
VERSION = 1
LEAF_SIZE = 4
DIST_EPSILON = 0.03125  # Quake's SURFACE_CLIP_EPSILON


def _dot(a, b):
	return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def with_axial_bevels(planes, verts):
	"""planes: [(normal, dist)]. Adds any missing axis-aligned bounding planes."""
	out = list(planes)
	for ax in range(3):
		for sign in (1.0, -1.0):
			n = [0.0, 0.0, 0.0]
			n[ax] = sign
			if any(abs(p[0][0] - n[0]) < 1e-6 and abs(p[0][1] - n[1]) < 1e-6 and abs(p[0][2] - n[2]) < 1e-6
			       for p in planes):
				continue
			d = max(sign * v[ax] for v in verts)
			out.append((tuple(n), d))
	return out


class Collision:
	def __init__(self):
		self.brushes = []  # (planes, mins, maxs)

	def add_brush(self, planes, verts):
		mins = tuple(min(v[i] for v in verts) for i in range(3))
		maxs = tuple(max(v[i] for v in verts) for i in range(3))
		self.brushes.append((with_axial_bevels(planes, verts), mins, maxs))

	def build(self):
		"""Returns (planes, brushes, sides, nodes) with brushes in leaf order."""
		plane_ix, planes = {}, []
		nodes, order = [], []

		def build_into(slot, items):
			mins = tuple(min(self.brushes[i][1][k] for i in items) for k in range(3))
			maxs = tuple(max(self.brushes[i][2][k] for i in items) for k in range(3))
			if len(items) <= LEAF_SIZE:
				nodes[slot] = (mins, maxs, len(order), len(items))
				order.extend(items)
				return
			ax = max(range(3), key=lambda k: maxs[k] - mins[k])
			items = sorted(items, key=lambda i: self.brushes[i][1][ax] + self.brushes[i][2][ax])
			half = len(items) // 2
			first = len(nodes)
			nodes.extend([None, None])  # children stay adjacent
			build_into(first, items[:half])
			build_into(first + 1, items[half:])
			nodes[slot] = (mins, maxs, first, 0)

		if self.brushes:
			nodes.append(None)
			build_into(0, list(range(len(self.brushes))))
		fixed = nodes
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
		return planes, brushes, sides, fixed

	def write(self, path):
		planes, brushes, sides, nodes = self.build()
		with open(path, "wb") as f:
			f.write(MAGIC + struct.pack("<5i", VERSION, len(planes), len(brushes), len(sides), len(nodes)))
			for n, d in planes:
				f.write(struct.pack("<4f", n[0], n[1], n[2], d))
			for first, num, mins, maxs in brushes:
				f.write(struct.pack("<2i6f", first, num, *mins, *maxs))
			for s in sides:
				f.write(struct.pack("<i", s))
			for mins, maxs, a, b in nodes:
				f.write(struct.pack("<6f2i", *mins, *maxs, a, b))
		return len(planes), len(brushes), len(sides), len(nodes)


def read(path):
	with open(path, "rb") as f:
		data = f.read()
	assert data[:4] == MAGIC
	ver, npl, nbr, nsd, nnd = struct.unpack_from("<5i", data, 4)
	assert ver == VERSION
	o = 24
	planes = [((a, b, c), d) for a, b, c, d in struct.iter_unpack("<4f", data[o:o + 16 * npl])]
	o += 16 * npl
	brushes = [(a, b, (c, d, e), (f, g, h)) for a, b, c, d, e, f, g, h in struct.iter_unpack("<2i6f", data[o:o + 32 * nbr])]
	o += 32 * nbr
	sides = [s for (s,) in struct.iter_unpack("<i", data[o:o + 4 * nsd])]
	o += 4 * nsd
	nodes = [((a, b, c), (d, e, f), g, h) for a, b, c, d, e, f, g, h in struct.iter_unpack("<6f2i", data[o:o + 32 * nnd])]
	return planes, brushes, sides, nodes


def trace_box(mcol, start, end, mins, maxs):
	"""Sweep box (mins, maxs) from start to end. Returns (fraction, normal, startsolid).
	Quake 3 CM_TraceThroughBrush: each plane is pushed out by the box's support
	distance; enter/leave fractions are clipped DIST_EPSILON short of the surface."""
	planes, brushes, sides, nodes = mcol
	best = [1.0, None, False]
	bmin = [min(start[i], end[i]) + mins[i] for i in range(3)]
	bmax = [max(start[i], end[i]) + maxs[i] for i in range(3)]

	def overlaps(lo, hi):
		return all(lo[i] <= bmax[i] and hi[i] >= bmin[i] for i in range(3))

	def brush(first, num):
		enter, leave = -1.0, 1.0
		clipn = None
		startout = getsout = False
		for s in sides[first:first + num]:
			n, d = planes[s]
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

	stack = [0] if nodes else []
	while stack:
		lo, hi, a, b = nodes[stack.pop()]
		if not overlaps(lo, hi):
			continue
		if b:
			for first, num, bl, bh in brushes[a:a + b]:
				if overlaps(bl, bh):
					brush(first, num)
		else:
			stack.extend((a, a + 1))
	return tuple(best)
