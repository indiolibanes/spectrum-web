# Interface ISA-101, tema noturno e correções — 4.16.2

Versão 4.16.2 · Build 1263 · 20/10/2026.

## O que mudou

**Interface**

- Estilo plano da ISA-101 nos dois temas: sem vidro, degradê, brilho ambiente nem textura (a textura de celulose foi desativada). Gráficos com barras lisas. Veja [docs/ISA-101.md](docs/ISA-101.md).
- Tema **Noturno** (roxo, com turquesa como cor secundária) no lugar do preto e dourado. Preferências antigas (`dark`, `gold`, `umber`) migram sozinhas.
- Cor por função de botão padronizada, sem matizes de alarme (tabela em [docs/IDENTIDADE_VISUAL.md](docs/IDENTIDADE_VISUAL.md)).
- Logo do projeto ao lado do nome no cabeçalho.
- Nova hierarquia de fontes: Arena (marca), Dropline (títulos), IBM Plex Sans (interface) e IBM Plex Mono (valores). A EB Garamond saiu.
- Indicadores (KPIs) e logos do rodapé menores; cartões **ESP32 · Comunicação** e **Sensor espectral** com mais destaque.
- Link do GitHub de Davi Baracat (@DaviBaracat) na assinatura.

**Teclado na tela**

- Não abre mais sozinho ao iniciar um teste. Reconhece se o aparelho tem tela de toque (ou é móvel) e só então abre; modos **Automático**, **Sempre** e **Nunca**.
- Menor e no canto superior esquerdo (desloca-se só se cobrir o campo).

**Conexão com o ESP32**

- Tempo-limite de 4 s na conexão TCP, botão "Conectando…" durante a tentativa e janela **Falha na conexão** com o motivo.
- O indicador abaixo do gráfico mostra "ESP32 desconectado" em vez de "Pronto" quando não há conexão.
- **Causa raiz não confirmada.** O defeito relatado ("pronto" mas "desconectado") não foi reproduzido: o transporte funcionou em teste sem interface. As mudanças acima tornam a falha visível e explicável; o teste N1–N5 de [docs/TUTORIAL_CODESPACE.md](docs/TUTORIAL_CODESPACE.md) (seção F) deve fechar o caso, de preferência também com o ESP32 real.

## Limites desta versão

- A interface gráfica real (PyQt5) não pôde ser executada no ambiente de desenvolvimento do assistente. Os testes sem interface passam; os testes de interface (`tests/test_gui_smoke.py`) e a conferência visual dependem do Codespace.
- A ISA-101 foi aplicada a partir de fontes secundárias; a norma não foi lida na íntegra.
- As fontes Arena e Dropline (e as decorativas Evershore e Heritage, não usadas) vieram sem licença legível: confirme os direitos antes de distribuir.
- Android e web continuam para a última fase do roteiro.
