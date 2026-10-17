"""Split Media/Flower_In_A_Hurricane.flac into Demucs (htdemucs) stems at 44.1 kHz: <out>/stem_{drums,bass,other,vocals}.npy"""
import sys, subprocess, numpy as np, torch
from demucs.pretrained import get_model
from demucs.apply import apply_model
O=sys.argv[1]; m=get_model("htdemucs"); m.eval()
raw=subprocess.run(["ffmpeg","-loglevel","error","-i","Media/Flower_In_A_Hurricane.flac","-f","f32le","-ac","2","-ar","44100","-"],capture_output=True,check=True).stdout
x=np.frombuffer(raw,np.float32).reshape(-1,2).T.copy()
with torch.no_grad(): st=apply_model(m,torch.from_numpy(x)[None],shifts=1,overlap=0.25,progress=False)[0].numpy()
for i,s in enumerate(m.sources): np.save(f"{O}/stem_{s}.npy",st[i].T.astype(np.float32))
res=x.T-st.sum(0).T; print("stems",m.sources,"reconstruction error dB",round(10*np.log10((res**2).mean()/(x**2).mean()),1))
