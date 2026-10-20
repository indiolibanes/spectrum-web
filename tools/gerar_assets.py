"""
Gera as imagens procedurais do tema: textura de madeira escura e cursores de fibra de celulose.

Uso (só desenvolvimento; precisa de numpy e Pillow):
    python3 tools/gerar_assets.py

Tudo é gerado por semente fixa, então o resultado é reproduzível. Não há imagem de terceiros.
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
TEXTURES = ROOT / "assets" / "textures"
CURSORS = ROOT / "assets" / "cursors"


# ---------------------------------------------------------------------------------------------
# Textura de madeira (tile 512 x 512 sem emendas, RGBA, só alfa varia)
# ---------------------------------------------------------------------------------------------
def periodic_noise(size, sigma_x, sigma_y, rng):
    """Ruído periódico (emenda perfeita) com correlação maior em x que em y: gera fibras."""
    spectrum = np.fft.fft2(rng.standard_normal((size, size)))
    fx = np.fft.fftfreq(size)[None, :]
    fy = np.fft.fftfreq(size)[:, None]
    gauss = np.exp(-0.5 * ((fx * sigma_x) ** 2 + (fy * sigma_y) ** 2) * (2 * math.pi) ** 2)
    out = np.real(np.fft.ifft2(spectrum * gauss))
    out -= out.min()
    return out / out.max()


def wood_texture(size=512, planks=2, seed=7):
    rng = np.random.default_rng(seed)
    fibers = periodic_noise(size, 90, 1.3, rng)            # fibras longas, finas
    streaks = periodic_noise(size, 40, 3.5, rng)           # veios mais largos
    warp = periodic_noise(size, 110, 40, rng)              # deforma de leve os anéis de crescimento
    pores = periodic_noise(size, 1.2, 0.9, rng)            # poros pequenos
    height = size // planks
    yy, xx = np.mgrid[0:size, 0:size]
    value = np.zeros((size, size))
    for k in range(planks):
        y0, y1 = k * height, (k + 1) * height
        local = (yy[y0:y1] - y0) / height
        phase = rng.uniform(0, 1)
        rings = 0.5 + 0.5 * np.sin(2 * math.pi * (local * (5.5 + 2 * k) + warp[y0:y1] * 1.1 + phase))
        rings = rings ** 1.6
        plank = 0.40 * rings + 0.34 * fibers[y0:y1] + 0.26 * streaks[y0:y1]
        plank = (plank - plank.min()) / (plank.max() - plank.min())
        plank = plank ** 1.35
        plank *= 0.80 + 0.25 * (rng.uniform() - 0.5)          # cada tábua com um brilho próprio
        value[y0:y1] = plank
        # junta entre as tábuas: um fio claro seguido de uma sombra
        value[y0, :] = 0.0
        value[y0 + 1, :] = 0.95
        value[y0 + 2, :] = 0.35
    value -= 0.10 * (pores > 0.82)                           # poros escurecem um pouco
    value = np.clip(value, 0, 1)
    alpha = (value * 74).astype(np.uint8)
    rgba = np.zeros((size, size, 4), np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = 214, 160, 88  # âmbar (cor da fibra)
    rgba[..., 3] = alpha
    return Image.fromarray(rgba, "RGBA")


# ---------------------------------------------------------------------------------------------
# Cursores de fibra de celulose
# ---------------------------------------------------------------------------------------------
ARROW = [(1.0, 1.0), (1.0, 20.5), (6.0, 16.0), (9.6, 24.2), (13.0, 22.8), (9.4, 14.8), (16.0, 14.8)]


def bezier(p0, p1, p2, steps=24):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            for t in (i / steps for i in range(steps + 1))]


def cursor_image(fill, outline, strand, scale=4, logical=32, seed=3, ring=False):
    """Seta feita de papel: corpo claro com fibras soltas na cauda e traços de fibra por dentro."""
    rng = np.random.default_rng(seed)
    n = logical * scale
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pts = [(x * scale, y * scale) for x, y in ARROW]

    # sombra suave
    shadow = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).polygon([(x + 1.6 * scale, y + 1.8 * scale) for x, y in pts], fill=(0, 0, 0, 120))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(1.3 * scale)))

    draw.polygon(pts, fill=fill)
    draw = ImageDraw.Draw(img)
    # fibras por dentro (curvas finas e claras/escuras seguindo o eixo da seta)
    inner = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    idraw = ImageDraw.Draw(inner)
    for _ in range(11):
        x0 = rng.uniform(1.5, 11.0) * scale
        y0 = rng.uniform(3.0, 22.0) * scale
        curve = bezier((x0, y0), (x0 + rng.uniform(-1.5, 1.5) * scale, y0 + 3 * scale),
                       (x0 + rng.uniform(-2, 2) * scale, y0 + rng.uniform(5, 8) * scale))
        shade = (110, 84, 40, 70) if rng.uniform() < .6 else (255, 255, 255, 90)
        idraw.line(curve, fill=shade, width=max(1, int(0.55 * scale)))
    mask = Image.new("L", (n, n), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    clipped = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    clipped.paste(inner, (0, 0), mask)
    img.alpha_composite(clipped)

    # halo claro fino (legível sobre o preto AMOLED) e contorno escuro
    draw = ImageDraw.Draw(img)
    draw.line(pts + [pts[0]], fill=(255, 250, 235, 110), width=int(2.6 * scale), joint="curve")
    draw.line(pts + [pts[0]], fill=outline, width=int(1.25 * scale), joint="curve")

    # fibras soltas saindo da cauda
    for i in range(4):
        base = (9.3 * scale + i * 0.5 * scale, 21.0 * scale + i * 0.4 * scale)
        angle = math.radians(rng.uniform(60, 105))
        length = rng.uniform(2.6, 4.6) * scale
        end = (base[0] + math.cos(angle) * length, base[1] + math.sin(angle) * length)
        ctrl = (base[0] + rng.uniform(-3, 3) * scale, base[1] + length * 0.45)
        draw.line(bezier(base, ctrl, end), fill=strand, width=max(1, int(0.7 * scale)))
    if ring:  # anel de polpa perto da ponta: marca de "clicável"
        cx, cy = 1.0 * scale, 1.0 * scale
        draw.ellipse([cx - 0.2 * scale, cy - 0.2 * scale, cx + 0.2 * scale, cy + 0.2 * scale], fill=outline)
    return img


def save_cursor(name, **kw):
    big = cursor_image(scale=4, **kw)                       # 128 px
    big.resize((64, 64), Image.LANCZOS).save(CURSORS / f"{name}@2x.png", optimize=True)
    big.resize((32, 32), Image.LANCZOS).save(CURSORS / f"{name}.png", optimize=True)


def main():
    TEXTURES.mkdir(parents=True, exist_ok=True)
    CURSORS.mkdir(parents=True, exist_ok=True)
    wood_texture().save(TEXTURES / "madeira-escura.png", optimize=True)
    save_cursor("fibra-seta", fill=(244, 237, 220, 255), outline=(30, 22, 10, 255), strand=(236, 226, 200, 220))
    save_cursor("fibra-mao", fill=(226, 195, 92, 255), outline=(30, 22, 10, 255), strand=(240, 220, 150, 230), ring=True)
    print("Gerado em", TEXTURES, "e", CURSORS)


if __name__ == "__main__":
    main()
