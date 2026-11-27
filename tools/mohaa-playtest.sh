#!/usr/bin/env bash
# Capture a MOHAA Dolphin probe into this repository's local media archive.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DODGC_ROOT="${MOHAA_DODGC_ROOT:-$ROOT/dod-gc}"
MEDIA="$ROOT/media/playtests"

usage() {
	cat <<'EOF'
usage: tools/mohaa-playtest.sh [probe options] <MOHAA ISO>

Runs a bounded Dolphin playtest using dod-gc's capture harness and stores its
milestone screenshots, eight-second gameplay frames, video, OSReport log,
metadata, and note under
media/playtests/{screenshots,videos,notes}/.

Probe options: --route NAME --duration SEC --note TEXT --skip-video
              --ready-regex REGEX

Set MOHAA_CAPTURE_INTERVAL to change the periodic screenshot interval.
If PulseAudio is unavailable, a silent H.264 recording is captured instead;
MOHAA_FORCE_SILENT_VIDEO=1 selects that recording path explicitly.

The profile's GCPadNew.ini and GFX.ini are copied from
MOHAA_DOLPHIN_PROFILE (default: /tmp/mohaa-m1l1-playable). Set MOHAA_ENGINE
or MOHAA_DOLPHIN_BIN if the local Dolphin build is elsewhere.
EOF
}

