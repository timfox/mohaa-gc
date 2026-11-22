#!/usr/bin/env python3
"""props_models: a .mprop pack from synthetic .tik/.skd/.skc/.tga files."""
from __future__ import annotations

import io
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import props_models as pm  # noqa: E402
import mohaa_skd as skd  # noqa: E402
from test_mohaa_skd import QUAD, build_skd  # noqa: E402


def tga(w, h, alpha_hole=False):
	from PIL import Image
	img = Image.new("RGBA", (w, h), (40, 120, 30, 255))
	if alpha_hole:
		img.paste((0, 0, 0, 0), (0, 0, 20, 20))
	buf = io.BytesIO()
	img.save(buf, format="TGA")
	return buf.getvalue()


def skc():
	frame = skd.SKC_FRAME.pack(0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 96)
	chans = struct.pack("<4f", 0, 0, 0, 0) + struct.pack("<4f", 0.5, 0.5, 0.5, -0.5)
	names = b"Box02 pos".ljust(32, b"\0") + b"Box02 rot".ljust(32, b"\0")
	return skd.SKC_HEADER.pack(b"SKAN", 13, 0, 192, 1 / 30, 0, 0, 0, 0, 2, 128, 1) + frame + chans + names


TIK = b"TIKI\nsetup\n{\n scale 2\n path models/static\n skelmodel pine.skd\n surface bark shader pinebark\n}\nanimations\n{\n idle pine.skc\n}\n"
SHADER = b"pinebark\n{\n {\n  map textures/models/bark.tga\n  alphaFunc GE128\n }\n}\n"


