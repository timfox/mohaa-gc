# MOHAA Probe m1l2a-door-hint-targeted — 20261124-042207

- ISO: `/tmp/mohaa-door-hint/mohaa-m1l2a-door-hint-playable.iso`
- Route: `m1l2a-door-hint-targeted`
- Duration cap: 45s
- Repo: `unknown`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261124-042207-m1l2a-door-hint-targeted/`
- Periodic guest frames: 14 screenshots in `media/playtests/screenshots/20261124-042207-m1l2a-door-hint-targeted/frames/`
- Video: `media/playtests/videos/20261124-042207-m1l2a-door-hint-targeted-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: bd6a4241d7. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-door-hint/mohaa-m1l2a-door-hint-playable.iso (SHA-256 1bb6e4f9ddcaff5b1860020cb43ec1506d409de2a045ffd5b0c5bb1bb8109164). Full-physics m1l2a route with corrected Dolphin pad-pipe setup; drive from info_player_start toward BSP-derived door_locked trigger model 8, then turn and press USE. Input sequence saved in /tmp/mohaa-door-hint/pad-input-target.log.

## Result

The controller input reached Dolphin. OSReport shows the player at `(4869,-3840,22)` and the nearest `trigger_multiple` at 118 units; the engine then skipped the world interaction on m1l2a. No door trigger touch or hint occurred.

## Frame stats
```
final.png: (640, 480) black=8.9% mean=(39, 32, 23)
```

## OSReport (key)
```
19:22:09:524 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
34:22:09:560 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=mohaa
35:22:09:560 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: linked gamedir=mohaa detected=mohaa
40:22:09:561 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
67:22:09:609 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
84:22:10:010 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Program args: xash xash -dev 2 -log -game mohaa -gcnewgame -gcworldrender -gcmap m1l2a -gclistenserver m1l2a -gcfullphysics -gcchangelevel m1l2a -gcplayerinput -width 320 -height 240
117:22:10:026 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: released unused nodes reserve 256 Kb
118:22:10:027 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: released unused submodels reserve 16 Kb
170:22:10:066 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: heap mark stage=client_local_init_ready used=865824 free=246400 unclaimed=319488 avail=565888
200:22:10:095 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=876272 free=235952 unclaimed=319488 avail=555440
207:22:10:130 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: renderer screen map ready
210:22:10:131 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=876272 free=235952 unclaimed=319488 avail=555440
219:22:10:132 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: heap mark stage=renderer_images_ready used=876408 free=235816 unclaimed=319488 avail=555304
223:22:10:134 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: heap mark stage=renderer_init_ready used=974800 free=137424 unclaimed=319488 avail=456912
230:22:10:140 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: heap mark stage=client_video_init_ready used=978552 free=133672 unclaimed=319488 avail=453160
253:22:10:145 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=982344 free=129880 unclaimed=319488 avail=449368
261:22:10:153 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: gcmap lookup begin
262:22:10:153 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: queue map m1l2a
263:22:10:153 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: direct map begin
270:22:10:155 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: G326 pre-map client ensure begin
273:22:10:155 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: released unused nodes reserve 256 Kb
274:22:10:155 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: released unused submodels reserve 16 Kb
276:22:10:155 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: freed 0 menu/UI textures for map load
277:22:10:156 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: GX HUD/menu slabs released for map load
298:22:10:160 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: titles init skipped for gcmap smoke route
303:22:10:163 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: client edicts using static gcmap bootstrap tables
393:22:10:171 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: heap mark stage=client_module_ready used=1004232 free=79320 unclaimed=348160 avail=427480
395:22:10:171 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1004232 free=79320 unclaimed=348160 avail=427480
396:22:10:171 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: G326 pre-map client ensure ready
397:22:10:171 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: freed 0 menu/UI textures for map load
398:22:10:171 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: GX HUD/menu slabs released for map load
399:22:10:172 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: G326 keep client across newgame map load
400:22:10:172 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: client subsystems trimmed for map load
404:22:10:172 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: renderer trim for map load
405:22:10:172 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: present buf released map load
421:22:10:176 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: map load cfg skipped
424:22:10:178 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: pre-spawn mem map set
437:22:10:180 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: present buf released map load
441:22:10:181 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: server string arena spill dropped for map reload
454:22:10:182 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: pre-spawn map buffer prepared for m1l2a
457:22:10:182 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:09] Xash3D GameCube: server string arena spill dropped for map reload
468:22:11:294 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:10] Xash3D GameCube: map load compact (no lighting, miptex headers only) 3.14 Mb 竊 1.96 Mb (G154 disc LM) +align
513:22:11:526 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:11] Xash3D GameCube: world surfedges copied 230.03 Kb to map tail
525:22:11:529 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:11] Xash3D GameCube: releasing gcmap BSP staging 1.96 Mb before surfaces
572:22:11:606 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:11] Xash3D GameCube: map skyname early mohnight1 (before CapFaces)
648:22:13:865 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:13] Xash3D GameCube: freed 126 menu/UI textures for map load
649:22:13:865 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:13] Xash3D GameCube: GX HUD/menu slabs released for map load
1315:22:14:449 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:14] Xash3D GameCube: resource sync skipped for local map route
1321:22:14:455 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:14] Xash3D GameCube: renderer restore after map load
1322:22:14:456 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:14] Xash3D GameCube: map loaded m1l2a
1323:22:14:456 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1325:22:14:457 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:14] Xash3D GameCube: budget moved entity text to map leftover (46.10 Kb), entity reserve returned, heap free 201.74 Kb
1327:22:14:465 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:14] Warning: Xash3D GameCube: direct-map player unavailable map=m1l2a
1331:22:14:466 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1333:22:14:466 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:14] Xash3D GameCube: direct map ready
1336:22:14:467 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:14] Xash3D GameCube: freed 126 menu/UI textures for map load
1337:22:14:467 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:14] Xash3D GameCube: GX HUD/menu slabs released for map load
1340:22:14:467 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:14] Xash3D GameCube: freed 126 menu/UI textures for map load
1341:22:14:467 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:14] Xash3D GameCube: GX HUD/menu slabs released for map load
1345:22:14:468 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:22:14] Xash3D GameCube: map loaded m1l2a
```

- Full Dolphin log: `media/playtests/screenshots/20261124-042207-m1l2a-door-hint-targeted/dolphin.log.gz`
