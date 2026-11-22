#!/usr/bin/env python3
"""Pack a map's static props (trees, rocks ...) into one <map>.mprop file for the engine to draw.

    python3 tools/props_models.py "/path/to/MOHAA/main" out/m6l1a.props -o out/m6l1a.mprop [--bsp m6l1a.bsp]

It reads the .props sidecar that bsp19_to_map.py writes, loads each model's .tik, posed .skd mesh
and textures from the paks, and writes the models, their textures and every instance into one file.
Props cost the engine no edict and no model slot. Their collision is already in the map.
With --bsp the map's LOD terrain, curved patches and triangle soups are added too, as "*world/"
meshes in map units: the converter gives them collision only, so without them that ground is not drawn.

The output is built from retail data: write it outside the repository and never commit it.

Format (little-endian, like .mcol):
  "MPRP" version numTextures numModels numInstances
  texture: name[32], u16 width, u16 height, u32 flags (1 = alpha tested), palette 256 x RGBA,
           width*height palette indices (index 255 is transparent when alpha tested)
  model:   name[64], mins[3], maxs[3], numSurfaces; then per surface:
           texture index (-1 = none), numVerts, numTris, verts (x y z nx ny nz s t as floats), tris (3 x u16)
  instance: model index, origin[3], angles[3] (pitch yaw roll), scale
Model positions are in MOHAA units with the .tik scale applied; an instance's scale (from .props)
converts them to the map's units.
"""
from __future__ import annotations

import argparse
import io
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mohaa_skd as skd  # noqa: E402

MAGIC = b"MPRP"
VERSION = 2  # 2: vertices carry their normal
MAX_TEXTURE = 128  # largest side, so a map's textures stay a few hundred KiB on the GameCube
TEX_ALPHA = 1


def _pow2_at_most(n, cap):
	p = 1
	while p * 2 <= min(n, cap):
		p *= 2
	return p


