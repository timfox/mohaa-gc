# MOHAA Probe m1l2a-door-hint-trigger-touch2 — 20261124-042517

- ISO: `/tmp/mohaa-door-hint/mohaa-m1l2a-door-hint-playable.iso`
- Route: `m1l2a-door-hint-trigger-touch2`
- Duration cap: 40s
- Repo: `unknown`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261124-042517-m1l2a-door-hint-trigger-touch2/`
- Periodic guest frames: 20 screenshots in `media/playtests/screenshots/20261124-042517-m1l2a-door-hint-trigger-touch2/frames/`
- Video: `media/playtests/videos/20261124-042517-m1l2a-door-hint-trigger-touch2-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: bd6a4241d7. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-door-hint/mohaa-m1l2a-door-hint-playable.iso (SHA-256 1bb6e4f9ddcaff5b1860020cb43ec1506d409de2a045ffd5b0c5bb1bb8109164). Full-physics m1l2a pad run: forward from player start to the locked-door trigger x/y, then strafe left across its brush; press USE. Input sequence archived in /tmp/mohaa-door-hint/pad-input-target2.log.

## Result

The controller reached within 74 units. The engine logged `world interaction skip classname=trigger_multiple map=m1l2a`, so `pfnTouch` did not reach the retail trigger and the hint did not appear.

## Frame stats
```
final.png: (640, 480) black=8.9% mean=(41, 33, 24)
```

## OSReport (key)
```
19:25:19:065 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
34:25:19:101 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=mohaa
35:25:19:102 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: linked gamedir=mohaa detected=mohaa
40:25:19:103 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
67:25:19:151 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
84:25:19:550 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Program args: xash xash -dev 2 -log -game mohaa -gcnewgame -gcworldrender -gcmap m1l2a -gclistenserver m1l2a -gcfullphysics -gcchangelevel m1l2a -gcplayerinput -width 320 -height 240
117:25:19:567 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: released unused nodes reserve 256 Kb
118:25:19:567 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: released unused submodels reserve 16 Kb
170:25:19:605 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: heap mark stage=client_local_init_ready used=865824 free=246400 unclaimed=319488 avail=565888
200:25:19:634 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=876272 free=235952 unclaimed=319488 avail=555440
207:25:19:669 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: renderer screen map ready
210:25:19:670 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=876272 free=235952 unclaimed=319488 avail=555440
219:25:19:671 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: heap mark stage=renderer_images_ready used=876408 free=235816 unclaimed=319488 avail=555304
223:25:19:673 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: heap mark stage=renderer_init_ready used=974800 free=137424 unclaimed=319488 avail=456912
230:25:19:678 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: heap mark stage=client_video_init_ready used=978552 free=133672 unclaimed=319488 avail=453160
253:25:19:682 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=982344 free=129880 unclaimed=319488 avail=449368
261:25:19:690 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: gcmap lookup begin
262:25:19:690 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: queue map m1l2a
263:25:19:690 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: direct map begin
270:25:19:691 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: G326 pre-map client ensure begin
273:25:19:691 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: released unused nodes reserve 256 Kb
274:25:19:692 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: released unused submodels reserve 16 Kb
276:25:19:692 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: freed 0 menu/UI textures for map load
277:25:19:692 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: GX HUD/menu slabs released for map load
298:25:19:696 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: titles init skipped for gcmap smoke route
303:25:19:699 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: client edicts using static gcmap bootstrap tables
393:25:19:706 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: heap mark stage=client_module_ready used=1004232 free=79320 unclaimed=348160 avail=427480
395:25:19:707 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1004232 free=79320 unclaimed=348160 avail=427480
396:25:19:707 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: G326 pre-map client ensure ready
397:25:19:707 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: freed 0 menu/UI textures for map load
398:25:19:707 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: GX HUD/menu slabs released for map load
399:25:19:707 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: G326 keep client across newgame map load
400:25:19:707 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: client subsystems trimmed for map load
404:25:19:708 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: renderer trim for map load
405:25:19:708 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: present buf released map load
421:25:19:711 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: map load cfg skipped
424:25:19:714 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: pre-spawn mem map set
437:25:19:715 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: present buf released map load
441:25:19:716 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: server string arena spill dropped for map reload
454:25:19:717 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: pre-spawn map buffer prepared for m1l2a
457:25:19:717 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:18] Xash3D GameCube: server string arena spill dropped for map reload
468:25:20:834 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:19] Xash3D GameCube: map load compact (no lighting, miptex headers only) 3.14 Mb 竊 1.96 Mb (G154 disc LM) +align
513:25:21:067 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:20] Xash3D GameCube: world surfedges copied 230.03 Kb to map tail
525:25:21:070 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:20] Xash3D GameCube: releasing gcmap BSP staging 1.96 Mb before surfaces
572:25:21:148 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:20] Xash3D GameCube: map skyname early mohnight1 (before CapFaces)
648:25:23:407 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:22] Xash3D GameCube: freed 126 menu/UI textures for map load
649:25:23:407 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:22] Xash3D GameCube: GX HUD/menu slabs released for map load
1315:25:23:991 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:23] Xash3D GameCube: resource sync skipped for local map route
1321:25:23:999 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:23] Xash3D GameCube: renderer restore after map load
1322:25:23:999 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:23] Xash3D GameCube: map loaded m1l2a
1323:25:23:999 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1325:25:24:000 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:23] Xash3D GameCube: budget moved entity text to map leftover (46.10 Kb), entity reserve returned, heap free 201.74 Kb
1327:25:24:011 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:23] Warning: Xash3D GameCube: direct-map player unavailable map=m1l2a
1331:25:24:012 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1333:25:24:012 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:23] Xash3D GameCube: direct map ready
1336:25:24:013 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:23] Xash3D GameCube: freed 126 menu/UI textures for map load
1337:25:24:013 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:23] Xash3D GameCube: GX HUD/menu slabs released for map load
1340:25:24:013 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:23] Xash3D GameCube: freed 126 menu/UI textures for map load
1341:25:24:014 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:23] Xash3D GameCube: GX HUD/menu slabs released for map load
1345:25:24:014 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:25:23] Xash3D GameCube: map loaded m1l2a
```

- Full Dolphin log: `media/playtests/screenshots/20261124-042517-m1l2a-door-hint-trigger-touch2/dolphin.log.gz`
