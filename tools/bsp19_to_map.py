#!/usr/bin/env python3
"""Extract a MOHAA BSP's brushes into a GoldSrc Valve-220 .map for SDHLT.

First stage of the map pipeline: brushes only. Curved patches, LOD terrain
and static models are left out (they go to the render bake, and their
collision is decided separately). Output compiles with SDHLT
(sdHLCSG/sdHLBSP[/sdHLVIS/sdHLRAD]) into a BSP30 for dod-gc.

What it does:
  * rebuilds every brush from its planes (no texture coordinates exist on
    Q3-family brush sides, so faces get box-projected Valve-220 axes)
  * scales the world uniformly (default 72/94, MOHAA player -> GoldSrc hull)
  * maps MOHAA shaders to <=15-char WAD names; caulk/nodraw -> NULL,
    clip -> CLIP, sky -> sky, water -> !water, triggers -> AAATRIGGER
  * writes brush entities (doors, script objects) and player starts;
    other point entities are counted, not written
  * optionally writes a placeholder WAD3 with one flat texture per name

Usage:
  bsp19_to_map.py SOURCE -o out.map [--wad out.wad] [--scale S]
  SOURCE = file.bsp, or archive.pk3:maps/name.bsp
"""
from __future__ import annotations

import argparse
import hashlib
import math
import struct
import sys
import zipfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mohaa_bsp19 as b19  # noqa: E402

DEFAULT_SCALE = 72.0 / 94.0
GOLDSRC_HULL_HALF_HEIGHT = 36.0  # standing hull is -36..36 around the origin
EPS = 0.01
BIG = 1.0e5

# ---------------------------------------------------------------- geometry


def _dot(a, b):
	return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _sub(a, b):
	return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a, b):
	return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _norm(v):
	l = math.sqrt(_dot(v, v))
	return (v[0] / l, v[1] / l, v[2] / l) if l > 1e-12 else (0.0, 0.0, 0.0)


def base_winding(n, d):
	"""A huge quad on plane (n, d), wound so cross(p0-p1, p2-p1) points along n."""
	ax = max(range(3), key=lambda i: abs(n[i]))
	up = (0.0, 0.0, 1.0) if ax != 2 else (1.0, 0.0, 0.0)
	v = _sub(up, tuple(n[i] * _dot(up, n) for i in range(3)))
	v = _norm(v)
	r = _cross(v, n)
	org = tuple(n[i] * d for i in range(3))
	v = tuple(c * BIG for c in v)
	r = tuple(c * BIG for c in r)
	w = [
		tuple(org[i] - r[i] + v[i] for i in range(3)),
		tuple(org[i] + r[i] + v[i] for i in range(3)),
		tuple(org[i] + r[i] - v[i] for i in range(3)),
		tuple(org[i] - r[i] - v[i] for i in range(3)),
	]
	return w if _dot(_cross(_sub(w[0], w[1]), _sub(w[2], w[1])), n) > 0 else w[::-1]


def clip_winding(w, n, d):
	"""Keep the part of w behind plane (n, d) (dot(p, n) <= d)."""
	if not w:
		return w
	dists = [_dot(p, n) - d for p in w]
	if all(x <= EPS for x in dists):
		return w
	if all(x >= -EPS for x in dists):
		return []
	out = []
	for i, p in enumerate(w):
		q = w[(i + 1) % len(w)]
		dp, dq = dists[i], dists[(i + 1) % len(w)]
		if dp <= EPS:
			out.append(p)
		if (dp < -EPS and dq > EPS) or (dp > EPS and dq < -EPS):
			t = dp / (dp - dq)
			out.append(tuple(p[k] + t * (q[k] - p[k]) for k in range(3)))
	return out


def winding_area(w):
	if len(w) < 3:
		return 0.0
	total = (0.0, 0.0, 0.0)
	for i in range(1, len(w) - 1):
		c = _cross(_sub(w[i], w[0]), _sub(w[i + 1], w[0]))
		total = (total[0] + c[0], total[1] + c[1], total[2] + c[2])
	return 0.5 * math.sqrt(_dot(total, total))