def encode_texture(data: bytes, max_side: int = MAX_TEXTURE):
	"""(width, height, flags, palette bytes, index bytes) from a TGA/JPG/PNG: power-of-two sides of at
	most max_side, 8-bit palette. Images with real alpha get index 255 for alpha under 128."""
	from PIL import Image

	img = Image.open(io.BytesIO(data)).convert("RGBA")
	tested = img.getchannel("A").getextrema()[0] < 128  # judged at full size: thin holes can blur away
	w, h = _pow2_at_most(img.width, max_side), _pow2_at_most(img.height, max_side)
	img = img.resize((w, h), Image.LANCZOS)
	alpha = img.getchannel("A")
	colours = 255 if tested else 256
	pal_img = img.convert("RGB").quantize(colors=colours, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
	idx = bytearray(pal_img.tobytes())
	pal = (pal_img.getpalette() or [])[:colours * 3]
	pal += [0] * (256 * 3 - len(pal))
	if tested:
		for i, a in enumerate(alpha.tobytes()):
			if a < 128:
				idx[i] = 255
	rgba = bytearray()
	for i in range(256):
		rgba += bytes(pal[i * 3:i * 3 + 3]) + (b"\0" if tested and i == 255 else b"\xff")
	return w, h, TEX_ALPHA if tested else 0, bytes(rgba), bytes(idx)


def _unit(n):
	length = (n[0] * n[0] + n[1] * n[1] + n[2] * n[2]) ** 0.5
	return (n[0] / length, n[1] / length, n[2] / length) if length > 1e-6 else (0.0, 0.0, 1.0)


def read_props(path):
	"""[(model, origin, angles, scale)] from a .props sidecar."""
	out = []
	with open(path) as f:
		for line in f:
			if line.startswith("#") or not line.strip():
				continue
			parts = line.split()
			nums = [float(v) for v in parts[:7]]
			model = skd.norm(parts[7].replace("%20", " ").replace("%25", "%"))
			out.append((model, tuple(nums[0:3]), tuple(nums[3:6]), nums[6]))
	return out


def _image(files, path, read):
	"""The texture's bytes: the shader names .tga, but a .jpg of the same name serves too."""
	base = path.rsplit(".", 1)[0]
	for cand in (path, base + ".tga", base + ".jpg", base + ".png"):
		if cand in files:
			return read(files[cand])
	return None


WORLD_PREFIX = "*world/"  # a world mesh: drawn whole wherever it is, no impostor, no far cell
WORLD_MAX_MODELS = 96


def terrain_meshes(bsp, scale: float, max_models: int = WORLD_MAX_MODELS):
	"""MOHAA's LOD terrain as world meshes: [(name, centre, [(shader, verts, tris)])], positions in map
	units around the centre (the instance scale is 1). The converter gives terrain only collision; this
	is what draws it. Patches are grouped G x G per mesh, G growing until the meshes fit max_models."""
	import mohaa_bsp19 as b19

	n = b19.TERRAIN_SAMPLES
	if not bsp.terrain:
		return []
	group = 2
	while True:
		chunks = {}
		for tp in bsp.terrain:
			chunks.setdefault((tp.x // (8 * group), tp.y // (8 * group)), []).append(tp)
		if len(chunks) <= max_models or group >= 64:
			break
		group *= 2
	out = []
	for key in sorted(chunks):
		pts = []
		for tp in chunks[key]:
			x0, y0 = tp.origin
			pts += [(x0, y0, min(tp.heights)), (x0 + 512, y0 + 512, max(tp.heights))]
		centre = tuple(0.5 * (min(p[a] for p in pts) + max(p[a] for p in pts)) * scale for a in range(3))
		by_shader = {}
		for tp in chunks[key]:
			name = bsp.shaders[tp.shader].name if 0 <= tp.shader < len(bsp.shaders) else ""
			verts, tris = by_shader.setdefault(name, ([], []))
			base = len(verts)
			x0, y0 = tp.origin
			tc = tp.tex if len(tp.tex) == 8 else (0, 0, 0, 1, 1, 0, 1, 1)
			h = lambda i, j: tp.heights[min(max(j, 0), n - 1) * n + min(max(i, 0), n - 1)]  # noqa: E731
			for j in range(n):
				for i in range(n):
					fx, fy = i / (n - 1), j / (n - 1)
					w00, w01, w10, w11 = (1 - fx) * (1 - fy), (1 - fx) * fy, fx * (1 - fy), fx * fy
					s_ = w00 * tc[0] + w01 * tc[2] + w10 * tc[4] + w11 * tc[6]
					t_ = w00 * tc[1] + w01 * tc[3] + w10 * tc[5] + w11 * tc[7]
					nx = (h(i - 1, j) - h(i + 1, j)) / (2.0 * b19.TERRAIN_CELL)
					ny = (h(i, j - 1) - h(i, j + 1)) / (2.0 * b19.TERRAIN_CELL)
					nrm = _unit((nx, ny, 1.0))
					pos = tuple((v * scale) - c for v, c in zip(
						(x0 + i * b19.TERRAIN_CELL, y0 + j * b19.TERRAIN_CELL, tp.heights[j * n + i]), centre))
					verts.append((*pos, *nrm, s_, t_))
			for j in range(n - 1):
				for i in range(n - 1):
					a = base + j * n + i
					# the collision's diagonal (bsp19_to_map._terrain_triangles), counter-clockwise from above
					tris += [(a, a + 1, a + n), (a + n + 1, a + n, a + 1)]
		out.append((f"{WORLD_PREFIX}terrain_{key[0]}_{key[1]}", centre,
			[(sh, v, t) for sh, (v, t) in sorted(by_shader.items())]))
	return out


def _bez(a, b, c, t):
	u = 1.0 - t
	return tuple(u * u * x + 2 * u * t * y + t * t * z for x, y, z in zip(a, b, c))


def _facing(verts, tris):
	"""Sum over tris of (counter-clockwise face normal . vertex normals): negative when the tris wind the other way."""
	tot = 0.0
	for a, b, c in tris:
		pa, pb, pc = verts[a], verts[b], verts[c]
		e1 = [pb[k] - pa[k] for k in range(3)]
		e2 = [pc[k] - pa[k] for k in range(3)]
		n = (e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0])
		tot += sum(n[k] * (pa[3 + k] + pb[3 + k] + pc[3 + k]) for k in range(3))
	return tot


def patch_mesh(ctrl, w, h, steps=4):
	"""A Quake 3 biquadratic patch (w x h control vertices, row-major, both odd, each a tuple of
	floats: position, normal, st) as (verts, tris), every 3x3 piece cut steps x steps."""
	if w < 3 or h < 3 or not (w & 1) or not (h & 1) or len(ctrl) < w * h:
		return [], []
	cp = lambda i, j: ctrl[j * w + i]  # noqa: E731
	nu, nv = (w - 1) // 2 * steps, (h - 1) // 2 * steps
	verts = []
	for y in range(nv + 1):
		j = min(y // steps, (h - 1) // 2 - 1)
		tv = (y - j * steps) / steps
		for x in range(nu + 1):
			i = min(x // steps, (w - 1) // 2 - 1)
			tu = (x - i * steps) / steps
			cols = [_bez(cp(2 * i, 2 * j + r), cp(2 * i + 1, 2 * j + r), cp(2 * i + 2, 2 * j + r), tu) for r in range(3)]
			verts.append(_bez(cols[0], cols[1], cols[2], tv))
	tris = []
	row = nu + 1
	for y in range(nv):
		for x in range(nu):
			a = y * row + x
			tris += [(a, a + row, a + 1), (a + 1, a + row, a + row + 1)]
	return verts, tris


def surface_meshes(bsp, scale: float, max_models: int = WORLD_MAX_MODELS // 2, steps: int = 4):
	"""The world's curved patches and triangle soups (MOHAA's mesh ground, rocks and rubble), which
	the converter keeps only as collision, as world meshes like terrain_meshes(): grouped by a grid
	whose cell grows until the meshes fit max_models. Sky and nodraw surfaces are left out."""
	import mohaa_bsp19 as b19

	if not bsp.models or not bsp.drawverts:
		return []
	m = bsp.models[0]
	pieces = []	# (shader, verts in map units, tris, centre)
	for si in range(m.first_surface, min(m.first_surface + m.num_surfaces, len(bsp.surfaces))):
		sf = bsp.surfaces[si]
		if sf.surface_type not in (b19.MST_PATCH, b19.MST_TRIANGLE_SOUP):
			continue
		sh = bsp.shaders[sf.shader] if 0 <= sf.shader < len(bsp.shaders) else None
		if sh is None or sh.surface_flags & (b19.SURF_SKY | b19.SURF_NODRAW) or "nodraw" in sh.name.lower():
			continue
		lo, hi = sf.first_vert, sf.first_vert + sf.num_verts
		if hi > len(bsp.drawverts):
			continue
		dv = [(*bsp.drawverts[k], *bsp.drawvert_normals[k], *bsp.drawvert_st[k]) for k in range(lo, hi)]
		if sf.surface_type == b19.MST_PATCH:
			verts, tris = patch_mesh(dv, sf.patch_width, sf.patch_height, steps)
		else:
			idx = bsp.drawindexes[sf.first_index:sf.first_index + sf.num_indexes]
			verts = dv
			tris = [tuple(idx[k:k + 3]) for k in range(0, len(idx) - 2, 3) if max(idx[k:k + 3]) < len(dv)]
		if not tris:
			continue
		verts = [(*v[:3], *_unit(v[3:6]), *v[6:8]) for v in verts]
		if _facing(verts, tris) < 0:	# the props draw counter-clockwise: wind each surface to match its normals
			tris = [(a, c, b) for a, b, c in tris]
		c = tuple(0.5 * (min(v[a] for v in verts) + max(v[a] for v in verts)) for a in range(3))
		pieces.append((sh.name, verts, tris, c))
	if not pieces:
		return []
	side = 1024.0
	while True:
		chunks = {}
		for p in pieces:
			chunks.setdefault((int(p[3][0] // side), int(p[3][1] // side)), []).append(p)
		if len(chunks) <= max_models or side >= 65536:
			break
		side *= 1.5
	out = []
	for key in sorted(chunks):
		ps = chunks[key]
		allv = [v for p in ps for v in p[1]]
		centre = tuple(0.5 * (min(v[a] for v in allv) + max(v[a] for v in allv)) * scale for a in range(3))
		by_shader = {}
		for name, verts, tris, _ in ps:
			vv, tt = by_shader.setdefault(name, ([], []))
			base = len(vv)
			vv += [(v[0] * scale - centre[0], v[1] * scale - centre[1], v[2] * scale - centre[2], *v[3:]) for v in verts]
			tt += [(a + base, b + base, c + base) for a, b, c in tris]
		out.append((f"{WORLD_PREFIX}mesh_{key[0]}_{key[1]}", centre,
			[(sh, v, t) for sh, (v, t) in sorted(by_shader.items())]))
	return out


def build(files, read, props, max_side=MAX_TEXTURE, world=()):
	"""(pack bytes, stats) for the props, reading models and textures from files {path: entry}.
	world: terrain_meshes() output, added as models drawn at scale 1."""
	shaders = {}
	for p, e in sorted(files.items()):
		if p.endswith(".shader"):
			shaders.update(skd.parse_shaders(read(e).decode("latin-1")))
	stats = {"instances": 0, "instances_unloaded": 0, "models": 0, "models_unloaded": 0, "textures": 0,
	         "textures_missing": 0, "triangles": 0, "texture_bytes": 0}
	models, model_index, textures, tex_index = [], {}, [], {}
	instances = []
	models_done = set()
	for model, origin, angles, scale in props:
		tik = None
		if model not in model_index:
			model_index[model] = None
			key = model if model.startswith("models/") else "models/" + model
			try:
				tik = skd.parse_tik(read(files[key]).decode("latin-1"))
				mesh = skd.parse_skd(read(files[tik.mesh]), tik.mesh)
				if tik.idle_anim in files:
					skd.apply_pose(mesh, skd.parse_skc(read(files[tik.idle_anim]), tik.idle_anim))
			except (KeyError, skd.SkdError) as err:
				print(f"  {model}: not loaded ({err})", file=sys.stderr)
				stats["models_unloaded"] += 1
				tik = None
		if model_index[model] is None and tik is not None and model not in models_done:
			models_done.add(model)
			surfs = []
			for s in mesh.surfaces:
				tpath = skd.surface_texture(tik, s.name, shaders)
				ti = -1
				if tpath:
					if tpath not in tex_index:
						img = _image(files, tpath, read)
						if img is None:
							tex_index[tpath] = -1
							stats["textures_missing"] += 1
						else:
							tex_index[tpath] = len(textures)
							textures.append((tpath, encode_texture(img, max_side)))
					ti = tex_index[tpath]
				verts = [(p[0] * tik.scale, p[1] * tik.scale, p[2] * tik.scale, *_unit(n), uv[0], uv[1])
				         for p, n, uv in zip(s.positions, s.normals, s.uvs)]
				surfs.append((ti, verts, s.triangles))
				stats["triangles"] += len(s.triangles)
			lo, hi = mesh.bounds()
			model_index[model] = len(models)
			models.append((model, tuple(c * tik.scale for c in lo), tuple(c * tik.scale for c in hi), surfs))
		mi = model_index[model]
		if mi is None:
			stats["instances_unloaded"] += 1
			continue
		instances.append((mi, origin, angles, scale))

	stats["world_models"] = 0
	for name, centre, surfaces in world:
		surfs, lo, hi = [], [1e30] * 3, [-1e30] * 3
		for shader, verts, tris in surfaces:
			tpath = shaders.get(shader.lower(), skd.norm(shader)) if shader else ""
			ti = -1
			if tpath:
				if tpath not in tex_index:
					img = _image(files, tpath, read)
					if img is None:
						tex_index[tpath] = -1
						stats["textures_missing"] += 1
					else:
						tex_index[tpath] = len(textures)
						textures.append((tpath, encode_texture(img, max_side)))
				ti = tex_index[tpath]
			for v in verts:
				for a in range(3):
					lo[a], hi[a] = min(lo[a], v[a]), max(hi[a], v[a])
			surfs.append((ti, verts, tris))
			stats["triangles"] += len(tris)
		if not surfs:
			continue
		instances.append((len(models), centre, (0.0, 0.0, 0.0), 1.0))
		models.append((name, tuple(lo), tuple(hi), surfs))
		stats["world_models"] += 1

	out = bytearray(MAGIC + struct.pack("<4i", VERSION, len(textures), len(models), len(instances)))
	for name, (w, h, flags, pal, idx) in textures:
		out += name.encode("latin-1")[-31:].ljust(32, b"\0") + struct.pack("<2HI", w, h, flags) + pal + idx
		stats["texture_bytes"] += len(pal) + len(idx)
	for name, lo, hi, surfs in models:
		out += name.encode("latin-1")[-63:].ljust(64, b"\0") + struct.pack("<6fi", *lo, *hi, len(surfs))
		for ti, verts, tris in surfs:
			if len(verts) > 0xffff:
				raise skd.SkdError(f"{name}: a surface has more than 65535 vertices")
			out += struct.pack("<3i", ti, len(verts), len(tris))
			out += b"".join(struct.pack("<8f", *v) for v in verts)
			out += b"".join(struct.pack("<3H", *t) for t in tris)
	for mi, origin, angles, scale in instances:
		out += struct.pack("<i7f", mi, *origin, *angles, scale)
	stats.update(instances=len(instances), models=len(models), textures=len(textures))
	return bytes(out), stats


def main(argv=None) -> int:
	from ubersound import collect, read

	ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
	ap.add_argument("main", nargs="+", help="MOHAA main folder or pk3 files, then the .props sidecar last")
	ap.add_argument("-o", "--out", required=True, help="the .mprop file to write")
	ap.add_argument("--max-texture", type=int, default=MAX_TEXTURE, help="largest texture side (power of two)")
	ap.add_argument("--bsp", help="the map's MOHAA .bsp: its terrain is added as world meshes (drawn, not just collided)")
	ap.add_argument("--scale", type=float, default=None, help="map scale for the terrain (default: the converter's)")
	args = ap.parse_args(argv)
	*mains, props_path = args.main
	if not mains:
		ap.error("give the MOHAA main folder (or pk3 files) and then the .props file")
	files = collect(mains, (".tik", ".skd", ".skc", ".shader", ".tga", ".jpg", ".png"))
	world = []
	if args.bsp:
		import mohaa_bsp19 as b19
		from bsp19_to_map import DEFAULT_SCALE

		bsp = b19.load(args.bsp)
		sc = args.scale if args.scale else DEFAULT_SCALE
		world = terrain_meshes(bsp, sc) + surface_meshes(bsp, sc)
	data, stats = build(files, read, read_props(props_path), args.max_texture, world)
	with open(args.out, "wb") as f:
		f.write(data)
	print(f"wrote {args.out} ({len(data)} bytes)")
	for k, v in stats.items():
		print(f"  {k:<20} {v}")
	return 1 if stats["models_unloaded"] or stats["textures_missing"] else 0


if __name__ == "__main__":
	sys.exit(main())
