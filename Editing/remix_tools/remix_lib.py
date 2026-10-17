"""Small stem-mixing toolkit: filters, sweeps, convolution reverb, risers, automation, mastering."""
import numpy as np, subprocess
from scipy.signal import butter, sosfiltfilt, fftconvolve, resample_poly
BEAT=0.47601; DOWNBEAT0=64.458          # song grid: 126.05 BPM, chorus downbeat at 64.458 s
def bar(t): return DOWNBEAT0+np.round((t-DOWNBEAT0)/(4*BEAT))*4*BEAT
def beat(t): return DOWNBEAT0+np.round((t-DOWNBEAT0)/BEAT)*BEAT
class Mix:
    def __init__(s,sr,n): s.sr=sr; s.n=n; s.t=np.arange(n)/sr
    def ix(s,t): return int(round(t*s.sr))
    def ramp(s,t0,t1):              # 0 -> 1 cosine
        x=np.clip((s.t-t0)/max(t1-t0,1e-6),0,1); return 0.5-0.5*np.cos(np.pi*x)
    def window(s,t0,t1,fin=0.01,fout=0.01):   # 1 inside [t0,t1] with short fades
        return s.ramp(t0-fin,t0)*(1-s.ramp(t1,t1+fout))
    def lp(s,x,f,order=4): return sosfiltfilt(butter(order,f,"low",fs=s.sr,output="sos"),x,axis=0)
    def hp(s,x,f,order=4): return sosfiltfilt(butter(order,f,"high",fs=s.sr,output="sos"),x,axis=0)
    def sweep(s,x,kind,freqs,t0,t1):
        """Filter sweep approximated by crossfading fixed filters spaced over [t0,t1]; outside it: first/last state."""
        f=s.lp if kind=="lp" else s.hp
        vers=[f(x,q) if q else x for q in freqs]; k=len(vers)-1; out=np.zeros_like(x)
        pos=np.clip((s.t-t0)/(t1-t0),0,1)*k
        for i,v in enumerate(vers):
            w=np.clip(1-np.abs(pos-i),0,1); out+=v*w[:,None]
        return out
    def reverb(s,x,decay=2.2,predelay=0.02,tone=6000,seed=1):
        r=np.random.default_rng(seed); L=int(decay*1.2*s.sr)
        ir=r.standard_normal((L,2))*np.exp(-6.9*np.arange(L)/(decay*s.sr))[:,None]
        ir=s.lp(ir,tone,2); ir=np.vstack([np.zeros((int(predelay*s.sr),2)),ir]); ir/=np.sqrt((ir**2).sum(0))
        y=np.stack([fftconvolve(x[:,c],ir[:,c])[:len(x)] for c in range(2)],1); return y
    def riser(s,t0,t1,level=0.08,seed=2):
        r=np.random.default_rng(seed); x=r.standard_normal((s.n,2))*s.ramp(t0,t1)[:,None]**2
        x=s.sweep(x,"hp",[2000,1000,400,150],t0,t1); x=s.lp(x,12000,2)
        return x*level*s.window(t0,t1,0.01,0.02)[:,None]
    def width(s,x,amt):              # stereo widen (mid/side)
        m=(x[:,0]+x[:,1])/2; d=(x[:,0]-x[:,1])/2*(1+amt); return np.stack([m+d,m-d],1)
def _ff(x,sr,af):
    raw=subprocess.run(["ffmpeg","-loglevel","error","-f","f32le","-ar",str(sr),"-ac","2","-i","-","-af",af,"-ar",str(sr),"-f","f32le","-"],
        input=x.astype(np.float32).tobytes(),capture_output=True,check=True).stdout
    y=np.frombuffer(raw,np.float32).reshape(-1,2).astype(np.float64); return y[:len(x)] if len(y)>=len(x) else np.pad(y,((0,len(x)-len(y)),(0,0)))
def lufs(x,sr):
    r=subprocess.run(["ffmpeg","-f","f32le","-ar",str(sr),"-ac","2","-i","-","-af","ebur128","-f","null","-"],
        input=x.astype(np.float32).tobytes(),capture_output=True).stderr.decode()
    return float(r.rsplit("I:",1)[1].split("LUFS")[0])
def master(x,sr,target=-11.0):
    """Gentle glue compression, static gain to the loudness target, then a peak limiter (keeps section dynamics)."""
    y=_ff(x,sr,"acompressor=threshold=-16dB:ratio=1.8:attack=25:release=250:makeup=1dB")
    for _ in range(2):
        y=y*10**((target-lufs(y,sr))/20); y=_ff(y,sr,"alimiter=limit=0.89:attack=3:release=60:level=false")
    return y
def load_stems(d,sr=44100):
    st={k:np.load(f"{d}/stem_{k}.npy").astype(np.float64) for k in ("drums","bass","other","vocals")}
    if sr!=44100: st={k:resample_poly(v,160,147,axis=0) for k,v in st.items()}
    return st
