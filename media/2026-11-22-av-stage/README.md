# Combined MOHAA music and intro-video staging

Run on 2026-11-22 from the local retail install and both extracted CD images:

```sh
python3 tools/mohaa_sd.py \
  --cd /home/tim/Desktop/mohaa-gc/retail/cd/disc1 /home/tim/Desktop/mohaa-gc/retail/cd/disc2 \
  --mohaa /home/tim/Desktop/mohaa-gc/retail \
  --music-source /home/tim/Desktop/mohaa-gc/retail/unshield/main \
  --movie-source /home/tim/Desktop/mohaa-gc/retail/video-out/Video_Files \
  --sd /tmp/mohaa-av-cd-stage-20261122 \
  --stages music,movie --list
```

The real staging run completed successfully and wrote generated retail media only beneath `/tmp/mohaa-av-cd-stage-20261122/`. It converted 75 of 79 referenced music tracks, emitted 51 mood tables and 126 music-stage files (355.9 MB), then staged the 2,503-frame (166.9 second) intro movie as GCV2/GCPA (2 movie-stage files, 161.0 MB). Total newly staged output was 516.9 MB.

Three references remain absent after extraction of both CDs and the loose install music folder:

- `sound/amb_stereo/amb_teamdm6_trainstation_ext.mp3`
- `sound/mohpc_prototype_music/the_jet_aircraft_facility.mp3`
- `sound/music/mus_snipertown_01e.mp3`

There was one intentional no-stream sentinel and zero conversion failures. The stage printed an ffmpeg RoQ demux I/O warning at end-of-stream while returning success. The GCV2 and GCPA outputs matched the preceding loose-source-only staging run byte-for-byte:

- `mohaa_intro.gcvid`: `6f6c994183d93bc9c42bd6bd9ad754f0264cd622e69d4b03f3ff46f0a960b076`
- `mohaa_intro.gcpcm`: `254537503ba9c54ef5831afa14e6d377a0ad32c7c64a69c57fbea5f4283c28dc`

Full output is in [cd-backed-stage.log](cd-backed-stage.log). Runtime playback of this newly staged intro is still unverified because another Dolphin process was active during this session. No retail media was added to Git.
