#!/usr/bin/env bash
# Tim's play session: MOHAA (mohaa gamedir) with the retail loading screens on the disc. Visible window, sound on.
W=/run/media/tim/Stream/mohaa-loadscreen-20261122
ISO=${1:-$W/discs/discA-loadscreen.iso}
U=$W/play-user
mkdir -p "$U/Config"
P=$HOME/.local/share/dod-gc/dolphin/Config
for f in GCPadNew.ini GFX.ini Hotkeys.ini; do [[ -f $P/$f && ! -f $U/Config/$f ]] && cp "$P/$f" "$U/Config/"; done
cat > "$U/Config/Dolphin.ini" <<E2
[Core]
CPUCore = 1
CPUThread = True
DSPHLE = True
FastDiscSpeed = True
MMU = True
AccurateCPUCache = True
SIDevice0 = 6
SlotB = 255
SerialPort1 = 255
[DSP]
Muted = False
Volume = 100
[Interface]
ConfirmStop = False
[Display]
KeepWindowOnTop = False
[Analytics]
PermissionAsked = True
Enabled = False
E2
cat > "$U/Config/Logger.ini" <<'E2'
[Logs]
BOOT = True
OSREPORT = True
OSREPORT_HLE = True
[Options]
Verbosity = 4
WriteToConsole = True
WriteToFile = False
WriteToWindow = False
E2
export EGL_PLATFORM=x11 QT_QPA_PLATFORM=xcb DISPLAY=${DISPLAY:-:0}; unset WAYLAND_DISPLAY
exec /home/tim/xash3d-gc-hl1/3rdparty/dolphin/build/Binaries/dolphin-emu -u "$U" -b -e "$ISO" > "$W/play-$(date +%H%M%S).log" 2>&1
