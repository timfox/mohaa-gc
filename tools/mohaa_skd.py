#!/usr/bin/env python3
"""Read MOHAA static model meshes: .tik model scripts and the SKMD (.skd) meshes they name.

    python3 tools/mohaa_skd.py "/path/to/MOHAA/main" --props out/m6l1a.props

The CLI reads every model a .props sidecar lists from the paks and prints each one's LOD 0
triangle and vertex counts, bounds, vertex layout and surfaces with their textures. That checks the
reader against the real files before the engine draws anything. It prints numbers and names only.

Written from the file layout (header, surfaces, triangles, weighted vertices), not from any game
or GPL source. A vertex's position is the weighted sum of its bone-space offsets. Static props
are rigged to one root bone at the origin, so the offsets are already the bind pose.
"""
from __future__ import annotations

import argparse
import os
import re
import struct
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SKD_IDENT = b"SKMD"
SURF_IDENT = b"SKSF"
# ident, version, name[64], numSurfaces, numBones, ofsBones, ofsSurfaces, ofsEnd
HEADER = struct.Struct("<4si64s5i")
# ident, name[64], numTriangles, numVerts, staticSurfProcessed, ofsTriangles, ofsVerts,
# ofsCollapse, ofsEnd, ofsCollapseIndex
SURFACE = struct.Struct("<4s64s8i")
WEIGHT = struct.Struct("<if3f")  # bone, weight, offset
MORPH = struct.Struct("<i3f")  # morph target, offset


class SkdError(ValueError):
	pass


@dataclass
class Surface:
	name: str
	triangles: list  # (a, b, c) vertex indices
	positions: list  # (x, y, z)
	normals: list
	uvs: list  # (s, t)
	layout: str = ""  # which vertex record the file uses: "weights" or "morphs+weights"


@dataclass
class Skd:
	name: str
	version: int
	num_bones: int
	surfaces: list = field(default_factory=list)

	@property
	def num_triangles(self):
		return sum(len(s.triangles) for s in self.surfaces)

	@property
	def num_verts(self):
		return sum(len(s.positions) for s in self.surfaces)

	def bounds(self):
		pts = [p for s in self.surfaces for p in s.positions]
		if not pts:
			return (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)
		return tuple(min(p[i] for p in pts) for i in range(3)), tuple(max(p[i] for p in pts) for i in range(3))


def _cstr(b: bytes) -> str:
	return b.split(b"\0", 1)[0].decode("latin-1", "replace")


def _vertices(data, start, end, count, num_bones, morphs):
	"""count vertices from data[start:end], or None when the bytes don't read as this layout."""
	pos, out = start, []
	for _ in range(count):
		if pos + 24 > end:
			return None
		nx, ny, nz, s, t, nw = struct.unpack_from("<5fi", data, pos)
		pos += 24
		nm = 0
		if morphs:
			if pos + 4 > end:
				return None
			nm = struct.unpack_from("<i", data, pos)[0]
			pos += 4
			if not 0 <= nm <= 64:
				return None
			pos += nm * MORPH.size
		if not 1 <= nw <= 8 or pos + nw * WEIGHT.size > end:
			return None
		x = y = z = 0.0
		total = 0.0
		for _ in range(nw):
			bone, w, ox, oy, oz = WEIGHT.unpack_from(data, pos)
			pos += WEIGHT.size
			if not 0 <= bone < max(num_bones, 1) or not -0.01 <= w <= 1.01:
				return None
			x, y, z, total = x + w * ox, y + w * oy, z + w * oz, total + w
		if not 0.9 <= total <= 1.1:
			return None
		out.append(((x, y, z), (nx, ny, nz), (s, t)))
	return out, pos


def parse_skd(data: bytes, name: str = "") -> Skd:
	if len(data) < HEADER.size:
		raise SkdError(f"{name}: too short for an SKMD header")
	ident, version, mname, nsurf, nbones, _ofs_bones, ofs_surf, ofs_end = HEADER.unpack_from(data, 0)
	if ident != SKD_IDENT:
		raise SkdError(f"{name}: not an SKMD file")
	if not 0 <= nsurf <= 256 or not 0 < ofs_surf < len(data):
		raise SkdError(f"{name}: bad surface table ({nsurf} at {ofs_surf})")
	skd = Skd(_cstr(mname) or name, version, nbones)
	at = ofs_surf
	for i in range(nsurf):
		if at + SURFACE.size > len(data):
			raise SkdError(f"{name}: surface {i} runs past the file")
		sident, sname, ntri, nvert, _proc, ofs_tri, ofs_vert, ofs_col, ofs_send, ofs_colidx = \
			SURFACE.unpack_from(data, at)
		if sident != SURF_IDENT or ntri < 0 or nvert < 0 or ofs_send <= 0:
			raise SkdError(f"{name}: surface {i} has a bad header")
		tris = []
		for k in range(ntri):
			a, b, c = struct.unpack_from("<3i", data, at + ofs_tri + 12 * k)
			if not (0 <= a < nvert and 0 <= b < nvert and 0 <= c < nvert):
				raise SkdError(f"{name}: surface {i} triangle {k} names a missing vertex")
			tris.append((a, b, c))
		# the vertex block ends where the next part of the surface starts
		vstart = at + ofs_vert
		vend = min([at + o for o in (ofs_tri, ofs_col, ofs_colidx, ofs_send) if o > ofs_vert] or [len(data)])
		got = None
		for morphs in (False, True):
			got = _vertices(data, vstart, vend, nvert, nbones, morphs)
			if got and got[1] == vend:
				layout = "morphs+weights" if morphs else "weights"
				break
			got = None
		if got is None:
			raise SkdError(f"{name}: surface {i} vertices match no known layout")
		verts = got[0]
		skd.surfaces.append(Surface(_cstr(sname), tris, [v[0] for v in verts], [v[1] for v in verts],
		                            [v[2] for v in verts], layout))
		at += ofs_send
	return skd


