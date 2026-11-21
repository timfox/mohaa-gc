#!/usr/bin/env python3
from __future__ import annotations

import re
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))

import bsp19_to_map as conv  # noqa: E402
import make_sample_bsp  # noqa: E402
import mohaa_bsp19 as b19  # noqa: E402

FACE_RE = re.compile(r"^\( ([^)]*) \) \( ([^)]*) \) \( ([^)]*) \) (\S+) \[")


def box_planes(lo, hi):
	out = []
	for ax in range(3):
		for sign in (1, -1):
			n = [0.0, 0.0, 0.0]
			n[ax] = float(sign)
			out.append((tuple(n), hi[ax] if sign > 0 else -lo[ax], None))
	return out


class GeometryTest(unittest.TestCase):
	def test_box_faces_and_orientation(self):
		faces = conv.brush_faces(box_planes((0, 0, 0), (64, 32, 16)))
		self.assertEqual(len(faces), 6)
		for n, d, w, _ in faces:
			self.assertEqual(len(w), 4)
			for p in w:
				self.assertAlmostEqual(conv._dot(p, n), d, places=3)
			p0, p1, p2 = conv.three_points(n, w)
			normal = conv._cross(conv._sub(p0, p1), conv._sub(p2, p1))
			self.assertGreater(conv._dot(normal, n), 0)  # Quake/SDHLT plane-from-points rule

	def test_bevel_and_duplicate_planes_dropped(self):
		planes = box_planes((0, 0, 0), (64, 64, 64))
		planes.append(planes[0])  # duplicate
		s = 2 ** -0.5
		planes.append(((s, s, 0.0), 64 * 2 * s, None))  # touches only the corner edge: zero-area bevel
		faces = conv.brush_faces(planes)
		self.assertEqual(len(faces), 6)


def tiny_bsp(world_boxes, door_boxes, door_class="func_rotatingdoor"):
	"""In-memory Bsp: shader 0 = concrete, 1 = sky. Boxes are (lo, hi, side_shader)."""
	bsp = b19.Bsp("tiny", 19, 0, 0, {})
	bsp.shaders = [b19.Shader("textures/concrete", 0, b19.CONTENTS_SOLID, 0),
	               b19.Shader("textures/sky/sky1", b19.SURF_SKY, b19.CONTENTS_SOLID, 0)]

	def add(boxes):
		first = len(bsp.brushes)
		for lo, hi, sh in boxes:
			fs = len(bsp.brushsides)
			for n, d, _ in box_planes(lo, hi):
				bsp.planes.append((*n, d))
				bsp.brushsides.append((len(bsp.planes) - 1, sh))
			bsp.brushes.append(b19.Brush(fs, 6, 0))
		return first, len(boxes)

	for boxes in (world_boxes, door_boxes):
		fb, nb = add(boxes)
		bsp.models.append(b19.Model((-512, -512, -512), (512, 512, 512), 0, 0, fb, nb))
	bsp.entities = [{"classname": "worldspawn"},
	                {"classname": door_class, "model": "*1", "origin": "0 0 0"},
	                {"classname": "info_player_allied", "origin": "0 0 16"}]
	return bsp


