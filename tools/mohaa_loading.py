#!/usr/bin/env python3
"""Make the GameCube loading screens from MOHAA's own: ui/loading_*.urc, drawn the way the retail game draws them.

    python3 tools/mohaa_loading.py "/path/to/MOHAA/main" --out <sd>/xash3d/<gamedir> [--png DIR]

MOHAA shows a loading screen while a map loads: a 640x480 urc menu named after the map ("m1l1", "dm/mohdm1",
"obj/obj_team1"), or "loading_default" (the sepia soldiers, the stone border and the MOHAA logo) for a map
without one. Every menu postincludes ui/loadingbar.txt: the red progress bar (a statbar tiling
textures/mohmenu/loadingbar over 194,456 252x8) in its silver frame (textures/mohmenu/loadingbar_border).
The single-player maps show their mission briefing; the multiplayer maps show a photo on paper with the
map's place name.

This draws each menu's pieces in urc order through their shader stages (plain, blend, filter, add, and the
white-then-picture stages of the multiplayer photos), leaves out what the retail loading screen does not
show (the 3dfx Voodoo tiles gated by ui_voodoo, the flashing briefing widget, the continue button), draws
label titles in their RitualFont, and keeps the bar apart: the screen gets the empty frame, and the bar's
fill texture rides along so the engine can draw it at the load fraction.

Output, read by xash3d-gc (engine/platform/gamecube/gc_loadscreen.h):

    resource/gc_loading/<map>.cmp      one per map menu (basename: m1l1, mohdm1, obj_team1)
    resource/gc_loading/default.cmp    loading_default, for every other map

Each is a GCMP file, GX CMPR 640 x (480 + fill rows): the screen, then the fill texture at x 0, with the bar
layout in the header's reserved bytes. 150 KiB per screen on the SD card; the engine draws it once per load
and keeps only 4 KiB (the tiles under the bar and the fill) while the map loads.
The output is retail data: write it outside the repository and never commit it.
"""
import argparse
import io
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mohaa_menu import IMAGE_EXTS, cmpr_encode, find_image, parse_urc, strip_comments, tokens  # noqa: E402
from ubersound import collect, read  # noqa: E402

SCREEN = (640, 480)
OUT = "resource/gc_loading"
DEFAULT_MENU = "loading_default"
LOADING_URC = re.compile(r"^ui/loading_[^/]+\.urc$")
# Pieces of ui/loadingbar.txt the retail screen does not show while loading: the flashing "loading" widget and
# the continue button belong to the briefing that waits for the player after the load.
HIDDEN = {"loadingflasher", "continuebutton"}
RESIDENT_MAX = 4096   # GC_LOADSCREEN_RESIDENT_MAX: plate + fill bytes the engine keeps while loading
BAR_DEFAULT = ((194, 456, 252, 8), "textures/mohmenu/loadingbar")


def parse_menu_header(text):
    """(menu name, [postinclude paths]) of a urc file."""
    name, incs = None, []
    for line in strip_comments(text).splitlines():
        t = tokens(line)
        if not t:
            continue
        key = t[0].lower()
        if key == "menu" and len(t) > 1 and name is None:
            name = t[1]
        elif key in ("include", "postinclude") and len(t) > 1:
            incs.append(t[1].lower().replace("\\", "/"))
        elif key == "resource":
            break
    return name, incs


# blendFunc shorthands and GL factors (Q3 shader scripts)
BLEND_SHORT = {"blend": ("gl_src_alpha", "gl_one_minus_src_alpha"), "filter": ("gl_dst_color", "gl_zero"),
               "add": ("gl_one", "gl_one")}


def parse_shader_stages(text):
    """{shader name: [(image path or "$whiteimage", (src factor, dst factor) or None)]} from shader script text."""
    out = {}
    depth, name, stage = 0, None, None
    for line in strip_comments(text).splitlines():
        t = tokens(line)
        if not t:
            continue
        if t[0] == "{":
            depth += 1
            if depth == 2 and name:
                stage = {"map": None, "blend": None}
            continue
        if t[0] == "}":
            if depth == 2 and name and stage is not None:
                if stage["map"]:
                    out.setdefault(name, []).append((stage["map"], stage["blend"]))
                stage = None
            depth = max(0, depth - 1)
            if depth == 0:
                name = None
            continue
        if depth == 0:
            name = t[0].lower()
            if name in out:   # the first definition wins, as in the game
                name = None
            continue
        if depth == 2 and stage is not None:
            key = t[0].lower()
            if key in ("map", "clampmap") and len(t) > 1:
                stage["map"] = t[1]
            elif key == "animmap" and len(t) > 2:
                stage["map"] = t[2]
            elif key == "blendfunc" and len(t) > 1:
                if t[1].lower() in BLEND_SHORT:
                    stage["blend"] = BLEND_SHORT[t[1].lower()]
                elif len(t) > 2:
                    stage["blend"] = (t[1].lower(), t[2].lower())
    return out


