# MOHAA Probe m1l1-actor-anim-dispatch — 20261123-205328

- ISO: `/tmp/mohaa-actor-anim-fix/out/mohaa-m1l1-actor-animation-dispatch.iso`
- Route: `m1l1-actor-anim-dispatch`
- Duration cap: 60s
- Repo: `daa2c65049`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261123-205328-m1l1-actor-anim-dispatch/`

MOHAA GameCube playtest. Repo HEAD: daa2c65049. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-actor-anim-fix/out/mohaa-m1l1-actor-animation-dispatch.iso (SHA-256 97fc9343f9bf0a722cbf2316a5ee85213c719b4fc1bc0e6ed39c245a4c1b6ca1). Actor animation dispatch change; verify runtime sequence and cutscene actor visuals.

## Frame stats
```
final.png: (640, 480) black=8.9% mean=(49, 44, 36)
```

## OSReport (key)
```
41:53:30:618 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
42:53:30:618 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:30] Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
69:53:30:705 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:30] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
96:53:31:420 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Program args: xash xash -dev 2 -log -game mohaa -gcworldrender -gclistenserver m1l1 -gcmap m1l1 -gcvideo prog -gcplayerinput -width 320 -height 240
143:53:31:453 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: released unused nodes reserve 256 Kb
144:53:31:454 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: released unused submodels reserve 16 Kb
196:53:31:494 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: heap mark stage=client_local_init_ready used=876128 free=238560 unclaimed=790528 avail=1029088
226:53:31:531 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=886560 free=228128 unclaimed=790528 avail=1018656
233:53:31:567 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: renderer screen map ready
236:53:31:568 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=886560 free=228128 unclaimed=790528 avail=1018656
245:53:31:569 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: heap mark stage=renderer_images_ready used=886696 free=227992 unclaimed=790528 avail=1018520
249:53:31:571 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: heap mark stage=renderer_init_ready used=985088 free=129600 unclaimed=790528 avail=920128
256:53:31:577 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: heap mark stage=client_video_init_ready used=988832 free=125856 unclaimed=790528 avail=916384
279:53:31:582 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=992624 free=122064 unclaimed=790528 avail=912592
289:53:31:590 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: gcmap lookup begin
290:53:31:590 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: queue map m1l1
291:53:31:590 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: direct map begin
293:53:31:591 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: freed 0 menu/UI textures for map load
294:53:31:591 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: GX HUD/menu slabs released for map load
296:53:31:593 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: sound trimmed for map load
297:53:31:593 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: client subsystems trimmed for map load
306:53:31:594 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: renderer trim for map load
307:53:31:594 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: present buf released map load
323:53:31:600 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: map load cfg skipped
326:53:31:602 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: pre-spawn mem map set
340:53:31:604 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: present buf released map load
342:53:31:604 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: server string arena spill dropped for map reload
351:53:31:605 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: pre-spawn map buffer prepared for m1l1
355:53:31:606 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: server string arena spill dropped for map reload
364:53:32:070 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:31] Xash3D GameCube: map load compact (no lighting, miptex headers only) 1.79 Mb 竊 1.14 Mb (G154 disc LM)
402:53:32:274 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:32] Xash3D GameCube: world surfedges copied 95.81 Kb to map tail
404:53:32:274 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:32] Xash3D GameCube: world faces copied 100.84 Kb to map tail
416:53:32:281 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:32] Xash3D GameCube: releasing gcmap BSP staging 1.14 Mb before surfaces
521:53:33:708 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:33] Xash3D GameCube: freed 64 menu/UI textures for map load
522:53:33:708 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:33] Xash3D GameCube: GX HUD/menu slabs released for map load
530:53:33:840 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:33] PM_WorldMesh: maps/m1l1.mcol, 0 brushes, 18 terrain patches, 13212 patch triangles, 388920 bytes in the map arena
875:53:34:338 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] mohaa: running maps/m1l1.scr (budget 384 KiB, 384 KiB in the map arena in 1 piece, the rest from the heap)
1090:53:34:886 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: resource sync skipped for local map route
1096:53:34:891 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: renderer restore after map load
1097:53:34:891 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: map loaded m1l1
1098:53:34:892 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1100:53:34:893 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: budget moved entity text to map leftover (20.55 Kb), entity reserve returned, heap free 223.68 Kb
1105:53:34:900 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1107:53:34:900 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: direct map ready
1110:53:34:901 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: skip startup video scan for gcmap route
1111:53:34:901 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: gcmap smoke frames begin
1118:53:34:906 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: gcmap smoke frames ready
1121:53:34:906 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=1676168 free=204472 unclaimed=24576 avail=229048
1122:53:34:906 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: solo listenserver active map=m1l1 (gcmap tip)
1133:53:34:915 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: livemap armed=0 (file absent)
1137:53:34:953 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: released unused nodes reserve 256 Kb
1138:53:34:953 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: released unused submodels reserve 16 Kb
1140:53:34:954 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: freed 64 menu/UI textures for map load
1141:53:34:954 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: GX HUD/menu slabs released for map load
1162:53:34:961 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: titles init skipped for gcmap smoke route
1167:53:34:965 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: client edicts using static gcmap bootstrap tables
1253:53:34:972 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: heap mark stage=client_module_ready used=1411232 free=469408 unclaimed=24576 avail=493984
1255:53:34:972 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1411232 free=469408 unclaimed=24576 avail=493984
1284:53:35:006 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: serverdata HUD vidinit deferred for local map route
1285:53:35:007 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [20:53:34] Xash3D GameCube: client edicts capped for map route max=460 requested=460
```

- Full Dolphin log: `media/playtests/screenshots/20261123-205328-m1l1-actor-anim-dispatch/dolphin.log.gz`
