# MOHAA Probe mohaa-hud-direct-map — 20261123-232953

- ISO: `/tmp/mohaa-hud-visual/mohaa-m1l1-hud-direct.iso`
- Route: `mohaa-hud-direct-map`
- Duration cap: 60s
- Repo: `6be6ce53a9`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261123-232953-mohaa-hud-direct-map/`
- Periodic guest frames: 7 screenshots in `media/playtests/screenshots/20261123-232953-mohaa-hud-direct-map/frames/`
- Video: `media/playtests/videos/20261123-232953-mohaa-hud-direct-map-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: 6be6ce53a9. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-hud-visual/mohaa-m1l1-hud-direct.iso (SHA-256 b392ba97e698b64dba73a321d54f1889c5c9e318a652faac06c8e291d306cd3e). Direct m1l1 listenserver boot, GameCube-aware ISO, all retail MOHAA HUD sprites in extras.pk3. Capture gameplay HUD, actor/map load, and retail skybox.

## Frame stats
```
final.png: (640, 480) black=8.9% mean=(52, 47, 43)
```

## OSReport (key)
```
41:29:55:612 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
42:29:55:612 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:55] Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
69:29:55:714 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:55] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
98:29:56:530 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Program args: xash xash -dev 2 -log -game mohaa -gcworldrender -gclistenserver m1l1 -gcmap m1l1 -gcvideo prog -gcplayerinput -width 320 -height 240
142:29:56:553 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: released unused nodes reserve 256 Kb
143:29:56:553 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: released unused submodels reserve 16 Kb
195:29:56:598 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: heap mark stage=client_local_init_ready used=877488 free=238096 unclaimed=475136 avail=713232
225:29:56:636 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=887936 free=227648 unclaimed=475136 avail=702784
232:29:56:678 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: renderer screen map ready
235:29:56:679 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=887936 free=227648 unclaimed=475136 avail=702784
244:29:56:680 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: heap mark stage=renderer_images_ready used=888072 free=227512 unclaimed=475136 avail=702648
248:29:56:682 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: heap mark stage=renderer_init_ready used=986464 free=129120 unclaimed=475136 avail=604256
255:29:56:688 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: heap mark stage=client_video_init_ready used=990216 free=125368 unclaimed=475136 avail=600504
278:29:56:696 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=994008 free=121576 unclaimed=475136 avail=596712
288:29:56:704 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: gcmap lookup begin
289:29:56:705 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: queue map m1l1
290:29:56:705 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: direct map begin
292:29:56:705 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: freed 0 menu/UI textures for map load
293:29:56:706 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: GX HUD/menu slabs released for map load
295:29:56:707 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: sound trimmed for map load
296:29:56:708 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: client subsystems trimmed for map load
305:29:56:709 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: renderer trim for map load
306:29:56:709 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: present buf released map load
322:29:56:715 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: map load cfg skipped
325:29:56:717 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: pre-spawn mem map set
339:29:56:719 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: present buf released map load
341:29:56:719 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: server string arena spill dropped for map reload
350:29:56:720 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: pre-spawn map buffer prepared for m1l1
354:29:56:721 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: server string arena spill dropped for map reload
363:29:57:213 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:56] Xash3D GameCube: map load compact (no lighting, miptex headers only) 1.87 Mb 竊 1.22 Mb (G154 disc LM)
401:29:57:412 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:57] Xash3D GameCube: world surfedges copied 95.81 Kb to map tail
403:29:57:413 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:57] Xash3D GameCube: world faces copied 100.84 Kb to map tail
415:29:57:419 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:57] Xash3D GameCube: releasing gcmap BSP staging 1.22 Mb before surfaces
467:29:57:558 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:57] Xash3D GameCube: map skyname early mohnight1 (before CapFaces)
521:29:59:016 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:58] Xash3D GameCube: freed 64 menu/UI textures for map load
522:29:59:017 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:58] Xash3D GameCube: GX HUD/menu slabs released for map load
530:29:59:149 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:58] PM_WorldMesh: maps/m1l1.mcol, 0 brushes, 18 terrain patches, 13212 patch triangles, 388920 bytes in the map arena
875:29:59:632 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] mohaa: running maps/m1l1.scr (budget 384 KiB, 384 KiB in the map arena in 1 piece, the rest from the heap)
1052:29:59:833 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: resource sync skipped for local map route
1058:29:59:839 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: renderer restore after map load
1059:29:59:839 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: map loaded m1l1
1060:29:59:839 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1062:29:59:840 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: budget moved entity text to map leftover (20.54 Kb), entity reserve returned, heap free 178.29 Kb
1067:29:59:848 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1069:29:59:848 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: direct map ready
1072:29:59:848 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: skip startup video scan for gcmap route
1073:29:59:849 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: gcmap smoke frames begin
1080:29:59:853 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: gcmap smoke frames ready
1083:29:59:853 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=1408152 free=174376 unclaimed=8192 avail=182568
1084:29:59:854 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: solo listenserver active map=m1l1 (gcmap tip)
1095:29:59:861 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: livemap armed=0 (file absent)
1104:29:59:902 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: released unused nodes reserve 256 Kb
1105:29:59:902 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: released unused submodels reserve 16 Kb
1106:29:59:902 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: freed 64 menu/UI textures for map load
1107:29:59:903 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: GX HUD/menu slabs released for map load
1128:29:59:906 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: titles init skipped for gcmap smoke route
1133:29:59:910 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: client edicts using static gcmap bootstrap tables
1219:29:59:919 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: heap mark stage=client_module_ready used=1142512 free=440016 unclaimed=8192 avail=448208
1221:29:59:919 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1142512 free=440016 unclaimed=8192 avail=448208
1250:29:59:950 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:29:59] Xash3D GameCube: serverdata HUD vidinit deferred for local map route
```

- Full Dolphin log: `media/playtests/screenshots/20261123-232953-mohaa-hud-direct-map/dolphin.log.gz`
