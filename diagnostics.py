"""Diagnóstico sem valores nominais apresentados como medições reais."""
import math,time
from PyQt5.QtCore import Qt,QRectF,QSize
from PyQt5.QtGui import QColor,QPainter,QFontMetrics
from PyQt5.QtWidgets import QFrame,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel
import kpi_status as ks
import typography as ty

def _title(text):
    out=QLabel(text);out.setProperty('role','heading');out.setStyleSheet(ty.qss('card','font-weight: 700;'));return out

class TemperatureLabel(QLabel):
    """Temperatura com um marcador de cor pelo nível (ISA-101: a cor só informa o estado).

    Frio = azul, normal = verde, quente = âmbar, alarme = vermelho, sem dado = cinza (kpi_status.temperature_level).
    O texto continua legível sem a cor: o nível também aparece por extenso na dica.
    """
    DOT=10
    def __init__(self,kind,parent=None):
        super().__init__('—',parent);self.kind=kind;self._level=ks.NONE
        self.setStyleSheet(ty.qss('data','font-weight: 700;'))
    def set_celsius(self,celsius):
        """Define o nível a partir de um valor em °C (ou None quando não há medição)."""
        self._level=ks.temperature_level(self.kind,celsius)
        self.setToolTip('Temperatura: '+ks.THERMAL_LABEL[self._level]);self.update()
    @property
    def level(self):return self._level
    def sizeHint(self):
        base=QFontMetrics(self.font()).boundingRect(self.text()).width()
        return QSize(base+self.DOT+14,max(20,QFontMetrics(self.font()).height()+2))
    def minimumSizeHint(self):return self.sizeHint()
    def paintEvent(self,event):
        from appearance import palette_for
        pal=palette_for();painter=QPainter(self);painter.setRenderHint(QPainter.Antialiasing);painter.setRenderHint(QPainter.TextAntialiasing)
        color=QColor(pal[ks.THERMAL_COLOR_KEY[self._level]]);h=self.height()
        painter.setPen(Qt.NoPen);painter.setBrush(color)
        painter.drawEllipse(QRectF(1,(h-self.DOT)/2,self.DOT,self.DOT))
        painter.setFont(self.font());painter.setPen(QColor(pal['heading']))
        painter.drawText(QRectF(self.DOT+8,0,self.width()-self.DOT-8,h),Qt.AlignLeft|Qt.AlignVCenter,self.text())
        painter.end()

def _caption(text):
    out=QLabel(text);out.setStyleSheet('color: #9CA3AF; '+ty.qss('caption'));return out

def _value(text='—'):
    out=QLabel(text);out.setStyleSheet(ty.qss('data'));return out

class SensorDiagnosticsCard(QFrame):
    def __init__(self,parent=None):
        super().__init__(parent);self.setObjectName('scadaPanel');self.setProperty('priority','high');self.last_received=None
        layout=QVBoxLayout(self);layout.setContentsMargins(12,8,12,8);layout.setSpacing(4)
        row=QHBoxLayout();row.addWidget(_title('GY-AS7263 · Sensor espectral'));row.addStretch()
        self.lbl_status_badge=QLabel('Aguardando telemetria');self.lbl_status_badge.setStyleSheet('color: #9CA3AF; '+ty.qss('caption'))
        row.addWidget(self.lbl_status_badge);layout.addLayout(row)
        grid=QGridLayout();grid.setHorizontalSpacing(12);grid.setVerticalSpacing(2);layout.addLayout(grid)
        fields=[('Temperatura interna','lbl_die_temp'),('Ganho configurado','lbl_ganho'),
                ('Integração configurada','lbl_integracao'),('Corrente LED configurada','lbl_driver_led'),
                ('Estado reportado do LED','lbl_led_state'),('Modelo declarado','lbl_hardware'),
                ('Saturação nas contagens','lbl_sat'),('Irradiância absoluta','lbl_irrad'),
                ('Firmware do chip','lbl_chip_firmware')]
        for i,(title,name) in enumerate(fields):
            caption=_caption(title)
            value=TemperatureLabel('sensor') if name=='lbl_die_temp' else _value();setattr(self,name,value)
            row,col=divmod(i,3);grid.addWidget(caption,row,col*2);grid.addWidget(value,row,col*2+1)
        self.lbl_status_sensor=QLabel('Aguardando telemetria');self.lbl_status_sensor.hide()
        for alias,name in [('temp','die_temp'),('gain','ganho'),('integration','integracao'),('led','driver_led'),
                           ('irrad','irrad'),('hw','hardware'),('status','status_sensor'),('sat','sat')]:
            setattr(self,'lbl_val_'+alias,getattr(self,'lbl_'+name))
        self.reset()

    def refresh_freshness(self,busy=False):
        if self.last_received is None:return
        age=max(0,time.monotonic()-self.last_received)
        if busy:message=f'Atualização pausada · último diagnóstico há {age:.0f} s'
        elif age>10:message=f'Telemetria desatualizada · último diagnóstico há {age:.0f} s'
        else:message=f'Diagnóstico recebido há {age:.0f} s'
        self.lbl_status_badge.setText(message)
        self.setToolTip(message+'; os valores de diagnóstico são os últimos recebidos.')

    def reset(self,message='Aguardando telemetria'):
        self.last_received=None
        for name in ('die_temp','ganho','integracao','driver_led','led_state','hardware','sat'):
            getattr(self,'lbl_'+name).setText('—')
        self.lbl_die_temp.set_celsius(None)
        self.lbl_irrad.setText('Não disponível');self.lbl_chip_firmware.setText('Não consultado')
        self.lbl_status_sensor.setText(message);self.lbl_status_badge.setText(message)

    def atualizar_telemetria(self,die_temp=None,gain=None,integration=None,led=None,
                            irradiance=None,hw_id=None,status=None,saturation=None,led_state=None,received=False):
        if received:self.last_received=time.monotonic()
        if die_temp is not None:
            try:
                temp=float(str(die_temp).replace('TEMP:','').replace('°C','').strip())
                valid=math.isfinite(temp) and -40<=temp<=125
                self.lbl_die_temp.setText(f'{temp:.1f} °C' if valid else 'Indisponível')
                self.lbl_die_temp.set_celsius(temp if valid else None)
            except (ValueError,TypeError):
                self.lbl_die_temp.setText('Indisponível');self.lbl_die_temp.set_celsius(None)
        for value,name in ((gain,'ganho'),(integration,'integracao'),(hw_id,'hardware')):
            if value is not None:getattr(self,'lbl_'+name).setText(str(value).replace('_',' '))
        if led is not None:
            value=str(led).replace('Ativo (','').rstrip(')')
            if value.upper() not in ('OFF','ON','DESLIGADO','LIGADO'):
                self.lbl_driver_led.setText(value)
            else:led_state=value
        if led_state is not None:
            value=str(led_state).upper()
            self.lbl_led_state.setText({'ON':'Ligado','OFF':'Desligado','LIGADO':'Ligado','DESLIGADO':'Desligado'}.get(value,'Não informado'))
        if irradiance is not None:self.lbl_irrad.setText('Não validada')
        if status is not None:
            self.lbl_status_sensor.setText(str(status));self.lbl_status_badge.setText(str(status))
        if saturation is not None:
            value=saturation if isinstance(saturation,bool) else str(saturation).lower() in ('1','true','sim')
            self.lbl_sat.setText('Detectada' if value else 'Não detectada')

