# MOHAA Probe m1l1-intro-hud-lean-mode — 20261124-030600

- ISO: `/tmp/mohaa-hud-refine/out/mohaa-m1l1-intro-hud-detect.iso`
- Route: `m1l1-intro-hud-lean-mode`
- Duration cap: 25s
- Repo: `ebf188540a`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261124-030600-m1l1-intro-hud-lean-mode/`
- Video: `media/playtests/videos/20261124-030600-m1l1-intro-hud-lean-mode-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: ebf188540a. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-hud-refine/out/mohaa-m1l1-intro-hud-detect.iso (SHA-256 4a094c623ca52570630585413239597f4a8a53caa73d247bf069cc95515f1a31). MOHAA selects the native/GameCube HUD path during CHud initialization even at default gc_quality=1.

## Frame stats
```
final.png: (640, 480) black=100.0% mean=(0, 0, 0)
```

## OSReport (key)
```
24:06:02:069 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l1
35:06:02:090 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=mohaa
36:06:02:090 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Xash3D GameCube: linked gamedir=mohaa detected=mohaa
41:06:02:091 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l1
62:06:02:120 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
77:06:02:528 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Program args: xash xash -dev 2 -log -game mohaa -gcworldrender -gcmap m1l1 -gclistenserver m1l1 -gcplayerinput -width 320 -height 240
110:06:02:546 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Xash3D GameCube: released unused submodels reserve 16 Kb
162:06:02:585 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Xash3D GameCube: heap mark stage=client_local_init_ready used=247432 free=2936 unclaimed=94208 avail=97144
191:06:02:609 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=256600 free=1960 unclaimed=86016 avail=87976
198:06:02:643 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Xash3D GameCube: renderer screen map ready
201:06:02:644 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=256600 free=1960 unclaimed=86016 avail=87976
210:06:02:645 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Xash3D GameCube: heap mark stage=renderer_images_ready used=256736 free=1824 unclaimed=86016 avail=87840
214:06:02:647 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Xash3D GameCube: heap mark stage=renderer_init_ready used=256816 free=1744 unclaimed=86016 avail=87760
221:06:02:653 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Xash3D GameCube: heap mark stage=client_video_init_ready used=260560 free=2096 unclaimed=81920 avail=84016
244:06:02:657 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=264352 free=2400 unclaimed=77824 avail=80224
252:06:02:665 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Xash3D GameCube: gcmap lookup begin
253:06:02:665 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Xash3D GameCube: queue map m1l1
254:06:02:665 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Xash3D GameCube: direct map begin
256:06:02:666 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Xash3D GameCube: freed 0 menu/UI textures for map load
257:06:02:666 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Xash3D GameCube: GX HUD/menu slabs released for map load
259:06:02:668 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Xash3D GameCube: sound trimmed for map load
260:06:02:668 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Xash3D GameCube: client subsystems trimmed for map load
271:06:02:669 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Xash3D GameCube: renderer trim for map load
272:06:02:669 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:01] Xash3D GameCube: present buf released map load
289:06:07:169 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:06] Xash3D GameCube: map load cfg skipped
292:06:07:172 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:06] Xash3D GameCube: pre-spawn mem map set
306:06:07:173 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:06] Xash3D GameCube: present buf released map load
308:06:07:174 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:06] Xash3D GameCube: server string arena spill dropped for map reload
318:06:07:175 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:06] Xash3D GameCube: pre-spawn map buffer prepared for m1l1
322:06:07:175 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:06] Xash3D GameCube: server string arena spill dropped for map reload
333:06:07:884 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:06] Xash3D GameCube: map load compact (no lighting, miptex headers only) 1.87 Mb 竊 1.22 Mb (G154 disc LM)
372:06:08:033 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:07] Xash3D GameCube: world surfedges copied 95.81 Kb to map tail
374:06:08:034 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:07] Xash3D GameCube: world faces copied 100.84 Kb to map tail
386:06:08:036 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:07] Xash3D GameCube: releasing gcmap BSP staging 1.22 Mb before surfaces
437:06:08:161 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:07] Xash3D GameCube: map skyname early mohnight1 (before CapFaces)
502:06:09:536 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: freed 64 menu/UI textures for map load
503:06:09:536 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: GX HUD/menu slabs released for map load
977:06:09:677 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: resource sync skipped for local map route
983:06:09:681 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: renderer restore after map load
984:06:09:681 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: map loaded m1l1
985:06:09:681 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
987:06:09:682 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: budget moved entity text to map leftover (20.53 Kb), heap free 24.03 Kb
992:06:09:689 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
994:06:09:689 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: direct map ready
997:06:09:690 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: skip startup video scan for gcmap route
998:06:09:690 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: gcmap smoke frames begin
1005:06:09:692 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: gcmap smoke frames ready
1008:06:09:692 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=319968 free=24608 unclaimed=0 avail=24608
1009:06:09:692 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: solo listenserver active map=m1l1 (gcmap tip)
1020:06:09:699 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: livemap armed=0 (file absent)
1023:06:09:735 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: released unused submodels reserve 16 Kb
1025:06:09:736 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: freed 64 menu/UI textures for map load
1026:06:09:736 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: GX HUD/menu slabs released for map load
1047:06:09:740 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: titles init skipped for gcmap smoke route
1052:06:09:743 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: client edicts using static gcmap bootstrap tables
1142:06:09:751 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: heap mark stage=client_module_ready used=317680 free=26896 unclaimed=0 avail=26896
1144:06:09:751 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=317680 free=26896 unclaimed=0 avail=26896
1185:06:09:786 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: serverdata HUD vidinit deferred for local map route
1186:06:09:786 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: client edicts capped for map route max=460 requested=460
1187:06:09:787 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:06:08] Xash3D GameCube: serverdata map CRC skipped for local map route
```

- Full Dolphin log: `media/playtests/screenshots/20261124-030600-m1l1-intro-hud-lean-mode/dolphin.log.gz`