# ---------------------------------------------------------------- .tik and shaders

@dataclass
class Tik:
	path: str = ""
	skelmodel: str = ""
	scale: float = 1.0
	shaders: dict = field(default_factory=dict)  # surface name (or "all"/"*") -> shader

	@property
	def mesh(self):
		if not self.skelmodel:
			return ""
		return norm(self.skelmodel if "/" in self.skelmodel else f"{self.path}/{self.skelmodel}")


def norm(path: str) -> str:
	return re.sub(r"/+", "/", path.strip().strip('"').replace("\\", "/")).lower().lstrip("/")


def parse_tik(text: str) -> Tik:
	"""The setup block's mesh, scale and surface shaders. Other blocks (init, animations) are ignored."""
	tik = Tik()
	for raw in text.splitlines():
		line = raw.split("//", 1)[0].strip()
		words = line.replace("{", " ").replace("}", " ").split()
		if not words:
			continue
		key = words[0].lower()
		if key == "path" and len(words) > 1:
			tik.path = norm(words[1])
		elif key == "skelmodel" and len(words) > 1:
			tik.skelmodel = words[1].strip('"')
		elif key == "scale" and len(words) > 1:
			try:
				tik.scale = float(words[1])
			except ValueError:
				pass
		elif key == "surface" and len(words) > 3 and words[2].lower() == "shader":
			tik.shaders[words[1].lower()] = words[3].strip('"')
	return tik


def parse_shaders(text: str) -> dict:
	"""{shader name: first texture its stages map}, from a scripts/*.shader file."""
	out, depth, name, want = {}, 0, None, False
	for tok in re.findall(r'"[^"]*"|\{|\}|[^\s{}]+', re.sub(r"//[^\n]*", "", text)):
		if tok == "{":
			depth += 1
		elif tok == "}":
			depth = max(depth - 1, 0)
			name = None if depth == 0 else name
			want = False
		elif depth == 0:
			name = tok.strip('"').lower()
		elif depth == 2 and tok.lower() in ("map", "clampmap", "animmap"):
			want = name is not None and name not in out
		elif want:
			if re.fullmatch(r"[\d.]+", tok):
				continue  # animmap's frame rate
			want = False
			if not tok.startswith("$"):  # $lightmap, $whiteimage: not a texture
				out[name] = norm(tok)
	return out


def surface_texture(tik: Tik, surface: str, shaders: dict) -> str:
	sh = tik.shaders.get(surface.lower()) or tik.shaders.get("all") or tik.shaders.get("*") or ""
	return shaders.get(sh.lower(), norm(sh)) if sh else ""


# ---------------------------------------------------------------- CLI

def props_models(path) -> dict:
	"""{model path: instance count} from a .props sidecar."""
	counts = {}
	with open(path) as f:
		for line in f:
			if line.startswith("#") or not line.strip():
				continue
			model = norm(line.rsplit(" ", 1)[1].replace("%20", " ").replace("%25", "%"))
			counts[model] = counts.get(model, 0) + 1
	return counts


def main(argv=None) -> int:
	from ubersound import collect, read

	ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
	ap.add_argument("main", nargs="+", help="MOHAA main folder or pk3 files")
	ap.add_argument("--props", action="append", required=True, help="a <map>.props sidecar (repeatable)")
	args = ap.parse_args(argv)
	files = collect(args.main, (".tik", ".skd", ".shader"))
	shaders = {}
	for p, e in sorted(files.items()):
		if p.endswith(".shader"):
			shaders.update(parse_shaders(read(e).decode("latin-1")))
	counts = {}
	for pp in args.props:
		for m, n in props_models(pp).items():
			counts[m] = counts.get(m, 0) + n
	total_tris = bad = 0
	print(f"{'instances':>9} {'tris':>5} {'verts':>5} layout          bounds                         model")
	for model, n in sorted(counts.items(), key=lambda kv: -kv[1]):
		key = model if model.startswith("models/") else "models/" + model
		if key not in files:
			print(f"{n:>9}     -     - missing .tik                                       {model}")
			bad += 1
			continue
		tik = parse_tik(read(files[key]).decode("latin-1"))
		if tik.mesh not in files:
			print(f"{n:>9}     -     - missing {tik.mesh or 'skelmodel'}  {model}")
			bad += 1
			continue
		try:
			skd = parse_skd(read(files[tik.mesh]), tik.mesh)
		except SkdError as err:
			print(f"{n:>9}     -     - {err}")
			bad += 1
			continue
		lo, hi = skd.bounds()
		layouts = ",".join(sorted({s.layout for s in skd.surfaces}))
		box = " ".join(f"{h - l:.0f}" for l, h in zip(lo, hi))
		print(f"{n:>9} {skd.num_triangles:>5} {skd.num_verts:>5} v{skd.version} {layouts:<14} size {box:<22} {model}"
		      f" (scale {tik.scale:g})")
		for s in skd.surfaces:
			print(f"{'':>17}{s.name}: {len(s.triangles)} tris -> {surface_texture(tik, s.name, shaders) or '?'}")
		total_tris += n * skd.num_triangles
	print(f"{len(counts)} models, {sum(counts.values())} instances, {total_tris} triangles if all drawn, {bad} unread")
	return 1 if bad else 0


if __name__ == "__main__":
	sys.exit(main())
