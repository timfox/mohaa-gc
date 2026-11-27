"""Tests for tools/mohaa_menu.py on a made-up menu (no retail data)."""
import io
import os
import struct
import sys
import tempfile
import unittest
import wave
import zipfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

try:
    import numpy as np
    from PIL import Image
except ImportError:  # pragma: no cover
    np = Image = None

import mohaa_menu  # noqa: E402
import mohaa_sd  # noqa: E402

URC = """menu "main" 639 479 NONE 0
virtualres 1
resource
Label
{
name "Default"
rect 480 0 256 512
shader "room_b"
}
resource
Label
{
name "Default"
rect 0 0 512 512
shader "room_a"
}
resource
Label
{
rect 0 0 256 256
shader "textures/mohmenu/voodoo/main_a.tga"
enabledcvar "ui_voodoo"
}
resource
Button
{
name "map"
rect 100 100 64 32
shader "bigmap"
hovershader "bigmap_h"
stuffcommand "pushmenu briefingroom"
hovercommand "set ui_signshader newgame_sign"
}
resource
Button
{
name "quit"
rect 536 448 96 24
shader "textures/mohmenu/quit"
hovershader "textures/mohmenu/quit_h"
clicksound "sound/menu/back.wav"
stuffcommand "quit"
}
resource
Label
{
name "sign"
rect 48 36 172 56
linkcvar "ui_signshader"
linkcvartoshader
}
resource
Button
{
name "options"
rect 0 172 128 128
shader "menu_button_trans"
hovershader "textures/mohmenu/options_h"
stuffcommand "pushmenu options_main"
hovercommand "set ui_signshader options_sign"
}
resource
Button
{
name "dev"
rect 436 156 24 48
shader "menu_button_trans"
hovershader "textures/mohmenu/options_h"
stuffcommand "maplist"
enabledcvar "developer"
}
resource
Button
{
rect 0 172 128 128
shader "menu_button_trans"
}
"""

SHADER = """// menu
room_a
{
   nomipmaps
   {
      blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
	clampMap textures/mohmenu/main_a.tga
   }
}
room_b
{
   {
	clampMap textures/mohmenu/main_b.tga
   }
}
bigmap
{
   {
      animMap 24 textures/mohmenu/map1.tga textures/mohmenu/map2.tga
   }
}
options_sign
{
	{
	clampMap textures/mohmenu/options_sign.tga
	}
}
bigmap_h
{
   {
      clampMap textures/mohmenu/options_h.tga
   }
}
menu_button_trans
{
	{
		map $whiteimage
	}
}
"""

# A made-up options desk and game type page in the retail shape: a glow button added at a constant
# alpha, a plain hover image, a sign label and Back; the game type page pulls its picture from an include.
OPTIONS_URC = """menu "options_main" 640 480 NONE 0
resource
Label
{
rect 0 0 512 512
shader "desk_a"
}
resource
Label
{
rect 480 0 256 512
shader "desk_a"
}
resource
Button
{
name "video button"
rect 400 300 100 50
shader "menu_button_trans"
hovershader "menu_button_glow"
stuffcommand "pushmenu video_options"
hovercommand "set ui_optionshader video_sign"
}
resource
Button
{
name "advanced options"
rect 200 40 100 50
shader "menu_button_trans"
hovershader "textures/mohmenu/options_h"
stuffcommand "pushmenu advancedoptions"
}
resource
Label
{
rect 98 52 128 32
linkcvar "ui_optionshader"
linkcvartoshader
}
resource
Button
{
name "back"
rect 8 448 96 24
shader "textures/mohmenu/back"
hovershader "textures/mohmenu/back_h"
stuffcommand "popmenu 0"
}
"""

GAMETYPE_URC = """menu "multiplayerstart" 640 479 NONE 0
include "ui/serverback.inc"
resource
Button
{
name "Team-Match"
rect 192 192 256 64
shader "menu_button_trans"
hovershader "textures/mohmenu/options_h"
stuffcommand "set ui_dmmap dm/mohdm1;pushmenu multiplayerstart_team"
}
resource
Button
{
name "Free-For-All"
rect 192 112 256 64
shader "menu_button_trans"
hovershader "textures/mohmenu/options_h"
stuffcommand "set ui_dmmap dm/mohdm1;pushmenu multiplayerstart_ffa"
}
"""

