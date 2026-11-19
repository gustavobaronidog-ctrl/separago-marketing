import os,json,datetime,subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
R=os.getcwd()
src=open(R+"/gerar/gerar.py").read().split('T="/tmp/sgb"')[0].replace("#FFC53D","#9ADBBB").replace("#FF8A00","#0F7A55")
g={"__name__":"g5","__file__":R+"/gerar/gerar.py"}
os.environ.setdefault("FONTDIR","/usr/share/fonts/opentype/inter")
exec(src,g)
g2={};exec(open(R+"/gerar/conteudo2.py").read(),g2)
g3={};exec(open(R+"/gerar/conteudo3.py").read(),g3)
g["BAG"]='<svg viewBox="0 0 200 200" width="120" height="120"><rect width="200" height="200" rx="46" fill="#F6F5F2"/><path d="M72 80 C72 44 132 44 132 80" stroke="#E5452D" stroke-width="13" stroke-linecap="round" fill="none"/><path d="M52 76 H152 L160 148 Q161 160 149 160 H55 Q43 160 44 148 Z" fill="#0F7A55"/><path d="M84 118 H122 M106 100 L124 118 L106 136" stroke="#fff" stroke-width="11" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M22 112 H38 M16 130 H34" stroke="#0F7A55" stroke-width="8" stroke-linecap="round" opacity=".5"/></svg>'
page=g["page"]; BASE=g["BASE"]
TAGS=["#separago #mercado #supermercado #comerciolocal","#separago #lanchonete #pizzaria #delivery","#separago #varejo #donodemercado #gestao","#separago #mercadinho #empreendedorismo #vendas"]
CTA=["Quer organizar isso? **Teste grátis**. Link na bio. 👇","Quer ver funcionando? **Teste grátis**. Link na bio. 👇","Quer vender mais assim? **Teste grátis**. Link na bio. 👇","Quer testar sem risco? **Teste grátis**. Link na bio. 👇"]
import re
def limpa(s): return re.sub(r"\*\*","",s).strip()
allc={}
for i,(slug,bg,sl,leg,tg) in enumerate(g["C"],1): allc[f"c{i:02d}-{slug}"]=dict(slug=slug,leg=leg+"\n\n"+tg,dir=f"c{i:02d}")
for j,(slug,bg,sl,leg) in enumerate(g2["C2"]): allc[f"c{13+j:02d}-{slug}"]=dict(slug=slug,leg=leg+"\n\n"+TAGS[j%4],dir=f"c{13+j:02d}")
novos=[]
for k,(slug,ls) in enumerate(g3["N3"],1):
    iid=f"n{k:02d}-{slug}"; d=f"n{k:02d}"
    bg=["foto1","foto2","foto3","foto4"][(k//3)%4] if k%3==0 else None
    sl=ls+[CTA[k%4]]
    allc[iid]=dict(slug=slug,leg=limpa(ls[0])+"\n\nSalve e teste o SeparaGo grátis, link na bio.\n\n"+TAGS[k%4],dir=d)
    novos.append((iid,d,bg,sl))
T="/tmp/sgr"; os.makedirs(T,exist_ok=True); jobs=[]
for iid,d,bg,sl in novos:
    os.makedirs(f"{R}/midia/{d}",exist_ok=True)
    if os.path.exists(f"{R}/midia/{d}/reel.mp4"): continue
    for si,tx in enumerate(sl,1):
        h=f"{T}/{d}_{si}.html"; open(h,"w").write(page(tx,si,len(sl),bg if si==1 else None,si==len(sl))); jobs.append((h,f"{T}/{d}_{si}.png",f"{d}{si}",f"{R}/midia/{d}/{si}.jpg"))
def shot(a):
    h,p,n,o=a
    subprocess.run(["google-chrome","--headless=new","--no-sandbox","--disable-gpu","--allow-file-access-from-files","--hide-scrollbars","--window-size=1080,1350","--user-data-dir=/tmp/cr_%s"%n,"--screenshot="+p,"file://"+h],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=180)
    Image.open(p).convert("RGB").save(o,quality=90)
with ThreadPoolExecutor(4) as ex: list(ex.map(shot,jobs))
def reel(d):
    p=f"{R}/midia/{d}"
    if os.path.exists(p+"/reel.mp4"): return
    lst=f"{T}/{d}.txt"
    with open(lst,"w") as f:
        for si in range(1,7): f.write(f"file '{p}/{si}.jpg'\nduration 3.4\n")
        f.write(f"file '{p}/6.jpg'\n")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lst,"-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-vf","scale=1080:1350,pad=1080:1920:0:285:white,fps=30,format=yuv420p","-t","20.4","-c:v","libx264","-preset","veryfast","-crf","23","-c:a","aac","-shortest","-movflags","+faststart",p+"/reel.mp4"],check=True)
with ThreadPoolExecutor(3) as ex: list(ex.map(reel,[d for _,d,_,_ in novos]))
FP=R+"/fila/fila.json"; old=json.load(open(FP))
feitos=[x for x in old if x.get("status")!="pendente"]
ja={x["id"] for x in feitos}
fixos={"black-friday-premium":"2026-11-22","bf-semana":"2026-11-26","bf-sexta":"2026-11-27","cyber":"2026-11-30","quinto-dia":"2026-12-05","salario-13":"2026-12-10","natal-pedidos":"2026-12-15","natal-semana":"2026-12-22","natal-vespera":"2026-12-24","fim-ano":"2026-12-28","reveillon":"2026-12-31","ano-novo":"2027-01-01","meta-ano":"2027-01-02","janeiro":"2027-01-03"}
porslug={v["slug"]:k for k,v in allc.items()}
livres=[k for k in allc if k not in ja and allc[k]["slug"] not in fixos and k[:3] not in ("c01","c02")]
antigos=[k for k in livres if k[0]=="c"]; nn=[k for k in livres if k[0]=="n"]
mix=[]
while antigos or nn:
    if antigos: mix.append(antigos.pop(0))
    for _ in range(2):
        if nn: mix.append(nn.pop(0))
d0=datetime.date(2026,11,19); fim=datetime.date(2027,1,3)
CAR=["08:30","12:30","18:30"]; REE=["10:30","15:00","20:30"]
fila=list(feitos); dia=d0
while dia<=fim:
    ds=dia.isoformat(); hoje=[porslug[s] for s,dt in fixos.items() if dt==ds and porslug[s] not in ja]
    while len(hoje)<3 and mix: hoje.append(mix.pop(0))
    for n,iid in enumerate(hoje[:3]):
        c=allc[iid]
        fila.append({"id":iid,"data":ds,"hora":CAR[n],"tipo":"carrossel","legenda":c["leg"],"imagens":[f"{BASE}/{c['dir']}/{s}.jpg" for s in range(1,7)],"status":"pendente"})
        fila.append({"id":"r-"+iid,"data":ds,"hora":REE[n],"tipo":"reel","legenda":c["leg"],"video_url":f"{BASE}/{c['dir']}/reel.mp4","status":"pendente"})
    dia+=datetime.timedelta(days=1)
json.dump(fila,open(FP,"w"),ensure_ascii=False,indent=1)
pend=[x for x in fila if x["status"]=="pendente"]
print("ok pendentes",len(pend),"ultimo",pend[-1]["data"],"sobra",len(mix))
