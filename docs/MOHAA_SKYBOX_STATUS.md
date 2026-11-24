# MOHAA skybox status — 2026-11-23

The m1l1 runtime now resolves and draws its retail skybox. The retail BSP shader `textures/sky/africanight` maps to the `env/mohnight1` cubemap. `tools/mohaa_sky.py` converts all six faces to 128×128 GameCube CMPR (`8,192` bytes each), and the maps stage writes `mohnight1` as the compiled BSP's `skyname`.

## Runtime evidence

The previous m1l1 test ISO used an older converted BSP without a `skyname`; its log fell back to the empty `desert` sky. A separate scratch ISO was assembled with the m1l1 worldspawn set to `skyname "mohnight1"` and the six retail-derived CMPR faces. The source stage and original ISO were left untouched.

- ISO: `/tmp/mohaa-sky-update/out/m1l1-skybox-v2.iso` (1,199,233,024 bytes; SHA-256 `53975585c9d5b6f808e207e3a9b1247ec7a22a49021adb1d072711b9e5e7ef6a`)
- Runtime: isolated Dolphin, 28-second m1l1 probe. OSReport confirms `map skyname early mohnight1`, `sky mohnight1 loaded (6 x 128x128 CMPR)`, `sky cube drawn name=mohnight1`, and `MAP_READY m1l1`.
- Captures: [playtest note](../media/playtests/notes/20261123-213552-m1l1-skybox-runtime-verify.md), [silent H.264 clip](../media/playtests/videos/20261123-213552-m1l1-skybox-runtime-verify-silent.mp4), and [periodic guest frames](../media/playtests/screenshots/20261123-213552-m1l1-skybox-runtime-verify/frames/).

The stills show the Allies class picker, not an unobstructed sky view. Runtime logs verify the six-face load and sky-cube draw; visual review from the player view remains open.

## Remaining build gate

The full `mohaa_sd.py --stages maps --maps m1l1` rebuild could not run because the local SDHLT toolchain was absent and its build script could not clone `seedee/SDHLT` with network access restricted. The test ISO uses a scratch BSP copy to verify sky-name/runtime behavior. Regenerate the permanent m1l1 map stage with the local patched SDHLT toolchain when available; the six-face completeness check is now in `stage_map_sky`.
