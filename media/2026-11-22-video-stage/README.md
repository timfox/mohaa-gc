# MOHAA retail intro movie conversion — 2026-11-22

Converted the locally extracted retail `intro.RoQ` and its separate `intro.mp3` soundtrack with:

```sh
python3 tools/intro_movie.py retail/video-out/Video_Files/intro.RoQ \
  --sd /tmp/mohaa-roq-convert-20261122
```

The assets were written only to `/tmp`; no retail media was added to Git.

## Video stream

- Source: 70,444,751-byte RoQ, 512x256, 30 fps; ffprobe decoded 5,005 frames.
- Output: 2,503 letterboxed 320x240 RGB565 frames at 15 fps, 137,869,357 bytes, 0.83 MB/s.
- The GCV2 frame offsets and every packet boundary were checked through EOF. Replaying all key and
  delta packets matched all 2,503 ffmpeg reference frames after applying the converter's documented
  one-bit RGB565 comparison threshold. One keyframe and 2,502 delta frames were present.
- SHA-256: `6f6c994183d93bc9c42bd6bd9ad754f0264cd622e69d4b03f3ff46f0a960b076`.

## Audio stream

- Source: separate 2,572,890-byte MP3 soundtrack.
- Output: GCPA with 48 kHz, stereo, signed 16-bit big-endian PCM; 30,945,700-byte payload
  (161.176 seconds), 30,945,716 bytes total.
- The PCM payload matched ffmpeg's conversion byte for byte.
- SHA-256: `254537503ba9c54ef5831afa14e6d377a0ad32c7c64a69c57fbea5f4283c28dc`.

ffmpeg printed `Error during demuxing: Input/output error` at the end of RoQ conversion but exited
successfully. All 5,005 frames reported by ffprobe are represented in the output and validated
against ffmpeg decoding. The exact EOF diagnostic remains unexplained.

Prior runtime evidence in [the intro movie playtest](../2026-11-22-intro-movie/README.md) shows this
320x240 stream playing with picture and sound in Dolphin. SD-card streaming on physical hardware
remains unverified. The generated GCVID and GCPCM files were removed after validation.
