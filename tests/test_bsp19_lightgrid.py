import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import bsp19_lightgrid as lg  # noqa: E402
import mohaa_bsp19 as b19  # noqa: E402


def mohaa_grid():
	"""A MOHAA map whose world is 0..64 on each axis: a 3x3x3 light grid.
	Column (0, 0) holds literal points 1, 2, 3; every other column is colour 4
	repeated (its points share one run), except (2, 2), which is solid (0)."""
	pal = bytearray(768)
	pal[3:6] = bytes((30, 60, 90))
	pal[6:9] = bytes((60, 60, 60))
	pal[9:12] = bytes((90, 90, 90))
	pal[12:15] = bytes((100, 0, 200))
	data = bytes((0xFD, 1, 2, 3)) + bytes((0x01, 4)) + bytes((0x01, 0))
	lows = []
	for x in range(3):
		for y in range(3):
			lows.append(0 if (x, y) == (0, 0) else 6 if (x, y) == (2, 2) else 4)
	offsets = struct.pack("<12H", 0, 0, 0, *lows)
	lumps = {i: b"" for i in range(b19.HEADER_LUMPS)}
	lumps[b19.LUMP_MODELS] = struct.pack("<6f4i", 0, 0, 0, 64, 64, 64, 0, 0, 0, 0)
	lumps[b19.LUMP_LIGHTGRIDPALETTE] = bytes(pal)
	lumps[b19.LUMP_LIGHTGRIDOFFSETS] = offsets
	lumps[b19.LUMP_LIGHTGRIDDATA] = data
	head = 12 + 8 * b19.HEADER_LUMPS
	body, dirents = bytearray(), []
	for i in range(b19.HEADER_LUMPS):
		dirents.append((head + len(body), len(lumps[i])))
		body += lumps[i] + bytes((-len(lumps[i])) % 4)
	return b19.BSP_IDENT + struct.pack("<ii", 19, 0) + b"".join(struct.pack("<ii", *d) for d in dirents) + bytes(body)


class Bsp19LightgridTest(unittest.TestCase):
	def test_grid_geometry_and_columns(self):
		g = lg.Grid(mohaa_grid())
		self.assertEqual(g.origin, (0, 0, 0))
		self.assertEqual(g.bounds, (3, 3, 3))
		self.assertEqual(g.column(0, 0, 2), [1, 2, 3])
		self.assertEqual(g.column(1, 2, 2), [4, 4, 4])

	def test_light_reads_a_point_and_interpolates_up_a_column(self):
		g = lg.Grid(mohaa_grid())
		self.assertEqual(g.light((0, 0, 0)), (30.0, 60.0, 90.0))
		r, gr, b = g.light((0, 0, 16))  # halfway between colours 1 and 2
		self.assertAlmostEqual(r, 45.0)
		self.assertAlmostEqual(b, 75.0)

	def test_solid_corners_drop_out(self):
		g = lg.Grid(mohaa_grid())
		self.assertIsNone(g.light((64, 64, 0)))
		# halfway from colour 4 (1, 2) to solid (2, 2): all colour 4
		self.assertEqual(g.light((48, 64, 0)), (100.0, 0.0, 200.0))

	def test_pack_header_and_gain(self):
		blob = lg.pack(lg.Grid(mohaa_grid()), 0.5, 2.0)
		self.assertEqual(blob[:4], b"GClg")
		ver, bx, by, bz, oat, on, dat, dn = struct.unpack_from(">8I", blob, 4)
		self.assertEqual((ver, bx, by, bz, on, dn), (1, 3, 3, 3, 12, 8))
		self.assertEqual(struct.unpack_from(">6f", blob, 36), (0, 0, 0, 16, 16, 16))
		self.assertEqual(blob[64 + 3:64 + 6], bytes((60, 120, 180)))
		self.assertEqual(blob[64 + 12:64 + 15], bytes((200, 0, 255)))
		self.assertEqual(oat % 32, 0)
		self.assertEqual(dat % 32, 0)
		self.assertEqual(blob[dat:dat + 8], bytes((0xFD, 1, 2, 3, 1, 4, 1, 0)))
		self.assertEqual(struct.unpack_from(">H", blob, oat + 2 * (3 + 8))[0], 6)
		self.assertEqual(len(blob) % 32, 0)


if __name__ == "__main__":
	unittest.main()
