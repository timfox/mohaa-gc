#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))

import bsp19_to_map as conv  # noqa: E402
import mesh_collision as mc  # noqa: E402
from test_bsp19_to_map import box_planes, tiny_bsp  # noqa: E402
import mohaa_bsp19 as b19  # noqa: E402

PLAYER = ((-16.0, -16.0, -36.0), (16.0, 16.0, 36.0))


def ramp_brush():
	"""A 45-degree ramp rising along +x: floor 0..256 in x, top plane z = x."""
	s = 2 ** -0.5
	planes = box_planes((0, -128, 0), (256, 128, 256))
	planes.append(((-s, 0.0, s), 0.0, None))  # solid below z = x
	return conv.brush_faces(planes)


def roundtrip(col):
	with tempfile.TemporaryDirectory() as d:
		p = Path(d) / "t.mcol"
		col.write(p)
		return mc.read(p)


class MeshCollisionTest(unittest.TestCase):
	def test_box_hit_and_miss(self):
		col = mc.Collision()
		faces = conv.brush_faces(box_planes((0, 0, 0), (64, 64, 64)))
		col.add_brush([(n, d) for n, d, _, _ in faces], [p for _, _, w, _ in faces for p in w])
		m = roundtrip(col)
		frac, normal, solid = mc.trace_box(m, (-100, 32, 32), (100, 32, 32), *PLAYER)
		# box face at x=0, player half-width 16: stops at x = -16 - epsilon
		self.assertAlmostEqual(-100 + 200 * frac, -16 - mc.DIST_EPSILON, places=2)
		self.assertEqual(normal, (-1.0, 0.0, 0.0))
		self.assertFalse(solid)
		frac, _, _ = mc.trace_box(m, (-100, 200, 32), (100, 200, 32), *PLAYER)
		self.assertEqual(frac, 1.0)

	def test_ramp_is_exact_not_stepped(self):
		col = mc.Collision()
		faces = ramp_brush()
		col.add_brush([(n, d) for n, d, _, _ in faces], [p for _, _, w, _ in faces for p in w])
		m = roundtrip(col)
		# drop the player onto the ramp at x=128: the box spans x 112..144, so the
		# ramp's highest point under it (x=144) carries the feet at z=144, not a voxel step
		frac, normal, _ = mc.trace_box(m, (128, 0, 400), (128, 0, 0), *PLAYER)
		feet = 400 - 400 * frac - 36
		self.assertAlmostEqual(feet, 144, delta=0.2)
		self.assertAlmostEqual(normal[2], 2 ** -0.5, places=4)

	def test_bvh_many_brushes(self):
		col = mc.Collision()
		for i in range(50):
			faces = conv.brush_faces(box_planes((i * 100, 0, 0), (i * 100 + 32, 32, 32)))
			col.add_brush([(n, d) for n, d, _, _ in faces], [p for _, _, w, _ in faces for p in w])
		m = roundtrip(col)
		planes, brushes, sides, nodes = m
		self.assertEqual(len(brushes), 50)
		for k in (0, 17, 49):
			frac, _, _ = mc.trace_box(m, (k * 100 + 16, 16, 300), (k * 100 + 16, 16, 0), *PLAYER)
			self.assertLess(frac, 1.0)
		frac, _, _ = mc.trace_box(m, (17 * 100 + 66, 16, 300), (17 * 100 + 66, 16, 0), *PLAYER)
		self.assertEqual(frac, 1.0)
		for mins, maxs, a, b in nodes:
			if b == 0:
				self.assertLess(a + 1, len(nodes))

	def test_converter_routes_angled_detail_to_mesh(self):
		s2 = 2 ** -0.5
		bsp = tiny_bsp([((0, 0, 0), (64, 64, 64), 0)], [])
		bsp.planes[0] = (s2, s2, 0.0, 64 * s2 * 1.5)
		bsp.shaders[0].content_flags |= b19.CONTENTS_DETAIL
		col = mc.Collision()
		text, _, stats, _ = conv.convert(bsp, scale=1.0, simplify_collision=True, mesh=col)
		self.assertEqual(stats["collision_mesh"], 1)
		self.assertEqual(stats["collision_boxes"], 0)
		self.assertEqual(len(col.brushes), 1)
		self.assertNotIn(" CLIP [", text)


if __name__ == "__main__":
	unittest.main()
