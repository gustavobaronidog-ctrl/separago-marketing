import os,re,json,datetime,subprocess,sys
from concurrent.futures import ThreadPoolExecutor
R=os.getcwd()
src=open(R+"/gerar/gerar.py").read()
src=src.split('T="/tmp/sgb"')[0]
src=src.replace("#FFC53D","#9ADBBB").replace("#FF8A00","#0F7A55")
g={"__name__":"g3","__file__":R+"/gerar/gerar.py"}
os.environ.setdefault("FONTDIR","/usr/share/fonts/opentype/inter")
exec(src,g)
g2={}
exec(open(R+"/gerar/conteudo2.py").read(),g2)
C=g["C"]; C2=g2["C2"]; SPECIAL=g2["SPECIAL"]
g["BAG"]='<svg viewBox="0 0 200 200" width="120" height="120"><rect width="200" height="200" rx="46" fill="#F6F5F2"/><path d="M72 80 C72 44 132 44 132 80" stroke="#E5452D" stroke-width="13" stroke-linecap="round" fill="none"/><path d="M52 76 H152 L160 148 Q161 160 149 160 H55 Q43 160 44 148 Z" fill="#0F7A55"/><path d="M84 118 H122 M106 100 L124 118 L106 136" stroke="#fff" stroke-width="11" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M22 112 H38 M16 130 H34" stroke="#0F7A55" stroke-width="8" stroke-linecap="round" opacity=".5"/></svg>'
page=g["page"]; BASE=g["BASE"]
TAGS=["#separago #mercado #supermercado #comerciolocal","#separago #lanchonete #pizzaria #delivery","#separago #varejo #donodemercado #gestao","#separago #mercadinho #empreendedorismo #vendas"]
allc={}
for i,(slug,bg,sl,leg,tg) in enumerate(C,1): allc[f"c{i:02d}-{slug}"]=(slug,bg,sl,leg,tg)
for j,(slug,bg,sl,leg) in enumerate(C2):
    allc[f"c{13+j:02d}-{slug}"]=(slug,bg,sl,leg,TAGS[j%4])
ids=list(allc)
c01,c02=ids[0],ids[1]
c10=[x for x in ids if allc[x][0]=='black-friday-premium'][0]
normal=[x for x in ids[2:12] if x!=c10]+[x for x in ids[12:] if allc[x][0] not in SPECIAL]
spec={SPECIAL[allc[x][0]]:x for x in ids[12:] if allc[x][0] in SPECIAL}
seq=list(normal)
seq.insert(14,c10)
for k in sorted(spec): seq.insert(k,spec[k])
assert len(seq)==55,len(seq)
T="/tmp/sgb"; os.makedirs(T,exist_ok=True)
def shot(a):
    h,p,n=a
    subprocess.run(["google-chrome","--headless=new","--no-sandbox","--disable-gpu","--allow-file-access-from-files","--hide-scrollbars","--window-size=1080,1350","--user-data-dir=/tmp/cd_%s"%n,"--screenshot="+p,"file://"+h],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=180)
jobs=[]
from PIL import Image
for iid in ids[1:]:
    slug,bg,sl,leg,tg=allc[iid]; out=f"{R}/midia/{iid[:3]}"; os.makedirs(out,exist_ok=True)
    for si,tx in enumerate(sl,1):
        h=f"{T}/{iid[:3]}_{si}.html"; p=f"{T}/{iid[:3]}_{si}.png"
        open(h,"w").write(page(tx,si,len(sl),bg if si==1 else None,si==len(sl)))
        jobs.append((h,p,f"{iid[:3]}{si}"))
with ThreadPoolExecutor(4) as ex: list(ex.map(shot,jobs))
for iid in ids[1:]:
    out=f"{R}/midia/{iid[:3]}"
    for si in range(1,7): Image.open(f"{T}/{iid[:3]}_{si}.png").convert("RGB").save(f"{out}/{si}.jpg",quality=90)
def reel(iid):
    d=f"{R}/midia/{iid[:3]}"; lst=f"{T}/{iid[:3]}.txt"
    with open(lst,"w") as f:
        for si in range(1,7): f.write(f"file '{d}/{si}.jpg'\nduration 3.4\n")
        f.write(f"file '{d}/6.jpg'\n")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lst,"-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-vf","scale=1080:1350,pad=1080:1920:0:285:white,fps=30,format=yuv420p","-t","20.4","-c:v","libx264","-preset","veryfast","-crf","23","-c:a","aac","-shortest","-movflags","+faststart",f"{d}/reel.mp4"],check=True)
with ThreadPoolExecutor(3) as ex: list(ex.map(reel,seq))
FP=R+"/fila/fila.json"; old={x["id"]:x for x in json.load(open(FP))}
def item(iid,data,hora,tipo):
    slug,bg,sl,leg,tg=allc[iid]; c=iid[:3]; rid=iid if tipo=="carrossel" else "r-"+iid
    o={"id":rid,"data":data,"hora":hora,"tipo":tipo,"legenda":leg+"\n\n"+tg}
    if tipo=="carrossel": o["imagens"]=[f"{BASE}/{c}/{s}.jpg" for s in range(1,7)]
    else: o["video_url"]=f"{BASE}/{c}/reel.mp4"
    o["status"]="pendente"
    if rid in old and old[rid].get("status")!="pendente": return old[rid]
    return o
fila=[old[c01] if c01 in old else item(c01,"2026-11-09","12:00","carrossel")]
fila.append(item(c02,"2026-11-09","19:00","carrossel"))
d0=datetime.date(2026,11,10)
for k,iid in enumerate(seq):
    dt=(d0+datetime.timedelta(days=k)).isoformat()
    fila.append(item(iid,dt,"12:00","carrossel")); fila.append(item(iid,dt,"19:00","reel"))
json.dump(fila,open(FP,"w"),ensure_ascii=False,indent=1)
print("ok",len(fila),fila[-1]["data"])
