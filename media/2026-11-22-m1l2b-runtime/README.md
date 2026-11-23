# MOHAA m1l2b GameCube runtime capture — 2026-11-22

Fresh 45-second Dolphin smoke run of the m1l2b map using the local MOHAA SD stage plus the shared DoD/Valve smoke assets. The ISO was assembled from the MOHAA gamedir and booted with `--smoke-map m1l2b --world-render`.

## Result

The engine reached `MAP_READY m1l2b` and `newgame world render ready`; the screenshot shows the first-person view in the night airfield map. This is an automated local map/world-render smoke route, not a complete MOHAA retail gameplay port.

![m1l2b in Dolphin](/home/tim/Desktop/mohaa-gc/media/2026-11-22-m1l2b-runtime/m1l2b-dolphin-final.png)

## Run identity

- Engine source: Xash3D-GC commit `52f7ae8bbb`.
- DOL SHA-256: `00058c7af6468840062e39d0ef5536af6ce2d5537f188e7051b1cdda29bcd17e`.
- ISO SHA-256: `80a8f55f8573b7f3acb5665ead9a0181a76ee09f682cdcd2a774f59ca310fc55` (built under `/tmp/mohaa-m1l2b-runtime-20261122/`).
- m1l2b BSP SHA-256: `ef71b1bd3f121d74560ba47bac1304e3c62d8c371d069dba5a7579e4d92b8a74`.
- Dolphin build revision: `7c9d49d63d` (`/home/tim/.local/xash3d-gc-baseline/3rdparty/dolphin`).
- Probe: 45 seconds, 640x480 screenshot; MMU and Accurate CPU Cache enabled. No physical GameCube result is claimed.

## Prop and sound assets — 2026-11-22 4:08 PM PT

A second scratch ISO mounted an `extras.pk3` containing the MOHAA prop, terrain, and sound assets. The engine log confirms `prop pack m1l2b v10 inst=254 models=101 tris=20089 aram=777 Kb`; the new capture shows the telephone poles and wires.

![m1l2b with converted props](/home/tim/Desktop/mohaa-gc/media/2026-11-22-m1l2b-runtime/m1l2b-props-dolphin.png)

- `gp_m1l2b.gcp`: 795,680 bytes, SHA-256 `0adb34f1105a330ff0c0a68de42f3300fbf6b510ffced4369813cae9129aeb81`.
- `pt_m1l2b.gct`: 704,704 bytes, SHA-256 `db0f929856643d5fa89b6c25a4dda53661ee00179f35d98a2fa6885ebbb6c059`.
- The prop bake found 80 source models and 60 textures, with no missing model textures; it emitted 254 instances, 101 models, and 20,089 triangles. See [prop-bake.log](prop-bake.log).
- `maps/m1l2b.snd` was generated from 31 scripts: 20 aliases, 29 referenced samples, zero unresolved aliases, 17 conversions. Six previously missing samples were added to the staged SD tree; 11 existing sound files were preserved. The runtime log does not confirm that it reads the `.snd` table.
- The scratch ISO SHA-256 is `9987a5c970821b39ca5cbd34d5920ef8af368bbdc857b7d1c77e04efa2330cf0`; the 45-second Dolphin log is [props-dolphin.log](props-dolphin.log).


## WorldDL versus live-BSP comparison — 2026-11-22 4:16–4:38 PM PT

A matched 45-second Dolphin control run used the same engine DOL, map stage, props/audio extras, `--smoke-map m1l2b --world-render` path, resolution, and Dolphin configuration, but omitted the scratch WorldDL pack. The live-BSP/CapFaces route reached `MAP_READY m1l2b` and `newgame world render ready`. Its first recorded frame split was 45.8 ms (21.8 fps); subsequent samples stabilized at 17.9–18.3 ms (54.6–56.0 fps). `R_EdgeDrawing GX CapFaces drawn=1920`.

The faster control was not a fidelity-equivalent result: its runtime log reports zero static props and does not load the 254-instance MOHAA prop pack. The WorldDL path does load the prop pack and renders map geometry and props. Keep WorldDL enabled for normal MOHAA builds; the no-WorldDL route is now an explicit diagnostic option only. The comparison points to a WorldDL performance bottleneck, but not a shippable path choice.