def brush_faces(planes):
	"""planes: list of (normal, dist, payload). Returns [(normal, dist, winding, payload)]
	for every side that keeps a real face; duplicate planes are dropped."""
	seen = set()
	uniq = []
	for n, d, pay in planes:
		key = (round(n[0], 4), round(n[1], 4), round(n[2], 4), round(d, 2))
		if key in seen:
			continue
		seen.add(key)
		uniq.append((n, d, pay))
	faces = []
	for i, (n, d, pay) in enumerate(uniq):
		w = base_winding(n, d)
		for j, (n2, d2, _) in enumerate(uniq):
			if i != j:
				w = clip_winding(w, n2, d2)
				if not w:
					break
		if len(w) >= 3 and winding_area(w) > 0.1:
			faces.append((n, d, w, pay))
	return faces


def three_points(n, w):
	"""Three well-spread winding points ordered for Valve-220 (cross(p0-p1, p2-p1) along n)."""
	best = None
	m = len(w)
	for a in range(m):
		for b in range(a + 1, m):
			for c in range(b + 1, m):
				area = _dot(_cross(_sub(w[a], w[b]), _sub(w[c], w[b])), n)
				if best is None or abs(area) > abs(best[0]):
					best = (area, w[a], w[b], w[c])
		if m > 12 and best and abs(best[0]) > 1.0:
			break
	area, p0, p1, p2 = best
	return (p0, p1, p2) if area > 0 else (p2, p1, p0)


def texture_axes(n):
	"""Quake-style box projection: pick the axis plane closest to the face."""
	ax = max(range(3), key=lambda i: abs(n[i]))
	if ax == 2:
		return (1.0, 0.0, 0.0), (0.0, -1.0, 0.0)
	if ax == 0:
		return (0.0, 1.0, 0.0), (0.0, 0.0, -1.0)
	return (1.0, 0.0, 0.0), (0.0, 0.0, -1.0)


def _f(v):
	s = f"{v:.3f}".rstrip("0").rstrip(".")
	return "0" if s in ("-0", "") else s


# ---------------------------------------------------------------- textures


class TextureNamer:
	"""MOHAA shader path -> unique <=15-char WAD-safe name."""

	SPECIAL = {"NULL", "CLIP", "sky", "!water", "AAATRIGGER", "ORIGIN"}

	def __init__(self):
		self.by_shader = {}
		self.used = set()
		self.special_used = set()  # sky / !water / AAATRIGGER need WAD entries too

	def name(self, shader: str) -> str:
		if shader in self.by_shader:
			return self.by_shader[shader]
		base = shader.replace("\\", "/").rsplit("/", 1)[-1].lower()
		base = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in base) or "tex"
		cand = base[:15]
		if cand in self.used or cand.upper() in {s.upper() for s in self.SPECIAL}:
			h = hashlib.md5(shader.encode()).hexdigest()[:4]
			cand = base[:10] + "_" + h
		self.used.add(cand)
		self.by_shader[shader] = cand
		return cand


def side_texture(sh: b19.Shader, namer: TextureNamer, brush_class: str) -> str:
	tex = _side_texture(sh, namer, brush_class)
	if tex in ("sky", "!water", "AAATRIGGER"):
		namer.special_used.add(tex)
	return tex


def _side_texture(sh: b19.Shader, namer: TextureNamer, brush_class: str) -> str:
	low = sh.name.lower()
	if brush_class == "clip":
		return "CLIP"
	if brush_class == "trigger":
		return "AAATRIGGER"
	if brush_class == "water":
		return "!water"
	if sh.surface_flags & b19.SURF_SKY or "/sky" in low:
		return "sky"
	if sh.surface_flags & b19.SURF_NODRAW or "caulk" in low or "nodraw" in low:
		return "NULL"
	return namer.name(sh.name)


