# MOHAA Probe m1l1-mainui-newgame-hud — 20261124-032257

- ISO: `/tmp/mohaa-hud-refine/out/mohaa-m1l1-mainui-newgame-hud.iso`
- Route: `m1l1-mainui-newgame-hud`
- Duration cap: 90s
- Repo: `ebf188540a`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261124-032257-m1l1-mainui-newgame-hud/`
- Periodic guest frames: 1 screenshots in `media/playtests/screenshots/20261124-032257-m1l1-mainui-newgame-hud/frames/`
- Video: `media/playtests/videos/20261124-032257-m1l1-mainui-newgame-hud-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: ebf188540a. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-hud-refine/out/mohaa-m1l1-mainui-newgame-hud.iso (SHA-256 a3837284b36fa60295ebb9a0d9f92be6132ea98cd26e96f2ab331f29906feb8d). Full-retail MainUI New Game route with intro=1, low-memory profile, and MOHAA compass arrow deferred until objective target.

## Frame stats
```
final.png: (640, 480) black=9.0% mean=(25, 26, 38)
menu-2.png: (640, 480) black=9.0% mean=(25, 26, 38)
menu.png: (640, 480) black=8.1% mean=(130, 131, 123)
```

## OSReport (key)
```
34:23:00:152 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=mohaa
35:23:00:153 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:22:59] Xash3D GameCube: linked gamedir=mohaa detected=mohaa
60:23:00:204 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:22:59] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
115:23:00:994 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: released unused nodes reserve 256 Kb
116:23:00:994 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: released unused submodels reserve 16 Kb
168:23:01:054 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: heap mark stage=client_local_init_ready used=1175680 free=247840 unclaimed=8192 avail=256032
199:23:01:102 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=1186144 free=237376 unclaimed=8192 avail=245568
205:23:01:140 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: renderer screen map ready
208:23:01:141 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=1186144 free=237376 unclaimed=8192 avail=245568
217:23:01:142 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: heap mark stage=renderer_images_ready used=1186280 free=237240 unclaimed=8192 avail=245432
220:23:01:143 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: heap mark stage=renderer_init_ready used=1186360 free=237160 unclaimed=8192 avail=245352
232:23:01:269 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: heap mark stage=gameui_library_handle_ready used=1190104 free=233416 unclaimed=8192 avail=241608
241:23:01:272 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: heap mark stage=gameui_pfninit_ready used=1196904 free=226616 unclaimed=8192 avail=234808
257:23:01:289 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: gc_menu_ready set 0
269:23:01:326 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: mainui vidinit backgrounds listed
272:23:01:328 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Rendering Bitmap Font(18, 500) took 0.000064 seconds
275:23:01:328 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Rendering Bitmap Font(6, 500) took 0.000061 seconds
279:23:01:329 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: mainui vidinit background ready
281:23:01:329 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: gc_menu_ready set 1
283:23:01:329 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: heap mark stage=gameui_deferred_vidinit_ready used=1297256 free=126264 unclaimed=8192 avail=134456
285:23:01:330 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: heap mark stage=client_video_init_ready used=1297256 free=126264 unclaimed=8192 avail=134456
307:23:01:340 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=1302152 free=121368 unclaimed=8192 avail=129560
326:23:01:350 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: gcmap lookup begin
327:23:01:350 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: no gcmap argument
336:23:01:353 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=1306432 free=117088 unclaimed=8192 avail=125280
399:23:01:507 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: freed 2 menu/UI textures for map load
400:23:01:508 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: GX HUD/menu slabs released for map load
402:23:01:510 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: menu unloaded for map load
404:23:01:512 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: sound trimmed for map load
405:23:01:512 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: client subsystems trimmed for map load
412:23:01:513 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: renderer trim for map load
414:23:01:513 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: present buf released map load
419:23:01:514 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: play start map buffer ready m1l1
427:23:01:518 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: map load cfg skipped
430:23:01:522 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: pre-spawn mem map set
444:23:01:526 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: present buf released map load
446:23:01:526 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: server string arena spill dropped for map reload
455:23:01:528 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: pre-spawn map buffer prepared for m1l1
458:23:01:528 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:00] Xash3D GameCube: server string arena spill dropped for map reload
467:23:02:037 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:01] Xash3D GameCube: map load compact (no lighting, miptex headers only) 1.87 Mb 竊 1.22 Mb (G154 disc LM)
508:23:02:268 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:01] Xash3D GameCube: world surfedges copied 95.81 Kb to map tail
510:23:02:269 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:01] Xash3D GameCube: world faces copied 100.84 Kb to map tail
522:23:02:277 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:01] Xash3D GameCube: releasing gcmap BSP staging 1.22 Mb before surfaces
617:23:02:519 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:01] Xash3D GameCube: entity overflow reserved 65536 bytes in map arena
622:23:02:638 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:01] PM_WorldMesh: maps/m1l1.mcol, 0 brushes, 18 terrain patches, 13212 patch triangles, 388920 bytes in the map arena
1069:23:02:805 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:02] Xash3D GameCube: resource sync skipped for local map route
1071:23:02:808 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:02] Xash3D GameCube: retaining map arena for entity private data
1076:23:02:809 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:02] Xash3D GameCube: renderer restore after map load
1077:23:02:809 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:02] Xash3D GameCube: map loaded m1l1
1078:23:02:809 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1080:23:02:810 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:02] Xash3D GameCube: budget moved entity text to map leftover (20.53 Kb), entity reserve returned, heap free 303.29 Kb
1081:23:02:816 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:02] Xash3D GameCube: mem stage=map active total=221.70 Kb delta=4.46 Kb hwm=221.70 Kb map=m1l1 heap_used=1.07 Mb heap_free=295.29 Kb unclaimed=8 Kb
1082:23:02:817 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:02] Xash3D GameCube: mem pools at=map active live=17 slots=17 small=4335 Zone Engine=93829 BaseCmd=42616 Console Commands=12631 Console Variables=23324 FileSystem Pool=26262 Server Strings=4661 maps/m1l1.bsp=19359
1083:23:02:817 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:02] Xash3D GameCube: budget texture region at=map active bytes=0 bytes live=0 bytes arena_usable=3.69 Mb
1084:23:02:818 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:02] Xash3D GameCube: direct-map player prime begin edict=1
1100:23:02:820 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:02] Xash3D GameCube: direct-map player prime ready edict=1 private=0x80b1c410 origin=(-1918,-3137,179)
1101:23:02:821 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:02] Xash3D GameCube: direct-map loopback netchan initialized
1102:23:02:822 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:02] Xash3D GameCube: direct-map queued 35 user message regs overflow=0
1103:23:02:822 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:23:02] Xash3D GameCube: direct-map client ready cs_spawned frames=0x80ac9aa0
1108:23:02:822 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
```

- Full Dolphin log: `media/playtests/screenshots/20261124-032257-m1l1-mainui-newgame-hud/dolphin.log.gz`
