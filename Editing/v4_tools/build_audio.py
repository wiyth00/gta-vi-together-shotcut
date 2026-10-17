import numpy as np, sys, wave, subprocess
S=sys.argv[1]; R=48000
def rd(p):
    raw=subprocess.run(["ffmpeg","-loglevel","error","-i",p,"-f","f32le","-ac","2","-ar","48000","-"],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).astype(np.float64)
bed=rd("Media/Trailer_Audio_Candidate_Polish.wav"); proc=rd(f"{S}/bed_proc.wav")[:len(bed)]; src=rd(f"{S}/src_tail.wav")
# 0) 11.03 s instrumental -> vocal chorus edit: 0.5 s equal-power crossfade, vocal section pre-rolled from source
pre=rd(f"{S}/src_xf.wav")  # source 27.0-29.0 s, unprocessed
e=int(round(11.03*R)); X=int(0.5*R); p0=int(round((27.901354-27.0)*R))
gm=np.sqrt((bed[e:e+int(0.4*R)]**2).mean()/((pre[p0:p0+int(0.4*R)]**2).mean()+1e-12))
k=np.arange(X)/X
bed=bed.copy()
bed[e-X:e]=bed[e-X:e]*np.cos(0.5*np.pi*k)[:,None]+pre[p0-X:p0]*(gm*np.sin(0.5*np.pi*k))[:,None]
print("xfade gain",round(gm,3))
n=len(bed); t=np.arange(n)/R
def ramp(t0,t1):  # cosine 0->1
    x=np.clip((t-t0)/(t1-t0),0,1); return 0.5-0.5*np.cos(np.pi*x)
# 1) ending: dry->processed blend, plus gentle level lift that fills the VO dip
w=ramp(22.30,22.90)
gdb=2.5*ramp(22.40,23.10)*(1-ramp(26.70,27.50))
out=((1-w)[:,None]*bed+w[:,None]*proc)*(10**(gdb/20))[:,None]
# 2) L-cut: carry the balcony line 9 frames past the 6.433 s cut, fading out
c=int(round(6.4333333*R)); L=int(0.30*R); s0=int(round((68.5313333-67.0)*R))
tail=src[s0:s0+L]
ref_b=bed[c-int(0.25*R):c]; ref_s=src[s0-int(0.25*R):s0]
match=np.sqrt((ref_b**2).mean()/((ref_s**2).mean()+1e-12))
fade=np.cos(0.5*np.pi*np.arange(L)/L)**2
out[c:c+L]+=tail*(match*10**(-6/20)*fade)[:,None]
pk=np.abs(out).max(); print("bedpk",20*np.log10(np.abs(bed).max()),"at",np.abs(bed).max(1).argmax()/R,"outpk at",np.abs(out).max(1).argmax()/R,"match",round(match,3),"peak dBFS",round(20*np.log10(pk),2))
lim=0.89; a=np.abs(out); m=a>lim; out[m]=np.sign(out[m])*(lim+(1-lim)*np.tanh((a[m]-lim)/(1-lim))); print("after",20*np.log10(np.abs(out).max()))
out.astype(np.float32).tofile(f"{S}/bed_v4.f32")
