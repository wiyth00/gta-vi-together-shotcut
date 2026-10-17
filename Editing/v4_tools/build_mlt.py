import copy, xml.etree.ElementTree as ET
T=ET.parse("Together_4K_HQ_Bumper_Candidate.mlt"); root=T.getroot()
def tc(f):
    ms=round(f*1000/30); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
def byid(i): return root.find(f"*[@id='{i}']")
def prop(el,name,val=None):
    p=el.find(f"property[@name='{name}']")
    if val is None: return p
    if p is None: p=ET.SubElement(el,"property",name=name)
    p.text=str(val); return p
def filt(parent,fid,props):
    f=ET.SubElement(parent,"filter",id=fid)
    for k,v in props.items(): ET.SubElement(f,"property",name=k).text=str(v)
    return f
# audio bed
bed=byid("bed"); prop(bed,"resource","Media/Trailer_Audio_Candidate_V4.wav")
prop(bed,"shotcut:caption","Trailer candidate V4 — L-cut balcony tail + smoothed VO ending")
h=prop(bed,"shotcut:hash"); bed.remove(h)
# V1 picture edit: (producer, source_in_frame, length)
EDIT=[("clip0",92,59),("clip1",791,44),("clip2",1094,46),("clip3",2012,44),
 ("clip4",1409,29),("clip14",2183,30),("clip5",1467,35),("clip6",1663,49),
 ("clip9",1052,42),("clip10",1589,29),("clip11",1140,28),("clip12",2132,30),("clip13",2162,21),
 ("clip7",1797,30),
 ("clip15",2056,36),("clip16",2098,22),("clip17",2223,73),
 ("clip18",2296,22),("clip18b",2350,71),("clip19",2421,70),("clip20",2640,60)]
v=byid("video")
old=[e for e in v.findall("entry")]
for e in old: v.remove(e)
pos=0; starts={}
idx=list(v).index(v.find("filter"))
for i,(p,sin,ln) in enumerate(EDIT):
    starts[p]=pos; pos+=ln
    v.insert(idx+i,ET.Element("entry",producer=p,**{"in":tc(sin),"out":tc(sin+ln-1)}))
v.insert(idx+len(EDIT),ET.Element("entry",producer="logo_hold",**{"in":tc(0),"out":tc(29)}))
assert pos==870, pos
prop(v,"shotcut:name","V1 — Together V4 picture edit")
# full-frame PlayStation outro (source is letterboxed 3840x1920 inside 2160)
for pid in ("clip20","logo_hold"):
    filt(byid(pid),f"filter_{pid}_fill",{"background":"color:#00000000","mlt_service":"affine",
      "shotcut:filter":"affineSizePosition","transition.fill":1,"transition.distort":0,
      "transition.rect":"-240 -135 4320 2430 1","transition.valign":"middle","transition.halign":"center",
      "transition.threads":0,"shotcut:animIn":tc(0),"shotcut:animOut":tc(0)})
# slate overlays: patch over the logo row, then PS5 logo re-centred above CAPTURED ON PS5
src19=byid("clip19"); tractor=root.find("tractor")
def overlay(cid,caption,filters,pl_id,pl_name):
    c=copy.deepcopy(src19); c.set("id",cid); prop(c,"shotcut:caption",caption)
    hh=prop(c,"shotcut:hash")
    if hh is not None: c.remove(hh)
    for fid,props in filters: filt(c,fid,props)
    root.insert(list(root).index(tractor),c)
    pl=ET.Element("playlist",id=pl_id); ET.SubElement(pl,"property",name="shotcut:video").text="1"
    ET.SubElement(pl,"property",name="shotcut:name").text=pl_name
    # start once the GTA logo has fully dissolved out (source frame 2432), run to the end of the slate shot
    st=starts["clip19"]+(2432-2421); ln=70-(2432-2421)
    ET.SubElement(pl,"blank",length=tc(st))
    ET.SubElement(pl,"entry",producer=cid,**{"in":tc(2432),"out":tc(2432+ln-1)})
    ET.SubElement(pl,"blank",length=tc(900-st-ln))
    root.insert(list(root).index(tractor),pl)
def aff(rect): return {"background":"color:#00000000","mlt_service":"affine","shotcut:filter":"affineSizePosition",
    "transition.fill":0,"transition.distort":0,"transition.rect":rect,"transition.valign":"top","transition.halign":"left","transition.threads":0}
def crop(rect): return {"rect":rect,"radius":0,"color":"#00000000","mlt_service":"qtcrop","shotcut:filter":"cropRectangle"}
# clean plate: pre-rendered 1240x200 RGBA patch (background from 140 px above, feathered alpha), source frames 2432-2490
plate=ET.Element("producer",id="slate_plate")
for k,val in (("length",59),("eof","pause"),("resource","Media/Slate_Clean_Plate_4K.mov"),("mlt_service","avformat"),("seekable",1),
              ("audio_index",-1),("video_index",0),("shotcut:caption","Slate clean plate — hides Xbox and original PS5 logo")):
    ET.SubElement(plate,"property",name=k).text=str(val)
filt(plate,"filter_plate_pos",aff("1300 1640 1240 200 1"))
root.insert(list(root).index(tractor),plate)
pl=ET.Element("playlist",id="slate_patch_track"); ET.SubElement(pl,"property",name="shotcut:video").text="1"
ET.SubElement(pl,"property",name="shotcut:name").text="V3 — Slate clean plate"
st=starts["clip19"]+11
ET.SubElement(pl,"blank",length=tc(st)); ET.SubElement(pl,"entry",producer="slate_plate",**{"in":tc(0),"out":tc(58)})
ET.SubElement(pl,"blank",length=tc(900-st-59)); root.insert(list(root).index(tractor),pl)
overlay("slate_ps5","Slate PS5 logo — centred over CAPTURED ON PS5",
    [("filter_ps5_crop",crop("1360 1682 395 103 1")),("filter_ps5_shift",aff("362 0 3840 2160 1"))],
    "slate_ps5_track","V4 — Slate PS5 logo (Lighten)")
for pl,mode in (("slate_patch_track",0),("slate_ps5_track",17)):
    n=len(tractor.findall("track"))
    tr=ET.Element("track",producer=pl,hide="audio")
    tractor.insert(list(tractor).index(tractor.findall("track")[-1])+1,tr)
    t=ET.SubElement(tractor,"transition",id=f"transition_{pl}",out=tc(899))
    for k,val in (("a_track",0),("b_track",n),("compositing",mode),("distort",0),("rotate_center",0),("mlt_service","qtblend"),("always_active",1)):
        ET.SubElement(t,"property",name=k).text=str(val)
prop(tractor,"shotcut:name","Together — 30-second spot (V4)")
ET.indent(T,"  ")
T.write("Together_4K_HQ_Bumper_V4.mlt",encoding="utf-8",xml_declaration=True)
print("ok")
