# m1l1 ride, m1l2a script, m1l2b: Dolphin runs (2026-11-26)

These runs were captured headless (Xvfb, llvmpipe) on ceres. Full Dolphin logs are on ceres at ~/Desktop/mohaa-media/2026-11-26-ride-m1l2a/.

- **Engine:** xash3d-gc `claude/mohaa-ride` 9b7e336c9, on master 85fdd7925. It stages the per-map media packs and keeps gcworldrender on menu New Game smoke discs.
- **Game:** mohaa-gc `claude/mohaa-m1l1-ride` 6f8e6e9, on main 3fe4e7a.
- **SDK:** hlsdk 0e324dac. Classic libogc.

## m1l1 (retail New Game)
- Terrain, palms, flags and buildings draw, now that gp_m1l1 is staged.
- The Opel and the GMC are sent and drawn. The GMC's skin isn't uploaded yet ("studio skin upload skipped"), so it shows untextured.
- Soldiers draw.
- The ride no longer stops at the checkpoint: the guard's blocked walk times out. The player gets weapons at the end.

## m1l2a
- maps/m1l2a.scr used to fail with "out of memory" at worldspawn. It now compiles after the map loads (try 1), and the mission runs.
- The door-hint check is still open: on this menu New Game route the TAS replay doesn't move the player, and USE only reaches the engine's trigger hook on -gcnewgame boots.

## m1l2b
- With the light grid and world render on, the scene is a normally lit night street, not the dark frame from 2026-11-23.
- A hint shows "NILNOT BOUNDNIL": a script string that isn't bound yet.
