"""Diagnóstico sem valores nominais apresentados como medições reais."""
import math,time
from PyQt5.QtWidgets import QFrame,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel
import typography as ty

def _title(text):
    out=QLabel(text);out.setProperty('role','heading');out.setStyleSheet(ty.qss('section'));return out

class SensorDiagnosticsCard(QFrame):
    def __init__(self,parent=None):
        super().__init__(parent);self.setObjectName('scadaPanel');self.setProperty('priority','high');self.last_received=None
        layout=QVBoxLayout(self);layout.setContentsMargins(18,14,18,14);layout.setSpacing(10)
        row=QHBoxLayout();row.addWidget(_title('GY-AS7263 · Sensor espectral'));row.addStretch()
        self.lbl_status_badge=QLabel('Aguardando telemetria');row.addWidget(self.lbl_status_badge);layout.addLayout(row)
        grid=QGridLayout();grid.setHorizontalSpacing(18);grid.setVerticalSpacing(8);layout.addLayout(grid)
        fields=[('Temperatura interna','lbl_die_temp'),('Ganho configurado','lbl_ganho'),
                ('Integração configurada','lbl_integracao'),('Corrente LED configurada','lbl_driver_led'),
                ('Estado reportado do LED','lbl_led_state'),('Modelo declarado','lbl_hardware'),
                ('Saturação nas contagens','lbl_sat'),('Irradiância absoluta','lbl_irrad'),
                ('Firmware do chip','lbl_chip_firmware')]
        for i,(title,name) in enumerate(fields):
            caption=QLabel(title);caption.setStyleSheet('color: #9CA3AF; '+ty.qss('body'))
            value=QLabel('—');value.setStyleSheet(ty.qss('button'));setattr(self,name,value)
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
        self.lbl_irrad.setText('Não disponível');self.lbl_chip_firmware.setText('Não consultado')
        self.lbl_status_sensor.setText(message);self.lbl_status_badge.setText(message)

    def atualizar_telemetria(self,die_temp=None,gain=None,integration=None,led=None,
                            irradiance=None,hw_id=None,status=None,saturation=None,led_state=None,received=False):
        if received:self.last_received=time.monotonic()
        if die_temp is not None:
            try:
                temp=float(str(die_temp).replace('TEMP:','').replace('°C','').strip())
                self.lbl_die_temp.setText(f'{temp:.1f} °C' if math.isfinite(temp) and -40<=temp<=125 else 'Indisponível')
            except (ValueError,TypeError):self.lbl_die_temp.setText('Indisponível')
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
        layout=QVBoxLayout(self);layout.setContentsMargins(18,14,18,14);layout.setSpacing(10)
        layout.addWidget(_title('ESP32 · Comunicação'))
        self.values={};grid=QGridLayout();grid.setHorizontalSpacing(18);grid.setVerticalSpacing(8);layout.addLayout(grid)
        for i,(key,title) in enumerate([('connection','Conexão'),('protocol','Protocolo'),('heartbeat','Heartbeat'),
                                       ('baud','Velocidade USB'),('resources','CPU / memória'),('temp','Temperatura ESP32')]):
            row,col=divmod(i,2);label=QLabel(title);label.setStyleSheet('color: #9CA3AF; '+ty.qss('body'))
            value=QLabel('—');value.setStyleSheet(ty.qss('button'));self.values[key]=value
            grid.addWidget(label,row,col*2);grid.addWidget(value,row,col*2+1)
        self.values['resources'].setText('Não enviados');self.values['temp'].setText('Não enviada')

    def refresh(self,window):
        connected=window.is_serial_connected()
        if not connected:
            self.values['resources'].setText('Não enviados')
            self.values['temp'].setText('Não enviada')
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
            self.values['temp'].setText(f'{temp:.1f} °C' if math.isfinite(temp) and -40<=temp<=125 else 'Indisponível')
        except (KeyError,ValueError,TypeError):
            pass
