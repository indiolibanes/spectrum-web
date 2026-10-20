"""Temas persistentes para widgets, estilos dinâmicos e gráficos."""
import json,os,re,tempfile,weakref
from pathlib import Path
from PyQt5 import sip
from PyQt5.QtCore import QObject,QEvent,QTimer,Qt
from PyQt5.QtGui import QColor,QPalette,QPixmap
from PyQt5.QtWidgets import (QApplication,QWidget,QLabel,QPushButton,QComboBox,QDialog,QButtonGroup,
                             QVBoxLayout,QHBoxLayout,QFrame,QTabWidget,QMenu)
from popup_design import popup_owner, popup_stylesheet
from typography import normalize_qss, install as install_typography
PALETTES={
 # Escuro: preto AMOLED sóbrio (fundo #000000, sem textura) com o dourado como destaque.
 # Texto em contraste alto (revisão de legibilidade): texto 18:1, secundário 12:1 sobre o fundo.
 "umber":{"canvas":"#000000","surface":"#17140E","soft":"#221E15","border":"#5A5342",
          "text":"#F8F4EA","heading":"#FFF3BF","muted":"#DDD5C0","disabled":"#8A836C","accent":"#E8C96A",
          "positive":"#9AD68F","warning":"#F0A965","danger":"#F58B7E",
          "sky":"#7CC4F2","violet":"#B9A2F2","rose":"#F29BB8",
          "accent_strong":"#E8C96A","positive_strong":"#8FD08A","danger_strong":"#EE9187","on_strong":"#2B2200"},
 # Claro: branco e verde. O matiz (~92 graus) vem das colinas do logo do Projeto Sucuriú.
 "light":{"canvas":"#F6F9F3","surface":"#FFFFFF","soft":"#EAF1E4","border":"#B9C6AE",
          "text":"#142009","heading":"#1B2E10","muted":"#44523A","disabled":"#7E8873","accent":"#436722",
          "positive":"#266435","warning":"#8A5A00","danger":"#B3261E",
          "sky":"#1F6FA8","violet":"#6A4BC2","rose":"#B03A6B",
          "accent_strong":"#436722","positive_strong":"#266435","danger_strong":"#B3261E","on_strong":"#FFFFFF"},
}
# Cores por série (bandas espectrais), em ordem fixa. Validadas com o validador de paletas
# (diferença para daltonismo e contraste sobre a superfície) nos dois temas.
SERIES={
 "umber":["#3987E5","#D95926","#199E70","#C98500","#D55181","#9085E9"],
 "light":["#2A78D6","#EB6834","#1BAF7A","#EDA100","#E87BA4","#6250D6"],
}
DEFAULT_THEME="umber"
LEGACY_THEMES={"dark":"umber","gold":"umber"}   # preferências salvas por versões anteriores
THEME_LABELS={"umber":"Escuro · preto e dourado","light":"Claro · branco e verde"}
TEXTURE_FILES={"light":"celulose-claro.png"}   # o Escuro é preto liso (AMOLED), sem textura
def texture_path(theme=None):
    """Textura do fundo da janela principal, ou None quando o tema não tem textura."""
    import sys
    name=TEXTURE_FILES.get(theme or current_theme())
    if name is None:return None
    base=Path(getattr(sys,"_MEIPASS",Path(__file__).resolve().parent))
    return base/"assets"/"textures"/name
_TEXTURE_CACHE={}
def texture_pixmap(theme=None):
    key=theme or current_theme()
    if key not in _TEXTURE_CACHE:
        path=texture_path(key)
        pix=QPixmap(str(path)) if path else QPixmap()   # QPixmap vazio: o chamador não desenha nada
        _TEXTURE_CACHE[key]=pix
    return _TEXTURE_CACHE[key]
def current_theme():
    app=QApplication.instance()
    return (app.property("spectrum_theme") or DEFAULT_THEME) if app else DEFAULT_THEME
def palette_for(theme=None):return PALETTES.get(theme or current_theme(),PALETTES[DEFAULT_THEME])
def series_colors(theme=None):return SERIES.get(theme or current_theme(),SERIES[DEFAULT_THEME])
def tone_for_hue(hue,p,strong=False):
    """Cor do tema para um matiz (0 a 1) de uma cor antiga: vermelho, laranja, verde, azul, violeta e rosa viram tons distintos."""
    if hue<0.08 or hue>=0.93:return p["danger_strong" if strong else "danger"]
    if hue<0.19:return p["warning"]
    if hue<0.47:return p["positive_strong" if strong else "positive"]
    if hue<0.60:return p["sky"]
    if hue<0.80:return p["violet"]
    return p["rose"]
