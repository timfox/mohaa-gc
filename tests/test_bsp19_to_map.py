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
