# MOHAA m1l2b GameCube map conversion — 2026-11-22

Converted retail `Pak5.pk3:maps/m1l2b.bsp` through `tools/mohaa_sd.py --stages maps` into a temporary SD tree. The conversion used the existing patched SDHLT cache at `/home/tim/.local/share/mohaa-gc/sdhlt/SDHLT/tools`; no network fetch was required.

## Generated formats

- `maps/m1l2b.bsp`: BSP30, 3,122,151 bytes including lighting; 2,515,452 bytes with the lighting lump excluded (630,276 bytes under the GameCube 3 MiB map limit).
- BSP validation: 16,233 16-bit clipnodes, 9,106 planes, 90 models.
- `maps/m1l2b.mcol`: 44,796-byte collision mesh.
- `maps/m1l2b.nodes`: 21,072-byte path-node table.
- `media/lg_m1l2b.gcg`: 2,071,136-byte MOHAA light grid.
- Six 128x128 CMPR sky faces for `mohnight1`.
- `maps.lst`: `m1l2b "m1l2b"`.

BSP SHA-256: `ef71b1bd3f121d74560ba47bac1304e3c62d8c371d069dba5a7579e4d92b8a74`.

## Runtime status

The converted files are staged under `/home/tim/Desktop/mohaa-gc/cutscene-20261122/sd/xash3d/mohaa/`; existing m1l1 and m1l2a assets remain in place, and `maps.lst` includes all three maps. Scratch ISOs supplied the four shared GoldSrc boot assets from the local DoD/Valve cache and reached `MAP_READY m1l2b` and `newgame world render ready` in Dolphin. Runtime screenshots, hashes, performance comparison, and open issues are recorded in [the m1l2b runtime evidence](../2026-11-22-m1l2b-runtime/README.md). This is a smoke map/world-render route, not a complete MOHAA gameplay port. The generic smoke builder generated WorldDL only in the first scratch ISO; a matched 45-second control without that pack stabilized around 55–56 FPS versus 4.6 FPS in the WorldDL run. Treat this as an emulator lead, not a final performance result; see [the comparison notes](../2026-11-22-m1l2b-runtime/worlddl-vs-live-bsp.md). The MOHAA SD stage now includes `media/gp_m1l2b.gcp` and `media/pt_m1l2b.gct`; the prop pack was confirmed loaded at runtime. A per-map `.snd` and referenced WAVs were generated, but the runtime log does not confirm table loading; `media/ss_m1l2b.gcs` remains absent. Retail-derived game data remains local and uncommitted.
