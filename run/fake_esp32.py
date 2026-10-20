#!/usr/bin/env python3
"""
Simulador de bancada ESP32 (somente para teste de interface).

Fala o mesmo protocolo TCP do firmware, na porta 8080 (modo Wi-Fi do supervisório):
  - Recebe linhas CMD:... terminadas em \\n.
  - Responde com STATUS:..., PORTA:... e DATA:v1,...,v6.

Não movimenta nada e não mede luz real. Serve para testar telas, mensagens,
intertravamentos e fluxos de ensaio sem a bancada.
"""
import argparse
import random
import socket
import threading
import time

PORTA_PADRAO = 8080
ATRASO_MOVIMENTO = 0.25   # segundos entre o comando e o fim de curso
ATRASO_LEITURA = 0.4      # tempo simulado de integração do sensor


class Bancada:
    def __init__(self):
        self.lock = threading.Lock()
        self.porta_aberta = False
        self.gaveta_aberta = False
        self.sensor_avancado = False
        self.carcaca_fechada = True
        self.autorizada = False

    def estado_linha(self):
        # Formato esperado por EquipmentInterlocks.update: PORTA:CHAVE:valor|CHAVE:valor...
        return (f"PORTA:ABERTA:{int(self.porta_aberta)}|FECHADA:{int(not self.porta_aberta)}"
                f"|CARCACA_FECHADA:{int(self.carcaca_fechada)}"
                f"|SENSOR_RECUADO:{int(not self.sensor_avancado)}|SENSOR_AVANCADO:{int(self.sensor_avancado)}")

    def amostra(self, escuro):
        # Canais 610, 680, 730, 760, 810 e 860 nm, com ruído leve.
        base = [60, 62, 65, 63, 61, 60] if escuro else [2400, 2900, 3300, 3100, 2600, 2100]
        return [max(0, round(v + random.gauss(0, 12 if escuro else 60))) for v in base]


def responder(bancada, comando, enviar):
    """Gera as respostas do firmware para um comando. Retorna False se o comando for desconhecido."""
    if comando.startswith("MANUAL:"):
        comando = comando[len("MANUAL:"):]

    if comando == "PING":
        # Mesma sequência do firmware 4.16.2: sem os *_PROTOCOLO_1 a interface nunca libera a leitura.
        for status in ("PROTOCOLO_2", "PORTA_PROTOCOLO_1", "MANUAL_PROTOCOLO_1",
                       "CARRINHO_PROTOCOLO_1", "ADMIN_PROTOCOLO_1", "SENSOR_OK"):
            enviar("STATUS:" + status)
        enviar(bancada.estado_linha())
        enviar("STATUS:PONG")
        return True
    if comando == "ESTADO_PORTA":
        enviar(bancada.estado_linha())
        return True
    if comando == "DIAG_SENSOR":
        # Mesmo formato do firmware 4.16.2: telemetria do ESP32 e do sensor (valores simulados).
        enviar("ESPDIAG:TEMP:" + f"{random.uniform(34, 41):.1f}" + "|CPU_MHZ:240|HEAP_FREE:"
               + str(random.randint(150000, 190000)) + "|HEAP_TOTAL:327680")
        enviar("DIAG:TEMP:27.0|HW:SIMULADOR|STATUS:SIMULADO")
        return True
    if comando == "ADMIN_CARCACA":
        # Simula a sessão administrativa: a validação de usuário/senha fica no supervisório.
        with bancada.lock:
            bancada.autorizada = True
        enviar("STATUS:ADMIN_CARCACA_AUTORIZADA")
        return True

    def movimento(atualizar, status):
        time.sleep(ATRASO_MOVIMENTO)
        with bancada.lock:
            atualizar()
        enviar("STATUS:" + status)
        enviar(bancada.estado_linha())

    if comando == "ABRIR_GAVETA":
        movimento(lambda: setattr(bancada, "gaveta_aberta", True), "GAVETA_ABERTA")
    elif comando == "FECHAR_GAVETA":
        movimento(lambda: setattr(bancada, "gaveta_aberta", False), "GAVETA_FECHADA")
    elif comando == "ABRIR_PORTA":
        movimento(lambda: setattr(bancada, "porta_aberta", True), "PORTA_ABERTA")
    elif comando == "FECHAR_PORTA":
        movimento(lambda: setattr(bancada, "porta_aberta", False), "PORTA_FECHADA")
    elif comando == "AVANCAR_SENSOR":
        movimento(lambda: setattr(bancada, "sensor_avancado", True), "SENSOR_AVANCADO")
    elif comando == "RECUAR_SENSOR":
        movimento(lambda: setattr(bancada, "sensor_avancado", False), "SENSOR_RECUADO")
    elif comando == "AUTORIZAR_CARCACA" or comando == "RENOVAR_CARCACA":
        bancada.autorizada = True
        enviar("STATUS:CARCACA_AUTORIZADA")
    elif comando == "REVOGAR_CARCACA":
        bancada.autorizada = False
        enviar("STATUS:CARCACA_AUTORIZACAO_REVOGADA")
    elif comando in ("LER_ESPECTRO", "LER_ESCURO"):
        time.sleep(ATRASO_LEITURA)
        valores = bancada.amostra(escuro=(comando == "LER_ESCURO"))
        enviar("DATA:" + ",".join(str(v) for v in valores))
        enviar("STATUS:LEITURA_CONCLUIDA")
    elif comando == "EMERGENCIA":
        with bancada.lock:
            bancada.autorizada = False
        enviar("STATUS:EMERGENCIA_ACIONADA")
        enviar(bancada.estado_linha())
    else:
        return False
    return True


def atender(conexao, endereco, bancada):
    print(f"[SIM] cliente conectado: {endereco}", flush=True)
    trava_envio = threading.Lock()

    def enviar(linha):
        with trava_envio:
            conexao.sendall((linha + "\n").encode("utf-8"))
        print(f"[SIM] -> {linha}", flush=True)

    buffer = b""
    try:
        while True:
            dados = conexao.recv(1024)
            if not dados:
                break
            buffer += dados
            while b"\n" in buffer:
                bruta, buffer = buffer.split(b"\n", 1)
                linha = bruta.decode("utf-8", "replace").strip()
                if not linha.startswith("CMD:"):
                    continue
                comando = linha[4:]
                print(f"[SIM] <- {linha}", flush=True)
                if not responder(bancada, comando, enviar):
                    print(f"[SIM] comando sem resposta simulada: {comando}", flush=True)
    except OSError:
        pass
    finally:
        conexao.close()
        print(f"[SIM] cliente desconectado: {endereco}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Simulador ESP32 para o SPECTRUM-LAB PRO")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=PORTA_PADRAO)
    args = parser.parse_args()

    bancada = Bancada()
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((args.host, args.port))
    servidor.listen(1)
    print(f"[SIM] bancada simulada ouvindo em {args.host}:{args.port}", flush=True)
    while True:
        conexao, endereco = servidor.accept()
        threading.Thread(target=atender, args=(conexao, endereco, bancada), daemon=True).start()


if __name__ == "__main__":
    main()
