# MOHAA compass and scripted tips

## Current implementation

The GameCube client draws a MOHAA compass in the upper-left corner. The compass uses the retail back, face, needle, and objective-arrow textures converted to compact Xash v32 sprites. The face and objective arrow are baked into 16 orientation frames so the GameCube renderer does not need runtime sprite rotation. The active mission objective supplies the compass target.

The MOHAA script VM now handles the retail `huddraw_*` slot commands and routes `iprintlnbold` / `iprintlnbold_noloc` to a five-second gameplay tip. It concatenates multi-argument tips like the retail VM print routine. Tips are left-aligned under the compass and use a dark offset for readability; wrapping uses the active font's pixel widths and the remaining viewport width. The HUD draw runs on the MOHAA branch of the lean client redraw path. Menu-like shader slots are also supported through converted MOHAA sprite textures.

The retail `set_objective_pos` script command is now bound for both vector and entity arguments. It updates the client compass target, so scripts can steer the objective arrow toward a fixed point or a moving mission actor.

## Verification

- The GameCube DOL built successfully from isolated source copies; the output used for the probe was `/tmp/mohaa-compass-build/out/mohaagc.dol`.
- A GameCube-aware hybrid ISO booted directly into m1l2a in Dolphin. Runtime log reports the map ready and all four compass sprites loaded (`MOHAA HUD compass: back=1 face=1 needle=1 objective=1`).
- A temporary probe-only copy of `maps/m1l2a.scr` invoked `iprintlnbold` with the retail door instruction. The captured gameplay frame shows the message rendered. The test copy was staged under `/tmp/mohaa-compass-build/data`; retail source assets were not edited.
- A follow-up probe calls `iprintlnbold_noloc` with three text fragments, then runs the existing retail `hint_door` function via the script VM. Dolphin shows the exact retail message and confirms the client-width wrapping path. The injected `thread hint_door` call is only a probe; it does not prove which retail gameplay trigger should invoke that function.
- A separate probe invokes retail `set_objective_pos` with a known vector. The command is no longer reported as unbound, all compass sprites load, and the gameplay capture includes the compass and scripted hint. This proves command dispatch and HUD transport; matching the arrow bearing against a live retail mission target is still open.
- The test map's side/class chooser overlaps part of that message in the captured frame. A separate m1l1 gameplay capture shows the compass unobstructed.
- Follow-up visual refinement moves the tip to virtual x=20/y=126 beneath the compass, draws a dark one-pixel text offset, and scales the 32x32 compact compass sprites to a 48x48 logical display size. Both changed GameCube source files pass PowerPC syntax checks and the isolated DOL build succeeds (`/tmp/mohaa-hud-refine/engine-out/bin/mohaagc.dol`, SHA-256 `eb8cee28db6ae1a9a6b063e22a88d900a674bce97f1c03c0fa77208e96cf9490`). A full retail-data ISO was launched in Dolphin and reached the MOHAA front end, but the bounded pad-input probe did not enter gameplay; its capture is [here](../media/playtests/screenshots/20261124-020500-m1l2a-retail-compass-menu-route/final.png). Therefore the latest 48x48 compass and x=20/y=126 tip layout are build-verified but not yet visually verified in a gameplay frame.

Evidence:

- [Hint rendered in gameplay](../media/playtests/screenshots/20261124-003947-m1l2a-hint-render-v3/frames/frame-0007-0020s.png)
- [m1l1 compass gameplay screenshot](../media/playtests/screenshots/20261124-002832-m1l1-compass-tips-v3/final.png)
- [Probe note and runtime log details](../media/playtests/notes/20261124-003947-m1l2a-hint-render-v3.md)
- [Captured probe video](../media/playtests/videos/20261124-003947-m1l2a-hint-render-v3-silent.mp4)
- [Retail hint function capture](../media/playtests/screenshots/20261124-005153-m1l2a-retail-tip-wrap/frames/frame-0011-0026s.png)
- [Retail hint function probe log](../media/playtests/notes/20261124-005153-m1l2a-retail-tip-wrap.md)
- [Retail objective-position probe capture](../media/playtests/screenshots/20261124-005940-m1l2a-retail-objective-pos/frames/frame-0015-0034s.png)
- [Retail objective-position probe log](../media/playtests/notes/20261124-005940-m1l2a-retail-objective-pos.md)

## Still to verify

The compass and retail hint function are runtime-proven in earlier builds, but the latest position and scale need a gameplay capture. The real door interaction has not yet been played to prove its trigger invokes the message. The objective-position command reaches the HUD; bearing against a real moving mission target remains unverified. Compare compass size, font, lifetime, and fade against retail footage, verify non-text `huddraw_*` overlays such as the MG42 view across campaign triggers, and verify on physical GameCube hardware.
