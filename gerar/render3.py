#!/usr/bin/env python3
"""Roupagem 3: video real (Pexels) de fundo, trocando de cena a cada ideia da narracao, com camada de cor da marca,
cabecalho de vidro, texto grande palavra por palavra e CTA na cor do segmento.
Clipes em /home/claude/px (m1-m4 mercado, c1-c4 confeitaria/salgados, l1,l3,l4 lanchonete; creditos: Pexels).
Uso: python3 gerar/render3.py [id ...]"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import videos_dinamicos as V
from videos_dinamicos import W, H, FPS, F, ease_back, ease_out, quebra, emoji_png, logo, round_mask, montar, audio, OUT, T, VIDEOS

PX = os.environ.get("PX_DIR", "/home/claude/px")
CLIPES = {"mercado": ["m1", "m2", "m4", "m1"], "confeitaria": ["c3", "c2", "c4", "c1"], "lanchonete": ["l1", "l3", "l4", "l1"]}
ROTULO = {"mercado": "DICA PARA MERCADO", "confeitaria": "DICA PARA CONFEITARIA", "lanchonete": "DICA PARA LANCHONETE"}
os.makedirs(T + "/bg", exist_ok=True)

def dur_clip(n):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{PX}/{n}.mp4"], capture_output=True, text=True).stdout)

def montar_fundo(vid, v, beats, cta, total, idx):
    """Gera T/bg/<vid>.mp4 (1080x1920, 30fps) com um trecho de clipe real por beat."""
    seg = v["seg"]; lista = CLIPES[seg]; partes = []
    cenas = [(b["t0"], b["dur"]) for b in beats] + [(cta["t0"], total - cta["t0"] + 0.2)]
    for i, (t0, du) in enumerate(cenas):
        n = lista[(idx + i) % len(lista)]; dc = dur_clip(n)
        lento = 1.6 if dc < 10 else 1.0
        need = du / lento
        ini = (idx * 2.7 + i * 3.3) % max(0.1, dc - need - 0.1) if dc > need + 0.3 else 0.0
        zoom = 1.0 + 0.00035 * 30  # pan/zoom lento
        out = f"{T}/bg/{vid}_{i}.mp4"
        vf = (f"setpts={lento}*PTS,scale=1188:2112:force_original_aspect_ratio=increase,"
              f"crop=1080:1920:x='(iw-1080)/2+((iw-1080)/2-4)*sin(t*0.5+{i})':y='(ih-1920)/2',fps=30,setsar=1,eq=saturation=1.12:contrast=1.04")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-ss", f"{ini:.2f}", "-i", f"{PX}/{n}.mp4", "-t", f"{du:.3f}",
                        "-vf", vf, "-an", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-pix_fmt", "yuv420p", out], check=True)
        partes.append(out)
    lst = f"{T}/bg/{vid}.txt"; open(lst, "w").write("".join(f"file '{p}'\n" for p in partes))
    bg = f"{T}/bg/{vid}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", bg], check=True)
    return bg

def camadas(c):
    """Sobreposicoes estaticas: cor da marca + escurecimento no topo e na base."""
    m = np.array(c["marca"], float)
    yy = np.linspace(0, 1, H)[:, None]
    alfa_t = np.clip(1 - yy / 0.22, 0, 1) * 0.62
    alfa_b = np.clip((yy - 0.40) / 0.55, 0, 1) ** 1.2 * 0.92
    a = np.clip(alfa_t + alfa_b + 0.16, 0, 0.94) * np.ones((1, W))
    cor = np.zeros((H, W, 3)); cor[:] = (m * 0.20 + np.array([8, 8, 12]) * 0.8)
    # reflexo de cor da marca nos cantos
    xx = np.linspace(0, 1, W)[None, :]
    glow = np.exp(-(((xx - 1.0) ** 2) + ((yy - 0.45) ** 2)) / 0.18)
    cor = cor * (1 - 0.35 * glow[..., None]) + m * 0.35 * glow[..., None]
    arr = np.dstack([cor, a * 255]).astype("uint8")
    return Image.fromarray(arr, "RGBA")

def vidro(ov, box, r, alpha=40, escuro=False):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, r, fill=((0, 0, 0, alpha) if escuro else (255, 255, 255, alpha)), outline=(255, 255, 255, 80), width=3)
    ov.alpha_composite(layer)

def topo(ov, c, seg):
    vidro(ov, (60, 84, 1020, 236), 76, 70, escuro=True)
    d = ImageDraw.Draw(ov)
    ov.paste(logo(112), (88, 104), round_mask(112))
    d.text((226, 108), "SeparaGo", font=F(48), fill=(255, 255, 255, 255))
    d.text((226, 168), "@separa.go", font=F(32), fill=(255, 255, 255, 200))
    rot = ROTULO[seg]; f = F(27); w = int(f.getlength(rot)) + 52
    d.rounded_rectangle((1020 - 24 - w, 126, 1020 - 24, 194), 34, fill=tuple(c["apoio"]) + (255,))
    d.text((1020 - 24 - w + 26, 142), rot, font=f, fill=(30, 30, 30, 255))

def frame3(t, bgimg, cam, v, c, beats, cta, total):
    seg = v["seg"]
    img = bgimg.convert("RGBA"); img.alpha_composite(cam)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    b = next((x for x in beats if x["t0"] <= t < x["t0"] + x["dur"]), None)
    topo(ov, c, seg)
    if b is None:  # CTA
        lt = t - cta["t0"]
        tint = Image.new("RGBA", (W, H), tuple(c["marca"]) + (int(min(1, lt / 0.4) * 205),)); img.alpha_composite(tint)
        s = min(1, ease_back(min(1, lt / 0.5))); sz = max(8, int(300 * s))
        vidro(ov, (330, 330, 750, 750), 90, 50)
        lg = logo(sz); ov.alpha_composite(lg, (540 - sz // 2, int(540 - sz // 2 + 10 * math.sin(lt * 3))))
        f = F(80); linhas = quebra(cta["toks"], f, 900); y = 840; n = 0
        for ln in linhas:
            wl = sum(f.getlength(w + " ") for w, _ in ln) - f.getlength(" "); x = 540 - wl / 2
            for w, forte in ln:
                a = min(1, max(0, (lt - 0.5 - n * cta['pw']) / 0.2)); n += 1
                if a > 0:
                    d.text((x + 3, y + 4 + (1 - ease_out(a)) * 24), w, font=f, fill=(0, 0, 0, int(100 * a)))
                    d.text((x, y + (1 - ease_out(a)) * 24), w, font=f, fill=(255, 255, 255, int(255 * a)))
                x += f.getlength(w + " ")
            y += 104
        a = min(1, max(0, (lt - 0.6 - n * cta['pw']) / 0.4))
        if a > 0:
            pul = 1 + 0.04 * math.sin(lt * 6); bw, bh = 560 * pul, 124 * pul; cy = y + 80
            d.rounded_rectangle((540 - bw / 2 + 5, cy - bh / 2 + 9, 540 + bw / 2 + 5, cy + bh / 2 + 9), 62, fill=(0, 0, 0, 80))
            d.rounded_rectangle((540 - bw / 2, cy - bh / 2, 540 + bw / 2, cy + bh / 2), 62, fill=(255, 255, 255, 255))
            ft = F(54); txt = "Link na bio →"; d.text((540 - ft.getlength(txt) / 2, cy - 36), txt, font=ft, fill=tuple(c["marca"]) + (255,))
            d.text((540 - F(38).getlength("@separa.go") / 2, cy + bh / 2 + 36), "@separa.go", font=F(38), fill=(255, 255, 255, 235))
        img.alpha_composite(ov); return img.convert("RGB")
    lt = t - b["t0"]
    pop = 1.0 if b["first"] else max(0.05, min(1, ease_back(min(1, lt / 0.45))))
    # emoji em medalha de vidro
    ep = Image.open(emoji_png(b["emo"])).convert("RGBA")
    f = F(96); linhas = quebra(b["toks"], f, 860)
    ph = len(linhas) * 136 + 80; pt = 1790 - ph
    vidro(ov, (70, pt - 250, 300, pt - 20), 115, 70, escuro=True)
    sz = max(6, int(150 * pop)); e2 = ep.resize((sz, max(4, int(sz * ep.height / ep.width))), Image.LANCZOS)
    ov.alpha_composite(e2, (185 - e2.width // 2, int(pt - 135 - e2.height // 2 + 6 * math.sin(lt * 4))))
    vidro(ov, (60, pt, 1020, 1790), 64, 105, escuro=True)
    y = pt + 38; n = 0
    for ln in linhas:
        x = 110
        for w, forte in ln:
            a = 1 if b["first"] else min(1, max(0, (lt - 0.1 - n * b['pw']) / 0.15)); n += 1
            wl = f.getlength(w)
            if a > 0:
                dy = (1 - ease_out(a)) * 34
                if forte:
                    d.rounded_rectangle((x - 14, y + 8 + dy, x + wl + 14, y + 128 + dy), 26, fill=tuple(c["apoio"]) + (int(255 * a),))
                    d.text((x, y + dy), w, font=f, fill=(28, 28, 28, int(255 * a)))
                else:
                    d.text((x, y + dy), w, font=f, fill=(255, 255, 255, int(255 * a)))
            x += f.getlength(w + " ")
        y += 136
    d.rounded_rectangle((60, 1830, 1020, 1844), 7, fill=(255, 255, 255, 60))
    d.rounded_rectangle((60, 1830, 60 + int(960 * min(1, t / total)), 1844), 7, fill=tuple(c["apoio"]) + (255,))
    img.alpha_composite(ov)
    return img.convert("RGB")

def gerar3(vid, idx=0):
    v, c, beats, cta, total, mp3v = montar(vid)
    for b in beats: emoji_png(b["emo"])
    bg = montar_fundo(vid, v, beats, cta, total, idx)
    wav = f"{T}/{vid}.wav"; audio(beats, cta, total, wav)
    cam = camadas(c); mp4 = f"{OUT}/{vid}.mp4"
    rd = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", bg, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-i", wav, "-i", mp3v, "-filter_complex", "[1:a]volume=0.4[a1];[2:a]volume=1.2[a2];[a1][a2]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.9[a]",
                          "-map", "0:v", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", mp4], stdin=subprocess.PIPE)
    nf = int(total * FPS); fs = W * H * 3; ultimo = None
    for i in range(nf):
        raw = rd.stdout.read(fs)
        if len(raw) == fs: ultimo = Image.frombytes("RGB", (W, H), raw)
        im = frame3(i / FPS, ultimo, cam, v, c, beats, cta, total)
        if i == 0: im.save(f"{OUT}/{vid}.jpg", quality=90)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait(); rd.kill()
    print(vid, f"{total:.1f}s", os.path.getsize(mp4) // 1024, "KB", flush=True)

if __name__ == "__main__":
    ids = sys.argv[1:] or list(VIDEOS)
    for vid in ids:
        seg_ids = [k for k in VIDEOS if VIDEOS[k]["seg"] == VIDEOS[vid]["seg"]]
        gerar3(vid, seg_ids.index(vid))
