"""Tests for tools/mohaa_sd.py on a made-up install and made-up CDs (no retail data)."""
import io
import os
import shutil
import stat
import sys
import tempfile
import unittest
import wave
import zipfile
from contextlib import redirect_stdout
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import mohaa_sd  # noqa: E402

MUS = "path sound/music\nnormal sting.wav\n!normal loop\n"
SCR = "main:\n\tprintln \"hi\"\nend\n"


def pak(path):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("music/t1.mus", MUS)
        z.writestr("maps/t1.scr", SCR)


def wav(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(bytes(4 * 4410))


def run(argv):
    out = io.StringIO()
    with redirect_stdout(out):
        rc = mohaa_sd.main(argv)
    return rc, out.getvalue()


class MohaaSdTest(unittest.TestCase):
    def test_install_to_sd_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            game, sd = os.path.join(tmp, "MOHAA"), os.path.join(tmp, "sd")
            os.makedirs(os.path.join(game, "Main"))   # Windows installs capitalise it
            pak(os.path.join(game, "Main", "pak0.pk3"))
            wav(os.path.join(game, "Main", "sound", "music", "sting.wav"))
            self.assertEqual(mohaa_sd.find_main(game), os.path.join(game, "Main"))
            stages = "music,scripts" if shutil.which("ffmpeg") else "scripts"
            rc, log = run(["--mohaa", game, "--sd", sd, "--maps", "t1", "--stages", stages, "--list"])
            self.assertEqual(rc, 0)
            root = os.path.join(sd, "xash3d", "mohaa")
            self.assertTrue(os.path.isfile(os.path.join(root, "maps", "t1.scr")))
            if shutil.which("ffmpeg"):
                self.assertTrue(os.path.isfile(os.path.join(root, "music", "t1.mood")))
                with wave.open(os.path.join(root, "sound", "mohaa", "music", "sting.wav")) as w:
                    self.assertEqual((w.getnchannels(), w.getframerate()), (1, 22050))
            self.assertIn("== scripts:", log)

    def test_cds_are_unpacked_once_with_unshield(self):
        with tempfile.TemporaryDirectory() as tmp:
            cd1, cd2, sd, bin_ = (os.path.join(tmp, n) for n in ("cd1", "cd2", "sd", "bin"))
            for d in (cd1, cd2, bin_):
                os.makedirs(d)
            for name, d in (("DATA1.HDR", cd1), ("DATA1.CAB", cd1), ("DATA2.CAB", cd1), ("DATA3.CAB", cd2)):
                open(os.path.join(d, name), "w").close()
            # a stand-in unshield: writes the groups as the real one does (one flat folder per group)
            src = os.path.join(tmp, "payload")
            os.makedirs(src)
            pak(os.path.join(src, "pak0.pk3"))
            wav(os.path.join(src, "sting.wav"))
            fake = os.path.join(bin_, "unshield")
            with open(fake, "w") as f:
                f.write("#!/bin/sh\n"
                        "while [ $# -gt 0 ]; do case $1 in -d) shift; out=$1;; *.CAB) cab=$1;; esac; shift; done\n"
                        "test -e \"$(dirname \"$cab\")/DATA3.CAB\" || exit 3\n"
                        "mkdir -p \"$out/Music Files\" \"$out/Data Files Complete\" \"$out/Help Files EN-US\"\n"
                        "cp '%s' \"$out/Music Files/\"\n"
                        "cp '%s' \"$out/Data Files Complete/PAK0.PK3\"\n"
                        "echo x > \"$out/Help Files EN-US/readme.txt\"\n"
                        "echo ran >> '%s'\n" % (os.path.join(src, "sting.wav"), os.path.join(src, "pak0.pk3"),
                                               os.path.join(tmp, "runs")))
            os.chmod(fake, os.stat(fake).st_mode | stat.S_IEXEC)
            with mock.patch.dict(os.environ, {"PATH": bin_ + os.pathsep + os.environ["PATH"]}):
                for _ in range(2):
                    rc, _log = run(["--cd", cd1, cd2, "--sd", sd, "--maps", "t1", "--stages", "scripts"])
                    self.assertEqual(rc, 0)
            main = os.path.join(sd, ".mohaa-work", "cd", "main")
            self.assertTrue(os.path.isfile(os.path.join(main, "pak0.pk3")))
            self.assertTrue(os.path.isfile(os.path.join(main, "sound", "music", "sting.wav")))
            self.assertFalse(os.path.exists(os.path.join(main, "readme.txt")))
            with open(os.path.join(tmp, "runs")) as f:
                self.assertEqual(f.read().count("ran"), 1)   # the second run reuses the unpacked set
            self.assertTrue(os.path.isfile(os.path.join(sd, "xash3d", "mohaa", "maps", "t1.scr")))

    def test_a_failing_stage_does_not_stop_the_rest(self):
        with tempfile.TemporaryDirectory() as tmp:
            game, sd = os.path.join(tmp, "MOHAA"), os.path.join(tmp, "sd")
            os.makedirs(os.path.join(game, "main"))
            pak(os.path.join(game, "main", "pak0.pk3"))   # no ubersound aliases: the sounds stage fails
            rc, log = run(["--mohaa", game, "--sd", sd, "--maps", "t1", "--stages", "sounds,scripts"])
            self.assertEqual(rc, 1)
            self.assertIn("== sounds: FAILED", log)
            self.assertIn("failed stages: sounds", log)
            self.assertTrue(os.path.isfile(os.path.join(sd, "xash3d", "mohaa", "maps", "t1.scr")))

    def test_maps_and_bakes(self):
        """maps -> worlddl -> props with stand-ins for SDHLT, the xash3d-gc bakers and the Python converters."""
        with tempfile.TemporaryDirectory() as tmp:
            game, sd, bin_, xg = (os.path.join(tmp, n) for n in ("MOHAA", "sd", "sdhlt", "xash3d-gc"))
            os.makedirs(os.path.join(game, "main"))
            with zipfile.ZipFile(os.path.join(game, "main", "pak0.pk3"), "w") as z:
                z.writestr("maps/t1.bsp", b"IBSP-t1")
                z.writestr("maps/t2.bsp", b"IBSP-t2")
                z.writestr("maps/t1.scr", SCR)
            calls = []

            def tool(name, body):
                path = os.path.join(bin_, name)
                with open(path, "w") as f:
                    f.write("#!/bin/sh\n# -hull2alias\necho %s \"$@\" >> '%s'\n%s\n" % (name, os.path.join(tmp, "calls"), body))
                os.chmod(path, 0o755)

            os.makedirs(bin_)
            for name in ("sdHLCSG", "sdHLVIS"):
                tool(name, "")
            tool("sdHLBSP", 'for m; do :; done; echo BSP30 > "$m.bsp"')
            os.makedirs(os.path.join(xg, "scripts"))
            with open(os.path.join(xg, "scripts", "bake_worlddl_goldsrc.py"), "w") as f:
                f.write("import sys\no = sys.argv[sys.argv.index('--out') + 1]\n"
                        "open(o, 'w').write('wd'); open(o[:-4] + '_lf.gcd', 'w').write('lf')\n")
            with open(os.path.join(xg, "scripts", "bake_props_goldsrc.py"), "w") as f:
                f.write("import os, sys\na = sys.argv\nm = os.path.basename(a[a.index('--map') + 1])[:-4]\n"
                        "o = a[a.index('--out') + 1]\nassert open(a[a.index('--mprop') + 1]).read() == 'mprop'\n"
                        "open(os.path.join(o, 'gp_%s.gcp' % m), 'w').write('gp')\n"
                        "open(os.path.join(o, 'pt_%s.gct' % m), 'w').write('pt')\n")

            def convert(argv):
                calls.append(("convert", argv))
                self.assertEqual(open(argv[0], "rb").read(), b"IBSP-t1")
                self.assertIn("--scripts", argv)
                self.assertIn("--textures", argv)   # real textures from the same sources
                out = argv[argv.index("-o") + 1][:-4]
                for ext, text in ((".map", "{}"), (".mcol", "MCOL"), (".nodes", "n"), (".props", "p")):
                    open(out + ext, "w").write(text)
                return 0

            def light(argv):
                calls.append(("light", argv))
                self.assertEqual(open(argv[1]).read(), "BSP30\n")
                shutil.copy(argv[1], argv[argv.index("-o") + 1])
                return 0

            def pack(argv):
                calls.append(("pack", argv))
                open(argv[argv.index("-o") + 1], "w").write("mprop")
                return 0

            import bsp19_lightmaps
            import bsp19_to_map
            import props_models
            with mock.patch.object(bsp19_to_map, "main", convert), mock.patch.object(bsp19_lightmaps, "main", light), \
                    mock.patch.object(props_models, "main", pack):
                rc, log = run(["--mohaa", game, "--sd", sd, "--maps", "t1", "--stages", "props,maps,worlddl",
                               "--sdhlt", bin_, "--xash3d-gc", xg, "--list"])
            self.assertEqual(rc, 0, log)
            self.assertLess(log.index("== maps"), log.index("== worlddl"))   # pipeline order, whatever was asked
            self.assertLess(log.index("== worlddl"), log.index("== props"))
            root = os.path.join(sd, "xash3d", "mohaa")
            for rel in ("maps/t1.bsp", "maps/t1.mcol", "maps/t1.nodes", "media/wd_t1.gcd", "media/wd_t1_lf.gcd",
                        "media/gp_t1.gcp", "media/pt_t1.gct"):
                self.assertTrue(os.path.isfile(os.path.join(root, rel)), rel)
            self.assertFalse(os.path.exists(os.path.join(root, "maps", "t2.bsp")))   # only the map asked for
            sdhlt = open(os.path.join(tmp, "calls")).read().splitlines()
            self.assertEqual([c.split()[0] for c in sdhlt], ["sdHLCSG", "sdHLBSP", "sdHLVIS"])
            self.assertIn("-wadinclude t1.wad", sdhlt[0])
            self.assertIn("-hull2alias", sdhlt[1])
            self.assertEqual([c[0] for c in calls], ["convert", "light", "pack"])

    def test_stages_without_their_tools_are_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            game, sd = os.path.join(tmp, "MOHAA"), os.path.join(tmp, "sd")
            os.makedirs(os.path.join(game, "main"))
            pak(os.path.join(game, "main", "pak0.pk3"))
            with mock.patch.dict(os.environ, {"PATH": os.path.join(tmp, "nothing")}), \
                    mock.patch.object(mohaa_sd, "STAGES", {k: mohaa_sd.STAGES[k] for k in ("maps", "worlddl", "scripts")}):
                rc, log = run(["--mohaa", game, "--sd", sd, "--maps", "t1", "--tools-dir", os.path.join(tmp, "t")])
            self.assertEqual(rc, 0, log)
            self.assertIn("skipping maps: needs the patched SDHLT (building it needs bash", log)
            self.assertIn("skipping worlddl: needs --xash3d-gc", log)
            self.assertIn("== scripts:", log)

    def test_gameinfo(self):
        with tempfile.TemporaryDirectory() as tmp:
            game, sd = os.path.join(tmp, "MOHAA"), os.path.join(tmp, "sd")
            os.makedirs(os.path.join(game, "main"))
            pak(os.path.join(game, "main", "pak0.pk3"))
            rc, log = run(["--mohaa", game, "--sd", sd, "--maps", "t1", "--stages", "scripts"])
            self.assertEqual(rc, 0, log)
            root = os.path.join(sd, "xash3d", "mohaa")
            info = open(os.path.join(root, "gameinfo.txt")).read()
            self.assertIn('gamedir\t\t"mohaa"', info)
            self.assertIn('fallback_dir\t"dod"', info)
            self.assertIn('fallback_dir "dod"', open(os.path.join(root, "liblist.gam")).read())
            with open(os.path.join(root, "liblist.gam"), "w") as f:
                f.write('game "mine"\n')   # someone else's: left alone
            run(["--mohaa", game, "--sd", sd, "--maps", "t1", "--stages", "scripts"])
            self.assertEqual(open(os.path.join(root, "liblist.gam")).read(), 'game "mine"\n')
            run(["--mohaa", game, "--sd", sd, "--gamedir", "dod", "--maps", "t1", "--stages", "scripts"])
            self.assertFalse(os.path.exists(os.path.join(sd, "xash3d", "dod", "liblist.gam")))   # never over DoD's

    def test_sdhlt_is_built_once_and_stock_sdhlt_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            stock, tools = os.path.join(tmp, "stock"), os.path.join(tmp, "tools")
            os.makedirs(stock)
            for name in mohaa_sd.SDHLT:   # an unpatched SDHLT on PATH: no -hull2alias
                with open(os.path.join(stock, name), "w") as f:
                    f.write("#!/bin/sh\n")
                os.chmod(os.path.join(stock, name), 0o755)
            build = os.path.join(tmp, "build.sh")
            with open(build, "w") as f:   # stands in for third_party/sdhlt-bsp30ext/build.sh <workdir>
                f.write('echo built >> "%s"\nmkdir -p "$1/SDHLT/tools"\nfor t in sdHLCSG sdHLBSP sdHLVIS; do\n'
                        '  printf "#!/bin/sh\\n# -hull2alias\\n" > "$1/SDHLT/tools/$t"; chmod +x "$1/SDHLT/tools/$t"\n'
                        'done\n' % os.path.join(tmp, "builds"))
            built = os.path.join(tools, "sdhlt", "SDHLT", "tools")
            try:
                mohaa_sd.CONFIG.update(sdhlt=None, tools_dir=tools, build_sdhlt=True)
                with mock.patch.dict(os.environ, {"PATH": stock + os.pathsep + os.environ["PATH"]}), \
                        mock.patch.object(mohaa_sd, "SDHLT_BUILD", build), \
                        mock.patch.object(mohaa_sd, "sdhlt_buildable", lambda: None), redirect_stdout(io.StringIO()):
                    mohaa_sd._found.clear()
                    self.assertIsNone(mohaa_sd.sdhlt_dir())   # the stock one on PATH is refused
                    for _ in range(2):
                        mohaa_sd._found.clear()
                        self.assertEqual(mohaa_sd.ensure_sdhlt(), built)
                    mohaa_sd.CONFIG.update(sdhlt=stock)
                    mohaa_sd._found.clear()
                    with self.assertRaises(SystemExit):   # --sdhlt at a stock build is an error, not a rebuild
                        mohaa_sd.ensure_sdhlt()
            finally:
                mohaa_sd.CONFIG.update(sdhlt=None, tools_dir=None)
                mohaa_sd._found.clear()
            with open(os.path.join(tmp, "builds")) as f:
                self.assertEqual(f.read().count("built"), 1)   # built once, then reused

    def test_map_flags(self):
        flags = mohaa_sd.map_flags()
        self.assertIn("--detail-walls", flags["m2l1"])
        self.assertNotIn("#", " ".join(sum(flags.values(), [])))

    def test_needs_a_source(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit):
                with mock.patch("sys.stderr", io.StringIO()):
                    mohaa_sd.main(["--sd", tmp])


if __name__ == "__main__":
    unittest.main()
