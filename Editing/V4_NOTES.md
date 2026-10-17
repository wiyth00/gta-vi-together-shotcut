# Candidate V4 — review fixes

Project: `../Together_4K_HQ_Bumper_V4.mlt` (built from the Candidate V3 project, which is left unchanged)
Export: `../Reference/Together_4K_HQ_Bumper_30s_V4.mp4`
EDL: `edit_decisions_4K_HQ_Bumper_V4.json`

3840 × 2160, 30 fps, 900 frames. Beat-locked cuts (6.433 s drop, 13.567 s chorus, 21.567 s logo hit, 27.000 s PlayStation) are unchanged.

## Changes

| Note | Fix |
| --- | --- |
| 21–23 s: logo over a grey void, then the skyline pops in | Logo reveal trimmed to its 22-frame animation (76.533–77.233 s). The glide now starts at source 78.333 s, so the trailer's own city dissolve plays under the logo from ~22.3 s. The glide and slate run continuously from there (source 78.333–83.000 s). This replaces the hard jump from 77.7 s to 79.13 s. |
| 23–26 s: abrupt duck and dry voiceover | New bed `Media/Trailer_Audio_Candidate_V4.wav`. From 22.3 to 22.9 s it crossfades into a processed copy: compressor (−22 dB threshold, 2.5:1), +2 dB low shelf at 180 Hz, −1.5 dB high shelf at 7.5 kHz and a light short echo for room. A smooth +2.5 dB lift fills the dip and rides back down before the PlayStation sting. The source is a stereo mix, so the voiceover can't be processed or removed on its own. |
| 25–27 s: Xbox logo on a PlayStation spot | V3 holds `Media/Slate_Clean_Plate_4K.mov`, a 1240 × 200 RGBA patch of the same shot taken from 140 px higher, with a feathered alpha from `Media/Slate_Patch_Mask_4K.png`. It covers the logo row. V4 re-uses the PS5 logo, cropped and moved +362 px so it sits centred over “CAPTURED ON PS5”, with a Lighten blend. Both overlays start at source frame 2432, after the GTA VI logo has fully dissolved. |
| ~11 s: vocal entered mid-phrase into the vault shot | The chorus section used to start at source 27.901 s, the middle of a sung phrase. It now starts two beats (0.975 s at 123 BPM) earlier, at source 26.926 s, in the instrumental gap before the phrase. The audio edit moves from 11.03 s to 10.05 s with a 0.25 s equal-power crossfade, and the phrase now begins cleanly at about 10.1–10.3 s. The source is sample-aligned with the polished bed (correlation 1.0), so it rejoins the existing chorus audio by 11.33 s. Everything stays on the beat grid. |
| 13–24 s: song switches at the twirl and again at the logo | From the beat at 13.119 s, just before the neon-club twirl, the bed plays the song continuously from source 37.622 s: “Let's take it fast, just like a flash, and in a moment we'll be gone like a second chance, you and me…”. It is beat-aligned at 123 BPM (timeline 13.607 s ↔ source 38.110 s). It replaces the old 13.567–22.733 s section and the clipped “Like…” at 13.4 s. The song fades out from 22.6 to 24.3 s under the “Grand Theft Auto VI, coming November 19th” voiceover. Lyrics were located with Whisper (medium.en). The trailer's own pool-splash and logo-hit sounds go with the old section. |
| 5–6 s: Jason's line | No change. Whisper shows “We just gotta get through it” ends at 5.74 s, before the 6.43 s cut, so the earlier L-cut was removed. |
| 15–17 s: night → day → night | “Lucia returns fire” (daytime) moved into the day montage at 7.400 s. Drift, motorcycle and beach shots were trimmed 14, 8 and 8 frames to make room. Its 16.2 s slot now holds “Masked partners” (night, source 59.900 s), so everything from 11.2 s onward is night or interior. |
| 27–30 s: letterbox on the PlayStation outro | The PlayStation sting and logo hold now have Size, Position & Rotate filters scaled to 112.5 % (`-240 -135 4320 2430`). This fills 16:9 and removes the source's baked-in 120 px bars. |

## Rebuilding

`v4_tools/build_audio.py` builds the bed and `v4_tools/build_mlt.py` builds the project, both from the V3 Candidate files. The audio script expects these intermediates in the folder passed as its argument:

- `bed_proc.wav`: the processed bed, from ffmpeg `acompressor=threshold=-22dB:ratio=2.5:attack=12:release=220:makeup=1.5dB,lowshelf=f=180:g=2,highshelf=f=7500:g=-1.5,aecho=0.85:0.5:38|74:0.10|0.06`.
- `src_xf.wav`: unprocessed source audio from 25.0 s for 6.0 s, used for the earlier chorus entry.
- `src_flash.wav`: unprocessed source audio from 36.0 s for 14.0 s (the “like a flash” section).
- `src_vo.wav`: unprocessed source audio from 78.0 s for 2.0 s (voiceover pre-roll).

The processed copy (`bed_proc.wav`) is now generated inside the script from the re-cut bed.

Rendering note: melt with all 4K chains open used more than 15 GB RAM in this environment. The export was rendered in two halves (frames 0–449 and 450–899) and joined losslessly. Shotcut on a desktop should export in one pass.

Not verified by ear: the audio work was done from level measurements, not listening. Check the 10 s chorus entry, the 13.1 s switch into “like a flash” and the 22–27 s ending on speakers before calling it final.
