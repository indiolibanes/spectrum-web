"""
Gera os espécimes de tema (docs/img/especime-*.png) em HTML + Chromium, a partir das MESMAS receitas
de vidro e das MESMAS paletas usadas pelo programa (glass.py e appearance.PALETTES).

É uma prévia fiel de cor, textura, tipografia e proporção; não é uma captura do PyQt5.

Uso (desenvolvimento): python3 tools/especime.py   # precisa de playwright + chromium
"""
import asyncio
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import glass  # noqa: E402
from animation_math import mix_hex  # noqa: E402


def palettes():
    source = (ROOT / "appearance.py").read_text(encoding="utf-8")
    start, end = source.index("PALETTES={"), source.index("DEFAULT_THEME")
    namespace = {}
    exec(source[start:end], namespace)
    return namespace["PALETTES"]


def css(value):
    match = re.fullmatch(r"qlineargradient\(x1:0,y1:0,x2:0,y2:1,stop:0 (.+?),stop:1 (.+)\)", value)
    return f"linear-gradient(180deg,{match.group(1)},{match.group(2)})" if match else value


def page(p, texture, arrow, hand):
    f = ROOT.as_uri() + "/assets/fonts/"
    dark = glass.is_dark(p)
    accent = p["accent_strong"]
    glows = ",".join(
        f"radial-gradient(circle at {fx*100:.0f}% {fy*100:.0f}%,{glass.rgba(c, a)} 0,transparent {r*100:.0f}vmax)"
        for fx, fy, r, c, a in glass.glow_spec(p))
    return f"""<!doctype html><meta charset=utf-8><style>
@font-face{{font-family:'IBM Plex Sans';src:url('{f}IBMPlexSans-Regular.ttf');font-weight:400}}
@font-face{{font-family:'IBM Plex Sans';src:url('{f}IBMPlexSans-Bold.ttf');font-weight:700}}
@font-face{{font-family:'EB Garamond';src:url('{f}EBGaramond-Bold.ttf');font-weight:700}}
@font-face{{font-family:'EB Garamond';src:url('{f}EBGaramond-Regular.ttf');font-weight:400}}
@font-face{{font-family:'IBM Plex Mono';src:url('{f}IBMPlexMono-Regular.ttf');font-weight:400}}
*{{box-sizing:border-box;margin:0}}
body{{width:1600px;height:1000px;background:{glows},url('{texture}'),{p['canvas']};color:{p['text']};font:400 13px 'IBM Plex Sans';padding:16px 20px;display:flex;flex-direction:column;gap:14px;position:relative}}
.panel{{background:{css(glass.panel_fill(p))};border:1px solid {glass.rim(p)};border-radius:16px}}
.top{{display:flex;align-items:center;gap:14px;padding:12px 18px}}
.brand b{{display:block;font:700 24px 'EB Garamond';color:{p['heading']}}} .brand small{{color:{p['muted']};font-size:11px}}
.btn{{padding:10px 16px;border-radius:10px;border:1px solid {glass.rim(p)};background:{css(glass.button_fill(p))};color:{p['text']};position:relative;overflow:hidden}}
.btn:before,.go:before{{content:'';position:absolute;inset:0 0 50% 0;background:linear-gradient(180deg,{glass.rgba(*glass.edge_highlight(p))},transparent);max-height:18px}}
.btn.hover{{background:{css(glass.button_fill(p,'hover'))};border-color:{glass.rgba(p['accent'],.75)}}}
.btn.pressed{{background:{css(glass.primary_fill(p,'hot'))};color:{p['on_strong']};border-color:{accent}}}
.btn.primary{{background:{css(glass.primary_fill(p))};color:{p['on_strong']};border-color:{mix_hex(accent,'#FFFFFF',.35)};padding:13px 18px;font:700 15px 'IBM Plex Sans'}}
.btn.busy{{background:{css(glass.vgrad(glass.rgba(p['accent'],.30),glass.rgba(p['accent'],.16)))};color:{p['accent']};border-color:{glass.rgba(p['accent'],.7)};font:700 15px 'IBM Plex Sans'}}
.btn.danger{{color:{p['danger']};border-color:{glass.rgba(p['danger'],.7)}}}
input{{background:{glass.field_fill(p)};color:{p['text']};border:1px solid {p['accent']};border-radius:10px;padding:9px 13px;font:400 13px 'IBM Plex Sans';width:150px}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}} .kpi{{padding:12px 18px}}
.kpi .t{{color:{p['muted']}}} .kpi .v{{font:400 28px 'IBM Plex Mono'}} .kpi .s{{color:{p['muted']};font-size:11px}}
.main{{display:grid;grid-template-columns:420px 1fr;gap:16px;flex:1}}
.left{{display:flex;flex-direction:column;gap:12px}} .box{{padding:14px 16px;display:flex;flex-direction:column;gap:10px}}
.lbl{{color:{p['muted']};font-size:11px}} .sec{{font:700 19px 'EB Garamond';color:{p['heading']}}}
.result{{background:{css(glass.result_fill(p))};border:1px solid {glass.rgba(p['accent'],.38)};border-radius:16px;padding:14px 16px}}
.hero{{font:400 40px 'IBM Plex Mono';color:{p['accent']}}}
.chart{{padding:14px;display:flex;flex-direction:column;gap:10px}} .plot{{flex:1;border-radius:10px;position:relative;overflow:hidden;background:{glass.field_fill(p)}}}
.ind{{height:92px;background:{css(glass.vgrad(glass.rgba(p['soft'] if dark else '#FFFFFF',.78),glass.rgba(p['surface'] if dark else p['soft'],.62)))};border:1px solid {glass.rim(p)};border-radius:14px;position:relative;padding:12px 16px 0 86px}}
.ind:before{{content:'';position:absolute;left:0;top:0;bottom:0;width:6px;background:{p['accent']};border-radius:3px}}
.face{{position:absolute;left:24px;top:24px;width:44px;height:44px;border-radius:50%;border:2px solid {p['accent']};background:{glass.rgba(p['accent'],.16)}}}
.face:before,.face:after{{content:'';position:absolute;top:15px;width:4px;height:4px;border-radius:50%;background:{p['accent']}}} .face:before{{left:11px}} .face:after{{right:11px}}
.mouth{{position:absolute;left:12px;top:22px;width:16px;height:9px;border-bottom:2.2px solid {p['accent']};border-radius:0 0 16px 16px}}
.ind h4{{font:700 19px 'EB Garamond';color:{p['heading']}}} .ind p{{color:{p['muted']};margin-top:4px;width:520px}}
.steps{{position:absolute;right:16px;top:58px;display:flex;gap:6px}} .steps i{{display:block;width:34px;height:6px;border-radius:3px;background:{p['border']}}} .steps i.on{{background:{p['accent']}}}
.steps small{{position:absolute;right:0;top:10px;color:{p['muted']};font-size:11px}}
.foot{{padding:9px 14px;display:flex;justify-content:space-between;align-items:center;color:{p['muted']}}} .cred{{font-size:11px}}
.kb{{position:absolute;right:40px;bottom:120px;width:440px;background:{css(glass.vgrad(mix_hex(p['canvas'],p['surface'],.65),p['canvas'])) if dark else css(glass.vgrad(p['soft'],mix_hex(p['soft'],p['border'],.5)))};border:1px solid {glass.rim(p,1.2)};padding:10px 14px 14px;border-radius:14px}}
.kb .cap{{display:flex;justify-content:space-between;color:{p['muted']};font-size:11px;margin-bottom:8px}}
.kb .row{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:8px}}
.kb .k{{height:56px;border-radius:10px;border:1px solid {glass.rim(p,1.2)};background:{css(glass.button_fill(p))};display:flex;align-items:center;justify-content:center;font:400 19px 'IBM Plex Mono'}}
.kb .a{{color:{p['muted']};font:400 13px 'IBM Plex Sans'}} .kb .e{{background:{css(glass.primary_fill(p))};color:{p['on_strong']};border-color:{mix_hex(accent,'#FFFFFF',.35)};font:700 15px 'IBM Plex Sans'}} .kb .p{{background:{css(glass.primary_fill(p,'hot'))};color:{p['on_strong']};border-color:{accent}}}
.cur{{position:absolute;width:32px;height:32px}}
</style><body>
<div class='panel top'><div class=brand><b>SpectrumLab Pro</b><small>Supervisório NIR</small></div>
<span class=btn>Wi-Fi</span><span class=lbl>IP ESP32:</span><input value='192.168.4.1'><span class=lbl>Porta:</span><input value='8080' style='width:84px'>
<span class='btn primary' style='padding:10px 16px;font-size:13px;font-weight:400'>Conectar ESP32</span><span style='flex:1'></span><span class=btn>Modo manual</span><span class='btn danger'>Parada de emergência</span><span class=btn>Login</span></div>
<div class=kpis><div class='panel kpi'><div class=t>Energia espectral</div><div class=v>12 480</div><div class=s>contagens</div></div><div class='panel kpi'><div class=t>Pico</div><div class=v>730 nm</div><div class=s>R730</div></div><div class='panel kpi'><div class=t>Razão R680 / R730</div><div class=v>0,842</div><div class=s>celulose</div></div><div class='panel kpi'><div class=t>Razão R860 / R760</div><div class=v>1,117</div><div class=s>água</div></div></div>
<div class=main><div class=left>
<div class='panel box'><span class=lbl>Método analítico</span><input value='Seco (placa)' style='width:100%'><span class=sec>Ensaios automáticos</span>
<span class='btn busy'>Analisando…</span><span class='btn hover'>Leitura com repetibilidade · 5×</span><span class='btn pressed'>Calibrar · Branco e escuro</span><span class='btn primary'>Realizar leitura</span><span class=btn>Calibrar · Branco e escuro</span></div>
<div class=result><span class=lbl>Número kappa</span><div class=hero>18,4</div><div class=lbl style='margin-top:4px'>Classificação: polpa branqueável</div></div></div>
<div class='panel chart'><div class=plot><svg width=1100 height=420 style='position:absolute;left:0;top:0'><polyline fill=none stroke='{p['accent']}' stroke-width=3 points='40,300 200,230 360,180 520,140 680,120 840,105 1000,100'/></svg></div>
<div class=ind><div class=face><div class=mouth></div></div><h4>Leitura com repetibilidade</h4><p>Lendo o espectro. Seis bandas do infravermelho próximo em ação.</p><div class=steps><i class=on></i><i class=on></i><i class=on></i><i></i><i></i><small>Etapa 3 de 5</small></div></div></div></div>
<div class='panel foot'><span>Status: pronto para a próxima amostra.</span><span class=cred>Protótipo desenvolvido por Davi Baracat, Kauê Carvalho e Mateus Ferreira</span></div>
<div class=kb><div class=cap><span>IP ESP32</span><span>Fechar</span></div>
<div class=row><div class=k>1</div><div class=k>2</div><div class=k>3</div><div class='k a'>Apagar</div></div>
<div class=row><div class=k>4</div><div class='k p'>5</div><div class=k>6</div><div class='k a'>Limpar</div></div>
<div class=row><div class=k>7</div><div class=k>8</div><div class=k>9</div><div class=k>.</div></div>
<div class=row><div class='k a'>‹</div><div class=k>0</div><div class='k a'>›</div><div class='k e'>Concluir</div></div></div>
<img class=cur src='{arrow}' style='left:560px;top:250px'><img class=cur src='{hand}' style='left:300px;top:352px'>
</body>"""


async def shoot(items, out_dir):
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(executable_path="/opt/pw-browsers/chromium", args=["--allow-file-access-from-files"])
        for name, html in items:
            tmp = out_dir / f".{name}.html"
            tmp.write_text(html, encoding="utf-8")
            tab = await browser.new_page(viewport={"width": 1600, "height": 1000})
            await tab.goto(tmp.as_uri())
            await tab.wait_for_timeout(500)
            await tab.screenshot(path=str(out_dir / f"especime-{name}.png"))
            tmp.unlink()
        await browser.close()


def main():
    out = ROOT / "docs" / "img"
    out.mkdir(parents=True, exist_ok=True)
    pals = palettes()
    arrow = (ROOT / "assets/cursors/fibra-seta@2x.png").as_uri()
    hand = (ROOT / "assets/cursors/fibra-mao@2x.png").as_uri()
    items = [("umber", page(pals["umber"], (ROOT / "assets/textures/madeira-escura.png").as_uri(), arrow, hand)),
             ("claro", page(pals["light"], (ROOT / "assets/textures/celulose-claro.png").as_uri(), arrow, hand))]
    asyncio.run(shoot(items, out))
    print("espécimes em", out)


if __name__ == "__main__":
    main()