def _factor(name, src, dst):
    import numpy as np

    one = np.ones_like(dst[..., :1])
    sa, da = src[..., 3:4], dst[..., 3:4]
    return {
        "gl_one": one, "gl_zero": one * 0,
        "gl_src_alpha": sa, "gl_one_minus_src_alpha": 1 - sa,
        "gl_dst_alpha": da, "gl_one_minus_dst_alpha": 1 - da,
        "gl_src_color": src[..., :3], "gl_one_minus_src_color": 1 - src[..., :3],
        "gl_dst_color": dst[..., :3], "gl_one_minus_dst_color": 1 - dst[..., :3],
    }.get(name, one)


class Painter:
    """Draws urc pieces onto a 640x480 float RGBA canvas."""

    def __init__(self, files):
        import numpy as np

        self.files = files
        self.shaders = {}
        for path in sorted(p for p in files if p.startswith("scripts/") and p.endswith(".shader")):
            for k, v in parse_shader_stages(read(files[path]).decode("latin-1")).items():
                self.shaders.setdefault(k, v)
        self.canvas = np.zeros((SCREEN[1], SCREEN[0], 4), np.float64)
        self.canvas[..., 3] = 1.0
        self._images = {}

    def image(self, path, size):
        """The image at path as float RGBA (h, w, 4) resized to size, or None."""
        import numpy as np
        from PIL import Image

        if path.lower() == "$whiteimage":
            return np.ones((size[1], size[0], 4))
        found = find_image(self.files, path)
        if not found:
            return None
        key = (found, size)
        if key not in self._images:
            im = Image.open(io.BytesIO(read(self.files[found]))).convert("RGBA")
            if im.size != size:   # colour and alpha apart: an RGBA resize premultiplies, losing colour under alpha 0
                rgb = im.convert("RGB").resize(size, Image.LANCZOS)
                im = Image.merge("RGBA", rgb.split() + (im.getchannel("A").resize(size, Image.LANCZOS),))
            self._images[key] = np.asarray(im, np.float64) / 255.0
        return self._images[key]

    def stages(self, shader):
        """[(image, blend)] for a shader name; a bare image path draws alpha-blended, as MOHAA's 2D does."""
        st = self.shaders.get(shader.lower())
        if st:
            return st
        return [(shader, BLEND_SHORT["blend"])]

    def draw(self, shader, rect):
        """Draw a shader over rect (x, y, w, h); the parts off the screen are clipped. Returns True if drawn."""
        x, y, w, h = rect
        if w <= 0 or h <= 0:
            return False
        drawn = False
        for path, blend in self.stages(shader):
            src = self.image(path, (w, h))
            if src is None:
                continue
            x0, y0 = max(x, 0), max(y, 0)
            x1, y1 = min(x + w, SCREEN[0]), min(y + h, SCREEN[1])
            if x1 <= x0 or y1 <= y0:
                continue
            s = src[y0 - y:y1 - y, x0 - x:x1 - x]
            d = self.canvas[y0:y1, x0:x1]
            if blend is None:
                out = s.copy()
                out[..., 3] = 1.0
            else:
                out = d.copy()
                out[..., :3] = s[..., :3] * _factor(blend[0], s, d) + d[..., :3] * _factor(blend[1], s, d)
            self.canvas[y0:y1, x0:x1, :3] = out[..., :3].clip(0, 1)
            drawn = True
        return drawn

    def text(self, title, rect, font, color):
        """A label title in its RitualFont, centred in rect."""
        import numpy as np

        glyphs = load_ritualfont(self.files, font)
        if not glyphs or not title:
            return False
        atlas, height, locs, ind = glyphs
        width = sum(locs[ind[ord(c)]][2] if 0 <= ord(c) < len(ind) and ind[ord(c)] >= 0 else height / 2
                    for c in title)
        x = rect[0] + (rect[2] - width) / 2.0
        y = int(round(rect[1] + (rect[3] - height) / 2.0))
        for c in title:
            k = ind[ord(c)] if 0 <= ord(c) < len(ind) else -1
            if k < 0:
                x += height / 2
                continue
            gx, gy, gw, gh = (int(round(v)) for v in locs[k])
            g = atlas[gy:gy + gh, gx:gx + gw]
            ix = int(round(x))
            x0, y0 = max(ix, 0), max(y, 0)
            x1, y1 = min(ix + g.shape[1], SCREEN[0]), min(y + g.shape[0], SCREEN[1])
            if x1 > x0 and y1 > y0:
                a = g[y0 - y:y1 - y, x0 - ix:x1 - ix, 3:4] * color[3]
                rgb = g[y0 - y:y1 - y, x0 - ix:x1 - ix, :3] * np.array(color[:3])
                d = self.canvas[y0:y1, x0:x1, :3]
                self.canvas[y0:y1, x0:x1, :3] = rgb * a + d * (1 - a)
            x += locs[k][2]
        return True

    def rgb(self):
        import numpy as np

        return (self.canvas[..., :3] * 255.0 + 0.5).clip(0, 255).astype(np.uint8)