def classify(contents: int) -> str:
	if contents & b19.CONTENTS_ORIGIN:
		return "origin"
	if contents & (b19.CONTENTS_AREAPORTAL | b19.CONTENTS_FOG) and not contents & b19.CONTENTS_SOLID:
		return "skip"
	if contents & b19.CONTENTS_TRIGGER:
		return "trigger"
	if contents & b19.CONTENTS_FLUID:
		return "water"
	if contents & (b19.CONTENTS_SOLID | b19.CONTENTS_FENCE):
		return "detail" if contents & b19.CONTENTS_DETAIL else "solid"
	if contents & b19.CONTENTS_ANYCLIP:
		return "clip"
	return "nonsolid"


# ---------------------------------------------------------------- entities

PLAYER_STARTS = {
	"info_player_start": ["info_player_start", "info_player_allies"],
	"info_player_allied": ["info_player_allies"],
	"info_player_axis": ["info_player_axis"],
	"info_player_deathmatch": ["info_player_allies", "info_player_axis"],
	"info_player_intermission": ["info_intermission"],
}

BRUSH_CLASS_MAP = {
	"func_door": "func_door",
	"func_rotatingdoor": "func_door_rotating",
	"func_door_rotating": "func_door_rotating",
	"func_explodingwall": "func_breakable",
	"func_window": "func_breakable",
}
ROTATING = {"func_door_rotating"}


def parse_vec(s, default=(0.0, 0.0, 0.0)):
	try:
		v = [float(x) for x in s.split()]
		return tuple(v[:3]) if len(v) >= 3 else default
	except (ValueError, AttributeError):
		return default


# ---------------------------------------------------------------- convert


def brush_text(bsp, brush, scale, offset, namer, stats, cls):
	planes = []
	for si in range(brush.first_side, brush.first_side + brush.num_sides):
		if si >= len(bsp.brushsides):
			break
		pi, shi = bsp.brushsides[si]
		if not 0 <= pi < len(bsp.planes):
			continue
		nx, ny, nz, dist = bsp.planes[pi]
		n = (nx, ny, nz)
		d = (dist + _dot(n, offset)) * scale
		sh = bsp.shaders[shi] if 0 <= shi < len(bsp.shaders) else b19.Shader("", 0, 0, 0)
		planes.append((n, d, sh))
	faces = brush_faces(planes)
	if len(faces) < 4:
		stats["brushes_degenerate"] += 1
		return None
	lines = ["{"]
	for n, d, w, sh in faces:
		tex = side_texture(sh, namer, cls)
		p0, p1, p2 = three_points(n, w)
		u, v = texture_axes(n)
		pts = " ".join("( %s %s %s )" % tuple(_f(c) for c in p) for p in (p0, p1, p2))
		lines.append(f"{pts} {tex} [ {_f(u[0])} {_f(u[1])} {_f(u[2])} 0 ] [ {_f(v[0])} {_f(v[1])} {_f(v[2])} 0 ] 0 1 1")
		stats["faces"] += 1
	lines.append("}")
	return "\n".join(lines)


def origin_brush(o, half=8.0):
	x, y, z = o
	lo = (x - half, y - half, z - half)
	hi = (x + half, y + half, z + half)
	faces = []
	for ax in range(3):
		for sign in (1, -1):
			n = [0.0, 0.0, 0.0]
			n[ax] = float(sign)
			d = hi[ax] if sign > 0 else -lo[ax]
			faces.append((tuple(n), d, None))
	out = ["{"]
	for n, d, w, _ in brush_faces(faces):
		p0, p1, p2 = three_points(n, w)
		u, v = texture_axes(n)
		pts = " ".join("( %s %s %s )" % tuple(_f(c) for c in p) for p in (p0, p1, p2))
		out.append(f"{pts} ORIGIN [ {_f(u[0])} {_f(u[1])} {_f(u[2])} 0 ] [ {_f(v[0])} {_f(v[1])} {_f(v[2])} 0 ] 0 1 1")
	out.append("}")
	return "\n".join(out)


