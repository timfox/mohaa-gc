#!/usr/bin/env python3
"""mohaa_skd: SKMD meshes, .tik setup blocks and shader textures, from synthetic files."""
from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import mohaa_skd as skd  # noqa: E402


def build_skd(verts, tris, morphs=False, bones=1, version=5, ident=b"SKL "):
	"""One surface. verts: [((x, y, z), [(bone, weight, (ox, oy, oz)), ...])]."""
	vb = b""
	for (n, uv), weights in verts:
		vb += struct.pack("<5fi", *n, *uv, len(weights))
		if morphs:
			vb += struct.pack("<i", 1) + struct.pack("<i3f", 0, 9, 9, 9)
		for bone, w, off in weights:
			vb += struct.pack("<if3f", bone, w, *off)
	tb = b"".join(struct.pack("<3i", *t) for t in tris)
	col = struct.pack(f"<{len(verts)}i", *range(len(verts)))
	ofs_tri = skd.SURFACE.size
	ofs_vert = ofs_tri + len(tb)
	ofs_col = ofs_vert + len(vb)
	ofs_end = ofs_col + len(col)
	surf = skd.SURFACE.pack(ident, b"bark", len(tris), len(verts), 0, ofs_tri, ofs_vert, ofs_col, ofs_end, 0)
	bone = skd.BONE.pack(b"Box02", b"worldbone", 1, 84, 96, 116, 116) + struct.pack("<3f", 1, 1, 1) \
		+ b"Box02 rot\0Box02 pos\0"
	ofs_bones = skd.HEADER.size
	ofs_surf = ofs_bones + len(bone)
	header = skd.HEADER.pack(b"SKMD", version, b"tree", 1, bones, ofs_bones, ofs_surf, ofs_surf + ofs_end)
	return header + bone + surf + tb + vb + col


QUAD = [(((0, 0, 1), (0, 0)), [(0, 1.0, (0, 0, 0))]),
        (((0, 0, 1), (1, 0)), [(0, 1.0, (10, 0, 0))]),
        (((0, 0, 1), (1, 1)), [(0, 0.5, (10, 20, 0)), (0, 0.5, (10, 20, 8))]),
        (((0, 0, 1), (0, 1)), [(0, 1.0, (0, 20, 0))])]


class SkdTest(unittest.TestCase):
	def test_reads_a_weighted_mesh(self):
		m = skd.parse_skd(build_skd(QUAD, [(0, 1, 2), (0, 2, 3)]), "t.skd")
		self.assertEqual((m.version, m.num_triangles, m.num_verts), (5, 2, 4))
		s = m.surfaces[0]
		self.assertEqual(s.name, "bark")
		self.assertEqual(s.layout, "weights")
		self.assertEqual(s.positions[2], (10.0, 20.0, 4.0))  # weighted sum of the offsets
		self.assertEqual(s.uvs[1], (1.0, 0.0))
		self.assertEqual(m.bounds(), ((0.0, 0.0, 0.0), (10.0, 20.0, 4.0)))

	def test_reads_morph_records(self):
		m = skd.parse_skd(build_skd(QUAD, [(0, 1, 2)], morphs=True), "t.skd")
		self.assertEqual(m.surfaces[0].layout, "morphs+weights")
		self.assertEqual(m.surfaces[0].positions[1], (10.0, 0.0, 0.0))

	def test_bone_names_and_idle_pose(self):
		m = skd.parse_skd(build_skd(QUAD, [(0, 1, 2), (0, 2, 3)]), "t.skd")
		self.assertEqual(m.bones, ["Box02"])
		# the props' idle rotation: mesh x, y, z become world y, z, x (a tree's height lands on z)
		skd.apply_pose(m, {"box02": ((1.0, 2.0, 3.0), (0.5, 0.5, 0.5, -0.5))})
		got = [tuple(round(c, 6) for c in p) for p in m.surfaces[0].positions]
		self.assertEqual(got[1], (1.0, 12.0, 3.0))   # offset (10, 0, 0) -> (0, 10, 0) + pos
		self.assertEqual(got[3], (1.0, 2.0, 23.0))   # offset (0, 20, 0) -> (0, 0, 20) + pos
		self.assertEqual(tuple(round(c, 6) for c in m.surfaces[0].normals[0]), (1.0, 0.0, 0.0))

	def test_idle_animation_pose(self):
		frame = skd.SKC_FRAME.pack(-1, -1, -1, 1, 1, 1, 2, 0, 0, 0, 0, 96)
		chans = struct.pack("<4f", 1, 2, 3, 0) + struct.pack("<4f", 0.5, 0.5, 0.5, -0.5)
		names = b"Box02 pos".ljust(32, b"\0") + b"Box02 rot".ljust(32, b"\0")
		header = skd.SKC_HEADER.pack(b"SKAN", 13, 0, 192, 1 / 30, 0, 0, 0, 0, 2, 128, 1)
		data = header + frame + chans + names
		self.assertEqual(len(data), 192)
		pose = skd.parse_skc(data, "t.skc")
		self.assertEqual(pose, {"box02": ((1.0, 2.0, 3.0), (0.5, 0.5, 0.5, -0.5))})
		t = skd.parse_tik("setup { path models/static\n skelmodel a.skd }\nanimations\n{\n idle  a.skc\n}\n")
		self.assertEqual(t.idle_anim, "models/static/a.skc")
		with self.assertRaises(skd.SkdError):
			skd.parse_skc(b"SKMD" + bytes(188))

	def test_older_surface_ident(self):
		self.assertEqual(skd.parse_skd(build_skd(QUAD, [(0, 1, 2)], ident=b"SKSF")).num_triangles, 1)

	def test_rejects_bad_files(self):
		with self.assertRaises(skd.SkdError):
			skd.parse_skd(b"IDP3" + bytes(200))
		with self.assertRaises(skd.SkdError):
			skd.parse_skd(build_skd(QUAD, [(0, 1, 7)]))  # a triangle past the vertices


class TikTest(unittest.TestCase):
	TIK = """TIKI
setup
{
	scale 0.8   // smaller
	path models/static
	skelmodel tree_pine.skd
	surface bark shader tree_bark
	surface all shader tree_leaves
}
init { server { classname static } }
"""

	def test_setup_block(self):
		t = skd.parse_tik(self.TIK)
		self.assertEqual(t.scale, 0.8)
		self.assertEqual(t.mesh, "models/static/tree_pine.skd")
		self.assertEqual(t.shaders, {"bark": "tree_bark", "all": "tree_leaves"})

	def test_shader_textures(self):
		shaders = skd.parse_shaders("""
tree_bark
{
	surfaceparm nolightmap
	{
		map $lightmap
	}
	{
		map textures/trees/Bark1.tga
		rgbGen identity
	}
}
tree_leaves { cull none { animmap 4 textures/trees/leaf1.tga textures/trees/leaf2.tga alphaFunc GE128 } }
""")
		self.assertEqual(shaders, {"tree_bark": "textures/trees/bark1.tga", "tree_leaves": "textures/trees/leaf1.tga"})
		t = skd.parse_tik(self.TIK)
		self.assertEqual(skd.surface_texture(t, "BARK", shaders), "textures/trees/bark1.tga")
		self.assertEqual(skd.surface_texture(t, "needles", shaders), "textures/trees/leaf1.tga")


if __name__ == "__main__":
	unittest.main()
