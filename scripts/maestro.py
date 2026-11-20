#!/usr/bin/env python3
"""MAESTRO do SeparaGo. Roda a cada ~10 min no GitHub Actions.

Compara o que JA DEVIA ter ido ao ar hoje (pelos horarios da fila) com o que realmente
esta no Instagram (conta os posts de hoje pela API) e publica o que faltar:
no maximo 1 carrossel e 1 Reel por rodada. Se o GitHub atrasar ou pular rodadas,
a proxima corrige sozinha. Nao publica depois das 22h.
Em caso de duvida (API nao respondeu), NAO publica: melhor atrasar do que duplicar."""
import os, sys, time, subprocess
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import postar as P

BRT = timezone(timedelta(hours=-3))
LIMITE_MIN = 22 * 60
MAX_TENTATIVAS = 5


CI = os.environ.get("GITHUB_ACTIONS") == "true"


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True)


def puxar():
    """Pega a fila mais nova do repositorio (alguem pode ter mexido nela)."""
    if CI:
        git("pull", "--rebase", "--autostash", "-q")


def empurrar():
    """Grava o estado no GitHub NA HORA, para um post nunca se repetir se o job cair depois."""
    if not CI:
        return
    git("config", "user.name", "robo-separago"); git("config", "user.email", "robo@users.noreply.github.com")
    git("add", "fila/")
    if git("diff", "--cached", "--quiet").returncode == 0:
        return
    git("commit", "-q", "-m", "maestro: atualiza fila")
    for _ in range(4):
        git("pull", "--rebase", "--autostash", "-q")
        if git("push", "-q").returncode == 0:
            return
        time.sleep(5)


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
    # a API conta todo Reel junto: separa os videos dinamicos (tipo "video") dos Reels de carrossel
    videos_hoje = sum(1 for i in fila if i["tipo"] == "video" and i.get("status") == "postado"
                      and (i.get("postado_em") or "")[:10] == hoje)
    ja = {"carrossel": ja["carrossel"], "reel": max(0, ja["reel"] - videos_hoje), "video": videos_hoje}
    print(f"{hoje} {agora:%H:%M} (Brasilia) - ja no ar hoje: {ja}", flush=True)

    mudou = False
    for tipo in ("carrossel", "video", "reel"):
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
        empurrar()
        if estado.get("pausa_ate"):
            break
        time.sleep(20)
    print("Maestro ok." if mudou else "Maestro: nada atrasado.", flush=True)
    return 0


def laco(minutos, passo=300):
    """Fica de plantao por `minutos`: confere a cada `passo` segundos e publica o que atrasou.
    Assim um agendamento (cron) que o GitHub pule ou atrase nao deixa nenhum post de fora.
    Ao fim, o proprio Maestro dispara a proxima rodada (cadeia sem depender do cron)."""
    fim = time.time() + minutos * 60
    while True:
        puxar()
        try:
            main()
        except Exception as e:
            print("Erro na conferencia (segue no proximo ciclo):", str(e).replace(P.TOKEN, "***")[:200], file=sys.stderr)
        if time.time() + passo >= fim:
            break
        time.sleep(passo)
    h = agora_brt()
    if CI and 7 <= h.hour < 22:
        r = subprocess.run(["gh", "workflow", "run", "maestro.yml", "--ref", "main", "-f", "minutos=50"],
                           capture_output=True, text=True)
        print("Proxima rodada disparada." if r.returncode == 0 else f"Nao consegui disparar a proxima rodada (o agendamento cobre): {r.stderr[:200]}")
    return 0


if __name__ == "__main__":
    minutos = float(os.environ.get("MAESTRO_MINUTOS", "0") or 0)
    sys.exit(laco(minutos) if minutos > 0 else main())
