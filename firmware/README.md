# Firmware ESP32

Firmware de referência do controlador da bancada NIR, importado do repositório `spectrum-alpha`.

| Pasta | Versão | Observação |
|---|---|---|
| `Firmware_ESP32_4_16_2/` | 4.16.2 | Sketch `sketch_sep4a_copy_20261008183551.ino` com `src/` (Adafruit_AS726x) |

## Novidades desta versão em relação à 4.16.0

- `CMD:DIAG_SENSOR` responde `ESPDIAG:TEMP|CPU_MHZ|HEAP_FREE|HEAP_TOTAL`, mostrado no cartão "ESP32 · Comunicação" do supervisório.
- `CMD:ADMIN_CARCACA` abre uma sessão administrativa temporária para a carcaça. O firmware não verifica senha: a validação de usuário e senha é feita pelo supervisório, e a autorização exige renovação (`CMD:RENOVAR_CARCACA`) e fica restrita ao transporte de origem.
- `STATUS:ADMIN_PROTOCOLO_1` é enviado no `CMD:PING` quando o protocolo administrativo está disponível.

## Gravação

Abra o `.ino` na Arduino IDE com a placa ESP32 e a biblioteca `src/` na mesma pasta do sketch, depois compile e grave.