class ControllerDiagnosticsCard(QFrame):
    def __init__(self,parent=None):
        super().__init__(parent);self.setObjectName('scadaPanel');self.setProperty('priority','high')
        layout=QVBoxLayout(self);layout.setContentsMargins(12,8,12,8);layout.setSpacing(4)
        layout.addWidget(_title('ESP32 · Comunicação'))
        self.values={};grid=QGridLayout();grid.setHorizontalSpacing(12);grid.setVerticalSpacing(2);layout.addLayout(grid)
        for i,(key,title) in enumerate([('connection','Conexão'),('protocol','Protocolo'),('heartbeat','Heartbeat'),
                                       ('baud','Velocidade USB'),('resources','CPU / memória'),('temp','Temperatura ESP32')]):
            row,col=divmod(i,2);label=_caption(title)
            value=TemperatureLabel('esp32') if key=='temp' else _value();self.values[key]=value
            grid.addWidget(label,row,col*2);grid.addWidget(value,row,col*2+1)
        self.values['resources'].setText('Não enviados');self.values['temp'].setText('Não enviada')

    def refresh(self,window):
        connected=window.is_serial_connected()
        if not connected:
            self.values['resources'].setText('Não enviados')
            self.values['temp'].setText('Não enviada');self.values['temp'].set_celsius(None)
        mode=window.combo_conn_mode.currentData()
        target=window.txt_ip.text() if mode=='WIFI' else window.combo_com.currentText()
        self.values['connection'].setText(f'{mode} · {target}' if connected else 'Desconectado')
        self.values['protocol'].setText('2 · confirmado' if connected and window._protocol_ready else 'Aguardando')
        age=max(0,time.monotonic()-window._last_pong)
        self.values['heartbeat'].setText(f'Última resposta: {age:.1f} s' if connected and window._protocol_ready else 'Sem confirmação')
        self.values['baud'].setText('115.200 baud' if mode in ('USB','BLUETOOTH') else 'TCP/IP')

    def update_telemetry(self,fields):
        """Recebe ESPDIAG:TEMP|CPU_MHZ|HEAP_FREE|HEAP_TOTAL do firmware 4.16.2 e atualiza os valores."""
        try:
            mhz=int(fields['CPU_MHZ']);free=int(fields['HEAP_FREE']);total=int(fields['HEAP_TOTAL'])
            if mhz>0 and 0<=free<=total and total>0:
                self.values['resources'].setText(f'{mhz} MHz / {free/1024:.0f} de {total/1024:.0f} KiB')
        except (KeyError,ValueError,TypeError):
            pass
        try:
            temp=float(fields['TEMP'])
            valid=math.isfinite(temp) and -40<=temp<=125
            self.values['temp'].setText(f'{temp:.1f} °C' if valid else 'Indisponível')
            self.values['temp'].set_celsius(temp if valid else None)
        except (KeyError,ValueError,TypeError):
            pass
