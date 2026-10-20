"""Composição SCADA aprovada: controles à esquerda, bandas à direita, diagnóstico abaixo."""
from PyQt5.QtCore import Qt,QTimer,QSize
from PyQt5.QtGui import QColor,QPainter
from PyQt5.QtWidgets import (QWidget,QFrame,QLabel,QPushButton,QVBoxLayout,QHBoxLayout,QGridLayout,
                             QSplitter,QDialog,QSizePolicy)
import typography as ty
from animation_math import mix_hex
from analysis_indicator import AnalysisIndicator
from brand_assets import institutional_signature
from diagnostics import ControllerDiagnosticsCard
from responsive_layout import ScaledCanvasView
from version import __credits__

class CanvasRoot(QWidget):
    """Raiz do painel: cor de fundo do tema e, por baixo dos cartões, a textura de fibras de celulose."""
    def paintEvent(self,event):
        from appearance import palette_for,texture_pixmap
        painter=QPainter(self)
        painter.fillRect(self.rect(),QColor(palette_for()['canvas']))
        tile=texture_pixmap()
        if not tile.isNull():painter.drawTiledPixmap(self.rect(),tile)
        painter.end()

def panel():
    box=QFrame();box.setObjectName('scadaPanel');return box

def label(text,role='body',muted=False,name=None):
    """Rótulo com um papel tipográfico (ver typography.ROLES). 'muted' usa a cor secundária do tema."""
    out=QLabel(text)
    out.setStyleSheet(('color: #9CA3AF; ' if muted else '')+ty.qss(role))
    if name:out.setObjectName(name)
    return out

def open_login(window):
    if window.authenticated_user:
        window.logout_action();return
    from auth_dialogs import DialogLogin
    dialog=DialogLogin(window.auth_manager,window)
    if dialog.exec_()==QDialog.Accepted and dialog.usuario_logado:
        window.authenticated_user=dialog.usuario_logado
        window.is_manual_mode_unlocked=True
        window.current_operator_name=dialog.usuario_logado.get('username','Operador')
        window.log_message('Sessão autenticada: '+window.current_operator_name)

def rgba(color,alpha):
    """'#RRGGBB' + opacidade de 0 a 1 -> 'rgba(r, g, b, N%)' para o QSS."""
    r,g,b=(int(color[i:i+2],16) for i in (1,3,5))
    return f"rgba({r}, {g}, {b}, {round(alpha*100)}%)"

