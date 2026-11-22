#!/usr/bin/env bash
# Package MEM1-friendly lean DoD discs into out/ (does not touch HL1 ISOs).
# Uses stage-lean-dod.sh + existing out/dodgc.dol.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/env.sh"

usage() {
	cat <<'EOF'
usage: scripts/build-lean-iso.sh [options]

  --menu-only      only out/dodgc-menu.iso (Valve intro + DoD menu)
  --intro-only     only out/dodgc.iso (same lean tree; larger full pack path)
  --skip-startup-vids
                   omit Valve intro AVI/gcvid (faster menu-only smoke)
  --net            stage gamecube.cfg "net" for early BBA/eth2sp1 DHCP (-net)
  --map NAME       stage one BSP into lean maps/ (DoD or valve)
  --smoke MAP      disc --smoke-map MAP (auto map load; implies staging MAP)
  --listen MAP     playable listen host (local player plus one peer)
  --headless       server only; requires --listen (optional third Cube)
  --connect ADDR   peer client (gamecube.cfg connect ADDR); use with --net
  --net-ip IP      static IPv4 address (DHCP when omitted)
  --net-mask MASK  static subnet mask (default 255.255.255.0)
  --net-gateway IP static router address (default same subnet .1)
  --full-map       stage BSP-referenced mapmodels (capped) + lean HUD; not the prop farm
  --all-maps-audio stage every map's soundscape/ambient WAVs + menu music/UI
  --core-sfx       opt-in weapons/player/ui/items/... WAV trees (OOMs menu if always on)
  --world-render   render the BSP world in menu or gameplay sessions (default)
  --no-world-render
                   leave the BSP world hidden for diagnostic sessions
  --dumpframes     gamecube.cfg dumpframes (-gcdumpframes stills; with --smoke)
  --dumpeye "x y z [pitch] [yaw]"
                   CapFaces camera override in gamecube.cfg (spawn atlas)
  --tas NAME       stage dod/tas/NAME.tas + gamecube.cfg tas NAME (pad replay)
  --film DIR       stage a film plan (from a film plan): DIR/cine/*.cam onto the disc and
                   DIR/film-<map>.cfg into listenserver.cfg, so the listen map plays its shots; needs --listen.
                   DIR/models/player/<body>/<body>.mdl, when there, replaces that team body on this disc
  --skip-stage     reuse existing lean cache trees
  -h, --help

Requires out/dodgc.dol (scripts/build-intro-dod-menu.sh or build-dodgc.sh --dol-only).
EOF
}

MENU=1
INTRO=1
SKIP_STAGE=0
SKIP_STARTUP_VIDS=0
WANT_NET=0
FULL_MAP=0
WORLD_RENDER=1
WORLD_RENDER_EXPLICIT=0
DUMPFRAMES=0
DUMPEYE=""
TAS=""
FILM=""
MAP=""
SMOKE=""
LISTEN=""
CONNECT=""
NET_IP=""
NET_MASK="255.255.255.0"
NET_GW=""
HEADLESS=0
STAGE_ARGS=()

while [[ $# -gt 0 ]]; do
	case "$1" in
		--menu-only) INTRO=0; MENU=1 ;;
		--intro-only) INTRO=1; MENU=0 ;;
		--skip-startup-vids) SKIP_STARTUP_VIDS=1 ;;
		--net) WANT_NET=1 ;;
		--headless) HEADLESS=1 ;;
		--net-mask) NET_MASK="${2:?--net-mask needs MASK}"; shift ;;
		--net-gateway) NET_GW="${2:?--net-gateway needs IP}"; shift ;;
		--full-map) FULL_MAP=1; STAGE_ARGS+=(--full-map) ;;
		--all-maps-audio) STAGE_ARGS+=(--all-maps-audio) ;;
		--core-sfx) STAGE_ARGS+=(--core-sfx) ;;
		--world-render) WORLD_RENDER=1; WORLD_RENDER_EXPLICIT=1 ;;
		--no-world-render) WORLD_RENDER=0; WORLD_RENDER_EXPLICIT=1 ;;
		--dumpframes) DUMPFRAMES=1 ;;
		--dumpeye)
			DUMPEYE="${2:-}"
			[[ -n "$DUMPEYE" ]] || { echo "error: --dumpeye needs coords" >&2; exit 2; }
			shift
			;;
		--tas)
			TAS="${2:-}"
			[[ -n "$TAS" ]] || { echo "error: --tas needs NAME" >&2; exit 2; }
			if [[ "$TAS" == */* || "$TAS" == *\\* || "$TAS" == *.* ]]; then
				echo "error: --tas NAME must be a simple token" >&2
				exit 2
			fi
			shift
			;;
		--net-ip)
			NET_IP="${2:-}"
			[[ -n "$NET_IP" ]] || { echo "error: --net-ip needs IP" >&2; exit 2; }
			shift
			;;
		--map) MAP="${2:-}"; shift; STAGE_ARGS+=(--map "$MAP") ;;
		--smoke)
			SMOKE="${2:-}"
			[[ -n "$SMOKE" ]] || { echo "error: --smoke needs a map" >&2; exit 2; }
			MAP="$SMOKE"
			STAGE_ARGS+=(--map "$SMOKE")
			shift
			;;
		--listen)
			LISTEN="${2:-}"
			[[ -n "$LISTEN" ]] || { echo "error: --listen needs a map" >&2; exit 2; }
			MAP="$LISTEN"
			STAGE_ARGS+=(--map "$LISTEN")
			shift
			;;
		--connect)
			CONNECT="${2:-}"
			[[ -n "$CONNECT" ]] || { echo "error: --connect needs ADDR" >&2; exit 2; }
			shift
			;;
		--film)
			FILM="${2:-}"
			[[ -d "$FILM/cine" ]] || { echo "error: --film needs a plan directory with cine/ (from a film plan)" >&2; exit 2; }
			shift
			;;
		--skip-stage) SKIP_STAGE=1 ;;
		-h|--help) usage; exit 0 ;;
		*) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
	esac
	shift
