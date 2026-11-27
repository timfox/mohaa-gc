# MOHAA Probe m1l2a-retail-objective-pos — 20261124-005940

- ISO: `/tmp/mohaa-compass-build/mohaa-set-objective-pos.iso`
- Route: `m1l2a-retail-objective-pos`
- Duration cap: 45s
- Repo: `2c0a59c871`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261124-005940-m1l2a-retail-objective-pos/`
- Periodic guest frames: 20 screenshots in `media/playtests/screenshots/20261124-005940-m1l2a-retail-objective-pos/frames/`
- Video: `media/playtests/videos/20261124-005940-m1l2a-retail-objective-pos-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: 2c0a59c871. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-compass-build/mohaa-set-objective-pos.iso (SHA-256 2bc91ccc454abaebb992f9b633065c08e58a24b35e3e90333db3042f83cdbe05). Scratch-only map script calls retail set_objective_pos with a known vector, then exercises multi-argument iprintlnbold_noloc and the retail hint_door function.

## Reproducible baseline

- GameCube DOL: `/tmp/mohaa-compass-build/out/mohaagc.dol`, SHA-256 `f20e296425688cd2af53673adbd566115ae113c43b6eff85e52f5dccae123bb1`
- Dolphin build: `eeaafed88a`, local executable `/home/tim/xash3d-gc-lostcoast/3rdparty/dolphin/build/Binaries/dolphin-emu`
- Video backend: OpenGL (`Backend = OGL`); CPU core 1, CPU thread enabled, MMU enabled, accurate CPU cache enabled
- GameCube video route: progressive, 320x240 (`-gcvideo prog -width 320 -height 240`)
- Timeout: 45 seconds; screenshots every 2 seconds; silent H.264 recording; no controller/TAS inputs
- Engine source snapshot: `db73d0d126`; the DOL and ISO were built from the same current MOHAA source state

The guest reached m1l2a and loaded all four compass sprites. The log also contains a FileSystem Pool allocation failure and script errors in cardgame/spotlight routines, so this is feature evidence rather than a campaign-stability certification. The `set_objective_pos` command is no longer reported as unbound; the target bearing against a moving retail mission entity still needs visual confirmation.

## Frame stats
```
final.png: (640, 480) black=9.0% mean=(59, 48, 32)
```

## OSReport (key)
```
36:59:42:448 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
37:59:42:448 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:42] Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
63:59:42:715 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:42] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
152:59:44:349 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Program args: xash xash -dev 2 -log -game mohaa -gclistenserver m1l2a -gcmap m1l2a -gcvideo prog -gcplayerinput -width 320 -height 240
194:59:44:387 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: released unused nodes reserve 256 Kb
195:59:44:387 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: released unused submodels reserve 16 Kb
247:59:44:487 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: heap mark stage=client_local_init_ready used=941936 free=243792 unclaimed=569344 avail=813136
277:59:44:564 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=952688 free=233040 unclaimed=569344 avail=802384
284:59:44:610 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: renderer screen map ready
287:59:44:611 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=952688 free=233040 unclaimed=569344 avail=802384
296:59:44:613 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: heap mark stage=renderer_images_ready used=952824 free=232904 unclaimed=569344 avail=802248
299:59:44:615 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: heap mark stage=renderer_init_ready used=952904 free=232824 unclaimed=569344 avail=802168
306:59:44:623 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: heap mark stage=client_video_init_ready used=956664 free=229064 unclaimed=569344 avail=798408
329:59:44:630 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=960456 free=225272 unclaimed=569344 avail=794616
337:59:44:646 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: gcmap lookup begin
338:59:44:646 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: queue map m1l2a
339:59:44:646 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: direct map begin
341:59:44:647 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: freed 0 menu/UI textures for map load
342:59:44:647 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: GX HUD/menu slabs released for map load
344:59:44:650 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: sound trimmed for map load
345:59:44:650 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: client subsystems trimmed for map load
354:59:44:652 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: renderer trim for map load
355:59:44:653 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: present buf released map load
371:59:44:657 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: map load cfg skipped
374:59:44:660 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: pre-spawn mem map set
388:59:44:662 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: present buf released map load
390:59:44:663 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: server string arena spill dropped for map reload
399:59:44:664 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: pre-spawn map buffer prepared for m1l2a
403:59:44:664 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:44] Xash3D GameCube: server string arena spill dropped for map reload
412:59:45:482 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:45] Xash3D GameCube: map load compact (no lighting, miptex headers only) 3.14 Mb 竊 1.96 Mb (G154 disc LM) +align
459:59:45:793 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:45] Xash3D GameCube: world surfedges copied 230.03 Kb to map tail
471:59:45:797 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:45] Xash3D GameCube: releasing gcmap BSP staging 1.96 Mb before surfaces
578:59:48:056 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:48] Xash3D GameCube: freed 126 menu/UI textures for map load
579:59:48:056 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:48] Xash3D GameCube: GX HUD/menu slabs released for map load
587:59:48:135 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:48] PM_WorldMesh: maps/m1l2a.mcol, 0 brushes, 146 terrain patches, 7870 patch triangles, 243960 bytes in the map arena
649:59:49:144 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] mohaa: running maps/m1l2a.scr (budget 384 KiB, 384 KiB in the map arena in 1 piece, the rest from the heap)
1062:59:49:614 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: resource sync skipped for local map route
1068:59:49:621 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: renderer restore after map load
1069:59:49:621 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: map loaded m1l2a
1070:59:49:622 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1072:59:49:623 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: budget moved entity text to map leftover (46.10 Kb), entity reserve returned, heap free 284.13 Kb
1077:59:49:634 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1079:59:49:635 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: direct map ready
1082:59:49:636 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: skip startup video scan for gcmap route
1083:59:49:636 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: gcmap smoke frames begin
1084:59:49:637 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: gcmap smoke frames ready
1087:59:49:637 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=1464120 free=274568 unclaimed=16384 avail=290952
1088:59:49:637 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: solo listenserver active map=m1l2a (gcmap tip)
1102:59:49:649 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: livemap armed=0 (file absent)
1111:59:49:692 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: released unused nodes reserve 256 Kb
1112:59:49:692 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: released unused submodels reserve 16 Kb
1113:59:49:693 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: freed 126 menu/UI textures for map load
1114:59:49:693 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: GX HUD/menu slabs released for map load
1135:59:49:697 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: titles init skipped for gcmap smoke route
1140:59:49:700 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: client edicts using static gcmap bootstrap tables
1230:59:49:753 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: heap mark stage=client_module_ready used=1198368 free=540320 unclaimed=16384 avail=556704
1232:59:49:753 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1198368 free=540320 unclaimed=16384 avail=556704
1260:59:49:799 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: serverdata HUD vidinit deferred for local map route
1261:59:49:799 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: client edicts capped for map route max=460 requested=460
1262:59:49:800 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [00:59:49] Xash3D GameCube: serverdata map CRC skipped for local map route
```

- Full Dolphin log: `media/playtests/screenshots/20261124-005940-m1l2a-retail-objective-pos/dolphin.log.gz`
