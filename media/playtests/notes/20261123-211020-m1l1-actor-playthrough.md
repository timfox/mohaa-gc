# MOHAA Probe m1l1-actor-playthrough — 20261123-211020

- ISO: `/tmp/mohaa-actor-anim-fix/out/mohaa-m1l1-actor-animation-dispatch.iso`
- Route: `m1l1-actor-playthrough`
- Duration cap: 65s
- Repo: `c1064a463f`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261123-211020-m1l1-actor-playthrough/`

MOHAA GameCube playtest. Repo HEAD: c1064a463f. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-actor-anim-fix/out/mohaa-m1l1-actor-animation-dispatch.iso (SHA-256 97fc9343f9bf0a722cbf2316a5ee85213c719b4fc1bc0e6ed39c245a4c1b6ca1). Input-assisted m1l1 playthrough; record the 640x480 guest render for actor and intro review.

## Frame stats
```
final.png: (640, 480) black=8.9% mean=(53, 49, 46)
```

## OSReport (key)
```
41:10:22:587 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
42:10:22:587 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:22] Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
69:10:22:674 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:22] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
96:10:23:390 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Program args: xash xash -dev 2 -log -game mohaa -gcworldrender -gclistenserver m1l1 -gcmap m1l1 -gcvideo prog -gcplayerinput -width 320 -height 240
143:10:23:422 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: released unused nodes reserve 256 Kb
144:10:23:422 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: released unused submodels reserve 16 Kb
196:10:23:461 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: heap mark stage=client_local_init_ready used=876128 free=238560 unclaimed=790528 avail=1029088
226:10:23:494 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=886560 free=228128 unclaimed=790528 avail=1018656
233:10:23:531 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: renderer screen map ready
236:10:23:531 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=886560 free=228128 unclaimed=790528 avail=1018656
245:10:23:533 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: heap mark stage=renderer_images_ready used=886696 free=227992 unclaimed=790528 avail=1018520
249:10:23:535 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: heap mark stage=renderer_init_ready used=985088 free=129600 unclaimed=790528 avail=920128
256:10:23:540 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: heap mark stage=client_video_init_ready used=988832 free=125856 unclaimed=790528 avail=916384
279:10:23:545 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=992624 free=122064 unclaimed=790528 avail=912592
289:10:23:554 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: gcmap lookup begin
290:10:23:554 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: queue map m1l1
291:10:23:554 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: direct map begin
293:10:23:554 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: freed 0 menu/UI textures for map load
294:10:23:555 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: GX HUD/menu slabs released for map load
296:10:23:556 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: sound trimmed for map load
297:10:23:556 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: client subsystems trimmed for map load
306:10:23:558 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: renderer trim for map load
307:10:23:558 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: present buf released map load
323:10:23:562 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: map load cfg skipped
326:10:23:565 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: pre-spawn mem map set
340:10:23:567 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: present buf released map load
342:10:23:567 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: server string arena spill dropped for map reload
351:10:23:568 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: pre-spawn map buffer prepared for m1l1
355:10:23:568 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: server string arena spill dropped for map reload
364:10:24:039 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:23] Xash3D GameCube: map load compact (no lighting, miptex headers only) 1.79 Mb 竊 1.14 Mb (G154 disc LM)
402:10:24:242 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:24] Xash3D GameCube: world surfedges copied 95.81 Kb to map tail
404:10:24:243 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:24] Xash3D GameCube: world faces copied 100.84 Kb to map tail
416:10:24:249 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:24] Xash3D GameCube: releasing gcmap BSP staging 1.14 Mb before surfaces
521:10:25:677 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:25] Xash3D GameCube: freed 64 menu/UI textures for map load
522:10:25:677 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:25] Xash3D GameCube: GX HUD/menu slabs released for map load
530:10:25:809 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:25] PM_WorldMesh: maps/m1l1.mcol, 0 brushes, 18 terrain patches, 13212 patch triangles, 388920 bytes in the map arena
875:10:26:306 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] mohaa: running maps/m1l1.scr (budget 384 KiB, 384 KiB in the map arena in 1 piece, the rest from the heap)
1090:10:26:855 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: resource sync skipped for local map route
1096:10:26:861 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: renderer restore after map load
1097:10:26:861 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: map loaded m1l1
1098:10:26:861 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1100:10:26:862 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: budget moved entity text to map leftover (20.55 Kb), entity reserve returned, heap free 223.68 Kb
1105:10:26:870 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1107:10:26:870 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: direct map ready
1110:10:26:871 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: skip startup video scan for gcmap route
1111:10:26:871 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: gcmap smoke frames begin
1118:10:26:877 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: gcmap smoke frames ready
1121:10:26:877 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=1676168 free=204472 unclaimed=24576 avail=229048
1122:10:26:877 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: solo listenserver active map=m1l1 (gcmap tip)
1133:10:26:887 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: livemap armed=0 (file absent)
1137:10:26:926 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: released unused nodes reserve 256 Kb
1138:10:26:926 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: released unused submodels reserve 16 Kb
1140:10:26:926 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: freed 64 menu/UI textures for map load
1141:10:26:926 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: GX HUD/menu slabs released for map load
1162:10:26:933 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: titles init skipped for gcmap smoke route
1167:10:26:936 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: client edicts using static gcmap bootstrap tables
1253:10:26:944 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: heap mark stage=client_module_ready used=1411232 free=469408 unclaimed=24576 avail=493984
1255:10:26:944 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1411232 free=469408 unclaimed=24576 avail=493984
1284:10:26:977 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: serverdata HUD vidinit deferred for local map route
1285:10:26:977 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:10:26] Xash3D GameCube: client edicts capped for map route max=460 requested=460
```

- Full Dolphin log: `media/playtests/screenshots/20261123-211020-m1l1-actor-playthrough/dolphin.log.gz`
