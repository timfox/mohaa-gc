# Probe m1l2a-door-hint-trigger-touch-after-engine-fix — 20261124-044428

- ISO: `/dev/shm/mohaa-door-hint-engine-out/mohaa-m1l2a-door-hint.iso`
- Route: `m1l2a-door-hint-trigger-touch-after-engine-fix`
- Duration cap: 40s
- Repo: `bd6a4241d7`
- Engine: `db73d0d126`
- Shots: `playtests/screenshots/20261124-044428-m1l2a-door-hint-trigger-touch-after-engine-fix/`

MOHAA GameCube full-physics probe with matching 256/32 engine and MOHAA SDK layouts. It crashed during map loading, before controller interaction.

## Frame stats
```

- Full Dolphin log: `media/playtests/screenshots/20261124-044428-m1l2a-door-hint-trigger-touch-after-engine-fix/dolphin.log.gz`
- Video: `media/playtests/videos/20261124-044428-m1l2a-door-hint-trigger-touch-after-engine-fix-silent.mkv` (39.9s; failed map-load screen)

## Result

The engine passed initialization but exhausted the engine zone during `Mod_LoadWorld`: a 508-byte allocation failed with 144 bytes free, before `map loaded`. No gameplay or door interaction was reached. The 39.9-second Matroska capture shows the failed load. `/tmp` refused the controller driver's log write due to per-user quota, so no controller input is verified.
final.png: (640, 480) black=70.7% mean=(34, 0, 0)
```

## OSReport (key)
```
19:44:29:855 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
34:44:29:891 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=mohaa
35:44:29:891 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: linked gamedir=mohaa detected=mohaa
40:44:29:893 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
67:44:29:941 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
84:44:30:342 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Program args: xash xash -dev 2 -log -game mohaa -gcnewgame -gcworldrender -gcmap m1l2a -gclistenserver m1l2a -gcfullphysics -gcchangelevel m1l2a -gcplayerinput -width 320 -height 240
118:44:30:361 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: released unused submodels reserve 16 Kb
171:44:30:428 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: heap mark stage=client_local_init_ready used=707464 free=88 unclaimed=0 avail=88
201:44:30:461 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=707072 free=480 unclaimed=0 avail=480
208:44:30:500 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: renderer screen map ready
211:44:30:502 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=707072 free=480 unclaimed=0 avail=480
220:44:30:503 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: heap mark stage=renderer_images_ready used=707208 free=344 unclaimed=0 avail=344
224:44:30:505 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: heap mark stage=renderer_init_ready used=707288 free=264 unclaimed=0 avail=264
231:44:30:514 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: heap mark stage=client_video_init_ready used=707432 free=120 unclaimed=0 avail=120
254:44:30:524 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=707432 free=120 unclaimed=0 avail=120
262:44:30:534 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: gcmap lookup begin
263:44:30:534 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: queue map m1l2a
264:44:30:534 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: direct map begin
273:44:30:536 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: G326 pre-map client ensure begin
277:44:30:537 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: freed 0 menu/UI textures for map load
278:44:30:537 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: GX HUD/menu slabs released for map load
299:44:30:542 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: titles init skipped for gcmap smoke route
304:44:30:547 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: client edicts using static gcmap bootstrap tables
394:44:30:566 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: heap mark stage=client_module_ready used=707432 free=120 unclaimed=0 avail=120
396:44:30:566 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=707432 free=120 unclaimed=0 avail=120
397:44:30:566 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: G326 pre-map client ensure ready
398:44:30:566 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: freed 0 menu/UI textures for map load
399:44:30:566 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: GX HUD/menu slabs released for map load
400:44:30:567 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: G326 keep client across newgame map load
401:44:30:567 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: client subsystems trimmed for map load
403:44:30:567 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: freed 0 menu/UI textures for map load
404:44:30:568 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: GX HUD/menu slabs released for map load
406:44:30:572 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: GX HUD/menu slabs released for map load
417:44:30:576 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: map load cfg skipped
420:44:30:578 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: pre-spawn mem map set
433:44:30:580 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: present buf released map load
436:44:30:581 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: server string arena spill dropped for map reload
450:44:30:583 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: pre-spawn map buffer prepared for m1l2a
453:44:30:583 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: server string arena spill dropped for map reload
463:44:30:586 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:44:29] Xash3D GameCube: GX HUD/menu slabs released for map load
```
