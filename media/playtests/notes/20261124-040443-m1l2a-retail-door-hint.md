# MOHAA Probe m1l2a-retail-door-hint — 20261124-040443

- ISO: `/tmp/mohaa-door-hint/mohaa-m1l2a-door-hint.iso`
- Route: `m1l2a-retail-door-hint`
- Duration cap: 60s
- Repo: `893bf3e037`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261124-040443-m1l2a-retail-door-hint/`
- Periodic guest frames: 14 screenshots in `media/playtests/screenshots/20261124-040443-m1l2a-retail-door-hint/frames/`
- Video: `media/playtests/videos/20261124-040443-m1l2a-retail-door-hint-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: 893bf3e037. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-door-hint/mohaa-m1l2a-door-hint.iso (SHA-256 009025b11ff8b7cde1dbc400dc0e5cbf6a167a5ce4c055f795577069dc3c2f57). Isolated full-physics m1l2a run using the staged GC door-hint listener; check whether the converted door trigger invokes the retail hint.

## Frame stats
```
final.png: (640, 480) black=88.1% mean=(3, 3, 2)
```

## OSReport (key)
```
26:04:46:676 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
39:04:46:745 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=mohaa
40:04:46:745 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: linked gamedir=mohaa detected=mohaa
45:04:46:748 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
70:04:46:782 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
87:04:47:161 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Program args: xash xash -dev 2 -log -game mohaa -gcnewgame -gcworldrender -gcmap m1l2a -gclistenserver m1l2a -gcfullphysics -gcplayerinput -width 320 -height 240
120:04:47:189 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: released unused nodes reserve 256 Kb
121:04:47:189 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: released unused submodels reserve 16 Kb
173:04:47:274 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: heap mark stage=client_local_init_ready used=865824 free=246400 unclaimed=319488 avail=565888
203:04:47:337 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=876272 free=235952 unclaimed=319488 avail=555440
210:04:47:382 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: renderer screen map ready
213:04:47:385 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=876272 free=235952 unclaimed=319488 avail=555440
222:04:47:388 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: heap mark stage=renderer_images_ready used=876408 free=235816 unclaimed=319488 avail=555304
226:04:47:394 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: heap mark stage=renderer_init_ready used=974800 free=137424 unclaimed=319488 avail=456912
233:04:47:409 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: heap mark stage=client_video_init_ready used=978552 free=133672 unclaimed=319488 avail=453160
256:04:47:420 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=982344 free=129880 unclaimed=319488 avail=449368
264:04:47:440 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: gcmap lookup begin
265:04:47:440 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: queue map m1l2a
266:04:47:440 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: direct map begin
273:04:47:443 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: G326 pre-map client ensure begin
276:04:47:444 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: released unused nodes reserve 256 Kb
277:04:47:444 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: released unused submodels reserve 16 Kb
279:04:47:445 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: freed 0 menu/UI textures for map load
280:04:47:445 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: GX HUD/menu slabs released for map load
301:04:47:454 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: titles init skipped for gcmap smoke route
306:04:47:462 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: client edicts using static gcmap bootstrap tables
396:04:47:472 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: heap mark stage=client_module_ready used=1004232 free=79320 unclaimed=348160 avail=427480
398:04:47:472 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1004232 free=79320 unclaimed=348160 avail=427480
399:04:47:472 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: G326 pre-map client ensure ready
400:04:47:473 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: freed 0 menu/UI textures for map load
401:04:47:473 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: GX HUD/menu slabs released for map load
402:04:47:473 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: G326 keep client across newgame map load
403:04:47:474 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: client subsystems trimmed for map load
409:04:47:474 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: renderer trim for map load
410:04:47:474 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: present buf released map load
426:04:47:479 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: map load cfg skipped
429:04:47:482 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: pre-spawn mem map set
443:04:47:483 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: present buf released map load
445:04:47:484 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: server string arena spill dropped for map reload
454:04:47:485 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: pre-spawn map buffer prepared for m1l2a
458:04:47:485 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:46] Xash3D GameCube: server string arena spill dropped for map reload
469:04:48:541 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:47] Xash3D GameCube: map load compact (no lighting, miptex headers only) 3.14 Mb 竊 1.96 Mb (G154 disc LM) +align
514:04:48:790 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:48] Xash3D GameCube: world surfedges copied 230.03 Kb to map tail
526:04:48:795 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:48] Xash3D GameCube: releasing gcmap BSP staging 1.96 Mb before surfaces
573:04:48:853 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:48] Xash3D GameCube: map skyname early mohnight1 (before CapFaces)
649:04:51:104 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:50] Xash3D GameCube: freed 126 menu/UI textures for map load
650:04:51:104 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:50] Xash3D GameCube: GX HUD/menu slabs released for map load
1316:04:51:697 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:51] Xash3D GameCube: resource sync skipped for local map route
1322:04:51:707 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:51] Xash3D GameCube: renderer restore after map load
1323:04:51:707 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:51] Xash3D GameCube: map loaded m1l2a
1324:04:51:707 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1326:04:51:708 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:51] Xash3D GameCube: budget moved entity text to map leftover (46.10 Kb), entity reserve returned, heap free 201.74 Kb
1328:04:51:719 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:51] Warning: Xash3D GameCube: direct-map player unavailable map=m1l2a
1332:04:51:720 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1334:04:51:720 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:51] Xash3D GameCube: direct map ready
1337:04:51:721 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:51] Xash3D GameCube: freed 126 menu/UI textures for map load
1338:04:51:722 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:51] Xash3D GameCube: GX HUD/menu slabs released for map load
1341:04:51:722 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:51] Xash3D GameCube: freed 126 menu/UI textures for map load
1342:04:51:722 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:51] Xash3D GameCube: GX HUD/menu slabs released for map load
1346:04:51:723 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:04:51] Xash3D GameCube: map loaded m1l2a
```

- Full Dolphin log: `media/playtests/screenshots/20261124-040443-m1l2a-retail-door-hint/dolphin.log.gz`