def mapped_color(value,kind="text",theme=None):
    p=palette_for(theme);color=QColor(value)
    if not color.isValid():return value
    hue,saturation,lightness,_=color.getHslF()
    neutral=saturation<0.20 or hue<0
    if kind=="border":return p["border"]
    if kind=="surface":
        if neutral or (lightness<0.20 and 0.48<hue<0.72):
            return p["canvas"] if value.lower() in ("#202020","#0f172a","#18181b","#111B24") else p["surface"]
        if lightness<0.35:
            if hue<0.08 or hue>0.90:return "#FDECEA" if (theme or current_theme())=="light" else "#2A1512"
            return p["soft"]
        return tone_for_hue(hue,p,True)
    if neutral:
        if lightness>0.82:return p["text"]
        return p["disabled"] if lightness<0.38 else p["muted"]
    return tone_for_hue(hue,p)
def theme_color(value,kind="text"):return mapped_color(value,kind)

COLOR=re.compile(r"#[0-9a-fA-F]{6}\b")
DECL=re.compile(r"(background(?:-color)?|color|border(?:-(?:color|top|bottom|left|right))?)\s*:\s*([^;{}]+)(;|$)",re.I)
def transform_stylesheet(source,theme):
    def block(text):
        strong=False
        bg=re.search(r"background(?:-color)?\s*:\s*([^;]+)",text,re.I)
        if bg:
            colors=COLOR.findall(bg.group(1))
            strong=any(QColor(c).hslSaturationF()>0.4 and QColor(c).lightnessF()>0.30 for c in colors)
        def declaration(match):
            prop,value,end=match.groups()
            kind="surface" if prop.lower().startswith("background") else "border" if prop.lower().startswith("border") else "text"
            if prop.lower()=="color" and strong:
                # Texto sobre fundo forte: marrom escuro no tema umber, branco no tema claro.
                on_strong=palette_for(theme)["on_strong"]
                value=COLOR.sub(lambda m:on_strong if QColor(m[0]).lightnessF()>0.82 else mapped_color(m[0],kind,theme),value)
            else:value=COLOR.sub(lambda m:mapped_color(m[0],kind,theme),value)
            if kind=="surface" and "qlineargradient" in value:
                colors=COLOR.findall(value)
                if colors:value=colors[0]
            return f"{prop}: {value}{end}"
        return DECL.sub(declaration,text)
    if "{" not in source:return block(source)
    return re.sub(r"\{([^{}]*)\}",lambda m:"{"+block(m.group(1))+"}",source)

def preferences_path():
    base=os.environ.get("SPECTRUM_LAB_DATA_DIR")
    if not base:base=str(Path(os.environ.get("LOCALAPPDATA",str(Path.home()/".spectrum_lab")))/"SpectrumLabPro")
    return Path(base)/"interface.json"
def read_preferences(path):
    """Lê interface.json. Aceita o formato antigo (só o tema) e migra os temas escuros anteriores para o umber."""
    try:
        data=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,ValueError,TypeError,AttributeError):
        data={}
    if not isinstance(data,dict):data={}
    theme=data.get("theme")
    theme=LEGACY_THEMES.get(theme,theme)
    if theme not in PALETTES:theme=DEFAULT_THEME
    return {"theme":theme,"touch_keyboard":bool(data.get("touch_keyboard",True)),"reduce_motion":bool(data.get("reduce_motion",False))}
def read_preference(path):return read_preferences(path)["theme"]
def save_preferences(path,prefs):
    temporary=None
    try:
        path.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile("w",encoding="utf-8",dir=path.parent,delete=False) as handle:
            temporary=Path(handle.name);json.dump(prefs,handle);handle.flush();os.fsync(handle.fileno())
        os.replace(temporary,path);return True,""
    except OSError as exc:return False,str(exc)
    finally:
        if temporary and temporary.exists():temporary.unlink(missing_ok=True)
def save_preference(path,theme):
    prefs=read_preferences(path);prefs["theme"]=theme
    return save_preferences(path,prefs)