done

# Keep discs without a staged map lightweight; map-bearing play builds render
# CapFaces by default so Create Game can use its packed BSP path and lean mode.
if [[ -z "$MAP" && "$WORLD_RENDER_EXPLICIT" -eq 0 ]]; then
	WORLD_RENDER=0
fi
if (( DUMPFRAMES )) && [[ -z "$SMOKE" && -z "$LISTEN" && -z "$CONNECT" ]]; then
	echo "error: --dumpframes requires --smoke, --listen, or --connect" >&2
	exit 2
fi
if (( WORLD_RENDER )) && [[ -z "$MAP" ]]; then
	echo "error: --world-render needs a staged map (--map, --smoke, or --listen)" >&2
	exit 2
fi
if [[ -n "$SMOKE" && -n "$LISTEN" ]]; then
	echo "error: --smoke and --listen are mutually exclusive" >&2
	exit 2
fi
if [[ -n "$LISTEN" && -n "$CONNECT" ]]; then
	echo "error: --listen and --connect are mutually exclusive" >&2
	exit 2
fi
if [[ -n "$CONNECT" && $WANT_NET -eq 0 ]]; then
	echo "error: --connect requires --net" >&2
	exit 2
fi
if [[ -n "$NET_IP" && $WANT_NET -eq 0 ]]; then
	WANT_NET=1
fi

if [[ -n "$FILM" && -z "$LISTEN" ]]; then
	echo "error: --film requires --listen MAP" >&2; exit 2
fi
if (( HEADLESS )) && [[ -z "$LISTEN" ]]; then
	echo "error: --headless requires --listen" >&2; exit 2
fi
# Validate before staging or invoking disc tooling. Derive a conventional router
# only for explicit /24 addresses; other subnets must supply their gateway.
if [[ -n "$NET_IP" ]]; then
	if [[ -z "$NET_GW" ]]; then
		[[ "$NET_MASK" == 255.255.255.0 ]] || { echo "error: supply --net-gateway with a non-/24 mask" >&2; exit 2; }
		NET_GW="${NET_IP%.*}.1"
	fi
	python3 - "$NET_IP" "$NET_MASK" "$NET_GW" <<'PYNET'
