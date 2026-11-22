#!/usr/bin/env python3
"""world_textures.py: real WAD textures and fitted texture axes, on made-up data (no game data)."""
from __future__ import annotations

import io
import re
import struct
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))

import bsp19_to_map as conv  # noqa: E402
import mohaa_bsp19 as b19  # noqa: E402
import world_textures as wt  # noqa: E402
from test_bsp19_to_map import tiny_bsp  # noqa: E402

try:
	from PIL import Image
except ImportError:  # pragma: no cover
	Image = None

SIDE = re.compile(r"^\( ([^)]*) \) \( ([^)]*) \) \( ([^)]*) \) (\S+) \[ (\S+) (\S+) (\S+) (\S+) \] "
                  r"\[ (\S+) (\S+) (\S+) (\S+) \] (\S+) (\S+) (\S+)$")


def mohaa_st(p):
	"""The made-up MOHAA texturing of the slab top: one repeat per 128 x 256 units, rotated 90 degrees,
	shifted a quarter repeat."""
	return (p[1] / 128.0 + 0.25, -p[0] / 256.0)


def slab_bsp():
	bsp = tiny_bsp([((0, 0, 0), (512, 512, 32), 0)], [])
	# the planar surface MOHAA draws on the slab's top (z = 32), with its st
	pts = [(0.0, 0.0, 32.0), (512.0, 0.0, 32.0), (512.0, 512.0, 32.0), (0.0, 512.0, 32.0)]
	bsp.drawverts = pts
	bsp.drawvert_st = [mohaa_st(p) for p in pts]
	bsp.surfaces = [b19.Surface(shader=0, surface_type=b19.MST_PLANAR, num_verts=4, num_indexes=6,
	                            patch_width=0, patch_height=0, subdivisions=0.0, first_vert=0)]
	return bsp


def pak(path, w=256, h=128):
	img = Image.new("RGB", (w, h))
	for x in range(w):
		for y in range(h):
			img.putpixel((x, y), ((x * 7) % 256, (y * 13) % 256, 90))
	buf = io.BytesIO()
	img.save(buf, "JPEG")
	with zipfile.ZipFile(path, "w") as z:
		z.writestr("textures/concrete.jpg", buf.getvalue())   # no shader script: the shader's own name


@unittest.skipIf(Image is None, "needs Pillow")
class WorldTexturesTest(unittest.TestCase):
	def test_fit_plane_st_recovers_an_affine_map(self):
		n = wt._norm((1.0, 2.0, 3.0))
		e1 = wt._norm(wt._cross(n, (0.0, 0.0, 1.0)))
		e2 = wt._cross(n, e1)
		pts = [tuple(10 * n[i] + x * e1[i] + y * e2[i] for i in range(3)) for x, y in ((0, 0), (90, 5), (30, 70), (-20, 40))]
		a_s, a_t = (0.01, -0.02, 0.005), (0.003, 0.004, -0.01)
		sts = [(wt._dot(p, a_s) + 0.3, wt._dot(p, a_t) - 1.5) for p in pts]
		(fs, bs), (ft, bt) = wt.fit_plane_st(pts, sts, n)
		for p, (s, t) in zip(pts, sts):
			self.assertAlmostEqual(wt._dot(p, fs) + bs, s, places=6)
			self.assertAlmostEqual(wt._dot(p, ft) + bt, t, places=6)
		self.assertIsNone(wt.fit_plane_st(pts[:1] * 3, sts[:1] * 3, n))   # one point spans nothing

	def test_sides_follow_mohaa_texturing(self):
		with tempfile.TemporaryDirectory() as tmp:
			pak(Path(tmp) / "pak0.pk3")
			images = wt.Images([tmp])
			self.assertEqual(images.size("textures/concrete"), (128, 128))   # 256 x 128 capped at 128
			scale = 72.0 / 94.0
			bsp = slab_bsp()
			fit = wt.TextureFit(bsp, images, scale)
			text, namer, stats, _ = conv.convert(bsp, scale, texture_fit=fit)
		self.assertEqual(fit.stats["sides_fitted"], 1)        # the top
		self.assertEqual(fit.stats["sides_projected"], 5)     # the rest keep the projection
		sides = [SIDE.match(l) for l in text.splitlines()]
		sides = [m for m in sides if m and m.group(4) == "concrete"]
		top = [m for m in sides if all(abs(float(p.split()[2]) - 32 * scale) < 0.01 for p in m.group(1, 2, 3))]
		self.assertEqual(len(top), 1)
		m = top[0]
		su = [float(m.group(i)) for i in (5, 6, 7)]
		ss = float(m.group(8))
		tv = [float(m.group(i)) for i in (9, 10, 11)]
		ts = float(m.group(12))
		sk, tk = float(m.group(14)), float(m.group(15))
		for corner in ((0, 0, 32), (512, 0, 32), (512, 512, 32), (100, 300, 32)):
			p_map = [c * scale for c in corner]
			u = sum(a * b for a, b in zip(p_map, su)) / sk + ss          # how SDHLT reads Valve-220
			v = sum(a * b for a, b in zip(p_map, tv)) / tk + ts
			s, t = mohaa_st(corner)
			self.assertAlmostEqual(u, s * 128, delta=0.05)
			self.assertAlmostEqual(v, t * 128, delta=0.05)
		# a projected side gets the texture's density from the fitted surface, not scale 1
		other = [x for x in sides if x is not m][0]
		self.assertNotEqual(float(other.group(14)), 1.0)

	def test_a_slivers_fit_keeps_the_projection(self):
		with tempfile.TemporaryDirectory() as tmp:
			pak(Path(tmp) / "pak0.pk3")
			images = wt.Images([tmp])
			scale = 72.0 / 94.0
			bsp = slab_bsp()
			# s and t run along the same direction: SDHLT would call that alignment malformed
			bsp.drawvert_st = [(p[0] / 128.0, p[0] / 128.0 + p[1] / 4096.0) for p in bsp.drawverts]
			fit = wt.TextureFit(bsp, images, scale)
			conv.convert(bsp, scale, texture_fit=fit)
		self.assertEqual(fit.stats["sides_fitted"], 0)
		self.assertEqual(fit.stats["sides_unfit"], 1)
		self.assertEqual(fit.stats["sides_projected"], 6)

	def test_miptex_and_wad(self):
		with tempfile.TemporaryDirectory() as tmp:
			pak(Path(tmp) / "pak0.pk3", 64, 32)
			images = wt.Images([tmp])
			body = images.miptex("textures/concrete", "concrete")
			self.assertIsNone(images.miptex("textures/missing", "missing"))
			name, w, h, o0, o1, o2, o3 = struct.unpack_from("<16sII4I", body)
			self.assertEqual((name.rstrip(b"\0"), w, h), (b"concrete", 64, 32))
			self.assertEqual((o1 - o0, o2 - o1, o3 - o2), (64 * 32, 32 * 16, 16 * 8))
			end = o3 + 8 * 4
			self.assertEqual(struct.unpack_from("<H", body, end)[0], 256)
			self.assertEqual(len(body), end + 2 + 768 + 2)
			wad = Path(tmp) / "t.wad"
			wt.write_wad(wad, [("concrete", body), ("sky", conv.placeholder_lump("sky"))])
			data = wad.read_bytes()
			magic, count, dir_ofs = struct.unpack_from("<4sii", data)
			self.assertEqual((magic, count), (b"WAD3", 2))
			ofs, ln = struct.unpack_from("<ii", data, dir_ofs)
			self.assertEqual(data[ofs:ofs + ln], body)


if __name__ == "__main__":
	unittest.main()
