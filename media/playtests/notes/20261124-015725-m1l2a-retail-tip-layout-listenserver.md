# MOHAA Probe m1l2a-retail-tip-layout-listenserver — 20261124-015725

- ISO: `/tmp/mohaa-hud-refine/out/mohaa-compass-layout-listenserver.iso`
- Route: `m1l2a-retail-tip-layout-listenserver`
- Duration cap: 45s
- Repo: `8d0887dca6`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261124-015725-m1l2a-retail-tip-layout-listenserver/`
- Periodic guest frames: 40 screenshots in `media/playtests/screenshots/20261124-015725-m1l2a-retail-tip-layout-listenserver/frames/`

MOHAA GameCube playtest. Repo HEAD: 8d0887dca6. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-hud-refine/out/mohaa-compass-layout-listenserver.iso (SHA-256 630262fdf179a4ec5650e78f69c549b9e97c0de5b9d1908b31f617a44c1e0648). Isolated Dolphin probe of enlarged MOHAA compass and retail door-tip placement. Uses current GameCube DOL and a probe-only m1l2a script invoking hint_door; listenserver starts the local player for HUD rendering.

## Frame stats
```
final.png: (640, 480) black=9.1% mean=(53, 53, 45)
```

## OSReport (key)
```
32:57:27:642 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
43:57:27:705 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
44:57:27:705 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:27] Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
49:57:27:708 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
71:57:27:783 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:27] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
94:57:28:397 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:27] Program args: xash xash -dev 2 -log -game mohaa -gcmap m1l2a -gclistenserver m1l2a -gcvideo prog -gcplayerinput -width 320 -height 240
136:57:28:451 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:27] Xash3D GameCube: released unused nodes reserve 256 Kb
137:57:28:451 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:27] Xash3D GameCube: released unused submodels reserve 16 Kb
189:57:28:529 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:27] Xash3D GameCube: heap mark stage=client_local_init_ready used=874928 free=236528 unclaimed=643072 avail=879600
219:57:28:606 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=885376 free=226080 unclaimed=643072 avail=869152
226:57:28:693 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: renderer screen map ready
229:57:28:696 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=885376 free=226080 unclaimed=643072 avail=869152
238:57:28:699 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: heap mark stage=renderer_images_ready used=885512 free=225944 unclaimed=643072 avail=869016
241:57:28:704 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: heap mark stage=renderer_init_ready used=885592 free=225864 unclaimed=643072 avail=868936
248:57:28:714 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: heap mark stage=client_video_init_ready used=889336 free=222120 unclaimed=643072 avail=865192
271:57:28:722 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=893128 free=218328 unclaimed=643072 avail=861400
279:57:28:733 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: gcmap lookup begin
280:57:28:733 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: queue map m1l2a
281:57:28:733 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: direct map begin
283:57:28:735 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: freed 0 menu/UI textures for map load
284:57:28:735 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: GX HUD/menu slabs released for map load
286:57:28:739 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: sound trimmed for map load
287:57:28:739 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: client subsystems trimmed for map load
296:57:28:743 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: renderer trim for map load
297:57:28:743 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: present buf released map load
313:57:28:754 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: map load cfg skipped
316:57:28:760 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: pre-spawn mem map set
330:57:28:764 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: present buf released map load
332:57:28:764 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: server string arena spill dropped for map reload
341:57:28:767 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: pre-spawn map buffer prepared for m1l2a
345:57:28:767 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:28] Xash3D GameCube: server string arena spill dropped for map reload
356:57:29:825 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:29] Xash3D GameCube: map load compact (no lighting, miptex headers only) 3.14 Mb 竊 1.96 Mb (G154 disc LM) +align
404:57:30:093 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:29] Xash3D GameCube: world surfedges copied 230.03 Kb to map tail
416:57:30:099 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:29] Xash3D GameCube: releasing gcmap BSP staging 1.96 Mb before surfaces
526:57:32:386 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:31] Xash3D GameCube: freed 126 menu/UI textures for map load
527:57:32:386 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:31] Xash3D GameCube: GX HUD/menu slabs released for map load
1261:57:33:058 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: resource sync skipped for local map route
1267:57:33:067 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: renderer restore after map load
1268:57:33:067 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: map loaded m1l2a
1269:57:33:067 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1271:57:33:068 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: budget moved entity text to map leftover (46.10 Kb), entity reserve returned, heap free 370.82 Kb
1276:57:33:082 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1278:57:33:082 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: direct map ready
1281:57:33:083 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: skip startup video scan for gcmap route
1282:57:33:083 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: gcmap smoke frames begin
1283:57:33:084 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: gcmap smoke frames ready
1286:57:33:085 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=1374808 free=248648 unclaimed=131072 avail=379720
1287:57:33:085 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: solo listenserver active map=m1l2a (gcmap tip)
1302:57:33:102 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: livemap armed=0 (file absent)
1311:57:33:176 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: released unused nodes reserve 256 Kb
1312:57:33:176 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: released unused submodels reserve 16 Kb
1313:57:33:177 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: freed 126 menu/UI textures for map load
1314:57:33:177 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: GX HUD/menu slabs released for map load
1335:57:33:184 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: titles init skipped for gcmap smoke route
1340:57:33:192 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: client edicts using static gcmap bootstrap tables
1430:57:33:209 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: heap mark stage=client_module_ready used=1109400 free=514056 unclaimed=131072 avail=645128
1432:57:33:209 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1109400 free=514056 unclaimed=131072 avail=645128
1472:57:33:299 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: serverdata HUD vidinit deferred for local map route
1473:57:33:300 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: client edicts capped for map route max=460 requested=460
1474:57:33:301 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:57:32] Xash3D GameCube: serverdata map CRC skipped for local map route
```

- Full Dolphin log: `media/playtests/screenshots/20261124-015725-m1l2a-retail-tip-layout-listenserver/dolphin.log.gz`
