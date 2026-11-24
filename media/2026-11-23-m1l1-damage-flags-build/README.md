# m1l1 damage-flag build

## Artifacts

- ISO: `/tmp/mohaa-m1l1-damage-flag-build/out/mohaa-m1l1-damage-flags.iso`
- ISO size: 1,165,940,736 bytes
- ISO SHA-256: `2785add0290335b621a32cd85ac53e493c0c098097babeef628b64f26c105225`
- DOL: `/tmp/mohaa-m1l1-damage-flag-build/out/mohaagc.dol`
- DOL size: 7,484,448 bytes
- DOL SHA-256: `4056881ccf38bd8c54f9871f36e8e7c620e3d906dd4233ad0315a72255f14e3`

## Changes and provenance

The m1l1 script uses `nodamage` and `takedamage` to toggle damage on scripted actors. Those commands were no-ops; the MOHAA backend now maps them to GoldSrc `DAMAGE_NO` and `DAMAGE_YES` through `pev->takedamage`.

The DOL was built from `/home/tim/Desktop/mohaa-gc` with devkitPPC and classic libogc (`/opt/devkitpro/libogc`). The host does not have libogc2/Swiss packages. Its linked engine source was the isolated `/tmp/mohaa-loopback-fix/engine` tree at `db73d0d1`, including the uncommitted `models/vehicles/` spill preference and MOHAA model allowlist change in `engine/common/model.c`. The SDK was copied to `/tmp/mohaa-m1l1-damage-flag-build/hlsdk-portable` from the user-owned `cutscene-20261122/hlsdk-portable` source (commit `238827b`); the original was not modified.

The ISO was assembled with the current m1l1 stage and the lean DoD/Valve support trees. The disc builder verified the embedded DOL during assembly. A read-only ISO listing confirmed `maps/m1l1.nodes`, `maps/m1l1.models`, `models/human/german_afrika_private_fa3a4b4e746f.gca`, `models/vehicles/opeltruck.mdl`, and `models/vehicles/gmctruck_opening.mdl` are present.

This is a build and packaging result, not runtime proof. The active Dolphin session is still on the previous ISO; the new damage commands and the path-node allocator need an OSReport-enabled run. The logger is configured in `/tmp/mohaa-m1l1-user/Config/Logger.ini` for a later launch.
