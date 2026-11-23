# m1l2b forced-chunk ring probe — 2026-11-22 5:17 PM PT

## Build and run

- Engine source commit: `62a3a6a3a912e1d45db4e1516f8d722c3256944a` (`codex/mohaa-local-diagnostics`).
- MOHAA wrapper revision used by the generated probe note: `c5888cb3f0`.
- DOL SHA-256: `bd1c185cbbad4591765715577e1ef7ace812b295fbecf707594a011e47185803`.
- Smoke ISO SHA-256: `af34b60635f5f2a3239b88a8f0dfa3e19f661c5ee5aa5205bfddfec8e06de56b`.
- ISO built from the staged MOHAA `m1l2b` map, shared local DoD/Valve boot assets, WorldDL assets, and a 41-entry `extras.pk3` with the large converted prop entries stored without compression.
- Dolphin revision `7c9d49d63d`; 60-second run at 640x480. MMU and Accurate CPU Cache were enabled. The log shows the OpenGL shader cache. This is a Dolphin smoke route, not a retail gameplay session or physical GameCube run.
- Reproducible artifacts copied here: `dolphin.log`, `engine-build.log`, `disc-build.log`, `m1l2b-force-ring.png`.

## Runtime evidence

- Reached `MAP_READY m1l2b` and `newgame world render ready`.
- Loaded the prop pack: 254 instances, 101 models, 20,089 triangles, 777 KiB ARAM.
- The startup counter reports zero static props drawn at that point. Pack loading is verified; drawing of those instances during the measured frames is not.
- Renderer reports a three-slot forced-chunk ring, 7 KiB per slot.

## Timings

The previous profiler capture measured WorldDL at 149.9–184.7 ms/frame, forced work at 42.9–47.5 ms/frame, and total frame time at 170.8–192.8 ms (5.2–5.9 fps). This capture measured:

- WorldDL: 61.6–67.4 ms/frame.
- Forced work: 12.8–14.6 ms/frame; 1,146–1,298 force calls per profile window.
- Texture binding: 38.3–41.8 ms/frame.
- Total frame: 75.6–77.1 ms (13.0–13.2 fps).
- Forced-chunk fences: 381.6–432 per profile window.

The captures use different DOL builds, so this is directional evidence rather than a controlled A/B. Next, build both revisions with the same assets/configuration, compare the exact capture route, and verify static-prop draw counts. Then profile texture binding. Physical GameCube budget validation remains open.
