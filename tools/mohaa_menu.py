#!/usr/bin/env python3
"""Make the DoD-GC main menu background from MOHAA's own main menu (the war room with the big map).

    python3 tools/mohaa_menu.py "/path/to/MOHAA/main" --out <sd>/xash3d/<gamedir> [--png preview.png]

MOHAA draws its main menu from ui/main.urc: a 640x480 screen of Label and Button resources, each a
rect and a shader (scripts/mohmenu.shader maps shader names to textures/mohmenu/*.tga). The room
itself is main_a (512x512 at 0,0) over main_b (256x512 at 480,0); the big map, the war records and
the fan sit on top as their own pieces. This draws every piece of the room in urc order, at its rect,
and leaves out what is not the room: menu text buttons (quit, back to game), the hover sign, pieces
gated by a cvar (the 3dfx Voodoo tiles, developer buttons) and invisible hit boxes.

The result goes where the GameCube main menu (mainui BackgroundBitmap) looks first:

    resource/gc_menu/BackgroundLayout.txt   the four quadrant tiles below at 320x240 menu units
    resource/gc_menu/bg_<r>_<c>.tga         160x120 RGB quadrants (the fallback when there is no .cmp)
    resource/gc_menu/bg_<r>_<c>.cmp         320x240 GX CMPR quadrants ("GCMP" header): 640x480 at 4 bpp,
                                            150 KiB of texture memory for the whole sheet
    resource/gc_menu/background.tga/.bmp    the whole sheet at 320x240 (single-sheet path, host tools)

It also writes the retail menu's working parts, which mainui turns into MOHAA's main menu:

    resource/gc_menu/mohaa_main.txt         the layout: sign rect, spots (action, rect, lit image, sign),
                                            buttons (Quit, Back to game) and click sounds
    resource/gc_menu/mohaa/*.tga            each spot's rect of the room with its hover art drawn in (opaque,
                                            loaded only while lit), its sign, the Quit / Back to game art
    sound/mohaa/menu/*.wav                  sound/menu/apply.wav and back.wav as 22 kHz mono PCM

The background files are the same files and sizes the disc build bakes from DoD's own splash, so on the SD card they
take the place of the disc's copies; without them the disc's DoD background shows as before.
The output is retail data: write it outside the repository and never commit it.
"""
import argparse
import io
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ubersound import collect, read  # noqa: E402

URC = "ui/main.urc"
SHEET = (640, 480)          # the menu screen, and the full-resolution sheet
SOFT = (320, 240)           # the GameCube soft-HUD menu units the layout is written in
OUT = "resource/gc_menu"
# Buttons whose command leaves the menu are text on the screen, not part of the room.
UI_COMMAND = re.compile(r"\b(quit|popmenu|disconnect)\b", re.I)
IMAGE_EXTS = (".tga", ".jpg", ".png")

TOKEN = re.compile(r'"([^"]*)"|(\S+)')


def tokens(line):
    return [b if b else q for q, b in TOKEN.findall(line)]


def strip_comments(text):
    return re.sub(r"//[^\n]*", "", text)


# The resource keys a urc writes; a resource written on one line ("resource Label { rect 0 0 512 512
# shader x }") is split before each of them so it reads like the usual one key per line.
URC_KEYS = {"name", "rect", "fgcolor", "bgcolor", "borderstyle", "shader", "hovershader", "selectshader",
            "clicksound", "stuffcommand", "hovercommand", "enabledcvar", "linkcvar", "linkcvartoshader",
            "font", "title", "textalign", "ordernumber", "checked_shader", "unchecked_shader"}
RAW_TOKEN = re.compile(r'"[^"]*"|[{}]|[^\s{}]+')


def urc_lines(text):
    """The urc's lines, with braces on lines of their own and one-line resources split by key."""
    out = []
    for line in strip_comments(text).splitlines():
        cur = []
        for tok in RAW_TOKEN.findall(line):
            if tok in ("{", "}") or (cur and tok.lower() in URC_KEYS and not cur[0] in ("menu",)):
                if cur:
                    out.append(" ".join(cur))
                cur = []
                if tok in ("{", "}"):
                    out.append(tok)
                    continue
            cur.append(tok)
        if cur:
            out.append(" ".join(cur))
    return out