class ThemeManager(QObject):
    def __init__(self,app):
        super().__init__(app)
        self.app=app;self.applying=False;self.path=preferences_path();self.last_error=""
        self.prefs=read_preferences(self.path)
        self.theme=self.prefs["theme"]
        try:install_typography(app)
        except Exception:pass   # sem as fontes embutidas o programa usa as alternativas da pilha
        app.installEventFilter(self)
        from button_fx import ButtonFx
        from touch_keyboard import TouchKeyboardController
        self.button_fx=ButtonFx(app)
        from cursors import CursorController
        self.cursor_fx=CursorController(app)
        import motion
        motion.set_reduced(motion.reduced() or self.prefs["reduce_motion"])
        self.motion_fx=motion.MotionController(app)
        self.keyboard=TouchKeyboardController(app,self)
        self.keyboard.enabled=self.prefs["touch_keyboard"]
        self.set_theme(self.theme,False)
    @property
    def touch_keyboard(self):return self.keyboard.enabled
    def set_touch_keyboard(self,enabled):
        self.keyboard.enabled=bool(enabled);self.prefs["touch_keyboard"]=bool(enabled)
        if not enabled:self.keyboard.hide_keyboard()
        ok,self.last_error=save_preferences(self.path,self.prefs);return ok
    @property
    def reduce_motion(self):return bool(self.prefs.get("reduce_motion",False))
    def set_reduce_motion(self,enabled):
        import motion
        self.prefs["reduce_motion"]=bool(enabled);motion.set_reduced(bool(enabled))
        ok,self.last_error=save_preferences(self.path,self.prefs);return ok
    def refresh_preferences_path(self):
        path=preferences_path()
        if path!=self.path:
            self.path=path;self.prefs=read_preferences(path)
            self.keyboard.enabled=self.prefs["touch_keyboard"]
            self.set_theme(self.prefs["theme"],False)
    def eventFilter(self,obj,event):
        if isinstance(obj,QWidget) and not self.applying and event.type() in (QEvent.StyleChange,QEvent.Show):
            if not getattr(obj,"_theme_queued",False):
                obj._theme_queued=True
                ref=weakref.ref(obj)
                def apply_later():
                    widget=ref()
                    if widget is not None and not sip.isdeleted(widget):
                        widget._theme_queued=False;self.apply_widget(widget)
                QTimer.singleShot(0,apply_later)
        return False
    def apply_widget(self,widget):
        if sip.isdeleted(widget):return
        current=widget.styleSheet()
        if current!=getattr(widget,"_theme_last_qss",None):
            widget._theme_base_qss=current
        source=getattr(widget,"_theme_base_qss",current)
        # Evita que os estilos de caixas sejam herdados pelos rótulos internos.
        scoped=source
        if scoped:
            name=widget.objectName()
            if not name:
                name=f"themeWidget{id(widget)}";widget.setObjectName(name)
            if "{" not in scoped and re.search(r"(?:background|border)\s*[-:]",scoped):
                scoped=f"#{name} {{ {scoped} }}"
            scoped=re.sub(r"(?<![\w#])QFrame\s*\{",f"QFrame#{name} {{",scoped)
            if isinstance(widget,QLabel):
                scoped=re.sub(r"(?:background(?:-color)?|border(?:-(?:top|bottom|left|right|color))?)\s*:[^;{}]+;?","",scoped)
        factory=getattr(widget,"_scada_style_factory",None)
        rendered=factory(palette_for(self.theme)) if factory else transform_stylesheet(scoped,self.theme)
        in_popup = popup_owner(widget) is not None
        if in_popup:
            rendered = popup_stylesheet(widget, palette_for(self.theme), rendered)
        rendered=normalize_qss(rendered)
        widget._theme_last_qss=rendered
        previous=self.applying;self.applying=True
        try:
            if current!=rendered:widget.setStyleSheet(rendered)
            if isinstance(widget,(QLabel,QPushButton)) and not in_popup:
                text=widget.text()
                clean=re.sub(r"[\U0001F000-\U0001FAFF\u2300-\u23FF\u25B6\u2600-\u27BF\uFE0F\u200D]","",text).strip()
                if clean!=text:widget.setText(clean)
                if text and not clean and isinstance(widget,QLabel):widget.hide()
            if isinstance(widget,QComboBox) and not in_popup:
                for i in range(widget.count()):
                    text=widget.itemText(i)
                    clean=re.sub(r"[\U0001F000-\U0001FAFF\u2300-\u23FF\u25B6\u2600-\u27BF\uFE0F\u200D]","",text).strip()
                    if clean!=text:widget.setItemText(i,clean)
            if isinstance(widget,QTabWidget) and not in_popup:
                for i in range(widget.count()):
                    text=widget.tabText(i)
                    clean=re.sub(r"[\U0001F000-\U0001FAFF\u25B6\u2300-\u23FF\u2600-\u27BF\uFE0F\u200D]","",text).strip()
                    if clean!=text:widget.setTabText(i,clean)
            if isinstance(widget,QMenu):
                for action in widget.actions():
                    text=action.text()
                    clean=re.sub(r"[\U0001F000-\U0001FAFF\u25B6\u2300-\u23FF\u2600-\u27BF\uFE0F\u200D]","",text).strip()
                    if clean!=text:action.setText(clean)
            p=palette_for(self.theme)
            widget.setPalette(self.app.palette())
            if hasattr(widget,"setBackgroundBrush"):widget.setBackgroundBrush(QColor(p["canvas"]))
            widget.update()
        finally:self.applying=previous
    def set_theme(self,theme,persist=True):
        if theme not in PALETTES:raise ValueError("Tema inválido.")
        self.theme=theme;self.app.setProperty("spectrum_theme",theme)
        p=palette_for(theme);pal=QPalette()
        for role,key in ((QPalette.Window,"canvas"),(QPalette.WindowText,"text"),(QPalette.Base,"surface"),
                         (QPalette.AlternateBase,"soft"),(QPalette.Text,"text"),(QPalette.Button,"soft"),
                         (QPalette.ButtonText,"text"),(QPalette.Highlight,"accent"),
                         (QPalette.ToolTipBase,"surface"),(QPalette.ToolTipText,"text")):
            pal.setColor(role,QColor(p[key]))
        pal.setColor(QPalette.HighlightedText,QColor(p["on_strong"]))
        pal.setColor(QPalette.Link,QColor(p["accent"]));pal.setColor(QPalette.LinkVisited,QColor(p["violet"]))
        for role in (QPalette.Text,QPalette.WindowText,QPalette.ButtonText):
            pal.setColor(QPalette.Disabled,role,QColor(p["disabled"]))
        import motion
        fades=motion.begin_crossfade(self.app)   # sem janelas visíveis (ao iniciar) não faz nada
        self.applying=True
        try:self.app.setPalette(pal)
        finally:self.applying=False
        for widget in self.app.allWidgets():self.apply_widget(widget)
        motion.run_crossfade(fades)
        self.prefs["theme"]=theme
        if persist:
            ok,self.last_error=save_preferences(self.path,self.prefs);return ok
        return True

