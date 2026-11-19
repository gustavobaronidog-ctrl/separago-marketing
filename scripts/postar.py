"""Robô de postagem do SeparaGo (Graph API) - v2.
Roda a cada 30 min. Posta o item pendente mais antigo cujo dia/hora já chegou.
Regras de segurança: no máximo 1 post por execução, intervalo mínimo de 60 min entre posts,
no máximo 7 por dia, pausa de 6 h se o Instagram bloquear por excesso.
"""
import json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

IG_ID = os.environ["IG_USER_ID"]
TOKEN = os.environ["IG_TOKEN"]
API = "https://graph.facebook.com/v21.0"
FILA = "fila/fila.json"
ESTADO = "fila/estado.json"
BRT = timezone(timedelta(hours=-3))
INTERVALO_MIN = 60
MAX_DIA = 7


def chamar(metodo, caminho, dados=None):
    dados = dict(dados or {})
    dados["access_token"] = TOKEN
    if metodo == "GET":
        req = urllib.request.Request(f"{API}/{caminho}?{urllib.parse.urlencode(dados)}")
    else:
        req = urllib.request.Request(f"{API}/{caminho}", data=urllib.parse.urlencode(dados).encode(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        corpo = e.read().decode().replace(TOKEN, "***")
        print("ERRO da API:", corpo, file=sys.stderr)
        raise RuntimeError(corpo[:300])


def esperar_pronto(container):
    for _ in range(40):
        s = chamar("GET", container, {"fields": "status_code"}).get("status_code")
        if s == "FINISHED":
            return
        if s in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"container {s}")
        time.sleep(15)
    raise RuntimeError("tempo esgotado esperando processar")


def postar(item):
    legenda = item["legenda"]
    if item["tipo"] == "reel":
        c = chamar("POST", f"{IG_ID}/media", {"media_type": "REELS", "video_url": item["video_url"],
                                             "caption": legenda, "share_to_feed": "true"})["id"]
    else:
        filhos = []
        for u in item["imagens"]:
            f = chamar("POST", f"{IG_ID}/media", {"image_url": u, "is_carousel_item": "true"})["id"]
            esperar_pronto(f)
            filhos.append(f)
        c = chamar("POST", f"{IG_ID}/media", {"media_type": "CAROUSEL", "children": ",".join(filhos), "caption": legenda})["id"]
    esperar_pronto(c)
    return chamar("POST", f"{IG_ID}/media_publish", {"creation_id": c})["id"]


def ler(caminho, padrao):
    try:
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return padrao


def salvar(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)


def main():
    fila = ler(FILA, [])
    estado = ler(ESTADO, {})
    agora = datetime.now(BRT)
    hoje, hhmm = agora.strftime("%Y-%m-%d"), agora.strftime("%H:%M")

    if hhmm < "07:30" or hhmm >= "22:30":
        print("Fora do horário de postagem (07:30-22:30)."); return

    if estado.get("pausa_ate") and agora < datetime.fromisoformat(estado["pausa_ate"]):
        print("Em pausa por bloqueio do Instagram até", estado["pausa_ate"]); return

    postados = [datetime.fromisoformat(i["postado_em"]) for i in fila if i.get("postado_em")]
    if postados and agora - max(postados) < timedelta(minutes=INTERVALO_MIN):
        print("Último post há menos de", INTERVALO_MIN, "min. Aguardando."); return
    if sum(1 for p in postados if p.astimezone(BRT).strftime("%Y-%m-%d") == hoje) >= MAX_DIA:
        print("Limite diário atingido."); return

    vencidos = sorted((i for i in fila if i.get("status") == "pendente"
                       and (i["data"], i.get("hora", "00:00")) <= (hoje, hhmm)),
                      key=lambda i: (i["data"], i.get("hora", "00:00")))
    if not vencidos:
        print("Nada vencido agora."); return
    alvo = vencidos[0]
    try:
        alvo["post_id"] = postar(alvo)
        alvo["status"] = "postado"
        alvo["postado_em"] = datetime.now(BRT).isoformat()
        alvo.pop("ultimo_erro", None)
        print("Postado:", alvo["id"])
    except Exception as e:
        msg = str(e).replace(TOKEN, "***")[:300]
        alvo["ultimo_erro"] = msg
        alvo["tentativas"] = alvo.get("tentativas", 0) + 1
        if "2207051" in msg or "request limit" in msg.lower() or '"code":4' in msg:
            estado["pausa_ate"] = (agora + timedelta(hours=6)).isoformat()
            print("Instagram limitou. Pausa de 6 h.", file=sys.stderr)
        elif alvo["tentativas"] >= 4:
            alvo["status"] = "falhou"
        print("Falhou:", alvo["id"], msg, file=sys.stderr)
    finally:
        salvar(FILA, fila)
        salvar(ESTADO, estado)


if __name__ == "__main__":
    main()
"""Robô de postagem do SeparaGo no Instagram (Graph API).
Pega o primeiro item pendente da fila cuja data já chegou, posta e marca como postado.
Seguro para rodar mais de uma vez no dia: se já postou hoje, não posta de novo.
"""
import json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

IG_ID = os.environ["IG_USER_ID"]
TOKEN = os.environ["IG_TOKEN"]
API = "https://graph.facebook.com/v21.0"
FILA = "fila/fila.json"
BRT = timezone(timedelta(hours=-3))


def chamar(metodo, caminho, dados=None):
    dados = dict(dados or {})
    dados["access_token"] = TOKEN
    if metodo == "GET":
        url = f"{API}/{caminho}?{urllib.parse.urlencode(dados)}"
        req = urllib.request.Request(url)
    else:
        req = urllib.request.Request(
            f"{API}/{caminho}", data=urllib.parse.urlencode(dados).encode(), method="POST"
        )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        corpo = e.read().decode()
        # nunca imprimir o token
        print("ERRO da API:", corpo.replace(TOKEN, "***"), file=sys.stderr)
        raise


def esperar_pronto(container):
    for _ in range(40):
        s = chamar("GET", container, {"fields": "status_code"}).get("status_code")
        if s == "FINISHED":
            return
        if s in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"container {s}")
        time.sleep(15)
    raise RuntimeError("tempo esgotado esperando o vídeo/imagem processar")


