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
screenshots, H.264/AAC video, OSReport log, metadata, and note under
media/playtests/{screenshots,videos,notes}/.

Probe options: --route NAME --duration SEC --note TEXT --skip-video
              --ready-regex REGEX

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
if [[ -z "$DOLPHIN" ]]; then
	for candidate in "${ENGINE:-}" /run/media/tim/Expansion1/xash3d-gc /home/tim/xash3d-gc-lostcoast; do
		[[ -n "$candidate" ]] || continue
		if [[ -x "$candidate/3rdparty/dolphin/build/Binaries/dolphin-emu" ]]; then
			ENGINE="$candidate"
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
			ARGS+=("$arg" "$1")
			shift
			;;
		--skip-video) ARGS+=("$arg") ;;
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

"$PROBE" --route mohaa "${ARGS[@]}" --note "$NOTE"

# The shared capture helper is maintained with dod-gc; normalize its index and
# metadata so artifacts stored here identify this MOHAA project correctly.
python3 - "$MEDIA" <<'PY'
import gzip
import json
import shutil
import sys
from pathlib import Path

root = Path(sys.argv[1])
rows = []
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
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    rows.append(
        f"| {data.get('date', '')} | `{data.get('file', '')}` | "
        f"{data.get('route', '')} | {data.get('duration_s', '')}s | "
        f"{data.get('size_mb', '')} MB | `{data.get('commit', '')}` |"
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
