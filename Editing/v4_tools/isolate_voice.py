"""Pull dialogue / voiceover out of the trailer mix by subtracting the aligned studio song.

For each piece (trailer start, end, song offset) the song is fine-aligned at 48 kHz, then a per-channel
frequency-domain Wiener filter (H = S_xy / S_xx) models the trailer's EQ/level on the song; residual = trailer - H*song.
Usage: isolate_voice.py <out_dir>; writes voice_open.f32 (trailer 61.0-69.0 s) and voice_vo.f32 (trailer 76.5-86.0 s).
"""
import numpy as np, subprocess, sys
from scipy.signal import csd, welch, stft, istft
O=sys.argv[1]; R=48000
def rd(p,extra=()):
    raw=subprocess.run(["ffmpeg","-loglevel","error",*extra,"-i",p,"-f","f32le","-ac","2","-ar","48000","-"],capture_output=True,check=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).astype(np.float64)
tr=rd("Media/Trailer_Source_Rockstar_4K.mp4",("-vn",)); so=rd("Media/Flower_In_A_Hurricane.flac")
def ix(t): return int(round(t*R))
def align(t0,t1,off):
    x=tr[ix(t0):ix(t1)].mean(1); best=(-1,0)
    for d in range(-240,241):
        y=so[ix(t0+off)+d:][:len(x)].mean(1); c=np.dot(x,y)/np.sqrt(np.dot(x,x)*np.dot(y,y)+1e-12); best=max(best,(c,d))
    return off+best[1]/R, best[0]
def cancel(t0,t1,off,fit=None):
    a,b=ix(t0),ix(t1); y=tr[a:b]; x=so[ix(t0+off):ix(t0+off)+(b-a)]
    f0,f1=(ix(fit[0])-a,ix(fit[1])-a) if fit else (0,b-a)
    out=np.zeros_like(y)
    for ch in range(2):
        _,Sxy=csd(x[f0:f1,ch],y[f0:f1,ch],fs=R,nperseg=4096); _,Sxx=welch(x[f0:f1,ch],fs=R,nperseg=4096)
        H=Sxy/(Sxx+1e-12)
        _,_,X=stft(x[:,ch],fs=R,nperseg=4096); _,_,Y=stft(y[:,ch],fs=R,nperseg=4096)
        _,r=istft(Y-H.conj()[:,None]*X if False else Y-H[:,None]*X,fs=R,nperseg=4096)
        out[:,ch]=r[:b-a]
    return out
def rms(z): return 10*np.log10((z**2).mean()+1e-15)
pieces={"open":[(61.0,67.45,57.30),(67.45,68.45,141.10),(68.45,69.0,95.40)],"vo":[(76.5,86.0,95.40)]}
for name,ps in pieces.items():
    segs=[]
    for t0,t1,off in ps:
        off,c=align(t0+0.05,min(t1,t0+2.0)-0.05,off)
        r=cancel(t0,t1,off); segs.append(r)
        print(name,t0,t1,"offset",round(off,5),"r",round(c,3),"trailer",round(rms(tr[ix(t0):ix(t1)]),1),"dB -> residual",round(rms(r),1),"dB")
    np.concatenate(segs).astype(np.float32).tofile(f"{O}/voice_{name}.f32")
