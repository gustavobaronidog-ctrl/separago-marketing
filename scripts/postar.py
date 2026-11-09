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
