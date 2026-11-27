# MOHAA skybox status — 2026-11-24

## Campaign stage

Retail sky resolution now covers all 37 maps in the current source set. Nineteen maps point to one of eight real retail cubemaps; all 48 128×128 GameCube CMPR faces are staged at 8,192 bytes each. Eighteen previously staged BSPs now have their resolved retail `skyname`; m1l1 already carried `mohnight1` from its full rebuild.

| Retail cubemap | Maps |
|---|---|
| `mohnight1` | m1l1, m1l2a, m1l2b, m6l3b |
| `mohnightfog` | m1l3a, m1l3b |
| `lighthousesky` | m1l3c |
| `nordawn` | m2l1 |
| `dday2` | m3l1a, m3l1b, m3l2, m3l3 |
| `mohday1` | m4l0 |
| `m5l2` | m5l1a, m5l1b, m5l2a, m5l2b |
| `mohday2` | m5l3, training |

Four maps have no sky surface in their BSP. Fourteen maps resolve to the literal retail shader root `idontexist`, for which the retail install contains no cubemap faces. Those maps keep `skyname` unset so they do not advertise a missing sky. No substitute art was invented.

The map-stage code now treats an absent retail face set as a nonfatal, unstaged sky and logs that it left the map skyname unset. It also rewrites any incomplete or wrong-size cached cubemap instead of accepting it based only on filenames. The retail-derived map and CMPR files live in the ignored local stage at `retail/mohaa-full-stage-20261122/`; they are not in Git.

## Runtime evidence

- The 2026-11-24 GX fix draws the retail cubemap even when MOHAA sets a fog far plane. The smoke-disc builder now stages the selected maps' six `media/sky_<skyname>*.cmp` faces, which had previously been omitted and caused early sky prefetch to fail. Both checks ran in isolated native Dolphin profiles:
  - m1l3a: all six `mohnightfog` faces load, the far plane remains `3523` with retail fog colour `8 13 23`, `sky cube drawn name=mohnightfog` is logged, and the capture visibly shows the foggy night sky: [probe note](../dod-gc/playtests/notes/20261124-182730-m1l3a-sky-farplane-fix-2.md), [screenshot](../dod-gc/playtests/screenshots/20261124-182730-m1l3a-sky-farplane-fix-2/matched.png), [video](../dod-gc/playtests/videos/20261124-182730-m1l3a-sky-farplane-fix-2-599d2faa7c.mp4).
  - Training: all six `mohday2` faces load, the far plane remains `9957` with retail fog colour `179 179 140`, `sky cube drawn name=mohday2` is logged, and the capture shows the daylight sky: [probe note](../dod-gc/playtests/notes/20261124-182819-training-mohday2-sky-farplane-fix.md), [screenshot](../dod-gc/playtests/screenshots/20261124-182819-training-mohday2-sky-farplane-fix/matched.png), [video](../dod-gc/playtests/videos/20261124-182820-training-mohday2-sky-farplane-fix-599d2faa7c.mp4).
- Earlier m1l1 visual/runtime verification loaded six `mohnight1` faces, logged `sky cube drawn name=mohnight1`, and visibly showed the night sky in Dolphin: [m1l1 report](../media/playtests/notes/20261123-215710-m1l1-final-skybox.md), [screenshot](../media/playtests/screenshots/20261123-215710-m1l1-final-skybox/final.png), [video](../media/playtests/videos/20261123-215710-m1l1-final-skybox-silent.mp4).
- The latest retail MainUI New Game capture combines the corrected m1l1 BSP and six staged `mohnight1` CMPR faces with the now-stable low-memory HUD. Dolphin logs `MAP_READY m1l1`, `sky mohnight1 loaded (6 x 128x128 CMPR)`, `sky cube drawn name=mohnight1`, and three completed client HUD redraws; its final still visibly shows the night cubemap over gameplay: [playtest note](../media/playtests/notes/20261123-231619-m1l1-hud-sky-retail.md), [screenshot](../media/playtests/screenshots/20261123-231619-m1l1-hud-sky-retail/final.png), [video](../media/playtests/videos/20261123-231619-m1l1-hud-sky-retail-silent.mp4).
- The follow-up GameCube-aware direct-map run packages the converted HUD sprites and confirms the full runtime combination: HUD assets load, `mohnight1` loads and draws, and the screenshot visibly shows the HUD over the nighttime m1l1 scene. See the [HUD/sky probe](../media/playtests/notes/20261123-232953-mohaa-hud-direct-map.md) and [screenshot](../media/playtests/screenshots/20261123-232953-mohaa-hud-direct-map/final.png).
- New m1l3a direct-map probe reached `MAP_READY m1l3a` and logged `sky mohnightfog loaded (6 x 128x128 CMPR)`: [probe note](../media/playtests/notes/20261123-222949-m1l3a-mohnightfog-verified.md), [screenshot](../media/playtests/screenshots/20261123-222949-m1l3a-mohnightfog-verified/final.png), [video](../media/playtests/videos/20261123-222949-m1l3a-mohnightfog-verified-silent.mp4).
- A training-map probe reached `MAP_READY training` and logged `sky mohday2 loaded (6 x 128x128 CMPR)`: [probe note](../media/playtests/notes/20261123-223534-training-mohday2-player.md), [screenshot](../media/playtests/screenshots/20261123-223534-training-mohday2-player/final.png), [video](../media/playtests/videos/20261123-223534-training-mohday2-player-silent.mp4).

The m1l3a, Training, and m1l1 captures now visibly prove three distinct retail sky roots. Five other real roots remain to be visually checked. The gameplay views also show other map and world-rendering gaps outside this skybox fix. Dolphin evidence does not certify physical GameCube rendering.
