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
- Follow-up visual refinement scales the 32x32 compact compass sprites to a 48x48 logical display size and positions the retail tip at virtual x=8/y=45, just under the compass as in the supplied retail reference. After regenerating the GameCube client/server archives and engine, the DOL built at `/tmp/mohaa-hud-refine/engine-out/bin/mohaagc.dol` (SHA-256 `f07963070d21ff4401eac1845c63bfbf740b83ddd5d522682e20be4fdc9643c0`). The first build attempt exhausted the startup heap; the rebuilt DOL reached `MAP_READY m1l1`, then DSI’d in the stock `CHudBattery::Draw` at `battery.cpp:85` before `GC_DrawMohaaHud` ran. The [guest error frame](../media/playtests/screenshots/20261124-024911-m1l1-intro-finalhud-bootcheck/final.png) and [runtime log](../media/playtests/screenshots/20261124-024911-m1l1-intro-finalhud-bootcheck/dolphin.log) are archived. The revised tip position has not yet been visually verified.

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

The compass and retail hint function are runtime-proven in earlier builds, but the latest position still needs a gameplay capture. Fix the current stock `CHudBattery::Draw` DSI so the MOHAA branch can draw, then capture the m1l1 opening truck and its native retail movement tip. The real door interaction has not yet been played to prove its trigger invokes the message. The objective-position command reaches the HUD; bearing against a real moving mission target remains unverified. Compare compass size, font, lifetime, and fade against retail footage, verify non-text `huddraw_*` overlays such as the MG42 view across campaign triggers, and verify on physical GameCube hardware.