class PackTest(unittest.TestCase):
	def files(self):
		return {
			"models/static/pine.tik": TIK,
			"models/static/pine.skd": build_skd(QUAD, [(0, 1, 2), (0, 2, 3)]),
			"models/static/pine.skc": skc(),
			"scripts/trees.shader": SHADER,
			"textures/models/bark.tga": tga(300, 70, alpha_hole=True),
		}

	def test_pack(self):
		props = [("static/pine.tik", (1.0, 2.0, 3.0), (0.0, 90.0, 0.0), 0.766),
		         ("static/pine.tik", (5.0, 5.0, 5.0), (0.0, 0.0, 0.0), 0.766),
		         ("static/missing.tik", (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), 1.0)]
		data, stats = pm.build(self.files(), lambda e: e, props)
		self.assertEqual((stats["models"], stats["instances"], stats["textures"]), (1, 2, 1))
		self.assertEqual((stats["models_unloaded"], stats["instances_unloaded"]), (1, 1))
		magic, ver, ntex, nmod, ninst = struct.unpack_from("<4s4i", data, 0)
		self.assertEqual((magic, ver, ntex, nmod, ninst), (b"MPRP", 2, 1, 1, 2))
		at = 20
		name = data[at:at + 32].rstrip(b"\0")
		w, h, flags = struct.unpack_from("<2HI", data, at + 32)
		self.assertEqual((name, w, h, flags), (b"textures/models/bark.tga", 128, 64, pm.TEX_ALPHA))
		pal = data[at + 40:at + 40 + 1024]
		idx = data[at + 1064:at + 1064 + w * h]
		self.assertEqual(idx[0], 255)          # the transparent pixel
		self.assertEqual(pal[255 * 4 + 3], 0)  # and its palette entry
		at += 1064 + w * h
		mname = data[at:at + 64].rstrip(b"\0")
		mins_maxs = struct.unpack_from("<6fi", data, at + 64)
		self.assertEqual(mname, b"static/pine.tik")
		# posed (heights on z) and scaled by the .tik's 2: the quad spans 20 in x, 40 in z
		self.assertEqual([round(v, 4) for v in mins_maxs[:6]], [0, 0, 0, 0, 20, 40][:3] + [8.0, 20.0, 40.0])
		at += 64 + 28
		ti, nv, nt = struct.unpack_from("<3i", data, at)
		self.assertEqual((ti, nv, nt), (0, 4, 2))
		v0 = struct.unpack_from("<8f", data, at + 12)
		self.assertEqual([round(c, 4) for c in v0[3:6]], [1.0, 0.0, 0.0])  # normal (0,0,1) posed: on x
		at += 12 + nv * 32 + nt * 6
		inst = struct.unpack_from("<i7f", data, at)
		self.assertEqual(inst[0], 0)
		self.assertAlmostEqual(inst[7], 0.766, places=5)
		self.assertEqual(len(data), at + 2 * 32)

	def test_terrain_becomes_world_meshes(self):
		import mohaa_bsp19 as b19
		bsp = b19.Bsp("t", 19, 0, 0, {})
		bsp.shaders = [b19.Shader("textures/terrain/snow", 0, 1, 0)]
		heights = [100 + 2 * (k % 9) for k in range(81)]	# rises along x
		tex = (0.0, 0.0, 0.0, 4.0, 4.0, 0.0, 4.0, 4.0)
		bsp.terrain = [b19.TerrainPatch(0, 0, 100, 0, heights, tex), b19.TerrainPatch(8, 0, 100, 0, heights, tex),
			b19.TerrainPatch(64, 64, 100, 0, heights, tex)]
		meshes = pm.terrain_meshes(bsp, 0.5)
		self.assertEqual(len(meshes), 2)	# two patches side by side share a mesh, the far one has its own
		name, centre, surfaces = meshes[0]
		self.assertTrue(name.startswith(pm.WORLD_PREFIX))
		shader, verts, tris = surfaces[0]
		self.assertEqual((shader, len(verts), len(tris)), ("textures/terrain/snow", 2 * 81, 2 * 128))
		# map units around the centre: the first patch spans x 0..256 (512 at scale 0.5)
		xs = [v[0] + centre[0] for v in verts[:81]]
		self.assertEqual((min(xs), max(xs)), (0.0, 256.0))
		self.assertEqual(verts[80][6:8], (4.0, 4.0))	# far corner's texture coordinates
		self.assertLess(verts[40][3], 0.0)	# the slope rises along x: the normal leans back
		files = dict(self.files(), **{"textures/terrain/snow.jpg": tga(64, 64)})
		data, stats = pm.build(files, lambda e: e, [], world=meshes)
		self.assertEqual((stats["world_models"], stats["instances"], stats["models"]), (2, 2, 2))
		self.assertIn(b"*world/terrain_0_0", data)

	def test_patches_and_soups_become_world_meshes(self):
		import mohaa_bsp19 as b19
		bsp = b19.Bsp("t", 19, 0, 0, {})
		bsp.shaders = [b19.Shader("textures/ground/mud", 0, 1, 0), b19.Shader("textures/sky/sky", b19.SURF_SKY, 0, 0)]
		# a flat 3x3 patch facing up (z), 0..64, and a soup quad wound clockwise seen from above
		pts = [(x * 32.0, y * 32.0, 0.0) for y in range(3) for x in range(3)]
		soup = [(100.0, 0.0, 8.0), (100.0, 32.0, 8.0), (132.0, 32.0, 8.0), (132.0, 0.0, 8.0)]
		bsp.drawverts = pts + soup
		bsp.drawvert_normals = [(0.0, 0.0, 1.0)] * len(bsp.drawverts)
		bsp.drawvert_st = [(p[0] / 64, p[1] / 64) for p in bsp.drawverts]
		bsp.drawindexes = [0, 1, 2, 0, 2, 3]
		bsp.surfaces = [b19.Surface(0, b19.MST_PATCH, 9, 0, 3, 3, 0.0, 0, 0),
			b19.Surface(0, b19.MST_TRIANGLE_SOUP, 4, 6, 0, 0, 0.0, 9, 0),
			b19.Surface(1, b19.MST_TRIANGLE_SOUP, 4, 6, 0, 0, 0.0, 9, 0)]	# sky: left out
		bsp.models = [b19.Model((0, 0, 0), (0, 0, 0), 0, 3, 0, 0)]
		meshes = pm.surface_meshes(bsp, 0.5, steps=2)
		self.assertEqual(len(meshes), 1)
		name, centre, surfaces = meshes[0]
		self.assertTrue(name.startswith(pm.WORLD_PREFIX))
		shader, verts, tris = surfaces[0]
		self.assertEqual((shader, len(verts), len(tris)), ("textures/ground/mud", 9 + 4, 8 + 2))
		for a, b, c in tris:	# all counter-clockwise seen from above, like the props
			e1 = [verts[b][k] - verts[a][k] for k in range(2)]
			e2 = [verts[c][k] - verts[a][k] for k in range(2)]
			self.assertGreater(e1[0] * e2[1] - e1[1] * e2[0], 0)
		self.assertEqual(verts[8][6:8], (1.0, 1.0))	# the patch's far corner keeps its st
		self.assertEqual(round(verts[4][0] + centre[0], 4), 16.0)	# patch middle at map x 32 * 0.5

	def test_read_props(self):
		with tempfile.NamedTemporaryFile("w", suffix=".props", delete=False) as f:
			f.write("# header\n1 2 3 0 90 0 0.5 static/rock%20big.tik\n")
		self.assertEqual(pm.read_props(f.name), [("static/rock big.tik", (1.0, 2.0, 3.0), (0.0, 90.0, 0.0), 0.5)])


if __name__ == "__main__":
	unittest.main()