def model_brushes(bsp, model_index, scale, offset, namer, stats):
	m = bsp.models[model_index]
	out = []
	for bi in range(m.first_brush, m.first_brush + m.num_brushes):
		br = bsp.brushes[bi]
		sh = bsp.shaders[br.shader] if 0 <= br.shader < len(bsp.shaders) else b19.Shader("", 0, 0, 0)
		cls = classify(sh.content_flags)
		stats["brush_class_" + cls] += 1
		if cls in ("origin", "skip", "nonsolid"):
			continue
		if cls == "water" and model_index == 0:
			pass
		txt = brush_text(bsp, br, scale, offset, namer, stats, cls)
		if txt:
			out.append((cls, txt))
	return out


def kv_block(keys, brushes=()):
	lines = ["{"]
	for k, v in keys.items():
		lines.append(f'"{k}" "{v}"')
	lines.extend(brushes)
	lines.append("}")
	return "\n".join(lines)


def convert(bsp: b19.Bsp, scale: float = DEFAULT_SCALE, wad_name: str | None = None):
	namer = TextureNamer()
	stats = Counter()
	world = bsp.entities[0] if bsp.entities else {"classname": "worldspawn"}
	ws_keys = {"classname": "worldspawn", "mapversion": "220"}
	if wad_name:
		ws_keys["wad"] = wad_name
	if "message" in world:
		ws_keys["message"] = world["message"]
	ws_keys["mohaa_source"] = bsp.name.replace('"', "'")

	world_brushes = []
	detail = []
	for cls, txt in model_brushes(bsp, 0, scale, (0.0, 0.0, 0.0), namer, stats):
		(detail if cls == "detail" else world_brushes).append(txt)
		stats["world_brushes_written"] += 1
	blocks = [kv_block(ws_keys, world_brushes)]
	if detail:
		# SDHLT func_detail keeps MOHAA's detail brushes out of the vis tree.
		blocks.append(kv_block({"classname": "func_detail", "zhlt_detaillevel": "1"}, detail))

	skipped = Counter()
	for e in bsp.entities[1:]:
		cn = e.get("classname", "")
		model = e.get("model", "")
		if model.startswith("*"):
			try:
				mi = int(model[1:])
			except ValueError:
				mi = -1
			if not 0 < mi < len(bsp.models):
				skipped[cn + " (bad model)"] += 1
				continue
			if cn.startswith("trigger_"):
				skipped[cn] += 1
				continue
			gcn = BRUSH_CLASS_MAP.get(cn, "func_wall")
			o = parse_vec(e.get("origin", ""))
			brushes = [t for _, t in model_brushes(bsp, mi, scale, o, namer, stats)]
			if not brushes:
				skipped[cn + " (no brushes)"] += 1
				continue
			keys = {"classname": gcn, "mohaa_classname": cn}
			for k in ("targetname", "target", "angle", "angles", "speed", "wait", "lip"):
				if k in e:
					keys[k] = e[k]
			if gcn in ROTATING:
				brushes.append(origin_brush(tuple(c * scale for c in o)))
			blocks.append(kv_block(keys, brushes))
			stats["brush_entities_written"] += 1
			continue
		if cn in PLAYER_STARTS:
			ox, oy, oz = parse_vec(e.get("origin", ""))
			org = f"{_f(ox * scale)} {_f(oy * scale)} {_f(oz * scale + GOLDSRC_HULL_HALF_HEIGHT + 1)}"
			for gcn in PLAYER_STARTS[cn]:
				keys = {"classname": gcn, "origin": org}
				if "angle" in e:
					keys["angle"] = e["angle"]
				blocks.append(kv_block(keys))
				stats["player_starts_written"] += 1
			continue
		skipped[cn] += 1

	if not stats["player_starts_written"]:
		# A map with no start can't be walked; drop one above the world centre.
		m = bsp.models[0]
		c = [(m.mins[i] + m.maxs[i]) * 0.5 * scale for i in range(3)]
		c[2] = m.maxs[2] * scale - 64
		for gcn in ("info_player_start", "info_player_allies", "info_player_axis"):
			blocks.append(kv_block({"classname": gcn, "origin": " ".join(_f(v) for v in c)}))
		stats["player_starts_fallback"] += 1

	text = "// generated by mohaa-gc tools/bsp19_to_map.py from " + bsp.name + "\n" + "\n".join(blocks) + "\n"
	return text, namer, stats, skipped


