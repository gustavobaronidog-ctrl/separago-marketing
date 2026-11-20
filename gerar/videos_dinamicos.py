#!/usr/bin/env python3
"""Gera os videos dinamicos (Reels 1080x1920) do SeparaGo.
Texto entra palavra por palavra, cada passo ganha um desenho (emoji grande que 'estoura' na tela),
efeitos sonoros sincronizados (pop, tique, whoosh, sino) e final com contexto, na cor do segmento.
Uso: python3 gerar/videos_dinamicos.py [id ...]   (sem argumento gera todos)"""
import os, sys, subprocess, math, wave, struct, re, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f"{R}/midia/dinamicos"; T = "/tmp/vid"
os.makedirs(OUT, exist_ok=True); os.makedirs(T + "/emo", exist_ok=True)
W, H, FPS = 1080, 1920, 30
BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
F = lambda s: ImageFont.truetype(BOLD, s)

# identidade visual por segmento (as mesmas cores do app / site do SeparaGo)
CORES = {
    "mercado":    dict(marca=(15, 122, 85),  claro=(79, 224, 160), apoio=(255, 181, 71)),
    "confeitaria": dict(marca=(217, 63, 122), claro=(255, 143, 181), apoio=(255, 214, 102)),
    "lanchonete": dict(marca=(214, 59, 36),  claro=(255, 138, 107), apoio=(255, 181, 71)),
}

FALAS = {'v01-balanca': ['Cliente pediu um quilo de carne.', 'Na balança deu um quilo e trezentos.', 'Quem paga a diferença?', 'Faz assim, em três passos.', 'Um: avisa antes que o valor final vem da balança.', 'Dois: pesa e confere antes de fechar.', 'Três: cobra o peso real. Nem mais, nem menos.', 'Combinado claro, sem briga na porta.', 'No SeparaGo o cliente já pede sabendo. Link na bio.'], 'v02-encomenda': ['Cem coxinhas pra sábado.', 'Três dias de conversa, e o cliente sumiu.', 'Encomenda espalhada se perde.', 'Antes de aceitar, confirma quatro coisas.', 'Um: quantidade e sabor.', 'Dois: dia e hora.', 'Três: sinal no Pix antes de fritar.', 'Quatro: tudo anotado num lugar só.', 'No SeparaGo o pedido já chega organizado. Link na bio.'], 'v03-correria': ['Sábado, oito da noite. Doze pedidos no zap.', 'E o sem cebola se perdeu na conversa.', 'Cliente bravo, lanche refeito.', 'Três jeitos de errar menos na correria.', 'Um: observação grudada no item.', 'Dois: comanda impressa na cozinha.', 'Três: confere antes de embalar.', 'No SeparaGo o sem cebola vai junto do lanche até a cozinha. Link na bio.']}

VIDEOS = {
 "v01-balanca": dict(seg="mercado", legenda=(
   "Item de balança sem briga na porta: avise antes que o valor final vem da pesagem, confira o peso e cobre o peso real.\n\n"
   "No SeparaGo o pedido entra com valor estimado e o Pix só sai depois da pesagem. Link na bio para ver como funciona.\n\n@separa.go"),
  beats=[
   ("🥩", "Cliente pediu **1 kg** de carne."),
   ("⚖️", "Na balança deu **1,3 kg**."),
   ("🤔", "Quem paga a **diferença**?"),
   ("📣", "Faz assim, em **3 passos**:"),
   ("⚖️", "**1.** Avise antes: o valor final vem da balança."),
   ("✅", "**2.** Pese e confira antes de fechar o pedido."),
   ("💰", "**3.** Cobre o **peso real**. Nem mais, nem menos."),
   ("🚪", "Cliente que entendeu o combinado **não briga na porta**."),
  ], cta="No SeparaGo o cliente pede já sabendo disso: valor estimado, e o Pix só depois da pesagem."),
 "v02-encomenda": dict(seg="confeitaria", legenda=(
   "Antes de aceitar uma encomenda de salgado ou doce, confirme 4 coisas: quantidade e sabor, dia e hora, sinal no Pix e tudo anotado num lugar só.\n\n"
   "No SeparaGo o cliente escolhe sabor e quantidade sozinho e o pedido chega organizado para você. Link na bio para ver.\n\n@separa.go"),
  beats=[
   ("🥟", "**100 coxinhas** para sábado."),
   ("💬", "Três dias de conversa. E o cliente **sumiu**."),
   ("😮‍💨", "Encomenda se perde quando fica **espalhada**."),
   ("📝", "Antes de aceitar, confirme **4 coisas**:"),
   ("🥟", "**1.** Quantidade e sabor de cada item."),
   ("📅", "**2.** Dia e hora de retirar ou entregar."),
   ("💸", "**3.** Sinal no Pix **antes** de fritar ou assar."),
   ("📋", "**4.** Tudo anotado num lugar só, não em 40 mensagens."),
  ], cta="No SeparaGo o cliente escolhe sabor e quantidade sozinho, e o pedido chega organizado."),
 "v03-correria": dict(seg="lanchonete", legenda=(
   "3 jeitos de errar menos pedido na correria: observação grudada no item, comanda impressa para a cozinha e conferência antes de embalar.\n\n"
   "No SeparaGo o 'sem cebola' vai junto do lanche até a cozinha. Link na bio para ver.\n\n@separa.go"),
  beats=[
   ("🍔", "Sábado, **20h**. 12 pedidos no WhatsApp."),
   ("🧅", "E o **'sem cebola'** se perdeu no meio da conversa."),
   ("😤", "Cliente bravo. Lanche **refeito**. Prejuízo."),
   ("📣", "**3 jeitos** de errar menos na correria:"),
   ("📝", "**1.** Observação grudada no **item**, não solta na conversa."),
   ("🖨️", "**2.** Comanda **impressa** na cozinha. Ninguém lê celular de mão suja."),
   ("✅", "**3.** Confere o pedido **antes** de fechar a embalagem."),
  ], cta="No SeparaGo o 'sem cebola' vai junto do lanche até a cozinha, e a comanda sai impressa."),
}

