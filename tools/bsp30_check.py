#!/usr/bin/env python3
"""Check a GoldSrc BSP30 file, including Xash3D's BSP30ext (32-bit clipnodes).

Prints lump sizes and the clipnode format, then checks every clipnode's
children and every model's hull headnodes. With --point x y z [hull],
reports the hull contents at that point, so you can spot-check collision.

    python3 tools/bsp30_check.py maps/m1l2a.bsp
    python3 tools/bsp30_check.py maps/m1l2a.bsp --point 0 0 40 1
"""
from __future__ import annotations

import argparse
import struct
import sys

HLBSP_VERSION = 30
LUMP_PLANES, LUMP_CLIPNODES, LUMP_MODELS = 1, 9, 14
HEADER_LUMPS = 15
IDEXTRAHEADER = b"XASH"
EXTRA_VERSION = 4
EXTRA_LUMPS = 12
MAX_MAP_CLIPNODES_HLBSP = 32767
CONTENTS = {-1: "empty", -2: "solid", -3: "water", -4: "slime", -5: "lava", -6: "sky"}


def load(data: bytes):
	version, = struct.unpack_from("<i", data, 0)
	if version != HLBSP_VERSION:
		raise SystemExit(f"not BSP30 (version {version})")
	lumps = [struct.unpack_from("<ii", data, 4 + 8 * i) for i in range(HEADER_LUMPS)]
	hdr_end = 4 + 8 * HEADER_LUMPS
	ext = data[hdr_end:hdr_end + 4] == IDEXTRAHEADER and struct.unpack_from("<i", data, hdr_end + 4)[0] == EXTRA_VERSION
	ofs, ln = lumps[LUMP_CLIPNODES]
	# same rule as xash3d mod_bmodel.c
	wide = ext and (ln % 8 != 0 or ln // 12 >= MAX_MAP_CLIPNODES_HLBSP)
	fmt, size = ("<iii", 12) if wide else ("<ihh", 8)
	if ln % size:
		raise SystemExit(f"clipnode lump length {ln} is not a multiple of {size}")
	clip = list(struct.iter_unpack(fmt, data[ofs:ofs + ln]))
	po, pl = lumps[LUMP_PLANES]
	planes = [p[:4] for p in struct.iter_unpack("<4fi", data[po:po + pl])]
	mo, ml = lumps[LUMP_MODELS]
	models = [struct.unpack_from("<9f4i3i", data, mo + i * 64) for i in range(ml // 64)]
	return {"ext": ext, "wide": wide, "clip": clip, "planes": planes, "models": models, "lumps": lumps}


def check(b) -> list[str]:
	errs = []
	n = len(b["clip"])
	for i, (pn, c0, c1) in enumerate(b["clip"]):
		if not 0 <= pn < len(b["planes"]):
			errs.append(f"clipnode {i}: plane {pn} out of range")
		for c in (c0, c1):
			if c >= n or (c < 0 and c not in CONTENTS and c > -20):
				errs.append(f"clipnode {i}: child {c} invalid")
	if errs:
		return errs
	# SDHLT shares identical subtrees, so the hulls form a DAG; make sure it has no cycle.
	state = [0] * n  # 0 new, 1 on stack, 2 done
	for mi, m in enumerate(b["models"]):
		for h in (1, 2, 3):
			hn = m[9 + h]
			if hn >= n:
				errs.append(f"model {mi} hull {h}: headnode {hn} out of range")
				continue
			stack = [(hn, 0)] if hn >= 0 else []
			while stack:
				node, k = stack.pop()
				if k == 0:
					if state[node] == 2:
						continue
					if state[node] == 1:
						errs.append(f"model {mi} hull {h}: cycle through clipnode {node}")
						return errs
					state[node] = 1
				if k < 2:
					stack.append((node, k + 1))
					c = b["clip"][node][1 + k]
					if c >= 0 and state[c] != 2:
						if state[c] == 1:
							errs.append(f"model {mi} hull {h}: cycle through clipnode {c}")
							return errs
						stack.append((c, 0))
				else:
					state[node] = 2
	return errs


def contents(b, hull: int, p, model: int = 0) -> int:
	node = b["models"][model][9 + hull]
	while node >= 0:
		pn, c0, c1 = b["clip"][node]
		nx, ny, nz, d = b["planes"][pn]
		node = c0 if nx * p[0] + ny * p[1] + nz * p[2] - d >= 0 else c1
	return node


def main(argv=None) -> int:
	ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	ap.add_argument("bsp")
	ap.add_argument("--point", nargs="+", type=float, metavar="N", help="x y z [hull]")
	a = ap.parse_args(argv)
	b = load(open(a.bsp, "rb").read())
	print(f"{a.bsp}: {'BSP30ext (XASH header)' if b['ext'] else 'BSP30'}, "
	      f"{len(b['clip'])} clipnodes ({'32' if b['wide'] else '16'}-bit), "
	      f"{len(b['planes'])} planes, {len(b['models'])} models")
	errs = check(b)
	for e in errs[:20]:
		print("  ERROR", e)
	if a.point:
		hull = int(a.point[3]) if len(a.point) > 3 else 1
		c = contents(b, hull, a.point[:3])
		print(f"  hull {hull} at {a.point[:3]}: {CONTENTS.get(c, c)}")
	return 1 if errs else 0


if __name__ == "__main__":
	sys.exit(main())