class CompileSafetyTest(unittest.TestCase):
	"""Failures seen when compiling the retail maps with SDHLT."""

	def test_thin_brush_dropped(self):
		bsp = tiny_bsp([((0, 0, 0), (64, 64, 0.03), 0), ((0, 0, 0), (64, 64, 64), 0)], [])
		text, _, stats, _ = conv.convert(bsp, scale=1.0)
		self.assertEqual(stats["brushes_too_thin"], 1)
		self.assertEqual(stats["world_brushes_written"], 1)

	def test_near_coplanar_side_dropped(self):
		stats = conv.Counter()
		sides = [(conv.three_points(n, w), "X") for n, d, w, _ in conv.brush_faces(box_planes((0, 0, 0), (64, 64, 64)))]
		top = next(pts for pts, _ in sides if conv.csg_plane(*pts)[0] == (0.0, 0.0, 1.0))
		sides.append((tuple((x, y, z + 0.01) for x, y, z in top), "X"))  # rounds onto the same sdHLCSG plane
		kept = conv.csg_safe_sides(sides, stats)
		self.assertEqual(len(kept), 6)
		self.assertEqual(stats["sides_coplanar_dropped"], 1)

	def test_runaway_brush_dropped(self):
		bsp = tiny_bsp([((-80000, 0, 0), (80000, 1, 1), 0), ((0, 0, 0), (64, 64, 64), 0)], [])
		_, _, stats, _ = conv.convert(bsp, scale=1.0)
		self.assertEqual(stats["brushes_outside_world"], 1)
		self.assertEqual(stats["world_brushes_written"], 1)

	def test_one_unit_beam_thickened(self):
		bsp = tiny_bsp([((-2000, 5351, 12), (2000, 5352, 13), 0), ((0, 0, 0), (64, 64, 64), 0)], [])
		text, _, stats, _ = conv.convert(bsp, scale=1.0)
		self.assertEqual(stats["brushes_thickened"], 1)
		self.assertEqual(stats["world_brushes_written"], 2)
		self.assertIn("5350.9", text)  # pushed out by (1.1 - 1) / 2 + 0.05 = 0.1 per side
		self.assertIn("5352.1", text)

	def test_sliver_with_tiny_caps_stays_closed(self):
		# m2l1: a 0.06-thick strip whose end caps fall under the face-area cutoff. Growing
		# only the faces that survived left a 4-sided prism SDHLT clipped to +/-80000.
		bsp = tiny_bsp([((-2000, 5351, 12), (2000, 5351.06, 13.2), 0), ((0, 0, 0), (64, 64, 64), 0)], [])
		text, _, stats, _ = conv.convert(bsp, scale=1.0)
		self.assertEqual(stats["brushes_thickened"], 1)
		self.assertEqual(stats["brushes_outside_world"], 0)
		sliver = text.split("{")[2].split("}")[0]
		self.assertEqual(len([l for l in sliver.splitlines() if l.startswith("(")]), 6)

	def test_thin_detail_goes_to_func_wall(self):
		bsp = tiny_bsp([((0, 0, 0), (64, 64, 0.5), 0), ((3000, 0, 0), (3064, 0.5, 64), 0),
		                ((0, 0, 100), (64, 64, 164), 0)], [])
		bsp.shaders[0].content_flags |= b19.CONTENTS_DETAIL
		text, _, stats, _ = conv.convert(bsp, scale=1.0)
		self.assertEqual(stats["thin_detail_to_wall"], 2)
		self.assertEqual(stats["thin_detail_walls"], 2)  # different 1024-unit cells
		self.assertEqual(text.count('"classname" "func_wall"'), 2)
		self.assertIn("func_detail", text)  # the thick brush stays detail
		self.assertEqual(text.count('"zhlt_noclip" "1"'), 2)
		world = text.split('"classname" "func_detail"')[0]
		self.assertEqual(world.count(" CLIP ["), 12)  # both slivers collide via world CLIP copies
		text, _, stats, _ = conv.convert(bsp, scale=1.0, thin_walls=False)
		self.assertEqual(stats["thin_detail_to_wall"], 0)
		self.assertNotIn('"func_wall"', text)

	def test_anisotropic_collision_grid(self):
		s = 2 ** -0.5
		planes = box_planes((0, 0, 0), (128, 128, 64))
		planes.append(((s, 0.0, s), 96 * s, None))  # a 45-degree ramp face
		faces = conv.brush_faces(planes)
		fine, coarse = set(), set()
		conv.voxelize_brush(faces, fine, 16)
		conv.voxelize_brush(faces, coarse, (64, 16))
		stats = conv.Counter()
		boxes = conv.voxel_boxes(coarse, (64, 16), stats)
		self.assertLess(len(coarse), len(fine))
		zs = {float(m) for b in boxes for m in re.findall(r"\( \S+ \S+ (\S+) \)", b)}
		self.assertTrue(all(z % 16 == 0 for z in zs))  # steps stay one 16-unit cell high

	def test_rain_volume_is_nonsolid(self):
		bsp = tiny_bsp([((0, 0, 0), (64, 64, 64), 0)], [((0, 0, 100), (64, 64, 164), 0)], door_class="func_rain")
		text, _, _, _ = conv.convert(bsp, scale=1.0)
		self.assertIn('"classname" "func_illusionary"', text)
		self.assertIn('"zhlt_noclip" "1"', text)

	def test_detail_walls(self):
		bsp = tiny_bsp([((0, 0, 0), (64, 64, 64), 0), ((2000, 0, 0), (2064, 64, 64), 0)], [])
		bsp.shaders[0].content_flags |= b19.CONTENTS_DETAIL
		text, _, stats, _ = conv.convert(bsp, scale=1.0, detail_walls=True)
		self.assertEqual(stats["detail_to_wall"], 2)
		self.assertNotIn("func_detail", text)
		self.assertEqual(text.count('"classname" "func_wall"'), 2)
		world = text.split('"classname" "func_wall"')[0]
		self.assertEqual(world.count(" CLIP ["), 12)

	def test_angled_sky_detail_stays_in_world_under_simplify(self):
		# m5l3: an angled detail brush with one sky face ended up in the noclip func_detail.
		s2 = 2 ** -0.5
		bsp = tiny_bsp([((0, 0, 0), (64, 64, 64), 1)], [])
		bsp.planes[0] = (s2, s2, 0.0, 64 * s2 * 1.5)  # tilt the +x side
		bsp.shaders[0].content_flags |= b19.CONTENTS_DETAIL
		for walls in (False, True):
			text, _, stats, _ = conv.convert(bsp, scale=1.0, simplify_collision=True, detail_walls=walls)
			self.assertEqual(stats["detail_sky_to_world"], 1)
			self.assertNotIn("func_detail", text)
			self.assertNotIn("func_wall", text)

	def test_tilted_near_coplanar_side_dropped(self):
		# sdHLCSG tests the new side's first point against the old plane, not the distances
		stats = conv.Counter()
		sides = [(conv.three_points(n, w), "X") for n, d, w, _ in conv.brush_faces(box_planes((0, 0, 0), (64, 64, 64)))]
		top = next(pts for pts, _ in sides if conv.csg_plane(*pts)[0] == (0.0, 0.0, 1.0))
		tilted = ((0, 0, 64), (0, 64, 64.006), (64, 64, 64.006))  # normal off by < DIR_EPSILON
		sides.append((tilted, "X"))
		self.assertEqual(len(conv.csg_safe_sides(sides, stats)), 6)
		self.assertEqual(stats["sides_coplanar_dropped"], 1)

	def test_detail_sky_brush_moves_to_world(self):
		bsp = tiny_bsp([((0, 0, 0), (64, 64, 64), 1)], [])
		bsp.shaders[0].content_flags |= b19.CONTENTS_DETAIL  # brush contents come from shader 0
		text, _, stats, _ = conv.convert(bsp, scale=1.0)
		self.assertEqual(stats["detail_sky_to_world"], 1)
		self.assertNotIn("func_detail", text)

	def test_terrain_seal_columns(self):
		bsp = b19.load_bytes(make_sample_bsp.build(19), "sample")
		text, _, stats, _ = conv.convert(bsp, scale=1.0)
		self.assertEqual(stats["terrain_seal_brushes"], len(bsp.terrain))
		floor = min(min(tp.heights) for tp in bsp.terrain) - 24
		_, _, s2, _ = conv.convert(bsp, scale=1.0, terrain_seal=False)
		self.assertEqual(s2["terrain_seal_brushes"], 0)
		self.assertIn(f" {floor} )", text.replace(".0 )", " )"))

	def test_detail_world_and_seal_box(self):
		bsp = tiny_bsp([((0, 0, 0), (64, 64, 64), 0)], [])
		bsp.shaders[0].content_flags |= b19.CONTENTS_DETAIL
		self.assertIn("func_detail", conv.convert(bsp, scale=1.0)[0])
		text, _, stats, _ = conv.convert(bsp, scale=1.0, detail_world=True, seal_box=True)
		self.assertNotIn("func_detail", text)
		self.assertEqual(stats["seal_box_brushes"], 6)
		self.assertIn("-784", text)  # model mins -512 minus 256 margin minus 16 wall

	def test_simplify_collision_kdop_proxy(self):
		import math
		bsp = tiny_bsp([((0, 0, 0), (64, 64, 64), 0)], [])
		bsp.shaders[0].content_flags |= b19.CONTENTS_DETAIL
		# rotate the box 30 degrees about z: four angled sides
		c, s_ = math.cos(math.radians(30)), math.sin(math.radians(30))
		for k, (nx, ny, nz, d) in enumerate(bsp.planes):
			bsp.planes[k] = (nx * c - ny * s_, nx * s_ + ny * c, nz, d)
		text, _, stats, _ = conv.convert(bsp, scale=1.0, simplify_collision=True)
		self.assertEqual(stats["detail_noclip"], 1)
		self.assertIn('"zhlt_noclip" "1"', text)
		self.assertGreater(stats["collision_voxels"], 0)
		self.assertLess(stats["collision_boxes"], stats["collision_voxels"])
		# the rotated 64 box spans about 87 units: 6 x 6 cells of 16 cover it, 4 high
		self.assertLessEqual(stats["collision_voxels"], 6 * 6 * 4)
		vox = set()
		conv.voxelize_brush(conv.brush_faces(box_planes((0, 0, 0), (32, 2, 32))), vox, 16.0)
		self.assertEqual(len(vox), 4)  # a 2-unit sliver still fills its cells
		# axial brushes are left alone
		plain = tiny_bsp([((0, 0, 0), (64, 64, 64), 0)], [])
		plain.shaders[0].content_flags |= b19.CONTENTS_DETAIL
		_, _, s2, _ = conv.convert(plain, scale=1.0, simplify_collision=True)
		self.assertEqual(s2["collision_voxels"], 0)

	def test_entity_sky_becomes_null_and_origin_in_wad(self):
		bsp = tiny_bsp([((0, 0, 0), (64, 64, 64), 1)], [((100, 0, 0), (110, 64, 64), 1)])
		text, namer, _, _ = conv.convert(bsp, scale=1.0)
		ent = text.split('"classname" "func_door_rotating"')[1]
		self.assertNotIn(" sky ", ent)
		self.assertIn(" NULL ", ent)
		self.assertIn(" sky ", text.split('"classname" "func_door_rotating"')[0])  # world keeps sky
		self.assertIn("ORIGIN", namer.special_used)