def dashboard_style(p):
    """Folha de estilo do painel. Os gradientes e as cores de destaque saem da paleta do tema."""
    g=lambda top,bottom:f"qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 {top},stop:1 {bottom})"
    accent=p['accent_strong']
    rest=g(mix_hex(accent,'#FFFFFF',.10),mix_hex(accent,'#000000',.14))
    hover=g(mix_hex(accent,'#FFFFFF',.20),mix_hex(accent,'#000000',.06))
    hot=g(mix_hex(accent,'#FFFFFF',.38),accent)
    busy=g(mix_hex(p['soft'],accent,.34),mix_hex(p['soft'],accent,.20))
    danger_hot=g(mix_hex(p['danger_strong'],'#FFFFFF',.25),p['danger_strong'])
    result_border=mix_hex(p['border'],p['accent'],.40)
    return f'''QWidget#centralWidget {{color:{p['text']};}}
QLabel#brandTitle,QLabel#kappaValue {{color:{p['accent']};}}
QFrame#scadaPanel {{background:{rgba(p['surface'],.92)};border:1px solid {p['border']};border-radius:14px;}}
QFrame[compact="true"] QPushButton {{padding:8px 10px;}}
QFrame#scadaResult {{background:{rgba(p['soft'],.94)};border:1px solid {result_border};border-radius:14px;}}
QPushButton {{background:{g(p['soft'],p['surface'])};color:{p['text']};border:1px solid {p['border']};border-radius:8px;padding:9px 14px;{ty.qss('card')}}}
QPushButton:hover {{border:1px solid {p['accent']};}}
QPushButton:pressed {{background:{hot};color:{p['on_strong']};border:1px solid {accent};}}
QPushButton:disabled {{color:{p['disabled']};background:{p['canvas']};border:1px solid {p['border']};}}
QPushButton#scadaPrimary {{background:{rest};color:{p['on_strong']};border:0;padding:12px 16px;{ty.qss('section')}}}
QPushButton#scadaPrimary:hover {{background:{hover};}}
QPushButton#scadaPrimary:pressed {{background:{hot};color:{p['on_strong']};}}
QPushButton#scadaPrimary:disabled {{background:{p['soft']};color:{p['disabled']};}}
QPushButton[fxBusy="true"]:disabled,QPushButton#scadaPrimary[fxBusy="true"]:disabled {{background:{busy};color:{p['accent']};border:1px solid {p['accent']};}}
QPushButton#scadaEmergency {{color:{p['danger']};border:1px solid {p['danger']};}}
QPushButton#scadaEmergency:pressed {{background:{danger_hot};color:{p['on_strong']};border:1px solid {p['danger_strong']};}}
QComboBox,QLineEdit {{background:{p['canvas']};color:{p['text']};border:1px solid {p['border']};border-radius:8px;padding:8px 12px;{ty.qss('body')}}}
QComboBox:focus,QLineEdit:focus {{border:1px solid {p['accent']};}}
QComboBox QAbstractItemView {{background:{p['surface']};color:{p['text']};selection-background-color:{p['soft']};}}
QProgressBar {{background:{p['soft']};border:0;border-radius:4px;color:{p['muted']};{ty.qss('caption')}}}
QProgressBar::chunk {{background:{g(mix_hex(accent,'#FFFFFF',.18),accent)};border-radius:4px;}}
QTextEdit {{background:{p['canvas']};color:{p['muted']};border:0;{ty.qss('data')}}}'''

def connect_busy_state(w):
    """Enquanto o ciclo roda, o botão que o iniciou mostra "Analisando…" com um brilho em movimento."""
    buttons={'AUTO':w.btn_start_scan,'REP':w.btn_repeatability,'CALIB':w.btn_calibrate}
    original={}
    w._last_run_button=w.btn_start_scan
    for button in buttons.values():
        button.clicked.connect(lambda _=False,b=button:setattr(w,'_last_run_button',b))
    def mark(button,busy):
        button.setProperty('fxBusy',busy)
        button.style().unpolish(button);button.style().polish(button);button.update()
    def sync(busy):
        state=str(getattr(w,'fsm_state','IDLE'))
        current=next((b for k,b in buttons.items() if state.startswith(k)),getattr(w,'_last_run_button',w.btn_start_scan))
        for button in buttons.values():
            if busy and button is current:
                original.setdefault(button,button.text());mark(button,True)
                if button is w.btn_start_scan:button.setText('Analisando…')
            elif button in original or button.property('fxBusy'):
                mark(button,False)
                if button in original:button.setText(original.pop(button))
    w.analysis_indicator.busyChanged.connect(sync)

