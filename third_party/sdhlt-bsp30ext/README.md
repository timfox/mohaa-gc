# SDHLT BSP30ext patch

This patch lets SDHLT compile maps with more than 32,767 clipnodes. The 15 MOHAA maps over that limit are written in Xash3D's **BSP30ext** layout, which xash3d-gc already loads (`engine/common/mod_bmodel.c`, `LUMP_BSP30EXT`).

- Clipnodes are int32 in memory, and the limit goes up to 262,144.
- A map under 32,767 clipnodes is still written as stock BSP30, so the output is the same as unpatched SDHLT.
- A larger map gets the `XASH` version 4 extra header (12 empty extra lumps) right after the BSP30 header, and a clipnode lump of 12-byte `{int planenum; int children[2];}` entries.
- `sdHLVIS` and `sdHLRAD` read both layouts, using the engine's rule: 32-bit if the file has the XASH header and the lump holds at least 32,767 entries (or its length isn't a multiple of 8).
- Hull 0 limits (`MAX_MAP_NODES` 32,767, world leaves 8,192) don't change.

```bash
third_party/sdhlt-bsp30ext/build.sh /tmp/sdhlt     # binaries in /tmp/sdhlt/SDHLT/tools
python3 tools/bsp30_check.py maps/m1l2a.bsp --point 0 0 40 1
```

**License:** SDHLT is GPL-2 (plus the Valve SDK EULA). `bsp30ext.patch` changes SDHLT source, so it is GPL-2 as well. This directory is separate from the MIT code in the rest of the repo: nothing in `tools/` includes or links it, and the compiler only ever runs as an external program.
