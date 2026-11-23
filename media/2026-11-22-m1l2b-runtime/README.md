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


## WorldDL versus live-BSP comparison — 2026-11-22 4:16 PM PT

A matched 45-second Dolphin control run used the same engine DOL, map stage, props/audio extras, `--smoke-map m1l2b --world-render` path, resolution, and Dolphin configuration, but omitted the scratch WorldDL pack. The live-BSP/CapFaces route reached `MAP_READY m1l2b` and `newgame world render ready`. Its first recorded frame split was 45.8 ms (21.8 fps); subsequent samples stabilized at 17.9–18.3 ms (54.6–56.0 fps). `R_EdgeDrawing GX CapFaces drawn=1920`.

The earlier WorldDL smoke ISO measured 198.5 ms (5.0 fps) and 217.6 ms (4.6 fps), with 2,799 CapFaces batches. Taken together, this points to the WorldDL path or its generated workload as the dominant cost in that smoke build. It does not isolate whether the cost is WorldDL itself or a difference in baked workload, and Dolphin is not physical GameCube evidence. The current MOHAA SD stage has no `wd_m1l2b.gcd`; the generic smoke builder added WorldDL only to its first scratch ISO.

Control ISO SHA-256: `c00140bf03815fda3f497f79b42c96b1d9965c217d4edbe1153415fd41621a6c`. DOL SHA-256 is the same as above. Full control log: [live-bsp-dolphin.log](live-bsp-dolphin.log); screenshot: [m1l2b-live-bsp-dolphin.png](m1l2b-live-bsp-dolphin.png); run details: [worlddl-vs-live-bsp.md](worlddl-vs-live-bsp.md).

## Open issues

- Validate representative WorldDL and live-BSP routes under physical GameCube hardware or a closer hardware budget. Current numbers are emulator observations from a smoke route.
- The new m1l2b prop pack is staged and verified at runtime. `media/ss_m1l2b.gcs` remains absent; the generated `maps/m1l2b.snd` table has no runtime read marker yet. The first-person object remains a fallback melee model.
- A filesystem pool allocation failed once during map load (225.04 KiB request); the map still reached the render-ready marker.

Full Dolphin/OSReport log: [dolphin.log](/home/tim/Desktop/mohaa-gc/media/2026-11-22-m1l2b-runtime/dolphin.log).
