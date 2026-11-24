# MOHAA compass and scripted tips

## Current implementation

The GameCube client draws a MOHAA compass in the upper-left corner. The compass uses the retail back, face, needle, and objective-arrow textures converted to compact Xash v32 sprites. The face and objective arrow are baked into 16 orientation frames so the GameCube renderer does not need runtime sprite rotation. The active mission objective supplies the compass target.

The MOHAA script VM now handles the retail `huddraw_*` slot commands and routes `iprintlnbold` / `iprintlnbold_noloc` to a centered, five-second HUD message. The HUD draw runs on the MOHAA branch of the lean client redraw path. Menu-like shader slots are also supported through converted MOHAA sprite textures.

## Verification

- The GameCube DOL built successfully from isolated source copies; the output used for the probe was `/tmp/mohaa-compass-build/out/mohaagc.dol`.
- A GameCube-aware hybrid ISO booted directly into m1l2a in Dolphin. Runtime log reports the map ready and all four compass sprites loaded (`MOHAA HUD compass: back=1 face=1 needle=1 objective=1`).
- A temporary probe-only copy of `maps/m1l2a.scr` invoked `iprintlnbold` with the retail door instruction. The captured gameplay frame shows the message rendered. The test copy was staged under `/tmp/mohaa-compass-build/data`; retail source assets were not edited.
- The test map's side/class chooser overlaps part of that message in the captured frame. A separate m1l1 gameplay capture shows the compass unobstructed.

Evidence:

- [Hint rendered in gameplay](../media/playtests/screenshots/20261124-003947-m1l2a-hint-render-v3/frames/frame-0007-0020s.png)
- [m1l1 compass gameplay screenshot](../media/playtests/screenshots/20261124-002832-m1l1-compass-tips-v3/final.png)
- [Probe note and runtime log details](../media/playtests/notes/20261124-003947-m1l2a-hint-render-v3.md)
- [Captured probe video](../media/playtests/videos/20261124-003947-m1l2a-hint-render-v3-silent.mp4)

## Still to verify

The compass and `iprintlnbold` presentation are runtime-proven, but the real retail door interaction has not yet been played to prove its trigger invokes the message. Additional work remains to compare compass positioning, font, lifetime, fade, and objective-arrow behavior against retail footage, and to verify non-text `huddraw_*` overlays such as the MG42 view across their actual campaign triggers. Physical GameCube playback is also unverified.
