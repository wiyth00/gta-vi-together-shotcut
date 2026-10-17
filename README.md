# GTA VI — Together

An editable 30-second, 4K Shotcut fan-edit project, with its source media, exports, and review handoff.

## Versions

| Version | Shotcut project | Export |
| --- | --- | --- |
| Codex baseline / alternate mix | [Together_4K_HQ_Bumper.mlt](Together_4K_HQ_Bumper.mlt) | [4K MP4](Reference/Together_4K_HQ_Bumper_30s.mp4) |
| Gemini polish candidate | [Together_4K_HQ_Bumper_Candidate.mlt](Together_4K_HQ_Bumper_Candidate.mlt) | [Candidate 4K MP4](Reference/Together_4K_HQ_Bumper_30s_Candidate.mp4) |
| Candidate V4 (review fixes) | [Together_4K_HQ_Bumper_V4.mlt](Together_4K_HQ_Bumper_V4.mlt) | [V4 4K MP4](Reference/Together_4K_HQ_Bumper_30s_V4.mp4) |
| V5 own music mix | [Together_4K_HQ_Bumper_V5_OwnMix.mlt](Together_4K_HQ_Bumper_V5_OwnMix.mlt) | [V5 4K MP4](Reference/Together_4K_HQ_Bumper_30s_V5_OwnMix.mp4) |
| V6 Claude stem remix | [Together_4K_HQ_Bumper_V6_ClaudeRemix.mlt](Together_4K_HQ_Bumper_V6_ClaudeRemix.mlt) | [V6 4K MP4](Reference/Together_4K_HQ_Bumper_30s_V6_ClaudeRemix.mp4) |
| **V7 Claude score — current** | [Together_4K_HQ_Bumper_V7_ClaudeScore.mlt](Together_4K_HQ_Bumper_V7_ClaudeScore.mlt) | [V7 4K MP4](Reference/Together_4K_HQ_Bumper_30s_V7_ClaudeScore.mp4) |

**V7 is the current version** (see [CURRENT_VERSION.md](CURRENT_VERSION.md)). V4 applies the review notes to the candidate; see [Editing/V4_NOTES.md](Editing/V4_NOTES.md).

The full-length remix of the song is in [Remix/](Remix/); see [Editing/REMIX_NOTES.md](Editing/REMIX_NOTES.md).

Keep the `Media` folder beside the projects. The projects link to those files rather than embedding them. Both project files and all their media are included. The candidate is a separate working version; see its EDL in `Editing/`.

## Download the complete project

Large media files use [Git LFS](https://git-lfs.com/). Install it before cloning, then run:

```sh
git lfs install
git clone https://github.com/wiyth00/gta-vi-together-shotcut.git
cd gta-vi-together-shotcut
git lfs pull
```

Open either `.mlt` file in Shotcut. A clone with LFS downloads disabled contains media pointers until `git lfs pull` completes.

## Sources and review context

Main picture comes from the supplied high-bitrate Rockstar 4K file. The PlayStation animation and final hold come from the supplied YouTube video’s 4K stream. Read [CURRENT_VERSION.md](CURRENT_VERSION.md), [the Gemini handoff](GEMINI_HANDOFF.md), and [bumper notes](Editing/HQ_BUMPER_NOTES.md) for the baseline’s timing, audio treatment, and provenance. These notes predate the Gemini candidate.

The baseline is 3840 × 2160 at 30 fps, exactly 900 frames / 30 seconds. The repository preserves the current folder snapshot, including both versions.

Before the initial commit, an unescaped ampersand in the candidate’s clip caption was escaped so its XML parses correctly; no creative settings were changed by that correction.
