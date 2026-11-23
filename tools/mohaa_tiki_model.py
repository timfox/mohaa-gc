#!/usr/bin/env python3
"""Bake one posed MOHAA TIKI mesh to a static GoldSrc studio model.

This is the first asset step for scripted MOHAA models: it preserves the retail
TIKI's idle pose, surface mesh boundaries, UVs and diffuse maps. It does not
convert SKC animation sequences; runtime animation support is separate.

Example:
  python3 tools/mohaa_tiki_model.py retail/main \
    --model vehicles/gmctruck_opening.tik \
    --out /tmp/mohaa-cutscene/models/vehicles/gmctruck_opening.mdl

Generated models contain retail data. Keep outputs outside the repository.
"""
from __future__ import annotations

import argparse
import math
import os
import struct
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mohaa_skd
from ubersound import collect, read

STUDIO_NF_MASKED = 1
MAX_MODEL_VERTS = 2048
MAX_MESH_TRIS = 4096


def _name(value: str, size: int) -> bytes:
	b = value.encode("latin-1", "replace")[: size - 1]
	return b + b"\0" * (size - len(b))


def _atlas(images: list[bytes], max_size: int):
	"""Return an RGBA power-of-two atlas and each source's inner rectangle."""
	from io import BytesIO
	from PIL import Image

	if not images:
		raise ValueError("model has no diffuse textures")
	if max_size < 8:
		raise ValueError("skin atlas edge must be at least 8 pixels")
	decoded = [Image.open(BytesIO(data)).convert("RGBA") for data in images]
	cap = 1 << int(math.log2(max_size))
	if len(decoded) == 1:
		image = decoded[0]
		scale = min(1.0, cap / max(image.width, image.height))
		width = max(1, 1 << int(math.log2(max(1, int(image.width * scale)))))
		height = max(1, 1 << int(math.log2(max(1, int(image.height * scale)))))
		if image.size != (width, height):
			image = image.resize((width, height), Image.Resampling.LANCZOS)
		return image, [None]
	if max_size < 32:
		raise ValueError("multiple model textures need an atlas of at least 32 pixels")
	cols = math.ceil(math.sqrt(len(decoded)))
	rows = math.ceil(len(decoded) / cols)
	cell = 1 << int(math.log2(max(16, cap // max(cols, rows))))
	while (1 << math.ceil(math.log2(cols * cell))) > cap or (1 << math.ceil(math.log2(rows * cell))) > cap:
		cell //= 2
		if cell < 8:
			raise ValueError(f"{len(decoded)} textures do not fit a {cap}px atlas")
	width = 1 << math.ceil(math.log2(cols * cell))
	height = 1 << math.ceil(math.log2(rows * cell))
	atlas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
	pad = 2
	rects = []
	for i, image in enumerate(decoded):
		inner = cell - 2 * pad
		scale = min(inner / image.width, inner / image.height)
		iw = max(1, min(inner, int(round(image.width * scale))))
		ih = max(1, min(inner, int(round(image.height * scale))))
		if image.size != (iw, ih):
			image = image.resize((iw, ih), Image.Resampling.LANCZOS)
		cx, cy = (i % cols) * cell, (i // cols) * cell
		x, y = cx + (cell - iw) // 2, cy + (cell - ih) // 2
		atlas.alpha_composite(image, (x, y))
		# Extend edge texels into the filter gutter while retaining their alpha.
		atlas.paste(image.crop((0, 0, iw, 1)).resize((iw, pad)), (x, y - pad))
		atlas.paste(image.crop((0, ih - 1, iw, ih)).resize((iw, pad)), (x, y + ih))
		atlas.paste(image.crop((0, 0, 1, ih)).resize((pad, ih)), (x - pad, y))
		atlas.paste(image.crop((iw - 1, 0, iw, ih)).resize((pad, ih)), (x + iw, y))
		rects.append((x, y, iw, ih))
	return atlas, rects


def _skin(atlas):
	"""Indexed 8-bit skin; reserve index 255 for GoldSrc masked texels."""
	from PIL import Image

	width, height = atlas.size
	alpha = atlas.getchannel("A")
	masked = alpha.getextrema()[0] < 255
	quant = atlas.convert("RGB").quantize(colors=255 if masked else 256,
	                                     method=Image.Quantize.MEDIANCUT,
	                                     dither=Image.Dither.NONE)
	indices = bytearray(quant.tobytes())
	palette = (quant.getpalette() or [])[: (255 if masked else 256) * 3]
	palette += [0] * (768 - len(palette))
	if masked:
		for i, value in enumerate(alpha.tobytes()):
			if value < 128:
				indices[i] = 255
	return bytes(indices) + bytes(palette), width, height, STUDIO_NF_MASKED if masked else 0


def _static_mdl(name: str, parts, skin: bytes, width: int, height: int, texture_flags: int) -> bytes:
	"""Write a static one-bone model with one default-visible bodygroup per TIKI surface."""
	if not parts:
		raise ValueError("model has no drawable surfaces")
	all_positions = [p for part in parts for p in part["positions"]]
	lo = tuple(min(p[i] for p in all_positions) for i in range(3))
	hi = tuple(max(p[i] for p in all_positions) for i in range(3))
	radius = max(math.sqrt(sum(x * x for x in p)) for p in all_positions)
	out = bytearray(244)

	def align(n=4):
		while len(out) % n:
			out.append(0)

	boneindex = len(out)
	ctl = [-1] * 6
	out += _name("root", 32) + struct.pack("<ii", -1, 0) + struct.pack("<6i", *ctl)
	out += struct.pack("<6f", 0, 0, 0, 0, 0, 0) + struct.pack("<6f", 1, 1, 1, 1, 1, 1)
	ctlindex = len(out)
	hbindex = len(out)
	out += struct.pack("<ii6f", 0, 0, *lo, *hi)
	sgindex = len(out)
	out += _name("default", 32) + _name("", 64) + struct.pack("<ii", 0, 0)
	animindex = len(out)
	out += b"\0" * 12
	seqindex = len(out)
	seq = _name("idle", 32) + struct.pack("<fiiiiiiiiii", 10.0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0)
	seq += struct.pack("<3f", 0, 0, 0) + struct.pack("<ii", 0, 0) + struct.pack("<6f", *lo, *hi)
	seq += struct.pack("<ii", 1, animindex) + struct.pack("<2i", 0, 0) + struct.pack("<2f", 0, 0) + struct.pack("<2f", 1, 1)
	seq += struct.pack("<iiiiii", 0, 0, 0, 0, 0, 0)
	if len(seq) != 176:
		raise ValueError(f"internal sequence layout is {len(seq)} bytes, expected 176")
	out += seq
	bodypartsindex = len(out)
	bodypart_headers = []
	for part in parts:
		bodypart_headers.append(len(out))
		out += b"\0" * 76

	for part, bpindex in zip(parts, bodypart_headers):
		modelindex = len(out)
		out += b"\0" * 112
		meshindex = len(out)
		out += b"\0" * 20
		align()
		triindex = len(out)
		for tri in part["triangles"]:
			out += struct.pack("<h", 3)
			for vi, ni, s, t in tri:
				out += struct.pack("<4h", vi, ni, s, t)
		out += struct.pack("<h", 0)
		align()
		vertinfo = len(out)
		out += bytes(len(part["positions"]))
		align()
		norminfo = len(out)
		out += bytes(len(part["normals"]))
		align()
		vertindex = len(out)
		for p in part["positions"]:
			out += struct.pack("<3f", *p)
		normindex = len(out)
		for n in part["normals"]:
			out += struct.pack("<3f", *n)
		struct.pack_into("<5i", out, meshindex, len(part["triangles"]), triindex, 0,
		                 len(part["normals"]), normindex)
		struct.pack_into("<64sif10i", out, modelindex, _name(part["name"], 64), 0, part["radius"],
		                 1, meshindex, len(part["positions"]), vertinfo, vertindex,
		                 len(part["normals"]), norminfo, normindex, 0, 0)
		struct.pack_into("<64siii", out, bpindex, _name(part["name"], 64), 1, 1, modelindex)

	textureindex = len(out)
	out += _name(name + ".bmp", 64) + struct.pack("<iiii", texture_flags, width, height, 0)
	skinindex = len(out)
	out += struct.pack("<h", 0)
	align()
	texturedata = len(out)
	struct.pack_into("<i", out, textureindex + 76, texturedata)
	out += skin
	align()
	hdr = struct.pack("<4si64si", b"IDST", 10, _name(name + ".mdl", 64), len(out))
	hdr += struct.pack("<3f", 0, 0, 0) + struct.pack("<3f", *lo) + struct.pack("<3f", *hi)
	hdr += struct.pack("<3f", *lo) + struct.pack("<3f", *hi) + struct.pack("<i", 0)
	fields = [1, boneindex, 0, ctlindex, 1, hbindex, 1, seqindex, 1, sgindex,
	          1, textureindex, texturedata, 1, 1, skinindex, len(parts), bodypartsindex]
	fields += [0] * 8
	hdr += struct.pack("<26i", *fields)
	if len(hdr) != 244:
		raise ValueError(f"internal header layout is {len(hdr)} bytes, expected 244")
	out[:244] = hdr
	return bytes(out)


def convert(main_paths, model: str, output: Path, skin_size: int = 256, scale: float | None = None):
	files = collect(main_paths, (".tik", ".skd", ".skb", ".skc", ".shader", ".tga", ".jpg", ".png", ".bmp"))
	model = mohaa_skd.norm(model)
	if not model.startswith("models/"):
		model = "models/" + model
	if not model.endswith(".tik"):
		model += ".tik"
	if model not in files:
		raise ValueError(f"retail TIKI not found: {model}")
	tik = mohaa_skd.parse_tik(read(files[model]).decode("latin-1", "replace"))
	if tik.mesh not in files:
		raise ValueError(f"retail mesh not found: {tik.mesh}")
	skd = mohaa_skd.parse_skd(read(files[tik.mesh]), tik.mesh)
	if tik.idle_anim and tik.idle_anim in files:
		mohaa_skd.apply_pose(skd, mohaa_skd.parse_skc(read(files[tik.idle_anim]), tik.idle_anim))
	shaders = {}
	for path, entry in files.items():
		if path.endswith(".shader"):
			shaders.update(mohaa_skd.parse_shaders(read(entry).decode("latin-1", "replace")))
	texture_paths, surface_textures, kept = [], {}, []
	for surface in skd.surfaces:
		shader = tik.shaders.get(surface.name.lower(), "")
		if "nodraw" in shader.lower():
			continue
		texture = mohaa_skd.surface_texture(tik, surface.name, shaders)
		if not texture:
			continue
		candidate = texture.lower().lstrip("/")
		if not Path(candidate).suffix:
			candidate += ".tga"
		if candidate not in files and candidate.endswith(".tga"):
			candidate = candidate[:-4] + ".jpg"
		if candidate not in files:
			raise ValueError(f"diffuse texture not found for {surface.name}: {texture}")
		if candidate not in texture_paths:
			texture_paths.append(candidate)
		surface_textures[surface.name] = texture_paths.index(candidate)
		kept.append(surface)
	if not kept or not texture_paths:
		raise ValueError("no textured surfaces remain after filtering")
	atlas, rects = _atlas([read(files[p]) for p in texture_paths], skin_size)
	skin, texw, texh, texture_flags = _skin(atlas)
	unit_scale = (tik.scale if scale is None else scale) * (72.0 / 94.0)
	parts = []
	for surface in kept:
		positions, normals, triangles = [], [], []
		position_ids, normal_ids = {}, {}
		rect = rects[surface_textures[surface.name]]
		for tri in surface.triangles:
			corners = []
			for index in tri:
				p = tuple(float(v) * unit_scale for v in surface.positions[index])
				n = tuple(float(v) for v in surface.normals[index])
				pk = tuple(round(v, 5) for v in p)
				if pk not in position_ids:
					position_ids[pk] = len(positions)
					positions.append(p)
				nk = tuple(round(v, 5) for v in n)
				if nk not in normal_ids:
					normal_ids[nk] = len(normals)
					normals.append(n)
				u, v = surface.uvs[index]
				if rect is None:
					s = min(texw - 1, max(0, int(round(u * (texw - 1)))))
					t = min(texh - 1, max(0, int(round((1.0 - v) * (texh - 1)))))
				else:
					x, y, rw, rh = rect
					s = min(texw - 1, max(0, x + int(round(u * (rw - 1)))))
					t = min(texh - 1, max(0, y + int(round((1.0 - v) * (rh - 1)))))
				corners.append((position_ids[pk], normal_ids[nk], s, t))
			triangles.append(corners)
		if len(positions) > MAX_MODEL_VERTS or len(normals) > MAX_MODEL_VERTS or len(triangles) > MAX_MESH_TRIS:
			raise ValueError(f"surface {surface.name} exceeds GameCube studio limits: "
			                 f"{len(positions)} verts, {len(normals)} normals, {len(triangles)} tris")
		radius = max(math.sqrt(sum(v * v for v in p)) for p in positions)
		parts.append({"name": surface.name, "positions": positions, "normals": normals,
		              "triangles": triangles, "radius": radius})
	data = _static_mdl(output.stem, parts, skin, texw, texh, texture_flags)
	output.parent.mkdir(parents=True, exist_ok=True)
	output.write_bytes(data)
	return len(parts), sum(len(p["positions"]) for p in parts), sum(len(p["triangles"]) for p in parts), texture_paths, unit_scale, tik.idle_anim


def main(argv=None):
	ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
	ap.add_argument("main", nargs="+", help="MOHAA main directory or .pk3 files")
	ap.add_argument("--model", required=True, help="TIKI path, e.g. vehicles/gmctruck_opening.tik")
	ap.add_argument("--out", required=True, type=Path, help="output GoldSrc studio v10 .mdl")
	ap.add_argument("--skin-size", type=int, default=256, help="maximum power-of-two atlas edge")
	ap.add_argument("--scale", type=float, default=None, help="override TIKI scale; map scale 72/94 is still applied")
	a = ap.parse_args(argv)
	parts, verts, tris, textures, scale, idle = convert(a.main, a.model, a.out, a.skin_size, a.scale)
	print(f"MOHAA TIKI: {a.model}, idle={idle or '-'}, {parts} bodygroups, {tris} triangles, "
	      f"{verts} bodygroup vertices, scale {scale:.5f}")
	print(f"Textures ({len(textures)}): " + ", ".join(textures))
	print(f"Studio v10: {a.out} ({a.out.stat().st_size} bytes)")
	return 0


if __name__ == "__main__":
	sys.exit(main())