FFA_URC = """menu "multiplayerstart_ffa" 639 479 NONE 0
include "ui/serverback.inc"
resource
Label
{
name "Multiplayer : Free-For-All Start"
rect 64 16 512 432
shader "ffaserverback"
}
resource
Label
{
rect 64 16 256 216
shader "textures/mohmenu/voodoo/ffa_a"
enabledcvar "ui_voodoo"
}
resource
Button
{
rect 8 440 96 24
shader "textures/mohmenu/back"
hovershader "textures/mohmenu/back_h"
stuffcommand "Popmenu 0"
}
resource
Label
{
title "map title"
rect 88 106 208 24
linkcvar "ui_dmmap"
}
resource
Field
{
title "server name entry"
rect 260 314 292 28
linkcvar "ui_hostname"
}
resource
Field
{
title "maplist entry"
rect 212 252 344 28
linkcvar "ui_maplist_ffa"
}
resource
Button
{
name "Select Map"
rect 134 84 112 16
shader "menu_button_trans"
hovershader "menu_button_glow"
stuffcommand "dmmapselect dm dm"
}
resource
Button
{
name "Start Game"
rect 264 416 112 16
shader "menu_button_trans"
hovershader "menu_button_glow"
stuffcommand "ui_startdmmap 1 Free-For-All ui_maplist_ffa"
}
resource
Field
{
title "max player entry"
rect 498 92 60 28
linkcvar "ui_maxclients"
}
"""

SERVERBACK = """resource Label { name "Default" rect 0 0 512 512 fgcolor 0.00 0.00 0.00 1.00 shader "serverback_a" }
resource
Label
{
rect 384 0 256 512
shader "serverback_a"
}
"""

PAGE_SHADER = """desk_a
{
	{
	clampMap textures/mohmenu/options_a.tga
	}
}
ffaserverback
{
	{
	clampMap textures/mohmenu/ffaserverback.tga
	}
}
serverback_a
{
	{
	clampMap textures/mohmenu/serverback_a.tga
	}
}
video_sign
{
	{
	clampMap textures/mohmenu/video_sign.tga
	}
}
menu_button_glow
{
	{
		map $whiteimage
		blendfunc alphaadd
		alphagen constant 0.2
	}
}
"""

RED, BLUE, GREEN, WHITE = (200, 0, 0), (0, 0, 200), (0, 200, 0), (255, 255, 255)


def tga(colour, size):
    b = io.BytesIO()
    Image.new("RGB", size, colour).save(b, format="TGA")
    return b.getvalue()


