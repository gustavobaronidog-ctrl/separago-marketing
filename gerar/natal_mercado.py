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
("natal-ceia-quilo", ["A cliente quer a **ceia inteira num pedido só**: peru, bacalhau, frutas, bebida. 🎄",
 "Por WhatsApp, ela manda a lista em cinco mensagens e você perde item no meio. 💬",
 "Peça vendida por quilo precisa do peso real na hora de separar. ⚖️",
 "No SeparaGo o cliente monta o pedido sozinho e o valor sai pelo peso conferido. ✅",
 "Sua equipe separa tudo de uma vez, sem caderno e sem erro de soma. 📋",
 "Quer vender a ceia pelo celular? **" + CTA + "**"],
 "Ceia de Natal é pedido grande, cheio de item por quilo. Com o pedido montado pelo cliente, nada se perde no WhatsApp.\n\nSalve e organize antes da correria. Teste o SeparaGo grátis, link na bio."),
("natal-vitrine-esgotou", ["Panetone e bebida **esgotaram na semana do Natal** e sua vitrine ainda mostra? 😬",
 "O cliente pede, você responde que acabou, e ele já foi comprar no concorrente. 🏃",
 "Em semana de Natal o estoque muda de hora em hora. 📦",
 "Vitrine atualizada evita pedido de produto que você não tem. ✅",
 "E o cliente confia mais na loja que mostra só o que existe. 🤝",
 "Quer a vitrine sempre certa? **" + CTA + "**"],
 "Na semana do Natal o estoque muda de hora em hora. Vitrine certa evita pedido de produto que acabou.\n\nSalve para a semana das festas. Teste o SeparaGo grátis, link na bio."),
("natal-fila-caixa", ["Dia 23, **fila no caixa até a porta** e o cliente indo embora? 🛒",
 "Quem tem pressa para a ceia não espera 20 minutos para pagar. ⏰",
 "Quem pede pelo celular com antecedência nem entra na fila. 📲",
 "Seu caixa atende só quem quer comprar na hora. 🙌",
 "O resto chega como pedido pronto para separar e retirar ou entregar. 📋",
 "Quer aliviar o caixa do Natal? **" + CTA + "**"],
 "Fila no caixa em véspera de Natal faz cliente desistir. Pedido feito antes pelo celular alivia o balcão.\n\nSalve para a semana de Natal. Teste o SeparaGo grátis, link na bio."),
("natal-entrega-trocada", ["Pedido trocado na entrega de Natal vira **briga no grupo do bairro**. 😤",
 "Duas casas vizinhas, duas sacolas parecidas, uma ceia na casa errada. 🏠",
 "Dica 1: uma sacola por pedido, com nome e número bem visíveis. 🛍️",
 "Dica 2: confira o pedido na saída, item por item, com a lista na tela. ✅",
 "Dica 3: confirme endereço e forma de pagamento antes de a sacola sair. 📍",
 "Quer entrega sem susto no Natal? **" + CTA + "**"],
 "Entrega trocada na véspera de Natal custa caro. Uma sacola por pedido e conferência na saída evitam o erro.\n\nSalve as dicas. Teste o SeparaGo grátis, link na bio."),
("natal-pizzaria-vespera", ["Véspera de Natal na pizzaria: **WhatsApp apitando e ninguém dá conta de anotar**. 🍕",
 "Pedido errado em dia de festa vira pizza refeita e cliente perdido. 😰",
 "Ponha o cardápio num link só e deixe o cliente escolher sabor e borda. 📲",
 "O pedido já chega com endereço, forma de pagamento e observação. 🧾",
 "Você foca em fazer a pizza e o sistema cuida de anotar. 👨‍🍳",
 "Quer atravessar a véspera sem caos? **" + CTA + "**"],
 "Véspera de Natal na pizzaria é o pico do ano. Pedido que chega organizado deixa a cozinha respirar.\n\nSalve para a semana das festas. Teste o SeparaGo grátis, link na bio."),
("natal-pos-festa", ["O Natal passou. **O cliente que comprou a ceia volta?** 🎁",
 "Muita gente compra uma vez nas festas e some. 🫥",
 "Quem fica com o cadastro dele sabe quem pediu e quando. 📒",
 "Uma mensagem no dia certo faz ele lembrar da sua loja. 💬",
 "Cliente do Natal pode virar cliente do ano inteiro. 🔁",
 "Quer guardar quem comprou de você? **" + CTA + "**"],
 "Cliente do Natal pode virar cliente fiel, se você souber quem ele é. Cadastro próprio faz a diferença.\n\nSalve e use em janeiro. Teste o SeparaGo grátis, link na bio."),
]

SLOTS = {1: ("2026-12-02", "12:30"), 2: ("2026-12-17", "12:30"), 3: ("2026-12-19", "12:30"), 4: ("2026-12-20", "12:30"), 5: ("2026-12-22", "18:30"), 6: ("2026-12-26", None)}
REELS = {1: "2026-12-09", 2: "2026-12-14", 3: "2026-12-21", 4: "2026-12-23", 5: "2026-12-24", 6: "2026-12-31"}
FP = R + "/fila/fila.json"
fila = json.load(open(FP, encoding="utf-8")); por_id = {i["id"]: i for i in fila}
pend = lambda: [i for i in fila if i["status"] == "pendente"]
def pasta(i):
    m = re.search(r"midia/([a-z0-9]+)/", (i.get("imagens") or [""])[0]); return m.group(1) if m else None
