# MOHAA m1l2a fresh runtime capture — 2026-11-22

This capture is from a fresh temporary build at about 12:24 PM PT, after the current HUD-font and GameCube view-cvar changes. It replaces the older morning capture as the latest runtime evidence.

## Build pair

- MOHAA source: `3d55812521` (`/home/tim/Desktop/mohaa-gc`, local `main`).
- Xash3D-GC: `67d0e9a27f` (`codex/mohaa-local-diagnostics`). Its `3rdparty/MultiEmulator` dependency was copied into the isolated build tree from a local snapshot whose HEAD and header blob match the pinned commit `e369abc23c49310b0f5e58f12fef6f46563b0d21` / `7811e34bb6b34dd07cba9936d23ccd51209373bb`.
- HLSDK: local commit `adb14538` (`Guard skipped GameCube view cvars`), built with the current DoD game code. The GameCube route intentionally skips `V_Init()` to limit MEM1 use; view functions now use MOHAA/GoldSrc defaults when those cvar pointers were never registered.
- Engine and game DLL use matching `XASH_GC_PM_MAX_PHYSENTS=256` and `XASH_GC_PM_MAX_MOVEENTS=32`.
- Toolchain: devkitPPC 16.1.0, libogc stack. DOL and ISO were written under `/tmp/mohaa-dodgc-paired-out-20261122/`, not over existing artifacts.

DOL SHA-256: `e5fc0c5eb6429f9f38a1153f74bac7c1a5108597a6418b2c3f1b2561dd6420c5`
ISO SHA-256: `553ecb06dfb84fa28c00c3cf85715e951fad07dae080ad1d0d43d7451d97911e`

## Dolphin result

The 60-second `m1l2a` new-game probe reached `map loaded m1l2a` and `newgame world render ready`. No panic, fatal marker, or player-move layout mismatch appears in the captured log. The HUD font log confirms the 256×64 `CREDITSFONT` sheet is held in ARAM. The final frame overlay reported 57.51 FPS.

- Screenshot: [`shots/20261122-122448-mohaa-latest-safe-view-cvars-20261122/final.png`](shots/20261122-122448-mohaa-latest-safe-view-cvars-20261122/final.png)
- Guest log: [`shots/20261122-122448-mohaa-latest-safe-view-cvars-20261122/dolphin.log`](shots/20261122-122448-mohaa-latest-safe-view-cvars-20261122/dolphin.log)
- Probe note: [`notes/20261122-122448-mohaa-latest-safe-view-cvars-20261122.md`](notes/20261122-122448-mohaa-latest-safe-view-cvars-20261122.md)

Dolphin used OpenGL, MMU and accurate CPU cache enabled, progressive 320×240 guest video, and a 60-second cap. Audio capture was unavailable because the local PulseAudio connection was refused, so this run produced a screenshot and log, not a video.

## Still open

The map now renders and remains running, but this is not a retail-fidelity claim. The captured view still has missing/white map surfaces and no visible health/ammo HUD, even though the font is loaded in ARAM. The held weapon appearance also needs review. These are the next visual/runtime gaps to investigate.
