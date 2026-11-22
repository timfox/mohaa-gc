# Probe mohaa-garand-aspect-ratio-desktop — 20261122-150547

- ISO: `/tmp/mohaa-garand-refresh-20261122/out/mohaa-garand-refresh.iso`
- Route: `mohaa-garand-aspect-ratio-desktop`
- Duration cap: 45s
- Repo: `1f73df3bf8`
- Engine: `52f7ae8bbb`
- Shots: `playtests/screenshots/20261122-150547-mohaa-garand-aspect-ratio-desktop/`

## Frame stats
```
final.png: (640, 480) black=8.7% mean=(58, 49, 33)
```

The captured model is the retail-derived `gc_studio/v_garand.mdl` (86,968 bytes); runtime logs show it loaded as a 256x128 skin and the map reached `newgame world render ready`. The frame overlay reports about 45 FPS. The converted atlas decodes correctly on the host, but its colors render as green/magenta bands in-game. Adding a GoldSrc palette count was investigated and rejected: this Xash studio texture path expects the raw 768-byte RGB palette immediately after the indexed pixels. The GX/model color issue remains open.

## OSReport (key)
```
37:05:49:731 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
38:05:49:732 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
65:05:49:829 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
92:05:50:316 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Program args: xash xash -dev 2 -log -game mohaa -gcworldrender -gclistenserver m1l2a -gcmap m1l2a -gcvideo prog -gcplayerinput -width 320 -height 240 
141:05:50:358 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: released unused nodes reserve 256 Kb
142:05:50:358 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: released unused submodels reserve 16 Kb
194:05:50:451 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: heap mark stage=client_local_init_ready used=875264 free=239552 unclaimed=929792 avail=1169344
224:05:50:514 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=885712 free=229104 unclaimed=929792 avail=1158896
231:05:50:584 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: renderer screen map ready
234:05:50:586 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=885712 free=229104 unclaimed=929792 avail=1158896
243:05:50:589 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: heap mark stage=renderer_images_ready used=885848 free=228968 unclaimed=929792 avail=1158760
247:05:50:593 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: heap mark stage=renderer_init_ready used=984240 free=130576 unclaimed=929792 avail=1060368
254:05:50:606 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: heap mark stage=client_video_init_ready used=987992 free=126824 unclaimed=929792 avail=1056616
277:05:50:617 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=991784 free=123032 unclaimed=929792 avail=1052824
285:05:50:634 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: gcmap lookup begin
286:05:50:635 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: queue map m1l2a
287:05:50:635 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: direct map begin
289:05:50:636 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: freed 0 menu/UI textures for map load
290:05:50:637 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: GX HUD/menu slabs released for map load
292:05:50:640 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: sound trimmed for map load
293:05:50:640 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: client subsystems trimmed for map load
302:05:50:645 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: renderer trim for map load
303:05:50:645 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: present buf released map load
319:05:50:652 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: map load cfg skipped
322:05:50:657 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: pre-spawn mem map set
336:05:50:660 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: present buf released map load
338:05:50:661 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: server string arena spill dropped for map reload
347:05:50:662 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: pre-spawn map buffer prepared for m1l2a
351:05:50:663 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:49] Xash3D GameCube: server string arena spill dropped for map reload
360:05:51:360 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:50] Xash3D GameCube: map load compact (no lighting, miptex headers only) 3.09 Mb 竊 1.91 Mb (G154 disc LM) +align
404:05:51:620 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:50] Xash3D GameCube: world surfedges copied 230.03 Kb to map tail
416:05:51:626 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:50] Xash3D GameCube: releasing gcmap BSP staging 1.91 Mb before surfaces
531:05:53:849 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:53] Xash3D GameCube: freed 126 menu/UI textures for map load
532:05:53:849 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:53] Xash3D GameCube: GX HUD/menu slabs released for map load
540:05:53:930 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:53] PM_WorldMesh: maps/m1l2a.mcol, 0 brushes, 146 terrain patches, 7870 patch triangles, 243960 bytes in the map arena
1313:05:54:680 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: resource sync skipped for local map route
1319:05:54:692 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: renderer restore after map load
1320:05:54:692 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: map loaded m1l2a
1321:05:54:692 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1326:05:54:694 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1328:05:54:694 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: direct map ready
1331:05:54:694 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: skip startup video scan for gcmap route
1332:05:54:695 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: gcmap smoke frames begin
1339:05:54:698 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: gcmap smoke frames ready
1342:05:54:698 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=1990968 free=37256 unclaimed=16384 avail=53640
1343:05:54:698 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: solo listenserver active map=m1l2a (gcmap tip)
1354:05:54:710 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: livemap armed=0 (file absent)
1358:05:54:760 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: released unused nodes reserve 256 Kb
1359:05:54:760 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: released unused submodels reserve 16 Kb
1361:05:54:761 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: freed 126 menu/UI textures for map load
1362:05:54:761 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: GX HUD/menu slabs released for map load
1383:05:54:770 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: titles init skipped for gcmap smoke route
1388:05:54:776 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: client edicts using static gcmap bootstrap tables
1474:05:54:785 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: heap mark stage=client_module_ready used=1726040 free=302184 unclaimed=16384 avail=318568
1476:05:54:785 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1726040 free=302184 unclaimed=16384 avail=318568
1503:05:54:848 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: serverdata HUD vidinit deferred for local map route
1504:05:54:848 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: client edicts capped for map route max=460 requested=460
1505:05:54:849 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: serverdata map CRC skipped for local map route
1507:05:54:850 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: serverdata keep menu inactive for local map route
1513:05:54:852 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [15:05:54] Xash3D GameCube: client edicts using static gcmap bootstrap tables
```