def estilo(i):
    im = Image.open(f"midia/{pasta(i)}/1.jpg").convert("L").resize((60, 75)); return "B" if ImageStat.Stat(im).mean[0] < 150 else "A"
def achar(data, hora, tipo):
    c = [i for i in pend() if i["data"] == data and i["tipo"] == tipo and (hora is None or i["hora"] == hora) and not i["id"].startswith(("cf", "nm")) and "natal" not in i["id"]]
    if not c and hora is not None:
        c = [i for i in pend() if i["data"] == data and i["tipo"] == tipo and not i["id"].startswith(("cf", "nm")) and "natal" not in i["id"]]
    assert c, (data, hora, tipo); return c[0]
CAR = ["08:30", "12:30", "18:30"]; REE = ["10:30", "15:00", "20:30"]
fim = {"carrossel": [datetime.date.fromisoformat(max(i["data"] for i in pend())), 0], "reel": [datetime.date.fromisoformat(max(i["data"] for i in pend())), 0]}
def para_o_fim(it):
    d = fim[it["tipo"]]; d[1] += 1
    if d[1] > 3: d[0] += datetime.timedelta(days=1); d[1] = 1
    it["data"], it["hora"] = d[0].isoformat(), (CAR if it["tipo"] == "carrossel" else REE)[d[1] - 1]
def trocar(novo, slot):
    novo["data"], novo["hora"] = slot["data"], slot["hora"]; para_o_fim(slot)
os.makedirs(R + "/midia", exist_ok=True)
T = "/tmp/sgm"; os.makedirs(T, exist_ok=True); jobs = []
alvos = {}
for n in range(1, 7):
    d, h = SLOTS[n]
    alvos[n] = achar(d, h, "carrossel") if h else achar(d, "12:30", "carrossel")
for n, (slug, sl, leg) in enumerate(X, 1):
    st = estilo(alvos[n]); bg = ["foto1", "foto2", "foto3", "foto4"][n % 4] if st == "B" else None
    assert not os.path.exists(f"{R}/midia/nm{n:02d}")
    os.makedirs(f"{R}/midia/nm{n:02d}")
    for si, tx in enumerate(sl, 1):
        h = f"{T}/nm{n:02d}_{si}.html"; p = f"{T}/nm{n:02d}_{si}.png"
        open(h, "w").write(page(tx, si, len(sl), bg if si == 1 else None, si == len(sl))); jobs.append((h, p))
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350})
    for h, p in jobs:
        pg.goto("file://" + h); pg.wait_for_timeout(250); pg.screenshot(path=p)
    b.close()
for n, (slug, sl, leg) in enumerate(X, 1):
    for si in range(1, len(sl) + 1): Image.open(f"{T}/nm{n:02d}_{si}.png").convert("RGB").save(f"{R}/midia/nm{n:02d}/{si}.jpg", quality=90)
def reel(n):
    sl = X[n - 1][1]; d = f"{R}/midia/nm{n:02d}"; lst = f"{T}/nm{n:02d}.txt"
    with open(lst, "w") as f:
        for si in range(1, len(sl) + 1): f.write(f"file '{d}/{si}.jpg'\nduration 3.4\n")
        f.write(f"file '{d}/{len(sl)}.jpg'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-vf", "scale=1080:1350,pad=1080:1920:0:285:white,fps=30,format=yuv420p", "-t", f"{len(sl)*3.4:.1f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-shortest", "-movflags", "+faststart", f"{d}/reel.mp4"], check=True)
with ThreadPoolExecutor(3) as ex: list(ex.map(reel, range(1, 7)))
for n, (slug, sl, leg) in enumerate(X, 1):
    nid = f"nm{n:02d}-{slug}"
    c = {"id": nid, "data": "", "hora": "", "tipo": "carrossel", "legenda": leg, "imagens": [f"{BASE}/nm{n:02d}/{s}.jpg" for s in range(1, len(sl) + 1)], "status": "pendente"}
    r = {"id": "r-" + nid, "data": "", "hora": "", "tipo": "reel", "legenda": leg, "video_url": f"{BASE}/nm{n:02d}/reel.mp4", "status": "pendente"}
    trocar(c, alvos[n]); trocar(r, achar(REELS[n], "15:00", "reel")); fila += [c, r]
# realinhar os Natais antigos (datas coerentes) e tirar o que a epoca ja passou
def mover(id_, data, hora):
    it = por_id[id_]; outro = [i for i in pend() if i["data"] == data and i["hora"] == hora and i["tipo"] == it["tipo"] and i["id"] != id_ and not i["id"].startswith(("cf", "nm"))][0]
    outro["data"], outro["hora"], it["data"], it["hora"] = it["data"], it["hora"], data, hora
mover("c51-natal-semana", "2026-12-21", "12:30"); mover("c52-natal-vespera", "2026-12-23", "12:30")
mover("c54-reveillon", "2026-12-28", "12:30")
for i in fila:
    if i["status"] == "pendente" and "black-friday-mercado" in i["id"]:
        i["status"] = "pulado"; i["motivo"] = "Black Friday ja passou (27/11/2026)"
p2 = sorted(pend(), key=lambda i: (i["data"], i["hora"])); fe = [i for i in fila if i["status"] != "pendente"]
json.dump(fe + p2, open(FP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", len(p2), "pendentes ate", p2[-1]["data"])
