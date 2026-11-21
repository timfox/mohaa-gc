#!/usr/bin/env bash
# Build SDHLT with the BSP30ext (32-bit clipnode) patch.
#   third_party/sdhlt-bsp30ext/build.sh [workdir]   -> <workdir>/SDHLT/tools/sdHL*
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="${1:-$HERE/../../out/sdhlt}"
REV=d51cb01d0a70d1c7c4b3df3c53dc566a5e7e7011   # seedee/SDHLT v1.3.1
mkdir -p "$WORK"
cd "$WORK"
if [ ! -d SDHLT ]; then
	git clone https://github.com/seedee/SDHLT.git
fi
cd SDHLT
git checkout -q "$REV"
git checkout -q -- .
git apply "$HERE/bsp30ext.patch"
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release >/dev/null
cmake --build build -j"$(nproc)"
echo "built: $PWD/tools"
