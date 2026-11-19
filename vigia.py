#!/usr/bin/env python3
"""Vigia do robo do Instagram do SeparaGo. Roda no GitHub Actions, sem depender do Claude.
Se algo estiver errado o job FALHA e o GitHub manda e-mail ao dono do repositorio."""
import json, sys, urllib.request, datetime

problemas, avisos = [], []
agora = datetime.datetime.utcnow() - datetime.timedelta(hours=3)  # Brasilia
hoje = agora.date()

fila = json.load(open("fila/fila.json", encoding="utf-8"))
try:
    estado = json.load(open("fila/estado.json", encoding="utf-8"))
except Exception:
    estado = {}

pausa = str(estado.get("pausa_ate") or "")
pausado = False
if pausa:
    try:
        fim = datetime.datetime.fromisoformat(pausa.replace("Z", "+00:00"))
        pausado = fim.replace(tzinfo=None) > datetime.datetime.utcnow() if fim.tzinfo is None else fim > datetime.datetime.now(datetime.timezone.utc)
    except Exception:
        pausado = False
if pausado:
    avisos.append(f"robo em pausa ate {pausa} (Instagram bloqueou ou limitou)")

def quando(it):
    return datetime.datetime.strptime(it["data"] + " " + it["hora"], "%Y-%m-%d %H:%M")

pend = [i for i in fila if i.get("status") == "pendente"]
falhou = [i for i in fila if i.get("status") == "falhou"]
print(f"fila: {len(fila)} itens, {len(pend)} pendentes, {len(falhou)} com falha")

for i in falhou[:5]:
    problemas.append(f"item {i.get('id')} falhou: {i.get('ultimo_erro', 'sem detalhe')}")

atrasados = [i for i in pend if quando(i) + datetime.timedelta(minutes=90) < agora]
if atrasados and not pausado:
    ids = ", ".join(str(i.get("id")) for i in atrasados[:6])
    problemas.append(f"{len(atrasados)} post(s) atrasado(s) ha mais de 90 min: {ids}. Rode o botao Postar em Actions")

if pend:
    ultimo = max(datetime.date.fromisoformat(i["data"]) for i in pend)
    dias = (ultimo - hoje).days
    print(f"estoque ate {ultimo} ({dias} dias)")
    if dias < 2:
        problemas.append(f"estoque do SeparaGo acaba em {dias} dia(s). Precisa criar mais conteudo")
    elif dias < 7:
        avisos.append(f"estoque do SeparaGo baixo: {dias} dias")
else:
    problemas.append("fila do SeparaGo acabou, nada sera postado")

def existe(url):
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "vigia-github"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status < 400
    except Exception:
        return False

for it in pend[:8]:
    arqs = it.get("imagens") or []
    if isinstance(arqs, str):
        arqs = [arqs]
    for u in arqs:
        if isinstance(u, str) and u.startswith("http") and not existe(u):
            problemas.append(f"arquivo nao abre (item {it.get('id')}): {u}")

for url in ["https://separago.vercel.app/separago"]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "vigia-github"})
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"site {url}: HTTP {r.status}")
            if r.status >= 400:
                problemas.append(f"site fora do ar: {url} HTTP {r.status}")
    except Exception as e:
        problemas.append(f"site fora do ar: {url} ({e})")

for a in avisos:
    print(f"::warning::{a}")
if problemas:
    for p in problemas:
        print(f"::error::{p}")
    sys.exit(1)
print("Tudo certo.")
