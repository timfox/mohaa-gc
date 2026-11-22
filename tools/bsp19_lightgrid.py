#!/usr/bin/env python3
"""MOHAA's light grid, for the GameCube engine to light models the way retail does.

  bsp19_lightgrid.py MOHAA.bsp -o media/lg_<map>.gcg [--scale S] [--gain G]

MOHAA lights models (soldiers, props that move) from a grid of light colours
over the world, not from the floor under them. The BSP keeps it in three lumps:

- lightgridpalette: 256 RGB colours. Index 0 is "no sample" (inside solid).
- lightgridoffsets: u16s. First one per grid x (a block base, in units of 256
  bytes), then one per grid column, x major and y fastest. A column's bytes start
  at base[x] * 256 + low[x * by + y] in the data lump. Identical columns share
  bytes.
- lightgriddata: each column from z = 0 up, run-length coded. A signed control
  byte c < 0 is followed by -c literal palette indices; c >= 0 by one index that
  repeats c + 2 times.

The grid spacing is 32 units. Its origin is 32 * ceil(mins / 32) of the world
model, and it has (32 * floor(maxs / 32) - origin) / 32 + 1 points on each axis.
The colours are at the light the game shows (not one overbright bit down, as
lightmaps are).

The output keeps that layout, so the engine can decode it from ARAM the same way.
Big-endian, for the GameCube:

  0   "GClg"  u32 version (1)  u32 bx, by, bz
  20  u32 offsets at, u32 offsets count, u32 data at, u32 data bytes
  36  f32 origin x, y, z  f32 cell x, y, z (GoldSrc units, after --scale)
  60  u32 0
  64  palette: 256 * RGB (after --gain), padded to 832
  832 offsets (u16), then data, each 32-byte aligned

Positions are scaled the way bsp19_to_map.py scales the world. --gain scales the
colours to match the lightmaps of bsp19_lightmaps.py: its gain over MOHAA's
lightmap bytes, over the 2 the game itself applies.
"""

import argparse
import math
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bsp19_lightmaps  # noqa: E402
import mohaa_bsp19 as b19  # noqa: E402

GRID = 32.0
MAGIC = b"GClg"
VERSION = 1
HEADER = 64
PALETTE_END = 832
DEFAULT_GAIN = bsp19_lightmaps.DEFAULT_GAIN / 2.0


class Grid:
	"""A MOHAA BSP's light grid, in MOHAA units."""

	def __init__(self, data: bytes):
		bsp = b19.load_bytes(data)
		lump = lambda i: bsp19_lightmaps.Mohaa._lump(data, bsp.version, i)  # noqa: E731
		self.palette = lump(b19.LUMP_LIGHTGRIDPALETTE)
		raw = lump(b19.LUMP_LIGHTGRIDOFFSETS)
		self.data = lump(b19.LUMP_LIGHTGRIDDATA)
		if not bsp.models:
			raise ValueError("no world model")
		mins, maxs = bsp.models[0].mins, bsp.models[0].maxs
		self.origin = tuple(GRID * math.ceil(mins[a] / GRID) for a in range(3))
		self.bounds = tuple(int((GRID * math.floor(maxs[a] / GRID) - self.origin[a]) / GRID) + 1 for a in range(3))
		bx, by, _bz = self.bounds
		self.offsets = struct.unpack("<%dH" % (len(raw) // 2), raw[:len(raw) // 2 * 2])
		if len(self.palette) < 768 or len(self.offsets) != bx * by + bx or not self.data:
			raise ValueError("light grid does not match the world bounds (%d offsets for %dx%d)"
				% (len(self.offsets), bx, by))

	def column_at(self, x: int, y: int) -> int:
		bx, by, _ = self.bounds
		return self.offsets[x] * 256 + self.offsets[bx + x * by + y]

	def column(self, x: int, y: int, upto: int) -> list:
		"""Palette indices of column (x, y) from z = 0 through z = upto."""
		o, out = self.column_at(x, y), []
		d = self.data
		while len(out) <= upto and o < len(d):
			c = d[o] - 256 if d[o] > 127 else d[o]
			o += 1
			if c < 0:
				out.extend(d[o:o - c])
				o -= c
			elif o < len(d):
				out.extend([d[o]] * (c + 2))
				o += 1
		return out

	def light(self, p) -> tuple | None:
		"""Trilinear light at p (MOHAA units), as the renderer reads it, or None in solid."""
		f = [(p[a] - self.origin[a]) / GRID for a in range(3)]
		i = [math.floor(v) for v in f]
		fr = [f[a] - i[a] for a in range(3)]
		acc, tw = [0.0, 0.0, 0.0], 0.0
		for dx in (0, 1):
			for dy in (0, 1):
				x, y = i[0] + dx, i[1] + dy
				if not (0 <= x < self.bounds[0] and 0 <= y < self.bounds[1]):
					continue
				col = self.column(x, y, max(i[2] + 1, 0))
				for dz in (0, 1):
					z = i[2] + dz
					if not (0 <= z < len(col)) or col[z] == 0:
						continue
					w = ((fr[0] if dx else 1 - fr[0]) * (fr[1] if dy else 1 - fr[1])
						* (fr[2] if dz else 1 - fr[2]))
					c = col[z] * 3
					for k in range(3):
						acc[k] += self.palette[c + k] * w
					tw += w
		if tw <= 0.0:
			return None
		if tw < 0.99:
			acc = [v / tw for v in acc]
		m = max(acc)
		if m > 255.0:
			acc = [v * 255.0 / m for v in acc]
		return tuple(acc)


def pack(grid: Grid, scale: float, gain: float) -> bytes:
	bx, by, bz = grid.bounds
	pal = bytes(min(255, int(c * gain + 0.5)) for c in grid.palette[:768])
	offs = struct.pack(">%dH" % len(grid.offsets), *grid.offsets)
	offs_at = PALETTE_END
	data_at = (offs_at + len(offs) + 31) & ~31
	head = MAGIC + struct.pack(">4I4I6fI", VERSION, bx, by, bz, offs_at, len(grid.offsets), data_at, len(grid.data),
		*(c * scale for c in grid.origin), *(GRID * scale,) * 3, 0)
	assert len(head) == HEADER
	out = bytearray(head + pal)
	out += bytes(offs_at - len(out)) + offs
	out += bytes(data_at - len(out)) + grid.data
	out += bytes((-len(out)) % 32)
	return bytes(out)


def main(argv=None) -> int:
	ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	ap.add_argument("mohaa", help="MOHAA BSP (or pk3:member)")
	ap.add_argument("-o", "--out", required=True, type=Path)
	ap.add_argument("--scale", type=float, default=bsp19_lightmaps.DEFAULT_SCALE)
	ap.add_argument("--gain", type=float, default=DEFAULT_GAIN, help="colour multiplier (default: matches bsp19_lightmaps)")
	a = ap.parse_args(argv)
	grid = Grid(bsp19_lightmaps.read_source(a.mohaa))
	blob = pack(grid, a.scale, a.gain)
	a.out.parent.mkdir(parents=True, exist_ok=True)
	a.out.write_bytes(blob)
	bx, by, bz = grid.bounds
	print(f"bsp19_lightgrid: {bx}x{by}x{bz} points, {len(grid.data)} data bytes, {len(blob)} bytes written")
	return 0


if __name__ == "__main__":
	sys.exit(main())
