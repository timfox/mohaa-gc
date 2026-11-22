#!/usr/bin/env bash
# One recorded Dolphin run of a menu disc: boot -> menu -> New Game (A) -> Create Game Done (A) -> map load -> gameplay.
# usage: run-load.sh <iso> <name> [max_seconds]
# Own Dolphin user dir, muted. Pad 1 is a Dolphin input pipe. Writes runs/<name>/:
#   <name>.mp4 (window capture from launch), <name>.log (OSReport on stdout, flushed),
#   stills/ (window grab every 0.5 s from the first A press to gameplay + 6 s), run.txt (timing).
set -u
ISO=$(readlink -f "$1"); NAME=$2; SECS=${3:-150}
W=/run/media/tim/Stream/mohaa-loadscreen-20261122
OUT=$W/runs/$NAME
DOL=/home/tim/xash3d-gc-hl1/3rdparty/dolphin/build/Binaries/dolphin-emu
U=$OUT/user
rm -rf "$OUT"; mkdir -p "$U/Config" "$U/Pipes" "$OUT/stills"
mkfifo "$U/Pipes/pad"
cat > "$U/Config/Dolphin.ini" <<EOF
[Core]
CPUCore = 1
CPUThread = True
DSPHLE = True
FastDiscSpeed = True
MMU = True
AccurateCPUCache = True
SIDevice0 = 6
SlotA = 255
SlotB = 255
SerialPort1 = 255
[DSP]
Muted = True
Volume = 0
[Interface]
ConfirmStop = False
UsePanicHandlers = False
[Display]
KeepWindowOnTop = False
[Input]
BackgroundInput = True
[Analytics]
PermissionAsked = True
Enabled = False
EOF
cat > "$U/Config/GFX.ini" <<'EOF'
[Settings]
Backend = OGL
ShowFPS = False
EOF
cat > "$U/Config/Logger.ini" <<'EOF'
[Logs]
BOOT = True
OSREPORT = True
OSREPORT_HLE = True
[Options]
Verbosity = 4
WriteToConsole = True
WriteToFile = False
WriteToWindow = False
EOF
cat > "$U/Config/GCPadNew.ini" <<'EOF'
[GCPad1]
Device = Pipe/0/pad
Buttons/A = `Button A`
Buttons/B = `Button B`
Buttons/Start = `Button START`
D-Pad/Up = `Button D_UP`
D-Pad/Down = `Button D_DOWN`
D-Pad/Left = `Button D_LEFT`
D-Pad/Right = `Button D_RIGHT`
Main Stick/Up = `Axis MAIN Y -`
Main Stick/Down = `Axis MAIN Y +`
Main Stick/Left = `Axis MAIN X -`
Main Stick/Right = `Axis MAIN X +`
C-Stick/Up = `Axis C Y -`
C-Stick/Down = `Axis C Y +`
C-Stick/Left = `Axis C X -`
C-Stick/Right = `Axis C X +`
EOF

export EGL_PLATFORM=x11 QT_QPA_PLATFORM=xcb DISPLAY=${DISPLAY:-:0}
unset WAYLAND_DISPLAY
LOG=$OUT/$NAME.log
exec 3<>"$U/Pipes/pad"
echo "SET MAIN 0.5 0.5" >&3; echo "SET C 0.5 0.5" >&3
"$DOL" -u "$U" -b -e "$ISO" > "$LOG" 2>&1 &
DPID=$!
T0=$(date +%s.%N)
rel() { echo "$(date +%s.%N) - $T0" | bc; }
WIN=
for _ in $(seq 1 120); do
	WIN=$(xwininfo -root -tree 2>/dev/null | grep -F '("dolphin-emu" "GameCube")' | grep -v ' 800x600' | grep -E ' [0-9]{3,}x[0-9]{3,}\+' | awk '{print $1}' | while read -r w; do
		p=$(xprop -id "$w" _NET_WM_PID 2>/dev/null | awk -F' = ' '{print $2}'); [[ "$p" == "$DPID" ]] && echo "$w"; done | head -1)
	if [[ -n "$WIN" ]] && xwininfo -id "$WIN" 2>/dev/null | awk '/Map State: IsViewable/{v=1}/Absolute upper-left X/{x=$4}/Width:/{w=$2}END{exit !(v && x>0 && w>=300)}'; then
		sleep 1; xwininfo -id "$WIN" >/dev/null 2>&1 && break
	fi
	WIN=; sleep 0.5
done
echo "window=$WIN" > "$OUT/run.txt"
ffmpeg -v error -y -thread_queue_size 512 -f x11grab -draw_mouse 0 -framerate 30 -window_id "$WIN" -i "$DISPLAY" \
	-vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p \
	-t "$SECS" "$OUT/$NAME.mp4" < /dev/null > "$OUT/ffmpeg.txt" 2>&1 &
FPID=$!
echo "rec_start=$(rel)" >> "$OUT/run.txt"
has() { tr -d '\000' < "$LOG" | grep -a -q -E "$1"; }
press() { echo "PRESS $1" >&3; sleep 0.2; echo "RELEASE $1" >&3; echo "press_$1=$(rel)" >> "$OUT/run.txt"; sleep "${2:-0.5}"; }
shooter() { local i=0; while kill -0 $DPID 2>/dev/null && [[ ! -f "$OUT/stop-shots" ]]; do
	import -window "$WIN" "$OUT/stills/$(printf '%04d' $i)-$(rel | xargs printf '%06.2f').png" 2>/dev/null; i=$((i+1)); sleep 0.4; done; }
# menu
for _ in $(seq 1 120); do has 'gc_menu_ready set 1|retail menu (steam )?background ready' && break; has 'FATAL|fatal message' && break; sleep 1; done
echo "menu_ready=$(rel)" >> "$OUT/run.txt"
sleep 3
import -window "$WIN" "$OUT/menu.png"
press D_DOWN 0.3; press D_UP 0.5
press A 2.0                        # New game -> Create Game panel
import -window "$WIN" "$OUT/creategame.png"
shooter & SPID=$!
press A 0.5                        # Done -> start the local match
# until gameplay (or timeout), answering team select with A
end=$(( $(date +%s) + SECS - 30 )); sel=0; done_at=
while (( $(date +%s) < end )) && kill -0 $DPID 2>/dev/null; do
	if (( !sel )) && has 'CapFaces team select UI'; then sleep 1; press A 0.3; sel=1; fi
	if has 'newgame world render SCR frames=8|direct map ready|MAP READY'; then done_at=$(rel); break; fi
	has 'FATAL|fatal message|out of memory' && break
	sleep 0.5
done
echo "gameplay_marker=$done_at" >> "$OUT/run.txt"
sleep 8
touch "$OUT/stop-shots"; wait $SPID 2>/dev/null
import -window "$WIN" "$OUT/final.png"
kill -INT $FPID 2>/dev/null; wait $FPID 2>/dev/null
kill $DPID 2>/dev/null; sleep 2; kill -9 $DPID 2>/dev/null
exec 3>&-
rm -rf "$U"
cat "$OUT/run.txt"
