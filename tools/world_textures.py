#!/usr/bin/env python3
"""Real textures for converted maps: a WAD3 of MOHAA's own images, and texture axes that match MOHAA's.

bsp19_to_map.py --textures MAIN uses this. Without it the map gets flat placeholder checkers on
box-projected axes. With it:

  * every drawn shader's first image stage (scripts/*.shader, else the shader's own name as .tga/.jpg)
    is read from the user's paks, resized to power-of-two sides of at most --texture-size (128), and
    written to the .wad with a 256-colour palette and four mip levels, under bsp19_to_map's WAD names.
    SDHLT embeds it (-wadinclude), so the compiled map carries its textures.
  * each brush side's Valve-220 texture axes are fitted to the MOHAA surface drawn on that side: Quake 3
    brush sides have no texture axes, but the planar draw surfaces carry per-vertex st. A least-squares
    fit of the surface's xyz to st (times the WAD texture's size) gives the axes and shifts, so the
    textures sit where MOHAA draws them. Sides with no such surface keep the box projection, scaled to
    the texture's density on the rest of the map.

Runs on the user's own install (bring your own data): nothing retail is kept in this repo.
"""
from __future__ import annotations

import io
import math
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mohaa_bsp19 as b19  # noqa: E402
import mohaa_skd as skd  # noqa: E402

TEXTURE_SIZE = 128   # largest WAD side: about one texel per map unit, as the placeholders had
PLANE_DOT = 0.995    # normals this close are one plane
PLANE_DIST = 1.0     # MOHAA units
MIPS = 4
MAX_AXIS_COS = 0.5   # fitted S and T axes closer than 60 degrees: a sliver's fit, kept projected instead
MIN_DENSITY, MAX_DENSITY = 1.0 / 16, 8.0   # texels per map unit a side may get


def _dot(a, b):
	return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _sub(a, b):
	return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a, b):
	return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _norm(v):
	ln = math.sqrt(_dot(v, v))
	return (v[0] / ln, v[1] / ln, v[2] / ln) if ln > 1e-9 else (0.0, 0.0, 0.0)


def _pow2_at_most(n, cap):
	p = 1
	while p * 2 <= min(n, cap):
		p *= 2
	return p


class Images:
	"""The user's MOHAA textures: shader name -> image, size and WAD encoding."""

	def __init__(self, inputs, max_side: int = TEXTURE_SIZE):
		from ubersound import collect, read
		self.read = read
		self.max_side = max_side
		self.files = collect(inputs, (".shader", ".tga", ".jpg", ".png"))
		self.shaders = {}
		for p, e in sorted(self.files.items()):
			if p.endswith(".shader"):
				self.shaders.update(skd.parse_shaders(read(e).decode("latin-1")))
		self._size = {}

	def image(self, shader: str):
		"""The shader's image bytes, or None."""
		name = shader.replace("\\", "/").lower()
		path = self.shaders.get(name) or name
		base = path.rsplit(".", 1)[0] if "." in path.rsplit("/", 1)[-1] else path
		for cand in (path, base + ".tga", base + ".jpg", base + ".png"):
			if cand in self.files:
				return self.read(self.files[cand])
		return None

	def size(self, shader: str):
		"""(width, height) the shader's WAD texture gets, or None if it has no image."""
		if shader not in self._size:
			from PIL import Image
			data = self.image(shader)
			got = None
			if data is not None:
				try:
					w, h = Image.open(io.BytesIO(data)).size
					got = (_pow2_at_most(w, self.max_side), _pow2_at_most(h, self.max_side))
				except OSError:
					got = None
			self._size[shader] = got
		return self._size[shader]

	def miptex(self, shader: str, name: str):
		"""A WAD3 miptex lump (four mip levels, 256-colour palette) for the shader, or None."""
		from PIL import Image
		data = self.image(shader)
		size = self.size(shader)
		if data is None or size is None:
			return None
		w, h = size
		img = Image.open(io.BytesIO(data)).convert("RGB").resize((w, h), Image.LANCZOS)
		pal_img = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
		mips = [pal_img.tobytes()]
		for level in range(1, MIPS):
			small = img.resize((max(1, w >> level), max(1, h >> level)), Image.LANCZOS)
			mips.append(small.quantize(palette=pal_img, dither=Image.Dither.NONE).tobytes())
		pal = bytes((pal_img.getpalette() or [])[:768]).ljust(768, b"\0")
		return miptex_lump(name, w, h, mips, pal)


