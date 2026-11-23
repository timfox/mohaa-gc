# m1l2b WorldDL versus live-BSP smoke comparison

Date: 2026-11-22, local Dolphin runs. Both captures used the same Xash3D-GC DOL (`00058c7af6468840062e39d0ef5536af6ce2d5537f188e7051b1cdda29bcd17e`), `m1l2b` map and props/audio stage, `--smoke-map m1l2b --world-render`, 640x480 output, Dolphin revision `7c9d49d63d`, and 45-second probe duration. The control ISO omitted only the `wd_m1l2b.gcd` WorldDL artifact. Both runs reached `MAP_READY m1l2b` and `newgame world render ready`.

| Route | ISO SHA-256 | Observed frame split | Renderer marker |
|---|---|---:|---|
| WorldDL scratch smoke | `9987a5c970821b39ca5cbd34d5920ef8af368bbdc857b7d1c77e04efa2330cf0` | 198.5 ms / 5.0 fps, then 217.6 ms / 4.6 fps | CapFaces `drawn=2799` |
| Live BSP / no WorldDL control | `c00140bf03815fda3f497f79b42c96b1d9965c217d4edbe1153415fd41621a6c` | 45.8 ms / 21.8 fps initially; later samples 17.9–18.3 ms / 54.6–56.0 fps | CapFaces `drawn=1920` |

The control log reports `MAP_READY m1l2b`, `newgame world render ready`, and a loaded CapFaces pack. The startup sample is higher cost; later samples stabilize near 55–56 fps. The first WorldDL run also had 2,799 batches. This comparison suggests the WorldDL route or its generated workload is responsible for most of the observed cost, but it does not identify the exact renderer operation or establish physical GameCube performance.

The current persistent MOHAA SD stage does not contain `wd_m1l2b.gcd`. The generic builder created it for the earlier scratch ISO. For a falsifiable follow-up, compare WorldDL and live-BSP with identical renderer content/camera and collect renderer timing/batch breakdowns, then run the chosen route on physical hardware or within a measured GameCube budget.

Control DOL SHA-256: `00058c7af6468840062e39d0ef5536af6ce2d5537f188e7051b1cdda29bcd17e`
Dolphin revision: `7c9d49d63d`
Control screenshot: [m1l2b-live-bsp-dolphin.png](m1l2b-live-bsp-dolphin.png)
Control log: [live-bsp-dolphin.log](live-bsp-dolphin.log)
