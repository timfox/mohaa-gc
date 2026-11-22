#!/usr/bin/env python3
"""Pack a map's static props (trees, rocks ...) into one <map>.mprop file for the engine to draw.

    python3 tools/props_models.py "/path/to/MOHAA/main" out/m6l1a.props -o out/m6l1a.mprop

It reads the .props sidecar that bsp19_to_map.py writes, loads each model's .tik, posed .skd mesh
and textures from the paks, and writes the models, their textures and every instance into one file.
Props cost the engine no edict and no model slot. Their collision is already in the map.

The output is built from retail data: write it outside the repository and never commit it.

Format (little-endian, like .mcol):
  "MPRP" version numTextures numModels numInstances
  texture: name[32], u16 width, u16 height, u32 flags (1 = alpha tested), palette 256 x RGBA,
           width*height palette indices (index 255 is transparent when alpha tested)
  model:   name[64], mins[3], maxs[3], numSurfaces; then per surface:
           texture index (-1 = none), numVerts, numTris, verts (x y z s t as floats), tris (3 x u16)
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
VERSION = 1
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


def build(files, read, props, max_side=MAX_TEXTURE):
	"""(pack bytes, stats) for the props, reading models and textures from files {path: entry}."""
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
				verts = [(p[0] * tik.scale, p[1] * tik.scale, p[2] * tik.scale, uv[0], uv[1])
				         for p, uv in zip(s.positions, s.uvs)]
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
			out += b"".join(struct.pack("<5f", *v) for v in verts)
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
	args = ap.parse_args(argv)
	*mains, props_path = args.main
	if not mains:
		ap.error("give the MOHAA main folder (or pk3 files) and then the .props file")
	files = collect(mains, (".tik", ".skd", ".skc", ".shader", ".tga", ".jpg", ".png"))
	data, stats = build(files, read, read_props(props_path), args.max_texture)
	with open(args.out, "wb") as f:
		f.write(data)
	print(f"wrote {args.out} ({len(data)} bytes)")
	for k, v in stats.items():
		print(f"  {k:<20} {v}")
	return 1 if stats["models_unloaded"] or stats["textures_missing"] else 0


if __name__ == "__main__":
	sys.exit(main())
