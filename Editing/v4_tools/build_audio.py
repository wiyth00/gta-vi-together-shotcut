import numpy as np, sys, wave, subprocess
S=sys.argv[1]; R=48000
def rd(p):
    raw=subprocess.run(["ffmpeg","-loglevel","error","-i",p,"-f","f32le","-ac","2","-ar","48000","-"],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).astype(np.float64)
bed=rd("Media/Trailer_Audio_Candidate_Polish.wav")
# 0) the chorus section entered mid-phrase at 11.03 s (source 27.901 s). Start it two beats (0.975 s at 123 BPM)
#    earlier instead, in the instrumental gap before the vocal phrase (source 26.926 s), and rejoin the polished bed by 11.33 s.
pre=rd(f"{S}/src_xf.wav")  # source 25.0-31.0 s, unprocessed
def at(src_t): return int(round((src_t-25.0)*R))
e0=11.03; d=2*60/123.0; e=e0-d
i_e=int(round(e*R)); i_0=int(round(e0*R)); X=int(0.25*R); Y=int(0.30*R)
# exact alignment of source to the bed's chorus (search +/-20 ms)
ref=bed[i_0+int(0.1*R):i_0+int(0.6*R),0]; best=(-1,0)
for lag in range(-960,961,4):
    seg=pre[at(27.901354)+int(0.1*R)+lag:][:len(ref),0]
    c=np.dot(ref,seg)/np.sqrt(np.dot(ref,ref)*np.dot(seg,seg)+1e-12); best=max(best,(c,lag))
lag=best[1]; base=at(27.901354)+lag-i_0   # pre index = base + timeline index
gm=np.sqrt((bed[i_0:i_0+int(0.4*R)]**2).mean()/((pre[base+i_0:base+i_0+int(0.4*R)]**2).mean()+1e-12))
src_line=pre[base+i_e-X:base+i_0+Y]*gm
new=bed.copy(); k=np.arange(X)/X
new[i_e-X:i_e]=bed[i_e-X:i_e]*np.cos(0.5*np.pi*k)[:,None]+src_line[:X]*np.sin(0.5*np.pi*k)[:,None]
new[i_e:i_0]=src_line[X:X+i_0-i_e]
k=np.arange(Y)/Y
new[i_0:i_0+Y]=src_line[X+i_0-i_e:]*(1-k)[:,None]+bed[i_0:i_0+Y]*k[:,None]
bed=new
print("chorus edit moved to",round(e,3),"s; align corr",round(best[0],3),"lag ms",round(lag/48,2),"gain",round(gm,3))
# 0b) from the twirl (beat at 13.119 s) play "Let's take it fast, just like a flash..." (source 37.622 s on) through to the
#     end, fading out under the "Grand Theft Auto VI" voiceover. Replaces the 13.567-22.733 s section, including its
#     clipped "Like..." at 13.4 s. Beat grids match: timeline 13.607 s <-> source 38.110 s at 123 BPM.
fl=rd(f"{S}/src_flash.wav")   # source 36.0-50.0 s, unprocessed
vo=rd(f"{S}/src_vo.wav")      # source 78.0-80.0 s, unprocessed
def ix(t): return int(round(t*R))
b0=13.119; off=38.110-13.607; vo_t=22.733
song=np.zeros_like(bed); i0=ix(b0-0.06); i1=ix(24.4)
song[i0:i1]=fl[ix(b0-0.06+off-36.0):ix(b0-0.06+off-36.0)+(i1-i0)]*gm
tt=np.arange(n0:=len(bed))/R
def cramp(t0,t1):
    x=np.clip((tt-t0)/(t1-t0),0,1); return 0.5-0.5*np.cos(np.pi*x)
song_g=np.sin(0.5*np.pi*np.clip((tt-(b0-0.06))/0.12,0,1))*(1-cramp(22.60,24.30))
# old bed: keep up to the twirl, then only the voiceover section (src 79.128 s on), with a 60 ms pre-roll fade-in
old_g=np.cos(0.5*np.pi*np.clip((tt-(b0-0.06))/0.12,0,1))
pre_vo=np.zeros_like(bed); j0=ix(vo_t-0.06); j1=ix(vo_t)
pre_vo[j0:j1]=vo[ix(79.128-0.06-78.0):ix(79.128-0.06-78.0)+(j1-j0)]*gm*np.sin(0.5*np.pi*np.arange(j1-j0)/(j1-j0))[:,None]
vo_mask=(tt>=vo_t).astype(float)
bed=bed*(old_g+vo_mask)[:,None]+pre_vo+song*song_g[:,None]
print("flash section from",round(b0,3),"s = source",round(b0+off,3),"s")
# processed copy must be made from the re-cut bed
import os
bed.astype(np.float32).tofile(f"{S}/bed_recut.f32")
subprocess.run(["ffmpeg","-loglevel","error","-f","f32le","-ar","48000","-ac","2","-i",f"{S}/bed_recut.f32","-af",
  "acompressor=threshold=-22dB:ratio=2.5:attack=12:release=220:makeup=1.5dB,lowshelf=f=180:g=2,highshelf=f=7500:g=-1.5,aecho=0.85:0.5:38|74:0.10|0.06",
  "-c:a","pcm_f32le",f"{S}/bed_proc.wav","-y"],check=True)
proc=rd(f"{S}/bed_proc.wav")[:len(bed)]
n=len(bed); t=np.arange(n)/R
def ramp(t0,t1):  # cosine 0->1
    x=np.clip((t-t0)/(t1-t0),0,1); return 0.5-0.5*np.cos(np.pi*x)
# 1) ending: dry->processed blend, plus gentle level lift that fills the VO dip
w=ramp(22.30,22.90)
gdb=2.5*ramp(22.40,23.10)*(1-ramp(26.70,27.50))
out=((1-w)[:,None]*bed+w[:,None]*proc)*(10**(gdb/20))[:,None]
pk=np.abs(out).max(); print("bedpk",20*np.log10(np.abs(bed).max()),"at",np.abs(bed).max(1).argmax()/R,"outpk at",np.abs(out).max(1).argmax()/R,"peak dBFS",round(20*np.log10(pk),2))
lim=0.89; a=np.abs(out); m=a>lim; out[m]=np.sign(out[m])*(lim+(1-lim)*np.tanh((a[m]-lim)/(1-lim))); print("after",20*np.log10(np.abs(out).max()))
out.astype(np.float32).tofile(f"{S}/bed_v4.f32")