try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from lote2 import NOVOS
    for _k, _v in NOVOS.items():
        FALAS[_k] = _v.pop('falas'); VIDEOS[_k] = _v
except ImportError:
    pass

# ---------- emoji crisp (renderizado pelo Chrome, fundo transparente) ----------
def emoji_png(e):
    p = f"{T}/emo/{'-'.join(f'{ord(c):x}' for c in e)}.png"
    if os.path.exists(p): return p
    h = f"{T}/emo/e.html"
    open(h, "w").write(f"<html><body style='margin:0;background:transparent'><div style=\"font-family:'Noto Color Emoji';font-size:380px;line-height:440px;width:480px;height:480px;text-align:center\">{e}</div></body></html>")
    subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    "--default-background-color=00000000", "--window-size=480,480", f"--screenshot={p}", "file://" + h],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    im = Image.open(p).convert("RGBA"); im = im.crop(im.getbbox()); im.save(p); return p

LOGO_SVG = ('<svg viewBox="0 0 200 200" width="400" height="400" xmlns="http://www.w3.org/2000/svg"><rect width="200" height="200" rx="46" fill="#F6F5F2"/>'
 '<path d="M72 80 C72 44 132 44 132 80" stroke="#E5452D" stroke-width="13" stroke-linecap="round" fill="none"/>'
 '<path d="M52 76 H152 L160 148 Q161 160 149 160 H55 Q43 160 44 148 Z" fill="#0F7A55"/>'
 '<path d="M84 118 H122 M106 100 L124 118 L106 136" stroke="#fff" stroke-width="11" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
 '<path d="M22 112 H38 M16 130 H34" stroke="#0F7A55" stroke-width="8" stroke-linecap="round" opacity=".5"/></svg>')
def logo(size):
    p = f"{T}/logo.png"
    if not os.path.exists(p):
        open(f"{T}/logo.svg", "w").write(LOGO_SVG)
        subprocess.run(["rsvg-convert", "-w", "400", "-h", "400", f"{T}/logo.svg", "-o", p], check=True)
    return Image.open(p).convert("RGBA").resize((size, size), Image.LANCZOS)

def round_mask(size):
    m = Image.new("L", (size * 4, size * 4), 0); ImageDraw.Draw(m).ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
    return m.resize((size, size), Image.LANCZOS)

# ---------- texto ----------
def tokens(txt):
    out = []
    for parte in re.split(r"(\*\*.+?\*\*)", txt):
        forte = parte.startswith("**")
        ws = parte.strip("*").split()
        for k, w in enumerate(ws):
            # pontuacao colada na palavra anterior (sem espaco no texto original)
            if k == 0 and out and not forte and not parte.startswith(" ") and not w[0].isalnum():
                out[-1] = (out[-1][0] + w, out[-1][1])
            else:
                out.append((w, forte))
    return out

