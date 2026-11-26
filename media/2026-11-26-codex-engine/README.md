# MOHAA GameCube: Codex engine port, Dolphin probes (2026-11-26)

Dolphin runs on ceres, 2026-11-26. Stills and clips are in this folder; full Dolphin logs are kept on ceres at ~/Desktop/mohaa-media/2026-11-26-codex-engine/.

- Engine: xash3d-gc branch claude/mohaa-codex-engine on master 8bbbc347d.
  - Each run used the DOL built from 6645a2f54 (19d91de90 Codex port, 19721a168 card workarea, 6645a2f54 libogc2 unwind).
  - The m1l2a run also had the map-arena script scratch (now commit d4d63431c).
  - Smoke-disc sidecar staging: 4e5e4a636 (disc builder only).
  - Clone: /run/media/tim/Stream/claude-mohaa-20261126/mohaa-gc/dod-gc/.deps/xash3d-gc.
- SDK: hlsdk-portable 0e324dac (the pinned commit; no SDK hook needed).
- Game: mohaa-gc branch claude/project-thread-synr24 at 35e3002, on main 8ec19ea.
  - The mohaa-gc code in these DOLs was this change, applied but not yet committed when they were built.
- Stack: classic libogc. On libogc2, m1l1 ran out of MEM1 while loading the BSP.
- Data: tools/mohaa_sd.py from the retail install (Paks only, so no music), with DoD's delta.lst added.
- Captures: m1l2a and m1l2b ran under Xvfb (llvmpipe). The m1l1 run used the live display, and two frames that caught the desktop were deleted.

## m1l1: retail New Game
- m1l1.scr now runs under the single-player rules.
- Results:
  - 643 path nodes loaded.
  - Tags loaded: 5 models, 65 animation lengths.
  - The trucks and the German private were precached from m1l1.models.
  - All 6 waiting soldiers came in.
  - The player's view rides the intro path.
- Still open:
  - The 2nd-ranger truck animations ("truck_idle_captain" and others) fail on the actors.
  - The trucks are not visible from the rider's camera.
  - The view stops at a building after about 50 s.

## m1l2b: New Game straight into m1l2b
- The map loads and renders.
- The HUD now uses Codex's GC_DrawMohaaHud layout: health gauge, ammo arms with the clip count, crosshair and compass.
- Its mohaa_actor "result=-1" lines are expected. The placeholder removes itself once its grunt spawns or joins the waiting list.

## m1l2a: door USE
- The map loads and renders.
- The level script did not start: "script compile error: maps/m1l2a.scr:0: out of memory". There is no 32 KiB gap left in the map arena on current master.
- The door hint was not reached.