def build_dashboard(w):
    root=CanvasRoot();root.setObjectName('centralWidget');root.main_win=w
    w.dashboard_content=root
    seeds=[w._create_topbar(),w._create_kpi_bar(),w._create_left_control_panel(),w._create_right_chart_panel(),w._create_footer()]
    # Mantém as páginas manuais existentes e suas conexões, sem recriar a lógica operacional.
    w._ui_seed_widgets=seeds
    for seed in seeds:seed.setParent(root);seed.hide()
    for seed in seeds:
        for widget in [seed,*seed.findChildren(QWidget)]:
            widget.setStyleSheet('');widget._theme_base_qss='';widget._theme_last_qss=''
    layout=QVBoxLayout(root);layout.setContentsMargins(20,16,20,16);layout.setSpacing(14)
    top=panel();top.setProperty('compact',True);w.topbar=top;row=QHBoxLayout(top);row.setContentsMargins(18,12,18,12);row.setSpacing(9)
    brand=QWidget();bl=QVBoxLayout(brand);bl.setContentsMargins(0,0,20,0);bl.setSpacing(1)
    bl.addWidget(label('SpectrumLab Pro','title',name='brandTitle'));bl.addWidget(label('Supervisório NIR','caption',True));row.addWidget(brand)
    row.addWidget(w.combo_conn_mode)
    # Conserva os containers utilizados pela troca USB/Bluetooth/Wi-Fi.
    for item in w.widget_serial.findChildren(QLabel):item.hide()
    w.combo_com.setMaximumWidth(120);w.btn_refresh_ports.setText('↻')
    row.addWidget(w.widget_serial);row.addWidget(w.widget_wifi);row.addWidget(w.btn_connect)
    row.addWidget(w.badge_com);row.addStretch()
    manual=next(b for b in seeds[0].findChildren(QPushButton) if 'Atuadores' in b.text())
    manual.setText('Modo manual');manual.setMinimumWidth(115);row.addWidget(manual)
    w.btn_top_emergency.setText('Parada de emergência');w.btn_top_emergency.setObjectName('scadaEmergency')
    row.addWidget(w.btn_top_emergency)
    w.btn_login=QPushButton('Login');w.btn_login.clicked.connect(lambda:open_login(w));row.addWidget(w.btn_login)
    row.addWidget(w.btn_settings);layout.addWidget(top)
    w.kpi_bar=seeds[1]
    for card in (w.kpi_energy,w.kpi_peak,w.kpi_ratio_cel,w.kpi_ratio_water):
        card.setObjectName('scadaPanel');card.layout().setContentsMargins(18,12,18,12);card.layout().setSpacing(2)
        card.lbl_title.setStyleSheet('color: #9CA3AF; '+ty.qss('card'))
        card.lbl_value.setStyleSheet('color: #FFFFFF; '+ty.qss('kpi'))
        card.lbl_sub.setStyleSheet('color: #9CA3AF; '+ty.qss('caption'))
    w.kpi_ratio_cel.lbl_title.setText('Razão R680 / R730');w.kpi_ratio_water.lbl_title.setText('Razão R860 / R760')
    layout.addWidget(w.kpi_bar)
    w.kpi_bar.show()
    w.dashboard_splitter=QSplitter(Qt.Horizontal);w.dashboard_splitter.setChildrenCollapsible(False);w.dashboard_splitter.setHandleWidth(16)
    left=QWidget();w.left_panel=left;ll=QVBoxLayout(left);ll.setContentsMargins(0,0,0,0);ll.setSpacing(12)
    controls=panel();cl=QVBoxLayout(controls);cl.setContentsMargins(16,14,16,14);cl.setSpacing(10)
    cl.addWidget(label('Método analítico','label',True));cl.addWidget(w.combo_op_mode)
    cl.addWidget(label('Ensaios automáticos','section'))
    w.btn_start_scan.setText('Realizar leitura');w.btn_start_scan.setObjectName('scadaPrimary')
    w.btn_repeatability.setText('Leitura com repetibilidade · 5×')
    w.btn_calibrate.setText('Calibrar · Branco e escuro')
    for button in (w.btn_start_scan,w.btn_repeatability,w.btn_calibrate):cl.addWidget(button)
    ll.addWidget(controls)
    w.card_housing.setObjectName('scadaPanel')
    ll.addWidget(w.card_housing)
    w.card_calibracao.setObjectName('scadaPanel');w.card_calibracao.layout().setSpacing(5)
    ll.addWidget(w.card_calibracao)
    w.card_resultado.setObjectName('scadaResult')
    w.lbl_kappa_valor.setObjectName('kappaValue');w.lbl_kappa_valor.setStyleSheet(ty.qss('hero'))
    w.lbl_metodo_info.setWordWrap(True);w.lbl_kappa_classificacao.setWordWrap(True)
    ll.addWidget(w.card_resultado)
    buttons=QHBoxLayout();buttons.setSpacing(8)
    for button,text in ((w.btn_history,'Histórico'),(w.btn_pdf,'PDF'),(w.btn_csv,'CSV')):
        button.setText(text);button.setMinimumWidth(0);buttons.addWidget(button)
    ll.addLayout(buttons);ll.addStretch(1)
    right=panel();w.right_panel=right;rl=QVBoxLayout(right);rl.setContentsMargins(14,12,14,12)
    rl.setSpacing(10);rl.addWidget(w.spectral_chart,1)
    w.analysis_indicator=AnalysisIndicator(lambda:getattr(w,'fsm_state','IDLE'));rl.addWidget(w.analysis_indicator)
    connect_busy_state(w)
    w.dashboard_splitter.addWidget(left);w.dashboard_splitter.addWidget(right)
    w.dashboard_splitter.setStretchFactor(0,0);w.dashboard_splitter.setStretchFactor(1,1)
    w.dashboard_splitter.setSizes([420,1120]);layout.addWidget(w.dashboard_splitter,1)
    w.card_esp32=ControllerDiagnosticsCard(w)
    diagnostics=QWidget();dg=QGridLayout(diagnostics);dg.setContentsMargins(0,0,0,0);dg.setSpacing(16)
    dg.addWidget(w.card_esp32,0,0);dg.addWidget(w.card_telemetria,0,1);dg.setColumnStretch(0,4);dg.setColumnStretch(1,7)
    w.diagnostic_grid=dg;layout.addWidget(diagnostics)
    footer=panel();w.footer=footer;fl=QVBoxLayout(footer);fl.setContentsMargins(14,9,14,9);fl.setSpacing(5)
    fr=QHBoxLayout();w.lbl_cycle_status.setWordWrap(True);fr.addWidget(w.lbl_cycle_status,1)
    w.cycle_progress.setMaximumWidth(180);fr.addWidget(w.cycle_progress)
    w.btn_console=QPushButton('Console de telemetria');w.btn_console.setCheckable(True)
    w.btn_console.toggled.connect(w.txt_console.setVisible);fr.addWidget(w.btn_console)
    fr.addWidget(institutional_signature());fl.addLayout(fr)
    credits=label(__credits__,'caption',True,'credits');credits.setAlignment(Qt.AlignRight|Qt.AlignVCenter);fl.addWidget(credits)
    w.txt_console.hide();fl.addWidget(w.txt_console)
    layout.addWidget(footer)
    root._scada_style_factory=dashboard_style
    w.canvas_view=ScaledCanvasView(root,QSize(1600,1000),w);w.setCentralWidget(w.canvas_view)
    w._scada_refresh_timer=QTimer(w)
    def refresh():
        w.card_esp32.refresh(w)
        w.btn_login.setText('Sair · '+w.authenticated_user.get('username','Operador') if w.authenticated_user else 'Login')
        card=w.card_telemetria
        if card.last_received and __import__('time').monotonic()-card.last_received>10:card.reset('Telemetria desatualizada')
    w._scada_refresh_timer.timeout.connect(refresh);w._scada_refresh_timer.start(1000);refresh()
    w._responsive_ready=True
    # As páginas manuais e o badge são os únicos controles ocultos necessários.
    # Descarta os containers de construção depois de transferir seus filhos ativos.
    w.control_tabs.setParent(root);w.control_tabs.hide()
    w.badge_calib.setParent(root);w.badge_calib.hide()
    w.btn_emergency_auto=w.btn_top_emergency
    for seed in (seeds[0],seeds[2],seeds[3],seeds[4]):
        seed.setParent(None);seed.deleteLater()
    w._ui_seed_widgets=[w.kpi_bar]
    for widget in (w,root,*root.findChildren(QWidget)):w.theme_manager.apply_widget(widget)
    QTimer.singleShot(0,w._adapt_interface)
