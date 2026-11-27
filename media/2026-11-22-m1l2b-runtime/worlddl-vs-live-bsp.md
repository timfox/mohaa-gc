# m1l2b WorldDL versus live-BSP smoke comparison

Date: 2026-11-22, local Dolphin runs. Both captures used the same Xash3D-GC DOL (`00058c7af6468840062e39d0ef5536af6ce2d5537f188e7051b1cdda29bcd17e`), `m1l2b` map and props/audio stage, `--smoke-map m1l2b --world-render`, 640x480 output, Dolphin revision `7c9d49d63d`, and 45-second probe duration. The control ISO omitted only the `wd_m1l2b.gcd` WorldDL artifact. Both runs reached `MAP_READY m1l2b` and `newgame world render ready`.

| Route | ISO SHA-256 | Observed frame split | Renderer marker |
|---|---|---:|---|
| Earlier WorldDL smoke | `9987a5c970821b39ca5cbd34d5920ef8af368bbdc857b7d1c77e04efa2330cf0` | 198.5 ms / 5.0 fps, then 217.6 ms / 4.6 fps | 2,799 CapFaces batches |
| Earlier live-BSP control | `c00140bf03815fda3f497f79b42c96b1d9965c217d4edbe1153415fd41621a6c` | 45.8 ms / 21.8 fps initially; later samples 17.9–18.3 ms / 54.6–56.0 fps | CapFaces `drawn=1920`, 0 static props |
| Latest WorldDL default | `6a91a5760cfe71812e0d806a098a7cc5a31f309139658656bf21402d66a9a2fb` | 192.4 ms / 5.2 fps | 2,799 batches, prop pack 254 instances |
| Latest live-BSP diagnostic | `899f8e290a27ba9ccd59b703bea37e7394c33db913cf895ed06bc6bbaa2280b8` | 47.8 ms / 20.9 fps initially; later samples 17.8–18.3 ms / 54.5–56.3 fps | CapFaces `drawn=1920`, 0 static props |

The control log reports `MAP_READY m1l2b`, `newgame world render ready`, and a loaded CapFaces pack. The startup sample is higher cost; later samples stabilize near 55–56 fps. The first WorldDL run also had 2,799 batches. The control is not a fidelity-equivalent result: it draws zero static props and does not load the 254-instance MOHAA prop pack. Its speed is useful diagnostically, but it cannot stand in for a near-retail scene.

The default WorldDL build was re-run after this comparison. It loaded `wd_m1l2b.gcd` and the prop pack (254 instances, 101 models, 20,089 triangles), reached both map-ready markers, and measured 192.4 ms / 5.2 fps in its first frame split. The first WorldDL frame reports 2,799 batches. Keep WorldDL as the MOHAA default; use the live-BSP route only for diagnostics.

Xash3D-GC builder commit `0f16e2dc7` adds `--skip-smoke-worlddl` for a smoke diagnostic; the MOHAA wrapper commit `2f96477` exposes it as `--skip-worlddl`. Normal MOHAA smoke builds continue to bake WorldDL. Next, profile and optimize the WorldDL path while preserving props, then validate against a GameCube hardware budget.

Control DOL SHA-256: `00058c7af6468840062e39d0ef5536af6ce2d5537f188e7051b1cdda29bcd17e`
Dolphin revision: `7c9d49d63d`
Control screenshot: [m1l2b-live-bsp-dolphin.png](m1l2b-live-bsp-dolphin.png)
Control log: [live-bsp-dolphin.log](live-bsp-dolphin.log)

## WorldDL stage profile — 2026-11-22 4:47 PM PT

With the default WorldDL path and converted m1l2b props enabled, the `gcvst` capture reported 2,799 batches in frame 1. At the two bounded profiler summaries, WorldDL consumed 149.9 ms and 184.7 ms per frame, while props consumed 11.7 ms and 5.7 ms; water was at or below 0.3 ms. Whole-frame measurements were 170.8 ms (5.9 fps) and 192.8 ms (5.2 fps). The renderer reached both map/world-render readiness markers and loaded the 254-instance / 101-model prop pack.

This confirms WorldDL is the dominant measured stage in this smoke view. It does not yet isolate time spent selecting chunks, preparing batches, binding textures/lightmaps, or submitting GX commands. Keep the props and WorldDL enabled while instrumenting those subcosts; do not use the fast live-BSP diagnostic as a fidelity replacement (that path omits props). The capture is under [gcvst-20261122-164734](gcvst-20261122-164734/), including the latest [screenshot](gcvst-20261122-164734/m1l2b-worlddl-gcvst.png), [full log](gcvst-20261122-164734/dolphin.log), and [build log](gcvst-20261122-164734/build.log).

Instrumented ISO SHA-256: `eda27e94947e8ce1a6bcfa6807ca01bc65f9c57ff078cbda2e4e56efac7def72`.

## Forced-chunk fence ring — 2026-11-22 5:17 PM PT

Xash3D-GC commit `62a3a6a3a912e1d45db4e1516f8d722c3256944a` added a three-slot forced-chunk bounce-buffer ring. It fences before a slot is reused after cycling through the ring, removing the previous immediate fence after each forced chunk. In a fresh 60-second Dolphin run, WorldDL measured 61.6–67.4 ms/frame and the whole frame 75.6–77.1 ms (13.0–13.2 fps), compared with 149.9–184.7 ms WorldDL and 170.8–192.8 ms total in the earlier capture. Forced chunk work measured 12.8–14.6 ms/frame, down from 42.9–47.5 ms/frame. The new run logged 382–432 fences per profiler window versus 1,307–1,435 force calls per window in the prior profile.

This is a directional comparison: the two runs used different DOL builds, so a same-DOL A/B remains necessary. The scene reached both map readiness markers and loaded the 254-instance prop pack, although its initial counter is zero before loading; later log lines confirm 1,890 horizon triangles from 27 instances and 988 near-prop triangles from 44 instances were drawn. Texture binding remains the largest profiled WorldDL substage at 38.3–41.8 ms/frame. The renderer has one 24 KiB CMPR bounce slot and logs 125 hits / 442 misses per frame, making texture-slot pressure the next target. Dolphin is not physical GameCube evidence. The new [screenshot](force-ring-20261122-171744/m1l2b-force-ring.png), [log](force-ring-20261122-171744/dolphin.log), and [run note](force-ring-20261122-171744/probe-note.md) are archived with build logs. Smoke ISO SHA-256: `af34b60635f5f2a3239b88a8f0dfa3e19f661c5ee5aa5205bfddfec8e06de56b`; DOL SHA-256: `bd1c185cbbad4591765715577e1ef7ace812b295fbecf707594a011e47185803`.
