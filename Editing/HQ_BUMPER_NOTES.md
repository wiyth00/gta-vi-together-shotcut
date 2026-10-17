# Higher-resolution PlayStation replacement

Source supplied by Joshua: https://www.youtube.com/watch?v=rz1B4B2yBZY

Downloaded its 3840 × 2160 / 30 fps VP9 video stream (format 313) using yt-dlp in a temporary isolated local environment, removed after cleanup. No YouTube audio was used. The project source is `../Media/PlayStation_YouTube_4K_Source.webm`.

Replaced only timeline 27.000–29.000 picture with source 88.000–90.000 seconds (60 frames). Replaced the final 29.000–30.000 hold with the 3840 × 2160 PNG extracted from the final source frame. The previous low-resolution bumper and logo still were removed during cleanup.

Project: `../Together_4K_HQ_Bumper.mlt`
Export: `../Reference/Together_4K_HQ_Bumper_30s.mp4`

Verified:
- 3840 × 2160, 30 fps, 900 total video frames; video/audio/container each exactly 30.000 seconds.
- First 810 encoded picture frames hash-identical to the prior 4K export: the Rockstar main edit received no additional video recompression.
- Decoded audio hash-identical to the prior 4K alternate mix, including the shaped handoff and +1.5 dB sting adjustment.
- Ending has exactly 60 animation frames and 30 logo-hold frames. Median downsampled luminance-pattern correlation between exported animation and YouTube source is 0.999974.
- New final-frame PNG and logo preview inspected visually.
- Project opens and saves in Shotcut, and all media links resolve.

Encoding: the new 90 ending frames use H.264 CRF 18 / fast preset, matching the existing segments' encoding settings; output is fast-start MP4 with the previous AAC audio copied intact. The source bitrates naturally differ. All picture sources in this version are 3840 × 2160; the ending no longer uses the upscaled 910 × 512 source.
