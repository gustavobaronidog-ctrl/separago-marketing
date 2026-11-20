#!/usr/bin/env python3
"""Vigia do robo do Instagram do SeparaGo. Roda no GitHub Actions, sem depender do Claude.
Se algo estiver errado o job FALHA e o GitHub manda e-mail ao dono do repositorio."""
import json, os, sys, urllib.request, datetime

problemas, avisos = [], []

REPO = "https://github.com/gustavobaronidog-ctrl/separago-marketing"
ACTIONS = REPO + "/actions/workflows/maestro.yml"

def prob(msg, sem, com):
    """Registra problema com a solucao: o que o Gustavo faz sozinho e o que o Claude faz."""
    problemas.append((msg, sem, com))

def fmt(msg, sem, com):
    # %0A = quebra de linha nos avisos do GitHub (aparece tambem no e-mail)
    return f"{msg}%0A>> SEM O CLAUDE: {sem}%0A>> COM O CLAUDE: {com}%0A>> Guia completo: {REPO}/blob/main/SOCORRO.md"

SEM_ESTOQUE = ("o robo nao inventa conteudo sozinho e nao ha como repetir sem codigo: a conta fica sem post novo, sem risco para o perfil. "
               "Se quiser manter a conta ativa, poste voce mesmo 1 story ou Reel pelo celular ate o Claude voltar.")
COM_ESTOQUE = "abra o Claude e escreva: criar mais carrosseis e Reels para a fila do SeparaGo (marketing-instagram-modelagem)."

SEM_SITE = ("abra vercel.com , entre no projeto separago, aba Deployments, ache o ultimo deploy marcado 'Ready' que "
            "funcionava, clique nos 3 pontinhos e em 'Promote to Production'. Se o site abrir normal no seu celular, foi falha passageira: ignore.")
COM_SITE = "abra o Claude e escreva: o site do SeparaGo caiu, diagnostique e corrija."
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
    prob(f"item {i.get('id')} falhou: {i.get('ultimo_erro', 'sem detalhe')}",
         f"abra {ACTIONS} , clique na ultima execucao com X vermelho e leia a linha do erro. Token do Instagram vencido: gere outro e troque em Settings > Secrets. "
         f"Bloqueio do Instagram: espere 6 horas, o robo volta sozinho. Para tentar de novo agora, abra o arquivo fila/fila.json, ache o item {i.get('id')}, troque \"falhou\" por \"pendente\", troque o numero de \"tentativas\" por 0 e confirme em Commit changes.",
         "abra o Claude e escreva: o robo do SeparaGo falhou, leia o erro no GitHub e corrija.")

atrasados = [i for i in pend if quando(i) + datetime.timedelta(minutes=90) < agora]
if atrasados and not pausado:
    ids = ", ".join(str(i.get("id")) for i in atrasados[:6])
    prob(f"{len(atrasados)} post(s) atrasado(s) ha mais de 90 min: {ids}",
         f"abra {ACTIONS} , clique no botao 'Run workflow' (a direita) e depois no botao verde 'Run workflow'. Clique so 1 vez: o Maestro publica o que estiver atrasado (1 carrossel e 1 Reel por vez). "
         "Se aparecer X vermelho, leia o erro na execucao.",
         "abra o Claude e escreva: o robo do SeparaGo atrasou os posts, destrave.")

if pend:
    ultimo = max(datetime.date.fromisoformat(i["data"]) for i in pend)
    dias = (ultimo - hoje).days
    print(f"estoque ate {ultimo} ({dias} dias)")
    if dias < 2:
        prob(f"estoque do SeparaGo acaba em {dias} dia(s)", SEM_ESTOQUE, COM_ESTOQUE)
    elif dias < 7:
        avisos.append(f"estoque do SeparaGo baixo: {dias} dias")
else:
    prob("fila do SeparaGo acabou, nada sera postado", SEM_ESTOQUE, COM_ESTOQUE)

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
    if it.get("video_url"):
        arqs = list(arqs) + [it["video_url"]]
    for u in arqs:
        if isinstance(u, str) and u.startswith("http") and not existe(u):
            prob(f"arquivo nao abre (item {it.get('id')}): {u}",
                 f"abra o link no navegador. Se nao abre, a imagem foi apagada: no arquivo fila/fila.json ache o item {it.get('id')} e troque \"pendente\" por \"pulado\" "
                 "(o robo ignora esse item e segue com o proximo), depois Commit changes.",
                 "abra o Claude e escreva: uma imagem da fila do SeparaGo nao abre, restaure ou troque.")

for url in ["https://separago.vercel.app/separago"]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "vigia-github"})
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"site {url}: HTTP {r.status}")
            if r.status >= 400:
                prob(f"site fora do ar: {url} HTTP {r.status}", SEM_SITE, COM_SITE)
    except Exception as e:
        prob(f"site fora do ar: {url} ({e})", SEM_SITE, COM_SITE)

for a in avisos:
    print(f"::warning::{a}")
if problemas:
    resumo = os.environ.get("GITHUB_STEP_SUMMARY")
    for m, sem, com in problemas:
        print(f"::error title=Robo SeparaGo::{fmt(m, sem, com)}")
        if resumo:
            with open(resumo, "a", encoding="utf-8") as f:
                f.write(f"### Problema: {m}\n- **Sem o Claude:** {sem}\n- **Com o Claude:** {com}\n\n")
    sys.exit(1)
print("Tudo certo.")
