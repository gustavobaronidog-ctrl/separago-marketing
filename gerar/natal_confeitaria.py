#!/usr/bin/env python3
"""Natal da confeitaria (SeparaGo Encomendas): 6 carrosseis + 6 reels de carrossel.
Troca de lugar com carrosseis genericos pendentes de dezembro (os deslocados vao para o fim da fila).
Nao mexe em item ja postado nem no codigo do robo. Uso: python3 gerar/natal_confeitaria.py"""
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
CTA = "Teste grátis. Link na bio. 👇"
X = [
("natal-whatsapp", ["Dezembro chegou e suas encomendas de Natal estão **perdidas no WhatsApp**? 🎄",
 "Panetone, chocotone, caixa de brigadeiro: cada cliente pede de um jeito e em um horário. 💬",
 "Aí anota errado, esquece o sabor e entrega no dia errado. 😰",
 "Num link só, a cliente escolhe o produto, a quantidade e o dia da retirada. ✅",
 "A encomenda chega organizada, sem você digitar nada. 📋",
 "Quer o Natal sem correria? **" + CTA + "**"],
 "Encomenda de Natal no WhatsApp vira bagunça rápido. Num link só, o pedido chega organizado.\n\nSalve para dezembro. Teste o SeparaGo grátis, link na bio.\n\n#confeitaria"),
("natal-limite-dia", ["Aceitou **encomenda demais** e o forno não dá conta? 🔥",
 "No Natal, a confeiteira diz sim para todo mundo. 😅",
 "Aí 23 e 24 de dezembro viram um dia impossível. 📅",
 "Defina um **limite de encomendas por dia**: quando lota, aquele dia fecha. 🔒",
 "Você produz com calma e entrega no horário combinado. 🎁",
 "Quer controlar a produção? **" + CTA + "**"],
 "Quem aceita mais do que consegue produzir perde a cliente e a noite de sono. Limite por dia resolve.\n\nSalve para a semana do Natal. Teste o SeparaGo grátis, link na bio.\n\n#confeitaria"),
("natal-sinal-pix", ["A cliente **encomendou e sumiu**. O bolo ficou pronto e ninguém retirou. 😞",
 "Sem sinal, encomenda é só uma promessa. 🤝",
 "Combine o sinal no Pix já na hora do pedido. 💸",
 "Assim a encomenda vira reserva de verdade. ✅",
 "Você compra os ingredientes sem medo de ficar no prejuízo. 🛒",
 "Quer encomenda que se confirma? **" + CTA + "**"],
 "Encomenda sem sinal é risco. Combinar o Pix na hora do pedido protege o seu bolso.\n\nSalve e confira o seu processo. Teste o SeparaGo grátis, link na bio.\n\n#confeitaria"),
("natal-5-erros", ["5 erros que **fazem a cliente não encomendar de novo** no Natal. 🎄",
 "1. Mandar o orçamento só horas depois. ⏰",
 "2. Não combinar dia e horário da retirada. 📍",
 "3. Esquecer sabor, recheio ou o recado no bolo. 📝",
 "4. Aceitar mais pedidos do que dá conta. 🔥",
 "5. Deixar a cliente sem saber se o pedido foi confirmado. ❓",
 "Quer evitar os 5? **" + CTA + "**"],
 "Os cinco erros que mais custam encomendas de fim de ano.\n\nSalve a lista. Teste o SeparaGo grátis, link na bio.\n\n#confeitaria"),
("natal-producao-dia", ["Na semana do Natal, **o que você precisa produzir amanhã**? 🤔",
 "Sem lista, você confere caderno, áudio e mensagem. 📒",
 "Com uma tela de produção, você vê o que precisa ficar pronto em cada dia. 📋",
 "Menos conferência, menos esquecimento, mais tempo na cozinha. 👩‍🍳",
 "Você começa o dia sabendo exatamente o que fazer. ✅",
 "Quer a produção na mão? **" + CTA + "**"],
 "Na correria de dezembro, saber o que produzir em cada dia evita esquecimento e atraso.\n\nSalve para consultar depois. Teste o SeparaGo grátis, link na bio.\n\n#confeitaria"),
("natal-cardapio-link", ["Você vende **só no boca a boca** e deixa dezembro passar? 📉",
 "Natal e Páscoa são as épocas em que mais gente encomenda doce. 🎉",
 "Cardápio em link, com foto e preço, deixa a cliente encomendar pelo celular. 📲",
 "O SeparaGo tem modelos prontos de Natal e Páscoa para você começar. 🎁",
 "Monte antes da correria. Dezembro chega rápido. ⏳",
 "Quer sua loja de encomendas? **" + CTA + "**"],
 "Natal e Páscoa são épocas fortes para quem faz doces. Cardápio em link ajuda a vender sem ficar o dia no WhatsApp.\n\nSalve e comece antes. Teste o SeparaGo grátis, link na bio.\n\n#confeitaria"),
]
DIAS = ["2026-12-01", "2026-12-04", "2026-12-07", "2026-12-11", "2026-12-14", "2026-12-18"]
FP = R + "/fila/fila.json"
fila = json.load(open(FP, encoding="utf-8")); por_id = {i["id"]: i for i in fila}