def parse_urc(text):
    """(width, height, [resource]) of a urc menu; each resource is {"type": ..., key: [args]}."""
    width, height = SHEET
    items, cur, depth, rtype, pending = [], None, 0, None, False
    for line in urc_lines(text):
        t = tokens(line)
        if not t:
            continue
        if cur is None:
            if t[0].lower() == "menu" and len(t) >= 4:
                # "menu main 639 479" gives inclusive extents, "menu options_main 640 480" the size
                width, height = int(t[2]), int(t[3])
                width, height = width + width % 2, height + height % 2
            elif t[0].lower() == "resource":
                pending, rtype = True, (t[1] if len(t) > 1 else None)
            elif pending and t[0] != "{":
                rtype = t[0]
            if pending and "{" in t:
                cur, depth, pending = {"type": rtype or ""}, 1, False
            continue
        if t[0] == "{":
            depth += 1
            continue
        if t[0] == "}":
            depth -= 1
            if depth == 0:
                items.append(cur)
                cur = None
            continue
        cur[t[0].lower()] = t[1:]
    return width, height, items


def parse_shaders(text):
    """{shader name: texture path of its first image stage} from Q3/MOHAA shader script text."""
    out = {}
    depth, name = 0, None
    for line in strip_comments(text).splitlines():
        t = tokens(line)
        if not t:
            continue
        if t[0] == "{":
            depth += 1
            continue
        if t[0] == "}":
            depth = max(0, depth - 1)
            if depth == 0:
                name = None
            continue
        if depth == 0:
            name = t[0].lower()
            continue
        if name and depth == 2 and name not in out:
            key = t[0].lower()
            if key in ("map", "clampmap") and len(t) > 1 and not t[1].startswith("$"):
                out[name] = t[1]
            elif key == "animmap" and len(t) > 2:
                out[name] = t[2]   # the first frame
    return out


def find_image(files, path):
    """The game path of an image named path (with or without its extension), or None."""
    p = path.lower().replace("\\", "/")
    if p in files:
        return p
    stem = os.path.splitext(p)[0] if p.endswith(IMAGE_EXTS) else p
    for ext in IMAGE_EXTS:
        if stem + ext in files:
            return stem + ext
    return None


def room_pieces(items):
    """[(shader, (x, y, w, h))] of the resources that draw the room, in drawing order."""
    pieces = []
    for it in items:
        if it["type"].lower() not in ("label", "button"):
            continue
        if "shader" not in it or "rect" not in it or len(it["rect"]) < 4:
            continue
        if "enabledcvar" in it or "linkcvartoshader" in it or "linkcvar" in it:
            continue
        cmd = " ".join(it.get("stuffcommand", []))
        if it["type"].lower() == "button" and UI_COMMAND.search(cmd):
            continue
        pieces.append((it["shader"][0], tuple(int(float(v)) for v in it["rect"][:4])))
    return pieces


INCLUDE = re.compile(r'^[ \t]*include[ \t]+"?([^"\s]+)"?[ \t]*$', re.I | re.M)


def urc_text(files, urc, depth=0):
    """A urc's text with its include "ui/x.inc" lines replaced by those files (ui/serverback.inc)."""
    text = read(files[urc]).decode("latin-1")
    if depth > 4:
        return text

    def inc(m):
        name = m.group(1).lower().replace("\\", "/")
        return urc_text(files, name, depth + 1) if name in files else ""
    return INCLUDE.sub(inc, strip_comments(text))