def make_pak(path):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("ui/main.urc", URC)
        z.writestr("scripts/mohmenu.shader", SHADER)
        z.writestr("textures/mohmenu/main_a.tga", tga(RED, (512, 512)))
        z.writestr("textures/mohmenu/main_b.tga", tga(BLUE, (256, 512)))
        z.writestr("textures/mohmenu/map1.tga", tga(GREEN, (128, 128)))
        z.writestr("textures/mohmenu/quit.tga", tga(WHITE, (96, 24)))
        z.writestr("textures/mohmenu/quit_h.tga", tga(GREEN, (128, 32)))
        z.writestr("textures/mohmenu/options_h.tga", tga(WHITE, (128, 128)))
        z.writestr("textures/mohmenu/options_sign.tga", tga(BLUE, (256, 64)))
        b = io.BytesIO()
        with wave.open(b, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(44100)
            w.writeframes(bytes(4 * 441))
        z.writestr("sound/menu/back.wav", b.getvalue())
        z.writestr("textures/mohmenu/voodoo/main_a.tga", tga(WHITE, (256, 256)))


def make_page_pak(path):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("ui/options_main.urc", OPTIONS_URC)
        z.writestr("ui/multiplayerstart.urc", GAMETYPE_URC.replace("\n", "\r\n"))   # retail urcs are CRLF
        z.writestr("ui/multiplayerstart_ffa.urc", FFA_URC.replace("\n", "\r\n"))
        z.writestr("ui/serverback.inc", SERVERBACK)
        z.writestr("textures/mohmenu/ffaserverback.tga", tga((230, 220, 190), (512, 432)))
        z.writestr("scripts/mohmenu.shader", SHADER + PAGE_SHADER)
        z.writestr("textures/mohmenu/options_a.tga", tga((100, 50, 0), (512, 512)))
        z.writestr("textures/mohmenu/serverback_a.tga", tga(BLUE, (512, 512)))
        z.writestr("textures/mohmenu/options_h.tga", tga(WHITE, (128, 128)))
        z.writestr("textures/mohmenu/video_sign.tga", tga(GREEN, (128, 32)))
        z.writestr("textures/mohmenu/back.tga", tga(RED, (128, 32)))
        z.writestr("textures/mohmenu/back_h.tga", tga(GREEN, (128, 32)))


@unittest.skipIf(np is None, "needs Pillow and numpy")
class MenuTest(unittest.TestCase):
    def test_parse(self):
        w, h, items = mohaa_menu.parse_urc(URC)
        self.assertEqual((w, h), (640, 480))
        self.assertEqual([i["type"] for i in items],
                         ["Label", "Label", "Label", "Button", "Button", "Label", "Button", "Button", "Button"])
        self.assertEqual(mohaa_menu.room_pieces(items), [
            ("room_b", (480, 0, 256, 512)), ("room_a", (0, 0, 512, 512)), ("bigmap", (100, 100, 64, 32)),
            ("menu_button_trans", (0, 172, 128, 128)), ("menu_button_trans", (0, 172, 128, 128))])
        sh = mohaa_menu.parse_shaders(SHADER)
        self.assertEqual(sh["room_a"], "textures/mohmenu/main_a.tga")
        self.assertEqual(sh["bigmap"], "textures/mohmenu/map1.tga")
        self.assertNotIn("menu_button_trans", sh)

    def test_compose_draws_the_room_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_pak(os.path.join(tmp, "pak0.pk3"))
            sheet = mohaa_menu.compose([tmp])
        self.assertEqual(sheet.size, (640, 480))
        self.assertEqual(sheet.getpixel((10, 10)), RED)       # main_a over main_b, voodoo tile skipped
        self.assertEqual(sheet.getpixel((600, 10)), BLUE)      # main_b where main_a ends
        self.assertEqual(sheet.getpixel((120, 110)), GREEN)    # map piece, first anim frame, scaled to rect
        self.assertEqual(sheet.getpixel((580, 460)), BLUE)     # no quit button
        self.assertEqual(sheet.getpixel((10, 200)), RED)       # invisible hit box draws nothing

    def test_no_menu(self):
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(os.path.join(tmp, "pak0.pk3"), "w") as z:
                z.writestr("maps/t1.scr", "main:\nend\n")
            self.assertIsNone(mohaa_menu.compose([tmp]))

    def test_cmpr_round_trip(self):
        rng = np.random.default_rng(1)
        img = np.zeros((16, 16, 3), np.uint8)
        img[:8, :8] = (255, 0, 0)
        img[:8, 8:] = (0, 255, 0)
        img[8:] = np.linspace(0, 255, 16, dtype=np.uint8)[None, :, None]
        data = mohaa_menu.cmpr_encode(img)
        self.assertEqual(len(data), 16 * 16 // 2)
        back = mohaa_menu.cmpr_decode(data, 16, 16).astype(int)
        self.assertLess(np.abs(back - img.astype(int)).max(), 24)
        noise = rng.integers(0, 255, (8, 8, 3), dtype=np.uint8)
        self.assertEqual(mohaa_menu.cmpr_decode(mohaa_menu.cmpr_encode(noise), 8, 8).shape, (8, 8, 3))

    def test_gc_menu_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_pak(os.path.join(tmp, "pak0.pk3"))
            out = os.path.join(tmp, "out")
            written = mohaa_menu.write_gc_menu(mohaa_menu.compose([tmp]), out)
            menu = os.path.join(out, "resource", "gc_menu")
            self.assertEqual(sorted(os.path.basename(p) for p in written), sorted(
                ["background.tga", "background.bmp", "BackgroundLayout.txt"]
                + ["bg_%d_%d.%s" % (r, c, e) for r in range(2) for c in range(2) for e in ("tga", "cmp")]))
            with open(os.path.join(menu, "BackgroundLayout.txt")) as f:
                layout = f.read().split()
            self.assertEqual(layout[:3], ["resolution", "320", "240"])
            self.assertIn("resource/gc_menu/bg_1_1.tga", layout)
            self.assertEqual(Image.open(os.path.join(menu, "bg_0_0.tga")).size, (160, 120))
            self.assertEqual(Image.open(os.path.join(menu, "background.tga")).size, (320, 240))
            with open(os.path.join(menu, "bg_0_1.cmp"), "rb") as f:
                data = f.read()
            self.assertEqual(data[:4], b"GCMP")
            self.assertEqual(struct.unpack(">HH", data[4:8]), (320, 240))
            self.assertEqual(len(data), 32 + 320 * 240 // 2)
            px = mohaa_menu.cmpr_decode(data[32:], 320, 240)[10, 300]   # x=620 on the sheet: main_b
            self.assertLess(np.abs(px.astype(int) - BLUE).max(), 12)

    def test_room_menu(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_pak(os.path.join(tmp, "pak0.pk3"))
            menu = mohaa_menu.room_menu([tmp])
            self.assertEqual(menu["sign"], (48, 36, 172, 56))
            # left to right: the options radio (x 0), then the map (x 100); the developer button is left out
            self.assertEqual([(a, r) for a, r, _, _ in menu["spots"]],
                             [("options", (0, 172, 128, 128)), ("newgame", (100, 100, 64, 32))])
            lit = menu["spots"][0][2]
            self.assertEqual((lit.size, lit.getpixel((5, 5))), ((128, 128), WHITE))
            self.assertEqual(menu["spots"][0][3].getpixel((5, 5)), BLUE)
            self.assertIsNone(menu["spots"][1][3])                     # no newgame_sign shader in the paks
            self.assertEqual([(a, r) for a, r, _, _ in menu["buttons"]], [("quit", (536, 448, 96, 24))])
            self.assertEqual(menu["buttons"][0][3].getpixel((5, 5)), GREEN)
            self.assertEqual([n for n, _, _ in menu["sounds"]], ["out"])
            out = os.path.join(tmp, "out")
            written = mohaa_menu.write_room_menu(menu, out)
            with open(os.path.join(out, "resource", "gc_menu", "mohaa_main.txt")) as f:
                lines = [l.split() for l in f if not l.startswith("//")]
            self.assertEqual(lines, [
                ["screen", "640", "480"], ["sign", "48", "36", "172", "56"],
                ["spot", "options", "0", "172", "128", "128", "resource/gc_menu/mohaa/spot0_options.tga",
                 "resource/gc_menu/mohaa/sign0_options.tga"],
                ["spot", "newgame", "100", "100", "64", "32", "resource/gc_menu/mohaa/spot1_newgame.tga", "-"],
                ["button", "quit", "536", "448", "96", "24", "resource/gc_menu/mohaa/quit.tga",
                 "resource/gc_menu/mohaa/quit_h.tga"],
                ["sound", "out", "sound/mohaa/menu/back.wav"]])
            for p in written:
                self.assertTrue(os.path.isfile(p), p)
            with wave.open(os.path.join(out, "sound", "mohaa", "menu", "back.wav")) as w:
                self.assertEqual((w.getnchannels(), w.getframerate()), (1, 22050))

    def test_sd_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            game, sd = os.path.join(tmp, "MOHAA"), os.path.join(tmp, "sd")
            os.makedirs(os.path.join(game, "main"))
            make_pak(os.path.join(game, "main", "pak0.pk3"))
            with redirect_stdout(io.StringIO()) as log:
                rc = mohaa_sd.main(["--mohaa", game, "--sd", sd, "--stages", "menu"])
            self.assertEqual(rc, 0, log.getvalue())
            self.assertTrue(os.path.isfile(os.path.join(sd, "xash3d", "mohaa", "resource", "gc_menu", "bg_1_1.cmp")))
            self.assertTrue(os.path.isfile(os.path.join(sd, "xash3d", "mohaa", "resource", "gc_menu", "mohaa_main.txt")))
            self.assertIn("== menu: 18 files", log.getvalue())

    def test_options_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_page_pak(os.path.join(tmp, "pak1.pk3"))
            menu = mohaa_menu.page_menu([tmp], "options")
            self.assertEqual(menu["sheet"].size, (640, 480))     # "640 480" is the size, not inclusive extents
            self.assertEqual(menu["sheet"].getpixel((10, 10)), (100, 50, 0))
            self.assertEqual(menu["sign"], (98, 52, 128, 32))
            # top to bottom: advanced, then video; Back is a picture button
            self.assertEqual([(a, r) for a, r, _, _ in menu["spots"]],
                             [("advanced", (200, 40, 100, 50)), ("video", (400, 300, 100, 50))])
            glow = menu["spots"][1][2].getpixel((5, 5))           # white added at 0.2 over (100, 50, 0)
            self.assertEqual(glow, (151, 101, 51))
            self.assertEqual(menu["spots"][0][2].getpixel((5, 5)), WHITE)   # plain hover art drawn over
            self.assertEqual(menu["spots"][1][3].getpixel((5, 5)), GREEN)
            self.assertIsNone(menu["spots"][0][3])
            self.assertEqual([(a, r) for a, r, _, _ in menu["buttons"]], [("back", (8, 448, 96, 24))])
            out = os.path.join(tmp, "out")
            written = mohaa_menu.write_page(menu, out, "options")
            for p in written:
                self.assertTrue(os.path.isfile(p), p)
            gc = os.path.join(out, "resource", "gc_menu")
            with open(os.path.join(gc, "mohaa_options.txt")) as f:
                lines = [l.split() for l in f if not l.startswith("//")]
            self.assertEqual(lines[:3], [
                ["screen", "640", "480"],
                ["background"] + ["resource/gc_menu/bg_options_%d_%d.tga" % (r, c) for r in range(2) for c in range(2)],
                ["sign", "98", "52", "128", "32"]])
            self.assertEqual(lines[3][:6], ["spot", "advanced", "200", "40", "100", "50"])
            self.assertEqual(lines[-1], ["button", "back", "8", "448", "96", "24",
                                         "resource/gc_menu/mohaa/options/back.tga",
                                         "resource/gc_menu/mohaa/options/back_h.tga"])
            with open(os.path.join(gc, "bg_options_1_1.cmp"), "rb") as f:
                data = f.read()
            self.assertEqual((data[:4], len(data)), (b"GCMP", 32 + 320 * 240 // 2))
            self.assertEqual(Image.open(os.path.join(gc, "bg_options_0_0.tga")).size, (64, 48))

    def test_gametype_page_reads_its_include(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_page_pak(os.path.join(tmp, "pak1.pk3"))
            menu = mohaa_menu.page_menu([tmp], "gametype")
            self.assertEqual(menu["sheet"].getpixel((300, 20)), BLUE)   # serverback.inc's picture
            self.assertEqual(menu["sheet"].getpixel((100, 400)), BLUE)  # its one-line resource too
            self.assertEqual([a for a, _, _, _ in menu["spots"]], ["ffa", "team"])
            self.assertEqual(menu["buttons"], [])

    def test_server_form(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_page_pak(os.path.join(tmp, "pak1.pk3"))
            menu = mohaa_menu.page_menu([tmp], "server")
            self.assertEqual(menu["sheet"].getpixel((20, 20)), BLUE)             # serverback.inc around it
            self.assertEqual(menu["sheet"].getpixel((300, 200)), (230, 220, 190))  # the form, no voodoo tile
            self.assertEqual([a for a, _, _, _ in menu["spots"]], ["map", "start"])
            lit = menu["spots"][0][2]
            self.assertEqual(lit.getpixel((5, 5)), (255, 255, 241))              # paper + white at 0.2, added
            self.assertEqual([a for a, _, _, _ in menu["buttons"]], ["back"])
            self.assertEqual(menu["fields"], [("map", (88, 106, 208, 24), (0, 0, 0)),
                                              ("hostname", (260, 314, 292, 28), (0, 0, 0)),
                                              ("maxplayers", (498, 92, 60, 28), (0, 0, 0))])
            out = os.path.join(tmp, "out")
            mohaa_menu.write_page(menu, out, "server")
            with open(os.path.join(out, "resource", "gc_menu", "mohaa_server.txt")) as f:
                text = f.read()
            self.assertIn("field hostname 260 314 292 28 0 0 0\n", text)
            self.assertIn("spot start 264 416 112 16 ", text)
            self.assertIn("button back 8 440 96 24 ", text)

    def test_no_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_pak(os.path.join(tmp, "pak0.pk3"))
            self.assertIsNone(mohaa_menu.page_menu([tmp], "options"))


if __name__ == "__main__":
    unittest.main()
