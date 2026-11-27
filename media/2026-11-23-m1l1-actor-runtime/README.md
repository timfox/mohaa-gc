# m1l1 actor runtime evidence

The initial class-picker capture and log remain as historical evidence for the failed monolithic-model load. The subsequent matched-layout interactive Dolphin session runs `/tmp/mohaa-m1l1-actor-gca-20261123/out/mohaa-m1l1-actor-gca-matched-code.iso` (SHA-256 `2cac04c5223330c7bc84ccdd235c938943c607f73bc9846c70404d69c649aeb3`). It reached m1l1, loaded the German Afrika actor’s external skin and 10-sequence GCA animation pack into ARAM, then logged draw submissions for the actor entities. This confirms model admission and renderer submission. The capture is still at the Allied class picker, so it does not verify the actor’s appearance, animation playback, camera motion, or a complete cutscene.

The live log also shows `gmctruck_opening.mdl` and `opeltruck.mdl` failing to load from the full studio BSS. A candidate ISO with an isolated `models/vehicles/` spill preference is built at `/tmp/mohaa-m1l1-actor-gca-20261123/out/mohaa-m1l1-actor-gca-spill-code.iso` (SHA-256 `64cb6cf1b15e02bf1537206debaa175fb4369d927ec27be9e0d6981f7715b183`), but has not been run. The interactive matched-actor Dolphin session later exited with status 143.

- Current matched-session screenshot: [matched-actor-test.png](matched-actor-test.png)
- Historical initial screenshot: [final.png](final.png)
- Current matched-session guest log: `/tmp/mohaa-m1l1-actor-gca-20261123/profile-matched/dod-gc/dolphin/Logs/dolphin.log`
- Historical initial guest log: `dolphin.log` (kept locally; raw Dolphin logs contain trailing whitespace)
- Initial probe notes: [probe.md](probe.md)
- Lossless model split experiment: `/tmp/mohaa-german-actor-gca-experiment/`
