#!/usr/bin/env python3
"""Reorganiza os Reels de carrossel PENDENTES (sem mexer nos carrosseis):
- o Reel de um carrossel nunca sai a menos de 7 dias do proprio carrossel (para o feed nao parecer
  dois posts iguais);
- o estilo do Reel do dia e o OPOSTO ao dos carrosseis do dia, quando houver (foto de fundo x branco);
- horarios dos Reels: 10:30, 15:00, 20:30.
Depois insere/atualiza os videos dinamicos (fila: tipo 'video'), um por dia ate acabarem."""
import json, re, datetime, os
from PIL import Image, ImageStat

FILA = "fila/fila.json"
REE = ["10:30", "15:00", "20:30"]
GAP = 7
fila = json.load(open(FILA, encoding="utf-8"))
por_id = {i["id"]: i for i in fila}
D = lambda s: datetime.date.fromisoformat(s)

def estilo(i):
    d = re.search(r"midia/([a-z0-9]+)/", i["imagens"][0]).group(1)
    return "B" if ImageStat.Stat(Image.open(f"midia/{d}/1.jpg").convert("L").resize((60, 75))).mean[0] < 150 else "A"

car_pend = [i for i in fila if i["tipo"] == "carrossel" and i["status"] == "pendente"]
reel_de = {i["id"][2:] for i in fila if i["tipo"] == "reel" and i["status"] == "pendente"}
com_reel = [i for i in fila if i["tipo"] == "carrossel" and (i["status"] == "pendente" or i["id"] in reel_de)]
est = {i["id"]: estilo(i) for i in com_reel}
dia_car = {i["id"]: D((i.get("postado_em") or i["data"])[:10]) for i in com_reel}
estilo_dia = {}
for i in car_pend: estilo_dia.setdefault(i["data"], est[i["id"]])

reels = [i for i in fila if i["tipo"] == "reel" and i["status"] == "pendente"]
pool = {"A": [], "B": []}
for r in sorted(reels, key=lambda r: (r["data"], r["hora"])):
    cid = r["id"][2:]
    if cid in est: pool[est[cid]].append(r)
dias = sorted(estilo_dia)
for dia in dias:
    d = D(dia)
    pref = "A" if estilo_dia[dia] == "B" else "B"
    for k in range(3):
        escolhido = None
        for estl in (pref, "A" if pref == "B" else "B"):
            ok = [r for r in pool[estl] if abs((dia_car[r["id"][2:]] - d).days) >= GAP]
            passado = sorted([r for r in ok if (dia_car[r["id"][2:]] - d).days <= -GAP], key=lambda r: -(dia_car[r["id"][2:]] - d).days)
            futuro = sorted([r for r in ok if (dia_car[r["id"][2:]] - d).days >= GAP], key=lambda r: (dia_car[r["id"][2:]] - d).days)
            esc = (passado or futuro or [None])[0]
            if esc: escolhido = (estl, esc); break
        if not escolhido:  # sem opcao com 7 dias: pega a mais distante possivel
            tudo = [(e, r) for e in "AB" for r in pool[e]]
            if not tudo: break
            escolhido = max(tudo, key=lambda x: abs((dia_car[x[1]["id"][2:]] - d).days))
        estl, r = escolhido; pool[estl].remove(r)
        r["data"], r["hora"] = dia, REE[k]
# sobras de reels (mais reels que dias) ficam no fim, em dias extras
extra = D(dias[-1]) + datetime.timedelta(days=1)
sobra = pool["A"] + pool["B"]
for n, r in enumerate(sobra):
    r["data"], r["hora"] = (extra + datetime.timedelta(days=n // 3)).isoformat(), REE[n % 3]

# ---- ajuste fino: troca de lugar os Reels que ficaram a menos de GAP dias do carrossel ----
def gap(r, dia): return abs((dia_car[r["id"][2:]] - D(dia)).days)
todos = [r for r in reels if r["id"][2:] in dia_car]
for _ in range(3):
    for r in sorted(todos, key=lambda x: x["data"], reverse=True):
        if gap(r, r["data"]) >= GAP: continue
        for r2 in todos:
            if r2 is r: continue
            if gap(r, r2["data"]) >= GAP and gap(r2, r["data"]) >= GAP:
                r["data"], r2["data"] = r2["data"], r["data"]
                r["hora"], r2["hora"] = r2["hora"], r["hora"]
                break

# ---- videos dinamicos ----
BASE = "https://raw.githubusercontent.com/gustavobaronidog-ctrl/separago-marketing/main/midia/dinamicos/"
import sys; sys.path.insert(0, "gerar")
import videos_dinamicos as V
inicio = datetime.date.today()
for n, vid in enumerate(V.VIDEOS):
    item = por_id.get(vid)
    novo = dict(id=vid, data=(inicio + datetime.timedelta(days=n)).isoformat(), hora="14:00", tipo="video",
                legenda=V.VIDEOS[vid]["legenda"], video_url=BASE + vid + ".mp4", status="pendente")
    if item and item["status"] != "pendente": continue
    if item: item.update(novo)
    else: fila.append(novo); por_id[vid] = novo
pend = sorted([i for i in fila if i["status"] == "pendente"], key=lambda i: (i["data"], i["hora"]))
feitos = [i for i in fila if i["status"] != "pendente"]
json.dump(feitos + pend, open(FILA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- conferencia ----
rs = [i for i in pend if i["tipo"] == "reel"]
menor = min(abs((dia_car[r["id"][2:]] - D(r["data"])).days) for r in rs)
print("reels:", len(rs), "distancia minima ate o proprio carrossel (dias):", menor)
igual = sum(1 for dia in dias for r in rs if r["data"] == dia and est[r["id"][2:]] == estilo_dia[dia])
print("reels com o MESMO estilo dos carrosseis do dia:", igual, "de", len(rs))
dd = {}
for i in pend: dd.setdefault(i["data"], []).append(i["hora"] + i["tipo"][0])
for k in list(dd)[:5]: print(k, sorted(dd[k]))