def pasta(i):
    m = re.search(r"midia/([a-z0-9]+)/", (i.get("imagens") or [""])[0]); return m.group(1) if m else None
def estilo(i):
    im = Image.open(f"midia/{pasta(i)}/1.jpg").convert("L").resize((60, 75))
    return "B" if ImageStat.Stat(im).mean[0] < 150 else "A"

slots = []
for d in DIAS:
    c = [i for i in fila if i["tipo"] == "carrossel" and i["status"] == "pendente" and i["data"] == d and i["hora"] == "12:30" and "natal" not in i["id"]]
    assert c, d
    slots.append(c[0])
T = "/tmp/sgn"; os.makedirs(T, exist_ok=True); jobs = []
FOTOS = ["foto1", "foto2", "foto3", "foto4"]
for n, (slug, sl, leg) in enumerate(X, 1):
    st = estilo(slots[n - 1]); bg = FOTOS[n % 4] if st == "B" else None
    out = f"{R}/midia/cf{n:02d}"; os.makedirs(out, exist_ok=True)
    for si, tx in enumerate(sl, 1):
        h = f"{T}/cf{n:02d}_{si}.html"; p = f"{T}/cf{n:02d}_{si}.png"
        open(h, "w").write(page(tx, si, len(sl), bg if si == 1 else None, si == len(sl))); jobs.append((h, p))
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350})
    for h, p in jobs:
        pg.goto("file://" + h); pg.wait_for_timeout(250); pg.screenshot(path=p)
    b.close()
for n, (slug, sl, leg) in enumerate(X, 1):
    for si in range(1, len(sl) + 1):
        Image.open(f"{T}/cf{n:02d}_{si}.png").convert("RGB").save(f"{R}/midia/cf{n:02d}/{si}.jpg", quality=90)
def reel(n):
    sl = X[n - 1][1]; d = f"{R}/midia/cf{n:02d}"; lst = f"{T}/cf{n:02d}.txt"
    with open(lst, "w") as f:
        for si in range(1, len(sl) + 1): f.write(f"file '{d}/{si}.jpg'\nduration 3.4\n")
        f.write(f"file '{d}/{len(sl)}.jpg'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-vf", "scale=1080:1350,pad=1080:1920:0:285:white,fps=30,format=yuv420p", "-t", f"{len(sl)*3.4:.1f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-shortest", "-movflags", "+faststart", f"{d}/reel.mp4"], check=True)
with ThreadPoolExecutor(3) as ex: list(ex.map(reel, range(1, len(X) + 1)))
# troca de lugar na fila
ult = max(i["data"] for i in fila if i["status"] == "pendente"); dfim = datetime.date.fromisoformat(ult)
CAR = ["08:30", "12:30", "18:30"]; REE = ["10:30", "15:00", "20:30"]
for n, (slug, sl, leg) in enumerate(X, 1):
    old = slots[n - 1]; oldr = por_id.get("r-" + old["id"])
    nid = f"cf{n:02d}-{slug}"
    novo = {"id": nid, "data": old["data"], "hora": old["hora"], "tipo": "carrossel", "legenda": leg, "imagens": [f"{BASE}/cf{n:02d}/{s}.jpg" for s in range(1, len(sl) + 1)], "status": "pendente"}
    novor = {"id": "r-" + nid, "data": oldr["data"] if oldr else old["data"], "hora": oldr["hora"] if oldr else "15:00", "tipo": "reel", "legenda": leg, "video_url": f"{BASE}/cf{n:02d}/reel.mp4", "status": "pendente"}
    dfim += datetime.timedelta(days=1)
    old["data"], old["hora"] = dfim.isoformat(), "12:30"
    if oldr: oldr["data"], oldr["hora"] = dfim.isoformat(), "15:00"
    fila += [novo, novor]
pend = sorted([i for i in fila if i["status"] == "pendente"], key=lambda i: (i["data"], i["hora"]))
feitos = [i for i in fila if i["status"] != "pendente"]
json.dump(feitos + pend, open(FP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", len(pend), "pendentes ate", pend[-1]["data"])
