"""
Gera os espécimes de tema (docs/img/especime-*.png) em HTML + Chromium, a partir das MESMAS receitas
planas e das MESMAS paletas usadas pelo programa (glass.py e appearance.PALETTES).

É uma prévia fiel de cor, tipografia e proporção; não é uma captura do PyQt5.

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
    return value   # as receitas já são cores sólidas


def tone_css(p, tone):
    return (f"background:{css(glass.tone_fill(p, tone))};color:{glass.tone_text(p, tone)};border-color:{glass.tone_border(p, tone)}")


def page(p, series, texture, arrow, hand):
    f = ROOT.as_uri() + "/assets/fonts/"
    dark = glass.is_dark(p)
    glows = ",".join(
        f"radial-gradient(circle at {fx*100:.0f}% {fy*100:.0f}%,{glass.rgba(c, a)} 0,transparent {r*100:.0f}vmax)" for fx, fy, r, c, a in glass.glow_spec(p))
    accent = p["accent_strong"]
    return f"""<!doctype html><meta charset=utf-8><style>
@font-face{{font-family:'Inter';src:url('{f}Inter-Regular.ttf');font-weight:400}}
@font-face{{font-family:'Inter';src:url('{f}Inter-Bold.ttf');font-weight:700}}
@font-face{{font-family:'Dropline';src:url('{f}DroplineRegular.otf');font-weight:400}}
@font-face{{font-family:'Arena';src:url('{f}Arena.ttf');font-weight:400}}
@font-face{{font-family:'IBM Plex Mono';src:url('{f}IBMPlexMono-Regular.ttf');font-weight:400}}
*{{box-sizing:border-box;margin:0}}
body{{width:1600px;min-height:1000px;background:{glows},{p['canvas']};color:{p['text']};font:400 13px 'Inter';padding:16px 20px;display:flex;flex-direction:column;gap:14px;position:relative}}
.panel{{background:{css(glass.panel_fill(p))};border:1px solid {glass.rim(p)};border-radius:12px}}
.top{{display:flex;align-items:center;gap:14px;padding:12px 18px}}
.brand{{display:flex;align-items:center;gap:10px}} .brand img{{width:40px;height:40px}} .brand b{{display:block;font:400 24px 'Arena','Dropline';color:{p['heading']}}} .brand small{{color:{p['muted']};font-size:12px}}
.btn{{padding:10px 16px;border-radius:10px;border:1px solid {glass.rim(p)};background:{css(glass.button_fill(p))};color:{p['text']}}}
.btn.hover{{background:{css(glass.button_fill(p,'hover'))};border-color:{p['accent']}}}
.btn.pressed{{background:{css(glass.primary_fill(p,'hot'))};color:{p['on_strong']};border-color:{accent}}}
.btn.primary{{background:{css(glass.primary_fill(p))};color:{p['on_strong']};border-color:{accent};padding:13px 18px;font:700 15px 'Inter'}}
.btn.busy{{background:{glass.button_fill(p,'hover')};color:{p['heading']};border-color:{p['accent']};font:700 15px 'Inter'}}
.btn.danger{{color:{p['danger']};border-color:{p['danger']};background:{mix_hex(p['surface'],p['danger'],.2)}}}
input{{background:{glass.field_fill(p)};color:{p['text']};border:1px solid {p['accent']};border-radius:10px;padding:9px 13px;font:400 13px 'Inter';width:150px}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}} .kpi{{padding:8px 18px}}
.kpi .t{{color:{p['muted']}}} .kpi .v{{font:400 28px 'IBM Plex Mono'}} .kpi .s{{color:{p['muted']};font-size:11px}}
.main{{display:grid;grid-template-columns:420px 1fr;gap:16px;flex:1}}
.left{{display:flex;flex-direction:column;gap:12px}} .box{{padding:14px 16px;display:flex;flex-direction:column;gap:10px}}
.lbl{{color:{p['muted']};font-size:11px}} .sec{{font:400 20px 'Dropline';color:{p['heading']}}}
.result{{background:{css(glass.result_fill(p))};border:1px solid {glass.tone_border(p,'accent')};border-radius:12px;padding:14px 16px}}
.hero{{font:400 40px 'IBM Plex Mono';color:{p['accent']}}}
.chart{{padding:14px;display:flex;flex-direction:column;gap:10px}} .plot{{flex:1;border-radius:10px;position:relative;overflow:hidden;background:{glass.field_fill(p)}}}
.ind{{height:92px;background:{p['soft']};border:1px solid {glass.rim(p)};border-radius:10px;position:relative;padding:12px 16px 0 86px}}
.ind:before{{content:'';position:absolute;left:0;top:0;bottom:0;width:6px;background:{p['accent']};border-radius:3px}}
.face{{position:absolute;left:24px;top:24px;width:44px;height:44px;border-radius:50%;border:2px solid {p['accent']};background:{glass.rgba(p['accent'],.16)}}}
.face:before,.face:after{{content:'';position:absolute;top:15px;width:4px;height:4px;border-radius:50%;background:{p['accent']}}} .face:before{{left:11px}} .face:after{{right:11px}}
.mouth{{position:absolute;left:12px;top:22px;width:16px;height:9px;border-bottom:2.2px solid {p['accent']};border-radius:0 0 16px 16px}}
.ind h4{{font:400 20px 'Dropline';color:{p['heading']}}} .ind p{{color:{p['muted']};margin-top:4px;width:520px}}
.steps{{position:absolute;right:16px;top:58px;display:flex;gap:6px}} .steps i{{display:block;width:34px;height:6px;border-radius:3px;background:{p['border']}}} .steps i.on{{background:{p['accent']}}}
.steps small{{position:absolute;right:0;top:10px;color:{p['muted']};font-size:11px}}
.foot{{padding:9px 14px;display:flex;justify-content:space-between;align-items:center;color:{p['muted']}}} .cred{{font-size:11px}}
.kb{{position:absolute;right:40px;bottom:120px;width:440px;background:{p['canvas'] if dark else p['soft']};border:1px solid {glass.rim(p,1.2)};padding:10px 14px 14px;border-radius:14px}}
.kb .cap{{display:flex;justify-content:space-between;color:{p['muted']};font-size:11px;margin-bottom:8px}}
.kb .row{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:8px}}
.kb .k{{height:56px;border-radius:10px;border:1px solid {glass.rim(p,1.2)};background:{css(glass.button_fill(p))};display:flex;align-items:center;justify-content:center;font:400 19px 'IBM Plex Mono'}}
.kb .a{{color:{p['muted']};font:400 13px 'Inter'}} .kb .e{{background:{css(glass.primary_fill(p))};color:{p['on_strong']};border-color:{accent};font:700 15px 'Inter'}} .kb .p{{background:{css(glass.primary_fill(p,'hot'))};color:{p['on_strong']};border-color:{accent}}}
.cur{{position:absolute;width:32px;height:32px}}
.face{{background:radial-gradient(circle at 35% 30%,#FFF0A0,#FFD23F 55%,#F2A20C);border:1.5px solid rgba(140,80,0,.7)}} .face:before,.face:after{{background:#4A2B00}} .mouth{{border-bottom-color:#4A2B00}}
.btn{{font-size:14px}} .btn.t-accent{{{tone_css(p,'accent')}}}
.btn.t-secondary{{{tone_css(p,'secondary')}}}
.btn.t-sky{{{tone_css(p,'sky')}}}
.btn.t-indigo{{{tone_css(p,'indigo')}}}
.btn.t-rose{{{tone_css(p,'rose')}}}
.btn.t-green{{{tone_css(p,'green')}}}
.btn.t-slate{{{tone_css(p,'slate')}}}
.btn.t-sand{{{tone_css(p,'sand')}}}
.kpi{{display:flex;gap:14px;align-items:center;position:relative;overflow:hidden}} .kpi .ic{{width:40px;height:40px;border-radius:12px;display:flex;align-items:center;justify-content:center;font:700 18px 'Inter'}}
.kpi .bar{{position:absolute;left:0;top:14px;bottom:14px;width:4px;border-radius:2px}}
.lbl{{font-size:13px}} .kpi .t{{font-size:14px}} .kpi .s{{font-size:12px}}
.bars{{position:absolute;left:30px;right:30px;bottom:34px;top:30px;display:flex;gap:26px;align-items:flex-end}}
.bars div{{flex:1;display:flex;flex-direction:column;align-items:center;gap:6px;height:100%;justify-content:flex-end}}
.bars i{{display:block;width:100%;border-radius:8px 8px 0 0;opacity:.88}} .bars b{{font:400 14px 'IBM Plex Mono'}} .bars s{{text-decoration:none;display:block;width:24px;height:4px;border-radius:2px}} .bars em{{font:700 12px 'Inter';font-style:normal;color:{p['text']}}} .bars u{{text-decoration:none;font-size:12px;color:{p['muted']}}}
.foot{{padding:14px 20px;font-size:14px;border:1px solid {glass.tone_border(p,'accent')};background:{css(glass.result_fill(p))}}} .foot b{{font-weight:700;color:{p['accent']}}} .cred{{font-size:14px;color:{p['text']}}}
.comm{{padding:10px 18px;border-color:{glass.tone_border(p,'secondary')}}} .comm .g{{display:grid;grid-template-columns:auto 1fr auto 1fr;gap:6px 14px;margin-top:6px;color:{p['muted']};font-size:14px}} .comm .g b{{font:700 16px 'Inter';color:{p['text']}}}
.cal{{display:flex;flex-direction:column;gap:6px;font-size:14px}} .cal div{{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid {glass.rim(p,.5)}}} .cal span{{color:{p['muted']}}} .cal b{{font:400 16px 'IBM Plex Mono';color:{p['text']}}}
</style><body>
<div class='panel top'><div class=brand><img src='{ROOT.as_uri()}/assets/logo/spectrumlab-mark.svg'><div><b>SpectrumLab Pro</b><small>Supervisório NIR</small></div></div>
<span class=btn>Wi-Fi</span><span class=lbl>IP ESP32:</span><input value='192.168.4.1'><span class=lbl>Porta:</span><input value='8080' style='width:84px'>
<span class='btn t-sky'>Conectar ESP32</span><span style='flex:1'></span><span class='btn t-indigo'>Modo manual</span><span class='btn danger'>Parada de emergência</span><span class='btn t-slate'>Login</span><span class=btn>Configurações</span></div>
<div class=kpis>
<div class='panel kpi'><i class=bar style='background:{p["accent"]}'></i><div class=ic style='background:{glass.rgba(p["accent"],.2)};color:{p["accent"]}'>⚡</div><div><div class=t>Energia espectral</div><div class=v>12 480</div><div class=s>contagens</div></div></div>
<div class='panel kpi'><i class=bar style='background:{p["secondary"]}'></i><div class=ic style='background:{glass.rgba(p["secondary"],.2)};color:{p["secondary"]}'>↗</div><div><div class=t>Pico</div><div class=v>730 nm</div><div class=s>R730</div></div></div>
<div class='panel kpi'><i class=bar style='background:{p["positive"]}'></i><div class=ic style='background:{glass.rgba(p["positive"],.2)};color:{p["positive"]}'>❦</div><div><div class=t>Razão R680 / R730</div><div class=v>0,842</div><div class=s>celulose</div></div></div>
<div class='panel kpi'><i class=bar style='background:{p["sky"]}'></i><div class=ic style='background:{glass.rgba(p["sky"],.2)};color:{p["sky"]}'>💧</div><div><div class=t>Razão R860 / R760</div><div class=v>1,117</div><div class=s>água</div></div></div></div>
<div class=main><div class=left>
<div class='panel box'><span class=lbl>Método analítico</span><input value='Seco (placa)' style='width:100%'><span class=sec>Ensaios automáticos</span>
<span class='btn busy'>Analisando…</span><span class='btn t-secondary hover'>Leitura com repetibilidade · 5×</span><span class='btn t-rose'>Calibrar · Branco e escuro</span><span class='btn primary'>Realizar leitura</span></div>
<div class='panel box'><span class=sec>Calibração</span><div class=cal><div><span>R²</span><b>0,998</b></div><div><span>RMSE</span><b>± 0,214</b></div><div><span>Amostras (N)</span><b>12</b></div></div></div>
<div class=result><span class=lbl>Número kappa</span><div class=hero>18,4</div><div class=lbl style='margin-top:4px'>Classificação: polpa branqueável</div></div><div style='display:flex;gap:10px'><span class='btn t-sand' style='flex:1;text-align:center'>Histórico</span><span class='btn t-indigo' style='flex:1;text-align:center'>PDF</span><span class='btn t-green' style='flex:1;text-align:center'>CSV</span></div></div>
<div class='panel chart'><div class=plot><div class=bars><div><b>8 120</b><i style='height:38%;background:{series[0]}'></i><s style='background:{series[0]}'></s><em>450 nm</em><u>Azul</u></div><div><b>9 960</b><i style='height:52%;background:{series[1]}'></i><s style='background:{series[1]}'></s><em>500 nm</em><u>Ciano</u></div><div><b>12 480</b><i style='height:70%;background:{series[2]}'></i><s style='background:{series[2]}'></s><em>550 nm</em><u>Verde</u></div><div><b>13 900</b><i style='height:82%;background:{series[3]}'></i><s style='background:{series[3]}'></s><em>570 nm</em><u>Amarelo</u></div><div><b>11 300</b><i style='height:66%;background:{series[4]}'></i><s style='background:{series[4]}'></s><em>600 nm</em><u>Laranja</u></div><div><b>7 840</b><i style='height:44%;background:{series[5]}'></i><s style='background:{series[5]}'></s><em>650 nm</em><u>Vermelho</u></div></div>
<svg width=1100 height=420 style='position:absolute;left:0;top:0'>
<polyline fill=none stroke='{p["heading"]}' stroke-width=2.6 points='105,317 282,246 459,154 636,92 813,174 989,287'/>
<circle cx=105 cy=317 r=5 fill='{series[0]}' stroke='{p["surface"]}' stroke-width=2 /><circle cx=282 cy=246 r=5 fill='{series[1]}' stroke='{p["surface"]}' stroke-width=2 /><circle cx=459 cy=154 r=5 fill='{series[2]}' stroke='{p["surface"]}' stroke-width=2 /><circle cx=636 cy=92 r=5 fill='{series[3]}' stroke='{p["surface"]}' stroke-width=2 /><circle cx=813 cy=174 r=5 fill='{series[4]}' stroke='{p["surface"]}' stroke-width=2 /><circle cx=989 cy=287 r=5 fill='{series[5]}' stroke='{p["surface"]}' stroke-width=2 />
</svg></div>
<div class=ind><div class=face><div class=mouth></div></div><h4>Leitura com repetibilidade</h4><p>Lendo o espectro. Seis bandas do infravermelho próximo em ação.</p><div class=steps><i style='background:{series[0]}'></i><i style='background:{series[1]}'></i><i style='background:{series[2]}'></i><i></i><i></i><small>Etapa 3 de 5</small></div></div></div></div>
<div style='display:grid;grid-template-columns:4fr 7fr;gap:14px'><div class='panel comm'><b class=sec>ESP32 · Comunicação</b><div class=g><span>Conexão</span><b>Wi-Fi · 192.168.4.1</b><span>Protocolo</span><b>2 · confirmado</b><span>Heartbeat</span><b>0,4 s</b></div></div><div class='panel comm'><b class=sec>GY-AS7263 · Sensor espectral</b><div class=g><span>Temperatura interna</span><b>31 °C</b><span>Ganho</span><b>16×</b><span>Integração</span><b>50 ms</b></div></div></div>
<div class='panel foot'><span>Status: pronto para a próxima amostra.</span><span class=cred>Protótipo desenvolvido por <b>Davi Baracat</b> (@DaviBaracat), <b>Kauê Alencar</b> (@indiolibanes) e <b>Mateus Ferreira</b> (@yosemate)</span></div>
</body>"""


def dialog_page(p, series, texture, arrow, hand):
    """Tela de Configurações: Aparência e Acessibilidade em seções separadas."""
    head = page(p, series, texture, arrow, hand).split("<body>")[0]
    sel = f"background:{css(glass.tone_fill(p, 'accent'))};border-color:{glass.tone_border(p, 'accent', 'hover')};color:{p['heading']}"
    return head + f"""<style>
body{{width:720px;height:820px;padding:28px;gap:18px;background:{p['canvas']}}}
h1{{font:400 28px 'Dropline';color:{p['heading']}}}
.sect{{padding:22px 24px;display:flex;flex-direction:column;gap:12px;background:{css(glass.panel_fill(p))};border:1px solid {glass.rim(p)};border-radius:12px}}
.sect h2{{font:400 22px 'Dropline';color:{p['heading']}}} .sect p{{color:{p['muted']};font-size:14px;line-height:1.45}}
.pick{{display:grid;grid-template-columns:1fr 1fr;gap:12px}} .pick .btn{{padding:16px;text-align:center;font-size:15px;line-height:1.4}}
.sel{{{sel}}} .cap{{color:{p['muted']};font-size:13px}}
.combo{{padding:11px 14px;border:1px solid {glass.rim(p)};border-radius:10px;background:{glass.field_fill(p)};font-size:14px}}
.done{{align-self:flex-end}}
</style><body><h1>Configurações</h1>
<div class=sect><h2>Aparência</h2><p>Tema da interface. A mudança é aplicada na hora e a escolha fica salva.</p>
<div class=pick><span class='btn sel'>Noturno<br>roxo e dourado</span><span class=btn>Claro<br>branco e verde</span></div></div>
<div class=sect><h2>Acessibilidade</h2><p>Recursos para uso com o dedo, em telas pequenas e para quem prefere menos movimento.</p>
<span class=cap>Teclado na tela</span><div class=combo>Automático: só em aparelhos com tela de toque</div>
<p>Neste aparelho: nenhuma tela de toque detectada. O campo de IP abre um teclado numérico e a porta, só de dígitos. Os demais campos abrem o teclado completo, com acentos.</p>
<span class=cap>Animações</span><div class=combo>Completas: molas, entradas e transições</div></div>
<span class='btn t-accent done'>Concluir</span></body>"""


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
            await tab.screenshot(path=str(out_dir / f"especime-{name}.png"), full_page=True)
            tmp.unlink()
        await browser.close()


def main():
    out = ROOT / "docs" / "img"
    out.mkdir(parents=True, exist_ok=True)
    pals, series = palettes()
    arrow = (ROOT / "assets/cursors/fibra-seta@2x.png").as_uri()
    hand = (ROOT / "assets/cursors/fibra-mao@2x.png").as_uri()
    items = [("noturno", page(pals["noturno"], series["noturno"], None, arrow, hand), (1600, 1000)),
             ("claro", page(pals["light"], series["light"], None, arrow, hand), (1600, 1000)),
             ("config-noturno", dialog_page(pals["noturno"], series["noturno"], None, arrow, hand), (720, 820)),
             ("config-claro", dialog_page(pals["light"], series["light"], None, arrow, hand), (720, 820))]
    asyncio.run(shoot(items, out))
    print("espécimes em", out)


if __name__ == "__main__":
    main()
