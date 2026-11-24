# MOHAA Probe m1l2a-retailhud-lowmemfix — 20261124-135543

- ISO: `/home/tim/Desktop/mohaa-gc/retail/mohaa-m1l2a-clean-retest-20261124/mohaa-m1l2a-retailhud-lowmemfix.iso`
- Route: `m1l2a-retailhud-lowmemfix`
- Duration cap: 50s
- Repo: `72394218ad`
- Engine source: `retail/xash3d-gc-latest`, base `136de06` plus local changes (MOHAA 256/32 ABI and HUD low-memory fallback)
- Shots: `media/playtests/screenshots/20261124-135543-m1l2a-retailhud-lowmemfix/`
- Periodic guest frames: 7 screenshots in `media/playtests/screenshots/20261124-135543-m1l2a-retailhud-lowmemfix/frames/`
- Video: `media/playtests/videos/20261124-135543-m1l2a-retailhud-lowmemfix-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: 72394218ad. Engine source: /home/tim/Desktop/mohaa-gc/retail/xash3d-gc-latest (base commit 136de06 plus local changes). The Dolphin executable came from /run/media/tim/Expansion/xash3d-gc. ISO: /home/tim/Desktop/mohaa-gc/retail/mohaa-m1l2a-clean-retest-20261124/mohaa-m1l2a-retailhud-lowmemfix.iso (SHA-256 4b39c9501f2cf0acf4689b94231f3ecb4080ab9d0ee0843ca6a7cee9b91a9e09). Retest of MEM1-safe MOHAA compass decode using the source-sized retail HUD sprites.

## Frame stats
```
final.png: (640, 480) black=8.9% mean=(84, 79, 68)
```

## OSReport (key)
```
23:55:45:080 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
38:55:45:109 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=dod,mohaa
39:55:45:109 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:44] Xash3D GameCube: linked gamedir=mohaa detected=dod,mohaa
43:55:45:111 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
71:55:45:192 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:44] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
95:55:45:859 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:44] Program args: xash xash -dev 2 -log -game mohaa -gcnewgame -gcworldrender -gcmap m1l2a -gcfullphysics -gcchangelevel m1l2a -width 320 -height 240
141:55:45:883 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:44] Xash3D GameCube: released unused nodes reserve 256 Kb
142:55:45:883 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:44] Xash3D GameCube: released unused submodels reserve 16 Kb
194:55:45:920 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:44] Xash3D GameCube: heap mark stage=client_local_init_ready used=1177760 free=227008 unclaimed=466944 avail=693952
224:55:45:948 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=1188192 free=216576 unclaimed=466944 avail=683520
231:55:45:990 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: renderer screen map ready
234:55:45:991 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=1188192 free=216576 unclaimed=466944 avail=683520
243:55:45:992 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: heap mark stage=renderer_images_ready used=1188328 free=216440 unclaimed=466944 avail=683384
247:55:45:994 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: heap mark stage=renderer_init_ready used=1286720 free=118048 unclaimed=466944 avail=584992
252:55:46:000 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: screen init minimal for gcmap smoke route
254:55:46:000 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: heap mark stage=client_video_init_ready used=1290464 free=114304 unclaimed=466944 avail=581248
277:55:46:005 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=1294256 free=110512 unclaimed=466944 avail=577456
285:55:46:013 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: gcmap lookup begin
286:55:46:013 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: queue map m1l2a
287:55:46:013 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: direct map begin
294:55:46:014 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: G326 pre-map client ensure begin
298:55:46:015 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: released unused nodes reserve 256 Kb
299:55:46:015 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: released unused submodels reserve 16 Kb
301:55:46:015 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: freed 0 menu/UI textures for map load
302:55:46:016 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: GX HUD/menu slabs released for map load
323:55:46:019 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: titles init skipped for gcmap smoke route
328:55:46:023 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: client edicts using static gcmap bootstrap tables
418:55:46:030 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: heap mark stage=client_module_ready used=1315640 free=76840 unclaimed=479232 avail=556072
420:55:46:030 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1315640 free=76840 unclaimed=479232 avail=556072
421:55:46:031 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: G326 pre-map client ensure ready
422:55:46:031 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: freed 0 menu/UI textures for map load
423:55:46:031 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: GX HUD/menu slabs released for map load
424:55:46:031 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: G326 keep client across newgame map load
425:55:46:031 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: client subsystems trimmed for map load
429:55:46:032 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: renderer trim for map load
430:55:46:032 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: present buf released map load
440:55:46:034 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: map load cfg skipped
443:55:46:036 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: pre-spawn mem map set
456:55:46:038 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: present buf released map load
460:55:46:039 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: server string arena spill dropped for map reload
475:55:46:040 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: pre-spawn map buffer prepared for m1l2a
478:55:46:041 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:45] Xash3D GameCube: server string arena spill dropped for map reload
489:55:47:159 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:46] Xash3D GameCube: map load compact (no lighting, miptex headers only) 3.14 Mb 竊 1.96 Mb (G154 disc LM) +align
534:55:47:392 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:46] Xash3D GameCube: world surfedges copied 230.03 Kb to map tail
546:55:47:395 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:46] Xash3D GameCube: releasing gcmap BSP staging 1.96 Mb before surfaces
592:55:47:472 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:46] Xash3D GameCube: map skyname early mohnight1 (before CapFaces)
661:55:47:574 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:46] Xash3D GameCube: freed 126 menu/UI textures for map load
662:55:47:574 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:46] Xash3D GameCube: GX HUD/menu slabs released for map load
1179:55:47:915 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:46] Xash3D GameCube: resource sync skipped for local map route
1185:55:47:918 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:46] Xash3D GameCube: renderer restore after map load
1186:55:47:918 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:46] Xash3D GameCube: map loaded m1l2a
1187:55:47:918 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1189:55:47:919 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:47] Xash3D GameCube: budget moved entity text to map leftover (46.10 Kb), heap free 50.83 Kb
1191:55:47:928 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:47] Xash3D GameCube: direct-map player prime begin edict=1
1280:55:48:016 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:47] Xash3D GameCube: CMPR ARAM bounce adopted 36 x 10944 + 0 x 0 bytes = 384 Kb (map arena)
1287:55:48:694 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:47] Xash3D GameCube: world DL lightmap pages stream@1669920 slots=510 (255 Kb from map arena, CMPR pages)
1468:55:49:579 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:48] Xash3D GameCube: direct-map player prime ready edict=1 private=0x80aab6f0 origin=(5349,-3867,69)
1469:55:49:579 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:48] Xash3D GameCube: direct-map loopback netchan initialized
1470:55:49:580 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:48] Xash3D GameCube: direct-map queued 35 user message regs overflow=0
1471:55:49:580 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [13:55:48] Xash3D GameCube: direct-map client ready cs_spawned frames=0x80a5e400
```

- Full Dolphin log: `media/playtests/screenshots/20261124-135543-m1l2a-retailhud-lowmemfix/dolphin.log.gz`
