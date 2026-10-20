"""
Mensagens e etapas mostradas ao operador durante a análise da amostra.

Este módulo não depende do Qt: traduz o estado da máquina de estados (fsm_state do main.py)
em uma fase legível (título, etapa, humor do rosto e frases que se alternam). Assim a lógica
pode ser testada sem interface (tests/test_analysis_messages.py).

Os textos não usam emoji: o gerenciador de temas remove emoji dos rótulos. O sorriso é
desenhado pelo AnalysisIndicator.
"""
from dataclasses import dataclass

# (ação no final do nome do estado) -> (etapa de 1 a 5, tipo de ação)
ACTIONS = {
    "FECHANDO_GAVETA": (1, "drawer_close"),
    "AVANCANDO_SENSOR": (2, "sensor_forward"),
    "LENDO_ESPECTRO": (3, "reading"),
    "RECUANDO_SENSOR": (4, "sensor_back"),
    "ABRINDO_GAVETA": (5, "drawer_open"),
}
TOTAL_STEPS = 5

MODE_TITLES = {
    "AUTO": "Medição da amostra",
    "REP": "Leitura com repetibilidade",
    "CALIB_ETAPA1": "Calibração · padrão branco",
    "CALIB_ETAPA2": "Calibração · referência escura",
}

# Frases por tipo de ação; alternam a cada poucos segundos.
MESSAGES = {
    "drawer_close": (
        "Fechando a gaveta com cuidado para não perturbar a amostra.",
        "A luz externa fica do lado de fora: a medição precisa de escuro.",
        "Gaveta a caminho. Já já começamos.",
    ),
    "sensor_forward": (
        "Aproximando o sensor da amostra.",
        "Posicionando o sensor a poucos milímetros da superfície.",
        "Quase lá. A distância certa dá espectros mais limpos.",
    ),
    "reading": (
        "Lendo o espectro. Seis bandas do infravermelho próximo em ação.",
        "Quanto mais constante a luz, melhor a leitura. Está tudo certo por aqui.",
        "A lignina absorve, a celulose reflete. O sensor está anotando tudo.",
        "Respire fundo: a amostra está em boas mãos.",
    ),
    "sensor_back": (
        "Leitura feita! Recuando o sensor.",
        "Guardando o sensor em segurança.",
    ),
    "drawer_open": (
        "Abrindo a gaveta para você retirar a amostra.",
        "Quase terminando. O resultado já está sendo calculado.",
    ),
    "preparing": (
        "Preparando o equipamento. Abrindo a gaveta para receber a amostra.",
        "Já vamos começar. Tenha a amostra à mão.",
    ),
    "waiting": (
        "Aguardando a sua confirmação para continuar.",
        "Sem pressa: o equipamento espera por você.",
    ),
    "waiting_next": (
        "Aguardando a próxima leitura da série de repetibilidade.",
        "Reposicione a amostra se necessário e confirme.",
    ),
    "wrapup": (
        "Finalizando e fechando a gaveta.",
        "Organizando os resultados.",
    ),
    "cancel": (
        "Cancelando com segurança. Fechando a gaveta.",
        "Tudo bem, podemos recomeçar quando quiser.",
    ),
    "idle": (
        "Pronto para a próxima amostra.",
        "Posicione a amostra e toque em Realizar leitura.",
        "Equipamento em repouso. Tudo em ordem.",
    ),
    "done": (
        "Análise concluída. Boa amostra!",
        "Resultado pronto. Foi um prazer analisar essa amostra.",
        "Missão cumprida. O número kappa está no painel ao lado.",
    ),
    "fault": (
        "Algo não saiu como esperado. Verifique o equipamento e tente de novo.",
    ),
    "emergency": (
        "Parada de emergência acionada. Confirme que o equipamento está seguro antes de reiniciar.",
    ),
}

