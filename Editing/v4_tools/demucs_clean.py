"""Second pass on the isolated voices: keep only Demucs (htdemucs) 'vocals' stem to strip leftover music.
Usage: demucs_clean.py <scratch_dir>  (reads/writes voice_open.f32 and voice_vo.f32, 48 kHz stereo; keeps *_sub.f32 copies)"""
import sys, subprocess, numpy as np, torch, shutil
from demucs.pretrained import get_model
from demucs.apply import apply_model
S=sys.argv[1]; m=get_model("htdemucs"); m.eval()
def conv(data,src,dst):
    p=subprocess.run(["ffmpeg","-loglevel","error","-f","f32le","-ar",str(src),"-ac","2","-i","-","-f","f32le","-ar",str(dst),"-ac","2","-"],
                     input=data.astype(np.float32).tobytes(),capture_output=True,check=True).stdout
    return np.frombuffer(p,np.float32).reshape(-1,2)
for nm in ("open","vo"):
    shutil.copy(f"{S}/voice_{nm}.f32",f"{S}/voice_{nm}_sub.f32")
    v=np.fromfile(f"{S}/voice_{nm}_sub.f32",np.float32).reshape(-1,2); n=len(v)
    x=torch.from_numpy(conv(v,48000,m.samplerate).T.copy())[None]
    with torch.no_grad(): st=apply_model(m,x,shifts=2,overlap=0.5,progress=False)[0]
    voc=st[m.sources.index("vocals")].numpy().T
    out=conv(voc,m.samplerate,48000)[:n]
    if len(out)<n: out=np.pad(out,((0,n-len(out)),(0,0)))
    out.astype(np.float32).tofile(f"{S}/voice_{nm}.f32")
    print(nm,"before",round(10*np.log10((v**2).mean()),1),"dB  vocals stem",round(10*np.log10((out**2).mean()),1),"dB")
