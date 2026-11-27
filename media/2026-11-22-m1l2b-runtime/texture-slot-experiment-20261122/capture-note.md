# MOHAA m1l2b texture-slot experiment — 2026-11-22

## Fresh baseline capture

- Local capture time: 2026-11-22 18:03–18:04 PT; Dolphin timeout: 60 seconds. Another Dolphin process was active throughout this guest run, so frame timing and FPS are not isolated.
- Route: `mohaa-ring-ab-baseline`; map reached `m1l2b`, then `gcmap smoke frames ready`.
- Visual: [baseline screenshot](baseline/m1l2b-baseline.png), 640×480. Dolphin FPS overlay reads about 5.23.
- Engine source used to build this DOL: `8b508c2d90e6a6e49fb081c183ff6955dbe919ec` (`engine-base`).
- DOL SHA-256: `e8410377f45714023d0af7b66e841f2babefbda9d5fe69bcf15ef463adae306b`.
- Smoke ISO SHA-256: `ddb4d0186b9cc6dec447f1fb5595afc6a70870bfdabb940757e426529ec82ca2`.
- Runtime reported `world DL widest PVS 1139 Kb`, cache 192 KiB, 11 cache-tail texture slots plus 6 heap slots (17 near slots total). The later prop counters report horizon props and `prop draw tris=988 near=44`.
- The raw log reported WorldDL at 184.4 ms/frame; forced work 47.5 ms, texture binding 101.2 ms, props 5.7 ms, whole frame 192.7 ms (5.2 fps). These are contaminated by the concurrent Dolphin and are not a valid standalone performance baseline.

## Candidate build

- Candidate DOL uses engine commit `62a3a6a3a912e1d45db4e1516f8d722c3256944a` plus an isolated scratch-only WorldDL cache cap change from 192 KiB to 128 KiB. No project source was changed for this experiment.
- Candidate DOL SHA-256: `0c3ceb53b629cd596d11d3d91fbed992066b3e1309b9a5042735a5c1efbe8703`.
- Candidate ISO SHA-256: `b709563385cab39d9274e5728bfe9964555c38e55a561382a1b2011153dd5af2`.
- Both ISOs use the same m1l2b content, boot grafts, extras archive, and probe settings. The DOLs differ only by the one-line cache-retention cap change. The isolated runtime captures compare map-render and allocation behavior; they do not establish a speedup because no frame-time profiler was enabled.
- The original attempts had no guest frame, but isolated runtime captures were completed on 2026-11-22 once a local Dolphin build was available. The 192 KiB control and 128 KiB candidate are recorded in [isolated-cache-ab](isolated-cache-ab/README.md). Both reached m1l2b render-ready and drew the same prop workload. The candidate retained 15 small + 1 large texture slot versus 11 small + 0 large for control. These probes confirm render compatibility and the cache/slot allocation change; no frame-time profiler was enabled, so they do not prove a speedup.

- Correction: the first isolated run was started with a route label that said `128k-candidate`, but its ISO hash identifies the 192 KiB control. It is archived as the control and the correctly hashed candidate was run separately.

Raw logs and build/package records are archived alongside this note. The upstream probe note reports the configured shared checkout SHA and does not identify the isolated baseline DOL source; use the build source revision above for this comparison.
