# MOHAA Probe m1l2a-door-hint-controller — 20261124-041356

- ISO: `/tmp/mohaa-door-hint/mohaa-m1l2a-door-hint-playable.iso`
- Route: `m1l2a-door-hint-controller`
- Duration cap: 45s
- Repo: `unknown`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261124-041356-m1l2a-door-hint-controller/`
- Periodic guest frames: 14 screenshots in `media/playtests/screenshots/20261124-041356-m1l2a-door-hint-controller/frames/`
- Video: `media/playtests/videos/20261124-041356-m1l2a-door-hint-controller-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: f465697668. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-door-hint/mohaa-m1l2a-door-hint-playable.iso (SHA-256 1bb6e4f9ddcaff5b1860020cb43ec1506d409de2a045ffd5b0c5bb1bb8109164). Full-physics newgame/changelevel m1l2a route with scripted GC pad movement and USE presses. Starting after ten seconds, the driver repeated: forward for three seconds, turn right for 0.8 seconds, press USE for 0.25 seconds, then forward for three seconds and press USE for 0.25 seconds. The final frame is at a gate, but the log only reports the spawn `trigger_once` plus `world interaction skip classname=trigger_multiple`; it does not report a locked-door trigger touch, and no hint appeared. Full timestamped pad commands are in `/tmp/mohaa-door-hint/pad-input.log`.

## Frame stats
```
final.png: (640, 480) black=8.9% mean=(47, 38, 25)
```

## OSReport (key)
```
26:13:59:262 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
41:13:59:302 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=mohaa
42:13:59:302 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: linked gamedir=mohaa detected=mohaa
47:13:59:304 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
74:13:59:349 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
91:13:59:754 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Program args: xash xash -dev 2 -log -game mohaa -gcnewgame -gcworldrender -gcmap m1l2a -gclistenserver m1l2a -gcfullphysics -gcchangelevel m1l2a -gcplayerinput -width 320 -height 240
124:13:59:792 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: released unused nodes reserve 256 Kb
125:13:59:792 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: released unused submodels reserve 16 Kb
177:13:59:849 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: heap mark stage=client_local_init_ready used=865824 free=246400 unclaimed=319488 avail=565888
207:13:59:901 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=876272 free=235952 unclaimed=319488 avail=555440
214:13:59:970 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: renderer screen map ready
217:13:59:971 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=876272 free=235952 unclaimed=319488 avail=555440
226:13:59:972 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: heap mark stage=renderer_images_ready used=876408 free=235816 unclaimed=319488 avail=555304
230:13:59:976 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: heap mark stage=renderer_init_ready used=974800 free=137424 unclaimed=319488 avail=456912
237:13:59:983 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: heap mark stage=client_video_init_ready used=978552 free=133672 unclaimed=319488 avail=453160
260:13:59:991 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=982344 free=129880 unclaimed=319488 avail=449368
268:14:00:004 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: gcmap lookup begin
269:14:00:004 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: queue map m1l2a
270:14:00:005 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: direct map begin
277:14:00:006 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: G326 pre-map client ensure begin
280:14:00:006 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: released unused nodes reserve 256 Kb
281:14:00:006 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: released unused submodels reserve 16 Kb
283:14:00:007 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: freed 0 menu/UI textures for map load
284:14:00:008 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: GX HUD/menu slabs released for map load
305:14:00:015 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: titles init skipped for gcmap smoke route
310:14:00:022 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: client edicts using static gcmap bootstrap tables
400:14:00:033 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: heap mark stage=client_module_ready used=1004232 free=79320 unclaimed=348160 avail=427480
402:14:00:033 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1004232 free=79320 unclaimed=348160 avail=427480
403:14:00:034 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: G326 pre-map client ensure ready
404:14:00:034 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: freed 0 menu/UI textures for map load
405:14:00:034 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: GX HUD/menu slabs released for map load
406:14:00:034 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: G326 keep client across newgame map load
407:14:00:035 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: client subsystems trimmed for map load
411:14:00:036 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: renderer trim for map load
412:14:00:036 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: present buf released map load
428:14:00:042 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: map load cfg skipped
431:14:00:045 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: pre-spawn mem map set
444:14:00:047 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: present buf released map load
448:14:00:047 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: server string arena spill dropped for map reload
461:14:00:049 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: pre-spawn map buffer prepared for m1l2a
464:14:00:049 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:13:59] Xash3D GameCube: server string arena spill dropped for map reload
475:14:01:090 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:14:00] Xash3D GameCube: map load compact (no lighting, miptex headers only) 3.14 Mb 竊 1.96 Mb (G154 disc LM) +align
520:14:01:336 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:14:01] Xash3D GameCube: world surfedges copied 230.03 Kb to map tail
532:14:01:342 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:14:01] Xash3D GameCube: releasing gcmap BSP staging 1.96 Mb before surfaces
579:14:01:414 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:14:01] Xash3D GameCube: map skyname early mohnight1 (before CapFaces)
655:14:03:663 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:14:03] Xash3D GameCube: freed 126 menu/UI textures for map load
656:14:03:663 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:14:03] Xash3D GameCube: GX HUD/menu slabs released for map load
1322:14:04:259 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:14:04] Xash3D GameCube: resource sync skipped for local map route
1328:14:04:266 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:14:04] Xash3D GameCube: renderer restore after map load
1329:14:04:266 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:14:04] Xash3D GameCube: map loaded m1l2a
1330:14:04:266 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1332:14:04:267 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:14:04] Xash3D GameCube: budget moved entity text to map leftover (46.10 Kb), entity reserve returned, heap free 201.74 Kb
1334:14:04:276 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:14:04] Warning: Xash3D GameCube: direct-map player unavailable map=m1l2a
1338:14:04:277 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1340:14:04:277 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:14:04] Xash3D GameCube: direct map ready
1343:14:04:278 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:14:04] Xash3D GameCube: freed 126 menu/UI textures for map load
1344:14:04:278 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:14:04] Xash3D GameCube: GX HUD/menu slabs released for map load
1347:14:04:278 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:14:04] Xash3D GameCube: freed 126 menu/UI textures for map load
1348:14:04:278 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:14:04] Xash3D GameCube: GX HUD/menu slabs released for map load
1352:14:04:278 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:14:04] Xash3D GameCube: map loaded m1l2a
```

- Full Dolphin log: `media/playtests/screenshots/20261124-041356-m1l2a-door-hint-controller/dolphin.log.gz`
