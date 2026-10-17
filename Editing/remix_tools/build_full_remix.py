"""Claude's full-length remix of Flower In A Hurricane from Demucs stems. Usage: build_full_remix.py <stem_dir> <out.wav>"""
import sys, numpy as np, subprocess
sys.path.insert(0,"Editing/remix_tools")
from remix_lib import Mix, bar, beat, BEAT, master, load_stems
D,OUT=sys.argv[1],sys.argv[2]; SR=44100
st=load_stems(D); n=len(st["drums"]); m=Mix(SR,n); T=n/SR
dr,ba,ot,vo=st["drums"].copy(),st["bass"].copy(),st["other"].copy(),st["vocals"].copy()
B=lambda t: float(bar(t)); b=lambda t: float(beat(t))
# 1  intro opens up: keys + bass low-passed, sweeping open over the first 16 bars
i_end=B(31.0)
ot=m.sweep(ot,"lp",[350,700,1500,4000,0],B(1.0),i_end); ba=m.sweep(ba,"lp",[180,400,0],B(1.0),B(16.0))
# 2  reverb throw on the "oh" vocal (~27-30 s)
vo=vo+m.reverb(vo*m.window(26.5,31.0,0.3,0.5)[:,None],decay=3.0)*0.6
# 3  breakdown 35-47 s: wide, washed keys
ot=ot+m.reverb(ot*m.window(35.0,B(47.6),0.5,0.5)[:,None],decay=2.5)*0.18
ot=ot*(1-m.window(35.0,B(47.6),0.5,0.5))[:,None]+m.width(ot,0.4)*m.window(35.0,B(47.6),0.5,0.5)[:,None]
# 4  drums enter thin (high-passed) and fill out over 4 bars; riser + one-beat dropout before the entry
d_in=B(48.0); dr=m.sweep(dr,"hp",[900,400,150,0],d_in,d_in+4*4*BEAT)
riser1=m.riser(d_in-4*4*BEAT,d_in-BEAT,0.05)
drop1=1-m.window(d_in-BEAT,d_in-0.005,0.005,0.005)
# 5  pre-chorus: one-beat dropout (vocals stay) then chorus slam with +2 dB drums, +1.5 dB bass
ch=64.458
riser2=m.riser(ch-4*4*BEAT,ch-BEAT,0.06,seed=3)
gap=1-m.window(ch-BEAT,ch-0.005,0.005,0.005)
for x,g in ((dr,2.0),(ba,1.5)): x*=(10**(g*m.window(ch,94.6,0.01,0.3)/20))[:,None]
# 6  verse 94.9-109: muffled drums, echo on vocals
v0,v1=B(94.6),B(109.8)
dr=dr*(1-m.window(v0,v1,0.05,0.05))[:,None]+m.lp(dr,2500)*m.window(v0,v1,0.05,0.05)[:,None]
vo=vo+m.reverb(vo*m.window(v0,v1,0.05,0.2)[:,None],decay=1.4,predelay=0.06)*0.35
# 7  "Let's take it fast" a cappella: band out from the break until the beat on "fast", then slam
a0,a1=124.0,b(126.80)
band_gap=1-m.window(a0,a1,0.15,0.005)
vo=vo+m.reverb(vo*m.window(a0,a1+0.3,0.05,0.4)[:,None],decay=2.6)*0.55
ot_f=m.lp(ot,600); ot=ot*band_gap[:,None]+ot_f*m.window(a0,a1,0.15,0.005)[:,None]*0.6
# 8  breakdown 142-164: washed, wide
k0,k1=B(142.0),B(164.0)
ot=ot+m.reverb(ot*m.window(k0,k1,0.5,0.3)[:,None],decay=3.0)*0.4
vo=vo+m.reverb(vo*m.window(k0,k1,0.5,0.3)[:,None],decay=2.2)*0.3
riser3=m.riser(k1-4*4*BEAT,k1-BEAT,0.06,seed=4); gap3=1-m.window(k1-BEAT,k1-0.005,0.005,0.005)
# 9  bridge 179.7-194: drums cut to kick only
r0,r1=B(179.5),B(195.0)
dr=dr*(1-m.window(r0,r1,0.1,0.02))[:,None]+m.lp(dr,180)*m.window(r0,r1,0.1,0.02)[:,None]
riser4=m.riser(r1-4*4*BEAT,r1-BEAT,0.06,seed=5)
# 10 final chord: long tail
tail=m.reverb((dr+ba+ot+vo)*m.window(209.6,211.5,0.02,1.0)[:,None],decay=5.0,tone=5000)*0.5
mix=(dr*drop1[:,None]*gap[:,None]*band_gap[:,None]*gap3[:,None]
     +ba*drop1[:,None]*gap[:,None]*band_gap[:,None]*gap3[:,None]
     +ot*gap[:,None]*gap3[:,None]+vo+riser1+riser2+riser3+riser4+tail)
# keep the breakdowns low (original contrast: ~5-6 dB under the body)
mix*=(10**((-4.0*m.window(35.0,B(47.6),0.8,0.8)-3.0*m.window(k0,k1-0.5,0.8,0.5))/20))[:,None]
mix*=(1-m.ramp(T-6,T-0.2))[:,None]
mix=master(mix,SR,-9.5)
subprocess.run(["ffmpeg","-loglevel","error","-f","f32le","-ar",str(SR),"-ac","2","-i","-","-c:a","pcm_s24le",OUT,"-y"],
               input=mix.astype(np.float32).tobytes(),check=True)
print("wrote",OUT,round(T,1),"s")
