#!/usr/bin/env python3
"""Read MOHAA static model meshes: .tik model scripts and their SKMD (.skd) or SKL (.skb) meshes.

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
SURF_IDENTS = (b"SKL ", b"SKSF")  # MOHAA's v5 files start each surface with "SKL "
# Both SKMD (.skd) and retail SKL (.skb) headers share these leading fields;
# SKL appends LOD and hitbox fields after ofsEnd.
HEADER = struct.Struct("<4si64s5i")
# ident, name[64], numTriangles, numVerts, staticSurfProcessed, ofsTriangles, ofsVerts,
# ofsCollapse, ofsEnd, ofsCollapseIndex
SURFACE = struct.Struct("<4s64s8i")
BONE = struct.Struct("<32s32s5i")
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
	weights: list = field(default_factory=list)  # per vertex: [(bone, weight, (ox, oy, oz))]


@dataclass
class Skd:
	name: str
	version: int
	num_bones: int
	bones: list = field(default_factory=list)  # bone names, in index order
	bone_parents: list = field(default_factory=list)  # parent names, parallel to bones
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
		ws = []
		for _ in range(nw):
			bone, w, ox, oy, oz = WEIGHT.unpack_from(data, pos)
			pos += WEIGHT.size
			if not 0 <= bone < max(num_bones, 1) or not -0.01 <= w <= 1.01:
				return None
			x, y, z, total = x + w * ox, y + w * oy, z + w * oz, total + w
			ws.append((bone, w, (ox, oy, oz)))
		if not 0.9 <= total <= 1.1:
			return None
		out.append(((x, y, z), (nx, ny, nz), (s, t), ws))
	return out, pos


def parse_skd(data: bytes, name: str = "") -> Skd:
	if len(data) < HEADER.size:
		raise SkdError(f"{name}: too short for an SKMD header")
	ident, version, mname, nsurf, nbones, _ofs_bones, ofs_surf, ofs_end = HEADER.unpack_from(data, 0)
	if ident not in (SKD_IDENT, b"SKL "):
		raise SkdError(f"{name}: not an SKMD or SKL file")
	if not 0 <= nsurf <= 256 or not 0 < ofs_surf < len(data):
		raise SkdError(f"{name}: bad surface table ({nsurf} at {ofs_surf})")
	skd = Skd(_cstr(mname) or name, version, nbones)
	# bone records: name[32], parent[32], joint type, then offsets of values, channels, refs and the
	# record's end. They hold names and joint settings only; the pose comes from an animation.
	at = _ofs_bones
	for _ in range(nbones if 0 < _ofs_bones < len(data) else 0):
		if at + BONE.size > len(data):
			break
		bname, parent, _jtype, _ov, _oc, _orf, oend = BONE.unpack_from(data, at)
		skd.bones.append(_cstr(bname))
		skd.bone_parents.append(_cstr(parent))
		if oend < BONE.size:
			break
		at += oend
	at = ofs_surf
	for i in range(nsurf):
		if at + SURFACE.size > len(data):
			raise SkdError(f"{name}: surface {i} runs past the file")
		sident, sname, ntri, nvert, _proc, ofs_tri, ofs_vert, ofs_col, ofs_send, ofs_colidx = \
			SURFACE.unpack_from(data, at)
		if sident not in SURF_IDENTS or ntri < 0 or nvert < 0 or ofs_send <= 0:
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
		                            [v[2] for v in verts], layout, [v[3] for v in verts]))
		at += ofs_send
	return skd


def _rotate(q, v):
	"""v turned by quaternion q = (x, y, z, w), applied the way MOHAA's skeletor does: the inverse of
	the textbook q v q* (checked on ceres: the props' idle quaternion (.5, .5, .5, -.5) has to turn a
	mesh's x, y, z into the world's y, z, x for their heights to land on z)."""
	qx, qy, qz, qw = -q[0], -q[1], -q[2], q[3]
	tx = 2 * (qy * v[2] - qz * v[1])
	ty = 2 * (qz * v[0] - qx * v[2])
	tz = 2 * (qx * v[1] - qy * v[0])
	return (v[0] + qw * tx + (qy * tz - qz * ty),
	        v[1] + qw * ty + (qz * tx - qx * tz),
	        v[2] + qw * tz + (qx * ty - qy * tx))


def apply_pose(skd: Skd, pose: dict) -> None:
	"""Re-place every vertex with its bones posed: pose maps a bone name to (position, quaternion).
	Bones the pose lacks stay where the offsets put them."""
	for s in skd.surfaces:
		for i, ws in enumerate(s.weights):
			x = y = z = 0.0
			for bone, w, off in ws:
				name = skd.bones[bone] if bone < len(skd.bones) else ""
				pos, q = pose.get(name.lower(), ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0)))
				r = _rotate(q, off)
				x, y, z = x + w * (r[0] + pos[0]), y + w * (r[1] + pos[1]), z + w * (r[2] + pos[2])
			s.positions[i] = (x, y, z)
		s.normals = [_rotate(pose.get(skd.bones[ws[0][0]].lower() if ws and ws[0][0] < len(skd.bones) else "",
		                              (None, (0.0, 0.0, 0.0, 1.0)))[1], n) for ws, n in zip(s.weights, s.normals)]


SKC_IDENT = b"SKAN"
# ident, version, flags, bytes used, frame time, total delta[3], total angle delta, channels,
# ofs channel names, frames
SKC_HEADER = struct.Struct("<4s3if3ff3i")
# bounds min[3], max[3], radius, delta[3], angle delta, ofs channels (from the file start)
SKC_FRAME = struct.Struct("<3f3ff3ffi")


def parse_skc_animation(data: bytes, name: str = "") -> dict:
	"""Read all SKAN frames as per-bone (position, quaternion) poses.

	Channels are "<bone> pos" and "<bone> rot", four floats each (pos uses
	xyz plus a spare; rot uses xyzw). Frame channel offsets are absolute file
	offsets, as in the retail SKCs used by the TIKI converter.
	"""
	if len(data) < SKC_HEADER.size + SKC_FRAME.size:
		raise SkdError(f"{name}: too short for an SKAN header")
	(ident, _ver, _flags, used, frame_time, dx, dy, dz, angle_delta,
	 nchan, ofs_names, nframes) = SKC_HEADER.unpack_from(data, 0)
	limit = used if used else len(data)
	frame_table_end = SKC_HEADER.size + nframes * SKC_FRAME.size
	if (ident != SKC_IDENT or nframes < 1 or not 0 < nchan <= 512 or
			limit > len(data) or limit < SKC_HEADER.size or
			frame_table_end > limit or ofs_names < frame_table_end or
			ofs_names + 32 * nchan > limit):
		raise SkdError(f"{name}: not a readable SKAN file")

	channels = []
	for i in range(nchan):
		cname = _cstr(data[ofs_names + 32 * i:ofs_names + 32 * (i + 1)]).lower()
		bone, _, kind = cname.rpartition(" ")
		channels.append((bone, kind) if bone and kind in ("pos", "rot") else ("", ""))

	poses = []
	for frame in range(nframes):
		ofs_frame = SKC_HEADER.size + frame * SKC_FRAME.size
		ofs_chan = SKC_FRAME.unpack_from(data, ofs_frame)[-1]
		if ofs_chan < frame_table_end or ofs_chan + 16 * nchan > limit:
			raise SkdError(f"{name}: frame {frame} channels run past the file")
		pose = {}
		for i, (bone, kind) in enumerate(channels):
			if not bone:
				continue
			vals = struct.unpack_from("<4f", data, ofs_chan + 16 * i)
			pos, q = pose.get(bone, (None, None))
			if kind == "pos":
				pos = vals[:3]
			else:
				q = vals
			pose[bone] = (pos, q)
		poses.append(pose)

	return {
		"frame_time": frame_time,
		"delta": (dx, dy, dz),
		"angle_delta": angle_delta,
		"poses": poses,
	}


def parse_skc(data: bytes, name: str = "") -> dict:
	"""Frame 0 as a complete pose, retained for existing static-pose callers."""
	pose = parse_skc_animation(data, name)["poses"][0]
	return {
		bone: (pos if pos is not None else (0.0, 0.0, 0.0),
		       q if q is not None else (0.0, 0.0, 0.0, 1.0))
		for bone, (pos, q) in pose.items()
	}


# ---------------------------------------------------------------- .tik and shaders

@dataclass
class Tik:
	path: str = ""
	skelmodel: str = ""
	scale: float = 1.0
	shaders: dict = field(default_factory=dict)  # surface name (or "all"/"*") -> shader
	idle: str = ""  # the idle animation, whose frame 0 is the model's pose

	def _resolve(self, f):
		return norm(f if "/" in f else f"{self.path}/{f}") if f else ""

	@property
	def idle_anim(self):
		return self._resolve(self.idle)

	@property
	def mesh(self):
		if not self.skelmodel:
			return ""
		return norm(self.skelmodel if "/" in self.skelmodel else f"{self.path}/{self.skelmodel}")


def norm(path: str) -> str:
	return re.sub(r"/+", "/", path.strip().strip('"').replace("\\", "/")).lower().lstrip("/")


def parse_tik(text: str) -> Tik:
	"""The setup block's mesh, scale and surface shaders, and the idle animation. Other keys are ignored."""
	tik = Tik()
	seen_scale = False
	toks = [t.strip('"') for t in re.findall(r'"[^"]*"|[^\s{}]+', re.sub(r"//[^\n]*", "", text))]
	for i, tok in enumerate(toks[:-1]):
		key, val = tok.lower(), toks[i + 1]
		# the first of each is setup's; later blocks (init, client) can reuse the words
		if key == "path" and not tik.path:
			tik.path = norm(val)
		elif key == "skelmodel" and not tik.skelmodel:
			tik.skelmodel = val
		elif key == "scale" and not seen_scale:
			seen_scale = True
			try:
				tik.scale = float(val)
			except ValueError:
				pass
		elif key == "idle" and not tik.idle:
			tik.idle = val
		elif key == "surface" and i + 3 < len(toks) and toks[i + 2].lower() == "shader":
			tik.shaders[val.lower()] = toks[i + 3]
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