def load_ritualfont(files, font):
    """(atlas float RGBA, height, [(x, y, w, h)], [index per char]) of fonts/<font>.ritualfont, or None."""
    import numpy as np
    from PIL import Image

    rf = files.get("fonts/%s.ritualfont" % font.lower())
    tga = find_image(files, "gfx/fonts/%s" % font.lower())
    if not rf or not tga:
        return None
    text = read(rf).decode("latin-1")
    m = re.search(r"height\s+([\d.]+)", text)
    ind = re.search(r"indirections\s*\{([^}]*)\}", text)
    loc = re.search(r"locations\s*\{(.*)\}", text, re.S)
    if not (m and ind and loc):
        return None
    locs = [tuple(float(v) for v in g.split()) for g in re.findall(r"\{([^{}]*)\}", loc.group(1))]
    atlas = np.asarray(Image.open(io.BytesIO(read(files[tga]))).convert("RGBA"), np.float64) / 255.0
    return atlas, float(m.group(1)), locs, [int(v) for v in ind.group(1).split()]


def menu_items(files, path):
    """(menu name, [resource]) of a loading urc with its includes appended, in drawing order."""
    text = read(files[path]).decode("latin-1")
    name, incs = parse_menu_header(text)
    _, _, items = parse_urc(text)
    for inc in incs:
        if inc in files:
            items = items + parse_urc(read(files[inc]).decode("latin-1"))[2]
    return name, items


def _rect(it):
    return tuple(int(float(v)) for v in it["rect"][:4])


def compose_screen(files, path):
    """(menu name, 640x480 RGB uint8 array, (bar rect, bar tile shader)) of one loading urc, or None."""
    name, items = menu_items(files, path)
    if not name:
        return None
    painter = Painter(files)
    bar = None
    drawn = 0
    for it in items:
        if it["type"].lower() not in ("label", "button") or "rect" not in it or len(it["rect"]) < 4:
            continue
        if "enabledcvar" in it or " ".join(it.get("name", [])).lower() in HIDDEN:
            continue
        if "statbar" in it:
            shader = (it.get("statbar_tileshader") or it.get("statbar_shader") or [BAR_DEFAULT[1]])[0]
            bar = (_rect(it), shader)
            continue
        if "shader" in it and painter.draw(it["shader"][0], _rect(it)):
            drawn += 1
        if "title" in it and it["title"]:
            fg = [float(v) for v in it.get("fgcolor", ["1", "1", "1", "1"])[:4]]
            font = (it.get("font") or ["facfont-20"])[0]
            if painter.text(" ".join(it["title"]), _rect(it), font, fg):
                drawn += 1
    if not drawn:
        return None
    return name, painter.rgb(), bar or BAR_DEFAULT, painter


def plate_tiles(bar):
    """8x8 tiles (tx, ty, tw, th) under the bar frame, 16-pixel aligned across (XFB lines are 32 bytes)."""
    x, y, w, h = bar
    x0, x1 = (x - 2) // 16 * 16, -(-(x + w + 2) // 16) * 16   # the frame runs 2 px past the fill
    y0, y1 = (y - 4) // 8 * 8, -(-(y + h + 4) // 8) * 8
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, SCREEN[0]), min(y1, SCREEN[1])
    return x0 // 8, y0 // 8, (x1 - x0) // 8, (y1 - y0) // 8


