import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import bsp19_lightmaps as bl  # noqa: E402
import mohaa_bsp19 as b19  # noqa: E402


def mohaa_floor(size=128.0, clockwise=False, entity_origin=None):
	"""A MOHAA map with one lit floor quad, z=0, 0..size; its lightmap has
	red = 2 * x and green = y (in luxels), over a 64x64 rect of page 0."""
	page = bytearray(b19.LIGHTMAP_BYTES)
	for y in range(bl.LM):
		for x in range(bl.LM):
			o = (y * bl.LM + x) * 3
			page[o:o + 3] = bytes((min(255, 2 * x), y, 50))
	quad = [(0, 0), (size, 0), (size, size), (0, size)]
	dverts = b"".join(struct.pack("<3f2f2f3f4B", x, y, 0.0, 0, 0, x / size * 0.5, y / size * 0.5,
		0, 0, 1, 255, 255, 255, 255) for x, y in quad)
	surf = struct.pack("<12i3f9f2if", 0, -1, b19.MST_PLANAR, 0, 4, 0, 6, 0, 0, 0, 64, 64,
		*([0.0] * 12), 0, 0, 0.0)
	lumps = {i: b"" for i in range(b19.HEADER_LUMPS)}
	lumps[b19.LUMP_SHADERS] = struct.pack("<64s3i64s", b"textures/floor", 0, 1, 0, b"")
	lumps[b19.LUMP_LIGHTMAPS] = bytes(page)
	if entity_origin:  # the floor belongs to brush model *1, placed at entity_origin
		lumps[b19.LUMP_MODELS] = (struct.pack("<6f4i", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
			+ struct.pack("<6f4i", 0, 0, 0, size, size, 1, 0, 1, 0, 0))
		lumps[b19.LUMP_ENTITIES] = ('{\n"classname" "worldspawn"\n}\n{\n"classname" "func_wall"\n'
			'"model" "*1"\n"origin" "%g %g %g"\n}\n' % tuple(entity_origin)).encode() + b"\0"
	lumps[b19.LUMP_SURFACES] = surf
	lumps[b19.LUMP_DRAWVERTS] = dverts
	lumps[b19.LUMP_DRAWINDEXES] = struct.pack("<6i", *((0, 2, 1, 0, 3, 2) if clockwise else (0, 1, 2, 0, 2, 3)))
	head = 12 + 8 * b19.HEADER_LUMPS
	body, dirents = bytearray(), []
	for i in range(b19.HEADER_LUMPS):
		dirents.append((head + len(body), len(lumps[i])))
		body += lumps[i] + bytes((-len(lumps[i])) % 4)
	return b19.BSP_IDENT + struct.pack("<ii", 19, 0) + b"".join(struct.pack("<ii", *d) for d in dirents) + bytes(body)


def goldsrc_floor(size=128.0, flags=0):
	"""A BSP30 with one floor face 0..size at z=0, texture axes along x and y."""
	lumps = [b""] * bl.BSP30_LUMPS
	lumps[1] = struct.pack("<4fi", 0, 0, 1, 0, 2)
	lumps[3] = b"".join(struct.pack("<3f", x, y, 0) for x, y in ((0, 0), (size, 0), (size, size), (0, size)))
	lumps[12] = struct.pack("<10H", 0, 0, 0, 1, 1, 2, 2, 3, 3, 0)
	lumps[13] = struct.pack("<4i", 1, 2, 3, 4)
	lumps[6] = struct.pack("<8f2i", 1, 0, 0, 0, 0, 1, 0, 0, 0, flags)
	lumps[7] = struct.pack("<Hhihh4Bi", 0, 0, 0, 4, 0, 255, 255, 255, 255, -1)
	head = 4 + 8 * bl.BSP30_LUMPS
	body, dirents = bytearray(), []
	for blob in lumps:
		dirents.append((head + len(body), len(blob)))
		body += blob + bytes((-len(blob)) % 4)
	return struct.pack("<i", 30) + b"".join(struct.pack("<2i", *d) for d in dirents) + bytes(body)


def lighting_of(data):
	ofs, n = struct.unpack_from("<2i", data, 4 + bl.LUMP_LIGHTING * 8)
	face = struct.unpack_from("<Hhihh4Bi", data, struct.unpack_from("<i", data, 4 + 7 * 8)[0])
	return data[ofs:ofs + n], face


class Bsp19LightmapsTest(unittest.TestCase):
	def test_floor_takes_the_mohaa_light_under_each_luxel(self):
		mohaa = bl.Mohaa(mohaa_floor(), 1.0)
		out, st = bl.relight(mohaa, goldsrc_floor(), gain=2.0)
		lit, face = lighting_of(out)
		self.assertEqual(face[5:9], (0, 255, 255, 255))
		self.assertEqual(face[9], 0)
		self.assertEqual(len(lit), 9 * 9 * 3)  # 128 / 16 + 1 luxels a side
		self.assertEqual(st["matched"], 81)
		# luxel (2, 0): x = 32 -> lightmap x 15.5 -> red 31, green 0 (clamped), doubled
		o = (0 * 9 + 2) * 3
		self.assertEqual(tuple(lit[o:o + 3]), (62, 0, 100))
		# luxel (4, 4): x = y = 64 -> 31.5 -> red 63, green 31.5
		o = (4 * 9 + 4) * 3
		self.assertEqual(tuple(lit[o:o + 3]), (126, 63, 100))

	def test_clockwise_mohaa_winding_still_faces_up(self):
		out, st = bl.relight(bl.Mohaa(mohaa_floor(clockwise=True), 1.0), goldsrc_floor())
		self.assertEqual(st["matched"], 81)

	def test_brush_entity_surfaces_move_out_by_the_entity_origin(self):
		mohaa = bl.Mohaa(mohaa_floor(entity_origin=(0, 0, 64)), 1.0)
		data = bytearray(goldsrc_floor())
		struct.pack_into("<4f", data, struct.unpack_from("<i", data, 4 + 8)[0], 0, 0, 1, 64)
		lit_verts = struct.unpack_from("<i", data, 4 + 3 * 8)[0]
		for i in range(4):
			struct.pack_into("<f", data, lit_verts + i * 12 + 8, 64.0)
		out, st = bl.relight(mohaa, bytes(data))
		self.assertEqual((st["matched"], st["fallback"]), (81, 0))

	def test_world_scale_maps_goldsrc_luxels_back_onto_mohaa(self):
		mohaa = bl.Mohaa(mohaa_floor(128.0), 0.5)  # GoldSrc floor is 64 wide
		out, st = bl.relight(mohaa, goldsrc_floor(64.0), gain=1.0)
		lit, _ = lighting_of(out)
		self.assertEqual(len(lit), 5 * 5 * 3)
		o = (0 * 5 + 2) * 3  # x = 32 GoldSrc = 64 MOHAA -> lightmap 31.5 -> red 63
		self.assertEqual(lit[o], 63)

	def test_special_faces_stay_unlit_and_unmatched_faces_get_a_flat_light(self):
		mohaa = bl.Mohaa(mohaa_floor(), 1.0)
		out, st = bl.relight(mohaa, goldsrc_floor(flags=bl.TEX_SPECIAL))
		lit, face = lighting_of(out)
		self.assertEqual((face[5], face[9]), (255, -1))
		self.assertEqual(lit, b"")
		far = goldsrc_floor()
		# move the GoldSrc face's plane up 64: nothing in MOHAA lies on it
		lumps = struct.unpack_from("<i", far, 4 + 1 * 8)[0]
		far = bytearray(far)
		struct.pack_into("<4f", far, lumps, 0, 0, 1, 64)
		out, st = bl.relight(mohaa, bytes(far))
		self.assertEqual(st["fallback"], 1)
		lit, _ = lighting_of(out)
		self.assertEqual(tuple(lit[:3]), bl.FALLBACK)

	def test_shift_keeps_the_hue_past_white(self):
		r, g, b = bl.shift((200, 100, 50), 2.0)
		self.assertEqual(r, 255)
		self.assertIn(g, (127, 128))
		self.assertIn(b, (63, 64))
		self.assertEqual(bl.shift((10, 20, 30), 2.0), bytes((20, 40, 60)))


if __name__ == "__main__":
	unittest.main()