def compose(inputs, urc=URC):
    """The MOHAA main menu room as a 640x480 RGB PIL image, or None when the paks have no menu."""
    from PIL import Image

    files = collect(inputs, (".urc", ".inc", ".shader") + IMAGE_EXTS)
    if urc not in files:
        return None
    width, height, items = parse_urc(urc_text(files, urc))
    shaders = {}
    for path in sorted(p for p in files if p.startswith("scripts/") and p.endswith(".shader")):
        for k, v in parse_shaders(read(files[path]).decode("latin-1")).items():
            shaders.setdefault(k, v)
    sheet = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    drawn = 0
    for shader, (x, y, w, h) in room_pieces(items):
        tex = shaders.get(shader.lower(), shader)
        path = find_image(files, tex)
        if not path:
            continue
        im = Image.open(io.BytesIO(read(files[path]))).convert("RGBA")
        if im.size != (w, h):
            im = im.resize((w, h), Image.LANCZOS)
        layer = Image.new("RGBA", sheet.size, (0, 0, 0, 0))
        layer.paste(im, (x, y))   # clips pieces that run off the screen (main_a, main_b)
        sheet = Image.alpha_composite(sheet, layer)
        drawn += 1
    if not drawn:
        return None
    sheet = sheet.convert("RGB")
    if sheet.size != SHEET:
        sheet = sheet.resize(SHEET, Image.LANCZOS)
    return sheet


# What each retail main menu button does, by its stuffcommand, as a GameCube main menu action.
ACTIONS = (
    (re.compile(r"pushmenu\s+briefingroom", re.I), "newgame"),
    (re.compile(r"pushmenu\s+multiplayer", re.I), "multiplayer"),
    (re.compile(r"pushmenu\s+options", re.I), "options"),
    (re.compile(r"pushmenu\s+war_records", re.I), "records"),
    (re.compile(r"spmap\s+credits", re.I), "credits"),
    (re.compile(r"^\s*quit\b", re.I), "quit"),
    (re.compile(r"popmenu", re.I), "resume"),
)
SIGN = re.compile(r"set\s+ui_signshader\s+(\S+)", re.I)
# The menu's click sounds (clicksound) by the mainui sound they stand in for.
SOUNDS = (("launch", "sound/menu/apply.wav"), ("out", "sound/menu/back.wav"))
ROOM = OUT + "/mohaa"
LAYOUT = OUT + "/mohaa_main.txt"


def action_of(cmd):
    for pat, name in ACTIONS:
        if pat.search(cmd):
            return name
    return None


def room_menu(inputs, urc=URC):
    """The retail main menu's working parts, or None: {"sheet": the room (PIL RGB 640x480), "sign": rect,
    "spots": [(action, rect, hover PIL image of the whole rect, sign PIL image or None)],
    "buttons": [(action, rect, normal, focus)], "sounds": [(mainui sound, game path, bytes)]}.

    A spot is a part of the room that lights up under the cursor (the map, the doors, the projector);
    its hover image is the room under the rect with the hover art drawn in, so it can be drawn opaque."""
    from PIL import Image

    files = collect(inputs, (".urc", ".shader", ".wav") + IMAGE_EXTS)
    if urc not in files:
        return None
    sheet = compose(inputs, urc)
    if sheet is None:
        return None
    width, height, items = parse_urc(read(files[urc]).decode("latin-1"))
    shaders = {}
    for path in sorted(p for p in files if p.startswith("scripts/") and p.endswith(".shader")):
        for k, v in parse_shaders(read(files[path]).decode("latin-1")).items():
            shaders.setdefault(k, v)
    sx, sy = SHEET[0] / float(width), SHEET[1] / float(height)

    def image(shader):
        path = find_image(files, shaders.get(shader.lower(), shader))
        return Image.open(io.BytesIO(read(files[path]))).convert("RGBA") if path else None

    menu = {"sheet": sheet, "sign": None, "spots": [], "buttons": [], "sounds": []}
    for it in items:
        rect = tuple(int(float(v)) for v in it.get("rect", [])[:4])
        if len(rect) < 4:
            continue
        rect = (round(rect[0] * sx), round(rect[1] * sy), round(rect[2] * sx), round(rect[3] * sy))
        if it["type"].lower() == "label" and "linkcvartoshader" in it and it.get("name", [""])[0].lower() == "sign":
            menu["sign"] = rect
            continue
        if it["type"].lower() != "button" or "enabledcvar" in it:
            continue
        action = action_of(" ".join(it.get("stuffcommand", [])))
        if not action:
            continue
        hover = image(it["hovershader"][0]) if "hovershader" in it else None
        x, y, w, h = rect
        sign = SIGN.search(" ".join(it.get("hovercommand", [])))
        if action in ("quit", "resume"):
            normal = image(it["shader"][0]) if "shader" in it else None
            if normal is not None and hover is not None:
                menu["buttons"].append((action, rect, normal.resize((w, h), Image.LANCZOS).convert("RGB"),
                                        hover.resize((w, h), Image.LANCZOS).convert("RGB")))
            continue
        if hover is None:
            continue
        lit = sheet.convert("RGBA").crop((x, y, x + w, y + h))
        lit.alpha_composite(hover.resize((w, h), Image.LANCZOS))
        menu["spots"].append((action, rect, lit.convert("RGB"),
                              image(sign.group(1)).convert("RGB") if sign and image(sign.group(1)) else None))
    menu["spots"].sort(key=lambda s: (s[1][0] + s[1][2] / 2.0, s[1][1]))   # left to right across the room
    for name, path in SOUNDS:
        if path in files:
            menu["sounds"].append((name, path, read(files[path])))
    return menu