def fill_texture(painter, bar):
    """The bar's fill as uint8 RGB, (w rounded up to 8) x (h rounded up to 8): its tile shader repeated."""
    import numpy as np

    (x, y, w, h), shader = bar
    fw, fh = -(-w // 8) * 8, -(-h // 8) * 8
    stages = painter.stages(shader)
    tex = None
    for path, _ in stages:
        found = find_image(painter.files, path) if path.lower() != "$whiteimage" else None
        if found:
            from PIL import Image

            im = Image.open(io.BytesIO(read(painter.files[found]))).convert("RGB")
            tex = np.asarray(im.resize((im.size[0], h), Image.LANCZOS) if im.size[1] != h else im)
            break
    if tex is None:
        tex = np.zeros((h, 8, 3), np.uint8)
        tex[..., 0] = 170
    reps = -(-fw // tex.shape[1])
    strip = np.tile(tex, (1, reps, 1))[:, :fw]
    out = np.zeros((fh, fw, 3), np.uint8)
    out[:h] = strip
    if fh > h:
        out[h:] = strip[-1:]
    return out


def encode_screen(rgb, bar_rect, fill):
    """The GCMP loading screen file bytes (see the module docstring)."""
    import numpy as np

    tx, ty, tw, th = plate_tiles(bar_rect)
    fh, fw = fill.shape[:2]
    if tw * th * 32 + (fw // 8) * (fh // 8) * 32 > RESIDENT_MAX:
        raise ValueError("bar %r needs more than %d resident bytes" % (bar_rect, RESIDENT_MAX))
    sheet = np.zeros((SCREEN[1] + fh, SCREEN[0], 3), np.uint8)
    sheet[:SCREEN[1]] = rgb
    sheet[SCREEN[1]:, :fw] = fill
    head = b"GCMP" + struct.pack(">HHBBH", SCREEN[0], SCREEN[1] + fh, 0, 1, 0) + bytes(8)
    head += struct.pack(">HHHHBBBB", *bar_rect, tx, ty, tw, th)
    return head + cmpr_encode(sheet)


def screens(inputs):
    """[(file stem, 640x480 RGB array, bar rect, fill RGB array)] for every loading urc in the paks."""
    files = collect(inputs, (".urc", ".txt", ".shader", ".ritualfont") + IMAGE_EXTS)
    out = []
    for path in sorted(p for p in files if LOADING_URC.match(p)):
        got = compose_screen(files, path)
        if not got:
            continue
        name, rgb, bar, painter = got
        stem = "default" if name.lower() == DEFAULT_MENU else name.replace("\\", "/").split("/")[-1].lower()
        out.append((stem, rgb, bar[0], fill_texture(painter, bar)))
    return out


def preview(rgb, bar_rect, fill, frac=0.6):
    """The screen as the game shows it with the bar at frac, a PIL image."""
    from PIL import Image

    out = rgb.copy()
    x, y, w, h = bar_rect
    fw = int(round(w * frac))
    out[y:y + h, x:x + fw] = fill[:h, :fw]
    return Image.fromarray(out)


def write_loading(items, game_root):
    """Write resource/gc_loading/<stem>.cmp for each screen; returns the paths."""
    d = os.path.join(game_root, *OUT.split("/"))
    os.makedirs(d, exist_ok=True)
    written = []
    for stem, rgb, bar, fill in items:
        p = os.path.join(d, stem + ".cmp")
        with open(p, "wb") as f:
            f.write(encode_screen(rgb, bar, fill))
        written.append(p)
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="MOHAA main directory or pk3 files")
    ap.add_argument("--out", help="game folder to write resource/gc_loading/ under")
    ap.add_argument("--png", help="also save a preview of each screen (bar at 60%%) in this folder")
    a = ap.parse_args(argv)
    items = screens(a.inputs)
    if not items:
        print("no ui/loading_*.urc screens in %s" % ", ".join(a.inputs), file=sys.stderr)
        return 1
    if a.png:
        os.makedirs(a.png, exist_ok=True)
        for stem, rgb, bar, fill in items:
            preview(rgb, bar, fill).save(os.path.join(a.png, stem + ".png"))
        print("previews: %s (%d)" % (a.png, len(items)))
    if a.out:
        for p in write_loading(items, a.out):
            print("wrote %s" % p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
