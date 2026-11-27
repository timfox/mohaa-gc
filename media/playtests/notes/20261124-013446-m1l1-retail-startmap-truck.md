# MOHAA Probe m1l1-retail-startmap-truck — 20261124-013446

- ISO: `/tmp/mohaa-compass-build/mohaa-m1l1-retail-startmap-current.iso`
- Route: `m1l1-retail-startmap-truck`
- Duration cap: 90s
- Repo: `8d0887dca6`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261124-013446-m1l1-retail-startmap-truck/`
- Periodic guest frames: 88 screenshots in `media/playtests/screenshots/20261124-013446-m1l1-retail-startmap-truck/frames/`
- Video: `media/playtests/videos/20261124-013446-m1l1-retail-startmap-truck-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: 8d0887dca6. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-compass-build/mohaa-m1l1-retail-startmap-current.iso (SHA-256 96eb93fad2b61476ef88fe1fc9adddfeca9107adc423a71acb0fe4f655726c6e). Retail MainUI boot with current MOHAA DOL and explicit gamecube.cfg startmap m1l1. Engine auto-selects New Game from the retail menu; capture the normal single-player intro without gcmap/listenserver smoke routing.

## Frame stats
```
menu-2.png: (640, 480) black=8.9% mean=(32, 35, 53)
menu.png: (640, 480) black=8.8% mean=(32, 35, 52)
```

## OSReport (key)
```
24:34:47:695 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: disc boot override startmap m1l1
35:34:47:903 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
36:34:47:903 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:47] Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
41:34:47:905 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: disc boot override startmap m1l1
62:34:48:005 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:47] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
91:34:48:671 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Program args: xash xash -dev 2 -log -game mohaa -gcvideo prog -gcstartmap m1l1 -width 320 -height 240
136:34:48:711 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: released unused nodes reserve 256 Kb
137:34:48:711 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: released unused submodels reserve 16 Kb
148:34:48:725 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: server game init deferred until map load
153:34:48:732 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: heap mark stage=client_local_init_ready used=1151736 free=275656 unclaimed=327680 avail=603336
182:34:48:771 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=1162176 free=265216 unclaimed=327680 avail=592896
190:34:48:813 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: renderer screen map ready
193:34:48:814 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=1162176 free=265216 unclaimed=327680 avail=592896
202:34:48:815 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: heap mark stage=renderer_images_ready used=1162312 free=265080 unclaimed=327680 avail=592760
205:34:48:817 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: heap mark stage=renderer_init_ready used=1162392 free=265000 unclaimed=327680 avail=592680
218:34:48:825 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: heap mark stage=gameui_library_handle_ready used=1166144 free=261248 unclaimed=327680 avail=588928
227:34:48:829 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: heap mark stage=gameui_pfninit_ready used=1172944 free=254448 unclaimed=327680 avail=582128
242:34:48:906 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: gc_menu_ready set 0
254:34:48:944 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: mainui vidinit backgrounds listed
257:34:48:946 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Rendering Bitmap Font(18, 500) took 0.000064 seconds
260:34:48:947 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Rendering Bitmap Font(6, 500) took 0.000062 seconds
264:34:48:947 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: mainui vidinit background ready
266:34:48:948 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: gc_menu_ready set 1
268:34:48:948 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: heap mark stage=gameui_deferred_vidinit_ready used=1371808 free=162080 unclaimed=221184 avail=383264
270:34:48:949 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: heap mark stage=client_video_init_ready used=1371808 free=162080 unclaimed=221184 avail=383264
292:34:48:955 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=1376704 free=157184 unclaimed=221184 avail=378368
311:34:48:968 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: gcmap lookup begin
312:34:48:968 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: no gcmap argument
326:34:48:972 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=1380984 free=152904 unclaimed=221184 avail=374088
344:34:49:124 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] LoadBackground: found steam background in game directory
345:34:49:125 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:34:48] Xash3D GameCube: retail menu steam background ready tiles=4
410:34:49:439 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: G197 CopyDisp ok fb=640 efb=480 xfb=480 stride=640 xfb_k1=1 crt_vf=0
```

- Full Dolphin log: `media/playtests/screenshots/20261124-013446-m1l1-retail-startmap-truck/dolphin.log.gz`
