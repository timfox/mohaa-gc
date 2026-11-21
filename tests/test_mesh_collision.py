#!/usr/bin/env python3
from __future__ import annotations

import math
import re
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
import make_sample_bsp  # noqa: E402
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
		planes, brushes, sides, nodes = m[:4]
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


def drop(m, x, y, top=400.0):
	"""Feet height where a standing player dropped at (x, y) lands, or None."""
	frac, normal, _ = mc.trace_box(m, (x, y, top), (x, y, -200.0), *PLAYER)
	return None if frac == 1.0 else top + (-200.0 - top) * frac - 36, normal


class TerrainPatchMeshTest(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.bsp = b19.load_bytes(make_sample_bsp.build(19), "sample")

	def mesh(self, **kw):
		col = mc.Collision()
		_, _, stats, _ = conv.convert(self.bsp, scale=1.0, mesh=col, mesh_angled=False, **kw)
		return roundtrip(col), stats

	def test_off_by_default(self):
		col = mc.Collision()
		conv.convert(self.bsp, scale=1.0, mesh=col)
		self.assertEqual(col.brushes, [])

	def test_terrain_heights(self):
		m, stats = self.mesh(mesh_terrain=True)
		self.assertEqual(stats["mesh_terrain_patches"], 3)
		# flat patch at x,y -1024..-512 (cells of 64, patch at -16,-16): ground z = 0
		feet, n = drop(m, -768, -768)
		self.assertAlmostEqual(feet, 0.0, delta=0.1)
		self.assertEqual(n[2], 1.0)
		# planar slope patch at x -512..0: z = base + 2 * (4 * i) = x_in_patch / 8. The box spans
		# 16 units either side, so the uphill corner carries the feet.
		feet, n = drop(m, -256, -768)
		self.assertAlmostEqual(feet, (256 + 16) / 8.0, delta=0.1)
		self.assertGreater(n[2], 0.99)

	def test_bumpy_terrain_is_exact(self):
		m, stats = self.mesh(mesh_terrain=True)
		tp = self.bsp.terrain[2]
		x0, y0 = tp.origin
		for i, j in ((3, 3), (4, 5), (6, 2)):
			x, y = x0 + 64 * i, y0 + 64 * j
			feet, _ = drop(m, x, y)
			# the box reaches 16 units around the sample, so it rests on the highest ground there:
			# at least the sample itself, at most the highest of the 3 x 3 samples around it
			around = [tp.heights[(j + dj) * 9 + i + di] for dj in (-1, 0, 1) for di in (-1, 0, 1)]
			self.assertGreaterEqual(feet, tp.heights[j * 9 + i] - 0.05)
			self.assertLessEqual(feet, max(around) + 0.05)

	def test_spawn_on_terrain_is_lifted_clear(self):
		import copy
		bsp = copy.copy(self.bsp)
		tp = bsp.terrain[2]
		x, y = tp.origin[0] + 64 * 4, tp.origin[1] + 64 * 4
		# MOHAA puts the origin at the feet, on the sample; the box corners dip into higher ground
		bsp.entities = [dict(e) for e in self.bsp.entities]
		for e in bsp.entities:
			if e.get("classname") == "info_player_allied":
				e["origin"] = f"{x} {y} {tp.heights[4 * 9 + 4]}"
		col = mc.Collision()
		text, _, stats, _ = conv.convert(bsp, scale=1.0, mesh=col, mesh_angled=False, mesh_terrain=True)
		self.assertEqual(stats["player_starts_lifted"], 1)
		self.assertEqual(stats["player_starts_stuck"], 0)
		m = roundtrip(col)
		origin = re.search(r'"classname" "info_player_allies"\n"origin" "([^"]+)"', text)
		if origin is None:
			origin = re.search(r'"origin" "([^"]+)"\n"classname" "info_player_allies"', text)
		ox, oy, oz = map(float, origin.group(1).split())
		self.assertFalse(mc.trace_box(m, (ox, oy, oz), (ox, oy, oz), *PLAYER)[2])
		# and it stands on the ground, not in the air
		self.assertLess(mc.trace_box(m, (ox, oy, oz), (ox, oy, oz - 4), *PLAYER)[0], 1.0)

	def test_solid_patch_collides_nonsolid_does_not(self):
		m, stats = self.mesh(mesh_patch_tol=1.0)
		self.assertEqual(stats["mesh_patches"], 1)
		self.assertEqual(stats["mesh_patches_nonsolid"], 1)
		# top of the hump: the joint control point at x = 428 lies on the surface, z = 64
		feet, n = drop(m, 428, 364)
		self.assertAlmostEqual(feet, 64.0, delta=1.0)
		self.assertGreater(n[2], 0.95)
		self.assertIsNone(drop(m, 664, 364)[0])  # vines: non-solid

	def test_patch_tessellation_error(self):
		row = [(0, 0), (64, 128), (128, 0)]
		ctrl = [(x, 64 * j, z) for j in range(3) for x, z in row]
		tris = conv.patch_triangles(ctrl, 3, 3, 1.0)
		self.assertGreater(len(tris), 8)
		# every vertex lies on the curve x = 128 t, z = 256 t (1 - t)
		for tri in tris:
			for x, _, z in tri:
				t = x / 128.0
				self.assertAlmostEqual(z, 2 * t * (1 - t) * 128, places=4)
		# and the chords stay within about the tolerance of the curve
		xs = sorted({round(p[0], 6) for tri in tris for p in tri})
		for a, b in zip(xs, xs[1:]):
			t = (a + b) / 256.0
			za = 2 * (a / 128) * (1 - a / 128) * 128
			zb = 2 * (b / 128) * (1 - b / 128) * 128
			self.assertLess(abs(2 * t * (1 - t) * 128 - (za + zb) / 2), 1.5)

	def test_prism_planes_contain_triangle(self):
		a, b, c = (0, 0, 0), (64, 0, 0), (0, 64, 32)
		_, _, planes = mc.triangle_prism(a, b, c)
		self.assertEqual(len(planes), 5)
		centroid = tuple((a[k] + b[k] + c[k]) / 3 for k in range(3))
		for n, d in planes:
			self.assertLessEqual(mc._dot(n, centroid) - d, 1e-6)
		self.assertIsNone(mc.triangle_prism(a, a, c))


if __name__ == "__main__":
	unittest.main()
