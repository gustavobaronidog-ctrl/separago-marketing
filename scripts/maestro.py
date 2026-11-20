#!/usr/bin/env python3
"""MAESTRO do SeparaGo. Roda a cada ~10 min no GitHub Actions.

Compara o que JA DEVIA ter ido ao ar hoje (pelos horarios da fila) com o que realmente
esta no Instagram (conta os posts de hoje pela API) e publica o que faltar:
no maximo 1 carrossel e 1 Reel por rodada. Se o GitHub atrasar ou pular rodadas,
a proxima corrige sozinha. Nao publica depois das 22h.
Em caso de duvida (API nao respondeu), NAO publica: melhor atrasar do que duplicar."""
import os, sys, time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import postar as P

BRT = timezone(timedelta(hours=-3))
LIMITE_MIN = 22 * 60
MAX_TENTATIVAS = 5


def agora_brt():
    return datetime.now(BRT)


def posts_reais_de_hoje(hoje):
    """Conta no Instagram os posts de hoje (carrossel, reel). Levanta erro se a API falhar."""
    r = P.chamar("GET", f"{P.IG_ID}/media",
                 {"fields": "timestamp,media_type,media_product_type", "limit": "50"})
    car = reel = 0
    for m in r.get("data", []):
        t = datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z").astimezone(BRT)
        if t.strftime("%Y-%m-%d") != hoje:
            continue
        if m.get("media_product_type") == "REELS":
            reel += 1
        elif m.get("media_type") == "CAROUSEL_ALBUM":
            car += 1
    return {"carrossel": car, "reel": reel}


def main():
    fila = P.ler(P.FILA, [])
    estado = P.ler(P.ESTADO, {})
    agora = agora_brt()
    hoje, minutos = agora.strftime("%Y-%m-%d"), agora.hour * 60 + agora.minute
    if minutos > LIMITE_MIN:
        print("Depois das 22h: nada a fazer."); return 0
    if estado.get("pausa_ate") and agora < datetime.fromisoformat(estado["pausa_ate"]):
        print("Em pausa por bloqueio do Instagram ate", estado["pausa_ate"]); return 0

    try:
        ja = posts_reais_de_hoje(hoje)
    except Exception as e:
        print("Nao consegui contar os posts de hoje no Instagram; nao publico nada nesta rodada:",
              str(e).replace(P.TOKEN, "***")[:200], file=sys.stderr)
        return 0
    print(f"{hoje} {agora:%H:%M} (Brasilia) - ja no ar hoje: {ja}", flush=True)

    mudou = False
    for tipo in ("carrossel", "reel"):
        devidos = sum(1 for i in fila if i["tipo"] == tipo and i["data"] == hoje
                      and i.get("hora", "00:00") <= f"{agora:%H:%M}")
        falta = devidos - ja[tipo]
        if falta <= 0:
            continue
        pend = sorted((i for i in fila if i["tipo"] == tipo and i.get("status") == "pendente"),
                      key=lambda i: (i["data"], i.get("hora", "00:00")))
        if not pend:
            print(f"DEVIDO e sem estoque: {tipo}", file=sys.stderr); continue
        alvo = pend[0]
        print(f"DEVIDO e nao publicado: {tipo} (faltam {falta}). Publicando {alvo['id']}.", flush=True)
        try:
            alvo["post_id"] = P.postar(alvo)
            alvo["status"] = "postado"
            alvo["postado_em"] = datetime.now(BRT).isoformat()
            alvo.pop("ultimo_erro", None)
            print("Postado:", alvo["id"], flush=True)
        except Exception as e:
            msg = str(e).replace(P.TOKEN, "***")[:300]
            alvo["ultimo_erro"] = msg
            alvo["tentativas"] = alvo.get("tentativas", 0) + 1
            if "2207051" in msg or "request limit" in msg.lower() or '"code":4' in msg:
                estado["pausa_ate"] = (agora + timedelta(hours=6)).isoformat()
                print("Instagram limitou. Pausa de 6 h.", file=sys.stderr)
            elif alvo["tentativas"] >= MAX_TENTATIVAS:
                alvo["status"] = "falhou"
            print("Falhou:", alvo["id"], msg, file=sys.stderr)
        mudou = True
        P.salvar(P.FILA, fila)       # grava ja, para nao perder o estado se algo cair depois
        P.salvar(P.ESTADO, estado)
        if estado.get("pausa_ate"):
            break
        time.sleep(20)
    print("Maestro ok." if mudou else "Maestro: nada atrasado.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