def write_room_menu(menu, game_root):
    """Write the retail main menu's parts and resource/gc_menu/mohaa_main.txt under game_root (the
    GameCube main menu draws the room menu when that file is there); returns the written paths."""
    import ubersound

    room = os.path.join(game_root, *ROOM.split("/"))
    os.makedirs(room, exist_ok=True)
    written = []

    def save(img, name):
        p = os.path.join(room, name)
        img.save(p, format="TGA")
        written.append(p)
        return ROOM + "/" + name

    lines = ["// The retail MOHAA main menu for the GameCube main menu (mainui), written by",
             "// mohaa-gc tools/mohaa_menu.py from the player's own ui/main.urc. Rects are x y w h on a",
             "// 640x480 screen. spot: a part of the room that lights up (hover image) and names itself on the",
             "// sign; button: a picture button (normal, focus). The action is what A / Enter opens.",
             "screen %d %d" % SHEET]
    if menu["sign"]:
        lines.append("sign %d %d %d %d" % menu["sign"])
    for i, (action, rect, lit, sign) in enumerate(menu["spots"]):
        hover = save(lit, "spot%d_%s.tga" % (i, action))
        signp = save(sign, "sign%d_%s.tga" % (i, action)) if sign is not None else "-"
        lines.append("spot %s %d %d %d %d %s %s" % ((action,) + rect + (hover, signp)))
    for action, rect, normal, focus in menu["buttons"]:
        lines.append("button %s %d %d %d %d %s %s" % ((action,) + rect + (
            save(normal, "%s.tga" % action), save(focus, "%s_h.tga" % action))))
    for name, path, data in menu["sounds"]:
        rel = "sound/mohaa/" + path[len("sound/"):]
        dest = os.path.join(game_root, *rel.split("/"))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if ubersound.convert_wav(data, dest) is None:
            written.append(dest)
            lines.append("sound %s %s" % (name, rel))
    p = os.path.join(game_root, *LAYOUT.split("/"))
    with open(p, "w", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    written.append(p)
    return written


# The retail pages after the war room that mainui draws as retail does (menus/MohaaPage.cpp): the urc
# whose picture is the page, and what each button does there, by its stuffcommand.
PAGES = {
    "options": ("ui/options_main.urc", (
        (re.compile(r"pushmenu\s+advancedoptions", re.I), "advanced"),
        (re.compile(r"pushmenu\s+audio_options", re.I), "audio"),
        (re.compile(r"pushmenu\s+controls", re.I), "controls"),
        (re.compile(r"pushmenu\s+video_options", re.I), "video"),
        (re.compile(r"popmenu", re.I), "back"),
    )),
    "gametype": ("ui/multiplayerstart.urc", (
        (re.compile(r"pushmenu\s+multiplayerstart_ffa", re.I), "ffa"),
        (re.compile(r"pushmenu\s+multiplayerstart_team", re.I), "team"),
        (re.compile(r"pushmenu\s+multiplayerstart_round", re.I), "round"),
        (re.compile(r"pushmenu\s+multiplayerstart_obj", re.I), "obj"),
        (re.compile(r"popmenu", re.I), "back"),
    )),
}
PAGE_STANDIN = (64, 48)   # a page quadrant's .tga stand-in for its 320x240 .cmp
PAGE_SIGN = re.compile(r"set\s+ui_\w*shader\s+(\S+)", re.I)
ADDITIVE = ("alphaadd", "add", "gl_one gl_one", "gl_src_alpha gl_one")


def parse_stages(text):
    """{shader name: {"map": path or "$whiteimage", "blend": blendfunc text, "alpha": constant or None}}
    of each shader's first stage (the menu glows are $whiteimage added at a constant alpha)."""
    out = {}
    depth, name, stage = 0, None, None
    for line in strip_comments(text).splitlines():
        t = tokens(line)
        if not t:
            continue
        if t[0] == "{":
            depth += 1
            if depth == 2 and name and name not in out:
                stage = {"map": None, "blend": "", "alpha": None}
            continue
        if t[0] == "}":
            if depth == 2 and stage is not None:
                out[name] = stage
                stage = None
            depth = max(0, depth - 1)
            if depth == 0:
                name = None
            continue
        if depth == 0:
            name = t[0].lower()
            continue
        if stage is None:
            continue
        key = t[0].lower()
        if key in ("map", "clampmap") and len(t) > 1:
            stage["map"] = t[1]
        elif key == "animmap" and len(t) > 2:
            stage["map"] = t[2]
        elif key == "blendfunc":
            stage["blend"] = " ".join(t[1:]).lower()
        elif key == "alphagen" and len(t) > 2 and t[1].lower() == "constant":
            stage["alpha"] = float(t[2])
    return out


def lit_image(files, stages, sheet, shader, rect):
    """The page under rect with the hover shader drawn over it, as retail draws it: added (the
    menu_button_glow family, a constant-alpha white or mask) or blended (plain hover art). RGB, or None."""
    import numpy as np
    from PIL import Image

    x, y, w, h = rect
    base = np.asarray(sheet.convert("RGB").crop((x, y, x + w, y + h)), dtype=np.float32)
    st = stages.get(shader.lower(), {"map": shader, "blend": "", "alpha": None})
    src = st["map"] or shader
    if src.startswith("$"):
        art = np.full((h, w, 4), 255.0, dtype=np.float32)
    else:
        path = find_image(files, src)
        if not path:
            return None
        im = Image.open(io.BytesIO(read(files[path]))).convert("RGBA").resize((w, h), Image.LANCZOS)
        art = np.asarray(im, dtype=np.float32)
    alpha = art[..., 3:4] / 255.0
    if st["alpha"] is not None:
        alpha = alpha * st["alpha"]
    if st["blend"] in ADDITIVE:
        out = base + art[..., :3] * alpha
    else:
        out = base * (1.0 - alpha) + art[..., :3] * alpha
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8), "RGB")