import ipaddress, sys
try:
    ip, mask, gateway = sys.argv[1:]
    address = ipaddress.IPv4Address(ip)
    network = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
    router = ipaddress.IPv4Address(gateway)
    assert network.prefixlen in range(1, 31)
    assert address not in (network.network_address, network.broadcast_address)
    assert not address.is_multicast and not address.is_loopback and int(address) >> 24 != 0
    assert int(router) != 0 and router in network and router not in (network.network_address, network.broadcast_address, address)
except (ValueError, AssertionError):
    sys.exit("error: invalid static IPv4 address, mask or gateway")
PYNET
elif [[ -n "$NET_GW" || "$NET_MASK" != 255.255.255.0 ]]; then
	echo "error: --net-mask/--net-gateway require --net-ip" >&2; exit 2
fi

write_net_config() {
	if [[ -n "$NET_IP" ]]; then
		printf 'netstatic %s %s %s\n' "$NET_IP" "$NET_MASK" "$NET_GW"
	else
		echo net
	fi
}

dodgc_require_content
[[ -f "$DODGC_DOL" ]] || {
	echo "error: missing $DODGC_DOL — build DOL first" >&2
	exit 1
}
bash "$SCRIPT_DIR/check-menu-provenance.sh" --dol "$DODGC_DOL" || exit 1

if (( ! SKIP_STAGE )); then
	bash "$SCRIPT_DIR/stage-lean-dod.sh" "${STAGE_ARGS[@]+"${STAGE_ARGS[@]}"}"
fi

LEAN="${DODGC_LEAN_DOD:-$XASH3D_GC_ISO_CACHE/dod-menu-min}"
VMIN="${DODGC_LEAN_VALVE:-$XASH3D_GC_ISO_CACHE/valve-menu-min}"
[[ -d "$LEAN" ]] || { echo "error: lean DoD tree missing: $LEAN" >&2; exit 1; }
[[ -d "$VMIN" ]] || { echo "error: lean valve tree missing: $VMIN" >&2; exit 1; }

# mohaa: the disc's primary game folder is mohaa/, holding only our own text (gameinfo.txt,
# liblist.gam, gamecube.cfg, the intro playlist). Everything converted from the player's MOHAA is
# read from sd:/xash3d/mohaa/ (tools/mohaa_sd.py); the lean DoD and valve trees go on as dod/ and
# valve/, which mohaa falls back to. Dolphin cannot emulate the SD adapter, so a test disc can carry
# converted content in mohaa/ with DODGC_MOHAA_TEST_DIR=<converter output>/xash3d/mohaa (never a
# release disc).
GDATA="$LEAN"
if [[ "$DODGC_GAME" == mohaa ]]; then
	GDATA="$XASH3D_GC_ISO_CACHE/mohaa-disc"
	rm -rf "$GDATA"
	mkdir -p "$GDATA/media" "$GDATA/maps"
	python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import mohaa_sd; mohaa_sd.write_gameinfo(sys.argv[2], "mohaa")' \
		"$DODGC_ROOT/../tools" "$GDATA" >/dev/null
	# The bootstrap pk3 is built from this folder, and the engine reads delta.lst from it: without it a
	# map load on mohaa dies with "Delta_InitFields: couldn't load file delta.lst" (the DoD copy in dod/
	# is found, but its DIR read fails for memory at that point).
	cp -f "$LEAN/delta.lst" "$GDATA/delta.lst"
	# GCube_HasGameAssets wants liblist.gam and a maps/ folder in the game folder.
	printf 'MOHAA maps are read from sd:/xash3d/mohaa/maps/ (tools/mohaa_sd.py).\n' > "$GDATA/maps/README.txt"
	[[ ! -f "$LEAN/media/StartupVids.txt" ]] || cp -f "$LEAN/media/StartupVids.txt" "$GDATA/media/StartupVids.txt"
	# The disc builder bakes the menu sheet and logo banner (resource/gc_menu/) from the primary game
	# folder. Give it DoD's menu sources, or mohaa/ gets the synthetic sheet (a white block for a
	# logo) on top of dod's. The converter's menu stage on the SD card overrides this with MOHAA's own.
	if [[ -d "$LEAN/resource" ]]; then
		mkdir -p "$GDATA/resource"
		rsync -a "$LEAN/resource/" "$GDATA/resource/"
	fi
	[[ ! -f "$LEAN/media/logo.avi" ]] || cp -f "$LEAN/media/logo.avi" "$GDATA/media/"
	if [[ -n "${DODGC_MOHAA_TEST_DIR:-}" ]]; then
		[[ -d "$DODGC_MOHAA_TEST_DIR" ]] || { echo "error: DODGC_MOHAA_TEST_DIR missing: $DODGC_MOHAA_TEST_DIR" >&2; exit 1; }
		rsync -a --exclude '.mohaa-work' --exclude 'gameinfo.txt' --exclude 'liblist.gam' \
			"$DODGC_MOHAA_TEST_DIR/" "$GDATA/"
		echo "==> TEST DISC: MOHAA data from $DODGC_MOHAA_TEST_DIR on the disc (not for release)"
	fi
	echo "==> game folder: mohaa/ over dod/ ($(find "$GDATA" -type f | wc -l) files)"
