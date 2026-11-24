# MOHAA skybox status — 2026-11-23 (updated)

The m1l1 runtime now resolves and draws its retail skybox. The retail BSP shader `textures/sky/africanight` maps to the `env/mohnight1` cubemap. `tools/mohaa_sky.py` converts all six faces to 128×128 GameCube CMPR (`8,192` bytes each), and the maps stage writes `mohnight1` as the compiled BSP's `skyname`.

## Runtime evidence

The permanent campaign stage now contains a fresh m1l1 map build from the patched SDHLT toolchain. It writes the `mohnight1` BSP skyname and all six retail-derived CMPR faces. The staged BSP is 1,959,876 bytes (SHA-256 `ee57d44b48476f54a9ca82e821cc8604bab79dd4f290fcc4f605e8b01a6ab239`); the six faces are each 8,192 bytes.

- Runtime ISO: `/tmp/mohaa-m1l1-sky-final/out/m1l1-final-skybox.iso` (1,750,908,928 bytes; SHA-256 `b88ea68032c066f6b34c5e68392768f00385164f6bcc32fdf867568c1793ab53`).
- Runtime: isolated Dolphin loaded m1l1 and reported `sky mohnight1 loaded (6 x 128x128 CMPR)` and `sky cube drawn name=mohnight1`; `direct map ready` confirms the map reached gameplay.
- Visual evidence: [playtest note](../media/playtests/notes/20261123-215710-m1l1-final-skybox.md), [gameplay screenshot](../media/playtests/screenshots/20261123-215710-m1l1-final-skybox/final.png), [silent H.264 capture](../media/playtests/videos/20261123-215710-m1l1-final-skybox-silent.mp4), and [six periodic frames](../media/playtests/screenshots/20261123-215710-m1l1-final-skybox/frames/).

The final screenshot shows the player view in m1l1 with the night sky over the village. Dolphin is emulator evidence; physical GameCube validation remains open.

## Remaining coverage

The full m1l1 maps stage is complete. Other campaign maps still need their own sky resolution, stage output, and runtime validation. The six-face completeness check in `stage_map_sky` prevents a partial cubemap from being treated as complete.