def quebra(toks, font, maxw):
    linhas, atual, wlin = [], [], 0
    sp = font.getlength(" ")
    for w, f in toks:
        wl = font.getlength(w)
        if atual and wlin + sp + wl > maxw:
            linhas.append(atual); atual, wlin = [], 0
        wlin += (sp if atual else 0) + wl; atual.append((w, f))
    if atual: linhas.append(atual)
    return linhas

def ease_back(x):
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def ease_out(x): return 1 - (1 - x) ** 3



def silencios(mp3):
    r = subprocess.run(["ffmpeg", "-i", mp3, "-af", "silencedetect=noise=-32dB:d=0.18", "-f", "null", "-"], capture_output=True, text=True).stderr
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
    fim = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    return [(a + b) / 2 for a, b in zip(ini, fim) if b > a]

def duracao(mp3):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp3],
                                capture_output=True, text=True).stdout)

def montar(vid):
    v = VIDEOS[vid]; c = CORES[v["seg"]]
    mp3 = f"{OUT}/voz/{vid}.mp3"; falas = FALAS[vid]; n = len(falas)
    dur_a = duracao(mp3); sil = silencios(mp3)
    inicio_fala, fim_fala = 0.25, dur_a - 0.15
    total_c = sum(len(f) for f in falas)
    acum, alvo = 0, []
    for f in falas:
        alvo.append(inicio_fala + (fim_fala - inicio_fala) * acum / total_c); acum += len(f)
    marcas = [0.0]
    for k in range(1, n):  # encaixa a fronteira de cada fala na pausa real mais proxima
        cand = [m for m in sil if abs(m - alvo[k]) < 0.9 and m > marcas[-1] + 1.0]
        marcas.append(min(cand, key=lambda m: abs(m - alvo[k])) - 0.1 if cand else alvo[k] - 0.1)
    marcas.append(dur_a + 1.4)
    toks_beats = [tokens(txt) for _, txt in v["beats"]]
    beats = []
    for i, (emo, txt) in enumerate(v["beats"]):
        t0, t1 = marcas[i], marcas[i + 1]
        nt = len(toks_beats[i])
        pw = min(0.30, max(0.10, (t1 - t0 - 0.7) / (nt + 1)))
        beats.append(dict(emo=emo, toks=toks_beats[i], t0=t0, dur=t1 - t0, first=(i == 0), pw=pw))
    ct = tokens(v["cta"]); t0, t1 = marcas[n - 1], marcas[n]
    cta = dict(toks=ct, t0=t0, dur=t1 - t0, pw=min(0.30, max(0.10, (t1 - t0 - 2.0) / (len(ct) + 1))))
    return v, c, beats, cta, t1, mp3

def desenhar_topo(img, d):
    av = logo(96); m = round_mask(96)
    img.paste(av, (80, 120), m)
    d.text((196, 126), "SeparaGo", font=F(42), fill=(20, 20, 20))
    d.text((196, 176), "@separa.go", font=F(32), fill=(120, 120, 120))

