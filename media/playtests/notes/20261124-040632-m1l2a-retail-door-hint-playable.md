# MOHAA Probe m1l2a-retail-door-hint-playable — 20261124-040632

- ISO: `/tmp/mohaa-door-hint/mohaa-m1l2a-door-hint-playable.iso`
- Route: `m1l2a-retail-door-hint-playable`
- Duration cap: 60s
- Repo: `893bf3e037`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261124-040632-m1l2a-retail-door-hint-playable/`
- Periodic guest frames: 15 screenshots in `media/playtests/screenshots/20261124-040632-m1l2a-retail-door-hint-playable/frames/`
- Video: `media/playtests/videos/20261124-040632-m1l2a-retail-door-hint-playable-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: 893bf3e037. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-door-hint/mohaa-m1l2a-door-hint-playable.iso (SHA-256 1bb6e4f9ddcaff5b1860020cb43ec1506d409de2a045ffd5b0c5bb1bb8109164). Full-physics newgame/changelevel m1l2a route with staged GC door hint listener. The game reached the map with a local player and weapon HUD and continued presenting frames without a DSI. No controller input was sent, so this capture does not show a door trigger or the hint itself.

## Frame stats
```
final.png: (640, 480) black=8.9% mean=(40, 32, 23)
```

## OSReport (key)
```
26:06:34:173 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
41:06:34:210 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=mohaa
42:06:34:210 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: linked gamedir=mohaa detected=mohaa
47:06:34:211 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
74:06:34:259 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
91:06:34:659 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Program args: xash xash -dev 2 -log -game mohaa -gcnewgame -gcworldrender -gcmap m1l2a -gclistenserver m1l2a -gcfullphysics -gcchangelevel m1l2a -gcplayerinput -width 320 -height 240
124:06:34:683 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: released unused nodes reserve 256 Kb
125:06:34:683 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: released unused submodels reserve 16 Kb
177:06:34:731 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: heap mark stage=client_local_init_ready used=865824 free=246400 unclaimed=319488 avail=565888
207:06:34:765 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=876272 free=235952 unclaimed=319488 avail=555440
214:06:34:808 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: renderer screen map ready
217:06:34:809 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=876272 free=235952 unclaimed=319488 avail=555440
226:06:34:810 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: heap mark stage=renderer_images_ready used=876408 free=235816 unclaimed=319488 avail=555304
230:06:34:812 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: heap mark stage=renderer_init_ready used=974800 free=137424 unclaimed=319488 avail=456912
237:06:34:818 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: heap mark stage=client_video_init_ready used=978552 free=133672 unclaimed=319488 avail=453160
260:06:34:824 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=982344 free=129880 unclaimed=319488 avail=449368
268:06:34:833 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: gcmap lookup begin
269:06:34:833 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: queue map m1l2a
270:06:34:833 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: direct map begin
277:06:34:834 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: G326 pre-map client ensure begin
280:06:34:835 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: released unused nodes reserve 256 Kb
281:06:34:835 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: released unused submodels reserve 16 Kb
283:06:34:836 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: freed 0 menu/UI textures for map load
284:06:34:836 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: GX HUD/menu slabs released for map load
305:06:34:842 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: titles init skipped for gcmap smoke route
310:06:34:848 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: client edicts using static gcmap bootstrap tables
400:06:34:861 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: heap mark stage=client_module_ready used=1004232 free=79320 unclaimed=348160 avail=427480
402:06:34:861 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1004232 free=79320 unclaimed=348160 avail=427480
403:06:34:861 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: G326 pre-map client ensure ready
404:06:34:861 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: freed 0 menu/UI textures for map load
405:06:34:861 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: GX HUD/menu slabs released for map load
406:06:34:862 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: G326 keep client across newgame map load
407:06:34:862 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: client subsystems trimmed for map load
411:06:34:863 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: renderer trim for map load
412:06:34:863 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: present buf released map load
428:06:34:869 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: map load cfg skipped
431:06:34:873 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: pre-spawn mem map set
444:06:34:876 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: present buf released map load
448:06:34:877 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: server string arena spill dropped for map reload
461:06:34:879 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: pre-spawn map buffer prepared for m1l2a
464:06:34:880 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:34] Xash3D GameCube: server string arena spill dropped for map reload
475:06:35:944 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:35] Xash3D GameCube: map load compact (no lighting, miptex headers only) 3.14 Mb 竊 1.96 Mb (G154 disc LM) +align
520:06:36:178 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:36] Xash3D GameCube: world surfedges copied 230.03 Kb to map tail
532:06:36:181 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:36] Xash3D GameCube: releasing gcmap BSP staging 1.96 Mb before surfaces
579:06:36:261 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:36] Xash3D GameCube: map skyname early mohnight1 (before CapFaces)
655:06:38:515 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:38] Xash3D GameCube: freed 126 menu/UI textures for map load
656:06:38:515 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:38] Xash3D GameCube: GX HUD/menu slabs released for map load
1322:06:39:101 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:39] Xash3D GameCube: resource sync skipped for local map route
1328:06:39:108 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:39] Xash3D GameCube: renderer restore after map load
1329:06:39:108 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:39] Xash3D GameCube: map loaded m1l2a
1330:06:39:108 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1332:06:39:109 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:39] Xash3D GameCube: budget moved entity text to map leftover (46.10 Kb), entity reserve returned, heap free 201.74 Kb
1334:06:39:119 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:39] Warning: Xash3D GameCube: direct-map player unavailable map=m1l2a
1338:06:39:120 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1340:06:39:121 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:39] Xash3D GameCube: direct map ready
1343:06:39:121 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:39] Xash3D GameCube: freed 126 menu/UI textures for map load
1344:06:39:121 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:39] Xash3D GameCube: GX HUD/menu slabs released for map load
1347:06:39:122 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:39] Xash3D GameCube: freed 126 menu/UI textures for map load
1348:06:39:122 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:39] Xash3D GameCube: GX HUD/menu slabs released for map load
1352:06:39:123 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:06:39] Xash3D GameCube: map loaded m1l2a
```

- Full Dolphin log: `media/playtests/screenshots/20261124-040632-m1l2a-retail-door-hint-playable/dolphin.log.gz`
