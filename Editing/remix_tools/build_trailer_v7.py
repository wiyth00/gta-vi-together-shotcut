"""V7 bed: Claude's own scoring of the spot - one continuous run of the song chosen to match the picture.
Song = timeline + 73.237 s (drop on a downbeat; 126.05 BPM grid) from 0 s to the logo:
  0.00-3.6    same passage, vocals and drums muted: low-passed keys + bass under the dialogue
  3.6-6.45    build: keys/bass filters open, drums creep in high-passed, level rises out of the duck,
              "Only love" fades in from 5.9 s; full band on the 6.453 s downbeat (drift)
 10.22        "Only trust has a price to pay" - pink-smoke plane into the vault approach
 14.02        "Like a flower in a hurricane" - neon-club twirl / night pursuit
 16.97-19.13  "I will die before I walk away" - band stripped to kick + keys over the helicopter / hanging shots
 19.133       band crashes back on the jump into the pool: "walk away, walk away"
 21.567       logo: carries on the bar into the song's full-band instrumental (song ~111.9 s), then fades slowly -
              -10 dB over 21.85-23.15 s as the voiceover starts, then gliding out by the PlayStation sting
Usage: build_trailer_v7.py <scratch_dir>"""
import sys, subprocess, numpy as np
sys.path.insert(0,"Editing/remix_tools")
from remix_lib import Mix, BEAT, load_stems
S=sys.argv[1]; SR=48000; N=int(28.0*SR); m=Mix(SR,N); G=0.527
st=load_stems(S,SR)
DROP,LOGO,VIN,STRIP,JUMP=6.453,21.567,6.10,16.97,19.133
OFF=73.237
def lay(stem,off,t0,t1,xf=0.012):
    out=np.zeros((N,2)); a,b=m.ix(max(t0-xf,0)),m.ix(min(t1+xf,28.0))
    out[a:b]=stem[m.ix(m.t[a]+off):m.ix(m.t[a]+off)+(b-a)]
    return out*m.window(t0,t1,xf if t0>0 else 0,xf)[:,None]
OFF2=OFF+9*4*BEAT    # 9 bars on: the full-band instrumental (song ~111.9 s at the logo), same bar phase
parts={k:lay(v,OFF,0,LOGO)+lay(v,OFF2,LOGO,28.0,0.03) for k,v in st.items()}
dr,ba,ot,vo=parts["drums"],parts["bass"],parts["other"],parts["vocals"]
B0=3.6                                                       # build starts
ot=m.sweep(ot,"lp",[900,1600,3500,8000,0],B0,DROP-0.05); ba=m.sweep(ba,"lp",[300,600,0],B0,DROP-0.05)
duck=10**((-6*(1-m.ramp(B0+0.8,DROP)))/20)
drb=m.sweep(dr,"hp",[3000,1500,700,250],B0+0.9,DROP-0.05)   # thin drums creeping in
dr=drb*(m.ramp(B0+0.9,DROP-0.3)*(1-m.ramp(DROP-0.02,DROP)))[:,None]*0.8+dr*m.ramp(DROP-0.02,DROP)[:,None]
dr*=(10**(1.5*m.window(DROP,LOGO,0.005,0.05)/20))[:,None]
vo*=(m.ramp(5.9,6.40)*(1-m.ramp(20.6,21.1)))[:,None]
riser=m.riser(DROP-4*BEAT*2,DROP-0.02,0.03)
strip=m.window(STRIP,JUMP-0.01,0.25,0.01)
dr=dr*(1-strip)[:,None]+m.lp(dr,180)*strip[:,None]
ba=ba*(1-0.5*strip)[:,None]
vo=vo+m.reverb(vo*m.window(STRIP,JUMP+0.2,0.1,0.3)[:,None],decay=2.4)*0.45
riser2=m.riser(JUMP-4*BEAT,JUMP-0.02,0.035,seed=7)
gap=np.ones(N); pre=np.zeros((N,2))
music=dr+ba+ot+vo+riser+riser2
music*=(G*duck)[:,None]
fade_db=-10*m.ramp(21.85,23.15)-8*m.ramp(23.15,26.4)           # full through the logo hit, easing under the VO
music*=(10**(fade_db/20)*(1-m.ramp(25.6,26.95)))[:,None]       # gone by the PlayStation sting
# voices (same as V5)
def gate(v):
    e=np.sqrt(np.convolve((v**2).mean(1),np.ones(2400)/2400,"same"))+1e-9; d=20*np.log10(e)
    return v*(10**(np.clip((d+30)/6,0,1)*10/20-10/20))[:,None]
vo_open=gate(np.fromfile(f"{S}/voice_open.f32",np.float32).reshape(-1,2).astype(np.float64))
vo_end=np.fromfile(f"{S}/voice_vo.f32",np.float32).reshape(-1,2).astype(np.float64)
voice=np.zeros((N,2)); a=m.ix(62.098-61.0); voice[:m.ix(6.433)]=vo_open[a:a+m.ix(6.433)]
voice*=(1-m.ramp(5.85,6.30))[:,None]
seg=gate(vo_end[m.ix(LOGO+56.395-76.5):m.ix(28.0+56.395-76.5)])
raw=subprocess.run(["ffmpeg","-loglevel","error","-f","f32le","-ar","48000","-ac","2","-i","-","-af",
   "acompressor=threshold=-24dB:ratio=3:attack=8:release=180:makeup=2dB,lowshelf=f=160:g=2.5,highshelf=f=8000:g=-1.5,aecho=1.0:1.0:42|88:0.09|0.05",
   "-f","f32le","-"],input=seg.astype(np.float32).tobytes(),capture_output=True,check=True).stdout
proc=np.frombuffer(raw,np.float32).reshape(-1,2).astype(np.float64)[:len(seg)]
proc*=np.sqrt((seg**2).mean()/(proc**2).mean())*10**(1.5/20)
voice[m.ix(LOGO):m.ix(LOGO)+len(proc)]+=proc*m.ramp(LOGO,LOGO+0.4)[m.ix(LOGO):m.ix(LOGO)+len(proc)][:,None]
music.astype(np.float32).tofile(f"{S}/music_v7.f32")
out=music+voice
lim=0.89; k=np.abs(out)>lim; out[k]=np.sign(out[k])*(lim+(1-lim)*np.tanh((np.abs(out[k])-lim)/(1-lim)))
print("peak dBFS",round(20*np.log10(np.abs(out).max()),2))
subprocess.run(["ffmpeg","-loglevel","error","-f","f32le","-ar","48000","-ac","2","-i","-","-c:a","pcm_f32le","Media/Trailer_Audio_Claude_Score_V7.wav","-y"],
               input=out.astype(np.float32).tobytes(),check=True)
