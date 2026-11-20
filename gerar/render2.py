#!/usr/bin/env python3
"""Roupagem 2 dos videos dinamicos do SeparaGo: fundo em gradiente animado com brilho (reflexo),
cartoes de vidro, bonequinhos animados que encenam o que a voz fala, texto grande palavra por palavra.
Usa os roteiros/narracao ja existentes (videos_dinamicos.py). Uso: python3 gerar/render2.py [id ...]"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import videos_dinamicos as V
from videos_dinamicos import W, H, FPS, F, ease_back, ease_out, quebra, emoji_png, logo, round_mask, montar, audio, OUT, T, VIDEOS

ROTULO = {"mercado": "DICA PARA MERCADO", "confeitaria": "DICA PARA CONFEITARIA", "lanchonete": "DICA PARA LANCHONETE"}
CLIENTE = {"mercado": (52, 120, 220), "confeitaria": (130, 96, 210), "lanchonete": (24, 160, 170)}
PELE = [(250, 208, 172), (196, 140, 102)]

# ---------------------------------------------------------------- fundo
_yy, _xx = np.mgrid[0:384, 0:216]
_xn, _yn = _xx / 216.0, _yy / 384.0
def fundo(t, c, vivo=False):
    m = np.array(c["marca"], float); cl = np.array(c["claro"], float)
    k = (_xn * 0.45 + _yn * 0.8)[..., None]
    base = m * (1.0 - 0.62 * k) if not vivo else m * (0.85 - 0.45 * k)
    img = base + 0 * _xn[..., None]
    for i in range(3):  # brilhos grandes que passeiam
        cx = 0.5 + 0.38 * math.sin(0.5 * t + i * 2.1); cy = 0.5 + 0.42 * math.cos(0.37 * t + i * 1.7)
        d2 = ((_xn - cx) ** 2 + (_yn - cy) ** 2) / 0.12
        img = img + cl * np.exp(-d2)[..., None] * (0.34 if not vivo else 0.30)
    for i in range(9):  # bokeh subindo
        cx = (0.1 + 0.8 * ((i * 0.37) % 1)); cy = 1.1 - ((t * (0.05 + 0.01 * i) + i * 0.13) % 1.2)
        d2 = ((_xn - cx) ** 2 + (_yn - cy) ** 2) / (0.0016 + 0.0006 * (i % 3))
        img = img + 255 * np.exp(-d2)[..., None] * 0.20
    p = (t * 0.16) % 2.2 - 0.6  # faixa de luz diagonal (reflexo)
    band = np.exp(-(((_xn + 0.55 * _yn) - p) ** 2) / 0.012)
    img = img + 255 * band[..., None] * 0.10
    im = Image.fromarray(np.clip(img, 0, 255).astype("uint8")).resize((W, H), Image.BICUBIC)
    return im

# ---------------------------------------------------------------- bonequinho
SS = 2
def _p(v): return int(round(v * SS))

def boneco(t, mood, pose, papel, seg, flip=False, escala=1.0, pulo=0.0):
    """Desenha um bonequinho (400x560 base) e devolve RGBA. papel: 'dono' ou 'cliente'."""
    cv = Image.new("RGBA", (_p(400), _p(560)), (0, 0, 0, 0)); d = ImageDraw.Draw(cv)
    c = V.CORES[seg]
    dono = papel == "dono"
    pele = PELE[0] if dono else PELE[1]
    camisa = (255, 255, 255) if dono else CLIENTE[seg]
    calca = (38, 44, 78)
    avental = tuple(c["apoio"])
    bob = math.sin(t * 6.0) * 6 + (-abs(math.sin(t * 7.5)) * 70 if pulo else 0)
    oy = bob
    def L(x0, y0, x1, y1, w, col):
        d.line((_p(x0), _p(y0 + oy), _p(x1), _p(y1 + oy)), fill=col, width=_p(w))
        for (x, y) in ((x0, y0), (x1, y1)):
            r = w / 2; d.ellipse((_p(x - r), _p(y + oy - r), _p(x + r), _p(y + oy + r)), fill=col)
    def E(x0, y0, x1, y1, col, off=True):
        o = oy if off else 0
        d.ellipse((_p(x0), _p(y0 + o), _p(x1), _p(y1 + o)), fill=col)
    def RR(x0, y0, x1, y1, r, col):
        d.rounded_rectangle((_p(x0), _p(y0 + oy), _p(x1), _p(y1 + oy)), _p(r), fill=col)
    # pernas e sapatos (nao seguem o pulo inteiro)
    perna = 8 * math.sin(t * 6.0) if pose in ("idle", "hold", "shrug") else 0
    for sx, ph in ((168, 1), (232, -1)):
        d.line((_p(sx), _p(430), _p(sx + perna * ph), _p(520 + (oy if pulo else 0) * 0.3)), fill=calca, width=_p(44))
        e = 520 + (oy if pulo else 0) * 0.3
        d.ellipse((_p(sx + perna * ph - 34), _p(e - 12), _p(sx + perna * ph + 36), _p(e + 22)), fill=(250, 250, 250))
    # cabelo atras (mulher da confeitaria)
    if dono and seg == "confeitaria":
        E(98, 60, 302, 330, (92, 52, 40))
    # corpo
    RR(105, 250, 295, 455, 78, camisa)
    if dono:
        RR(138, 292, 262, 455, 40, avental); RR(172, 340, 228, 385, 12, tuple(int(x * 0.82) for x in avental))
        d.line((_p(150), _p(262 + oy), _p(175), _p(296 + oy)), fill=avental, width=_p(14)); d.line((_p(250), _p(262 + oy), _p(225), _p(296 + oy)), fill=avental, width=_p(14))
    else:
        RR(105, 330, 295, 352, 4, tuple(int(x * 0.8) for x in camisa))
    # bracos
    sway = math.sin(t * 5.0)
    def mao(ombro, ang, comp):
        a = math.radians(ang); return ombro[0] + comp * math.cos(a), ombro[1] + comp * math.sin(a)
    ol, orr = (122, 292), (278, 292)
    if pose == "idle": al, ar, cl_, cr = 112 + 6 * sway, 68 - 6 * sway, 118, 118
    elif pose == "wave": al, ar, cl_, cr = 112, -62 + 26 * math.sin(t * 11), 118, 130
    elif pose == "up": al, ar, cl_, cr = -112 + 18 * math.sin(t * 9), -68 - 18 * math.sin(t * 9), 135, 135
    elif pose == "hold": al, ar, cl_, cr = 52 + 6 * sway, 128 - 6 * sway, 112, 112
    elif pose == "point": al, ar, cl_, cr = 112, -14 + 6 * sway, 118, 150
    elif pose == "shrug": al, ar, cl_, cr = 168 + 6 * sway, 12 - 6 * sway, 128, 128
    else: al, ar, cl_, cr = 112, 68, 118, 118
    for om, ang, comp in ((ol, al, cl_), (orr, ar, cr)):
        hx, hy = mao(om, ang, comp)
        L(om[0], om[1], hx, hy, 40, camisa)
        E(hx - 25, hy - 25, hx + 25, hy + 25, pele)
    # cabeca
    if not dono or seg != "confeitaria":
        pass
    E(98, 55, 302, 262, pele)
    # cabelo / bone
    if dono and seg != "confeitaria":
        d.pieslice((_p(94), _p(36), _p(306), _p(250 + oy)), 192, 348, fill=tuple(c["apoio"]))
        d.rounded_rectangle((_p(92), _p(100 + oy), _p(308), _p(118 + oy)), _p(9), fill=tuple(int(x * 0.85) for x in c["apoio"]))
        d.rounded_rectangle((_p(240), _p(102 + oy), _p(350), _p(124 + oy)), _p(11), fill=tuple(int(x * 0.85) for x in c["apoio"]))
    elif dono:
        d.pieslice((_p(94), _p(36), _p(306), _p(250 + oy)), 190, 350, fill=(92, 52, 40))
        E(160, 8, 240, 78, (92, 52, 40)); d.rectangle((_p(110), _p(96 + oy), _p(290), _p(112 + oy)), fill=tuple(c["apoio"]))
    else:
        d.pieslice((_p(96), _p(38), _p(304), _p(250 + oy)), 194, 346, fill=(40, 30, 28))
    # bochechas
    E(112, 190, 150, 218, (255, 140, 150)); E(250, 190, 288, 218, (255, 140, 150))
    # olhos
    piscar = (t % 3.3) < 0.11
    olhar = (6, -4) if mood == "think" else (0, 0)
    ew = 27 if mood == "wow" else 23
    for ex in (158, 242):
        if piscar:
            d.line((_p(ex - 20), _p(165 + oy), _p(ex + 20), _p(165 + oy)), fill=(30, 30, 40), width=_p(7))
        else:
            E(ex - ew, 165 - ew, ex + ew, 165 + ew, (255, 255, 255))
            E(ex - 11 + olhar[0], 165 - 11 + olhar[1], ex + 11 + olhar[0], 165 + 11 + olhar[1], (30, 30, 40))
            E(ex - 3 + olhar[0], 165 - 8 + olhar[1], ex + 3 + olhar[0], 165 - 2 + olhar[1], (255, 255, 255))
    # sobrancelhas e boca
    br = (50, 36, 30)
    def B(x0, y0, x1, y1): d.line((_p(x0), _p(y0 + oy), _p(x1), _p(y1 + oy)), fill=br, width=_p(9))
    if mood == "happy":
        B(130, 122, 182, 116); B(270, 122, 218, 116)
        d.pieslice((_p(168), _p(190 + oy), _p(232), _p(250 + oy)), 0, 180, fill=(120, 30, 44)); d.pieslice((_p(180), _p(222 + oy), _p(220), _p(250 + oy)), 0, 180, fill=(255, 120, 130))
    elif mood == "angry":
        B(128, 126, 184, 148); B(272, 126, 216, 148)
        d.arc((_p(170), _p(214 + oy), _p(230), _p(250 + oy)), 200, 340, fill=(120, 30, 44), width=_p(9))
    elif mood in ("worry", "sad"):
        B(128, 148, 184, 124); B(272, 148, 216, 124)
        d.arc((_p(172), _p(218 + oy), _p(228), _p(246 + oy)), 200, 340, fill=(120, 30, 44), width=_p(9))
        gx = 300 + 4 * math.sin(t * 4); gy = 98 + (t * 40) % 40
        d.polygon([(_p(gx), _p(gy - 30 + oy)), (_p(gx - 14), _p(gy + oy)), (_p(gx + 14), _p(gy + oy))], fill=(120, 200, 255))
        E(gx - 14, gy - 12, gx + 14, gy + 16, (120, 200, 255))
    elif mood == "wow":
        B(130, 112, 182, 104); B(270, 112, 218, 104)
        E(186, 205, 214, 246, (120, 30, 44))
    else:  # think
        B(130, 130, 182, 124); B(270, 112, 218, 120)
        d.line((_p(180), _p(228 + oy), _p(224), _p(222 + oy)), fill=(120, 30, 44), width=_p(8))
    cv = cv.resize((int(400 * escala), int(560 * escala)), Image.LANCZOS)
    if flip: cv = cv.transpose(Image.FLIP_LEFT_RIGHT)
    return cv

# ---------------------------------------------------------------- cena
def sombra(ov, cx, y, w):
    sh = Image.new("RGBA", (int(w), 46), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((0, 0, int(w) - 1, 45), fill=(0, 0, 0, 70))
    ov.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)), (int(cx - w / 2), int(y - 22)))

def vidro(ov, box, r, alpha=34):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, r, fill=(255, 255, 255, alpha), outline=(255, 255, 255, 90), width=3)
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0 + 18, y0 + 12, x1 - 18, y0 + 12 + (y1 - y0) // 5), r - 18, fill=(255, 255, 255, 18))  # reflexo
    ov.alpha_composite(layer)

def topo(ov, c, seg):
    vidro(ov, (60, 84, 1020, 236), 76, 36)
    d = ImageDraw.Draw(ov)
    av = logo(112); ov.paste(av, (88, 104), round_mask(112))
    d.text((226, 108), "SeparaGo", font=F(48), fill=(255, 255, 255, 255))
    d.text((226, 168), "@separa.go", font=F(32), fill=(255, 255, 255, 190))
    rot = ROTULO[seg]; f = F(27); w = int(f.getlength(rot)) + 52
    d.rounded_rectangle((1020 - 24 - w, 126, 1020 - 24, 194), 34, fill=tuple(c["apoio"]) + (255,))
    d.text((1020 - 24 - w + 26, 142), rot, font=f, fill=(30, 30, 30, 255))

def modo_beat(i, beats):
    intro = next((k for k, b in enumerate(beats) if b["emo"] == "📣"), 3)
    if i < intro: return "problema", i
    if i == intro: return "intro", 0
    if i == len(beats) - 1: return "final", 0
    return "dica", i - intro - 1

def frame2(t, v, c, beats, cta, total):
    seg = v["seg"]
    b = next((x for x in beats if x["t0"] <= t < x["t0"] + x["dur"]), None)
    if b is None:  # CTA
        lt = t - cta["t0"]
        img = fundo(t, c, vivo=True).convert("RGBA"); ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        # confete
        rs = np.random.RandomState(3)
        for k in range(46):
            x0 = rs.rand() * W; sp = 220 + rs.rand() * 380; ph = rs.rand() * 6
            y = ((lt * sp + ph * 300) % (H + 200)) - 100
            if lt < 0.2: continue
            col = [tuple(c["apoio"]), (255, 255, 255), tuple(c["claro"])][k % 3]
            ang = lt * (2 + rs.rand() * 4) + k
            sw = 14 * abs(math.cos(ang)) + 4
            d.rounded_rectangle((x0 + 30 * math.sin(lt * 2 + k), y, x0 + 30 * math.sin(lt * 2 + k) + sw, y + 26), 4, fill=col + (230,))
        s = min(1, ease_back(min(1, lt / 0.5))); sz = max(8, int(300 * s))
        vidro(ov, (330, 290, 750, 710), 90, 40)
        lg = logo(sz); ov.alpha_composite(lg, (540 - sz // 2, int(500 - sz // 2 + 10 * math.sin(lt * 3))))
        f = F(78); linhas = quebra(cta["toks"], f, 900); y = 790; n = 0
        for ln in linhas:
            wl = sum(f.getlength(w + " ") for w, _ in ln) - f.getlength(" "); x = 540 - wl / 2
            for w, forte in ln:
                a = min(1, max(0, (lt - 0.5 - n * cta['pw']) / 0.2)); n += 1
                if a > 0:
                    d.text((x + 3, y + 4 + (1 - ease_out(a)) * 24), w, font=f, fill=(0, 0, 0, int(90 * a)))
                    d.text((x, y + (1 - ease_out(a)) * 24), w, font=f, fill=(255, 255, 255, int(255 * a)))
                x += f.getlength(w + " ")
            y += 100
        a = min(1, max(0, (lt - 0.6 - n * cta['pw']) / 0.4))
        if a > 0:
            pul = 1 + 0.04 * math.sin(lt * 6); bw, bh = 560 * pul, 124 * pul; cy = y + 70
            d.rounded_rectangle((540 - bw / 2 + 5, cy - bh / 2 + 9, 540 + bw / 2 + 5, cy + bh / 2 + 9), 62, fill=(0, 0, 0, 70))
            d.rounded_rectangle((540 - bw / 2, cy - bh / 2, 540 + bw / 2, cy + bh / 2), 62, fill=(255, 255, 255, 255))
            ft = F(54); txt = "Link na bio →"; d.text((540 - ft.getlength(txt) / 2, cy - 36), txt, font=ft, fill=tuple(c["marca"]) + (255,))
            d.text((540 - F(38).getlength("@separa.go") / 2, cy + bh / 2 + 36), "@separa.go", font=F(38), fill=(255, 255, 255, 230))
        # bonecos comemorando
        for papel, cx, fl in ():
            bs = boneco(lt + (0 if papel == "dono" else 0.4), "happy", "up", papel, seg, flip=fl, escala=0.78, pulo=1)
            ov.alpha_composite(bs, (cx - bs.width // 2, 1840 - bs.height))
        img.alpha_composite(ov); return img.convert("RGB")

    lt = t - b["t0"]; i = beats.index(b)
    modo, j = modo_beat(i, beats)
    img = fundo(t, c).convert("RGBA"); ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    topo(ov, c, seg)
    vidro(ov, (60, 290, 1020, 1130), 70, 30)
    d = ImageDraw.Draw(ov)
    pop = 1.0 if b["first"] else min(1, ease_back(min(1, lt / 0.45)))
    pop = max(0.05, pop)
    chao = 1085
    # personagens
    if modo == "problema":
        md = ["wow", "worry", "sad"][j % 3]; mc = ["happy", "wow", "angry"][j % 3]
        pd_ = ["idle", "shrug", "shrug"][j % 3]; pc = ["wave", "up", "up"][j % 3]
        pers = [("dono", 300, md, pd_, False), ("cliente", 790, mc, pc, True)]
        prop = (540, 500, 280)
    elif modo == "intro":
        pers = [("dono", 330, "happy", "point", False)]
        prop = (760, 650, 340)
    elif modo == "dica":
        pers = [("dono", 330, "happy", ["hold", "point", "wave"][j % 3], False)]
        prop = (770, 660, 380)
    else:
        pers = [("dono", 300, "happy", "up", False), ("cliente", 790, "happy", "up", True)]
        prop = (540, 510, 270)
    pers = []
    prop = (540, 690, 520 if modo != "final" else 470)
    for k in range(3):  # aneis de onda atras do objeto
        ph = (lt * 0.7 + k / 3.0) % 1.0
        r = int(210 + 330 * ph); al = int(90 * (1 - ph))
        d.ellipse((540 - r, 690 - r, 540 + r, 690 + r), outline=(255, 255, 255, al), width=6)
    for k in range(7):  # brilhos orbitando
        ang = lt * 1.3 + k * 0.9; rr = 330 + 40 * math.sin(lt * 2 + k)
        sx, sy = 540 + rr * math.cos(ang), 690 + rr * 0.8 * math.sin(ang); sr = 9 + 5 * math.sin(lt * 5 + k)
        d.polygon([(sx, sy - sr * 2), (sx + sr * .6, sy - sr * .6), (sx + sr * 2, sy), (sx + sr * .6, sy + sr * .6), (sx, sy + sr * 2), (sx - sr * .6, sy + sr * .6), (sx - sr * 2, sy), (sx - sr * .6, sy - sr * .6)], fill=tuple(c["apoio"]) + (230,))
    for papel, cx, md, pz, fl in pers:
        esc = 1.02 * (0.92 + 0.08 * pop)
        bs = boneco(lt, md, pz, papel, seg, flip=fl, escala=esc, pulo=1 if modo == "final" else 0)
        sombra(ov, cx, chao, 230)
        ov.alpha_composite(bs, (int(cx - bs.width / 2), int(chao - 18 - bs.height * 0.965)))
    # objeto/emoji da cena
    ep = Image.open(emoji_png(b["emo"])).convert("RGBA")
    base = prop[2]; sz = int(base * pop); sz = max(6, sz)
    asp = ep.height / ep.width
    e2 = ep.resize((sz, max(4, int(sz * asp))), Image.LANCZOS)
    e2 = e2.rotate(7 * math.sin(lt * 3.2), resample=Image.BICUBIC, expand=True)
    fy = 18 * math.sin(lt * 3.6)
    halo = Image.new("RGBA", (sz + 160, sz + 160), (0, 0, 0, 0)); ImageDraw.Draw(halo).ellipse((20, 20, sz + 140, sz + 140), fill=(255, 255, 255, 46))
    ov.alpha_composite(halo.filter(ImageFilter.GaussianBlur(18)), (int(prop[0] - halo.width / 2), int(prop[1] - halo.height / 2 + fy)))
    ov.alpha_composite(e2, (int(prop[0] - e2.width / 2), int(prop[1] - e2.height / 2 + fy)))
    # texto
    f = F(100); linhas = quebra(b["toks"], f, 930); y = 1200; n = 0
    for ln in linhas:
        x = 80
        for w, forte in ln:
            a = 1 if b["first"] else min(1, max(0, (lt - 0.1 - n * b['pw']) / 0.15)); n += 1
            wl = f.getlength(w)
            if a > 0:
                dy = (1 - ease_out(a)) * 34
                if forte:
                    d.rounded_rectangle((x - 14, y + 8 + dy, x + wl + 14, y + 134 + dy), 26, fill=tuple(c["apoio"]) + (int(255 * a),))
                    d.text((x, y + dy), w, font=f, fill=(28, 28, 28, int(255 * a)))
                else:
                    d.text((x + 3, y + 5 + dy), w, font=f, fill=(0, 0, 0, int(80 * a)))
                    d.text((x, y + dy), w, font=f, fill=(255, 255, 255, int(255 * a)))
            x += f.getlength(w + " ")
        y += 144
    # barra de progresso
    d.rounded_rectangle((60, 1830, 1020, 1844), 7, fill=(255, 255, 255, 50))
    d.rounded_rectangle((60, 1830, 60 + int(960 * min(1, t / total)), 1844), 7, fill=tuple(c["apoio"]) + (255,))
    img.alpha_composite(ov)
    return img.convert("RGB")

def gerar2(vid):
    v, c, beats, cta, total, mp3v = montar(vid)
    for b in beats: emoji_png(b["emo"])
    wav = f"{T}/{vid}.wav"; audio(beats, cta, total, wav)
    mp4 = f"{OUT}/{vid}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-i", wav, "-i", mp3v, "-filter_complex", "[1:a]volume=0.4[a1];[2:a]volume=1.2[a2];[a1][a2]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.9[a]",
                          "-map", "0:v", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "25", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", mp4], stdin=subprocess.PIPE)
    nf = int(total * FPS)
    for i in range(nf):
        im = frame2(i / FPS, v, c, beats, cta, total)
        if i == 0: im.save(f"{OUT}/{vid}.jpg", quality=90)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    print(vid, f"{total:.1f}s", os.path.getsize(mp4) // 1024, "KB", flush=True)

if __name__ == "__main__":
    for vid in (sys.argv[1:] or VIDEOS): gerar2(vid)