fi

# Film plan: camera paths under cine/ and a marked block at the end of listenserver.cfg. Both are
# cleared on every build, so a disc built without --film carries neither.
FILM_BEGIN="// >>> film block (build-lean-iso.sh --film)"
FILM_END="// <<< film block"
rm -rf "$LEAN/cine"
# Team bodies a film plan brings (the retail model with extra sequences appended). The lean tree never
# stages player bodies of its own (the disc builder reads the retail ones), so this folder only ever
# holds a plan's, and a disc built without --film goes back to retail.
rm -rf "$LEAN/models/player"
# The two team gib models (allied_gibs/axis_gibs, about 54 KB each): every disc carries them, for the live
# gibs a death throws (DodGC_PrecacheGibs, loaded on demand) and the film deaths by a shell burst
# (dod_film_actor.cpp DodFilm_Gibs).
for g in allied_gibs.mdl axis_gibs.mdl; do
	if [[ -f "$DODGC_CONTENT_DOD/models/$g" ]]; then
		mkdir -p "$LEAN/models"
		cp -f "$DODGC_CONTENT_DOD/models/$g" "$LEAN/models/"
	else
		echo "warning: $DODGC_CONTENT_DOD/models/$g missing; deaths will not gib with the side's own model" >&2
	fi
done
# Our own cinematic vehicle models (tools/vehicle/obj_to_mdl.py: content/gopex/models/film/<name>.mdl, a
# cast's "vehicle <name> models/film/<name>.mdl"). Only a film disc carries them.
rm -rf "$LEAN/models/film"
if [[ -f "$LEAN/listenserver.cfg" ]]; then
	awk -v b="$FILM_BEGIN" -v e="$FILM_END" '$0==b{skip=1;next} $0==e{skip=0;next} !skip' \
		"$LEAN/listenserver.cfg" > "$LEAN/listenserver.cfg.tmp"
	mv -f "$LEAN/listenserver.cfg.tmp" "$LEAN/listenserver.cfg"
