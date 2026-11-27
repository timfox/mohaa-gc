# MOHAA Probe m1l1-actor-playthrough — 20261123-211220

- ISO: `/tmp/mohaa-actor-anim-fix/out/mohaa-m1l1-actor-animation-dispatch.iso`
- Route: `m1l1-actor-playthrough`
- Duration cap: 65s
- Repo: `c1064a463f`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261123-211220-m1l1-actor-playthrough/`
- Video: `media/playtests/videos/20261123-actor-playthrough-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: c1064a463f. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-actor-anim-fix/out/mohaa-m1l1-actor-animation-dispatch.iso (SHA-256 97fc9343f9bf0a722cbf2316a5ee85213c719b4fc1bc0e6ed39c245a4c1b6ca1). Input-assisted m1l1 playthrough; record the 640x480 guest render for actor and intro review.

## Frame stats
```
final.png: (640, 480) black=8.9% mean=(47, 43, 39)
```

## OSReport (key)
```
41:12:22:980 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
42:12:22:980 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:22] Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
69:12:23:071 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:22] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
96:12:23:783 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Program args: xash xash -dev 2 -log -game mohaa -gcworldrender -gclistenserver m1l1 -gcmap m1l1 -gcvideo prog -gcplayerinput -width 320 -height 240
143:12:23:818 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: released unused nodes reserve 256 Kb
144:12:23:819 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: released unused submodels reserve 16 Kb
196:12:23:872 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: heap mark stage=client_local_init_ready used=876128 free=238560 unclaimed=790528 avail=1029088
226:12:23:908 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=886560 free=228128 unclaimed=790528 avail=1018656
233:12:23:948 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: renderer screen map ready
236:12:23:949 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=886560 free=228128 unclaimed=790528 avail=1018656
245:12:23:950 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: heap mark stage=renderer_images_ready used=886696 free=227992 unclaimed=790528 avail=1018520
249:12:23:952 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: heap mark stage=renderer_init_ready used=985088 free=129600 unclaimed=790528 avail=920128
256:12:23:959 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: heap mark stage=client_video_init_ready used=988832 free=125856 unclaimed=790528 avail=916384
279:12:23:965 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=992624 free=122064 unclaimed=790528 avail=912592
289:12:23:975 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: gcmap lookup begin
290:12:23:975 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: queue map m1l1
291:12:23:975 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: direct map begin
293:12:23:976 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: freed 0 menu/UI textures for map load
294:12:23:976 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: GX HUD/menu slabs released for map load
296:12:23:979 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: sound trimmed for map load
297:12:23:980 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: client subsystems trimmed for map load
306:12:23:981 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: renderer trim for map load
307:12:23:981 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: present buf released map load
323:12:23:987 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: map load cfg skipped
326:12:23:991 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: pre-spawn mem map set
340:12:23:993 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: present buf released map load
342:12:23:993 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: server string arena spill dropped for map reload
351:12:23:994 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: pre-spawn map buffer prepared for m1l1
355:12:23:995 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: server string arena spill dropped for map reload
364:12:24:433 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:23] Xash3D GameCube: map load compact (no lighting, miptex headers only) 1.79 Mb 竊 1.14 Mb (G154 disc LM)
402:12:24:636 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:24] Xash3D GameCube: world surfedges copied 95.81 Kb to map tail
404:12:24:636 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:24] Xash3D GameCube: world faces copied 100.84 Kb to map tail
416:12:24:642 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:24] Xash3D GameCube: releasing gcmap BSP staging 1.14 Mb before surfaces
521:12:26:069 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:25] Xash3D GameCube: freed 64 menu/UI textures for map load
522:12:26:069 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:25] Xash3D GameCube: GX HUD/menu slabs released for map load
530:12:26:202 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:25] PM_WorldMesh: maps/m1l1.mcol, 0 brushes, 18 terrain patches, 13212 patch triangles, 388920 bytes in the map arena
875:12:26:684 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] mohaa: running maps/m1l1.scr (budget 384 KiB, 384 KiB in the map arena in 1 piece, the rest from the heap)
1090:12:27:244 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: resource sync skipped for local map route
1096:12:27:250 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: renderer restore after map load
1097:12:27:250 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: map loaded m1l1
1098:12:27:250 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1100:12:27:251 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: budget moved entity text to map leftover (20.55 Kb), entity reserve returned, heap free 223.68 Kb
1105:12:27:260 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1107:12:27:260 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: direct map ready
1110:12:27:260 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: skip startup video scan for gcmap route
1111:12:27:261 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: gcmap smoke frames begin
1118:12:27:265 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: gcmap smoke frames ready
1121:12:27:266 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=1676168 free=204472 unclaimed=24576 avail=229048
1122:12:27:266 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: solo listenserver active map=m1l1 (gcmap tip)
1133:12:27:274 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: livemap armed=0 (file absent)
1137:12:27:316 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: released unused nodes reserve 256 Kb
1138:12:27:316 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: released unused submodels reserve 16 Kb
1140:12:27:316 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: freed 64 menu/UI textures for map load
1141:12:27:316 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: GX HUD/menu slabs released for map load
1162:12:27:323 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: titles init skipped for gcmap smoke route
1167:12:27:326 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: client edicts using static gcmap bootstrap tables
1253:12:27:334 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: heap mark stage=client_module_ready used=1411232 free=469408 unclaimed=24576 avail=493984
1255:12:27:334 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1411232 free=469408 unclaimed=24576 avail=493984
1284:12:27:365 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: serverdata HUD vidinit deferred for local map route
1285:12:27:366 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [21:12:26] Xash3D GameCube: client edicts capped for map route max=460 requested=460
```

- Full Dolphin log: `media/playtests/screenshots/20261123-211220-m1l1-actor-playthrough/dolphin.log.gz`