def parse_shader_blends(text: str) -> dict:
	"""{shader name: "filter" or "add"} for shaders whose first mapped stage blends by colour, not alpha:
	a filter (GL_DST_COLOR GL_ZERO, GL_ZERO GL_SRC_COLOR) darkens through a mostly white image, an add
	(GL_ONE GL_ONE) brightens through a mostly black one. Drawn opaque, both show their background."""
	out, depth, name, stage, first = {}, 0, None, [], set()
	toks = re.findall(r'"[^"]*"|\{|\}|[^\s{}]+', re.sub(r"//[^\n]*", "", text))
	for k, tok in enumerate(toks):
		low = tok.lower()
		if tok == "{":
			depth += 1
			if depth == 2:
				stage = []
		elif tok == "}":
			if depth == 2 and name is not None and name not in first and any(
					t in ("map", "clampmap", "animmap") for t in stage):
				first.add(name)
				mode = None
				if "blendfunc" in stage:
					i = stage.index("blendfunc")
					a = stage[i + 1] if i + 1 < len(stage) else ""
					b = stage[i + 2] if i + 2 < len(stage) else ""
					if a == "filter" or (a, b) in (("gl_dst_color", "gl_zero"), ("gl_zero", "gl_src_color")):
						mode = "filter"
					elif a == "add" or (a, b) == ("gl_one", "gl_one"):
						mode = "add"
				if mode:
					out[name] = mode
			depth = max(depth - 1, 0)
			if depth == 0:
				name = None
		elif depth == 0:
			name = tok.strip('"').lower()
		elif depth == 2:
			stage.append(low)
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
	files = collect(args.main, (".tik", ".skd", ".skb", ".skc", ".shader"))
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
		posed = "no idle pose"
		if tik.idle_anim in files:
			try:
				skd_pose = parse_skc(read(files[tik.idle_anim]), tik.idle_anim)
				apply_pose(skd, skd_pose)
				posed = "posed"
			except SkdError as err:
				posed = str(err)
		lo, hi = skd.bounds()
		layouts = ",".join(sorted({s.layout for s in skd.surfaces}))
		box = " ".join(f"{h - l:.0f}" for l, h in zip(lo, hi))
		print(f"{n:>9} {skd.num_triangles:>5} {skd.num_verts:>5} v{skd.version} {layouts:<14} size {box:<22} {model}"
		      f" (scale {tik.scale:g}, {posed})")
		for s in skd.surfaces:
			print(f"{'':>17}{s.name}: {len(s.triangles)} tris -> {surface_texture(tik, s.name, shaders) or '?'}")
		total_tris += n * skd.num_triangles
	print(f"{len(counts)} models, {sum(counts.values())} instances, {total_tris} triangles if all drawn, {bad} unread")
	return 1 if bad else 0


if __name__ == "__main__":
	sys.exit(main())
