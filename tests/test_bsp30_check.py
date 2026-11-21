#!/usr/bin/env python3
from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import bsp30_check as bc  # noqa: E402


def make_bsp(clipnodes, wide: bool, ext: bool) -> bytes:
	"""Tiny BSP30: plane 0 is x = 0; model 0's hull 1-3 headnode is clipnode 0."""
	hdr = 4 + 8 * bc.HEADER_LUMPS
	extra = struct.pack("<4si", b"XASH", 4) + bytes(8 * bc.EXTRA_LUMPS) if ext else b""
	planes = struct.pack("<4fi", 1.0, 0.0, 0.0, 0.0, 0)
	fmt = "<iii" if wide else "<ihh"
	clip = b"".join(struct.pack(fmt, *c) for c in clipnodes)
	model = struct.pack("<9f4i3i", *([0.0] * 9), 0, 0, 0, 0, 0, 0, 0)
	body, lumps, pos = b"", [(0, 0)] * bc.HEADER_LUMPS, hdr + len(extra)
	for num, data in ((bc.LUMP_PLANES, planes), (bc.LUMP_CLIPNODES, clip), (bc.LUMP_MODELS, model)):
		lumps[num] = (pos + len(body), len(data))
		body += data
	return struct.pack("<i", 30) + b"".join(struct.pack("<ii", *l) for l in lumps) + extra + body


class Bsp30CheckTest(unittest.TestCase):
	def test_stock_16bit(self):
		b = bc.load(make_bsp([(0, -1, -2)], wide=False, ext=False))
		self.assertFalse(b["ext"] or b["wide"])
		self.assertEqual(bc.check(b), [])
		self.assertEqual(bc.contents(b, 1, (5, 0, 0)), -1)
		self.assertEqual(bc.contents(b, 1, (-5, 0, 0)), -2)

	def test_bsp30ext_wide(self):
		# 32767 nodes forces the 32-bit layout; node 0 -> node 32766 -> contents
		nodes = [(0, 32766, -2)] + [(0, -1, -2)] * 32766
		b = bc.load(make_bsp(nodes, wide=True, ext=True))
		self.assertTrue(b["ext"] and b["wide"])
		self.assertEqual(bc.check(b), [])
		self.assertEqual(bc.contents(b, 1, (5, 0, 0)), -1)

	def test_ext_header_small_lump_stays_16bit(self):
		b = bc.load(make_bsp([(0, -1, -2)], wide=False, ext=True))
		self.assertTrue(b["ext"])
		self.assertFalse(b["wide"])

	def test_cycle_detected(self):
		b = bc.load(make_bsp([(0, 1, -2), (0, 0, -2)], wide=False, ext=False))
		self.assertTrue(any("cycle" in e for e in bc.check(b)))


if __name__ == "__main__":
	unittest.main()
