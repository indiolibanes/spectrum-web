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
    return namespace["PALETTES"], namespace["SERIES"]


def css(value):
    match = re.fullmatch(r"qlineargradient\(x1:0,y1:0,x2:0,y2:1,stop:0 (.+?),stop:1 (.+)\)", value)
    return f"linear-gradient(180deg,{match.group(1)},{match.group(2)})" if match else value


def tone_css(p, tone):
    return (f"background:{css(glass.tone_fill(p, tone))};color:{glass.tone_text(p, tone)};border-color:{glass.tone_border(p, tone)}")


def page(p, series, texture, arrow, hand):
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
.face{{background:radial-gradient(circle at 35% 30%,#FFF0A0,#FFD23F 55%,#F2A20C);border:1.5px solid rgba(140,80,0,.7)}} .face:before,.face:after{{background:#4A2B00}} .mouth{{border-bottom-color:#4A2B00}}
.btn{{font-size:14px}} .btn.t-gold{{{tone_css(p,'gold')}}} .btn.t-sky{{{tone_css(p,'sky')}}} .btn.t-violet{{{tone_css(p,'violet')}}}
.btn.t-rose{{{tone_css(p,'rose')}}} .btn.t-green{{{tone_css(p,'green')}}} .btn.t-amber{{{tone_css(p,'amber')}}}
.kpi{{display:flex;gap:14px;align-items:center;position:relative;overflow:hidden}} .kpi .ic{{width:40px;height:40px;border-radius:12px;display:flex;align-items:center;justify-content:center;font:700 18px 'IBM Plex Sans'}}
.kpi .bar{{position:absolute;left:0;top:14px;bottom:14px;width:4px;border-radius:2px}}
.lbl{{font-size:13px}} .kpi .t{{font-size:14px}} .kpi .s{{font-size:12px}}
.bars{{position:absolute;left:30px;right:30px;bottom:34px;top:30px;display:flex;gap:26px;align-items:flex-end}}
.bars div{{flex:1;display:flex;flex-direction:column;align-items:center;gap:6px;height:100%;justify-content:flex-end}}
.bars i{{display:block;width:100%;border-radius:8px 8px 0 0;opacity:.88}} .bars b{{font:400 14px 'IBM Plex Mono'}} .bars s{{text-decoration:none;display:block;width:24px;height:4px;border-radius:2px}} .bars em{{font:700 12px 'IBM Plex Sans';font-style:normal;color:{p['text']}}} .bars u{{text-decoration:none;font-size:12px;color:{p['muted']}}}
.foot{{padding:14px 20px;font-size:14px;border:1px solid {glass.rgba(p['accent'],.40)};background:{css(glass.result_fill(p))}}} .foot b{{font-weight:700;color:{p['accent']}}} .cred{{font-size:14px;color:{p['text']}}}
.cal{{display:flex;flex-direction:column;gap:6px;font-size:14px}} .cal div{{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid {glass.rim(p,.5)}}} .cal span{{color:{p['muted']}}} .cal b{{font:400 16px 'IBM Plex Mono';color:{p['text']}}}
</style><body>
<div class='panel top'><div class=brand><b>SpectrumLab Pro</b><small>Supervisório NIR</small></div>
<span class=btn>Wi-Fi</span><span class=lbl>IP ESP32:</span><input value='192.168.4.1'><span class=lbl>Porta:</span><input value='8080' style='width:84px'>
<span class='btn t-green'>Conectar ESP32</span><span style='flex:1'></span><span class='btn t-amber'>Modo manual</span><span class='btn danger'>Parada de emergência</span><span class='btn t-sky'>Login</span><span class=btn>Configurações</span></div>
<div class=kpis>
<div class='panel kpi'><i class=bar style='background:{p["accent"]}'></i><div class=ic style='background:{glass.rgba(p["accent"],.2)};color:{p["accent"]}'>⚡</div><div><div class=t>Energia espectral</div><div class=v>12 480</div><div class=s>contagens</div></div></div>
<div class='panel kpi'><i class=bar style='background:{p["sky"]}'></i><div class=ic style='background:{glass.rgba(p["sky"],.2)};color:{p["sky"]}'>↗</div><div><div class=t>Pico</div><div class=v>730 nm</div><div class=s>R730</div></div></div>
<div class='panel kpi'><i class=bar style='background:{p["positive"]}'></i><div class=ic style='background:{glass.rgba(p["positive"],.2)};color:{p["positive"]}'>❦</div><div><div class=t>Razão R680 / R730</div><div class=v>0,842</div><div class=s>celulose</div></div></div>
<div class='panel kpi'><i class=bar style='background:{p["violet"]}'></i><div class=ic style='background:{glass.rgba(p["violet"],.2)};color:{p["violet"]}'>💧</div><div><div class=t>Razão R860 / R760</div><div class=v>1,117</div><div class=s>água</div></div></div></div>
<div class=main><div class=left>
<div class='panel box'><span class=lbl>Método analítico</span><input value='Seco (placa)' style='width:100%'><span class=sec>Ensaios automáticos</span>
<span class='btn busy'>Analisando…</span><span class='btn t-sky hover'>Leitura com repetibilidade · 5×</span><span class='btn t-violet'>Calibrar · Branco e escuro</span><span class='btn primary'>Realizar leitura</span><span class='btn t-rose'>Esvaziar gaveta</span></div>
<div class='panel box'><span class=sec>Calibração</span><div class=cal><div><span>R²</span><b>0,998</b></div><div><span>RMSE</span><b>± 0,214</b></div><div><span>Amostras (N)</span><b>12</b></div></div></div>
<div class=result><span class=lbl>Número kappa</span><div class=hero>18,4</div><div class=lbl style='margin-top:4px'>Classificação: polpa branqueável</div></div></div>
<div class='panel chart'><div class=plot><div class=bars><div><b>8 120</b><i style='height:38%;background:linear-gradient(180deg,{series[0]},{mix_hex(series[0],p["canvas"],.35)})'></i><s style='background:{series[0]}'></s><em>450 nm</em><u>Azul</u></div><div><b>9 960</b><i style='height:52%;background:linear-gradient(180deg,{series[1]},{mix_hex(series[1],p["canvas"],.35)})'></i><s style='background:{series[1]}'></s><em>500 nm</em><u>Ciano</u></div><div><b>12 480</b><i style='height:70%;background:linear-gradient(180deg,{series[2]},{mix_hex(series[2],p["canvas"],.35)})'></i><s style='background:{series[2]}'></s><em>550 nm</em><u>Verde</u></div><div><b>13 900</b><i style='height:82%;background:linear-gradient(180deg,{series[3]},{mix_hex(series[3],p["canvas"],.35)})'></i><s style='background:{series[3]}'></s><em>570 nm</em><u>Amarelo</u></div><div><b>11 300</b><i style='height:66%;background:linear-gradient(180deg,{series[4]},{mix_hex(series[4],p["canvas"],.35)})'></i><s style='background:{series[4]}'></s><em>600 nm</em><u>Laranja</u></div><div><b>7 840</b><i style='height:44%;background:linear-gradient(180deg,{series[5]},{mix_hex(series[5],p["canvas"],.35)})'></i><s style='background:{series[5]}'></s><em>650 nm</em><u>Vermelho</u></div></div>
<svg width=1100 height=420 style='position:absolute;left:0;top:0'><defs><linearGradient id=g x1=0 y1=0 x2=0 y2=1><stop offset=0 stop-color='{p["accent"]}' stop-opacity=.30 /><stop offset=1 stop-color='{p["accent"]}' stop-opacity=0 /></linearGradient></defs>
<polygon fill=url(#g) points='105,317 282,246 459,154 636,92 813,174 989,287 840,420 40,420'/>
<polyline fill=none stroke='{p["accent"]}' stroke-opacity=.25 stroke-width=8 points='105,317 282,246 459,154 636,92 813,174 989,287'/>
<polyline fill=none stroke='{p["heading"]}' stroke-width=2.6 points='105,317 282,246 459,154 636,92 813,174 989,287'/>
<circle cx=105 cy=317 r=5 fill='{series[0]}' stroke='{p["surface"]}' stroke-width=2 /><circle cx=282 cy=246 r=5 fill='{series[1]}' stroke='{p["surface"]}' stroke-width=2 /><circle cx=459 cy=154 r=5 fill='{series[2]}' stroke='{p["surface"]}' stroke-width=2 /><circle cx=636 cy=92 r=5 fill='{series[3]}' stroke='{p["surface"]}' stroke-width=2 /><circle cx=813 cy=174 r=5 fill='{series[4]}' stroke='{p["surface"]}' stroke-width=2 /><circle cx=989 cy=287 r=5 fill='{series[5]}' stroke='{p["surface"]}' stroke-width=2 />
</svg></div>
<div class=ind><div class=face><div class=mouth></div></div><h4>Leitura com repetibilidade</h4><p>Lendo o espectro. Seis bandas do infravermelho próximo em ação.</p><div class=steps><i style='background:{series[0]}'></i><i style='background:{series[1]}'></i><i style='background:{series[2]}'></i><i></i><i></i><small>Etapa 3 de 5</small></div></div></div></div>
<div class='panel foot'><span>Status: pronto para a próxima amostra.</span><span class=cred>Protótipo desenvolvido por Davi Baracat, <b>Kauê Carvalho</b> (github.com/indiolibanes) e <b>Mateus Ferreira</b> (github.com/yosemate)</span></div>
</body>"""


def dialog_page(p, series, texture, arrow, hand):
    """Tela de Configurações: Aparência e Acessibilidade em seções separadas."""
    head = page(p, series, texture, arrow, hand).split("<body>")[0]
    sel = f"background:{css(glass.tone_fill(p, 'gold'))};border-color:{glass.tone_border(p, 'gold', 'hover')};color:{p['heading']}"
    return head + f"""<style>
body{{width:720px;height:820px;padding:28px;gap:18px;background:{p['canvas']}}}
h1{{font:700 28px 'EB Garamond';color:{p['heading']}}}
.sect{{padding:22px 24px;display:flex;flex-direction:column;gap:12px;background:{css(glass.panel_fill(p))};border:1px solid {glass.rim(p)};border-radius:16px}}
.sect h2{{font:700 22px 'EB Garamond';color:{p['heading']}}} .sect p{{color:{p['muted']};font-size:14px;line-height:1.45}}
.pick{{display:grid;grid-template-columns:1fr 1fr;gap:12px}} .pick .btn{{padding:16px;text-align:center;font-size:15px;line-height:1.4}}
.sel{{{sel}}} .cap{{color:{p['muted']};font-size:13px}}
.combo{{padding:11px 14px;border:1px solid {glass.rim(p)};border-radius:10px;background:{glass.field_fill(p)};font-size:14px}}
.done{{align-self:flex-end}}
</style><body><h1>Configurações</h1>
<div class=sect><h2>Aparência</h2><p>Tema da interface. A mudança é aplicada na hora e a escolha fica salva.</p>
<div class=pick><span class='btn sel'>Escuro<br>âmbar e ouro</span><span class=btn>Claro<br>branco e verde</span></div></div>
<div class=sect><h2>Acessibilidade</h2><p>Recursos para uso com o dedo, em telas pequenas e para quem prefere menos movimento.</p>
<span class=cap>Teclado na tela (touchscreen)</span><div class=combo>Ligado: abre ao tocar em um campo</div>
<p>O campo de IP abre um teclado numérico e a porta, só de dígitos. Os demais campos abrem o teclado completo, com acentos.</p>
<span class=cap>Animações</span><div class=combo>Completas: molas, entradas e transições</div></div>
<span class='btn t-gold done'>Concluir</span></body>"""


async def shoot(items, out_dir):
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(executable_path="/opt/pw-browsers/chromium", args=["--allow-file-access-from-files"])
        for name, html, size in items:
            tmp = out_dir / f".{name}.html"
            tmp.write_text(html, encoding="utf-8")
            tab = await browser.new_page(viewport={"width": size[0], "height": size[1]})
            await tab.goto(tmp.as_uri())
            await tab.wait_for_timeout(500)
            await tab.screenshot(path=str(out_dir / f"especime-{name}.png"))
            tmp.unlink()
        await browser.close()


def main():
    out = ROOT / "docs" / "img"
    out.mkdir(parents=True, exist_ok=True)
    pals, series = palettes()
    arrow = (ROOT / "assets/cursors/fibra-seta@2x.png").as_uri()
    hand = (ROOT / "assets/cursors/fibra-mao@2x.png").as_uri()
    wood = (ROOT / "assets/textures/madeira-escura.png").as_uri()
    pulp = (ROOT / "assets/textures/celulose-claro.png").as_uri()
    items = [("umber", page(pals["umber"], series["umber"], wood, arrow, hand), (1600, 1000)),
             ("claro", page(pals["light"], series["light"], pulp, arrow, hand), (1600, 1000)),
             ("config-umber", dialog_page(pals["umber"], series["umber"], wood, arrow, hand), (720, 820)),
             ("config-claro", dialog_page(pals["light"], series["light"], pulp, arrow, hand), (720, 820))]
    asyncio.run(shoot(items, out))
    print("espécimes em", out)


if __name__ == "__main__":
    main()