A fresh default WorldDL build after that correction reached `MAP_READY m1l2b` and `newgame world render ready`, loaded `wd_m1l2b.gcd` and the prop pack (`254` instances, `101` models, `20,089` triangles), and measured 192.4 ms / 5.2 fps in its first logged frame split. Its first WorldDL frame reports 2,799 batches. This matches the earlier slow WorldDL result while retaining the map props. Dolphin is not physical GameCube evidence.

The latest paired builds used the same DOL (`00058c7af6468840062e39d0ef5536af6ce2d5537f188e7051b1cdda29bcd17e`), MOHAA map stage, boot grafts, and `extras.pk3`. The live-BSP diagnostic ISO SHA-256 is `899f8e290a27ba9ccd59b703bea37e7394c33db913cf895ed06bc6bbaa2280b8`; the default WorldDL ISO SHA-256 is `6a91a5760cfe71812e0d806a098a7cc5a31f309139658656bf21402d66a9a2fb`. Full logs, build logs, and captures: [live-BSP diagnostic](live-bsp-diagnostic-dolphin.log) / [screenshot](m1l2b-live-bsp-diagnostic.png), [default WorldDL](worlddl-default-dolphin.log) / [screenshot](m1l2b-worlddl-default-dolphin.png). Build logs are [live-BSP](build-live-bsp-diagnostic.log) and [WorldDL](build-worlddl-default.log).

The builder default is preserved. Xash3D-GC commit `0f16e2dc7` adds the low-fidelity `--skip-smoke-worlddl` diagnostic switch; the MOHAA lean wrapper commit `2f96477` exposes it as `--skip-worlddl`. Without that switch, MOHAA smoke builds bake WorldDL as before. The DOL remains from engine source `52f7ae8bb`; these changes affect disc staging only.

## Open issues

- Profile and reduce the WorldDL frame cost while retaining the static props; the 2,799-batch frame is the next target.
- Validate the optimized WorldDL route on physical GameCube hardware or within a measured hardware budget. Current numbers are Dolphin observations from a smoke route.
- The new m1l2b prop pack is staged and verified at runtime. `media/ss_m1l2b.gcs` remains absent; the generated `maps/m1l2b.snd` table has no runtime read marker yet. The first-person object remains a fallback melee model.
- A filesystem pool allocation failed once during map load (225.04 KiB request); the map still reached the render-ready marker.

Full Dolphin/OSReport log: [dolphin.log](/home/tim/Desktop/mohaa-gc/media/2026-11-22-m1l2b-runtime/dolphin.log).

## WorldDL stage timing — 2026-11-22 4:47 PM PT

A fresh 60-second Dolphin run enabled the renderer's bounded `gcvst` stage profiler while keeping the default WorldDL path and the full m1l2b prop pack enabled. It reached `MAP_READY m1l2b` and `newgame world render ready`; WorldDL reported 2,799 batches and the prop pack reported 254 instances, 101 models, and 20,089 triangles.

![Latest m1l2b WorldDL gameplay capture](/home/tim/Desktop/mohaa-gc/media/2026-11-22-m1l2b-runtime/gcvst-20261122-164734/m1l2b-worlddl-gcvst.png)

| Timed stage | Sample 1 | Sample 2 |
|---|---:|---:|
| WorldDL | 149.9 ms | 184.7 ms |
| Static props | 11.7 ms | 5.7 ms |
| Water | 0.3 ms | 0.0 ms |
| Whole frame | 170.8 ms (5.9 fps) | 192.8 ms (5.2 fps) |

The WorldDL traversal/draw stage dominates the measured frame. The 2,799-batch count is a useful workload marker, but is not proof that GX draw submission alone is the cost. The next optimization should separately measure candidate chunk traversal versus emitted batches and texture/lightmap binds, preserving the current prop-rendering path. Dolphin is not physical GameCube evidence.

Run artifacts: [screenshot](gcvst-20261122-164734/m1l2b-worlddl-gcvst.png), [Dolphin log](gcvst-20261122-164734/dolphin.log), [build log](gcvst-20261122-164734/build.log), and [probe note](gcvst-20261122-164734/probe-note.md). Instrumented ISO SHA-256: `eda27e94947e8ce1a6bcfa6807ca01bc65f9c57ff078cbda2e4e56efac7def72`.
