# V5 — own music mix

Project: `../Together_4K_HQ_Bumper_V5_OwnMix.mlt`. The picture is identical to V4; only the A1 audio bed is different.
Export: `../Reference/Together_4K_HQ_Bumper_30s_V5_OwnMix.mp4`
Bed: `Media/Trailer_Audio_Own_Mix_V5.wav`, built by `v4_tools/isolate_voice.py`, then `v4_tools/demucs_clean.py`, then `v4_tools/build_own_mix.py`.

## Arrangement

The song is the studio track `Media/Flower_In_A_Hurricane.flac` at 126.05 BPM, with timeline beats at 6.453 s and 13.593 s.

| Timeline | Music | On top |
| --- | --- | --- |
| 0.00–6.45 | Song build-up (song 58.0 s on), 7 dB under the dialogue, swelling into the drop | “Are we gonna be okay?… We just gotta get through it” |
| 6.45 | Chorus downbeat on the picture drop | |
| 6.6–9.3 | “Only love never hesitates” | Day montage |
| 9.79 | Cut on the beat after “hesitates”: instrumental fill, then the break | |
| 13.45 | “Let's take it fast, just like a flash… second chance, you and me” | Neon-club twirl onward |
| 21.567 | The song's final chord and ring-out, on the logo reveal | |
| 22.9–27.0 | Decaying ring-out | “Grand Theft Auto VI, coming November 19th. Rated M for Mature.” |

## Voices

The trailer has no separate stems. The song sits in its mix at known offsets: trailer 61.0–67.45 s is song +57.30 s, 67.45–68.45 s is +141.10 s, and 68.45 s onward is +95.40 s, with correlation 0.85–0.99.

`isolate_voice.py` aligns the song at 48 kHz and fits a per-channel Wiener filter, which models the trailer's EQ and level. It then subtracts the filtered song from the trailer mix. Music-only passages drop about 12 dB, from about −15 to −27 dB, which leaves the voices about 10 dB clear of the leftover music. A soft gate takes up to 10 dB more off between words. A second pass, `v4_tools/demucs_clean.py`, keeps only the Demucs (htdemucs) vocals stem of each isolated voice. Leftover music in a music-only window drops from −27 to −83 dB for the dialogue, and from −27 to −36 dB for the voiceover, where some sung vocal from the trailer's song remains.

Only the voiceover is processed: compression (−24 dB, 3:1), +2.5 dB low shelf at 160 Hz, −1.5 dB high shelf at 8 kHz, a light short echo, and +1.5 dB.

Loudness: −17.4 LUFS integrated, −5.0 dBFS peak.

Not verified by ear. Listen to the 9.8 s cut, the logo-hit ending, and any faint leftover song under the dialogue.
