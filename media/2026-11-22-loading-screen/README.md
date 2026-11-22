# MOHAA loading screen in Dolphin, 2026-11-22

The build uses xash3d-gc master f4a7635bcc (#506 loading screen, #507 mohaa game folder) and mohaa-gc main fa97ff1 (#92 loading converter, #93 intro/mohaa game), with hlsdk 0e324da. The DOL is mohaagc.dol with gamedir mohaa, over dod/ and valve/.
The `delta.lst` fix is committed in `dod-gc/scripts/build-lean-iso.sh` (MOHAA commit `6540177`): the lean DoD copy is added to `mohaa/` so the bootstrap pk3 can load it. `local-fix-delta-lst.patch` is the original experiment kept for reference. Without the fix, map loads failed with "Delta_InitFields: couldn't load file delta.lst" (play1-delta-lst-crash log).

Test disc content (Dolphin has no SD adapter, so the SD tree goes on the disc via DODGC_MOHAA_TEST_DIR) came from mohaa_sd.py on main: the menu, loading (34 .cmp) and m1l1 stages (map, mcol, nodes, scripts, sounds, world bake, props). No intro movie was found in retail/.
I added maps.lst listing m1l1 and dod_avalanche.

## Result

| What | Seen |
| --- | --- |
| previews/ | mohaa_loading.py renders all 34 screens correctly. default.png matches the retail screenshot. |
| m1l1 load (01-*.mp4, stills 02-04) | **The full-screen MOHAA loading screen did not show.** Instead, the menu background shows with the old "MEDAL OF HONOR: ALLIED" plaque, and its orange bar does not move. After about 8 s gameplay starts. |
| log | There are no "loading screen" or "loading overlay on" lines. This route goes Create Server → "play start begin m1l1" → "pre-spawn loading status ready". GC_LoadingOverlayBegin never runs, so GC_LoadScreenDrawFull is never reached. |

The new code only hooks the transition-hold path (status NEW GAME, PREPARING MAP, and so on). The mohaa menu's New Game uses the play-start / pre-spawn status path, which draws the HL1 plaque. Run B (fallback) was not recorded separately, because run A already shows the plaque.

## Engine fix #508 (0a7892b / f6f52bc), later runs

| File | Engine | Disc | Seen |
| --- | --- | --- | --- |
| 03-runB-fallback-plaque-contact.png, B1 log | 0a7892b | no default.cmp / m1l1.cmp | The fallback "MEDAL OF HONOR: ALLIED" plaque shows, which is correct. It then sticks after MAP_READY with no presents, but that is the disc's fault (see below). |
| 04-*.mp4, A4 log | 0a7892b | built without `--map` | The m1l1 briefing screen and red bar show, then a grey/checker test pattern, and "world render ready" never comes. |
| B2 log | master f4a7635 | same disc as B1 | **Stuck the same way**, so the engine fix didn't cause this. |
| 05-*.mp4, run05-unrevert-stills/ | master 25629af + revert of #510 (= #508) | built with `--map dod_avalanche` (stages listenserver.cfg) | **Works.** The m1l1 briefing screen is up about 3 s with the red bar growing (about 30% to 40%). Then a grey frame for about 4 s, then gameplay with the HUD. The log shows "loading screen m1l1 bar 194,456 252x8", "newgame world render ready" and normal presents. |

Root cause of the "no gameplay" runs: discs built with build-lean-iso.sh without `--map` have no listenserver.cfg ("couldn't exec listenserver.cfg"), and the world render never starts. That isn't the loading screen.
Cosmetic issues left: the bar starts at about 30% and the load is short, and a grey screen shows for about 4 s between the loading screen and the first world frame.

## Polish (saved engine diff based on master 52c93fd, run 14)

The loading screen now stays up from New game to the first world frame. Log: "loading screen off (first world frame) after 7.65s". There's no grey screen and no old plaque in between, only the engine's usual dark first frames while the world fades in. Bugs found along the way:
- The XFB on screen was the one `which_fb` pointed at, so holding presents with a CopyDisp to xfb[which_fb] painted grey over the screen. The fix: copy to the other XFB.
- "CLIENT INIT" took the status-panel path, which flips the old plaque over the screen. The fix: keep the screen.
- After the map load, the world renderer leaves GX state (indirect stages, fog, swap table and so on), and the bar quads stopped showing. The fix: the screen's pipe resets that state.

What's left on the bar: it shows NEW GAME 0.05, PREPARING 0.15 and LOADING BSP 0.3, creeping to about 0.44. Then the client load runs for about 4 s with no status or present calls, so the bar can't move. The 0.75 (CLIENT INIT) and 0.9 (in game) raises are in the code but don't reach the screen in time.
Tim's disc (07-*.mp4): master 52c93fd + mohaa-gc 014e52d. The m1l1 map, world bake and props come from the fa97ff1 conversion, because after #95 m1l1.bsp is 3.1 MB and the game runs out of MEM1 on load (PANIC).