def page_menu(inputs, page):
    """A retail page's working parts, or None: {"sheet": the page (PIL RGB 640x480), "sign": rect,
    "spots": [(action, rect, lit, sign or None)], "buttons": [(action, rect, normal, focus)]}."""
    from PIL import Image

    urc, actions = PAGES[page]
    files = collect(inputs, (".urc", ".inc", ".shader") + IMAGE_EXTS)
    if urc not in files:
        return None
    sheet = compose(inputs, urc)
    if sheet is None:
        return None
    width, height, items = parse_urc(urc_text(files, urc))
    shaders, stages = {}, {}
    for path in sorted(p for p in files if p.startswith("scripts/") and p.endswith(".shader")):
        text = read(files[path]).decode("latin-1")
        for k, v in parse_shaders(text).items():
            shaders.setdefault(k, v)
        for k, v in parse_stages(text).items():
            stages.setdefault(k, v)
    sx, sy = SHEET[0] / float(width), SHEET[1] / float(height)

    def image(shader):
        path = find_image(files, shaders.get(shader.lower(), shader))
        return Image.open(io.BytesIO(read(files[path]))).convert("RGBA") if path else None

    def act(cmd):
        for pat, name in actions:
            if pat.search(cmd):
                return name
        return None

    menu = {"sheet": sheet, "sign": None, "spots": [], "buttons": []}
    taken = set()
    for it in items:
        rect = tuple(int(float(v)) for v in it.get("rect", [])[:4])
        if len(rect) < 4:
            continue
        rect = (round(rect[0] * sx), round(rect[1] * sy), round(rect[2] * sx), round(rect[3] * sy))
        if it["type"].lower() == "label" and "linkcvartoshader" in it:
            menu["sign"] = rect
            continue
        if it["type"].lower() != "button" or "enabledcvar" in it or "hovershader" not in it:
            continue
        action = act(" ".join(it.get("stuffcommand", [])))
        if not action or action in taken:
            continue
        x, y, w, h = rect
        if action == "back":
            normal, focus = image(it["shader"][0]) if "shader" in it else None, image(it["hovershader"][0])
            if normal is not None and focus is not None:
                menu["buttons"].append((action, rect, normal.resize((w, h), Image.LANCZOS).convert("RGB"),
                                        focus.resize((w, h), Image.LANCZOS).convert("RGB")))
                taken.add(action)
            continue
        lit = lit_image(files, stages, sheet, it["hovershader"][0], rect)
        if lit is None:
            continue
        sign = PAGE_SIGN.search(" ".join(it.get("hovercommand", [])))
        signim = image(sign.group(1)) if sign else None
        menu["spots"].append((action, rect, lit, signim.convert("RGB") if signim is not None else None))
        taken.add(action)
    if not menu["spots"]:
        return None
    menu["spots"].sort(key=lambda s: (s[1][1], s[1][0]))   # top to bottom: the D-pad's order
    return menu


