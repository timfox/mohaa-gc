# MOHAA Probe m1l1-retail-newgame-pad — 20261124-012253

- ISO: `/tmp/mohaa-compass-build/mohaa-m1l1-retail-newgame-current.iso`
- Route: `m1l1-retail-newgame-pad`
- Duration cap: 65s
- Repo: `8d0887dca6`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261124-012253-m1l1-retail-newgame-pad/`
- Periodic guest frames: 16 screenshots in `media/playtests/screenshots/20261124-012253-m1l1-retail-newgame-pad/frames/`
- Video: `media/playtests/videos/20261124-012253-m1l1-retail-newgame-pad-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: 8d0887dca6. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-compass-build/mohaa-m1l1-retail-newgame-current.iso (SHA-256 7d5ae6e45f25556af88704fd7aca3b28859565159b3749f42d54a0e53b258e6f). GameCube retail MOHAA New Game path using the current DOL and `menunewgame`; deterministic Dolphin pad-pipe A presses select Allies and Rifleman. Capture whether the joined player starts inside the m1l1 intro truck.

## Frame stats
```
final.png: (640, 480) black=8.9% mean=(24, 25, 38)
menu-2.png: (640, 480) black=8.1% mean=(129, 129, 121)
menu.png: (640, 480) black=8.1% mean=(129, 129, 121)
```

## OSReport (key)
```
25:22:55:860 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: disc boot override startmap m1l1
36:22:56:069 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
37:22:56:070 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:55] Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
43:22:56:072 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: disc boot override startmap m1l1
64:22:56:173 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:55] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
93:22:56:836 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Program args: xash xash -dev 2 -log -game mohaa -gcmenuplaystart -gcfullactors -gcvideo prog -gcstartmap m1l1 -width 320 -height 240
138:22:56:876 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: released unused nodes reserve 256 Kb
139:22:56:876 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: released unused submodels reserve 16 Kb
191:22:56:920 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: heap mark stage=client_local_init_ready used=1186520 free=240872 unclaimed=327680 avail=568552
222:22:56:962 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=1196968 free=230424 unclaimed=327680 avail=558104
228:22:57:010 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: renderer screen map ready
231:22:57:012 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=1196968 free=230424 unclaimed=327680 avail=558104
240:22:57:016 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: heap mark stage=renderer_images_ready used=1197104 free=230288 unclaimed=327680 avail=557968
243:22:57:020 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: heap mark stage=renderer_init_ready used=1197184 free=230208 unclaimed=327680 avail=557888
256:22:57:035 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: heap mark stage=gameui_library_handle_ready used=1200928 free=226464 unclaimed=327680 avail=554144
265:22:57:038 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: heap mark stage=gameui_pfninit_ready used=1207736 free=219656 unclaimed=327680 avail=547336
280:22:57:057 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: gc_menu_ready set 0
292:22:57:086 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: mainui vidinit backgrounds listed
295:22:57:089 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Rendering Bitmap Font(18, 500) took 0.000064 seconds
298:22:57:089 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Rendering Bitmap Font(6, 500) took 0.000062 seconds
302:22:57:090 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: mainui vidinit background ready
304:22:57:090 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: gc_menu_ready set 1
306:22:57:090 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: heap mark stage=gameui_deferred_vidinit_ready used=1340888 free=160232 unclaimed=253952 avail=414184
308:22:57:091 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: heap mark stage=client_video_init_ready used=1340888 free=160232 unclaimed=253952 avail=414184
330:22:57:101 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=1345784 free=155336 unclaimed=253952 avail=409288
349:22:57:118 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: gcmap lookup begin
350:22:57:119 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: no gcmap argument
364:22:57:122 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=1350064 free=151056 unclaimed=253952 avail=405008
413:22:57:242 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: play start uses test start map m1l1
430:22:57:307 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: freed 2 menu/UI textures for map load
431:22:57:308 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: GX HUD/menu slabs released for map load
433:22:57:311 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: menu unloaded for map load
435:22:57:315 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: sound trimmed for map load
436:22:57:315 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: client subsystems trimmed for map load
442:22:57:316 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: renderer trim for map load
444:22:57:316 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: present buf released map load
449:22:57:317 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: play start map buffer ready m1l1
457:22:57:323 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: map load cfg skipped
460:22:57:330 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: pre-spawn mem map set
474:22:57:333 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: present buf released map load
476:22:57:334 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: server string arena spill dropped for map reload
485:22:57:335 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: pre-spawn map buffer prepared for m1l1
488:22:57:336 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:56] Xash3D GameCube: server string arena spill dropped for map reload
497:22:57:852 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:57] Xash3D GameCube: map load compact (no lighting, miptex headers only) 1.87 Mb 竊 1.22 Mb (G154 disc LM)
538:22:58:085 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:57] Xash3D GameCube: world surfedges copied 95.81 Kb to map tail
540:22:58:086 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:57] Xash3D GameCube: world faces copied 100.84 Kb to map tail
552:22:58:093 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:57] Xash3D GameCube: releasing gcmap BSP staging 1.22 Mb before surfaces
645:22:58:343 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:57] Xash3D GameCube: entity overflow reserved 65536 bytes in map arena
650:22:58:455 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:57] PM_WorldMesh: maps/m1l1.mcol, 0 brushes, 18 terrain patches, 13212 patch triangles, 388920 bytes in the map arena
1095:22:58:679 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:57] Xash3D GameCube: resource sync skipped for local map route
1097:22:58:685 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:57] Xash3D GameCube: retaining map arena for entity private data
1102:22:58:688 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:57] Xash3D GameCube: renderer restore after map load
1103:22:58:688 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:57] Xash3D GameCube: map loaded m1l1
1104:22:58:689 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1106:22:58:690 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:57] Xash3D GameCube: budget moved entity text to map leftover (20.53 Kb), entity reserve returned, heap free 349.42 Kb
1107:22:58:702 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:57] Xash3D GameCube: mem stage=map active total=236.02 Kb delta=4.46 Kb hwm=236.02 Kb map=m1l1 heap_used=1.33 Mb heap_free=297.42 Kb unclaimed=52 Kb
1108:22:58:703 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:57] Xash3D GameCube: mem pools at=map active live=20 slots=20 small=5755 Zone Engine=93829 BaseCmd=42616 Console Commands=12631 Console Variables=23324 FileSystem Pool=39514 Server Strings=4661 maps/m1l1.bsp=19359
1110:22:58:704 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:57] Xash3D GameCube: budget texture region at=map active bytes=0 bytes live=0 bytes arena_usable=3.69 Mb
1111:22:58:705 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:57] Xash3D GameCube: direct-map player prime begin edict=1
1127:22:58:712 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:22:57] Xash3D GameCube: direct-map player prime ready edict=1 private=0x80acd510 origin=(-1918,-3137,179)
```

- Full Dolphin log: `media/playtests/screenshots/20261124-012253-m1l1-retail-newgame-pad/dolphin.log.gz`