def ensure_theme_manager():
    app=QApplication.instance()
    manager=getattr(app,"_spectrum_themes",None)
    if manager is None:manager=ThemeManager(app);app._spectrum_themes=manager
    else:manager.refresh_preferences_path()
    return manager

class AppearanceDialog(QDialog):
    """Configurações, em duas seções separadas: Aparência (tema) e Acessibilidade (teclado na tela)."""
    def __init__(self,manager,parent=None):
        super().__init__(parent)
        self.manager=manager
        self.setWindowTitle("Configurações")
        self.resize(600,660)
        layout=QVBoxLayout(self);layout.setContentsMargins(26,24,26,22);layout.setSpacing(16)
        title=QLabel("Configurações");title.setProperty("role","heading")
        title.setStyleSheet("color: #FFFFFF; font-size: 24px; font-weight: 700; font-family: 'EB Garamond';")
        layout.addWidget(title)

        # ---- Aparência: tema claro ou escuro
        self.theme_buttons={}
        self.theme_group=QButtonGroup(self);self.theme_group.setExclusive(True)
        pickers=QHBoxLayout();pickers.setSpacing(12)
        for key,text in (("umber","Escuro\npreto e dourado"),("light","Claro\nbranco e verde")):
            button=QPushButton(text);button.setCheckable(True);button.setMinimumHeight(68)
            button.setProperty("fxTone","soft");button.setChecked(manager.theme==key)
            button.clicked.connect(lambda _=False,k=key:self.change_theme(k))
            self.theme_group.addButton(button);self.theme_buttons[key]=button;pickers.addWidget(button,1)
        theme_box=QWidget();theme_box.setLayout(pickers);pickers.setContentsMargins(0,0,0,0)
        layout.addWidget(self._section("Aparência","Tema da interface. A mudança é aplicada na hora e a escolha fica salva.",theme_box))

        # ---- Acessibilidade: teclado na tela para touchscreen
        access=QVBoxLayout();access.setSpacing(8);access.setContentsMargins(0,0,0,0)
        caption=QLabel("Teclado na tela (touchscreen)");caption.setStyleSheet("color: #9CA3AF; font-size: 12px;")
        access.addWidget(caption)
        self.keyboard_selector=QComboBox()
        self.keyboard_selector.addItem("Ligado: abre ao tocar em um campo",True)
        self.keyboard_selector.addItem("Desligado: usar o teclado do computador",False)
        self.keyboard_selector.setCurrentIndex(0 if manager.touch_keyboard else 1)
        self.keyboard_selector.setMinimumHeight(42)
        self.keyboard_selector.currentIndexChanged.connect(self.change_keyboard)
        access.addWidget(self.keyboard_selector)
        hint=QLabel("O campo de IP abre um teclado numérico e a porta, só de dígitos. Os demais campos abrem o teclado completo, com acentos.")
        hint.setWordWrap(True);hint.setStyleSheet("color: #9CA3AF; font-size: 12px;");access.addWidget(hint)
        motion_caption=QLabel("Animações");motion_caption.setStyleSheet("color: #9CA3AF; font-size: 12px;");access.addWidget(motion_caption)
        self.motion_selector=QComboBox()
        self.motion_selector.addItem("Completas: molas, entradas e transições",False)
        self.motion_selector.addItem("Reduzidas: só a troca de estado dos botões",True)
        self.motion_selector.setCurrentIndex(1 if manager.reduce_motion else 0)
        self.motion_selector.setMinimumHeight(42)
        self.motion_selector.currentIndexChanged.connect(self.change_motion)
        access.addWidget(self.motion_selector)
        access_box=QWidget();access_box.setLayout(access)
        layout.addWidget(self._section("Acessibilidade","Recursos para uso com o dedo, em telas pequenas e para quem prefere menos movimento.",access_box))

        self.feedback=QLabel("As alterações são aplicadas imediatamente.")
        self.feedback.setWordWrap(True);self.feedback.setStyleSheet("color: #9CA3AF; font-size: 12px;")
        layout.addWidget(self.feedback)
        layout.addStretch(1)
        row=QHBoxLayout();row.addStretch()
        close=QPushButton("Concluir");close.setObjectName("settingsDone");close.clicked.connect(self.accept);row.addWidget(close)
        layout.addLayout(row)
        for widget in (self,*self.findChildren(QWidget)):manager.apply_widget(widget)
    def _section(self,heading,description,content):
        """Cartão de uma seção: título em serifa, descrição e o conteúdo."""
        frame=QFrame();frame.setObjectName("settingsSection")
        box=QVBoxLayout(frame);box.setContentsMargins(20,16,20,18);box.setSpacing(10)
        head=QLabel(heading);head.setProperty("role","heading")
        head.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: 700; font-family: 'EB Garamond';")
        note=QLabel(description);note.setWordWrap(True);note.setStyleSheet("color: #9CA3AF; font-size: 14px;")
        box.addWidget(head);box.addWidget(note);box.addWidget(content)
        return frame
    def change_keyboard(self):
        ok=self.manager.set_touch_keyboard(self.keyboard_selector.currentData())
        self.feedback.setText("Preferência salva." if ok else "Aplicado nesta sessão. Não foi possível salvar a preferência.")
    def change_motion(self):
        ok=self.manager.set_reduce_motion(self.motion_selector.currentData())
        self.feedback.setText("Preferência salva." if ok else "Aplicado nesta sessão. Não foi possível salvar a preferência.")
    def change_theme(self,key=None):
        key=key or next((k for k,b in self.theme_buttons.items() if b.isChecked()),self.manager.theme)
        ok=self.manager.set_theme(key)
        for name,button in self.theme_buttons.items():button.setChecked(name==key)
        self.feedback.setText("Preferência salva." if ok else "Tema aplicado nesta sessão. Não foi possível salvar a preferência.")
