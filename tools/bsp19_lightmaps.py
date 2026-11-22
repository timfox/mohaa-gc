#!/usr/bin/env python3
"""Give a converted map MOHAA's own lightmaps.

bsp19_to_map.py hands SDHLT brushes only, and the map is compiled without
sdHLRAD, so the BSP30 comes out with an empty lighting lump: the world is
fullbright and the GameCube light faces have no samples (models went black).
MOHAA already ships the map lit. This copies that light across: every lit
BSP30 face gets a GoldSrc lightmap (one luxel per 16 texels, as the engine
reads it) whose samples are looked up in the MOHAA lightmap of the coplanar
MOHAA surface under each luxel.

Runs on the user's own install (bring your own data): nothing retail is kept
in this repo, and it is stdlib-only Python.

Usage:
  bsp19_lightmaps.py MOHAA.bsp MAP30.bsp [-o OUT.bsp] [--scale S] [--gain G]
  MOHAA.bsp may be archive.pk3:maps/name.bsp. Without -o MAP30.bsp is rewritten.
"""
from __future__ import annotations

import argparse
import math
import struct
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mohaa_bsp19 as b19  # noqa: E402

DEFAULT_SCALE = 72.0 / 94.0  # bsp19_to_map.py's
LM = 128  # MOHAA lightmap page side
# MOHAA stores lightmaps one overbright bit down (the renderer shifts them up),
# so the bytes are doubled to get the light the game shows.
DEFAULT_GAIN = 2.0
TEX_SPECIAL = 1
PLANE_DOT = 0.995  # normals this close are one plane
PLANE_DIST = 2.0  # GoldSrc units
NEAR = 24.0  # a luxel off every MOHAA triangle takes the nearest one this close
FALLBACK = (150, 150, 150)
BSP30_LUMPS = 15
LUMP_LIGHTING = 8


# ------------------------------------------------------------- MOHAA side