def write_page(menu, game_root, page):
    """Write a retail page under game_root: its picture as four quadrants (resource/gc_menu/bg_<page>_<r>_<c>
    .cmp, 320x240 GX CMPR, which the GameCube draws, and a 64x48 .tga stand-in), its parts under
    resource/gc_menu/mohaa/<page>/ and resource/gc_menu/mohaa_<page>.txt; returns the written paths."""
    from PIL import Image
    import numpy as np

    out = os.path.join(game_root, *OUT.split("/"))
    parts = os.path.join(game_root, *ROOM.split("/"), page)
    os.makedirs(parts, exist_ok=True)
    written = []

    def save(img, name):
        p = os.path.join(parts, name)
        img.save(p, format="TGA")
        written.append(p)
        return "%s/%s/%s" % (ROOM, page, name)

    sheet = menu["sheet"]
    fw, fh = SHEET[0] // 2, SHEET[1] // 2
    quads = []
    for row in range(2):
        for col in range(2):
            name = "bg_%s_%d_%d" % (page, row, col)
            quad = sheet.crop((col * fw, row * fh, (col + 1) * fw, (row + 1) * fh))
            p = os.path.join(out, name + ".tga")
            # The GameCube draws the .cmp; this .tga only stands in for it (and shows if the .cmp
            # cannot load). Kept small: a 160x120 quadrant took a 75 KiB decode buffer from the
            # 131 KiB image pool, and a second page's quadrants no longer fit.
            quad.resize(PAGE_STANDIN, Image.LANCZOS).save(p, format="TGA")
            written.append(p)
            p = os.path.join(out, name + ".cmp")
            with open(p, "wb") as fh_out:
                fh_out.write(b"GCMP" + struct.pack(">HH", fw, fh) + bytes(24) + cmpr_encode(np.asarray(quad)))
            written.append(p)
            quads.append("%s/%s.tga" % (OUT, name))
    lines = ["// The retail MOHAA %s page for the GameCube menu (mainui MohaaPage.cpp), written by" % page,
             "// mohaa-gc tools/mohaa_menu.py from the player's own %s. Rects are x y w h on a" % PAGES[page][0],
             "// 640x480 screen; the background is the page in four quadrants (tl tr bl br).",
             "screen %d %d" % SHEET,
             "background " + " ".join(quads)]
    if menu["sign"]:
        lines.append("sign %d %d %d %d" % menu["sign"])
    for i, (action, rect, lit, sign) in enumerate(menu["spots"]):
        hover = save(lit, "spot%d_%s.tga" % (i, action))
        signp = save(sign, "sign%d_%s.tga" % (i, action)) if sign is not None else "-"
        lines.append("spot %s %d %d %d %d %s %s" % ((action,) + rect + (hover, signp)))
    for action, rect, normal, focus in menu["buttons"]:
        lines.append("button %s %d %d %d %d %s %s" % ((action,) + rect + (
            save(normal, "%s.tga" % action), save(focus, "%s_h.tga" % action))))
    p = os.path.join(out, "mohaa_%s.txt" % page)
    with open(p, "w", newline="\n") as fh_out:
        fh_out.write("\n".join(lines) + "\n")
    written.append(p)
    return written


