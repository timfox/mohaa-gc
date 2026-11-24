# MOHAA Probe m1l2a-door-hint-trigger-crossing — 20261124-042723

- ISO: `/tmp/mohaa-door-hint/mohaa-m1l2a-door-hint-playable.iso`
- Route: `m1l2a-door-hint-trigger-crossing`
- Duration cap: 40s
- Repo: `unknown`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261124-042723-m1l2a-door-hint-trigger-crossing/`
- Periodic guest frames: 19 screenshots in `media/playtests/screenshots/20261124-042723-m1l2a-door-hint-trigger-crossing/frames/`
- Video: `media/playtests/videos/20261124-042723-m1l2a-door-hint-trigger-crossing-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: bd6a4241d7. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-door-hint/mohaa-m1l2a-door-hint-playable.iso (SHA-256 1bb6e4f9ddcaff5b1860020cb43ec1506d409de2a045ffd5b0c5bb1bb8109164). Full-physics m1l2a with scripted controller: forward toward door_locked trigger model 8, strafe left for nine seconds across its BSP bounds, then USE. Input sequence archived in /tmp/mohaa-door-hint/pad-input-target3.log.

## Result

The controller moved the player to the gate area. OSReport shows a 74-unit `trigger_multiple` candidate, but the engine safety gate skipped it before `pfnTouch`; the retail door hint was not reached.

## Frame stats
```
final.png: (640, 480) black=8.9% mean=(41, 33, 24)
```

## OSReport (key)
```
19:27:25:465 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
34:27:25:502 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=mohaa
35:27:25:503 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: linked gamedir=mohaa detected=mohaa
40:27:25:504 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
67:27:25:551 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
84:27:25:951 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Program args: xash xash -dev 2 -log -game mohaa -gcnewgame -gcworldrender -gcmap m1l2a -gclistenserver m1l2a -gcfullphysics -gcchangelevel m1l2a -gcplayerinput -width 320 -height 240
117:27:25:968 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: released unused nodes reserve 256 Kb
118:27:25:969 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: released unused submodels reserve 16 Kb
170:27:26:008 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: heap mark stage=client_local_init_ready used=865824 free=246400 unclaimed=319488 avail=565888
200:27:26:039 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=876272 free=235952 unclaimed=319488 avail=555440
207:27:26:074 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: renderer screen map ready
210:27:26:075 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=876272 free=235952 unclaimed=319488 avail=555440
219:27:26:076 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: heap mark stage=renderer_images_ready used=876408 free=235816 unclaimed=319488 avail=555304
223:27:26:078 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: heap mark stage=renderer_init_ready used=974800 free=137424 unclaimed=319488 avail=456912
230:27:26:084 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: heap mark stage=client_video_init_ready used=978552 free=133672 unclaimed=319488 avail=453160
253:27:26:089 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=982344 free=129880 unclaimed=319488 avail=449368
261:27:26:097 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: gcmap lookup begin
262:27:26:097 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: queue map m1l2a
263:27:26:097 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: direct map begin
270:27:26:098 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: G326 pre-map client ensure begin
273:27:26:099 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: released unused nodes reserve 256 Kb
274:27:26:099 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: released unused submodels reserve 16 Kb
276:27:26:099 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: freed 0 menu/UI textures for map load
277:27:26:099 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: GX HUD/menu slabs released for map load
298:27:26:103 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: titles init skipped for gcmap smoke route
303:27:26:107 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: client edicts using static gcmap bootstrap tables
393:27:26:114 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: heap mark stage=client_module_ready used=1004232 free=79320 unclaimed=348160 avail=427480
395:27:26:115 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1004232 free=79320 unclaimed=348160 avail=427480
396:27:26:115 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: G326 pre-map client ensure ready
397:27:26:115 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: freed 0 menu/UI textures for map load
398:27:26:115 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: GX HUD/menu slabs released for map load
399:27:26:115 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: G326 keep client across newgame map load
400:27:26:115 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: client subsystems trimmed for map load
404:27:26:116 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: renderer trim for map load
405:27:26:116 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: present buf released map load
421:27:26:120 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: map load cfg skipped
424:27:26:122 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: pre-spawn mem map set
437:27:26:124 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: present buf released map load
441:27:26:124 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: server string arena spill dropped for map reload
454:27:26:126 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: pre-spawn map buffer prepared for m1l2a
457:27:26:126 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:25] Xash3D GameCube: server string arena spill dropped for map reload
468:27:27:235 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:26] Xash3D GameCube: map load compact (no lighting, miptex headers only) 3.14 Mb 竊 1.96 Mb (G154 disc LM) +align
513:27:27:469 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:27] Xash3D GameCube: world surfedges copied 230.03 Kb to map tail
525:27:27:471 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:27] Xash3D GameCube: releasing gcmap BSP staging 1.96 Mb before surfaces
572:27:27:548 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:27] Xash3D GameCube: map skyname early mohnight1 (before CapFaces)
648:27:29:807 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:29] Xash3D GameCube: freed 126 menu/UI textures for map load
649:27:29:807 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:29] Xash3D GameCube: GX HUD/menu slabs released for map load
1315:27:30:391 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:30] Xash3D GameCube: resource sync skipped for local map route
1321:27:30:397 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:30] Xash3D GameCube: renderer restore after map load
1322:27:30:397 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:30] Xash3D GameCube: map loaded m1l2a
1323:27:30:397 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1325:27:30:398 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:30] Xash3D GameCube: budget moved entity text to map leftover (46.10 Kb), entity reserve returned, heap free 201.74 Kb
1327:27:30:407 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:30] Warning: Xash3D GameCube: direct-map player unavailable map=m1l2a
1331:27:30:408 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1333:27:30:408 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:30] Xash3D GameCube: direct map ready
1336:27:30:409 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:30] Xash3D GameCube: freed 126 menu/UI textures for map load
1337:27:30:409 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:30] Xash3D GameCube: GX HUD/menu slabs released for map load
1340:27:30:409 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:30] Xash3D GameCube: freed 126 menu/UI textures for map load
1341:27:30:409 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:30] Xash3D GameCube: GX HUD/menu slabs released for map load
1345:27:30:410 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:27:30] Xash3D GameCube: map loaded m1l2a
```

- Full Dolphin log: `media/playtests/screenshots/20261124-042723-m1l2a-door-hint-trigger-crossing/dolphin.log.gz`