def miptex_lump(name: str, w: int, h: int, mips, palette: bytes) -> bytes:
	header = 16 + 4 + 4 + 16
	offsets, pos = [], header
	for m in mips:
		offsets.append(pos)
		pos += len(m)
	return (struct.pack("<16sII4I", name.encode()[:15], w, h, *offsets) + b"".join(mips)
	        + struct.pack("<H", 256) + palette + b"\x00\x00")


def write_wad(path, lumps):
	"""A WAD3 of [(name, miptex lump)]."""
	out = bytearray(b"WAD3" + struct.pack("<ii", len(lumps), 0))
	entries = []
	for name, body in lumps:
		entries.append((len(out), len(body), name))
		out += body
	dir_ofs = len(out)
	for ofs, ln, name in entries:
		out += struct.pack("<iiibbh16s", ofs, ln, ln, 0x43, 0, 0, name.encode()[:15])
	struct.pack_into("<i", out, 8, dir_ofs)
	Path(path).write_bytes(bytes(out))


def fit_plane_st(points, sts, n):
	"""((a, b) for s, (a, b) for t): s = a . p + b over the points on the plane with normal n, by least
	squares in a 2D basis of the plane. None if the points don't span the plane."""
	e1 = _norm(_cross(n, (0.0, 0.0, 1.0) if abs(n[2]) < 0.9 else (1.0, 0.0, 0.0)))
	e2 = _cross(n, e1)
	p0 = points[0]
	xs = [(_dot(_sub(p, p0), e1), _dot(_sub(p, p0), e2)) for p in points]
	# normal equations for [x y 1] c = u
	sxx = sum(x * x for x, _ in xs)
	sxy = sum(x * y for x, y in xs)
	syy = sum(y * y for _, y in xs)
	sx = sum(x for x, _ in xs)
	sy = sum(y for _, y in xs)
	k = float(len(xs))
	m = ((sxx, sxy, sx), (sxy, syy, sy), (sx, sy, k))
	det = (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
	       + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
	if abs(det) < 1e-6 * max(1.0, sxx * syy):
		return None
	out = []
	for comp in (0, 1):
		u = [st[comp] for st in sts]
		r = (sum(x * v for (x, _), v in zip(xs, u)), sum(y * v for (_, y), v in zip(xs, u)), sum(u))
		c = []
		for col in range(3):   # Cramer's rule
			mm = [list(row) for row in m]
			for row in range(3):
				mm[row][col] = r[row]
			c.append((mm[0][0] * (mm[1][1] * mm[2][2] - mm[1][2] * mm[2][1])
			          - mm[0][1] * (mm[1][0] * mm[2][2] - mm[1][2] * mm[2][0])
			          + mm[0][2] * (mm[1][0] * mm[2][1] - mm[1][1] * mm[2][0])) / det)
		a = tuple(c[0] * e1[i] + c[1] * e2[i] for i in range(3))
		out.append((a, c[2] - _dot(a, p0)))
	return tuple(out)


class TextureFit:
	"""Valve-220 texture axes for brush sides, from the MOHAA surfaces drawn on them."""

	def __init__(self, bsp: b19.Bsp, images: Images, scale: float):
		self.images, self.scale = images, scale
		self.by_shader = {}   # shader name -> [(n, dist, lo, hi, ((a, b), (a, b)) in MOHAA units and 0..1 st)]
		self.stats = {"sides_fitted": 0, "sides_projected": 0, "sides_unfit": 0, "surfaces": 0}
		for sf in bsp.surfaces:
			if sf.surface_type != b19.MST_PLANAR or sf.num_verts < 3 or not 0 <= sf.shader < len(bsp.shaders):
				continue
			pts = bsp.drawverts[sf.first_vert:sf.first_vert + sf.num_verts]
			sts = bsp.drawvert_st[sf.first_vert:sf.first_vert + sf.num_verts]
			n = (0.0, 0.0, 0.0)
			for i in range(len(pts)):   # Newell
				a, b = pts[i], pts[(i + 1) % len(pts)]
				n = (n[0] + (a[1] - b[1]) * (a[2] + b[2]), n[1] + (a[2] - b[2]) * (a[0] + b[0]),
				     n[2] + (a[0] - b[0]) * (a[1] + b[1]))
			n = _norm(n)
			if n == (0.0, 0.0, 0.0):
				continue
			fit = fit_plane_st(pts, sts, n)
			if fit is None:
				continue
			lo = tuple(min(p[i] for p in pts) for i in range(3))
			hi = tuple(max(p[i] for p in pts) for i in range(3))
			name = bsp.shaders[sf.shader].name.lower()
			self.by_shader.setdefault(name, []).append((n, _dot(n, pts[0]), lo, hi, fit))
			self.stats["surfaces"] += 1
		self._density = {}

	def _pick(self, shader, n, dist, lo, hi):
		best, best_d = None, None
		for sn, sd, slo, shi, fit in self.by_shader.get(shader, ()):
			if _dot(sn, n) < PLANE_DOT or abs(sd - dist) > PLANE_DIST:
				continue
			# the surface overlapping the side wins; else the nearest one on the plane (same tiling)
			gap = sum(max(0.0, slo[i] - hi[i], lo[i] - shi[i]) for i in range(3))
			if best is None or gap < best_d:
				best, best_d = fit, gap
		return best

	def density(self, shader):
		"""Texels per MOHAA unit along s and t on this shader's other surfaces (for projected sides)."""
		if shader not in self._density:
			got = None
			for _, _, _, _, ((a_s, _), (a_t, _)) in self.by_shader.get(shader, ()):
				got = (math.sqrt(_dot(a_s, a_s)), math.sqrt(_dot(a_t, a_t)))
				break
			self._density[shader] = got
		return self._density[shader]

	def axes(self, shader: str, n, d_gs, winding_gs, offset, base_axes):
		"""(S axis, S shift, T axis, T shift, S scale, T scale) for a Valve-220 side in map units, or None to
		keep the caller's projection. n is the side's normal, d_gs its distance and winding_gs its corners in
		map units; offset is the brush's MOHAA offset (entity origin) and base_axes the box projection."""
		shader = shader.lower()
		size = self.images.size(shader)
		if size is None:
			return None
		w, h = size
		sc = self.scale
		local = [(p[0] / sc - offset[0], p[1] / sc - offset[1], p[2] / sc - offset[2]) for p in winding_gs]
		lo = tuple(min(p[i] for p in local) for i in range(3))
		hi = tuple(max(p[i] for p in local) for i in range(3))
		fit = self._pick(shader, n, d_gs / sc - _dot(n, offset), lo, hi)
		got = self._fitted(fit, w, h, offset) if fit is not None else None
		if got is not None:
			self.stats["sides_fitted"] += 1
			return got
		if fit is not None:
			self.stats["sides_unfit"] += 1
		self.stats["sides_projected"] += 1
		dens = self.density(shader)
		if dens is None:
			return None
		(u, v) = base_axes
		# keep the box projection, at the texture's density on the rest of the map
		ds = min(MAX_DENSITY, max(MIN_DENSITY, dens[0] * w / sc))
		dt = min(MAX_DENSITY, max(MIN_DENSITY, dens[1] * h / sc))
		return (u, 0.0, v, 0.0, 1.0 / ds, 1.0 / dt)

	def _fitted(self, fit, w, h, offset):
		"""The Valve-220 axes for a fitted surface, or None if they would make SDHLT's texture alignment
		malformed: S and T nearly parallel (a sliver's fit), or texels far too dense or sparse."""
		sc = self.scale
		out = []
		for (a, b), texels in zip(fit, (w, h)):
			# MOHAA: s = a . p_local + b (0..1 per repeat); map: texel = s * texels, p_local = p_map / sc - offset
			a_map = tuple(c * texels / sc for c in a)
			shift = (b - _dot(a, offset)) * texels
			k = math.sqrt(_dot(a_map, a_map))
			if k < 1e-9:
				return None
			out.append((tuple(c / k for c in a_map), shift, 1.0 / k))
		(su, ss, sk), (tu, ts, tk) = out
		if abs(_dot(su, tu)) > MAX_AXIS_COS:
			return None
		if not all(MIN_DENSITY <= 1.0 / k <= MAX_DENSITY for k in (sk, tk)):
			return None
		return (su, ss, tu, ts, sk, tk)