class TerrainTest(unittest.TestCase):
	def test_wedge_brush(self):
		txt = conv.wedge_brush((0, 0, 10), (64, 0, 20), (0, 64, 30), 16, "NULL", "NULL")
		lines = [l for l in txt.splitlines() if l.startswith("(")]
		self.assertEqual(len(lines), 5)  # top, bottom, three sides

	def test_terrain_brush_counts(self):
		bsp = b19.load_bytes(make_sample_bsp.build(19), "sample")
		text, _, stats, _ = conv.convert(bsp, scale=1.0, terrain=True, terrain_tol=8)
		# flat + sloped patches -> one 512 cell (2 wedges) each; bumpy patch -> 8x8 cells
		self.assertEqual(stats["terrain_patches_cell_512"], 2)
		self.assertEqual(stats["terrain_brushes_written"], 2 + 2 + 2 * 64)
		plain, _, s2, _ = conv.convert(bsp, scale=1.0)
		self.assertEqual(s2["terrain_brushes_written"], 0)


class ConvertTest(unittest.TestCase):
	def setUp(self):
		self.bsp = b19.load_bytes(make_sample_bsp.build(19), "sample")

	def test_sample_map(self):
		text, namer, stats, skipped = conv.convert(self.bsp, scale=0.5, wad_name="x.wad")
		self.assertEqual(stats["world_brushes_written"], 9)
		self.assertEqual(stats["brush_entities_written"], 1)
		self.assertEqual(skipped["info_pathnode"], 2)
		texes = set()
		for line in text.splitlines():
			m = FACE_RE.match(line)
			if m:
				texes.add(m.group(4))
		self.assertEqual(texes, {"NULL", "concrete", "CLIP", "!water", "sky"})
		self.assertIn('"classname" "func_door"', text)
		self.assertIn('"targetname" "door1"', text)
		# player start: MOHAA (0 0 16) at x0.5 -> feet z 8, origin lifted by hull half height + 1
		self.assertIn('"origin" "0 0 45"', text)
		self.assertIn('"classname" "info_player_allies"', text)
		# geometry is scaled: the 1024 floor edge lands at 512
		self.assertIn("512", text)
		self.assertNotIn("1024", text.split("\n", 2)[2].split('"mohaa_source"')[0])

	def test_texture_names_unique_and_short(self):
		n = conv.TextureNamer()
		a = n.name("textures/a/very_long_texture_name_here")
		b = n.name("textures/b/very_long_texture_name_here")
		self.assertLessEqual(len(a), 15)
		self.assertLessEqual(len(b), 15)
		self.assertNotEqual(a, b)
		self.assertEqual(n.name("textures/a/very_long_texture_name_here"), a)

	def test_cli_and_wad(self):
		with tempfile.TemporaryDirectory() as td:
			td = Path(td)
			(td / "in.bsp").write_bytes(make_sample_bsp.build(19))
			rc = conv.main([str(td / "in.bsp"), "-o", str(td / "out.map"), "--wad", str(td / "out.wad")])
			self.assertEqual(rc, 0)
			wad = (td / "out.wad").read_bytes()
			self.assertEqual(wad[:4], b"WAD3")
			count, ofs = struct.unpack_from("<ii", wad, 4)
			names = {wad[ofs + i * 32 + 16: ofs + i * 32 + 32].split(b"\0")[0].decode() for i in range(count)}
			self.assertEqual(names, {"concrete", "!water", "sky"})


if __name__ == "__main__":
	unittest.main()