class Mohaa:
	"""Lit planar surfaces of a MOHAA map, as scaled triangles."""

	def __init__(self, data: bytes, scale: float):
		bsp = b19.load_bytes(data)
		version = bsp.version
		self.pages = self._lump(data, version, b19.LUMP_LIGHTMAPS)
		dv = self._lump(data, version, b19.LUMP_DRAWVERTS)
		sraw = self._lump(data, version, b19.LUMP_SURFACES)
		self.tris = []  # (n, d, p0, p1, p2, lm0, lm1, lm2, page, rect)
		self.grid: dict = {}
		# Brush entity surfaces are stored around the entity's origin, and
		# bsp19_to_map.py moves their brushes out by it: do the same here.
		shift = {}
		for e in bsp.entities[1:]:
			model = e.get("model", "")
			if not model.startswith("*"):
				continue
			try:
				mi = int(model[1:])
				org = tuple(float(c) for c in e.get("origin", "0 0 0").split()[:3])
			except ValueError:
				continue
			if 0 < mi < len(bsp.models) and len(org) == 3 and any(org):
				m = bsp.models[mi]
				for k in range(m.first_surface, m.first_surface + m.num_surfaces):
					shift[k] = org
		for k in range(len(sraw) // b19.SZ_SURFACE):
			ox, oy, oz = shift.get(k, (0.0, 0.0, 0.0))
			v = struct.unpack_from("<12i", sraw, k * b19.SZ_SURFACE)
			stype, first_vert, num_verts, first_index, num_index = v[2], v[3], v[4], v[5], v[6]
			page, lx, ly, lw, lh = v[7], v[8], v[9], v[10], v[11]
			if stype != b19.MST_PLANAR or page < 0 or (page + 1) * b19.LIGHTMAP_BYTES > len(self.pages):
				continue
			sh = bsp.shaders[v[0]] if 0 <= v[0] < len(bsp.shaders) else None
			if sh and sh.surface_flags & (b19.SURF_SKY | b19.SURF_NODRAW):
				continue
			pos, lmst, vnorm = [], [], []
			for i in range(first_vert, first_vert + num_verts):
				o = i * b19.SZ_DRAWVERT
				if o + b19.SZ_DRAWVERT > len(dv):
					break
				x, y, z = struct.unpack_from("<3f", dv, o)
				pos.append(((x + ox) * scale, (y + oy) * scale, (z + oz) * scale))
				lmst.append(struct.unpack_from("<2f", dv, o + 20))
				vnorm.append(struct.unpack_from("<3f", dv, o + 28))
			if len(pos) < num_verts:
				continue
			rect = (lx, ly, lx + max(lw, 1) - 1, ly + max(lh, 1) - 1)
			for t in range(first_index, first_index + num_index - 2, 3):
				try:
					a, b, c = bsp.drawindexes[t], bsp.drawindexes[t + 1], bsp.drawindexes[t + 2]
					tri = (pos[a], pos[b], pos[c])
				except IndexError:
					break
				n = _cross(_sub(tri[1], tri[0]), _sub(tri[2], tri[0]))
				ln = math.sqrt(_dot(n, n))
				if ln < 1e-6:
					continue
				n = (n[0] / ln, n[1] / ln, n[2] / ln)
				if _dot(n, vnorm[a]) < 0.0:  # Q3 winds front faces clockwise
					n = (-n[0], -n[1], -n[2])
				self._add((n, _dot(n, tri[0]), tri, (lmst[a], lmst[b], lmst[c]), page, rect))

	@staticmethod
	def _lump(data: bytes, version: int, lump: int) -> bytes:
		idx = b19._lump_index(version, lump)
		ofs, ln = struct.unpack_from("<2i", data, 12 + idx * 8)
		return data[ofs:ofs + ln]

	CELL = 256.0

	def _add(self, tri):
		self.tris.append(tri)
		ti = len(self.tris) - 1
		p = tri[2]
		lo = [math.floor((min(q[a] for q in p) - NEAR) / self.CELL) for a in range(3)]
		hi = [math.floor((max(q[a] for q in p) + NEAR) / self.CELL) for a in range(3)]
		for x in range(lo[0], hi[0] + 1):
			for y in range(lo[1], hi[1] + 1):
				for z in range(lo[2], hi[2] + 1):
					self.grid.setdefault((x, y, z), []).append(ti)

	def candidates(self, n, d, lo, hi) -> list:
		"""Triangles on the plane (n, d) near the box lo..hi."""
		seen = set()
		out = []
		c0 = [math.floor(lo[a] / self.CELL) for a in range(3)]
		c1 = [math.floor(hi[a] / self.CELL) for a in range(3)]
		for x in range(c0[0], c1[0] + 1):
			for y in range(c0[1], c1[1] + 1):
				for z in range(c0[2], c1[2] + 1):
					for ti in self.grid.get((x, y, z), ()):
						if ti in seen:
							continue
						seen.add(ti)
						t = self.tris[ti]
						if _dot(t[0], n) >= PLANE_DOT and abs(t[1] - d) <= PLANE_DIST:
							out.append(t)
		return out

	def sample(self, tri, p) -> tuple:
		"""MOHAA light (0..255 floats, before the gain) at p on tri."""
		_n, _d, (a, b, c), (la, lb, lc), page, rect = tri
		u, v, w = _bary(a, b, c, p)
		s = la[0] * u + lb[0] * v + lc[0] * w
		t = la[1] * u + lb[1] * v + lc[1] * w
		x = min(max(s * LM - 0.5, rect[0]), rect[2])
		y = min(max(t * LM - 0.5, rect[1]), rect[3])
		x0, y0 = int(x), int(y)
		x1, y1 = min(x0 + 1, rect[2]), min(y0 + 1, rect[3])
		fx, fy = x - x0, y - y0
		base = page * b19.LIGHTMAP_BYTES
		pg = self.pages
		acc = [0.0, 0.0, 0.0]
		for xx, yy, wt in ((x0, y0, (1 - fx) * (1 - fy)), (x1, y0, fx * (1 - fy)),
				(x0, y1, (1 - fx) * fy), (x1, y1, fx * fy)):
			o = base + (yy * LM + xx) * 3
			acc[0] += pg[o] * wt
			acc[1] += pg[o + 1] * wt
			acc[2] += pg[o + 2] * wt
		return acc


def _sub(a, b):
	return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dot(a, b):
	return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
	return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _bary(a, b, c, p):
	v0, v1, v2 = _sub(b, a), _sub(c, a), _sub(p, a)
	d00, d01, d11 = _dot(v0, v0), _dot(v0, v1), _dot(v1, v1)
	d20, d21 = _dot(v2, v0), _dot(v2, v1)
	den = d00 * d11 - d01 * d01
	if abs(den) < 1e-12:
		return 1.0, 0.0, 0.0
	v = (d11 * d20 - d01 * d21) / den
	w = (d00 * d21 - d01 * d20) / den
	return 1.0 - v - w, v, w


def _clamp_tri(u, v, w):
	"""Barycentrics pulled onto the triangle, and how far outside they were."""
	out = -min(u, v, w, 0.0)
	u, v, w = max(u, 0.0), max(v, 0.0), max(w, 0.0)
	s = u + v + w
	return (u / s, v / s, w / s) if s > 0 else (1.0, 0.0, 0.0), out


def light_point(mohaa: Mohaa, cands: list, p):
	"""The MOHAA light at p from the candidate triangles, or None."""
	best, best_out = None, None
	for t in cands:
		(u, v, w), out = _clamp_tri(*_bary(*t[2], p))
		if out <= 1e-4:
			return mohaa.sample(t, p)
		if best_out is None or out < best_out:
			best, best_out = (t, (u, v, w)), out
	if best is None:
		return None
	t, (u, v, w) = best
	a, b, c = t[2]
	q = (a[0] * u + b[0] * v + c[0] * w, a[1] * u + b[1] * v + c[1] * w, a[2] * u + b[2] * v + c[2] * w)
	if math.dist(q, p) > NEAR:
		return None
	return mohaa.sample(t, q)


def shift(rgb, gain):
	"""Scale by the gain, keeping the hue when a channel passes 255 (as Q3)."""
	r, g, b = (c * gain for c in rgb)
	m = max(r, g, b)
	if m > 255.0:
		k = 255.0 / m
		r, g, b = r * k, g * k, b * k
	return bytes((int(r + 0.5), int(g + 0.5), int(b + 0.5)))


# ------------------------------------------------------------- GoldSrc side

def _lumps(data: bytes):
	ver = struct.unpack_from("<i", data, 0)[0]
	if ver != 30:
		raise SystemExit(f"expected a BSP30, got version {ver}")
	return [struct.unpack_from("<2i", data, 4 + i * 8) for i in range(BSP30_LUMPS)]


def relight(mohaa: Mohaa, data: bytes, gain: float = DEFAULT_GAIN):
	"""data (a BSP30) with a lighting lump from mohaa. Returns (bytes, stats)."""
	lumps = _lumps(data)

	def lump(i):
		o, n = lumps[i]
		return data[o:o + n]

	planes = [struct.unpack_from("<4f", lump(1), i) for i in range(0, lumps[1][1] - 19, 20)]
	verts = [struct.unpack_from("<3f", lump(3), i) for i in range(0, lumps[3][1] - 11, 12)]
	edges = [struct.unpack_from("<2H", lump(12), i) for i in range(0, lumps[12][1] - 3, 4)]
	sraw = lump(13)
	surfedges = struct.unpack_from("<%di" % (len(sraw) // 4), sraw)
	traw = lump(6)
	texinfo = []
	for i in range(0, len(traw) - 39, 40):
		vecs = struct.unpack_from("<8f", traw, i)
		flags = struct.unpack_from("<i", traw, i + 36)[0]
		texinfo.append((vecs[0:4], vecs[4:8], flags))
	faces = bytearray(lump(7))
	lighting = bytearray()
	st = {"faces": 0, "lit": 0, "luxels": 0, "matched": 0, "near": 0, "fallback": 0}
	for fo in range(0, len(faces) - 19, 20):
		planenum, side, firstedge, numedges, ti = struct.unpack_from("<Hhihh", faces, fo)
		st["faces"] += 1
		if not (0 <= ti < len(texinfo)) or texinfo[ti][2] & TEX_SPECIAL or planenum >= len(planes):
			struct.pack_into("<4Bi", faces, fo + 12, 255, 255, 255, 255, -1)
			continue
		S, T, _flags = texinfo[ti]
		pts = []
		for k in range(numedges):
			se = surfedges[firstedge + k]
			pts.append(verts[edges[se][0] if se >= 0 else edges[-se][1]])
		nx, ny, nz, dist = planes[planenum]
		n = (nx, ny, nz)
		if side:
			n, dist = (-nx, -ny, -nz), -dist
		ss = [_dot(p, S[:3]) + S[3] for p in pts]
		tt = [_dot(p, T[:3]) + T[3] for p in pts]
		bs, bt = math.floor(min(ss) / 16), math.floor(min(tt) / 16)
		w = math.ceil(max(ss) / 16) - bs + 1
		h = math.ceil(max(tt) / 16) - bt + 1
		# Solve P . S = s - S3, P . T = t - T3, P . n = dist for each luxel.
		m = (S[:3], T[:3], n)
		det = _dot(m[0], _cross(m[1], m[2]))
		if abs(det) < 1e-9 or w < 1 or h < 1:
			struct.pack_into("<4Bi", faces, fo + 12, 255, 255, 255, 255, -1)
			continue
		inv = [_cross(m[1], m[2]), _cross(m[2], m[0]), _cross(m[0], m[1])]  # columns / det
		lo = [min(p[a] for p in pts) - NEAR for a in range(3)]
		hi = [max(p[a] for p in pts) + NEAR for a in range(3)]
		cands = mohaa.candidates(n, dist, lo, hi)
		samples = []
		for j in range(h):
			for i in range(w):
				r0 = (bs + i) * 16 - S[3]
				r1 = (bt + j) * 16 - T[3]
				p = tuple((inv[0][a] * r0 + inv[1][a] * r1 + inv[2][a] * dist) / det for a in range(3))
				samples.append(light_point(mohaa, cands, p) if cands else None)
		got = [s for s in samples if s is not None]
		st["luxels"] += len(samples)
		st["matched"] += len(got)
		if got:
			avg = [sum(s[c] for s in got) / len(got) for c in range(3)]
			fill = shift(avg, gain)
		else:
			fill = bytes(FALLBACK)
			st["fallback"] += 1
		struct.pack_into("<4Bi", faces, fo + 12, 0, 255, 255, 255, len(lighting))
		for s in samples:
			lighting += shift(s, gain) if s is not None else fill
		st["lit"] += 1

	fo, _ = lumps[7]
	out = bytearray(data)
	out[fo:fo + len(faces)] = faces
	while len(out) % 4:
		out.append(0)
	struct.pack_into("<2i", out, 4 + LUMP_LIGHTING * 8, len(out), len(lighting))
	out += lighting
	st["lighting_bytes"] = len(lighting)
	return bytes(out), st


def read_source(spec: str) -> bytes:
	if ":" in spec and spec.split(":", 1)[0].lower().endswith(".pk3"):
		arc, member = spec.split(":", 1)
		with zipfile.ZipFile(arc) as z:
			return z.read(member)
	return Path(spec).read_bytes()


def main(argv=None) -> int:
	ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
	ap.add_argument("mohaa", help="the MOHAA BSP (or archive.pk3:maps/name.bsp)")
	ap.add_argument("bsp30", type=Path, help="the converted, compiled BSP30")
	ap.add_argument("-o", "--out", type=Path, help="output BSP30 (default: rewrite bsp30)")
	ap.add_argument("--scale", type=float, default=DEFAULT_SCALE, help="the scale bsp19_to_map.py used")
	ap.add_argument("--gain", type=float, default=DEFAULT_GAIN, help="light multiplier (MOHAA overbright)")
	a = ap.parse_args(argv)
	mohaa = Mohaa(read_source(a.mohaa), a.scale)
	data, st = relight(mohaa, a.bsp30.read_bytes(), a.gain)
	(a.out or a.bsp30).write_bytes(data)
	pct = 100.0 * st["matched"] / max(1, st["luxels"])
	print(f"bsp19_lightmaps: {st['lit']} of {st['faces']} faces lit, {st['luxels']} luxels "
		f"({pct:.1f}% from MOHAA), {st['fallback']} faces with no MOHAA match, "
		f"lighting {st['lighting_bytes']} bytes, {len(mohaa.tris)} MOHAA triangles")
	return 0


if __name__ == "__main__":
	sys.exit(main())