def cmpr_encode(rgb):
    """GX CMPR (DXT1, opaque) of an HxWx3 uint8 array (sides multiples of 8): per 4x4 block the endpoints
    are the extremes along the block's principal colour axis, and blocks go in 8x8 tiles of 2x2,
    big-endian, as the GameCube texture unit reads them."""
    import numpy as np

    h, w, _ = rgb.shape
    flat = rgb.astype(np.float64).reshape(h // 4, 4, w // 4, 4, 3).transpose(0, 2, 1, 3, 4).reshape(h // 4, w // 4, 16, 3)
    mean = flat.mean(2, keepdims=True)
    d = flat - mean
    cov = np.einsum("...ni,...nj->...ij", d, d)
    axis = np.ones(cov.shape[:-1]) / np.sqrt(3.0)
    for _ in range(8):   # power iteration for the dominant axis
        axis = np.einsum("...ij,...j->...i", cov, axis)
        norm = np.linalg.norm(axis, axis=-1, keepdims=True)
        axis = np.where(norm > 1e-9, axis / np.maximum(norm, 1e-9), 1.0 / np.sqrt(3.0))
    proj = np.einsum("...ni,...i->...n", d, axis)
    hi = np.clip(mean[..., 0, :] + axis * proj.max(-1, keepdims=True), 0, 255).astype(np.int32)
    lo = np.clip(mean[..., 0, :] + axis * proj.min(-1, keepdims=True), 0, 255).astype(np.int32)

    def to565(c):
        return ((c[..., 0] >> 3) << 11) | ((c[..., 1] >> 2) << 5) | (c[..., 2] >> 3)

    def from565(v):
        r, g, b = (v >> 11) & 31, (v >> 5) & 63, v & 31
        return np.stack(((r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2)), -1)

    c0, c1 = to565(hi), to565(lo)
    swap = c0 < c1                       # c0 > c1 selects the 4-colour (opaque) mode
    c0, c1 = np.where(swap, c1, c0), np.where(swap, c0, c1)
    e0, e1 = from565(c0), from565(c1)
    pal = np.stack((e0, e1, (2 * e0 + e1) // 3, (e0 + 2 * e1) // 3), 2)
    idx = ((flat[:, :, :, None, :] - pal[:, :, None, :, :]) ** 2).sum(-1).argmin(-1)
    idx = np.where((c0 == c1)[..., None], 0, idx)
    rows = idx.reshape(h // 4, w // 4, 4, 4)
    bits = (rows[..., 0] << 6) | (rows[..., 1] << 4) | (rows[..., 2] << 2) | rows[..., 3]
    out = bytearray()
    for ty in range(0, h // 4, 2):
        for tx in range(0, w // 4, 2):
            for by, bx in ((ty, tx), (ty, tx + 1), (ty + 1, tx), (ty + 1, tx + 1)):
                out += struct.pack(">HH", int(c0[by, bx]), int(c1[by, bx]))
                out += bytes(int(b) for b in bits[by, bx])
    return bytes(out)


def cmpr_decode(data, w, h):
    """HxWx3 uint8 array from GX CMPR bytes made by cmpr_encode (for checks and previews)."""
    import numpy as np

    out = np.zeros((h, w, 3), np.uint8)
    pos = 0
    for ty in range(0, h // 4, 2):
        for tx in range(0, w // 4, 2):
            for by, bx in ((ty, tx), (ty, tx + 1), (ty + 1, tx), (ty + 1, tx + 1)):
                c0, c1 = struct.unpack(">HH", data[pos:pos + 4])
                bits = data[pos + 4:pos + 8]
                pos += 8
                e = [np.array((((c >> 11) & 31) * 255 // 31, ((c >> 5) & 63) * 255 // 63, (c & 31) * 255 // 31))
                     for c in (c0, c1)]
                pal = [e[0], e[1], (2 * e[0] + e[1]) // 3, (e[0] + 2 * e[1]) // 3]
                for yy in range(4):
                    for xx in range(4):
                        out[by * 4 + yy, bx * 4 + xx] = pal[(bits[yy] >> (6 - 2 * xx)) & 3]
    return out


def write_gc_menu(sheet, game_root):
    """Write the GameCube menu background files for a 640x480 RGB sheet under game_root; returns their paths."""
    import numpy as np
    from PIL import Image

    menu = os.path.join(game_root, *OUT.split("/"))
    os.makedirs(menu, exist_ok=True)
    written = []
    soft = sheet.resize(SOFT, Image.LANCZOS)
    for ext, fmt in ((".tga", "TGA"), (".bmp", "BMP")):
        p = os.path.join(menu, "background" + ext)
        soft.save(p, format=fmt)
        written.append(p)
    tw, th = SOFT[0] // 2, SOFT[1] // 2
    fw, fh = SHEET[0] // 2, SHEET[1] // 2
    layout = ["resolution\t%d\t%d" % SOFT, ""]
    for row in range(2):
        for col in range(2):
            name = "bg_%d_%d" % (row, col)
            tile = soft.crop((col * tw, row * th, (col + 1) * tw, (row + 1) * th))
            p = os.path.join(menu, name + ".tga")
            tile.save(p, format="TGA")
            written.append(p)
            quad = np.asarray(sheet.crop((col * fw, row * fh, (col + 1) * fw, (row + 1) * fh)))
            p = os.path.join(menu, name + ".cmp")
            with open(p, "wb") as fh_out:
                fh_out.write(b"GCMP" + struct.pack(">HH", fw, fh) + bytes(24) + cmpr_encode(quad))
            written.append(p)
            layout.append("%s/%s.tga\tfit\t%d\t%d" % (OUT, name, col * tw, row * th))
    p = os.path.join(menu, "BackgroundLayout.txt")
    with open(p, "w", newline="\n") as fh_out:
        fh_out.write("\n".join(layout) + "\n")
    written.append(p)
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="MOHAA main directory or pk3 files")
    ap.add_argument("--out", help="game folder to write resource/gc_menu/ under")
    ap.add_argument("--png", help="also save the 640x480 sheet here (a preview)")
    a = ap.parse_args(argv)
    sheet = compose(a.inputs)
    if sheet is None:
        print("no %s with drawable pieces in %s" % (URC, ", ".join(a.inputs)), file=sys.stderr)
        return 1
    if a.png:
        sheet.save(a.png)
        print("preview: %s" % a.png)
    if a.out:
        for p in write_gc_menu(sheet, a.out):
            print("wrote %s" % p)
        menu = room_menu(a.inputs)
        if menu:
            for p in write_room_menu(menu, a.out):
                print("wrote %s" % p)
        for page in PAGES:
            pm = page_menu(a.inputs, page)
            if pm:
                for p in write_page(pm, a.out, page):
                    print("wrote %s" % p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