if [[ $# -eq 0 ]] || [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
	usage
	exit 0
fi

PROBE="$DODGC_ROOT/scripts/probe-playtest.sh"
[[ -x "$PROBE" ]] || { echo "error: capture harness not found: $PROBE" >&2; exit 1; }

ENGINE="${MOHAA_ENGINE:-}"
DOLPHIN="${MOHAA_DOLPHIN_BIN:-}"
ENGINE_EXPLICIT=0
[[ -n "$ENGINE" ]] && ENGINE_EXPLICIT=1
if [[ -z "$DOLPHIN" ]]; then
	for candidate in "${ENGINE:-}" /run/media/tim/Expansion1/xash3d-gc /home/tim/xash3d-gc-lostcoast; do
		[[ -n "$candidate" ]] || continue
		if [[ -x "$candidate/3rdparty/dolphin/build/Binaries/dolphin-emu" ]]; then
			[[ "$ENGINE_EXPLICIT" == 1 ]] || ENGINE="$candidate"
			DOLPHIN="$candidate/3rdparty/dolphin/build/Binaries/dolphin-emu"
			break
		fi
	done
fi
[[ -x "$DOLPHIN" ]] || { echo "error: set MOHAA_DOLPHIN_BIN to a local Dolphin executable" >&2; exit 2; }
if [[ -z "$ENGINE" ]]; then
	ENGINE="$(dirname "$(dirname "$(dirname "$(dirname "$(dirname "$DOLPHIN")")")")")"
fi
[[ -d "$ENGINE/scripts" ]] || { echo "error: set MOHAA_ENGINE to an Xash3D-GC checkout" >&2; exit 2; }

PROFILE="${MOHAA_DOLPHIN_PROFILE:-/tmp/mohaa-m1l1-playable}"
[[ -f "$PROFILE/Config/GCPadNew.ini" ]] || {
	echo "error: controller profile not found: $PROFILE/Config/GCPadNew.ini" >&2
	exit 2
}

ISO=""
USER_NOTE="${MOHAA_NOTE:-}"
ROUTE="mohaa"
SKIP_VIDEO=0
ARGS=()
while (($#)); do
	arg="$1"
	shift
	case "$arg" in
		--note)
			[[ $# -gt 0 ]] || { echo "error: --note needs text" >&2; exit 2; }
			USER_NOTE="$1"
			shift
			;;
		--route|--duration|--ready-regex)
			[[ $# -gt 0 ]] || { echo "error: $arg needs a value" >&2; exit 2; }
			[[ "$arg" != --route ]] || ROUTE="$1"
			ARGS+=("$arg" "$1")
			shift
			;;
		--skip-video) SKIP_VIDEO=1; ARGS+=("$arg") ;;
		-*) ARGS+=("$arg") ;;
		*)
			[[ -n "$ISO" ]] && { echo "error: pass one ISO" >&2; exit 2; }
			ISO="$(readlink -f "$arg")"
			ARGS+=("$ISO")
			;;
	esac
done
[[ -f "$ISO" ]] || { echo "error: pass an existing MOHAA ISO" >&2; exit 2; }

SEED_HOME="$(mktemp -d /tmp/mohaa-playtest-profile.XXXXXX)"
cleanup() { rm -rf "$SEED_HOME"; }
trap cleanup EXIT
if [[ -z "${XDG_RUNTIME_DIR:-}" || ! -d "$XDG_RUNTIME_DIR" || ! -w "$XDG_RUNTIME_DIR" ]]; then
	export XDG_RUNTIME_DIR="$SEED_HOME/runtime"
fi
mkdir -p "$XDG_RUNTIME_DIR"
SEED_CONFIG="$SEED_HOME/dod-gc/dolphin/Config"
mkdir -p "$SEED_CONFIG"
cp "$PROFILE/Config/GCPadNew.ini" "$SEED_CONFIG/"
[[ -f "$PROFILE/Config/GFX.ini" ]] && cp "$PROFILE/Config/GFX.ini" "$SEED_CONFIG/"

REPO_SHA="$(git -C "$ROOT" rev-parse --short=10 HEAD 2>/dev/null || echo unknown)"
ENGINE_SHA="$(git -C "$ENGINE" rev-parse --short=10 HEAD 2>/dev/null || echo unavailable)"
ISO_SHA="$(sha256sum "$ISO" | cut -d' ' -f1)"
NOTE="MOHAA GameCube playtest. Repo HEAD: $REPO_SHA. Engine checkout: $ENGINE (Git revision $ENGINE_SHA). ISO: $ISO (SHA-256 $ISO_SHA)."
[[ -n "$USER_NOTE" ]] && NOTE+=" $USER_NOTE"

export DODGC_ENGINE="$ENGINE"
export DODGC_DOLPHIN_BIN="$DOLPHIN"
export DODGC_PLAYTESTS="$MEDIA"
export DODGC_SHOTS="$MEDIA/screenshots"
export DODGC_VIDEOS="$MEDIA/videos"
export DODGC_NOTES="$MEDIA/notes"
export XDG_DATA_HOME="$SEED_HOME"

PROBE_RUN_ARGS=("${ARGS[@]}")
SILENT_FALLBACK=0
if (( ! SKIP_VIDEO )); then
	if [[ "${MOHAA_FORCE_SILENT_VIDEO:-0}" == 1 ]] || { ! command -v pactl >/dev/null 2>&1 || ! pactl info >/dev/null 2>&1; }; then
		SILENT_FALLBACK=1
		PROBE_RUN_ARGS+=(--skip-video)
	fi
fi

"$PROBE" --route mohaa "${PROBE_RUN_ARGS[@]}" --note "$NOTE" &
PROBE_PID=$!
LIVE_CAPTURE_ARGS=(
	--probe-pid "$PROBE_PID"
	--runtime-dir "$XDG_RUNTIME_DIR"
	--shot-root "$MEDIA/screenshots"
	--route "$ROUTE"
	--repo "$REPO_SHA"
	--engine "$ENGINE_SHA"
	--iso "$ISO"
	--interval "${MOHAA_CAPTURE_INTERVAL:-8}"
)
if (( SILENT_FALLBACK )); then
	VIDEO_STAMP="$(date +%Y%m%d-%H%M%S)"
	SAFE_ROUTE="$(printf '%s' "$ROUTE" | tr -cs 'A-Za-z0-9._-' '-' | sed 's/^-//;s/-$//')"
	LIVE_CAPTURE_ARGS+=(--video "$MEDIA/videos/${VIDEO_STAMP}-${SAFE_ROUTE}-silent.mp4")
fi
python3 "$ROOT/tools/mohaa-live-capture.py" "${LIVE_CAPTURE_ARGS[@]}" &
CAPTURE_PID=$!
set +e
wait "$PROBE_PID"
PROBE_STATUS=$?
wait "$CAPTURE_PID"
set -e
(( PROBE_STATUS == 0 )) || exit "$PROBE_STATUS"

# The shared capture helper is maintained with dod-gc; normalize its index and
# metadata so artifacts stored here identify this MOHAA project correctly.
python3 - "$MEDIA" <<'PY'
import gzip
import json
import re
import shutil
import sys
from pathlib import Path

root = Path(sys.argv[1])
rows = []
video_stamps = set()
video_by_stamp = {}
for path in (root / "notes").glob("*.md"):
    text = path.read_text(encoding="utf-8")
    text = text.replace("# Probe ", "# MOHAA Probe ")
    text = text.replace("`playtests/screenshots/", "`media/playtests/screenshots/")
    log = root / "screenshots" / path.stem / "dolphin.log"
    if log.is_file():
        compressed = log.with_suffix(".log.gz")
        with log.open("rb") as source, compressed.open("wb") as raw:
            with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as target:
                shutil.copyfileobj(source, target)
        log.unlink()
        text += f"\n- Full Dolphin log: `media/playtests/screenshots/{path.stem}/dolphin.log.gz`\n"
    text = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    path.write_text(text, encoding="utf-8")

for path in sorted((root / "videos").glob("*.json"), reverse=True):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        continue
    data["project"] = "mohaa-gc"
    if data.get("engine_commit") == "unknown":
        data["engine_commit"] = "unavailable"
    video_stamps.add(re.sub(r"\D", "", str(data.get("date", "")))[:14])
    video_by_stamp[re.sub(r"\D", "", str(data.get("date", "")))[:14]] = data.get("file", "")
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    rows.append(
        f"| {data.get('date', '')} | `videos/{data.get('file', '')}` | "
        f"{data.get('route', '')} | {data.get('duration_s', '')}s | "
        f"{data.get('size_mb', '')} MB | `{data.get('commit', '')}` |"
    )

for note_path in sorted((root / "notes").glob("*.md"), reverse=True):
    stamp = note_path.stem[:15]
    shot_dir = root / "screenshots" / note_path.stem
    stamp_digits = re.sub(r"\D", "", stamp)[:14]
    frames = sorted((shot_dir / "frames").glob("*.png"))
    if frames or stamp_digits in video_by_stamp:
        note_text = note_path.read_text(encoding="utf-8")
        capture_lines = []
        if frames:
            capture_lines.append(
                f"- Periodic guest frames: {len(frames)} screenshots in `media/playtests/screenshots/{note_path.stem}/frames/`"
            )
        if video_by_stamp.get(stamp_digits):
            capture_lines.append(f"- Video: `media/playtests/videos/{video_by_stamp[stamp_digits]}`")
        if capture_lines:
            existing = set(note_text.splitlines())
            missing_lines = [line for line in capture_lines if line not in existing]
            if missing_lines:
                insert_at = next((i + 1 for i, line in enumerate(note_text.splitlines()) if line.startswith("- Shots:")), None)
                lines = note_text.splitlines()
                if insert_at is not None:
                    lines[insert_at:insert_at] = missing_lines
                else:
                    lines.extend(["", *missing_lines])
                note_text = "\n".join(lines).rstrip() + "\n"
                note_path.write_text(note_text, encoding="utf-8")
    if stamp_digits in video_stamps:
        continue
    shot = next((p for p in (shot_dir / "final.png", shot_dir / "menu.png", shot_dir / "intro.png") if p.is_file()), None)
    if shot is None:
        continue
    note_text = note_path.read_text(encoding="utf-8")
    route = next((line.split(":", 1)[1].strip().strip("`") for line in note_text.splitlines() if line.startswith("- Route:")), "")
    commit = next((line.split(":", 1)[1].strip().strip("`") for line in note_text.splitlines() if line.startswith("- Repo:")), "")
    date = f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:8]}T{stamp[9:11]}:{stamp[11:13]}:{stamp[13:15]}"
    size_mb = shot.stat().st_size / (1024 * 1024)
    rows.append(
        f"| {date} | `{shot.relative_to(root)}` | {route} | still | "
        f"{size_mb:.1f} MB | `{commit}` |"
    )

index = (
    "# MOHAA GameCube playtests\n\n"
    "Screenshots: `screenshots/` · Videos: `videos/` · Notes: `notes/`\n\n"
    "| Date | File | Route | Duration | Size | Commit |\n"
    "|------|------|-------|----------|------|--------|\n"
    + ("\n".join(rows) if rows else "| — | — | — | — | — | — |\n")
    + "\n"
)
(root / "INDEX.md").write_text(index, encoding="utf-8")
PY
