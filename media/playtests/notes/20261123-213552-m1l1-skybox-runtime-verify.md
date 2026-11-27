# MOHAA Probe m1l1-skybox-runtime-verify — 20261123-213552

- ISO: `/tmp/mohaa-sky-update/out/m1l1-skybox-v2.iso`
- Route: `m1l1-skybox-runtime-verify`
- Duration cap: 28s
- Repo: `c1064a463f`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261123-213552-m1l1-skybox-runtime-verify/`
- Periodic guest frames: 3 screenshots in `media/playtests/screenshots/20261123-213552-m1l1-skybox-runtime-verify/frames/`
- Video: `media/playtests/videos/20261123-213552-m1l1-skybox-runtime-verify-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: c1064a463f. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-sky-update/out/m1l1-skybox-v2.iso (SHA-256 53975585c9d5b6f808e207e3a9b1247ec7a22a49021adb1d072711b9e5e7ef6a). m1l1 skybox runtime verification and forced silent video capture.

## Frame stats
```
final.png: (640, 480) black=8.9% mean=(48, 44, 41)
```

## OSReport (key)
```
40:35:54:394 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
41:35:54:395 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:54] Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
67:35:54:497 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:54] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
96:35:55:098 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Program args: xash xash -dev 2 -log -game mohaa -gcworldrender -gclistenserver m1l1 -gcmap m1l1 -gcplayerinput -width 320 -height 240
138:35:55:137 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: released unused nodes reserve 256 Kb
139:35:55:137 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: released unused submodels reserve 16 Kb
191:35:55:197 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: heap mark stage=client_local_init_ready used=878416 free=236272 unclaimed=790528 avail=1026800
221:35:55:233 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=888848 free=225840 unclaimed=790528 avail=1016368
228:35:55:270 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: renderer screen map ready
231:35:55:271 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=888848 free=225840 unclaimed=790528 avail=1016368
240:35:55:272 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: heap mark stage=renderer_images_ready used=888984 free=225704 unclaimed=790528 avail=1016232
244:35:55:274 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: heap mark stage=renderer_init_ready used=987376 free=127312 unclaimed=790528 avail=917840
251:35:55:280 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: heap mark stage=client_video_init_ready used=991128 free=123560 unclaimed=790528 avail=914088
274:35:55:284 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=994920 free=119768 unclaimed=790528 avail=910296
282:35:55:293 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: gcmap lookup begin
283:35:55:293 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: queue map m1l1
284:35:55:293 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: direct map begin
286:35:55:294 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: freed 0 menu/UI textures for map load
287:35:55:294 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: GX HUD/menu slabs released for map load
289:35:55:296 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: sound trimmed for map load
290:35:55:296 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: client subsystems trimmed for map load
299:35:55:298 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: renderer trim for map load
300:35:55:298 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: present buf released map load
316:35:55:303 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: map load cfg skipped
319:35:55:306 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: pre-spawn mem map set
333:35:55:308 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: present buf released map load
335:35:55:309 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: server string arena spill dropped for map reload
344:35:55:310 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: pre-spawn map buffer prepared for m1l1
348:35:55:310 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: server string arena spill dropped for map reload
357:35:55:929 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:55] Xash3D GameCube: map load compact (no lighting, miptex headers only) 1.79 Mb 竊 1.14 Mb (G154 disc LM)
395:35:56:128 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:56] Xash3D GameCube: world surfedges copied 95.81 Kb to map tail
397:35:56:129 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:56] Xash3D GameCube: world faces copied 100.84 Kb to map tail
409:35:56:136 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:56] Xash3D GameCube: releasing gcmap BSP staging 1.14 Mb before surfaces
461:35:56:278 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:56] Xash3D GameCube: map skyname early mohnight1 (before CapFaces)
515:35:57:736 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:57] Xash3D GameCube: freed 64 menu/UI textures for map load
516:35:57:736 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:57] Xash3D GameCube: GX HUD/menu slabs released for map load
524:35:57:866 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:57] PM_WorldMesh: maps/m1l1.mcol, 0 brushes, 18 terrain patches, 13212 patch triangles, 388920 bytes in the map arena
895:35:58:398 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] mohaa: running maps/m1l1.scr (budget 384 KiB, 384 KiB in the map arena in 1 piece, the rest from the heap)
1074:35:58:617 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: resource sync skipped for local map route
1080:35:58:623 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: renderer restore after map load
1081:35:58:623 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: map loaded m1l1
1082:35:58:623 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1084:35:58:624 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: budget moved entity text to map leftover (20.57 Kb), entity reserve returned, heap free 221.44 Kb
1089:35:58:632 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1091:35:58:632 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: direct map ready
1094:35:58:633 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: skip startup video scan for gcmap route
1095:35:58:633 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: gcmap smoke frames begin
1102:35:58:638 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: gcmap smoke frames ready
1105:35:58:639 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=1678464 free=202176 unclaimed=24576 avail=226752
1106:35:58:639 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: solo listenserver active map=m1l1 (gcmap tip)
1120:35:58:648 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: livemap armed=0 (file absent)
1129:35:58:692 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: released unused nodes reserve 256 Kb
1130:35:58:692 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: released unused submodels reserve 16 Kb
1131:35:58:693 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: freed 64 menu/UI textures for map load
1132:35:58:693 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: GX HUD/menu slabs released for map load
1153:35:58:698 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: titles init skipped for gcmap smoke route
1158:35:58:706 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: client edicts using static gcmap bootstrap tables
1244:35:58:715 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: heap mark stage=client_module_ready used=1412824 free=467816 unclaimed=24576 avail=492392
1246:35:58:715 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1412824 free=467816 unclaimed=24576 avail=492392
1275:35:58:750 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:35:58] Xash3D GameCube: serverdata HUD vidinit deferred for local map route
```

- Full Dolphin log: `media/playtests/screenshots/20261123-213552-m1l1-skybox-runtime-verify/dolphin.log.gz`
