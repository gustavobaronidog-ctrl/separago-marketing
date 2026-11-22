#!/usr/bin/env python3
"""Lote SeparaGo janeiro a marco: carrosseis + reels de carrossel, por DATA (depois do ultimo item da fila).
Datas sazonais fixas; genericos em sequencia (3 por dia por tipo).
Nao mexe em item ja postado nem no codigo do robo. Uso: python3 gerar/lote_separago.py"""
import os, json, re, datetime, subprocess
from PIL import Image, ImageStat
from concurrent.futures import ThreadPoolExecutor
R = os.getcwd()
src = open(R + "/gerar/gerar.py").read().split('T="/tmp/sgb"')[0].replace("#FFC53D", "#9ADBBB").replace("#FF8A00", "#0F7A55")
g = {"__name__": "gn", "__file__": R + "/gerar/gerar.py"}
os.environ.setdefault("FONTDIR", "/usr/share/fonts/opentype/inter")
exec(src, g)
g["BAG"] = '<svg viewBox="0 0 200 200" width="120" height="120"><rect width="200" height="200" rx="46" fill="#F6F5F2"/><path d="M72 80 C72 44 132 44 132 80" stroke="#E5452D" stroke-width="13" stroke-linecap="round" fill="none"/><path d="M52 76 H152 L160 148 Q161 160 149 160 H55 Q43 160 44 148 Z" fill="#0F7A55"/><path d="M84 118 H122 M106 100 L124 118 L106 136" stroke="#fff" stroke-width="11" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M22 112 H38 M16 130 H34" stroke="#0F7A55" stroke-width="8" stroke-linecap="round" opacity=".5"/></svg>'
page = g["page"]; BASE = g["BASE"]

sys_path = os.path.dirname(os.path.abspath(__file__)); import sys; sys.path.insert(0, sys_path)
from conteudo_lote_sg import X
FP = R + "/fila/fila.json"; fila = json.load(open(FP, encoding="utf-8"))
CAR = ["08:30", "12:30", "18:30"]; REE = ["10:30", "15:00", "20:30"]
ocu = {(i["data"], i["hora"], i["tipo"]) for i in fila if i["status"] == "pendente"}
ids = {i["id"] for i in fila}
fim = datetime.date.fromisoformat(max(i["data"] for i in fila if i["status"] == "pendente")) + datetime.timedelta(days=1)
def livre(data, tipo, pref=None):
    slots = CAR if tipo == "carrossel" else REE
    for h in ([pref] if pref else []) + slots:
        if h and (data, h, tipo) not in ocu: ocu.add((data, h, tipo)); return h
    raise SystemExit("sem slot " + data)
T = "/tmp/sgl"; os.makedirs(T, exist_ok=True); jobs = []; plano = []
cur = fim; uso = {}
for n, (slug, data, sl, leg, tag) in enumerate(X, 1):
    assert len(sl) == 6 and not os.path.exists(f"{R}/midia/lt{n:02d}")
    if data is None:
        while uso.get(cur.isoformat(), 0) >= 3: cur += datetime.timedelta(days=1)
        data = cur.isoformat(); uso[data] = uso.get(data, 0) + 1
    plano.append((n, slug, data, sl, leg, tag))
os.makedirs(R + "/midia", exist_ok=True)
for n, slug, data, sl, leg, tag in plano:
    os.makedirs(f"{R}/midia/lt{n:02d}")
    bg = ["foto1", "foto2", "foto3", "foto4"][n % 4] if n % 2 == 0 else None
    for si, tx in enumerate(sl, 1):
        h = f"{T}/lt{n:02d}_{si}.html"; open(h, "w").write(page(tx, si, len(sl), bg if si == 1 else None, si == len(sl))); jobs.append((h, f"{T}/lt{n:02d}_{si}.png", n, si))
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350})
    for h, p, n, si in jobs:
        pg.goto("file://" + h); pg.wait_for_timeout(250); pg.screenshot(path=p)
    b.close()
for h, p, n, si in jobs: Image.open(p).convert("RGB").save(f"{R}/midia/lt{n:02d}/{si}.jpg", quality=90)
def reel(n):
    d = f"{R}/midia/lt{n:02d}"; lst = f"{T}/lt{n:02d}.txt"
    with open(lst, "w") as f:
        for si in range(1, 7): f.write(f"file '{d}/{si}.jpg'\nduration 3.4\n")
        f.write(f"file '{d}/6.jpg'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-vf", "scale=1080:1350,pad=1080:1920:0:285:white,fps=30,format=yuv420p", "-t", f"{6*3.4:.1f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-shortest", "-movflags", "+faststart", f"{d}/reel.mp4"], check=True)
with ThreadPoolExecutor(3) as ex: list(ex.map(reel, [p[0] for p in plano]))
for n, slug, data, sl, leg, tag in plano:
    nid = f"lt{n:02d}-{slug}"; assert nid not in ids
    L2 = leg + "\n\n" + tag
    c = {"id": nid, "data": data, "hora": livre(data, "carrossel", "12:30" if n <= 10 else None), "tipo": "carrossel", "legenda": L2, "imagens": [f"{BASE}/lt{n:02d}/{s}.jpg" for s in range(1, 7)], "status": "pendente"}
    r = {"id": "r-" + nid, "data": data, "hora": livre(data, "reel", "15:00" if n <= 10 else None), "tipo": "reel", "legenda": L2, "video_url": f"{BASE}/lt{n:02d}/reel.mp4", "status": "pendente"}
    fila += [c, r]
fe = [i for i in fila if i["status"] != "pendente"]; pe = sorted([i for i in fila if i["status"] == "pendente"], key=lambda i: (i["data"], i["hora"]))
json.dump(fe + pe, open(FP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", len(pe), "pendentes ate", pe[-1]["data"])