def frame(t, v, c, beats, cta, total):
    img = Image.new("RGB", (W, H), (255, 255, 255)); d = ImageDraw.Draw(img)
    b = next((x for x in beats if x["t0"] <= t < x["t0"] + x["dur"]), None)
    if b is None:  # CTA
        lt = t - cta["t0"]
        img.paste(Image.new("RGB", (W, H), c["marca"]))
        d = ImageDraw.Draw(img)
        s = min(1, ease_back(min(1, lt / 0.45)))
        sz = max(8, int(360 * s)); lg = logo(sz)
        img.paste(lg, (100 + (360 - sz) // 2, 380 + (360 - sz) // 2), lg)
        f = F(76); linhas = quebra(cta["toks"], f, 880)
        y = 860; n = 0
        for ln in linhas:
            x = 100
            for w, forte in ln:
                a = min(1, max(0, (lt - 0.5 - n * cta['pw']) / 0.2)); n += 1
                if a > 0:
                    col = tuple(int(255 * a + c["marca"][k] * (1 - a)) for k in range(3))
                    d.text((x, y + (1 - ease_out(a)) * 24), w, font=f, fill=col)
                x += f.getlength(w + " ")
            y += 96
        a = min(1, max(0, (lt - 0.6 - n * cta['pw']) / 0.4))
        pill_y = y + 50
        if a > 0:
            d.rounded_rectangle((100, pill_y, 520, pill_y + 104), 52, fill=(255, 255, 255))
            d.text((140, pill_y + 20), "Link na bio →", font=F(48), fill=c["marca"])
            d.text((100, pill_y + 150), "@separa.go", font=F(40), fill=(255, 255, 255))
        return img
    lt = t - b["t0"]
    desenhar_topo(img, d)
    # emoji grande
    ep = Image.open(emoji_png(b["emo"])).convert("RGBA")
    base = 520
    if b["first"]: s = 1.0
    else: s = max(0.05, ease_back(min(1, lt / 0.4)))
    sz = int(base * s); e2 = ep.resize((sz, int(sz * ep.height / ep.width)), Image.LANCZOS)
    img.paste(e2, (80 + (base - sz) // 2, 340 + (base - e2.height) // 2), e2)
    # texto palavra por palavra
    f = F(98); linhas = quebra(b["toks"], f, 930); y = 940; n = 0
    for ln in linhas:
        x = 80
        for w, forte in ln:
            a = 1 if b["first"] else min(1, max(0, (lt - 0.1 - n * b['pw']) / 0.15)); n += 1
            wl = f.getlength(w)
            if a > 0:
                dy = (1 - ease_out(a)) * 30
                if forte:
                    barra = Image.new("RGBA", (int(wl) + 16, 104), tuple(c["marca"]) + (int(70 * a),))
                    img.paste(barra, (int(x) - 8, int(y + 26 + dy)), barra)
                col = c["marca"] if forte else (20, 20, 20)
                col = tuple(int(col[k] * a + 255 * (1 - a)) for k in range(3))
                d.text((x, y + dy), w, font=f, fill=col)
            x += f.getlength(w + " ")
        y += 128
    d.text((80, H - 130), "@separa.go", font=F(34), fill=(150, 150, 150))
    return img

# ---------- audio ----------
SR = 44100
def add(buf, t, s, vol=1.0):
    i = int(t * SR); n = min(len(s), len(buf) - i)
    if n > 0: buf[i:i + n] += s[:n] * vol
def tom(f0, f1, dur, dec=18):
    n = int(dur * SR); x = np.linspace(0, dur, n, endpoint=False)
    fr = f0 + (f1 - f0) * (x / dur); ph = 2 * np.pi * np.cumsum(fr) / SR
    return np.sin(ph) * np.exp(-dec * x)
def whoosh(dur=0.28):
    n = int(dur * SR); r = np.random.RandomState(7).randn(n)
    k = np.convolve(r, np.ones(40) / 40, mode="same")
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    return (k - np.convolve(k, np.ones(400) / 400, mode="same")) * env * 2.2
def audio(beats, cta, total, path):
    buf = np.zeros(int((total + 0.5) * SR))
    for b in beats:
        add(buf, b["t0"], whoosh(), 0.22)
        if not b["first"]: add(buf, b["t0"] + 0.02, tom(700, 260, 0.16), 0.30)
        for k in range(len(b["toks"])):
            if not b["first"]: add(buf, b["t0"] + 0.1 + k * b["pw"], tom(2200, 1800, 0.03, 90), 0.10)
    add(buf, cta["t0"], whoosh(0.4), 0.4)
    add(buf, cta["t0"] + 0.05, tom(660, 660, 0.9, 5), 0.3); add(buf, cta["t0"] + 0.18, tom(990, 990, 0.9, 5), 0.25)
    add(buf, cta["t0"] + 0.34, tom(1320, 1320, 1.0, 5), 0.2)
    buf = np.clip(buf * 0.9, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((buf * 32767).astype("<i2").tobytes())

def gerar(vid):
    v, c, beats, cta, total, mp3v = montar(vid)
    for b in beats: emoji_png(b["emo"])
    wav = f"{T}/{vid}.wav"; audio(beats, cta, total, wav)
    mp4 = f"{OUT}/{vid}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-i", wav, "-i", mp3v, "-filter_complex", "[1:a]volume=0.4[a1];[2:a]volume=1.2[a2];[a1][a2]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.9[a]", "-map", "0:v", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", mp4], stdin=subprocess.PIPE)
    nf = int(total * FPS)
    for i in range(nf):
        im = frame(i / FPS, v, c, beats, cta, total)
        if i == 0: im.save(f"{OUT}/{vid}.jpg", quality=90)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    print(vid, f"{total:.1f}s", os.path.getsize(mp4) // 1024, "KB")

if __name__ == "__main__":
    for vid in (sys.argv[1:] or VIDEOS): gerar(vid)