# Humor do rosto: "smile" (sorriso aberto), "calm" (sorriso leve), "alert" (sério)
KIND_MOOD = {
    "drawer_close": "calm", "sensor_forward": "calm", "reading": "calm", "sensor_back": "smile",
    "drawer_open": "smile", "preparing": "calm", "waiting": "calm", "waiting_next": "calm",
    "wrapup": "smile", "cancel": "calm", "idle": "smile", "done": "smile",
    "fault": "alert", "emergency": "alert",
}

BUSY_KINDS = {"drawer_close", "sensor_forward", "reading", "sensor_back", "drawer_open", "preparing", "wrapup", "cancel"}


@dataclass(frozen=True)
class Phase:
    kind: str         # chave de MESSAGES
    title: str        # linha de título
    step: int         # 0 se não houver etapa
    total: int        # TOTAL_STEPS quando há etapa, 0 caso contrário
    mood: str         # smile | calm | alert
    busy: bool        # equipamento em movimento / leitura

    @property
    def messages(self):
        return MESSAGES[self.kind]


def _mode_of(state):
    for prefix in ("CALIB_ETAPA1", "CALIB_ETAPA2", "AUTO", "REP"):
        if state.startswith(prefix + "_"):
            return prefix
    return None


def phase_for(state):
    """Fase correspondente a um fsm_state. Estados desconhecidos viram 'idle' com título genérico."""
    state = (state or "IDLE").strip().upper()
    if state == "IDLE":
        return Phase("idle", "Pronto", 0, 0, KIND_MOOD["idle"], False)
    if state == "EMERGENCIA":
        return Phase("emergency", "Parada de emergência", 0, 0, "alert", False)
    if state == "FALHA":
        return Phase("fault", "Falha", 0, 0, "alert", False)
    if state == "AGUARDANDO_POPUP":
        return Phase("waiting", "Aguardando confirmação", 0, 0, "calm", False)
    if state == "PREP_ABRINDO_GAVETA":
        return Phase("preparing", "Preparando", 0, 0, "calm", True)
    if state == "REP_AGUARDANDO_PROXIMA":
        return Phase("waiting_next", MODE_TITLES["REP"], 0, 0, "calm", False)
    if "CANCELANDO" in state:
        return Phase("cancel", "Cancelando", 0, 0, "calm", True)
    if state.endswith("CONCLUSAO_FECHANDO_GAVETA"):
        return Phase("wrapup", "Concluindo", 0, 0, "smile", True)

    mode = _mode_of(state)
    for action, (step, kind) in ACTIONS.items():
        if state.endswith(action) and mode:
            return Phase(kind, MODE_TITLES[mode], step, TOTAL_STEPS, KIND_MOOD[kind], True)
    return Phase("idle", "Em operação", 0, 0, "calm", False)


def message_for(phase, tick):
    """Frase de uma fase; 'tick' avança a cada poucos segundos e escolhe a frase."""
    options = phase.messages
    return options[int(tick) % len(options)]


def finished(previous_state, state):
    """True quando um ciclo terminou normalmente: saiu de um estado de operação e voltou a IDLE."""
    prev = (previous_state or "IDLE").upper()
    now = (state or "IDLE").upper()
    return now == "IDLE" and prev not in ("IDLE", "FALHA", "EMERGENCIA") and "CANCELANDO" not in prev


def known_states():
    """Todos os estados usados pelo main.py (para testes e para o simulador)."""
    states = ["IDLE", "FALHA", "EMERGENCIA", "AGUARDANDO_POPUP", "PREP_ABRINDO_GAVETA", "REP_AGUARDANDO_PROXIMA",
              "CONCLUSAO_FECHANDO_GAVETA", "CALIB_CONCLUSAO_FECHANDO_GAVETA", "CANCELANDO_FECHANDO_GAVETA",
              "CALIB_CANCELANDO_FECHANDO_GAVETA"]
    for mode in ("AUTO", "REP", "CALIB_ETAPA1", "CALIB_ETAPA2"):
        states.extend(f"{mode}_{action}" for action in ACTIONS)
    return states
