"""Build Media/Trailer_Audio_Own_Mix_V5.wav: an original music edit of the studio song under isolated trailer voices.

Grid: 126.05 BPM, timeline beat at 6.453 / 13.593 s (beat = 0.47601 s).
  0.000-9.786  song 58.005 s on: build under the opening dialogue (ducked), chorus downbeat on the 6.45 s drop,
               "Only love never hesitates"
  9.786        on the beat, after "hesitates": instrumental fill -> break -> "Let's take it fast, just like a flash"
               on the twirl (~13.45 s) -> "...you and me" (song = t + 112.2696)
 21.567        logo: the song's final chord and ring-out (song 209.70 s), decaying under the voiceover
Voices come from isolate_voice.py (trailer mix minus the aligned song). The voiceover alone gets compression,
warmth and a little room.
Usage: build_own_mix.py <scratch_dir>  (expects voice_open.f32 / voice_vo.f32 there)
"""
import numpy as np, subprocess, sys
S=sys.argv[1]; R=48000; N=int(28.0*R); tt=np.arange(N)/R
def rd(p,extra=()):
    raw=subprocess.run(["ffmpeg","-loglevel","error",*extra,"-i",p,"-f","f32le","-ac","2","-ar","48000","-"],capture_output=True,check=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).astype(np.float64)
def ix(t): return int(round(t*R))
def ramp(t0,t1):
    x=np.clip((tt-t0)/(t1-t0),0,1); return 0.5-0.5*np.cos(np.pi*x)
song=rd("Media/Flower_In_A_Hurricane.flac"); G=0.527     # level of the song in the trailer mix
def place(off,t0,t1,xf=0.03):
    out=np.zeros((N,2)); a,b=ix(max(t0-xf,0)),ix(min(t1+xf,28.0))
    out[a:b]=song[ix(tt[a]+off):ix(tt[a]+off)+(b-a)]
    g=np.clip((tt-(t0-xf))/(2*xf),0,1)*(1-np.clip((tt-(t1-xf))/(2*xf),0,1)) if t0>0 else (1-np.clip((tt-(t1-xf))/(2*xf),0,1))
    return out*np.sin(0.5*np.pi*g)[:,None]
CUT=9.786; LOGO=21.567
music=place(58.005,0.0,CUT)+place(112.2696,CUT,LOGO)+place(209.70-LOGO,LOGO,28.0,xf=0.015)
duck=10**((-7*(1-ramp(5.5,6.40)))/20)                       # -7 dB under the dialogue, swelling into the drop
music*=(G*duck)[:,None]*(1-ramp(26.6,27.9))[:,None]
def gate(v):
    e=np.sqrt(np.convolve((v**2).mean(1),np.ones(2400)/2400,"same"))+1e-9; d=20*np.log10(e)
    return v*(10**(np.clip((d+30)/6,0,1)*10/20-10/20))[:,None]   # up to -10 dB on the leftover music between words
vo_open=gate(np.fromfile(f"{S}/voice_open.f32",np.float32).reshape(-1,2).astype(np.float64))
vo_end=np.fromfile(f"{S}/voice_vo.f32",np.float32).reshape(-1,2).astype(np.float64)
voice=np.zeros((N,2))
a=ix(62.098-61.0); voice[:ix(6.433)]=vo_open[a:a+ix(6.433)]
voice*=(1-ramp(5.85,6.30))[:,None]
# voiceover: trailer = t + 56.395 -> process alone (compression, warmth, light room), loudness-matched
seg=gate(vo_end[ix(LOGO+56.395-76.5):ix(28.0+56.395-76.5)])
seg.astype(np.float32).tofile(f"{S}/vo_raw.f32")
raw=subprocess.run(["ffmpeg","-loglevel","error","-f","f32le","-ar","48000","-ac","2","-i",f"{S}/vo_raw.f32","-af",
   "acompressor=threshold=-24dB:ratio=3:attack=8:release=180:makeup=2dB,lowshelf=f=160:g=2.5,highshelf=f=8000:g=-1.5,aecho=1.0:1.0:42|88:0.09|0.05",
   "-f","f32le","-"],capture_output=True,check=True).stdout
proc=np.frombuffer(raw,np.float32).reshape(-1,2).astype(np.float64)[:len(seg)]
proc*=np.sqrt((seg**2).mean()/(proc**2).mean())*10**(1.5/20)
voice[ix(LOGO):ix(LOGO)+len(proc)]+=proc*ramp(LOGO,LOGO+0.4)[ix(LOGO):ix(LOGO)+len(proc)][:,None]
out=music+voice
lim=0.89; m=np.abs(out)>lim
out[m]=np.sign(out[m])*(lim+(1-lim)*np.tanh((np.abs(out[m])-lim)/(1-lim)))
print("peak dBFS",round(20*np.log10(np.abs(out).max()),2))
out.astype(np.float32).tofile(f"{S}/own_mix.f32")