def postar(item):
    legenda = item["legenda"]
    if item["tipo"] == "reel":
        c = chamar("POST", f"{IG_ID}/media", {
            "media_type": "REELS", "video_url": item["video_url"], "caption": legenda,
            "share_to_feed": "true"})["id"]
    else:
        filhos = []
        for u in item["imagens"]:
            f = chamar("POST", f"{IG_ID}/media", {"image_url": u, "is_carousel_item": "true"})["id"]
            esperar_pronto(f)
            filhos.append(f)
        c = chamar("POST", f"{IG_ID}/media", {
            "media_type": "CAROUSEL", "children": ",".join(filhos), "caption": legenda})["id"]
    esperar_pronto(c)
    return chamar("POST", f"{IG_ID}/media_publish", {"creation_id": c})["id"]


def main():
    with open(FILA, encoding="utf-8") as f:
        fila = json.load(f)
    agora = datetime.now(BRT)
    hoje = agora.strftime("%Y-%m-%d")
    slot = os.environ.get("SLOT", "")  # ex.: "12:00" - qual horário este disparo atende

    # já postou algo neste horário hoje? então não repete (garantia)
    if any(i.get("status") == "postado" and i.get("postado_em", "").startswith(hoje)
           and i.get("hora") == slot for i in fila if slot):
        print("Já postado neste horário hoje. Nada a fazer.")
        return

    alvo = next((i for i in fila if i.get("status") == "pendente"
                 and i["data"] <= hoje and (not slot or i.get("hora", slot) == slot)), None)
    if not alvo:
        print("Nada pendente para este horário.")
        return
    try:
        pid = postar(alvo)
        alvo["status"] = "postado"
        alvo["postado_em"] = agora.isoformat()
        alvo["post_id"] = pid
        print("Postado:", alvo["id"])
    except Exception as e:
        alvo["ultimo_erro"] = str(e)[:200].replace(TOKEN, "***")
        print("Falhou:", alvo["id"], file=sys.stderr)
        raise
    finally:
        with open(FILA, "w", encoding="utf-8") as f:
            json.dump(fila, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