# ---------------------------------------------------------------- WAD3


def _placeholder_mips(name: str, size: int = 64):
	"""Two-tone checker in a colour derived from the name, all 4 mip levels."""
	h = hashlib.md5(name.encode()).digest()
	base = (64 + h[0] % 160, 64 + h[1] % 160, 64 + h[2] % 160)
	palette = bytearray(768)
	palette[0:3] = bytes(base)
	palette[3:6] = bytes(max(0, c - 40) for c in base)
	palette[765:768] = b"\x00\x00\xff"  # index 255 blue (transparent key in GoldSrc)
	mips = []
	for level in range(4):
		s = size >> level
		cell = max(1, 16 >> level)
		mips.append(bytes(((x // cell + y // cell) & 1) for y in range(s) for x in range(s)))
	return mips, bytes(palette)


def write_wad(path: Path, names):
	size = 64
	lumps = []
	for name in sorted(set(names)):
		mips, palette = _placeholder_mips(name, size)
		header_len = 16 + 4 + 4 + 16
		offsets = []
		pos = header_len
		for m in mips:
			offsets.append(pos)
			pos += len(m)
		body = struct.pack("<16sII4I", name.encode()[:15], size, size, *offsets)
		body += b"".join(mips) + struct.pack("<H", 256) + palette + b"\x00\x00"
		lumps.append((name, body))
	out = bytearray(b"WAD3" + struct.pack("<ii", len(lumps), 0))
	entries = []
	for name, body in lumps:
		entries.append((len(out), len(body), name))
		out += body
	dir_ofs = len(out)
	for ofs, ln, name in entries:
		out += struct.pack("<iiibbh16s", ofs, ln, ln, 0x43, 0, 0, name.encode()[:15])
	struct.pack_into("<i", out, 8, dir_ofs)
	path.write_bytes(bytes(out))


# ---------------------------------------------------------------- CLI


def read_source(src: str) -> tuple[str, bytes]:
	if ".pk3:" in src.lower():
		i = src.lower().index(".pk3:") + 4
		pak, inner = src[:i], src[i + 1:]
		with zipfile.ZipFile(pak) as z:
			names = {n.lower(): n for n in z.namelist()}
			real = names.get(inner.lower())
			if not real:
				raise SystemExit(f"{inner} not found in {pak}")
			return f"{Path(pak).name}:{real}", z.read(real)
	return src, Path(src).read_bytes()


def main(argv=None) -> int:
	ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
	ap.add_argument("source")
	ap.add_argument("-o", "--out", type=Path, required=True, help="output .map")
	ap.add_argument("--wad", type=Path, help="also write a placeholder WAD3 with every used texture")
	ap.add_argument("--scale", type=float, default=DEFAULT_SCALE)
	args = ap.parse_args(argv)

	name, data = read_source(args.source)
	bsp = b19.load_bytes(data, name)
	wad_key = str(args.wad.resolve()) if args.wad else None
	text, namer, stats, skipped = convert(bsp, args.scale, wad_key)
	args.out.write_text(text)
	if args.wad:
		write_wad(args.wad, list(namer.by_shader.values()) + sorted(namer.special_used))
	print(f"{name}: wrote {args.out}")
	for k in sorted(stats):
		print(f"  {k:<28} {stats[k]}")
	print(f"  textures                     {len(namer.by_shader)}")
	if skipped:
		print("  point/brush entities not written: " + ", ".join(f"{k} x{v}" for k, v in skipped.most_common(15)))
	return 0


if __name__ == "__main__":
	sys.exit(main())
