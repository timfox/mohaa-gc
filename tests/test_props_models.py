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
		meshes = pm.terrain_meshes(bsp, 0.5, tol=-1.0)	# every sample (the coarse grids are tested below)
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

	def test_smooth_terrain_takes_a_coarse_grid_with_a_skirt(self):
		import mohaa_bsp19 as b19
		bsp = b19.Bsp("t", 19, 0, 0, {})
		bsp.shaders = [b19.Shader("textures/terrain/snow", 0, 1, 0)]
		slope = [100 + 2 * (k % 9) for k in range(81)]	# a plane: the 3 x 3 grid holds it exactly
		bump = list(slope)
		bump[4 * 9 + 4] += 40	# one tall sample in the middle: only the full grid keeps it
		tex = (0.0, 0.0, 0.0, 4.0, 4.0, 0.0, 4.0, 4.0)
		for heights, nv, nt in ((slope, 9 + 4 * 3 * 2, 8 + 4 * 2 * 2), (bump, 81, 128)):
			bsp.terrain = [b19.TerrainPatch(0, 0, 100, 0, heights, tex)]
			(_, centre, surfaces), = pm.terrain_meshes(bsp, 1.0)
			_, verts, tris = surfaces[0]
			self.assertEqual((len(verts), len(tris)), (nv, nt))
		bsp.terrain = [b19.TerrainPatch(0, 0, 100, 0, slope, tex)]
		(_, centre, surfaces), = pm.terrain_meshes(bsp, 1.0)
		_, verts, tris = surfaces[0]
		self.assertEqual(round(verts[8][0] + centre[0], 3), 512.0)	# the far corner is still at the edge
		self.assertEqual(verts[8][6:8], (4.0, 4.0))
		zs = sorted({round(v[2] + centre[2], 3) for v in verts[9:]})
		self.assertEqual(zs[0], 100 - pm.TERRAIN_SKIRT)	# the skirt hangs below the rim
		for a, b, c in tris[:8]:	# the top still faces up
			e1 = [verts[b][k] - verts[a][k] for k in range(2)]
			e2 = [verts[c][k] - verts[a][k] for k in range(2)]
			self.assertGreater(e1[0] * e2[1] - e1[1] * e2[0], 0)

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
		meshes = pm.surface_meshes(bsp, 0.5)
		self.assertEqual(len(meshes), 1)
		name, centre, surfaces = meshes[0]
		self.assertTrue(name.startswith(pm.WORLD_PREFIX))
		shader, verts, tris = surfaces[0]
		self.assertEqual((shader, len(verts), len(tris)), ("textures/ground/mud", 4 + 4, 2 + 2))	# a flat patch is one quad
		for a, b, c in tris:	# all counter-clockwise seen from above, like the props
			e1 = [verts[b][k] - verts[a][k] for k in range(2)]
			e2 = [verts[c][k] - verts[a][k] for k in range(2)]
			self.assertGreater(e1[0] * e2[1] - e1[1] * e2[0], 0)
		self.assertEqual(verts[3][6:8], (1.0, 1.0))	# the patch's far corner keeps its st
		self.assertEqual(round(verts[3][0] + centre[0], 4), 32.0)	# far corner at map x 64 * 0.5

	def test_curved_patches_get_more_cuts_than_flat_ones(self):
		def patch(bulge):
			pts = [(x * 64.0, y * 64.0, bulge if (x, y) == (1, 1) else 0.0, 0.0, 0.0, 1.0, x / 2, y / 2)
			       for y in range(3) for x in range(3)]
			return pm.patch_mesh(pts, 3, 3)
		self.assertEqual(len(patch(0.0)[1]), 2)
		v, t = patch(256.0)	# a strong dome: cut finer, crack-free grid
		self.assertGreater(len(t), 2)
		self.assertLessEqual(len(t), 2 * pm.PATCH_MAX_STEPS ** 2)
		self.assertGreater(max(p[2] for p in v), 32.0)	# the dome is there

	def test_filter_and_add_shaders_cut_out(self):
		text = ("netting\n{\n {\n  map textures/m/net.tga\n  blendFunc GL_DST_COLOR GL_ZERO\n }\n}\n"
			"glow\n{\n {\n  map textures/m/glow.tga\n  blendFunc add\n }\n}\n"
			"plain\n{\n {\n  map textures/m/plain.tga\n }\n {\n  map $lightmap\n  blendFunc filter\n }\n}\n")
		self.assertEqual(skd.parse_shader_blends(text), {"netting": "filter", "glow": "add"})
		from PIL import Image
		img = Image.new("RGB", (16, 16), (255, 255, 255))
		img.paste((20, 20, 20), (0, 0, 8, 16))	# the dark strands of the net
		buf = io.BytesIO()
		img.save(buf, format="TGA")
		w, h, flags, pal, idx = pm.encode_texture(buf.getvalue(), blend="filter")
		self.assertEqual(flags, pm.TEX_ALPHA)
		self.assertNotEqual(idx[0], 255)	# a strand stays
		self.assertEqual(idx[15], 255)	# the white between them is cut
		self.assertEqual(pm.encode_texture(buf.getvalue())[2], 0)	# without the blend: opaque, as before

	def test_read_props(self):
		with tempfile.NamedTemporaryFile("w", suffix=".props", delete=False) as f:
			f.write("# header\n1 2 3 0 90 0 0.5 static/rock%20big.tik\n")
		self.assertEqual(pm.read_props(f.name), [("static/rock big.tik", (1.0, 2.0, 3.0), (0.0, 90.0, 0.0), 0.5)])


if __name__ == "__main__":
	unittest.main()
