# Probe mohaa-garand-native-cmpr — 20261122-152046

- ISO: `/tmp/mohaa-garand-native-cmpr-20261122/out/mohaa-garand-native-cmpr.iso`
- Route: `mohaa-garand-native-cmpr`
- Duration cap: 45s
- Repo: `8d29747887`
- Engine DOL source commit: `52f7ae8bbb`
- DOL SHA-256: `00058c7af6468840062e39d0ef5536af6ce2d5537f188e7051b1cdda29bcd17e`
- ISO SHA-256: `93d60d5bbca2d0c544a78c2c8a2421d0736647b097306c1665f1adefd4c7a798`
- Dolphin revision: `eeaafed88a`
- Dolphin: OpenGL, GameCube progressive video, MMU on, Accurate CPU Cache on, 640x480 capture, 45s cap
- Evidence is from Dolphin only; no physical GameCube result is claimed.
- Shots: `playtests/screenshots/20261122-152046-mohaa-garand-native-cmpr/`

## Result

The standalone CMPR encoder output decodes to the expected atlas on the host. The runtime capture
reaches `map loaded m1l2a` and `newgame world render ready` at 45.79 FPS, with the rifle visible,
but the rifle remains blue/black. The log includes the `gc_studio/v_garand.mdl` read, skin setup,
and first-person draw pass; it does not contain a per-model confirmation that the baked CMPR bind
was selected. The runtime material problem remains unresolved.

## Frame stats
```
final.png: (640, 480) black=8.7% mean=(57, 44, 36)
```

## OSReport (key)
```
37:20:48:504 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
38:20:48:504 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
65:20:48:604 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
92:20:49:070 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Program args: xash xash -dev 2 -log -game mohaa -gcworldrender -gclistenserver m1l2a -gcmap m1l2a -gcvideo prog -gcplayerinput -width 320 -height 240
138:20:49:111 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: released unused nodes reserve 256 Kb
139:20:49:111 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: released unused submodels reserve 16 Kb
191:20:49:181 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: heap mark stage=client_local_init_ready used=875264 free=239552 unclaimed=929792 avail=1169344
221:20:49:234 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=885712 free=229104 unclaimed=929792 avail=1158896
228:20:49:296 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: renderer screen map ready
231:20:49:297 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=885712 free=229104 unclaimed=929792 avail=1158896
240:20:49:300 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: heap mark stage=renderer_images_ready used=885848 free=228968 unclaimed=929792 avail=1158760
244:20:49:305 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: heap mark stage=renderer_init_ready used=984240 free=130576 unclaimed=929792 avail=1060368
251:20:49:314 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: heap mark stage=client_video_init_ready used=987992 free=126824 unclaimed=929792 avail=1056616
274:20:49:321 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=991784 free=123032 unclaimed=929792 avail=1052824
282:20:49:330 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: gcmap lookup begin
283:20:49:330 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: queue map m1l2a
284:20:49:330 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: direct map begin
286:20:49:331 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: freed 0 menu/UI textures for map load
287:20:49:331 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: GX HUD/menu slabs released for map load
289:20:49:333 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: sound trimmed for map load
290:20:49:333 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: client subsystems trimmed for map load
299:20:49:336 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: renderer trim for map load
300:20:49:336 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: present buf released map load
316:20:49:344 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: map load cfg skipped
319:20:49:346 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: pre-spawn mem map set
333:20:49:348 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: present buf released map load
335:20:49:349 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: server string arena spill dropped for map reload
344:20:49:350 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: pre-spawn map buffer prepared for m1l2a
348:20:49:350 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:48] Xash3D GameCube: server string arena spill dropped for map reload
357:20:50:055 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:49] Xash3D GameCube: map load compact (no lighting, miptex headers only) 3.09 Mb 竊 1.91 Mb (G154 disc LM) +align
401:20:50:296 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:49] Xash3D GameCube: world surfedges copied 230.03 Kb to map tail
413:20:50:299 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:49] Xash3D GameCube: releasing gcmap BSP staging 1.91 Mb before surfaces
528:20:52:547 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:52] Xash3D GameCube: freed 126 menu/UI textures for map load
529:20:52:547 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:52] Xash3D GameCube: GX HUD/menu slabs released for map load
537:20:52:627 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:52] PM_WorldMesh: maps/m1l2a.mcol, 0 brushes, 146 terrain patches, 7870 patch triangles, 243960 bytes in the map arena
1310:20:53:390 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: resource sync skipped for local map route
1316:20:53:405 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: renderer restore after map load
1317:20:53:405 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: map loaded m1l2a
1318:20:53:406 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1323:20:53:409 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1325:20:53:410 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: direct map ready
1328:20:53:411 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: skip startup video scan for gcmap route
1329:20:53:412 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: gcmap smoke frames begin
1336:20:53:416 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: gcmap smoke frames ready
1339:20:53:418 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=1990968 free=37256 unclaimed=16384 avail=53640
1340:20:53:418 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: solo listenserver active map=m1l2a (gcmap tip)
1354:20:53:432 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: livemap armed=0 (file absent)
1358:20:53:508 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: released unused nodes reserve 256 Kb
1359:20:53:508 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: released unused submodels reserve 16 Kb
1361:20:53:509 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: freed 126 menu/UI textures for map load
1362:20:53:509 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: GX HUD/menu slabs released for map load
1383:20:53:516 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: titles init skipped for gcmap smoke route
1388:20:53:525 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: client edicts using static gcmap bootstrap tables
1474:20:53:539 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: heap mark stage=client_module_ready used=1726040 free=302184 unclaimed=16384 avail=318568
1476:20:53:539 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1726040 free=302184 unclaimed=16384 avail=318568
1503:20:53:605 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: serverdata HUD vidinit deferred for local map route
1504:20:53:607 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: client edicts capped for map route max=460 requested=460
1505:20:53:607 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: serverdata map CRC skipped for local map route
1507:20:53:610 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: serverdata keep menu inactive for local map route
1513:20:53:615 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:20:53] Xash3D GameCube: client edicts using static gcmap bootstrap tables
```