fi
if [[ -n "$FILM" ]]; then
	film_cfg="$FILM/film-$(echo "$LISTEN" | tr '[:upper:]' '[:lower:]').cfg"
	[[ -f "$film_cfg" ]] || { echo "error: $film_cfg missing: the plan has no shots on $LISTEN" >&2; exit 2; }
	mkdir -p "$LEAN/cine"
	cp -f "$FILM"/cine/*.cam "$LEAN/cine/"
	# actors: each shot's cast, and the sides whose player models this map precaches for them
	cp -f "$FILM"/cine/*.act "$LEAN/cine/" 2>/dev/null || true
	cast_list="$FILM/cine/cast-$(echo "$LISTEN" | tr '[:upper:]' '[:lower:]').txt"
	[[ -f "$cast_list" ]] && cp -f "$cast_list" "$LEAN/cine/cast.txt"
	if [[ -d "$FILM/models/player" ]]; then
		mkdir -p "$LEAN/models/player"
		cp -rf "$FILM/models/player/." "$LEAN/models/player/"
		echo "==> film: $(find "$LEAN/models/player" -name '*.mdl' | wc -l) team body model(s) from the plan"
	fi
	gopex_film="$SCRIPT_DIR/../content/gopex/models/film"
	if compgen -G "$gopex_film/*.mdl" > /dev/null; then
		mkdir -p "$LEAN/models/film"
		cp -f "$gopex_film"/*.mdl "$LEAN/models/film/"
		echo "==> film: $(ls "$LEAN/models/film"/*.mdl | wc -l) vehicle model(s) from content/gopex"
	fi
	{ echo "$FILM_BEGIN"; cat "$film_cfg"; echo "$FILM_END"; } >> "$LEAN/listenserver.cfg"
	echo "==> film: $(ls "$LEAN/cine"/*.cam | wc -l) camera path(s), $(ls "$LEAN/cine"/*.act 2>/dev/null | wc -l) cast(s), session $(basename "$film_cfg")"
fi

# What this disc was built from: the short form goes on the disc (the engine prints it in the boot
# log), the full report next to the other artifacts.
bash "$SCRIPT_DIR/build-info.sh" --short > "$LEAN/build-info.txt"
bash "$SCRIPT_DIR/build-info.sh" > "$DODGC_OUT/build-info.txt"

pack() {
	local mode=$1
	local out=$2
	local tmp="$XASH3D_GC_ISO_CACHE/dodgc-lean-${mode}-$$.iso"
	local args=(
		--dol "$DODGC_DOL"
		--output "$tmp"
		--data "$GDATA"
		--gamedir "$DODGC_GAME"
		--extra-data "valve=$VMIN"
		--no-auto-extra-gamedirs
	)
	if [[ "$GDATA" != "$LEAN" ]]; then args+=(--extra-data "dod=$LEAN"); fi
	# Solo listen / peer-connect boots own gamecube.cfg; otherwise use play defaults.
	if [[ -z "$LISTEN" && -z "$CONNECT" ]]; then
		args+=(--play)
	fi
	# Keep Valve intro (valve.avi → .gcvid) on lean discs unless explicitly skipped.
	(( SKIP_STARTUP_VIDS )) && args+=(--skip-startup-vids)
	if [[ -n "$SMOKE" ]]; then
		args+=(--smoke-map "$SMOKE")
		(( DUMPFRAMES )) && args+=(--probe-dumpframes)
	fi
	(( WORLD_RENDER )) && args+=(--world-render)
	if [[ -n "$LISTEN" ]]; then
		if [[ -n "$TAS" ]]; then
			tas_src="$DODGC_ENGINE/scripts/tas/${TAS}.tas"
			[[ -f "$tas_src" ]] || { echo "error: missing TAS script $tas_src" >&2; exit 2; }
			mkdir -p "$LEAN/tas"
			cp -f "$tas_src" "$LEAN/tas/${TAS}.tas"
		fi
		{
			echo "video prog"
			# worldrender listen skips game.cfg, so select the DoD rules here
			# (InstallGameRules reads mp_teamplay); otherwise no DoD rules, no bots.
			echo "mp_teamplay 1"
			echo "mp_teamlist \"Allies;Axis\""
			echo "listenserver $LISTEN"
			(( WANT_NET )) && write_net_config
			(( HEADLESS )) && echo headless
			# Flipper world tris (otherwise R_EdgeDrawing skips as gcmap smoke).
			(( WORLD_RENDER )) && echo "gcworldrender"
			# CapFaces GX display lists cost 128 KiB BSS tip — charlie tip-OOM'd
			# after MAP_READY with gcworlddl (heap_free=104). Skip for lean listen;
			# PVS/frustum CapFaces path does not need a static DL.
			# Solo listen needs pad → engfuncs; without this CapFaces is view-only.
			# DODGC_NO_PLAYERINPUT=1: no probe pad, so its attack/jump/use burst does not join the human (join-timing tests)
			[[ -z "${DODGC_NO_PLAYERINPUT:-}" ]] && echo "gcplayerinput"
			# Extra gamecube.cfg lines, e.g. DODGC_EXTRA_CFG="retailnewgame" (real play route).
			[[ -n "${DODGC_EXTRA_CFG:-}" ]] && printf '%b\n' "$DODGC_EXTRA_CFG"
			(( DUMPFRAMES )) && echo "dumpframes"
			[[ -n "$DUMPEYE" ]] && echo "dumpeye $DUMPEYE"
			[[ -n "$TAS" ]] && echo "tas $TAS"
		} > "$GDATA/gamecube.cfg"
		echo "==> listenserver cfg: $LISTEN net=$([[ $WANT_NET -eq 1 ]] && echo "${NET_IP:-dhcp}" || echo off) world_render=$WORLD_RENDER dumpframes=$DUMPFRAMES tas=${TAS:-off}"
	elif [[ -n "$CONNECT" ]]; then
		{
			echo "video prog"
			write_net_config
			# Extra gamecube.cfg lines before the connect, e.g. "dodgc_master http://10.0.0.1:8080\ninternetservers".
			[[ -n "${DODGC_EXTRA_CFG:-}" ]] && printf '%b\n' "$DODGC_EXTRA_CFG"
			echo "connect $CONNECT"
			# Peer BSP tip path needs -gcmap (high-slot surfaces); without it
			# Mod_LoadWorld OOMs on planes/surfaces (dual IPC 20261107-005100).
			if [[ -n "$MAP" ]]; then
				echo "map $MAP"
			fi
			(( WORLD_RENDER )) && echo "gcworldrender"
			(( DUMPFRAMES )) && echo "dumpframes"
			# Keep the peer CapFaces capture aligned with the listen host's
			# explicitly selected spawn/atlas eye.
			[[ -n "$DUMPEYE" ]] && echo "dumpeye $DUMPEYE"
		} > "$GDATA/gamecube.cfg"
		echo "==> connect cfg: $CONNECT net=${NET_IP:-dhcp} map=${MAP:-} world_render=$WORLD_RENDER dumpframes=$DUMPFRAMES"
	fi
	echo "==> packaging $out ($mode) startup_vids=$([[ $SKIP_STARTUP_VIDS -eq 0 ]] && echo on || echo off) net=$([[ $WANT_NET -eq 1 ]] && echo on || echo off) listen=${LISTEN:-} connect=${CONNECT:-} net_ip=${NET_IP:-}"
	if ! TMPDIR="$XASH3D_GC_ISO_CACHE" \
		XASH_GC_PROBE_NET="$([[ $WANT_NET -eq 1 ]] && echo 1 || echo 0)" \
		python3 "$DODGC_ENGINE/scripts/build-gamecube-disc.py" "${args[@]}"
	then
		rm -f "$tmp"
		echo "error: disc build failed for $mode" >&2
		exit 1
	fi
	[[ -f "$tmp" ]] || { echo "error: missing temp ISO $tmp" >&2; exit 1; }
	# CapFaces pack: build-gamecube-disc.py fails smoke staging if cf_*.gcp is
	# missing; hybrid GC ISOs are not reliably listed by 7z, so trust the disc build.
	if (( WORLD_RENDER )) && [[ -n "${SMOKE:-$LISTEN}" ]]; then
		local stem
		stem="$(echo "${SMOKE:-$LISTEN}" | tr '[:upper:]' '[:lower:]')"
		echo "==> CapFaces pack required for ${stem} (enforced by disc build)"
	fi
	local pub="$out.tmp.$$"
	cp --reflink=auto "$tmp" "$pub"
	mv -f "$pub" "$out"
	rm -f "$tmp"
	ls -lh "$out"
}

(( INTRO )) && pack intro "$DODGC_ISO"
(( MENU )) && pack menu "$DODGC_OUT/dodgc-menu.iso"

{
	echo "dod-gc lean disc"
	echo "built_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
	echo "iso=$DODGC_ISO"
	echo "menu_iso=$DODGC_OUT/dodgc-menu.iso"
	echo "dol=$DODGC_DOL"
	echo "lean=$LEAN"
	echo "valve_min=$VMIN"
	echo "smoke=${SMOKE:-}"
	echo "listen=${LISTEN:-}"
	echo "connect=${CONNECT:-}"
	echo "map=${MAP:-}"
	echo "engine_commit=$(dodgc_engine_sha)"
	echo "dodgc_commit=$(dodgc_repo_sha)"
} | tee "$DODGC_OUT/dodgc-iso-handoff.txt"

echo "==> lean ISOs ready"
echo "    probe: scripts/probe-playtest.sh --route intro-menu out/dodgc.iso"
