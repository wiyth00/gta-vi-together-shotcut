# Candidate V4 — review fixes

Project: `../Together_4K_HQ_Bumper_V4.mlt` (built from the Candidate V3 project, which is left unchanged)
Export: `../Reference/Together_4K_HQ_Bumper_30s_V4.mp4`
EDL: `edit_decisions_4K_HQ_Bumper_V4.json`

3840 × 2160, 30 fps, 900 frames. Beat-locked cuts (6.433 s drop, 13.567 s chorus, 21.567 s logo hit, 27.000 s PlayStation) are unchanged.

## Changes

| Note | Fix |
| --- | --- |
| 21–23 s: logo over a grey void, then the skyline pops in | Logo reveal trimmed to its 22-frame animation (76.533–77.233 s). The glide now starts at source 78.333 s, so the trailer's own city dissolve plays under the logo from ~22.3 s. The glide and slate run continuously from there (source 78.333–83.000 s). This replaces the hard jump from 77.7 s to 79.13 s. |
| 23–26 s: abrupt duck and dry voiceover | New bed `Media/Trailer_Audio_Candidate_V4.wav`. From 22.3 to 22.9 s it crossfades into a processed copy: compressor (−22 dB threshold, 2.5:1), +2 dB low shelf at 180 Hz, −1.5 dB high shelf at 7.5 kHz and a light short echo for room. The processed copy is loudness-matched to the dry mix. A smooth +1 dB lift fills the dip and rides back down before the PlayStation sting. The source is a stereo mix, so the voiceover can't be processed or removed on its own. |
| 25–27 s: Xbox logo on a PlayStation spot | V3 holds `Media/Slate_Clean_Plate_4K.mov`, a 1240 × 200 RGBA patch of the same shot taken from 140 px higher, with a feathered alpha from `Media/Slate_Patch_Mask_4K.png`. It covers the logo row. V4 re-uses the PS5 logo, cropped and moved +362 px so it sits centred over “CAPTURED ON PS5”, with a Lighten blend. Both overlays start at source frame 2432, after the GTA VI logo has fully dissolved. |
| 6–24 s: song switched between verses (~10 s and ~13 s) | From 5.97 s the bed is the clean studio track (`Media/Flower_In_A_Hurricane.flac`) in one continuous run, with no edits. It covers the instrumental build, the break and then “Let's take it fast, just like a flash, and in a moment we'll be gone like a second chance, you and me…” landing on the neon-club twirl at about 13.5 s. Song time = timeline + 112.2696 s, found by cross-correlating the trailer's mix of the same passage against the track (r = 0.96, same tempo). The song is level-matched to the trailer mix. It comes in as the opening dialogue fades (by the 6.43 s cut). On the logo hit (21.567 s) it crossfades to the song position the trailer itself plays under the voiceover (“I will die before I walk away”; song = timeline + 151.795 s, r = 0.98). At 22.733 s it hands over to the trailer's voiceover section, which carries that same music, so two different lines never overlap. This replaces the earlier 10 s chorus entry and 13.1 s switch. |
| 5–6 s: Jason's line | No change. Whisper shows “We just gotta get through it” ends at 5.74 s, before the 6.43 s cut, so the earlier L-cut was removed. |
| 15–17 s: night → day → night | “Lucia returns fire” (daytime) moved into the day montage at 7.400 s. Drift, motorcycle and beach shots were trimmed 14, 8 and 8 frames to make room. Its 16.2 s slot now holds “Masked partners” (night, source 59.900 s), so everything from 11.2 s onward is night or interior. |
| 27–30 s: letterbox on the PlayStation outro | The PlayStation sting and logo hold now have Size, Position & Rotate filters scaled to 112.5 % (`-240 -135 4320 2430`). This fills 16:9 and removes the source's baked-in 120 px bars. |

## Rebuilding

`v4_tools/build_audio.py <scratch dir>` builds the bed from `Trailer_Audio_Candidate_Polish.wav`, the song and the trailer source. `v4_tools/build_mlt.py` builds the project from the V3 Candidate.

Rendering note: melt with all 4K chains open used more than 15 GB RAM in this environment. The export was rendered in two halves (frames 0–449 and 450–899) and joined losslessly. Shotcut on a desktop should export in one pass.

Not verified by ear: the audio work was done from level measurements, not listening. Check the 6 s song entry and the 22–27 s ending on speakers before calling it final.
