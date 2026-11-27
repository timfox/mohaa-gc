# MOHAA Probe m1l2a-compass-objective — 20261124-005551

- ISO: `/tmp/mohaa-compass-build/mohaa-compass-objective-probe.iso`
- Route: `m1l2a-compass-objective`
- Duration cap: 45s
- Repo: `2c0a59c871`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261124-005551-m1l2a-compass-objective/`
- Periodic guest frames: 20 screenshots in `media/playtests/screenshots/20261124-005551-m1l2a-compass-objective/frames/`
- Video: `media/playtests/videos/20261124-005551-m1l2a-compass-objective-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: 2c0a59c871. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-compass-build/mohaa-compass-objective-probe.iso (SHA-256 6b3e1ff42f49548679d9447d47ebf6f010428a39553b545abc5bedc20ed3b11e). Scratch-only script probe sets objective 1 active at a known vector, then calls multi-argument iprintlnbold_noloc and the existing retail hint_door function.

## Frame stats
```
final.png: (640, 480) black=9.3% mean=(41, 33, 25)
```

## OSReport (key)
```
36:55:53:580 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
37:55:53:580 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:53] Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
63:55:53:847 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:53] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
152:55:55:481 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Program args: xash xash -dev 2 -log -game mohaa -gclistenserver m1l2a -gcmap m1l2a -gcvideo prog -gcplayerinput -width 320 -height 240
194:55:55:516 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: released unused nodes reserve 256 Kb
195:55:55:516 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: released unused submodels reserve 16 Kb
247:55:55:601 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: heap mark stage=client_local_init_ready used=941888 free=244192 unclaimed=569344 avail=813536
277:55:55:661 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=952640 free=233440 unclaimed=569344 avail=802784
284:55:55:712 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: renderer screen map ready
287:55:55:713 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=952640 free=233440 unclaimed=569344 avail=802784
296:55:55:714 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: heap mark stage=renderer_images_ready used=952776 free=233304 unclaimed=569344 avail=802648
299:55:55:716 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: heap mark stage=renderer_init_ready used=952856 free=233224 unclaimed=569344 avail=802568
306:55:55:722 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: heap mark stage=client_video_init_ready used=956616 free=229464 unclaimed=569344 avail=798808
329:55:55:728 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=960408 free=225672 unclaimed=569344 avail=795016
337:55:55:740 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: gcmap lookup begin
338:55:55:740 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: queue map m1l2a
339:55:55:741 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: direct map begin
341:55:55:741 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: freed 0 menu/UI textures for map load
342:55:55:742 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: GX HUD/menu slabs released for map load
344:55:55:743 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: sound trimmed for map load
345:55:55:744 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: client subsystems trimmed for map load
354:55:55:746 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: renderer trim for map load
355:55:55:746 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: present buf released map load
371:55:55:750 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: map load cfg skipped
374:55:55:753 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: pre-spawn mem map set
388:55:55:755 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: present buf released map load
390:55:55:755 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: server string arena spill dropped for map reload
399:55:55:756 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: pre-spawn map buffer prepared for m1l2a
403:55:55:756 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:55] Xash3D GameCube: server string arena spill dropped for map reload
412:55:56:615 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:56] Xash3D GameCube: map load compact (no lighting, miptex headers only) 3.14 Mb 竊 1.96 Mb (G154 disc LM) +align
459:55:56:921 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:56] Xash3D GameCube: world surfedges copied 230.03 Kb to map tail
471:55:56:924 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:56] Xash3D GameCube: releasing gcmap BSP staging 1.96 Mb before surfaces
578:55:59:188 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:59] Xash3D GameCube: freed 126 menu/UI textures for map load
579:55:59:188 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:59] Xash3D GameCube: GX HUD/menu slabs released for map load
587:55:59:268 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:55:59] PM_WorldMesh: maps/m1l2a.mcol, 0 brushes, 146 terrain patches, 7870 patch triangles, 243960 bytes in the map arena
649:56:00:218 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] mohaa: running maps/m1l2a.scr (budget 384 KiB, 384 KiB in the map arena in 1 piece, the rest from the heap)
1062:56:00:687 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: resource sync skipped for local map route
1068:56:00:694 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: renderer restore after map load
1069:56:00:694 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: map loaded m1l2a
1070:56:00:694 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1072:56:00:696 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: budget moved entity text to map leftover (46.10 Kb), entity reserve returned, heap free 284.54 Kb
1077:56:00:706 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1079:56:00:706 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: direct map ready
1082:56:00:707 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: skip startup video scan for gcmap route
1083:56:00:707 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: gcmap smoke frames begin
1084:56:00:707 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: gcmap smoke frames ready
1087:56:00:707 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=1464056 free=274984 unclaimed=16384 avail=291368
1088:56:00:708 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: solo listenserver active map=m1l2a (gcmap tip)
1102:56:00:720 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: livemap armed=0 (file absent)
1111:56:00:763 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: released unused nodes reserve 256 Kb
1112:56:00:763 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: released unused submodels reserve 16 Kb
1113:56:00:763 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: freed 126 menu/UI textures for map load
1114:56:00:763 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: GX HUD/menu slabs released for map load
1135:56:00:768 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: titles init skipped for gcmap smoke route
1140:56:00:772 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: client edicts using static gcmap bootstrap tables
1230:56:00:825 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: heap mark stage=client_module_ready used=1198304 free=540736 unclaimed=16384 avail=557120
1232:56:00:825 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1198304 free=540736 unclaimed=16384 avail=557120
1260:56:00:873 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: serverdata HUD vidinit deferred for local map route
1261:56:00:873 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: client edicts capped for map route max=460 requested=460
1262:56:00:874 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:56:00] Xash3D GameCube: serverdata map CRC skipped for local map route
```

- Full Dolphin log: `media/playtests/screenshots/20261124-005551-m1l2a-compass-objective/dolphin.log.gz`
