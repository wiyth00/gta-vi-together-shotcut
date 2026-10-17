"""V6 bed: Claude's stem remix of the song under the isolated (Demucs-cleaned) trailer voices.
  0.00-6.45   bass + keys only, low-passed and ducked under the dialogue; riser; one-beat dropout
  6.453       drums slam in on the chorus downbeat (picture drop): "Only love never hesitates"
  9.786       instrumental fill (song = t + 112.2696)
 12.60-14.545 band drops out (from the song's own break): filtered keys + "Let's take it ..." vocal with reverb
 14.545       band slams back on "FAST" (cut to the night pursuit): "just like a flash ... you and me"
 21.567       logo: the song's final chord with a long reverb tail under the voiceover
Usage: build_trailer_v6.py <scratch_dir>  (stems + voice_open.f32 / voice_vo.f32 from the V5 pipeline)"""
import sys, subprocess, numpy as np
sys.path.insert(0,"Editing/remix_tools")
from remix_lib import Mix, BEAT, load_stems
S=sys.argv[1]; SR=48000; N=int(28.0*SR); m=Mix(SR,N); G=0.527
st=load_stems(S,SR)
DROP,CUT,BRK,SLAM,LOGO=6.453,9.786,12.60,14.545,21.567
def lay(stem,off,t0,t1,xf=0.012):
    out=np.zeros((N,2)); a,b=m.ix(max(t0-xf,0)),m.ix(min(t1+xf,28.0))
    out[a:b]=stem[m.ix(m.t[a]+off):m.ix(m.t[a]+off)+(b-a)]
    return out*m.window(t0,t1,xf if t0>0 else 0,xf)[:,None]
parts={k:lay(v,58.005,0,CUT)+lay(v,112.2696,CUT,LOGO)+lay(v,209.70-LOGO,LOGO,28.0,0.008) for k,v in st.items()}
dr,ba,ot,vo=parts["drums"],parts["bass"],parts["other"],parts["vocals"]
intro=m.window(0,DROP-BEAT,0,0.005)
ot=ot*(1-intro)[:,None]+m.lp(ot,900)*intro[:,None]; ba=ba*(1-intro)[:,None]+m.lp(ba,300)*intro[:,None]
duck=10**((-6*(1-m.ramp(5.4,DROP-BEAT)))/20)
gap=1-m.window(DROP-BEAT,DROP-0.004,0.004,0.004)
dr*=(1-m.window(0,DROP-0.004,0,0.004))[:,None]*(10**(2*m.window(DROP,CUT,0.005,0.05)/20))[:,None]
vo*=(1-m.window(0,DROP-0.004,0,0.004))[:,None]
pre=m.reverb((ot+ba)*m.window(DROP-3*BEAT,DROP-BEAT,0.05,0.01)[:,None],decay=1.6)*0.6*m.window(DROP-BEAT,DROP,0.005,0.005)[:,None]
riser=m.riser(DROP-4*BEAT*2,DROP-BEAT,0.035)
brk=m.window(BRK,SLAM-0.004,0.15,0.004)
dr*=(1-brk)[:,None]; ba*=(1-brk)[:,None]
ot=ot*(1-brk)[:,None]+m.lp(ot,700)*brk[:,None]*0.85
ot=ot+m.reverb(ot*m.window(BRK-0.5,BRK+0.3,0.1,0.2)[:,None],decay=2.0)*0.35
vo=vo+m.reverb(vo*m.window(BRK,SLAM+0.3,0.05,0.4)[:,None],decay=2.4)*0.5
riser2=m.riser(SLAM-4*BEAT,SLAM-0.03,0.03,seed=7)
chord=(dr+ba+ot+vo)*m.window(LOGO,28.0,0.008,0.01)[:,None]
tail=m.reverb(chord*m.window(LOGO,LOGO+1.5,0.008,0.8)[:,None],decay=4.5,tone=5000)*0.45
music=((dr+ba)*gap[:,None]+ot*gap[:,None]+vo)*(1-m.window(LOGO,28.0,0.008,0.01))[:,None]+chord+tail+riser+riser2+pre
music*=(G*duck)[:,None]
music*=(10**((-3*m.ramp(22.6,23.0))/20)*(1-m.ramp(26.6,27.9)))[:,None]     # sit under the voiceover, clear by the sting
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
out=music+voice
lim=0.89; k=np.abs(out)>lim; out[k]=np.sign(out[k])*(lim+(1-lim)*np.tanh((np.abs(out[k])-lim)/(1-lim)))
print("peak dBFS",round(20*np.log10(np.abs(out).max()),2))
subprocess.run(["ffmpeg","-loglevel","error","-f","f32le","-ar","48000","-ac","2","-i","-","-c:a","pcm_f32le","Media/Trailer_Audio_Claude_Remix_V6.wav","-y"],
               input=out.astype(np.float32).tobytes(),check=True)
