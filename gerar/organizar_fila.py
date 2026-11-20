#!/usr/bin/env python3
"""Reorganiza os itens PENDENTES da fila para o feed ficar em blocos:
cada dia = 3 carrosseis + os 3 Reels desses mesmos carrosseis, todos do MESMO estilo.
Estilo B = 1o slide com foto de fundo escurecida; estilo A = 1o slide branco.
Os dias alternam B, A, B, A... (6 posts seguidos = 2 fileiras do feed no mesmo estilo).
Nao mexe em item ja postado. Uso: python3 gerar/organizar_fila.py [AAAA-MM-DD inicio] [AAAA-MM-DD fim]"""
import json, re, sys, datetime, collections
from PIL import Image, ImageStat

FILA = "fila/fila.json"
INICIO = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
FIM = datetime.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else datetime.date(2027, 1, 3)
CAR = ["08:30", "12:30", "18:30"]
REE = ["10:30", "15:00", "20:30"]

fila = json.load(open(FILA, encoding="utf-8"))
por_id = {i["id"]: i for i in fila}

def pasta(i):
    m = re.search(r"midia/([a-z0-9]+)/", (i.get("imagens") or [""])[0])
    return m.group(1) if m else None

def estilo(i):
    im = Image.open(f"midia/{pasta(i)}/1.jpg").convert("L").resize((60, 75))
    return "B" if ImageStat.Stat(im).mean[0] < 150 else "A"

for i in fila:  # carrossel que falhou so uma vez volta para a fila
    if i["tipo"] == "carrossel" and i.get("status") == "falhou":
        i["status"] = "pendente"; i["tentativas"] = 0; i.pop("ultimo_erro", None)

car = [i for i in fila if i["tipo"] == "carrossel" and i["status"] == "pendente"]
est = {i["id"]: estilo(i) for i in car}
ordem = {i["id"]: n for n, i in enumerate(fila)}
pool = {"A": [], "B": []}
for i in sorted(car, key=lambda x: (x["data"], x["hora"], ordem[x["id"]])):
    pool[est[i["id"]]].append(i)

# reels de carrosseis que ja foram postados (sem par pendente) saem da fila
for i in fila:
    if i["tipo"] == "reel" and i["status"] == "pendente" and i["id"][2:] not in est:
        i["status"] = "pulado"; i["motivo"] = "carrossel dele ja foi postado"

dias, d = [], INICIO
while d <= FIM:
    dias.append(d); d += datetime.timedelta(days=1)
plano, seq = [], ["B", "A"]
for n in range(len(dias)):
    s = seq[n % 2]
    if len(pool[s]) < 3:
        s = "A" if s == "B" else "B"
    plano.append(s)
dia_extra = FIM
for n, dia in enumerate(dias + [FIM + datetime.timedelta(days=k) for k in range(1, 6)]):
    s = plano[n] if n < len(plano) else ("A" if len(pool["A"]) >= len(pool["B"]) else "B")
    if not pool["A"] and not pool["B"]:
        break
    if len(pool[s]) == 0:
        s = "A" if s == "B" else "B"
    tres = [pool[s].pop(0) for _ in range(min(3, len(pool[s])))]
    for k, c in enumerate(tres):
        c["data"], c["hora"] = dia.isoformat(), CAR[k]
        r = por_id.get("r-" + c["id"])
        if r and r["status"] == "pendente":
            r["data"], r["hora"] = dia.isoformat(), REE[k]

pend = [i for i in fila if i["status"] == "pendente"]
feitos = [i for i in fila if i["status"] != "pendente"]
pend.sort(key=lambda i: (i["data"], i["hora"]))
json.dump(feitos + pend, open(FILA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("pendentes:", len(pend), "ate", pend[-1]["data"])
dd = collections.defaultdict(list)
for i in pend:
    dd[i["data"]].append((i["hora"], i["tipo"][0], est.get(i["id"].replace("r-", ""), "?")))
for k in list(dd)[:8]:
    print(k, dd[k])
