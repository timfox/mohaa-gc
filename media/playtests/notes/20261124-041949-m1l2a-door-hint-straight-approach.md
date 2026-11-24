# MOHAA Probe m1l2a-door-hint-straight-approach — 20261124-041949

- ISO: `/tmp/mohaa-door-hint/mohaa-m1l2a-door-hint-playable.iso`
- Route: `m1l2a-door-hint-straight-approach`
- Duration cap: 45s
- Repo: `unknown`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261124-041949-m1l2a-door-hint-straight-approach/`
- Periodic guest frames: 14 screenshots in `media/playtests/screenshots/20261124-041949-m1l2a-door-hint-straight-approach/frames/`
- Video: `media/playtests/videos/20261124-041949-m1l2a-door-hint-straight-approach-silent.mp4`

MOHAA GameCube full-physics m1l2a baseline. The pad driver attached to a stale FIFO; `pad-input-straight.log` is empty, so no movement or USE input reached this run. Treat it as an uncontrolled map-load capture.

## Frame stats
```
final.png: (640, 480) black=8.9% mean=(40, 32, 23)
```

## OSReport (key)
```
26:19:51:246 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
41:19:51:284 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=mohaa
42:19:51:284 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: linked gamedir=mohaa detected=mohaa
47:19:51:285 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
74:19:51:332 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
91:19:51:732 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Program args: xash xash -dev 2 -log -game mohaa -gcnewgame -gcworldrender -gcmap m1l2a -gclistenserver m1l2a -gcfullphysics -gcchangelevel m1l2a -gcplayerinput -width 320 -height 240
124:19:51:749 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: released unused nodes reserve 256 Kb
125:19:51:749 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: released unused submodels reserve 16 Kb
177:19:51:787 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: heap mark stage=client_local_init_ready used=865824 free=246400 unclaimed=319488 avail=565888
207:19:51:814 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=876272 free=235952 unclaimed=319488 avail=555440
214:19:51:849 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: renderer screen map ready
217:19:51:850 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=876272 free=235952 unclaimed=319488 avail=555440
226:19:51:851 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: heap mark stage=renderer_images_ready used=876408 free=235816 unclaimed=319488 avail=555304
230:19:51:852 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: heap mark stage=renderer_init_ready used=974800 free=137424 unclaimed=319488 avail=456912
237:19:51:858 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: heap mark stage=client_video_init_ready used=978552 free=133672 unclaimed=319488 avail=453160
260:19:51:863 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=982344 free=129880 unclaimed=319488 avail=449368
268:19:51:870 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: gcmap lookup begin
269:19:51:870 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: queue map m1l2a
270:19:51:870 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: direct map begin
277:19:51:871 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: G326 pre-map client ensure begin
280:19:51:872 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: released unused nodes reserve 256 Kb
281:19:51:872 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: released unused submodels reserve 16 Kb
283:19:51:872 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: freed 0 menu/UI textures for map load
284:19:51:873 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: GX HUD/menu slabs released for map load
305:19:51:876 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: titles init skipped for gcmap smoke route
310:19:51:880 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: client edicts using static gcmap bootstrap tables
400:19:51:888 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: heap mark stage=client_module_ready used=1004232 free=79320 unclaimed=348160 avail=427480
402:19:51:888 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1004232 free=79320 unclaimed=348160 avail=427480
403:19:51:888 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: G326 pre-map client ensure ready
404:19:51:888 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: freed 0 menu/UI textures for map load
405:19:51:888 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: GX HUD/menu slabs released for map load
406:19:51:888 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: G326 keep client across newgame map load
407:19:51:889 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: client subsystems trimmed for map load
411:19:51:889 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: renderer trim for map load
412:19:51:889 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: present buf released map load
428:19:51:893 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: map load cfg skipped
431:19:51:895 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: pre-spawn mem map set
444:19:51:897 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: present buf released map load
448:19:51:897 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: server string arena spill dropped for map reload
461:19:51:899 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: pre-spawn map buffer prepared for m1l2a
464:19:51:899 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:51] Xash3D GameCube: server string arena spill dropped for map reload
475:19:53:016 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:52] Xash3D GameCube: map load compact (no lighting, miptex headers only) 3.14 Mb 竊 1.96 Mb (G154 disc LM) +align
520:19:53:250 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:53] Xash3D GameCube: world surfedges copied 230.03 Kb to map tail
532:19:53:253 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:53] Xash3D GameCube: releasing gcmap BSP staging 1.96 Mb before surfaces
579:19:53:330 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:53] Xash3D GameCube: map skyname early mohnight1 (before CapFaces)
655:19:55:588 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:55] Xash3D GameCube: freed 126 menu/UI textures for map load
656:19:55:588 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:55] Xash3D GameCube: GX HUD/menu slabs released for map load
1322:19:56:171 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:56] Xash3D GameCube: resource sync skipped for local map route
1328:19:56:179 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:56] Xash3D GameCube: renderer restore after map load
1329:19:56:179 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:56] Xash3D GameCube: map loaded m1l2a
1330:19:56:179 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1332:19:56:180 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:56] Xash3D GameCube: budget moved entity text to map leftover (46.10 Kb), entity reserve returned, heap free 201.74 Kb
1334:19:56:188 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:56] Warning: Xash3D GameCube: direct-map player unavailable map=m1l2a
1338:19:56:189 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1340:19:56:189 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:56] Xash3D GameCube: direct map ready
1343:19:56:190 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:56] Xash3D GameCube: freed 126 menu/UI textures for map load
1344:19:56:190 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:56] Xash3D GameCube: GX HUD/menu slabs released for map load
1347:19:56:190 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:56] Xash3D GameCube: freed 126 menu/UI textures for map load
1348:19:56:190 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:56] Xash3D GameCube: GX HUD/menu slabs released for map load
1352:19:56:191 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:19:56] Xash3D GameCube: map loaded m1l2a
```

- Full Dolphin log: `media/playtests/screenshots/20261124-041949-m1l2a-door-hint-straight-approach/dolphin.log.gz`
