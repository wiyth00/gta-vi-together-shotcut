"""Build Media/Trailer_Audio_Candidate_V4.wav.

0-6.4 s   trailer opening dialogue (Trailer_Audio_Candidate_Polish.wav)
5.97 s -> clean song (Media/Flower_In_A_Hurricane.flac): instrumental build, then "Let's take it fast, just like
          a flash..." on the neon-club twirl (~13.5 s), "...you and me"
21.567 s  on the logo hit, crossfade to the song position the trailer plays under its voiceover ("I will die before
          I walk away"), so the clean song and the trailer's own music never play different lines at once
22.733 s  hand over to the trailer voiceover section ("Grand Theft Auto VI, coming November 19th"), same music underneath
22.3 s -> processed copy (compression / warmth / light room) with a gentle level lift, as before.
Song time = timeline + 112.2696 s (cross-correlation of trailer 38-46 s against the song, r = 0.96).
Usage: build_audio.py <scratch_dir>; writes <scratch_dir>/bed_v4.f32 (48 kHz stereo float32).
"""
import numpy as np, sys, subprocess
S=sys.argv[1]; R=48000
def rd(p,extra=()):
    raw=subprocess.run(["ffmpeg","-loglevel","error",*extra,"-i",p,"-f","f32le","-ac","2","-ar","48000","-"],capture_output=True,check=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).astype(np.float64)
def ix(t): return int(round(t*R))
bed=rd("Media/Trailer_Audio_Candidate_Polish.wav"); n=len(bed); tt=np.arange(n)/R
song=rd("Media/Flower_In_A_Hurricane.flac"); trailer=rd("Media/Trailer_Source_Rockstar_4K.mp4",("-vn",))
OFF=112.2696; IN=5.97; VO=22.733; HIT=21.567
def cramp(t0,t1):
    x=np.clip((tt-t0)/(t1-t0),0,1); return 0.5-0.5*np.cos(np.pi*x)
# song, level-matched to the trailer's own mix of the same passage (song 125.77-133.77 s = trailer 38-46 s)
seg=np.zeros_like(bed); a=ix(IN); b=ix(24.4)
seg[a:b]=song[ix(IN+OFF):ix(IN+OFF)+(b-a)]
ref=trailer[ix(38.0):ix(46.0)]; mine=song[ix(38.0+87.7666):ix(46.0+87.7666)]
g=np.sqrt((ref**2).mean()/(mine**2).mean())*0.992   # 0.992 = polished bed vs raw trailer
# second run: song position under the trailer's voiceover. Trailer src = t + 56.395 there; refine song offset at 48 kHz.
x=trailer[ix(77.4):ix(79.0)].mean(1); best=(-1,0)
for d in range(-480,481,2):
    y=song[ix(77.4+95.40)+d:][:len(x)].mean(1); c=np.dot(x,y)/np.sqrt(np.dot(x,x)*np.dot(y,y)); best=max(best,(c,d))
OFF2=56.395+95.40+best[1]/R
seg2=np.zeros_like(bed); a2=ix(HIT-0.10); b2=ix(VO+0.20)
seg2[a2:b2]=song[ix(HIT-0.10+OFF2):ix(HIT-0.10+OFF2)+(b2-a2)]
x1=np.clip((tt-(HIT-0.08))/0.16,0,1)        # run1 -> run2 on the logo hit
x2=np.clip((tt-(VO-0.02))/0.18,0,1)         # run2 -> trailer voiceover section (same music)
song_g=np.sin(0.5*np.pi*np.clip((tt-IN)/0.30,0,1))*np.cos(0.5*np.pi*x1)
song2_g=np.sin(0.5*np.pi*x1)*np.cos(0.5*np.pi*x2)
open_g=np.cos(0.5*np.pi*np.clip((tt-IN)/0.46,0,1))           # opening fades out by the 6.43 s cut
vo_g=np.sin(0.5*np.pi*x2)
bed=bed*(open_g*(tt<HIT)+vo_g)[:,None]+(seg*song_g[:,None]+seg2*song2_g[:,None])*g
print("run2 offset",round(OFF2,4),"corr",round(best[0],3))
print("song gain",round(g,3))
# processed copy for the ending
bed.astype(np.float32).tofile(f"{S}/bed_recut.f32")
subprocess.run(["ffmpeg","-loglevel","error","-f","f32le","-ar","48000","-ac","2","-i",f"{S}/bed_recut.f32","-af",
  "acompressor=threshold=-22dB:ratio=2.5:attack=12:release=220:makeup=1.5dB,lowshelf=f=180:g=2,highshelf=f=7500:g=-1.5,aecho=1.0:1.0:38|74:0.10|0.06",
  "-c:a","pcm_f32le",f"{S}/bed_proc.wav","-y"],check=True)
proc=rd(f"{S}/bed_proc.wav")[:n]
z=slice(ix(22.4),ix(27.0)); proc*=np.sqrt((bed[z]**2).mean()/(proc[z]**2).mean())   # loudness-match the processed copy
w=cramp(22.30,22.90); gdb=1.0*cramp(22.40,23.10)*(1-cramp(26.70,27.50))
out=((1-w)[:,None]*bed+w[:,None]*proc)*(10**(gdb/20))[:,None]
lim=0.89; m=np.abs(out)>lim
out[m]=np.sign(out[m])*(lim+(1-lim)*np.tanh((np.abs(out[m])-lim)/(1-lim)))
print("peak dBFS",round(20*np.log10(np.abs(out).max()),2))
out.astype(np.float32).tofile(f"{S}/bed_v4.f32")
