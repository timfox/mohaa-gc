# MOHAA m1l2b listenserver runtime — 2026-11-22

Two isolated runs were captured: the initial staged retail folder revealed 12 missing referenced WAVs, then a rebuilt disc included the complete 29-sample m1l2b sound set.

An isolated 60-second Dolphin listenserver run used a test disc assembled from the local staged retail data. This route runs the MOHAA game DLL and script VM, unlike the earlier map-render-only capture. The disc was built with `--skip-stage --intro-only --skip-startup-vids --listen m1l2b --world-render` and `DODGC_MOHAA_TEST_DIR=/home/tim/Desktop/mohaa-gc/retail/mohaa-full-stage-20261122/xash3d/mohaa`. No release disc or SD card was changed.

- Engine disc builder: local Xash3D-GC checkout `12dd85d9029272ed91867b2b3382c7340f57d207`.
- Game DOL SHA-256: `81986b991d5ae251a80c69a23003419cb633221ba2ec9eba1c47794cf0c2c019`.
- Test ISO SHA-256: `c3e18458728c3fbc47cc653fd03d765766fce55aa98f5d0412cf2f61c04440a4` (1,204,623,360 bytes).
- Probe: 60 seconds, 640×480, isolated Dolphin profile; full [build log](build.log) and [OSReport log](dolphin.log).

The OSReport confirms `maps/m1l2b.scr` and `maps/m1l2b.snd` were both found and loaded from `gcdisc:/xash3d/mohaa/`. It then reports `mohaa: running maps/m1l2b.scr` with 384 KiB of script memory in the map arena, `MAP_READY m1l2b`, `solo listenserver active map=m1l2b`, and `newgame world render ready`. The first-person screenshot shows the Garand and HUD in the map.

![m1l2b listenserver with Garand](/home/tim/Desktop/mohaa-gc/media/2026-11-22-m1l2b-runtime/listen-sfx-20261122/m1l2b-listen.png)

The staged retail folder used for this disc predates the complete loose SFX pass: it has the `.snd` table and 17 referenced WAVs but lacks three mechanics and nine dialogue WAVs. The separate current converter run documents all 29 converted samples in [the SFX stage report](/home/tim/Desktop/mohaa-gc/media/2026-11-22-sfx-stage/README.md). This gameplay capture proves the VM and table file load. It does not demonstrate playback of scripted MOHAA aliases or all 29 samples; a complete-content listen capture remains open. The scene is very dark in this spawn view, so this screenshot does not establish visual parity with retail.


## Complete native SFX disc

The second test disc kept the same game DOL and map route. Twelve missing WAVs (three mechanics, nine dialogue) were selected from the local retail cabinets and converted with `tools/mohaa_sd.py --maps m1l2b --stages sounds --sound-source /tmp/mohaa-m1l2b-listen-20261122/loose/main`. The [stage log](complete-sfx-stage.log) reports 29 samples converted, zero skipped, zero unresolved aliases. The converted WAVs and updated `.snd` table were copied into the isolated disc source before packaging; existing retail stage files were not modified.

- Complete test ISO SHA-256: `a6ac813ccd681353a6e88d321e25e8752eb733dcd3dd4af250b021012195ecd4` (1,206,648,832 bytes).
- An [ISO9660 directory audit](complete-iso-audit.txt) verified all 29 unique WAV paths named by `maps/m1l2b.snd` are present under `xash3d/mohaa/sound/`.
- The 60-second [Dolphin log](complete-dolphin.log) again shows `maps/m1l2b.snd` opened, `mohaa: running maps/m1l2b.scr`, `MAP_READY m1l2b`, and `newgame world render ready`. Build record: [complete-build.log](complete-build.log).
- The renderer displayed the Garand and HUD in the dark spawn view.

![m1l2b with complete native SFX staged](/home/tim/Desktop/mohaa-gc/media/2026-11-22-m1l2b-runtime/listen-sfx-20261122/m1l2b-complete-sfx.png)

The log does not identify a scripted MOHAA alias playing during this idle capture. The complete disc proves the native samples are packaged and the game VM loads the sound table; audible playback and alias timing still need an exercised gameplay event. A separate DoD fallback warning for `common/wpn_denyselect.wav` appears in the log and is outside the 29 MOHAA table references.
