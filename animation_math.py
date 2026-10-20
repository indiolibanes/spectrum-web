"""
Funções puras das animações (sem Qt), para poder testá-las sem interface.
Usadas por button_fx.py e analysis_indicator.py.
"""
import math


def clamp01(value):
    return max(0.0, min(1.0, value))


def ripple_radius(center_x, center_y, width, height, progress):
    """Raio da ondulação: cresce até cobrir o canto mais distante do ponto tocado."""
    far_x = max(center_x, width - center_x)
    far_y = max(center_y, height - center_y)
    return clamp01(progress) * ((far_x ** 2 + far_y ** 2) ** 0.5)


def ripple_alpha(progress, peak=0.34):
    """A ondulação nasce visível e desaparece até o fim."""
    return peak * (1.0 - clamp01(progress)) ** 1.4


def busy_sweep_x(phase, width, band):
    """Posição da faixa de brilho (fase de 0 a 1) indo da esquerda para a direita, entrando e saindo por fora."""
    return -band + (phase % 1.0) * (width + 2 * band)


def blink_amount(t, period=4.2, closed_for=0.14):
    """Quanto os olhos estão fechados (0 aberto, 1 fechado). Pisca uma vez por período."""
    local = t % period
    if local >= closed_for:
        return 0.0
    half = closed_for / 2.0
    return 1.0 - abs(local - half) / half


def bounce(t, period=0.9, height=1.0):
    """Quique suave (0 a height) para a celebração."""
    return height * abs(math.sin(math.pi * (t % period) / period))


def pulse(t, period=1.2, low=0.35, high=1.0):
    """Pulsação suave entre low e high, para a etapa atual."""
    wave = 0.5 - 0.5 * math.cos(2 * math.pi * (t % period) / period)
    return low + (high - low) * wave


def spectrum_points(count, t, amplitude=1.0):
    """
    Curva que lembra um espectro NIR em movimento: soma de duas senoides deslizando.
    Retorna 'count' valores em [0, 1].
    """
    values = []
    for i in range(count):
        x = i / max(1, count - 1)
        y = 0.5 + 0.28 * math.sin(2 * math.pi * (1.3 * x - 0.35 * t)) + 0.14 * math.sin(2 * math.pi * (3.1 * x + 0.6 * t))
        values.append(clamp01(0.5 + (y - 0.5) * amplitude))
    return values


def mouth_params(mood):
    """
    Forma da boca para cada humor: (curvatura de -1 a 1, largura relativa).
    Curvatura positiva = sorriso; negativa = boca para baixo.
    """
    return {"smile": (1.0, 0.62), "calm": (0.55, 0.50), "alert": (-0.12, 0.40)}.get(mood, (0.55, 0.50))


def mix_hex(color_a, color_b, amount):
    """Mistura duas cores '#RRGGBB': amount 0 devolve a primeira, 1 a segunda."""
    a = [int(color_a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(color_b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * amount):02X}" for x, y in zip(a, b))


def spring(t, response=0.5, damping=0.6):
    """
    Resposta de uma mola amortecida que vai de 0 a 1 (com ultrapassagem quando damping < 1).

    t em segundos; response é o período aproximado da oscilação; damping 1 não ultrapassa.
    É o movimento "elástico" das interfaces da Apple: chega rápido e assenta com um leve vai e volta.
    """
    if t <= 0:
        return 0.0
    response = max(1e-3, response)
    damping = max(0.0, damping)
    omega = 2.0 * math.pi / response
    if damping >= 1.0:
        return 1.0 - (1.0 + omega * t) * math.exp(-omega * t)
    wd = omega * math.sqrt(1.0 - damping * damping)
    decay = math.exp(-damping * omega * t)
    return 1.0 - decay * (math.cos(wd * t) + (damping * omega / wd) * math.sin(wd * t))


def ease_out_expo(progress):
    """Desaceleração forte no fim: usada nas entradas de painéis."""
    p = clamp01(progress)
    return 1.0 if p >= 1.0 else 1.0 - 2.0 ** (-10.0 * p)


def staggered(elapsed, index, delay=0.06, duration=0.55):
    """Progresso (0 a 1) do item `index` de uma lista que entra em cascata, `delay` s depois do anterior."""
    return clamp01((elapsed - index * delay) / max(1e-3, duration))
